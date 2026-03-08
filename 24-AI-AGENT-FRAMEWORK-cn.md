# AI Agent 链上框架与 QFC 机遇

> 最后更新: 2026-03-08 | 版本 1.0
> GitHub Issue: #6
> 作者: Alex Wei, 产品经理 @ QFC Network

---

## 1. 摘要

链上 AI Agent——在区块链上自主执行交易的程序——市场规模超过 $3B（2025 年 10 月峰值 $4.34B）。QFC 的双 VM（EVM + QVM）和原生 AI 推理协调器创造了成为最佳 AI Agent 平台的独特机遇。

**核心发现：**

- **Virtuals Protocol**（市值 $915M）开创了 Agent 代币化；收入分成模式创造了真实价值
- **ElizaOS** 是主流的开源 Agent 框架（3,800+ star）；TypeScript，基于插件
- **Autonolas** 拥有最成熟的可组合性模型（组件 → Agent → 服务注册为 NFT）
- 每个现有 Agent 框架都需要**链下桥接**进行 AI 推理——QFC 可以实现**链上原生**
- QVM 的 Move 风格资源类型提供了比纯 EVM 方案**更强的 Agent 安全保障**

**建议**：将 QFC 定位为"Agent 原生 AI 链"——推理是一等原语，Agent 能力由 VM 强制执行的资源控制，EVM 兼容性支持代币化。

---

## 2. 主要 Agent 项目

### 2.1 Virtuals Protocol（VIRTUAL，约 $915M 市值）

**平台**：Base（Ethereum L2）+ Solana。AI Agent 的代币化和共同所有权。

**GAME 框架**（General Autonomous Modular Entity）：
- 可组合、模块化的 Agent，分离规划和执行
- Agent 发布：100 VIRTUAL 费用 → 联合曲线 → 在 42,000 VIRTUAL 时永久 LP
- 每个 Agent 是与 VIRTUAL 配对的 ERC-20 代币

**收入分配**：

| 接收方 | 份额 |
|-----------|-------|
| Agent 自有钱包 | 60% |
| Agent 代币回购销毁 | 30% |
| Virtuals 国库 | 10% |

**规模**：Agent 总市值 >$500M，650K+ VIRTUAL 持有者。

### 2.2 ElizaOS（前身为 ai16z / ELIZA）

**概述**：具有区块链集成功能的自主 AI Agent 开源 TypeScript 框架。

**架构**：
- 模块化插件系统——核心运行时无需修改即可扩展
- 支持多种 LLM 后端（OpenAI、LLaMA、Qwen）和多条链
- 插件涵盖：NFT 生成、区块链分析、DeFi 操作、资产组合管理

**产品**：
- **Auto.fun**（2025 年 4 月）：无代码 Agent 创建平台
- **elizaOS v2**（2025 年 10 月）：多链架构

**规模**：3,800+ GitHub star，1,100+ fork，138+ 贡献者。

### 2.3 Autonolas（OLAS，2025 年 2 月融资 $13.8M）

**概述**：可组合、去中心化多 Agent 服务（MAS）协议。

**架构**：
- **Open Autonomy 框架**：多 Agent 系统在链下运行，链上协调
- **NFT 注册表**：组件 → Agent → 服务，分别注册为 NFT
- **POSE**（Protocol-Owned Services）：协议本身拥有并运营 Agent 服务

**规模**：700K+ 交易/月，跨 9 条区块链总计 3.5M+。

**代币经济学**：OLAS 协调资本与代码的配对。开发者按贡献获得收益；运营者因运行服务获得收益；绑定者提供流动性。

### 2.4 Spectral（Syntax）

**概述**：自然语言 → Solidity 智能合约，自主部署。

- 每个 Agent 获得智能钱包（Turnkey HSM 支持）用于无信任部署
- 60K+ 用户，1M+ 合约生成，4,700+ 模因币发行
- 正在构建 **InferChain**：AI 推理验证专用链

**QFC 相关性**：QFC 已经拥有 InferChain 试图构建的功能——原生推理验证。

### 2.5 Fetch.ai

**概述**：Agent 通信和发现平台。

- **uAgents 框架**：轻量级 Python 微 Agent 库
- **Almanac 合约**：去中心化 Agent 注册表（类似 Agent 的 DNS）
- **DeltaV**：将请求匹配到 Agent 的 AI 搜索界面
- **Agent 通信协议（ACP）**：Agent 通过协议摘要相互发现

---

## 3. Agent 安全模式

| 控制措施 | 描述 | 实现方式 |
|---------|-------------|---------------|
| **消费限额** | 单笔和周期上限 | 链上强制执行 |
| **合约白名单** | Agent 只能与白名单合约交互 | 钱包策略 |
| **终止开关** | 所有者冻结 Agent 钱包/撤销签名 | 管理函数 |
| **时间锁** | 大额提款需要延迟 | 时间锁合约 |
| **多方审批** | 高价值操作的门限签名 | 多签 |
| **审计追踪** | 所有操作记录在不可变账本上 | 区块链固有特性 |
| **熔断器** | 异常行为时自动暂停 | 监控合约 |

**威胁模型**（来自学术综述，arxiv 2601.04583）：
- 提示注入 → 未授权交易
- 策略滥用 → Agent 绕过边界
- 密钥泄露
- 多 Agent 串谋

---

## 4. Agent-合约交互模型

| 模型 | 描述 | 安全性 | 使用者 |
|-------|-------------|----------|---------|
| **EOA + 私钥** | Agent 直接持有密钥 | 弱——无链上策略 | 早期项目 |
| **账户抽象（ERC-4337）** | 通过智能合约钱包的 UserOperations | **强**——可编程策略 | Spectral，新兴标准 |
| **多 Agent 门限** | 多个 Agent 共同签名 | 最强——无单点故障 | Autonolas MAS |

**ERC-4337 是新兴标准**：具有自定义验证逻辑（消费限额、白名单、Paymaster 的 Gas 抽象）的智能合约钱包。

---

## 5. 市场数据

| 指标 | 值 |
|--------|-------|
| AI Agent 板块市值 | 约 $3.06B（2026 年 3 月） |
| 峰值市值 | 约 $4.34B（2025 年 10 月） |
| AI Agent 项目数量 | 550+ |
| 峰值 24 小时交易量 | 约 $1.09B |

**头部代币**：VIRTUAL（约 $915M）、FET（ASI Alliance）、TRAC（约 $356M）、OLAS。

---

## 6. QFC 在 AI Agent 领域的差异化

### 6.1 缺口：每个 Agent 框架都需要链下桥接进行 AI 推理

```
当前 Agent 架构（Virtuals、ElizaOS、Spectral）：

  Agent 链上 → 调用链下 API → AI 推理 → 结果返回链上
                ^^^^^^^^^^^^^^^^
                信任缺口：谁来验证推理是否正确？
```

QFC 消除了这一信任缺口：

```
QFC Agent 架构：

  Agent 链上 → 调用 QFC AI 协调器 → 矿工执行推理 →
  → 已验证结果（抽查 / zkML）→ 结果作为 Resource 上链
                                 ^^^^^^^^^^^^^^^^^^^^^^^^
                                 已验证、可组合、类型安全
```

### 6.2 资源类型化的 Agent 能力（QVM）

在 EVM 上，Agent 权限由合约逻辑执行（可能有漏洞）。在 QVM 上，Agent 能力是 **VM 强制执行的资源**：

```move
// Agent 能力：有权在推理上花费最多 100 QFC
resource InferenceCapability {
    id: UID,
    owner: address,
    remaining_budget: u64,    // 只能由授权函数修改
    allowed_models: vector<ModelId>,
    expires_at: u64,
}

// Agent 请求推理——必须出示并消费能力
public fun request_inference(
    cap: &mut InferenceCapability,
    task: InferenceTask,
): InferenceResult {
    assert!(cap.remaining_budget >= task.fee, E_INSUFFICIENT_BUDGET);
    cap.remaining_budget -= task.fee;
    // 提交到 AI 协调器...
}
```

**为什么比 EVM 更强**：
- `InferenceCapability` 在 VM 层面无法伪造、复制或超额消费
- 无重入风险——资源被线性消费
- 终止开关 = 简单地销毁或冻结能力资源

### 6.3 双 VM 可组合性

| 层 | VM | 角色 |
|-------|-----|------|
| Agent 代币化与交易 | **EVM** | ERC-20 Agent 代币，Uniswap 风格 LP（Virtuals 模式） |
| Agent 注册与组合 | **QVM** | 组件 → Agent → 服务作为 Resource（Autonolas 模式） |
| AI 推理 | **QFC AI 协调器** | 原生、已验证的推理作为一等原语 |
| DeFi 集成 | **EVM** | 现有 Solidity DeFi 协议（跨 VM 调用） |
| Agent 钱包 | **EVM** | ERC-4337 账户抽象（已支持） |

### 6.4 Agent 注册表即 Resource（Fetch.ai Almanac + QVM）

```move
resource AgentRegistration {
    id: UID,
    owner: address,
    protocol_digests: vector<Hash>,    // 该 Agent 支持的协议
    capabilities: vector<String>,       // "text-generation"、"image-analysis" 等
    endpoint: String,                   // 如何联系该 Agent
    stake: u64,                         // 利益绑定
}
```

- Agent 通过创建 Resource 注册（需要质押）
- 发现：按 protocol_digest 或能力查询
- 转让：Agent 可被出售/转让（Resource 所有权转移）
- 不可复制（Move 保证）

---

## 7. 推荐架构

### 7.1 QFC Agent 技术栈

```
┌─────────────────────────────────────────────────┐
│  用户 / DApp                                     │
│  "我需要一个基于 AI 情绪分析                       │
│   进行交易的 Agent"                               │
├─────────────────────────────────────────────────┤
│  Agent 运行时（ElizaOS 插件 / 自定义）              │
│  链下 Agent 逻辑，LLM 规划                        │
├─────────────────────────────────────────────────┤
│  QFC SDK（qfc-sdk-js / qfc-sdk-python）           │
│  提交推理任务，管理能力                              │
├────────────────────┬────────────────────────────┤
│  EVM 层            │  QVM 层                     │
│  - Agent 代币      │  - Agent 注册表              │
│  - ERC-4337 钱包   │  - 能力资源                  │
│  - DeFi 协议       │  - 推理结果                  │
│  - Paymaster       │  - 终止开关                  │
├────────────────────┴────────────────────────────┤
│  QFC AI 协调器                                    │
│  - 任务提交 → 矿工分配                             │
│  - 验证（抽查 / zkML）                             │
│  - 结果以 Resource 形式交付                         │
└─────────────────────────────────────────────────┘
```

### 7.2 ElizaOS 集成路径

由于 ElizaOS 是 TypeScript 且基于插件，集成非常简单：

```typescript
// qfc-elizaos-plugin（封装 qfc-sdk-js）
export const qfcPlugin: Plugin = {
    name: "qfc-inference",
    actions: [
        {
            name: "RUN_INFERENCE",
            description: "Run AI inference on QFC network",
            handler: async (runtime, message) => {
                const result = await qfcClient.submitInference({
                    model: "qfc-llm-7b",
                    prompt: message.content,
                    maxTokens: 500,
                });
                return result.output;
            },
        },
    ],
};
```

无需 fork ElizaOS——只需将插件发布到 npm。

---

## 8. 实施路线图

### 阶段一：Agent 能力资源（3-4 周）

| 任务 | 描述 |
|------|-------------|
| 在 QSC 中定义 `AgentCapability` 资源 | 消费限额、模型白名单、过期时间 |
| 实现能力门控推理 | AI 协调器在任务分配前检查能力 |
| 终止开关机制 | 资源冻结/销毁功能 |

### 阶段二：Agent 注册表（3-4 周）

| 任务 | 描述 |
|------|-------------|
| `AgentRegistration` 资源 | 包含协议摘要和能力元数据的注册表 |
| 发现 API | 按能力查询 Agent 的 RPC 端点 |
| 质押要求 | Agent 必须质押 QFC 才能注册（抗女巫攻击） |

### 阶段三：SDK 与框架集成（4-6 周）

| 任务 | 描述 |
|------|-------------|
| ElizaOS 插件 | 封装 qfc-sdk-js 的 `qfc-elizaos-plugin` |
| Agent 钱包模板 | 具有 QFC 特定验证的 ERC-4337 智能钱包 |
| 示例 Agent | 情绪交易 Agent、AI 预言机 Agent、内容生成 Agent |

### 阶段四：Agent 代币化（4-6 周）

| 任务 | 描述 |
|------|-------------|
| Agent 代币工厂 | 用于发行 Agent 代币的 EVM 合约（Virtuals 模式） |
| 收入分成 | 链上费用分配给 Agent 代币持有者 |
| 跨 VM 桥接 | Agent 代币（EVM）关联 Agent 能力（QVM） |

---

## 9. 竞争定位

| 功能 | Virtuals | ElizaOS | Autonolas | Fetch.ai | **QFC（目标）** |
|---------|----------|---------|-----------|----------|-----------------|
| Agent 代币化 | ✅ 核心功能 | ❌ | ❌ | ❌ | ✅（EVM） |
| Agent 可组合性 | 基础 | 基于插件 | ✅ NFT 注册表 | 协议摘要 | ✅ Resource 注册表 |
| 原生 AI 推理 | ❌ 链下 | ❌ 链下 | ❌ 链下 | ❌ 链下 | **✅ 链上已验证** |
| Agent 安全性 | 合约级别 | 应用级别 | 多 Agent 门限 | 应用级别 | **VM 强制执行的资源** |
| 智能合约交互 | 仅 EVM | 多链 | 多链 | 多链 | **双 VM（EVM + QVM）** |
| ERC-4337 支持 | ❌ | ❌ | ❌ | ❌ | ✅ |

**QFC 的独特定位**：唯一一个 Agent 可以请求**已验证 AI 推理作为原生区块链操作**且具有 **VM 级能力强制执行**的平台。

---

## 参考资料

- [Virtuals Protocol 白皮书](https://whitepaper.virtuals.io)
- [Virtuals Protocol 评测 - Coin Bureau](https://coinbureau.com/review/virtuals-protocol-review)
- [ElizaOS 文档](https://docs.elizaos.ai/)
- [ElizaOS GitHub](https://github.com/elizaOS/eliza)
- [Olas Network](https://olas.network/)
- [Spectral Labs](https://www.spectrallabs.xyz/)
- [Fetch.ai uAgents 框架](https://uagents.fetch.ai/docs)
- [Fetch.ai 架构论文（arxiv）](https://arxiv.org/html/2510.18699v1)
- [区块链上的自主 Agent（arxiv 2601.04583）](https://arxiv.org/abs/2601.04583)
- [AI 与加密 Agent 支付 - Chainalysis](https://www.chainalysis.com/blog/ai-and-crypto-agentic-payments/)
- [AI Agent 分类 - CoinGecko](https://www.coingecko.com/en/categories/ai-agents)
- [账户抽象 ERC-4337 - Alchemy](https://www.alchemy.com/overviews/what-is-account-abstraction)
