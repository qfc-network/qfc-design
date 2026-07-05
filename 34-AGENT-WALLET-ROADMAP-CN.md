# AI 原生 Agent 钱包路线图（执行计划）

[English](./34-AGENT-WALLET-ROADMAP-EN.md) | **中文**

> 最后更新：2026-03-11 | 版本 1.0
> GitHub Issue: #34
> 作者：Alex Wei，QFC Network 产品经理

---

## 1. 执行摘要

本文档是将 QFC 的 AI 原生 Agent 钱包从 v2.0 的部分实现推进到生产可用能力的执行计划。工作横跨四个仓库（qfc-core、qfc-contracts、qfc-explorer、qfc-openclaw-skill），划分为四个里程碑：

| 里程碑 | 优先级 | 目标 |
|-----------|------|------|
| **M1** | P0 | Agent 生命周期写 API + session key 强制执行 + e2e 测试 |
| **M2** | P1 | Agent 操作的 gas 代付 / Paymaster 流程 |
| **M3** | P1 | 浏览器控制 / 可见性升级 |
| **M4** | P2 | OpenClaw 原生集成 + 文档 + 演示 |

**完成定义（Definition of Done）**：AI Agent 可以在链上强制执行的前提下完成注册、注资和撤销。Session key 强制执行 TTL、权限和支出限额。区块浏览器提供运营级可见性。OpenClaw 无需长期持有所有者私钥即可执行 Agent 操作。

---

## 2. 现状评估

### v2.0 已有内容

| 组件 | 状态 | 位置 |
|-----------|--------|----------|
| AI 协调器（任务池 → 矿工 → 验证 → 结算） | ✅ 可用 | `qfc-core/crates/qfc-ai-coordinator` |
| 推理证明验证（抽查） | ✅ 可用 | `qfc-core/crates/qfc-inference` |
| 支持 Move 风格资源的 QVM | ✅ 可用 | `qfc-core/crates/qfc-qvm` |
| 带 ERC-4337 EntryPoint 的 EVM（revm） | ✅ 部分 | `qfc-core/crates/qfc-executor` |
| OpenClaw 推理 skill | ✅ 可用 | `qfc-openclaw-skill` |
| 带交易/区块视图的区块浏览器 | ✅ 可用 | `qfc-explorer` |

### 缺失内容

| 缺口 | 影响 |
|-----|--------|
| QVM 中无 `AgentRegistration` 资源 | 无法在链上注册 Agent |
| 无 session key 模块 | Agent 每次操作都必须使用所有者私钥 |
| 无 ERC-4337 Agent 钱包合约 | 没有可编程的安全策略 |
| 无 Paymaster 合约 | Agent 必须持有 QFC 支付 gas |
| 浏览器中无 Agent 视图 | 运营者无法监控 Agent 活动 |
| OpenClaw 没有 Agent 钱包命令 | 无法从 OpenClaw 管理 Agent |

---

## 3. 里程碑 M1：Agent 生命周期 + Session Key（P0）

### 3.1 QVM Agent 注册资源

```move
module qfc::agent_registry {

    /// Error codes
    const E_INSUFFICIENT_STAKE: u64 = 1;
    const E_NOT_OWNER: u64 = 2;
    const E_ALREADY_FROZEN: u64 = 3;
    const E_AGENT_FROZEN: u64 = 4;
    const E_INVALID_ENDPOINT: u64 = 5;

    /// Events
    struct AgentRegistered has copy, drop {
        agent_id: UID,
        owner: address,
        stake: u64,
    }

    struct AgentRevoked has copy, drop {
        agent_id: UID,
        owner: address,
    }

    /// Core resource
    resource AgentRegistration {
        id: UID,
        owner: address,
        protocol_digests: vector<Hash>,
        capabilities: vector<String>,
        endpoint: String,
        stake: u64,
        frozen: bool,
        created_at: u64,
    }

    /// Register a new agent (requires minimum stake)
    public fun register(
        owner: &signer,
        stake: Coin<QFC>,
        capabilities: vector<String>,
        endpoint: String,
    ): AgentRegistration { ... }

    /// Revoke and reclaim stake (after cooldown)
    public fun revoke(agent: AgentRegistration): Coin<QFC> { ... }

    /// Freeze agent (owner or governance)
    public fun freeze(agent: &mut AgentRegistration, caller: &signer) { ... }

    /// Update endpoint
    public fun update_endpoint(
        agent: &mut AgentRegistration,
        caller: &signer,
        new_endpoint: String,
    ) { ... }
}
```

### 3.2 Session Key 模块

```move
module qfc::session_keys {

    /// Permission bitmask
    const PERM_INFERENCE: u64    = 0x01;  // Submit inference tasks
    const PERM_TRANSFER: u64    = 0x02;  // Transfer tokens
    const PERM_STAKE: u64       = 0x04;  // Stake/unstake
    const PERM_REGISTER: u64   = 0x08;  // Register sub-agents

    resource SessionKey {
        id: UID,
        agent_id: UID,
        public_key: vector<u8>,
        permissions: u64,           // Bitmask
        spending_limit: u64,        // Max spend per period
        spent_this_period: u64,
        period_start: u64,
        period_duration: u64,       // e.g., 86400 for daily
        expires_at: u64,            // Absolute TTL
        nonce: u64,                 // Replay protection
    }

    /// Issue a new session key
    public fun issue(
        agent: &AgentRegistration,
        owner: &signer,
        public_key: vector<u8>,
        permissions: u64,
        spending_limit: u64,
        period_duration: u64,
        ttl: u64,
    ): SessionKey { ... }

    /// Validate a session key for an operation
    public fun validate(
        key: &mut SessionKey,
        operation: u64,     // Permission bit
        amount: u64,        // Spend amount
        provided_nonce: u64,
    ): bool { ... }

    /// Rotate: revoke old, issue new
    public fun rotate(
        old_key: SessionKey,
        owner: &signer,
        new_public_key: vector<u8>,
    ): SessionKey { ... }

    /// Revoke (destroy resource)
    public fun revoke(key: SessionKey, caller: &signer) { ... }
}
```

### 3.3 EVM Agent 账户合约

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@account-abstraction/contracts/interfaces/IAccount.sol";
import "@openzeppelin/contracts/proxy/utils/UUPSUpgradeable.sol";

contract QFCAgentAccount is IAccount, UUPSUpgradeable {
    address public owner;
    address public entryPoint;

    // Session keys
    mapping(address => SessionKeyData) public sessionKeys;

    struct SessionKeyData {
        uint64 permissions;
        uint256 spendingLimit;
        uint256 spentThisPeriod;
        uint64 periodStart;
        uint64 periodDuration;
        uint64 expiresAt;
        uint64 nonce;
        bool active;
    }

    // Spending limits
    uint256 public perTxLimit;
    uint256 public perPeriodLimit;

    // Contract allowlist
    mapping(address => bool) public allowedContracts;

    function validateUserOp(
        PackedUserOperation calldata userOp,
        bytes32 userOpHash,
        uint256 missingAccountFunds
    ) external override returns (uint256 validationData) {
        // 1. Check if signer is owner or valid session key
        // 2. Enforce spending limits
        // 3. Check contract allowlist
        // 4. Return SIG_VALIDATION_SUCCESS or SIG_VALIDATION_FAILED
    }

    function execute(address dest, uint256 value, bytes calldata data) external {
        require(msg.sender == entryPoint || msg.sender == owner);
        require(allowedContracts[dest] || dest == address(0), "Not allowed");
        require(value <= perTxLimit, "Exceeds per-tx limit");
        (bool success,) = dest.call{value: value}(data);
        require(success);
    }

    // Session key management (owner only)
    function addSessionKey(address key, SessionKeyData calldata data) external;
    function removeSessionKey(address key) external;

    // Policy management (owner only)
    function setPerTxLimit(uint256 limit) external;
    function setPerPeriodLimit(uint256 limit) external;
    function addAllowedContract(address contract_) external;
    function removeAllowedContract(address contract_) external;
}
```

### 3.4 JSON-RPC API 端点

| 方法 | 参数 | 返回 |
|--------|--------|---------|
| `qfc_registerAgent` | `{owner, stake, capabilities, endpoint}` | `{agent_id, tx_hash}` |
| `qfc_revokeAgent` | `{agent_id, owner_sig}` | `{tx_hash, stake_returned}` |
| `qfc_freezeAgent` | `{agent_id, caller_sig}` | `{tx_hash}` |
| `qfc_getAgent` | `{agent_id}` | `AgentRegistration` |
| `qfc_listAgents` | `{capability?, limit, offset}` | `AgentRegistration[]` |
| `qfc_issueSessionKey` | `{agent_id, pubkey, permissions, limit, ttl}` | `{session_key_id, tx_hash}` |
| `qfc_revokeSessionKey` | `{session_key_id, owner_sig}` | `{tx_hash}` |
| `qfc_getSessionKeys` | `{agent_id}` | `SessionKey[]` |
| `qfc_fundAgent` | `{agent_id, amount}` | `{tx_hash}` |
| `qfc_getAgentBalance` | `{agent_id}` | `{balance, stake}` |

### 3.5 E2E 测试场景

| ID | 场景 | 预期 |
|----|----------|----------|
| T1 | 以最低质押额注册 Agent | 成功，返回 agent_id |
| T2 | 以不足的质押额注册 Agent | 回滚 `E_INSUFFICIENT_STAKE` |
| T3 | 签发带 PERM_INFERENCE 的 session key | 密钥创建成功，可提交推理 |
| T4 | Session key 超出支出限额 | 回滚，交易被拒绝 |
| T5 | Session key 过期（超过 TTL） | 回滚，密钥无效 |
| T6 | Session key 权限不匹配（持有 INFERENCE，尝试 TRANSFER） | 回滚 |
| T7 | 所有者撤销 session key，密钥尝试操作 | 回滚，密钥已销毁 |
| T8 | 冻结 Agent 后尝试任意操作 | 所有操作回滚 |
| T9 | 撤销 Agent，冷却期后返还质押 | 质押返还给所有者 |
| T10 | 非所有者尝试冻结 Agent | 回滚 `E_NOT_OWNER` |

---

## 4. 里程碑 M2：Gas 代付 / Paymaster（P1）

### 4.1 Paymaster 合约

```solidity
contract QFCPaymaster is IPaymaster {
    address public entryPoint;
    address public owner;

    // Sponsor deposits
    mapping(address => uint256) public sponsorDeposits;

    // Per-agent sponsorship config
    struct SponsorshipConfig {
        address sponsor;
        uint256 maxPerOp;          // Max gas cost per UserOp
        uint256 maxPerDay;         // Daily cap
        uint256 spentToday;
        uint64 dayStart;
        bool active;
    }

    mapping(address => SponsorshipConfig) public agentSponsorship;

    function validatePaymasterUserOp(
        PackedUserOperation calldata userOp,
        bytes32 userOpHash,
        uint256 maxCost
    ) external override returns (bytes memory context, uint256 validationData) {
        address agent = userOp.sender;
        SponsorshipConfig storage config = agentSponsorship[agent];

        require(config.active, "No sponsorship");
        require(maxCost <= config.maxPerOp, "Exceeds per-op limit");

        // Reset daily counter if new day
        if (block.timestamp >= config.dayStart + 1 days) {
            config.spentToday = 0;
            config.dayStart = uint64(block.timestamp);
        }

        require(config.spentToday + maxCost <= config.maxPerDay, "Daily limit");
        config.spentToday += maxCost;

        return (abi.encode(agent, maxCost), 0);
    }

    function postOp(
        PostOpMode mode,
        bytes calldata context,
        uint256 actualGasCost,
        uint256 actualUserOpFeePerGas
    ) external override {
        (address agent, uint256 maxCost) = abi.decode(context, (address, uint256));
        // Refund over-charge
        uint256 refund = maxCost - actualGasCost;
        if (refund > 0) {
            agentSponsorship[agent].spentToday -= refund;
        }
    }

    // Sponsor management
    function deposit() external payable;
    function withdraw(uint256 amount) external;
    function sponsorAgent(address agent, uint256 maxPerOp, uint256 maxPerDay) external;
    function revokeSponsor(address agent) external;
}
```

### 4.2 代付流程

```
所有者/赞助方                     Paymaster                 EntryPoint
    │                               │                          │
    ├── deposit() ─────────────────►│                          │
    ├── sponsorAgent(agent) ───────►│                          │
    │                               │                          │
Agent（通过 session key）           │                          │
    ├── UserOp (paymasterAndData) ──┼─────────────────────────►│
    │                               │◄── validatePaymasterUserOp
    │                               │── 校验限额 ──────────────►│
    │                               │                          ├── 执行
    │                               │◄──────── postOp（退款）  │
```

---

## 5. 里程碑 M3：区块浏览器升级（P1）

### 5.1 新增浏览器页面

| 页面 | URL | 内容 |
|------|-----|---------|
| Agent 列表 | `/agents` | 所有已注册 Agent、状态、能力、质押 |
| Agent 详情 | `/agents/:id` | Agent 信息、session key、交易历史、支出 |
| Agent 仪表盘 | `/agents/dashboard` | 运营者视图：名下全部 Agent、告警、支出趋势 |
| Session Key 管理器 | `/agents/:id/keys` | 活跃密钥、权限、使用情况、撤销按钮 |

### 5.2 浏览器 API 端点

| 端点 | 方法 | 返回 |
|----------|--------|---------|
| `GET /api/agents` | List | 带过滤条件的分页 Agent 列表 |
| `GET /api/agents/:id` | Detail | 完整 Agent 信息 + 近期活动 |
| `GET /api/agents/:id/transactions` | History | Agent 的交易历史 |
| `GET /api/agents/:id/session-keys` | Keys | 活跃 session key 及使用统计 |
| `GET /api/agents/:id/spending` | Analytics | 按周期、按合约的支出分析 |
| `GET /api/agents/stats` | Overview | Agent 总数、总质押量、活跃数量 |

### 5.3 索引器需求

浏览器索引器必须订阅以下链上事件：

```solidity
event AgentRegistered(bytes32 indexed agentId, address indexed owner, uint256 stake);
event AgentRevoked(bytes32 indexed agentId, address indexed owner, uint256 stakeReturned);
event AgentFrozen(bytes32 indexed agentId, address indexed caller);
event SessionKeyIssued(bytes32 indexed agentId, address indexed key, uint64 permissions, uint64 expiresAt);
event SessionKeyRevoked(bytes32 indexed agentId, address indexed key);
event AgentFunded(bytes32 indexed agentId, uint256 amount);
event SponsorshipConfigured(address indexed agent, address indexed sponsor, uint256 maxPerDay);
```

### 5.4 数据库 Schema

```sql
CREATE TABLE agents (
    agent_id        TEXT PRIMARY KEY,
    owner           TEXT NOT NULL,
    capabilities    JSONB,
    endpoint        TEXT,
    stake           NUMERIC NOT NULL,
    frozen          BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMP NOT NULL,
    revoked_at      TIMESTAMP,
    tx_hash         TEXT NOT NULL
);

CREATE TABLE session_keys (
    key_id          TEXT PRIMARY KEY,
    agent_id        TEXT REFERENCES agents(agent_id),
    public_key      TEXT NOT NULL,
    permissions     BIGINT NOT NULL,
    spending_limit  NUMERIC,
    spent_this_period NUMERIC DEFAULT 0,
    period_duration INTEGER,
    expires_at      TIMESTAMP NOT NULL,
    revoked_at      TIMESTAMP,
    created_tx      TEXT NOT NULL
);

CREATE TABLE agent_transactions (
    tx_hash         TEXT PRIMARY KEY,
    agent_id        TEXT REFERENCES agents(agent_id),
    session_key     TEXT,
    action          TEXT NOT NULL,  -- 'inference', 'transfer', 'stake', etc.
    value           NUMERIC,
    target_contract TEXT,
    timestamp       TIMESTAMP NOT NULL,
    status          TEXT NOT NULL   -- 'success', 'reverted'
);

CREATE TABLE agent_sponsorships (
    agent_address   TEXT NOT NULL,
    sponsor         TEXT NOT NULL,
    max_per_op      NUMERIC,
    max_per_day     NUMERIC,
    spent_today     NUMERIC DEFAULT 0,
    active          BOOLEAN DEFAULT TRUE,
    PRIMARY KEY (agent_address, sponsor)
);

CREATE INDEX idx_agents_owner ON agents(owner);
CREATE INDEX idx_agent_tx_agent ON agent_transactions(agent_id, timestamp DESC);
CREATE INDEX idx_session_keys_agent ON session_keys(agent_id);
```

---

## 6. 里程碑 M4：OpenClaw 集成（P2）

### 6.1 新增 OpenClaw 命令

| 命令 | 说明 |
|---------|-------------|
| `agent register` | 注册新 Agent（含质押和能力声明） |
| `agent fund <agent_id> <amount>` | 为 Agent 钱包注资 |
| `agent revoke <agent_id>` | 撤销 Agent 并收回质押 |
| `agent list` | 列出当前钱包名下所有 Agent |
| `agent status <agent_id>` | 显示 Agent 状态、余额、活跃 session key |
| `session-key issue <agent_id>` | 签发带权限的新 session key |
| `session-key revoke <key_id>` | 撤销 session key |
| `session-key list <agent_id>` | 列出活跃 session key |

### 6.2 OpenClaw Agent 钱包客户端

```typescript
// qfc-openclaw-skill/src/agent-wallet.ts
import { QFCClient } from '@qfc/sdk-js';

export class AgentWalletClient {
    constructor(
        private qfc: QFCClient,
        private sessionKey?: { privateKey: string; agentId: string }
    ) {}

    // Use session key instead of owner key for operations
    async submitInference(task: InferenceTask): Promise<InferenceResult> {
        if (this.sessionKey) {
            return this.qfc.submitInferenceWithSessionKey(
                task,
                this.sessionKey.privateKey,
                this.sessionKey.agentId
            );
        }
        return this.qfc.submitInference(task);
    }

    async register(params: RegisterParams): Promise<AgentRegistration> { ... }
    async fund(agentId: string, amount: bigint): Promise<TxHash> { ... }
    async revoke(agentId: string): Promise<{ txHash: string; stakeReturned: bigint }> { ... }
    async issueSessionKey(params: SessionKeyParams): Promise<SessionKey> { ... }
    async revokeSessionKey(keyId: string): Promise<TxHash> { ... }
}
```

### 6.3 演示场景

| 演示 | 说明 |
|------|-------------|
| **自主交易员** | 注册 Agent → 签发 session key（INFERENCE + TRANSFER）→ Agent 运行情绪分析 → 执行交易 → 所有者通过浏览器监控 |
| **内容生成器** | 注册 Agent → 签发 session key（仅 INFERENCE）→ Agent 定时生成内容 → 结果上链存储 |
| **AI 预言机** | 注册 Agent → 通过 Paymaster 代付 gas → Agent 回答链上查询 → 收益分配给代币持有者 |
| **多 Agent 流水线** | 注册 3 个 Agent → 通过意图（intent）串联 → 分类 → 分析 → 总结 |

---

## 7. 跨仓库依赖图

```
qfc-contracts (Solidity)
  ├── QFCAgentAccount.sol        ─── M1
  ├── QFCAccountFactory.sol      ─── M1
  ├── QFCPaymaster.sol           ─── M2
  └── PolicyManager.sol          ─── M1

qfc-core (Rust)
  ├── qfc-qvm/agent_registry     ─── M1
  ├── qfc-qvm/session_keys       ─── M1
  ├── qfc-rpc/agent_endpoints    ─── M1
  └── qfc-executor/erc4337       ─── M1

qfc-sdk-js (TypeScript)
  ├── AgentWalletClient          ─── M1
  └── PaymasterClient            ─── M2

qfc-explorer (Next.js)
  ├── /agents 页面                ─── M3
  ├── API 端点                    ─── M3
  └── 索引器事件                  ─── M3

qfc-openclaw-skill (TypeScript)
  ├── agent 命令                  ─── M4
  ├── session-key 命令            ─── M4
  └── AgentWalletClient           ─── M4
```

### 执行时间线

```
周:    1   2   3   4   5   6   7   8
       ├───────────────┤
       M1: 核心 + Session Key + 测试
                ├───────────┤
                M2: Paymaster
                    ├───────────┤
                    M3: 浏览器
                            ├───────┤
                            M4: OpenClaw
```

**总计：1-2 名开发者 + Claude Code，约 8 周。**

---

## 8. 安全模型

### 8.1 纵深防御层级

| 层级 | 机制 | 强制执行方 |
|-------|-----------|-------------|
| 1. VM 层 | 资源不可伪造/复制 | QVM |
| 2. Session key | TTL + 权限位掩码 + 支出限额 | QVM + EVM |
| 3. 钱包策略 | 单笔限额、周期限额、合约白名单 | EVM（QFCAgentAccount） |
| 4. 时间锁 | 大额提现需延迟 | EVM（PolicyManager） |
| 5. 熔断开关 | 所有者/治理可冻结 Agent | QVM |
| 6. 审计轨迹 | 所有操作记录在不可篡改账本上 | 区块链 |

### 8.2 威胁模型

| 威胁 | 缓解措施 |
|--------|------------|
| 提示词注入 → 未授权交易 | Session key 权限限制影响范围 |
| Session key 泄露 | TTL 自动过期；所有者可立即撤销 |
| 所有者私钥泄露 | 大额提现受时间锁约束；高价值操作需多方审批 |
| Paymaster 被抽干 | 每 Agent 每日上限；赞助方可撤销 |
| 恶意 Agent 抽干资金 | 单笔与周期支出限额 |
| 多 Agent 合谋 | 合约白名单限制交互面 |
| 重放攻击 | Session key 的 nonce 防护 |

### 8.3 密钥轮换策略

- Session key：建议最大 TTL 为 7 天
- 所有者私钥：支持通过 `transferOwnership()` 轮换
- 自动密钥轮换：OpenClaw 可在旧密钥过期前签发新密钥

---

## 9. 测试策略

### 9.1 测试金字塔

| 层级 | 数量 | 仓库 | 框架 |
|-------|-------|------|-----------|
| 单元测试（QVM） | ~30 | qfc-core | Rust `#[test]` |
| 单元测试（Solidity） | ~50 | qfc-contracts | Foundry |
| 集成测试 | ~20 | qfc-core | Rust 集成测试 |
| E2E | ~10 | qfc-core | 多节点测试网 |
| UI | ~15 | qfc-explorer | Playwright |

### 9.2 验收标准

1. ✅ Agent 在 QVM 上完成带质押注册
2. ✅ 签发带权限位掩码的 session key
3. ✅ Session key 强制执行周期支出限额
4. ✅ 过期 session key 被拒绝
5. ✅ 已撤销 session key 被拒绝
6. ✅ Agent 被冻结 → 所有操作失败
7. ✅ Agent 被撤销 → 冷却期后返还质押
8. ✅ ERC-4337 UserOp 通过 QFCAgentAccount 验证
9. ✅ Paymaster 为 Agent 操作代付 gas
10. ✅ Paymaster 强制执行每日支出上限
11. ✅ 浏览器展示带状态的 Agent 列表
12. ✅ 浏览器展示 session key 详情
13. ✅ 浏览器展示 Agent 交易历史
14. ✅ OpenClaw `agent register` 命令可用
15. ✅ OpenClaw `session-key issue` 命令可用
16. ✅ OpenClaw 可用 session key 执行推理（无需所有者私钥）
17. ✅ 完整演示：注册 → 注资 → 签发密钥 → 推理 → 监控 → 撤销

---

## 参考资料

- [24-AI-AGENT-FRAMEWORK.md](./24-AI-AGENT-FRAMEWORK-CN.md) — 研究基础
- [28-V3-ROADMAP.md](./28-V3-ROADMAP-CN.md) — v3.0 总体路线图
- [ERC-4337 规范](https://eips.ethereum.org/EIPS/eip-4337)
- [Account Abstraction 概览 — Alchemy](https://www.alchemy.com/overviews/what-is-account-abstraction)
