# DAG 共识优化：面向 QFC 贡献证明机制

> 最后更新：2026-03-08 | 版本 1.0
> GitHub Issue: #3
> 作者：Alex Wei，QFC Network 产品经理

---

## 1. 概要

QFC 使用多维评分的贡献证明（PoC）共识机制。本报告评估基于 DAG 的共识协议，这些协议可在保留 PoC 评分模型的同时提升 QFC 的吞吐量和延迟。

**核心发现：**

- **Mysticeti**（Sui）实现 390ms 共识提交和 20 万-40 万 TPS——已在主网上经过生产验证
- **Shoal++**（Aptos/NSDI 2025）实现 4.5 平均消息延迟——比先前方案延迟降低 60%
- **Block-STM** 实现 16 万+ TPS 并行执行——非常适合 AI 推理任务（低争用）
- IOTA 在多年研究后放弃了其 Tangle DAG 并转而采用 Mysticeti——**强烈信号表明非结构化 DAG 不可行**
- QFC 的 PoC 评分天然适配基于 DAG 的领导者选举权重

**建议**：采用 **Mysticeti 变体 DAG 共识**，配合 PoC 加权领导者选举、Narwhal 风格的数据可用性分离和 Block-STM 并行执行。

---

## 2. DAG 共识协议调研

### 2.1 Mysticeti（Sui）——生产环境领先者

当前生产级 DAG-BFT 的最高水平。

**架构**：无认证 DAG——消除了显式区块认证。每个验证者在每轮都提议区块（多提议者）。区块通过 DAG 边引用前一轮的区块。

**核心创新**：新颖的提交规则，允许区块无需额外认证延迟即可提交。

| 指标 | 数值 |
|--------|-------|
| 共识提交 | **390ms**（P50），640ms 最终性 |
| Mysticeti v2 (2025) | ~260ms 改进，P95 为 90ms，P99 为 114ms |
| 吞吐量 | 20 万-40 万 TPS |
| 消息轮数 | **3**（DAG-BFT 的理论下界） |
| 验证者 | Sui 主网上 106+ |
| 生产运行始于 | 2024 年 8 月 |

**双路径执行**：
- **所有权对象**：完全绕过共识——近乎即时确认
- **共享对象**：通过 Mysticeti 处理但延迟已优化

**Mysticeti-FPC**（快速提交变体）：175,000 TPS，0.5 秒延迟。

### 2.2 Narwhal / Tusk / Bullshark——发展脉络

**Narwhal**（EuroSys 2022 最佳论文）——数据可用性层：
- **核心创新**：将可靠的数据分发与交易排序分离
- 验证者构建交易证书的 DAG
- 可与任何共识机制配对进行排序
- 在保持高吞吐量的同时容忍异步网络

**Tusk**——原始排序层：
- 在 Narwhal DAG 之上实现零消息开销排序
- 完全异步，无需领导者

**Bullshark**（CCS 2022）——替代了 Tusk：
- 部分同步，延迟更低
- 125,000 TPS，2 秒延迟（50 个参与方）
- 支持公平性属性

| 配置 | 吞吐量 | 延迟 |
|--------------|-----------|---------|
| Narwhal + HotStuff | 130,000 TPS | <2s |
| Narwhal + HotStuff（扩展） | 600,000 TPS | <2s |
| Bullshark | 125,000 TPS | ~2s |
| 故障场景下 | 70,000 TPS | 8-10s |

**对 QFC 的关键启示**：将数据可用性与排序分离对 AI 推理至关重要——大型推理结果应可靠分发而不阻塞共识排序。

### 2.3 Block-STM（Aptos）——并行执行引擎

不是共识协议，而是基于软件事务内存的**执行引擎**。

**工作原理**：
1. 交易以推测方式并行执行
2. 执行期间记录内存访问
3. 执行后验证检测读/写冲突
4. 冲突的交易被中止并重新执行
5. 预设的区块顺序确定性地解决冲突

| 工作负载 | 吞吐量 | 相比顺序执行的提升 |
|----------|-----------|--------------------------|
| 低争用 | 160,000+ TPS | **17 倍** |
| 高争用 | 80,000+ TPS | **8 倍** |
| 最差情况 | ~30% 损失 | 中止带来的开销 |

**与 QFC 的相关性**：AI 推理任务天然是低争用的（不同模型、输入、矿工）。预期提升：接近顺序执行的 17 倍。

### 2.4 Shoal++（NSDI 2025）——当前前沿

来自 Aptos Labs、Cornell 和 UIUC 的最新进展。

| 指标 | 数值 |
|--------|-------|
| 平均提交延迟 | **4.5 消息延迟**（先前 DAG-BFT 为 10.5） |
| 延迟改进 | 比最先进方案**降低 60%** |
| 吞吐量 | 100,000+ TPS，亚秒级延迟 |
| 与 Mysticeti 比较 | 在基准测试中表现更优（包括无故障场景） |

### 2.5 其他协议

**DAG-Rider**：基础性的基于轮次的结构化 DAG 协议。双层架构（通信 + 排序）。完全异步但延迟较高。

**Shoal**：基于 Bullshark 构建，通过交错两个 Bullshark 实例降低非领导者区块延迟。

**Sailfish**（2024）：首个每轮带领导者顶点的 DAG-BFT。领导者顶点提交延迟为 3-delta，非领导者为 5-delta。

### 2.6 Avalanche 共识——不同范式

**方法**：通过子采样投票实现的亚稳态概率共识（Snow 协议族：Slush → Snowflake → Snowball → Avalanche）。

| 指标 | 数值 |
|--------|-------|
| 吞吐量 | ~3,400 TPS |
| 确认时间 | ~1.35 秒 |
| 安全模型 | 概率性（非确定性 BFT） |
| 消息复杂度 | 每个节点 O(k)，与网络规模无关 |

**权衡**：吞吐量远低于 DAG-BFT（3,400 vs 100,000+ TPS），但可扩展至数千个验证者并优雅降级。

**与 QFC 的相关性**：子采样投票可用于链下对主观 AI 推理质量评分达成一致。

### 2.7 IOTA Tangle——前车之鉴

**最初设计**：无区块的 DAG；每笔交易引用 2 个之前的"tip"。使用加权随机游走进行 tip 选择。

**结果**：经过多年"Coordicide"去中心化研究后，IOTA **放弃了 Tangle** 并转而采用：
- Mysticeti 共识协议（与 Sui 相同）
- MoveVM 智能合约
- 50,000+ TPS，~400ms 最终性

**教训**：非结构化 DAG 极难安全地去中心化。**结构化 DAG-BFT 才是可行路径。**

---

## 3. 性能对比

| 协议 | TPS | 共识延迟 | 最终性 | 消息延迟 | 状态 |
|----------|-----|-------------------|----------|------------|--------|
| **Mysticeti v2** | 20 万-40 万 | ~260ms | <500ms | 3 轮 | Sui 主网 |
| **Shoal++** | 10 万+ | 亚秒级 | 亚秒级 | 4.5 平均 | Aptos 测试中 |
| **Bullshark** | 12.5 万 | ~2s | ~2s | ~10.5 平均 | 已替代 |
| **Narwhal+HotStuff** | 13 万-60 万 | <2s | <2s | 5+ 轮 | 已替代 |
| **Sailfish** | ~10 万（估计） | 3-5 delta | 3-5 delta | 3-5 | 研究阶段 |
| **Block-STM**（仅执行） | 16 万+ | N/A | N/A | N/A | Aptos 主网 |
| **Avalanche** | ~3,400 | ~1.35s | ~1.35s | 概率性 | C-Chain |
| **IOTA Rebased** | 5 万+ | ~400ms | ~400ms | 3（Mysticeti） | 2025 年主网 |

---

## 4. DAG 与 QFC PoC 评分的整合

### 4.1 PoC 维度 → DAG 机制

QFC 的评分维度天然适配基于 DAG 的共识：

| PoC 维度 | 权重 | DAG 整合方式 |
|--------------|--------|-----------------|
| **质押** (30%) | DAG 轮次中验证者投票的标准 PoS 加权 |
| **计算** (20%) | 在 DAG 顶点中嵌入推理证明哈希；异步验证 |
| **在线时间** (15%) | **DAG-BFT 中免费获得**：衡量每轮提议的区块数。缺失轮次 = 更低评分 |
| **验证准确率** (15%) | 在 DAG 元数据中追踪验证结果；滚动窗口 |
| **网络** (10%) | 通过数据可用性衡量（Narwhal 风格的证书传播速度） |
| **存储** (5%) | 证明 IPFS pin 可用性；在 DAG 区块中引用 CID |
| **信誉** (5%) | 从历史链上评分中汇总 |

**关键洞察**：在 DAG-BFT 中在线时间评分是免费的——每个验证者每轮都提议，因此参与度可以直接衡量而无需额外探测。

### 4.2 PoC 加权领导者选举

用复合 PoC 评分替代纯质押加权的领导者选举：

```
leader_weight(validator) =
    stake_score * 0.30 +
    compute_score * 0.20 +
    uptime_score * 0.15 +
    validation_score * 0.15 +
    network_score * 0.10 +
    storage_score * 0.05 +
    reputation_score * 0.05
```

在 Mysticeti 风格的 DAG 中：
- 所有验证者每轮都提议区块（多提议者）
- 提交规则的领导者选择按 PoC 评分加权
- 更高的 PoC 评分 → 成为提交领导者的概率更高 → 对排序影响更大
- 这保留了去中心化（人人都提议）同时奖励贡献

### 4.3 DAG 顶点中的 AI 推理证明

每个 DAG 顶点（区块）包含：

```
DAGVertex {
    // Standard consensus fields
    round: u64,
    author: ValidatorId,
    parents: Vec<VertexDigest>,     // References to previous round

    // Transaction payload
    transactions: Vec<Transaction>,

    // AI inference commitments
    inference_proofs: Vec<InferenceProofCommitment> {
        task_id: Hash,
        model_hash: Hash,
        input_hash: Hash,
        output_hash: Hash,
        compute_time_ms: u64,
        ipfs_cid: Option<String>,   // For results >1MB
        zk_proof: Option<Vec<u8>>,  // Optional ZK proof (see doc #20)
    },

    // PoC score updates
    poc_updates: PoCScoreDeltas {
        compute_contribution: u64,
        validation_results: Vec<ValidationResult>,
        storage_proofs: Vec<StorageProof>,
    },
}
```

### 4.4 AI 任务双路径

借鉴 Sui 的所有权/共享对象模式：

| 任务类型 | 共识路径 | 延迟 |
|-----------|---------------|---------|
| **私有推理**（单用户） | 快速路径——跳过共识 | 亚秒级 |
| **公共推理** (TaskPool) | 完整共识——共享状态 | ~500ms |
| **推理验证** | 异步——附载于 DAG | 后台执行 |
| **PoC 评分更新** | 嵌入 DAG 顶点中 | 每轮 |

---

## 5. 提议架构：QFC-DAG

### 5.1 三层设计

```
┌─────────────────────────────────────────────────┐
│ 第三层：并行执行（受 Block-STM 启发）              │
│   乐观并行交易执行                                │
│   AI 推理任务 = 低争用 = 快速                      │
├─────────────────────────────────────────────────┤
│ 第二层：排序（受 Mysticeti/Shoal++ 启发）          │
│   DAG-BFT 三轮提交                               │
│   PoC 加权领导者选举                              │
│   双路径：快速（私有） vs 共识（共享）               │
├─────────────────────────────────────────────────┤
│ 第一层：数据可用性（受 Narwhal 启发）               │
│   可靠的交易批次分发                               │
│   AI 推理结果通过 IPFS CID 引用                    │
│   与排序分离以提高吞吐量                            │
└─────────────────────────────────────────────────┘
```

### 5.2 区块生产流程

```
第 N 轮：
  1. 每个验证者收集待处理交易和推理证明
  2. 验证者创建 DAG 顶点，引用第 N-1 轮 ≥2f+1 个顶点
  3. 顶点包含：交易批次 + 推理证明承诺 + PoC 增量
  4. 顶点广播至所有验证者（Narwhal 风格可靠广播）

第 N+1 轮：
  5. 验证者引用第 N 轮顶点
  6. 如果第 N 轮存在可提交的领导者（PoC 加权选择）：
     → 提交领导者的因果历史（所有可达顶点）
     → 并行执行已提交交易（Block-STM）

第 N+2 轮：
  7. 第三轮确认提交（3 轮 Mysticeti 规则）
  8. 最终化的交易应用到状态
  9. 基于本轮贡献更新 PoC 评分
```

### 5.3 预期性能

| 指标 | 当前 QFC (PoC) | QFC-DAG（提议） | 提升 |
|--------|-------------------|-------------------|-------------|
| 共识延迟 | ~数秒（估计） | **<500ms** | 2-5 倍 |
| 吞吐量 | 受串行执行限制 | **10 万-20 万 TPS** | 10-50 倍 |
| 最终性 | 多轮 | **<1 秒** | 3-5 倍 |
| AI 任务并行执行 | 顺序执行 | **Block-STM 并行** | ~17 倍 |

---

## 6. Avalanche 采样用于主观评分

对于非确定性 AI 质量评分（文本生成质量、图像美学），使用 Avalanche 风格的子采样投票：

```
1. 多个验证者评估推理输出质量
2. 每个验证者独立评分（0-100）
3. Snowball 协议：重复采样 k=20 个验证者
4. 如果 α=14/20 同意评分范围 → 收敛
5. 最终评分用于矿工信誉
```

这避免了对主观质量指标进行全对全通信的开销，同时高效达成概率性共识。

---

## 7. 实施路线图

### 阶段一：Narwhal 风格数据可用性（4-6 周）

| 任务 | 描述 |
|------|-------------|
| DAG 顶点结构 | 定义包含推理证明承诺的顶点格式 |
| 可靠广播 | 实现 Narwhal 风格基于证书的分发 |
| IPFS 集成 | 大型推理结果通过 CID 在顶点中引用 |
| DA 与排序分离 | 数据可用性层独立于共识排序运行 |

### 阶段二：Mysticeti 变体共识（6-8 周）

| 任务 | 描述 |
|------|-------------|
| DAG 构建 | 基于轮次的结构化 DAG，带父引用 |
| 提交规则 | 3 轮无认证 DAG 提交（Mysticeti） |
| PoC 加权领导者 | 领导者选举按复合 PoC 评分加权 |
| 双路径执行 | 私有任务走快速路径，共享任务走共识 |

### 阶段三：Block-STM 并行执行（4-6 周）

| 任务 | 描述 |
|------|-------------|
| STM 执行引擎 | 带冲突检测的乐观并行执行 |
| AI 任务优化 | 推理验证任务并行化 |
| 基准测试 | 衡量推理工作负载下的实际 TPS 提升 |

### 阶段四：优化完善（4-6 周）

| 任务 | 描述 |
|------|-------------|
| Snowball 采样 | 非确定性任务的主观质量评分 |
| 性能调优 | 针对 QFC 特定工作负载组合进行优化 |
| 迁移计划 | 从当前 PoC 升级到 QFC-DAG 的路径 |

---

## 参考文献

- [Mysticeti Paper (NDSS 2025)](https://www.ndss-symposium.org/wp-content/uploads/2025-929-paper.pdf)
- [Mysticeti on Sui Blog](https://blog.sui.io/mysticeti-consensus-reduce-latency/)
- [Narwhal and Tusk (arXiv)](https://arxiv.org/abs/2105.11827)
- [Bullshark Paper (arXiv)](https://arxiv.org/pdf/2201.05677)
- [Block-STM on Aptos](https://medium.com/aptoslabs/block-stm-how-we-execute-over-160k-transactions-per-second-on-the-aptos-blockchain-3b003657e4ba)
- [Block-STM Paper (arXiv)](https://arxiv.org/abs/2203.06871)
- [Shoal++ (NSDI 2025)](https://www.usenix.org/conference/nsdi25/presentation/arun)
- [Shoal++ Paper (arXiv)](https://arxiv.org/abs/2405.20488)
- [Sailfish Paper (ePrint)](https://eprint.iacr.org/2024/472)
- [Avalanche Whitepaper](https://ipfs.io/ipfs/QmUy4jh5mGNZvLkjies1RWM4YuvJh5o2FYopNPVYwrRVGV)
- [IOTA Tangle to Rebased Analysis](https://www.mdpi.com/1424-8220/25/11/3408)
- [IOTA Rebased Mainnet](https://blog.iota.org/iota-rebased-fast-forward/)
- [DAG Meets BFT (Decentralized Thoughts)](https://decentralizedthoughts.github.io/2022-06-28-DAG-meets-BFT/)
- [SoK: DAG-based Consensus (arXiv 2025)](https://arxiv.org/abs/2411.10026)
