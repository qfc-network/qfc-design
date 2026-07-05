# Agent 能力资源（QVM）

[English](./35-AGENT-CAPABILITY-RESOURCES-EN.md) | **中文**

> 最后更新：2026-03-11 | 版本 1.0
> GitHub Issue: #19
> 作者：Alex Wei，QFC Network 产品经理

---

## 1. 摘要

本文档定义 QVM（QuantumScript VM）中用于在 VM 层强制执行 AI agent 能力（capability）的资源类型。与 EVM 合约层权限（可能存在 bug）不同，QVM 资源是 **Move 风格的线性类型**——从构造上就无法被伪造、复制，或超出额度花费。

两个核心资源：
- **InferenceCapability**——在 AI 推理任务上花费预算的权利
- **AgentRegistration**——agent 身份、发现元数据与质押

二者共同实现能力门控推理、agent 发现与紧急停止开关（kill switch）——全部在 VM 层强制执行。

---

## 2. 资源类型定义

### 2.1 InferenceCapability

```move
module qfc::inference_capability {

    // ─── Error Codes ───
    const E_INSUFFICIENT_BUDGET: u64 = 100;
    const E_MODEL_NOT_ALLOWED: u64 = 101;
    const E_CAPABILITY_EXPIRED: u64 = 102;
    const E_CAPABILITY_FROZEN: u64 = 103;
    const E_NOT_OWNER: u64 = 104;
    const E_ZERO_BUDGET: u64 = 105;

    // ─── Events ───
    struct CapabilityCreated has copy, drop {
        capability_id: UID,
        owner: address,
        budget: u64,
        allowed_models: vector<ModelId>,
        expires_at: u64,
    }

    struct CapabilityUsed has copy, drop {
        capability_id: UID,
        model_id: ModelId,
        fee: u64,
        remaining_budget: u64,
    }

    struct CapabilityFrozen has copy, drop {
        capability_id: UID,
        frozen_by: address,
    }

    struct CapabilityDestroyed has copy, drop {
        capability_id: UID,
        remaining_budget: u64,  // Refunded to owner
    }

    struct CapabilityToppedUp has copy, drop {
        capability_id: UID,
        added: u64,
        new_budget: u64,
    }

    // ─── Core Resource ───
    resource InferenceCapability {
        id: UID,
        owner: address,
        remaining_budget: u64,
        allowed_models: vector<ModelId>,
        expires_at: u64,            // Unix timestamp, 0 = no expiry
        frozen: bool,
        total_spent: u64,           // Lifetime counter
        total_tasks: u64,           // Lifetime task count
        created_at: u64,
    }
}
```

### 2.2 AgentRegistration

```move
module qfc::agent_registry {

    // ─── Error Codes ───
    const E_INSUFFICIENT_STAKE: u64 = 200;
    const E_NOT_OWNER: u64 = 201;
    const E_AGENT_FROZEN: u64 = 202;
    const E_ALREADY_REGISTERED: u64 = 203;
    const E_INVALID_ENDPOINT: u64 = 204;
    const E_COOLDOWN_NOT_ELAPSED: u64 = 205;
    const E_BELOW_MIN_STAKE: u64 = 206;

    // ─── Events ───
    struct AgentRegistered has copy, drop {
        agent_id: UID,
        owner: address,
        capabilities: vector<String>,
        stake: u64,
    }

    struct AgentUpdated has copy, drop {
        agent_id: UID,
        field: String,  // "endpoint", "capabilities", "protocol_digests"
    }

    struct AgentFrozen has copy, drop {
        agent_id: UID,
        frozen_by: address,
        reason: String,
    }

    struct AgentUnfrozen has copy, drop {
        agent_id: UID,
        unfrozen_by: address,
    }

    struct AgentRevoked has copy, drop {
        agent_id: UID,
        stake_returned: u64,
        stake_slashed: u64,
    }

    struct AgentSlashed has copy, drop {
        agent_id: UID,
        amount: u64,
        reason: String,
    }

    // ─── Core Resource ───
    resource AgentRegistration {
        id: UID,
        owner: address,
        protocol_digests: vector<Hash>,    // Protocols this agent supports
        capabilities: vector<String>,       // "text-generation", "image-analysis", etc.
        endpoint: String,                   // How to reach this agent off-chain
        stake: u64,                         // Skin-in-the-game (minimum required)
        frozen: bool,
        reputation_score: u64,              // 0-10000 (basis points)
        total_tasks_completed: u64,
        total_tasks_failed: u64,
        last_heartbeat: u64,                // Unix timestamp
        created_at: u64,
    }
}
```

---

## 3. 模块函数

### 3.1 InferenceCapability 函数

```move
/// Create a new inference capability
public fun create(
    owner: &signer,
    budget: Coin<QFC>,
    allowed_models: vector<ModelId>,
    expires_at: u64,
): InferenceCapability {
    assert!(coin::value(&budget) > 0, E_ZERO_BUDGET);

    let cap = InferenceCapability {
        id: new_uid(),
        owner: signer::address_of(owner),
        remaining_budget: coin::value(&budget),
        allowed_models,
        expires_at,
        frozen: false,
        total_spent: 0,
        total_tasks: 0,
        created_at: timestamp::now(),
    };

    // Deposit budget into escrow
    escrow::deposit(cap.id, budget);

    event::emit(CapabilityCreated { ... });
    cap
}

/// Use capability to pay for inference (called by AI Coordinator)
public fun use_for_inference(
    cap: &mut InferenceCapability,
    model_id: ModelId,
    fee: u64,
): bool {
    assert!(!cap.frozen, E_CAPABILITY_FROZEN);
    assert!(cap.expires_at == 0 || timestamp::now() < cap.expires_at, E_CAPABILITY_EXPIRED);
    assert!(vector::contains(&cap.allowed_models, &model_id), E_MODEL_NOT_ALLOWED);
    assert!(cap.remaining_budget >= fee, E_INSUFFICIENT_BUDGET);

    cap.remaining_budget = cap.remaining_budget - fee;
    cap.total_spent = cap.total_spent + fee;
    cap.total_tasks = cap.total_tasks + 1;

    event::emit(CapabilityUsed { ... });
    true
}

/// Top up budget
public fun top_up(
    cap: &mut InferenceCapability,
    owner: &signer,
    additional: Coin<QFC>,
) {
    assert!(signer::address_of(owner) == cap.owner, E_NOT_OWNER);
    let amount = coin::value(&additional);
    cap.remaining_budget = cap.remaining_budget + amount;
    escrow::deposit(cap.id, additional);
    event::emit(CapabilityToppedUp { ... });
}

/// Freeze capability (owner or governance)
public fun freeze(
    cap: &mut InferenceCapability,
    caller: &signer,
) {
    let addr = signer::address_of(caller);
    assert!(addr == cap.owner || governance::is_authorized(addr), E_NOT_OWNER);
    cap.frozen = true;
    event::emit(CapabilityFrozen { ... });
}

/// Unfreeze (owner or governance)
public fun unfreeze(
    cap: &mut InferenceCapability,
    caller: &signer,
) {
    let addr = signer::address_of(caller);
    assert!(addr == cap.owner || governance::is_authorized(addr), E_NOT_OWNER);
    cap.frozen = false;
}

/// Destroy capability and refund remaining budget
public fun destroy(
    cap: InferenceCapability,
    owner: &signer,
): Coin<QFC> {
    assert!(signer::address_of(owner) == cap.owner, E_NOT_OWNER);
    let refund = escrow::withdraw(cap.id, cap.remaining_budget);
    event::emit(CapabilityDestroyed { ... });
    // Resource is consumed (destroyed) by Move semantics
    let InferenceCapability { id, .. } = cap;
    uid::delete(id);
    refund
}
```

### 3.2 AgentRegistration 函数

```move
/// Minimum stake tiers
const MIN_STAKE_BASIC: u64 = 100_000_000;      // 100 QFC (8 decimals)
const MIN_STAKE_VERIFIED: u64 = 1_000_000_000;  // 1,000 QFC
const MIN_STAKE_PREMIUM: u64 = 10_000_000_000;  // 10,000 QFC
const UNSTAKE_COOLDOWN: u64 = 7 * 24 * 3600;    // 7 days

/// Register a new agent
public fun register(
    owner: &signer,
    stake: Coin<QFC>,
    capabilities: vector<String>,
    endpoint: String,
    protocol_digests: vector<Hash>,
): AgentRegistration {
    assert!(coin::value(&stake) >= MIN_STAKE_BASIC, E_INSUFFICIENT_STAKE);
    assert!(string::length(&endpoint) > 0, E_INVALID_ENDPOINT);

    let agent = AgentRegistration {
        id: new_uid(),
        owner: signer::address_of(owner),
        protocol_digests,
        capabilities,
        endpoint,
        stake: coin::value(&stake),
        frozen: false,
        reputation_score: 5000,  // Start at 50%
        total_tasks_completed: 0,
        total_tasks_failed: 0,
        last_heartbeat: timestamp::now(),
        created_at: timestamp::now(),
    };

    staking::deposit(agent.id, stake);
    event::emit(AgentRegistered { ... });
    agent
}

/// Update endpoint
public fun update_endpoint(
    agent: &mut AgentRegistration,
    caller: &signer,
    new_endpoint: String,
) {
    assert!(signer::address_of(caller) == agent.owner, E_NOT_OWNER);
    assert!(!agent.frozen, E_AGENT_FROZEN);
    agent.endpoint = new_endpoint;
    event::emit(AgentUpdated { agent_id: agent.id, field: string::utf8(b"endpoint") });
}

/// Update capabilities
public fun update_capabilities(
    agent: &mut AgentRegistration,
    caller: &signer,
    new_capabilities: vector<String>,
) {
    assert!(signer::address_of(caller) == agent.owner, E_NOT_OWNER);
    assert!(!agent.frozen, E_AGENT_FROZEN);
    agent.capabilities = new_capabilities;
    event::emit(AgentUpdated { agent_id: agent.id, field: string::utf8(b"capabilities") });
}

/// Freeze agent (owner or governance)
public fun freeze(
    agent: &mut AgentRegistration,
    caller: &signer,
    reason: String,
) {
    let addr = signer::address_of(caller);
    assert!(addr == agent.owner || governance::is_authorized(addr), E_NOT_OWNER);
    agent.frozen = true;
    event::emit(AgentFrozen { agent_id: agent.id, frozen_by: addr, reason });
}

/// Unfreeze (governance only for safety)
public fun unfreeze(
    agent: &mut AgentRegistration,
    caller: &signer,
) {
    assert!(governance::is_authorized(signer::address_of(caller)), E_NOT_OWNER);
    agent.frozen = false;
    event::emit(AgentUnfrozen { ... });
}

/// Slash stake (called by verification system on misbehavior)
public fun slash(
    agent: &mut AgentRegistration,
    amount: u64,
    reason: String,
) {
    // Only callable by AI Coordinator module
    let slash_amount = if (amount > agent.stake) { agent.stake } else { amount };
    agent.stake = agent.stake - slash_amount;
    staking::slash(agent.id, slash_amount);
    agent.reputation_score = if (agent.reputation_score >= 500) {
        agent.reputation_score - 500
    } else { 0 };
    event::emit(AgentSlashed { agent_id: agent.id, amount: slash_amount, reason });
}

/// Revoke agent and reclaim stake (after cooldown)
public fun revoke(
    agent: AgentRegistration,
    owner: &signer,
): Coin<QFC> {
    assert!(signer::address_of(owner) == agent.owner, E_NOT_OWNER);
    // Cooldown check handled by staking module
    let stake_returned = staking::withdraw(agent.id, agent.stake);
    event::emit(AgentRevoked { ... });
    let AgentRegistration { id, .. } = agent;
    uid::delete(id);
    stake_returned
}

/// Heartbeat (agent signals it's alive)
public fun heartbeat(
    agent: &mut AgentRegistration,
    caller: &signer,
) {
    assert!(signer::address_of(caller) == agent.owner, E_NOT_OWNER);
    agent.last_heartbeat = timestamp::now();
}

/// Record task completion (called by AI Coordinator)
public fun record_task_result(
    agent: &mut AgentRegistration,
    success: bool,
) {
    if (success) {
        agent.total_tasks_completed = agent.total_tasks_completed + 1;
        // Increase reputation (capped at 10000)
        agent.reputation_score = min(agent.reputation_score + 10, 10000);
    } else {
        agent.total_tasks_failed = agent.total_tasks_failed + 1;
        agent.reputation_score = if (agent.reputation_score >= 50) {
            agent.reputation_score - 50
        } else { 0 };
    }
}
```

---

## 4. 能力门控推理流程

```
用户 / Agent 运行时
    │
    ├─1─► 携带 capability_id 提交推理请求
    │
AI Coordinator (qfc-ai-coordinator)
    │
    ├─2─► 从 QVM 状态加载 InferenceCapability 资源
    │     ├── 检查：!frozen
    │     ├── 检查：未过期
    │     ├── 检查：model_id 在 allowed_models 中
    │     └── 检查：remaining_budget >= estimated_fee
    │
    ├─3─► 加载 AgentRegistration（若由 agent 提交）
    │     ├── 检查：!frozen
    │     └── 检查：reputation_score >= min_threshold
    │
    ├─4─► 将任务分配给矿工（沿用现有 TaskPool 流程）
    │
矿工
    ├─5─► 执行推理 → 提交结果 + 证明
    │
AI Coordinator
    ├─6─► 验证结果（抽查 / zkML）
    │
    ├─7─► 调用 use_for_inference(cap, model_id, actual_fee)
    │     └── 原子地从 capability 预算中扣除
    │
    ├─8─► 调用 record_task_result(agent, success)
    │     └── 更新声誉分
    │
    └─9─► 将结果返回给调用方
```

**关键保证**：第 7 步是原子的。若 capability 预算不足，整个交易回滚——由于预算检查在第 2 步分配之前完成，矿工不会执行没有报酬的工作。

---

## 5. Kill Switch 机制

### 5.1 冻结 vs 销毁

| 操作 | 效果 | 可逆 | 触发者 |
|--------|--------|------------|-----------------|
| **冻结（Freeze）** | Agent/capability 不可使用；资金锁定 | 是（解冻） | 所有者、治理 |
| **销毁（Destroy）** | Agent/capability 永久移除；质押/预算退还 | 否 | 仅所有者 |

### 5.2 紧急场景

| 场景 | 操作 | 触发者 |
|----------|--------|---------|
| Session key 泄露 | 撤销 session key + 冻结 agent | 所有者 |
| 检测到 agent 作恶 | 冻结 agent + 罚没质押 | 治理 / AI Coordinator |
| 所有者私钥泄露 | 治理冻结（经验证者投票） | 治理多签 |
| 全网攻击 | 治理冻结所有 agent | 紧急治理动作 |

### 5.3 治理冻结流程

1. 任何验证者均可发起紧急冻结提案
2. 需在 1 小时内获得 >2/3 验证者投票通过
3. 被冻结的 agent 无法执行任何操作
4. 解冻需另行发起治理投票（>2/3）
5. 所有者无法解冻被治理冻结的 agent

---

## 6. 发现 API

### 6.1 RPC 端点

#### `qfc_listAgents`

```json
// Request
{
    "jsonrpc": "2.0",
    "method": "qfc_listAgents",
    "params": {
        "status": "active",    // "active" | "frozen" | "all"
        "limit": 20,
        "offset": 0,
        "sort_by": "reputation_score",  // "reputation_score" | "stake" | "created_at"
        "sort_order": "desc"
    }
}

// Response
{
    "agents": [
        {
            "agent_id": "0xabc...",
            "owner": "0x123...",
            "capabilities": ["text-generation", "image-analysis"],
            "endpoint": "https://agent.example.com",
            "stake": "1000000000",
            "frozen": false,
            "reputation_score": 8500,
            "total_tasks_completed": 1234,
            "last_heartbeat": 1741651200
        }
    ],
    "total": 150,
    "has_more": true
}
```

#### `qfc_queryAgentsByCapability`

```json
// Request
{
    "jsonrpc": "2.0",
    "method": "qfc_queryAgentsByCapability",
    "params": {
        "capability": "text-generation",
        "min_reputation": 5000,
        "min_stake": "1000000000",
        "limit": 10
    }
}
```

#### `qfc_queryAgentsByProtocolDigest`

```json
// Request
{
    "jsonrpc": "2.0",
    "method": "qfc_queryAgentsByProtocolDigest",
    "params": {
        "protocol_digest": "0xdef..."
    }
}
```

#### `qfc_getAgentDetails`

```json
// Request
{
    "jsonrpc": "2.0",
    "method": "qfc_getAgentDetails",
    "params": {
        "agent_id": "0xabc..."
    }
}

// Response
{
    "agent_id": "0xabc...",
    "owner": "0x123...",
    "protocol_digests": ["0xdef..."],
    "capabilities": ["text-generation"],
    "endpoint": "https://agent.example.com",
    "stake": "1000000000",
    "frozen": false,
    "reputation_score": 8500,
    "total_tasks_completed": 1234,
    "total_tasks_failed": 12,
    "last_heartbeat": 1741651200,
    "created_at": 1740000000,
    "inference_capabilities": [
        {
            "id": "0xcap...",
            "remaining_budget": "500000000",
            "allowed_models": ["qfc-llm-7b", "qfc-embed-small"],
            "expires_at": 1742256000,
            "total_spent": "250000000",
            "total_tasks": 567
        }
    ],
    "session_keys": [
        {
            "public_key": "0xkey...",
            "permissions": 3,
            "spending_limit": "100000000",
            "expires_at": 1741737600
        }
    ]
}
```

### 6.2 Rust 注册表索引

```rust
// qfc-core/crates/qfc-qvm/src/agent_index.rs

/// In-memory index for fast agent discovery
pub struct AgentIndex {
    /// capability -> sorted vec of (reputation, agent_id)
    by_capability: HashMap<String, BTreeSet<(u64, AgentId)>>,
    /// protocol_digest -> set of agent_ids
    by_protocol: HashMap<Hash, HashSet<AgentId>>,
    /// All agents by ID
    agents: HashMap<AgentId, AgentRegistrationView>,
}

impl AgentIndex {
    /// Rebuild from QVM state (on node startup)
    pub fn rebuild_from_state(state: &QvmState) -> Self { ... }

    /// Incremental update on new block
    pub fn apply_events(&mut self, events: &[AgentEvent]) { ... }

    /// Query by capability with filters
    pub fn query_by_capability(
        &self,
        capability: &str,
        min_reputation: u64,
        min_stake: u64,
        limit: usize,
    ) -> Vec<&AgentRegistrationView> { ... }
}
```

---

## 7. 质押经济学

### 7.1 质押层级

| 层级 | 最低质押 | 权益 |
|------|--------------|----------|
| **Basic** | 100 QFC | 可注册，限 10 任务/天 |
| **Verified** | 1,000 QFC | 无任务上限，抽查率更低 |
| **Premium** | 10,000 QFC | 任务分配优先，发现结果中优先展示 |

### 7.2 罚没条件

| 违规行为 | 罚没金额 | 声誉影响 |
|-----------|-------------|-------------------|
| 验证失败（错误推理结果） | 质押的 1% | -50 分 |
| 超时（接受任务后未交付结果） | 质押的 0.5% | -25 分 |
| 连续失败（3 次及以上） | 质押的 5% | -500 分 + 自动冻结 |
| 治理认定的不当行为 | 最高 100% | 归零 + 永久冻结 |

### 7.3 解除质押流程

1. 所有者调用 `revoke(agent)`
2. 质押进入**冷却期**（7 天）
3. 冷却期内：agent 被冻结，质押锁定，待处理的罚没照常执行
4. 冷却期结束后：剩余质押退还所有者
5. 资源被销毁（Move 语义）

### 7.4 声誉评分

```
reputation_score: u64  // 0 - 10000（基点）

起始分：            5000（50%）
每次成功：          +10
每次失败：          -50
每次罚没：          -500
上限：              10000
下限：              0

高声誉的权益：
- reputation >= 8000：抽查率由 10% 降至 5%
- reputation >= 9000：有资格获得优质任务分配
- reputation < 2000：无论质押多少，均限制在 Basic 层级
```

---

## 8. 安全性分析

### 8.1 QVM vs EVM 对比

| 属性 | EVM（合约层） | QVM（资源层） |
|----------|---------------------|---------------------|
| 预算执行 | `require(balance >= fee)`——可能存在重入 bug | 资源算术——VM 防止下溢 |
| Capability 伪造 | 可能通过合约 bug 实现 | 不可能——资源是线性类型 |
| 复制 | 可能通过重入实现 | 不可能——Move 禁止 copy |
| Kill switch | 管理员函数（可被绕过） | 资源冻结（VM 强制执行） |
| 上溢/下溢 | Solidity 0.8+ 有检查，但旧合约存在风险 | VM 层边界检查 |

### 8.2 攻击向量与缓解措施

| 攻击 | 向量 | 缓解措施 |
|--------|--------|------------|
| **女巫注册** | 注册大量廉价 agent | 最低质押 + QIB 基准测试 |
| **Capability 抽干** | 快速发起小额任务耗尽预算 | 按周期的花费限额 + 速率限制 |
| **僵尸 agent** | 注册后从不执行任务 | 心跳要求；不活跃 >24h 的 agent 降低优先级 |
| **刷声誉** | 完成简单任务刷分 | 按任务难度加权计分 |
| **抢跑** | 拦截任务分配 | 任务分配在验证者内部完成，不进 mempool |

---

## 9. 与 EVM 层的集成

### 9.1 跨 VM 架构

```
EVM 层                              QVM 层
┌────────────────────┐              ┌─────────────────────┐
│ AgentTokenFactory  │◄── 桥接 ────►│ AgentRegistration    │
│ (ERC-20 代币)      │              │ (资源)               │
│                    │              │                      │
│ RevenueDistributor │              │ InferenceCapability  │
│ (60/30/10 分成)    │              │ (资源)               │
│                    │              │                      │
│ QFCAgentAccount    │              │ SessionKey           │
│ (ERC-4337 钱包)    │              │ (资源)               │
└────────────────────┘              └─────────────────────┘
         │                                    │
         └───────── 跨 VM 消息总线 ───────────┘
```

### 9.2 桥接合约

```solidity
interface IAgentBridge {
    /// Called by QVM when an agent is registered
    function onAgentRegistered(bytes32 agentId, address owner, uint256 stake) external;

    /// Called by QVM when an agent earns revenue
    function distributeRevenue(bytes32 agentId, uint256 amount) external;

    /// Query agent status from EVM side
    function isAgentActive(bytes32 agentId) external view returns (bool);
}
```

---

## 10. 测试策略

### 10.1 单元测试

| 模块 | 测试数量 | 关键场景 |
|--------|-----------|---------------|
| `inference_capability` | ~25 | 创建、使用、充值、冻结、销毁、过期、模型白名单 |
| `agent_registry` | ~30 | 注册、更新、冻结、罚没、注销、心跳、声誉 |
| `agent_index` | ~15 | 按 capability 查询、按协议查询、从状态重建 |
| `session_keys` | ~20 | 签发、验证、轮换、撤销、TTL、nonce、权限 |

### 10.2 集成测试

| 场景 | 涉及组件 |
|----------|-----------|
| 带 capability 的完整推理流程 | Capability + AI Coordinator + 矿工 |
| Agent 注册 → 任务执行 → 声誉更新 | Registry + Coordinator + Capability |
| 错误结果罚没 → 声誉下降 → 自动冻结 | Registry + 验证 + 罚没 |
| 跨 VM：注册 agent → 创建 EVM 代币 | Registry + Bridge + TokenFactory |
| 发现：注册 100 个 agent → 按 capability 查询 | Registry + Index + RPC |

### 10.3 对抗性测试

- 尝试使用被冻结的 capability → 必须失败
- 尝试使用已过期的 capability → 必须失败
- 尝试超预算花费 → 必须失败
- 尝试使用不在白名单中的模型 → 必须失败
- 并发提交任务超出预算 → 仅有效任务成功
- 女巫攻击：同一所有者注册 100 个 agent → 质押要求仍然生效

---

## 11. 从 v2.0 的迁移路径

### 阶段 1：增量部署（第 1-2 周）
- 向 QVM 部署 `inference_capability` 与 `agent_registry` 模块
- 现有推理流程保持不变
- 新的能力门控路径作为可选项（opt-in）开放

### 阶段 2：软迁移（第 3-4 周）
- SDK 更新为优先使用能力门控路径
- 现有直接推理仍可用，但标记为废弃
- 启用发现 API

### 阶段 3：强制执行（第 5 周起）
- 所有推理请求必须携带 InferenceCapability
- 移除旧路径
- 完整启用带质押要求的 agent 注册表

**向后兼容**：在阶段 1-2 期间，系统为现有用户自动创建一个预算无限的"默认 capability"，保持 v2.0 的行为不变。

---

## 参考资料

- [24-AI-AGENT-FRAMEWORK.md](./24-AI-AGENT-FRAMEWORK-CN.md) — 研究基础
- [28-V3-ROADMAP.md](./28-V3-ROADMAP-CN.md) — v3.0 总体路线图，Phase 3.2
- [Move Language Documentation](https://move-language.github.io/move/)
- [Sui Object Model](https://docs.sui.io/concepts/object-model)
