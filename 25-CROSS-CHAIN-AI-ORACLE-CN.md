# QFC 跨链 AI 预言机与互操作性

> 最后更新: 2026-03-08 | 版本 1.0
> GitHub Issue: #7
> 作者: Alex Wei, 产品经理 @ QFC Network

---

## 1. 摘要

QFC 在链上运行已验证的 AI 推理。为了最大化效用，推理结果应可被任何链上的智能合约消费。本报告评估跨链消息传递协议和 AI 预言机模式，以设计 QFC 的跨链 AI 预言机架构。

**核心发现：**

- **LayerZero V2**（160+ 链）和 **Hyperlane**（150+ 链，无需许可）是最佳选择——两者都允许自定义验证模块（DVN/ISM），QFC 可将其定制用于 AI 推理证明
- **Wormhole** 需要 Guardian 网络支持（集成较难）；**IBC** 是最小化信任的但与 Cosmos 耦合
- **ORA Protocol** 开创了链上 AI 预言机，通过 opML 欺诈证明——支持 7B+ 模型，快乐路径几乎零开销
- **Ritual Infernet** 拥有 8,000+ 节点在 Docker 容器中运行 AI 工作负载——最广泛的计算灵活性
- **协处理器模式**（读取 → 链下计算 → 证明 → 链上验证）是跨链 AI 的新兴标准

**建议**：将 QFC 实现为**跨链 AI 协处理器**，使用 Hyperlane 或 LayerZero 进行消息传递，并构建自定义验证模块来证明 QFC 的推理验证（验证者共识 + opML 升级）。

---

## 2. 跨链消息传递协议

### 2.1 LayerZero V2

**架构**：不可变、抗审查的消息传递协议，具有应用自主安全性。

| 组件 | 角色 |
|-----------|------|
| **Endpoint** | 部署在每条支持链上的入口/出口 |
| **超轻节点（ULN）** | 链上合约，无需存储完整区块数据即可验证交易证明 |
| **DVN（去中心化验证网络）** | 取代旧的 Oracle+Relayer；独立验证 `payloadHash` |
| **Executor** | 处理目标链上的消息交付 |

**消息流程**：
1. 源应用通过 Endpoint 发送消息 → 发出 `payloadHash`
2. 配置的 DVN 独立验证负载哈希
3. 一旦达到 DVN 阈值 → 消息 nonce 在目标链上被标记为"已验证"
4. Executor 将消息交付给接收应用

**关键特性**：
- **无需许可的 DVN**：任何人都可以用任何验证方案构建 DVN（多签、ZK、乐观、轻客户端）
- **应用自主安全性**：每个应用配置自己的 DVN 堆栈
- **热插拔**：应用可替换 DVN（例如多签 → zkOracle）而无需更改代码
- **支持 160+ 链**

**QFC 相关性**：QFC 可以构建自定义 DVN 来证明 AI 推理结果。无需 LayerZero 的审批即可集成。

### 2.2 Hyperlane

**架构**：完全无需许可的互操作性——任何链无需审批即可连接。

| 组件 | 角色 |
|-----------|------|
| **Mailbox** | 每条链上的入口/出口（类似 LayerZero Endpoint） |
| **ISM（链间安全模块）** | 可定制的智能合约，验证消息真实性 |
| **Validator** | 对源链消息签署证明 |
| **Relayer** | 将消息 + 元数据交付到目标链 |

**ISM 选项**：

| ISM 类型 | 描述 |
|----------|-------------|
| 多签 ISM | N-of-M 验证者签名 |
| 乐观 ISM | 假定有效，除非被挑战 |
| ZK 轻客户端 ISM | 通过 ZK 证明的密码学验证 |
| 路由 ISM | 不同源链使用不同 ISM |
| 自定义 ISM | 任意验证逻辑 |

**关键特性**：
- **无需许可部署**：可部署到任何 EVM、Sealevel（Solana）、CosmWasm 或 Move 链
- **无需白名单**或治理投票
- **多 VM 支持**：EVM、Solana、CosmWasm、Move、Fuel VM
- **150+ 链**

**QFC 相关性**：可以说是最佳选择。QFC 可以部署 Hyperlane 合约，构建验证 AI 推理证明的自定义 ISM，并立即被任何 Hyperlane 连接的链访问。

### 2.3 Wormhole

**架构**：由 19 个独立机构节点运营者组成的 Guardian 网络。

| 组件 | 角色 |
|-----------|------|
| **Guardian** | 19 个独立验证者（Jump Crypto、Certus One 等） |
| **VAA（已验证操作批准）** | 需要 13/19 Guardian 签名的签名证明 |
| **核心桥接** | 每条链上发出/验证 VAA 的合约 |
| **NTT（原生代币转移）** | 无需流动性池的代币转移 |

**特性**：固定的 Guardian 集合更简单但灵活性较低。2025 年优化将延迟降低了约 40%。强力的 Solana 支持。

**QFC 相关性**：VAA 模式有借鉴意义——QFC 推理结果可以类似地封装为签名证明。但固定的 Guardian 集合使自定义集成更困难。

### 2.4 IBC（跨区块链通信）

**架构**：基于轻客户端的验证——最小化信任互操作性的黄金标准。

| 层 | 组件 |
|-------|------------|
| 传输层（TAO） | 轻客户端、连接、通道、中继器 |
| 应用层 | 代币转移（ICS-20）、链间账户（ICS-27） |

**验证工作原理**：
- 每条链维护其对手方的链上轻客户端
- 轻客户端跟踪共识状态（验证者集合、区块头）
- 中继器提交数据包 + Merkle 证明 → 对照轻客户端验证
- **零额外信任假设**——纯密码学

**IBC v2（2025）**：旨在将 IBC 从 Cosmos 扩展到任何链。

**QFC 相关性**：最小化信任的选项。如果 QFC 实现确定性最终性（例如文档 #21 中的 Mysticeti 变体共识），可原生支持 IBC。实现成本高但安全性最高。

### 2.5 Chainlink CCIP

**架构**：由 Chainlink OCR 2.0 预言机基础设施 + 独立风险管理网络保护的跨链消息传递。

| 属性 | 值 |
|----------|-------|
| 链覆盖 | 60+ |
| 安全模型 | DON 共识 + 风险管理网络 |
| 安全保护的总价值 | $93B+（2025 年中） |
| 集成方式 | 需要 Chainlink 合作 |

**QFC 相关性**：展示了基于 DON 聚合的价值。QFC 可定位为专门的 AI 计算 DON——不同于 Chainlink Functions（调用外部 API），QFC 使用密码学/经济证明原生运行推理。

---

## 3. 协议比较

| 协议 | 链数 | 信任模型 | 自定义验证 | 集成工作量 | 最适用于 |
|----------|--------|-------------|--------------------|--------------------|----------|
| **LayerZero** | 160+ | 应用可配置（DVN） | ✅ 自定义 DVN | 中等 | 最广泛的 EVM 覆盖 |
| **Hyperlane** | 150+ | 应用可配置（ISM） | ✅ 自定义 ISM | 中等 | 无需许可、多 VM |
| **Wormhole** | 30+ | 13/19 Guardian | ❌ 固定 Guardian 集合 | 高 | Solana 生态 |
| **IBC** | Cosmos 生态 | 密码学（轻客户端） | ⚠️ 需要兼容的共识 | 非常高 | 最高安全性 |
| **Chainlink CCIP** | 60+ | DON + 风险网络 | ❌ 需要合作关系 | 高 | 企业/机构 |

**建议**：**Hyperlane**（首选）或 **LayerZero**（备选）。两者都允许无需许可的自定义验证模块，QFC 可构建 AI 专用验证器。

---

## 4. AI 预言机格局

### 4.1 ORA Protocol（OAO——链上 AI 预言机）

**方法**：opML（乐观机器学习）——受乐观 Rollup 启发的交互式欺诈证明。

| 属性 | 值 |
|----------|-------|
| 最大模型大小 | 消费级硬件上 7B+（32GB 内存） |
| 快乐路径开销 | 约 0 倍（除非被挑战，否则不生成证明） |
| 挑战期 | 分钟级 |
| 安全模型 | 经济（质押 + 欺诈证明） |
| 部署在 | Ethereum、Arbitrum 及其他 EVM 链 |
| 支持的模型 | LLaMA 3、Stable Diffusion |

**工作原理**：
1. AI 推理在链下运行 → 结果乐观地发布到链上
2. 挑战窗口开启
3. 如被挑战 → 通过欺诈证明 VM 逐步重新执行
4. 挑战者或证明者没收质押

**2025 年更新**："弹性模型服务"和"opAgent"用于可验证 AI Agent。

### 4.2 Ritual Infernet

**架构**：链下 Infernet 节点在 Docker 容器中执行 AI 工作负载。链上 SDK 提供 `CallbackConsumer` 和 `SubscriptionConsumer` 接口。

| 属性 | 值 |
|----------|-------|
| 节点数 | 8,000+ 独立节点 |
| 计算模型 | 任何 Docker 容器（任何模型、任何框架） |
| 交付方式 | 一次性回调或循环订阅 |
| 链 | Ritual Chain（无信任执行层） |
| 验证 | 发展中（不如 ORA 成熟） |

### 4.3 验证方法比较

| 方法 | 安全性 | 延迟 | 成本 | 模型大小 |
|----------|----------|---------|------|------------|
| **zkML** | 密码学（最高） | 分钟到小时（大模型） | 非常高 | 实际 <1B |
| **opML** | 经济（欺诈证明） | 挑战期（分钟） | 低 | 7B+ 可行 |
| **TEE** | 硬件信任 | 接近原生速度 | 低 | 受限于飞地内存 |
| **多签/委员会** | 诚实多数 | 快 | 低 | 无限制 |
| **QFC 分层**（文档 #20） | 自适应 | 按层级变化 | 变化 | 无限制 |

---

## 5. 协处理器模式

跨链可验证计算的新兴标准：

```
读取链上状态 → 链下计算 → 证明正确性 → 链上验证
```

### 5.1 ZK 协处理器项目

| 项目 | 方法 | 关键基准 |
|---------|----------|---------------|
| **Axiom** | 读取以太坊历史状态 + ZK 证明 | 以太坊生产环境运行 |
| **Brevis** | 基于 zkVM 的协处理器 | 证明 45M gas 区块平均延迟 6.9 秒 |
| **Lagrange** | ZK 协处理器 + DeepProve（zkML 证明器） | 最快的 zkML 证明器 |
| **Giza** | StarkNet 上的逐推理 ZK 证明 | 专注小型模型 |

### 5.2 QFC 作为 AI 协处理器

QFC 本身就是原生 AI 协处理器。关键问题是：如何将推理结果封装供跨链消费。

```
[请求链]                        [QFC 链]                       [请求链]

智能合约  ─LayerZero/→  QFC Endpoint 合约              结果 + 证明
(推理请求)  Hyperlane    ├─ 解码请求                    ─LayerZero/→  回调
                         ├─ 路由到矿工池                Hyperlane     合约
                         ├─ 矿工执行推理                              (已验证
                         ├─ 对结果达成共识                              结果)
                         ├─ 生成证明
                         └─ 发出跨链消息
```

---

## 6. QFC 跨链 AI 预言机设计

### 6.1 架构概览

```
┌──────────────────────────────────────────────────────────┐
│  外部链（Ethereum、Arbitrum、Solana 等）                    │
│  ┌────────────────────┐  ┌────────────────────────────┐  │
│  │ 请求合约            │  │ QFC 预言机接收合约           │  │
│  │ - submitRequest()  │  │ - receiveResult()           │  │
│  │ - 回调处理器        │  │ - 验证证明                   │  │
│  └────────┬───────────┘  └────────────▲───────────────┘  │
│           │                           │                    │
├───────────┼───────────────────────────┼────────────────────┤
│  跨链层（Hyperlane/LayerZero）                              │
│  ┌────────┴───────────────────────────┴───────────────┐   │
│  │  自定义 ISM/DVN：QFC 推理验证器                      │   │
│  │  - 验证推理结果的验证者签名                           │   │
│  │  - 可选：验证 opML 欺诈证明                          │   │
│  │  - 可选：验证 ZK 证明（第一层模型）                   │   │
│  └────────────────────────┬───────────────────────────┘   │
├───────────────────────────┼────────────────────────────────┤
│  QFC 链                   │                                │
│  ┌────────────────────────┴───────────────────────────┐   │
│  │  跨链预言机协调器                                    │   │
│  │  ├─ 接收跨链推理请求                                 │   │
│  │  ├─ 路由到 AI 协调器（现有 TaskPool）                │   │
│  │  ├─ 收集已验证结果                                   │   │
│  │  ├─ 生成证明（验证者共识）                            │   │
│  │  └─ 发出跨链响应                                     │   │
│  └─────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────┘
```

### 6.2 验证策略（混合）

参照 QFC 的分层验证（文档 #20），但适配跨链证明：

| 路径 | 触发条件 | 验证方式 | 延迟 |
|------|---------|-------------|---------|
| **快速路径**（默认） | 标准请求 | 带质押抵押的验证者共识 | 秒级 + 跨链消息传递 |
| **挑战路径** | 争议结果 | opML 欺诈证明或重新执行 | 分钟级 |
| **ZK 路径** | 高价值 / 第一层模型 | 完整 ZK 证明附加到结果 | 秒级（小模型） |
| **TEE 路径** | 隐私敏感 | TEE 证明（见文档 #19） | 近实时 |

### 6.3 跨链消息格式

```solidity
struct AIInferenceResult {
    bytes32 requestId;        // 唯一的跨链请求 ID
    bytes32 modelHash;        // 使用的模型哈希
    bytes32 inputHash;        // 推理输入的哈希
    bytes outputData;         // 结果（或大于 1MB 结果的 IPFS CID）
    uint8 verificationTier;   // 1=ZK, 2=OpZK, 3=SpotCheck
    bytes attestation;        // 验证者签名或 ZK 证明
    uint64 timestamp;         // 推理完成时间
    uint64 qfcBlockNumber;    // 包含结果的 QFC 区块号
}
```

### 6.4 自定义 ISM/DVN 实现

Hyperlane（ISM）实现：

```solidity
contract QFCInferenceISM is IInterchainSecurityModule {
    // QFC 验证者集合（镜像链上验证者注册表）
    mapping(address => uint256) public validatorStakes;
    uint256 public requiredSignatures;  // 例如质押权重的 2/3

    function verify(
        bytes calldata metadata,
        bytes calldata message
    ) external view returns (bool) {
        // 从元数据中解码证明
        (address[] memory signers, bytes[] memory signatures) =
            abi.decode(metadata, (address[], bytes[]));

        // 验证足够的质押加权签名
        uint256 totalStake = 0;
        bytes32 messageHash = keccak256(message);

        for (uint i = 0; i < signers.length; i++) {
            require(
                _verifySignature(messageHash, signers[i], signatures[i]),
                "Invalid signature"
            );
            totalStake += validatorStakes[signers[i]];
        }

        return totalStake >= requiredSignatures;
    }
}
```

LayerZero（DVN）：类似逻辑封装在 LayerZero 的 `ILayerZeroDVN` 接口中。

### 6.5 请求流程（端到端）

```
1. 外部链：用户/合约调用 QFCOracle.requestInference(model, input, callback)
   - 以原生代币或 USDC 支付费用
   - 通过 Hyperlane/LayerZero 发送跨链消息

2. QFC 链：跨链预言机协调器接收请求
   - 解码模型 ID、输入数据
   - 将任务提交到现有 AI 协调器（TaskPool）
   - 分配矿工，执行推理

3. QFC 链：按分层策略验证结果
   - 第一层（小模型）：生成 ZK 证明
   - 第二层（中型）：乐观模式，带挑战窗口
   - 第三层（大型）：抽查 + 验证者共识

4. QFC 链：生成证明
   - ≥2/3 质押加权验证者签名
   - 通过 Hyperlane/LayerZero 发出跨链响应

5. 外部链：QFC ISM/DVN 验证证明
   - 回调交付给请求合约
   - 结果可供链上使用
```

### 6.6 延迟预算

| 步骤 | 预估时间 |
|------|---------------|
| 跨链请求交付 | 1–15 分钟（取决于源链最终性） |
| 任务分配 + 推理 | 1–30 秒 |
| 验证（第一层 ZK） | 1–30 秒 |
| 验证（第二层乐观） | 10–30 分钟（挑战窗口） |
| 验证（第三层抽查） | 1–5 秒 |
| 证明收集 | 5–15 秒 |
| 跨链结果交付 | 1–15 分钟 |
| **总计（快速路径）** | **2–30 分钟** |

### 6.7 Gas 成本估算

| 操作 | 预估 Gas | USD（30 gwei 下） |
|-----------|--------------|-------------------|
| 在目标链发布推理结果 | 50K–200K | $0.10–0.40 |
| 验证多签证明 | 50K–100K | $0.10–0.20 |
| 验证 ZK 证明（如附带） | 200K–500K | $0.40–1.00 |
| 跨链消息开销 | 100K–300K | $0.20–0.60 |
| **每次跨链推理总计** | **200K–800K** | **$0.40–1.60** |

在 L2（Arbitrum、Optimism）上：便宜 10–100 倍。

---

## 7. 竞争定位

| 功能 | ORA（OAO） | Ritual | Chainlink Functions | Bittensor | **QFC 预言机** |
|---------|-----------|--------|-------------------|-----------|---------------|
| 原生推理 | ❌ 链下 | ❌ Docker 容器 | ❌ API 调用 | ❌ 链下子网 | **✅ 链上已验证** |
| 验证 | opML 欺诈证明 | 发展中 | DON 共识 | 主观评分 | **分层（ZK/opML/抽查）** |
| 跨链 | 仅 EVM | Ritual Chain | CCIP（60+ 链） | ❌ | **Hyperlane/LZ（150+）** |
| 模型大小 | 7B+ | 无限制 | API 限制 | 无限制 | **无限制（分层）** |
| 去中心化 | 经济（质押） | 8K+ 节点 | Chainlink DON | 32K+ 矿工 | **PoC 验证者** |
| 自定义模型 | 有限 | ✅ 任何 Docker | ❌ 外部 API | 子网特定 | **✅ 链上注册表** |

**QFC 的独特价值**：唯一的跨链 AI 预言机，其中推理是**原生区块链操作**且具有**分层密码学/经济验证**——而非 API 调用或链下 Docker 执行。

---

## 8. 实施路线图

### 阶段一：跨链消息集成（4-6 周）

| 任务 | 描述 |
|------|-------------|
| 评估 Hyperlane vs LayerZero | 在两者上部署测试合约，基准测试费用/延迟 |
| 在 QFC 上部署 Mailbox/Endpoint | 跨链消息入口 |
| 自定义 ISM/DVN | QFC 验证者证明验证器 |
| 消息格式 | 标准化 `AIInferenceResult` 结构 |

### 阶段二：预言机协调器（4-6 周）

| 任务 | 描述 |
|------|-------------|
| 跨链预言机协调器 | 接收请求，路由到 AI 协调器，发出响应 |
| 费用管理 | 接受跨链支付（原生/USDC → QFC 转换） |
| 请求/响应跟踪 | 待处理跨链请求的链上状态 |
| 超时处理 | 推理未在截止时间内完成时自动退款 |

### 阶段三：目标链合约（3-4 周）

| 任务 | 描述 |
|------|-------------|
| QFCOracle.sol | 用于从任何 EVM 链请求推理的 Solidity 合约 |
| 回调接口 | 接收推理结果的标准接口 |
| 示例集成 | 使用 QFC AI 预言机的 DeFi 协议（例如基于情绪的交易） |
| SDK 支持 | qfc-sdk-js/python 的跨链推理请求 |

### 阶段四：高级功能（4-6 周）

| 任务 | 描述 |
|------|-------------|
| 订阅模式 | 循环推理（例如每小时情绪更新） |
| 结果缓存 | 缓存频繁请求的推理，跨链提供缓存 |
| 多链部署 | 在 Ethereum、Arbitrum、Base、Solana 上部署接收合约 |
| 仪表板 | 浏览器显示跨链请求状态和延迟 |

---

## 9. 关键设计决策

### 9.1 为什么选 Hyperlane 而非 LayerZero？

两者都是强有力的候选者。Hyperlane 略有优势：
- **无需许可**：在 QFC 或任何目标链上部署无需审批
- **多 VM**：原生支持 Move（QVM 兼容），不仅限于 EVM
- **ISM 灵活性**：自定义 ISM 比自定义 DVN 更具可组合性
- **开源**：完全开源的代码库

LayerZero 的优势：更大的链覆盖（160 vs 150），生产环境更久经考验。

**决策**：以 Hyperlane 为首选，利用其无需许可的快速部署能力。添加 LayerZero 作为第二选项以获得更广覆盖。

### 9.2 为什么不构建原生跨链桥？

自建跨链桥：
- 构建和维护成本高（6 个月以上的安全工程）
- 每条目标链需要自定义集成
- 安全责任完全由 QFC 团队承担

使用 Hyperlane/LayerZero：
- 即时接入 150+ 链
- 与成熟协议共担安全
- 仍可通过 ISM/DVN 实现自定义验证

### 9.3 大结果处理

对于大于 1MB 的推理结果（例如图像生成）：
- 将输出发布到 IPFS（QFC 现有机制）
- 跨链消息仅包含 CID + 证明哈希
- 目标链合约可对照证明验证 CID
- 请求方应用使用 CID 从 IPFS 获取完整结果

这使得跨链 Gas 成本与输出大小无关。

---

## 参考资料

- [LayerZero V2 深度解析](https://medium.com/layerzero-official/layerzero-v2-deep-dive-869f93e09850)
- [LayerZero V2 白皮书](https://layerzero.network/publications/LayerZero_Whitepaper_V2.1.1.pdf)
- [LayerZero DVN 文档](https://layerzero.network/blog/layerzero-v2-explaining-dvns)
- [Hyperlane — 无需许可的互操作性](https://medium.com/hyperlane/permissionless-interoperability-3ae02fc162de)
- [Hyperlane 文档](https://docs.hyperlane.xyz/docs/intro)
- [Hyperlane 模块化安全](https://hyperlane.xyz/post/modular-security-with-hyperlane)
- [Wormhole NTT 架构](https://wormhole.com/docs/products/token-transfers/native-token-transfers/concepts/architecture/)
- [理解 Wormhole — Messari](https://messari.io/report/understanding-wormhole)
- [IBC 协议 — 工作原理](https://ibcprotocol.dev/how-ibc-works)
- [IBC v2 公告](https://ibcprotocol.dev/blog/ibc-v2-announcement)
- [Chainlink CCIP 文档](https://docs.chain.link/ccip)
- [Chainlink Functions 文档](https://docs.chain.link/chainlink-functions)
- [ORA 链上 AI 预言机](https://docs.ora.io/doc/onchain-ai-oracle-oao/onchain-ai-oracle)
- [opML 论文（arXiv）](https://arxiv.org/html/2401.17555v1)
- [Ritual Infernet SDK](https://github.com/ritual-net/infernet-sdk)
- [Ritual 架构](https://ritual.academy/ritual/architecture/)
- [Lagrange ZK 协处理器](https://lagrange.dev/zk-coprocessor)
- [Brevis ZK 协处理器](https://medium.com/@0xjacobzhao/brevis-research-report)
- [2025 区块链互操作性](https://lampros.tech/blogs/best-blockchain-interoperability-protocols-2025)
