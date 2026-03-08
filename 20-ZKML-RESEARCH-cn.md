# zkML：用于 AI 推理验证的零知识证明

> 最后更新：2026-03-08 | 版本 1.0
> GitHub Issue: #1
> 作者：Alex Wei，QFC Network 产品经理

---

## 1. 概要

QFC 目前通过 **5% 抽检重新执行** 来验证 AI 推理——随机重新运行 5% 的证明并比较输出哈希。zkML 可以在无需重新执行的情况下提供数学级别的验证保证。

**核心发现：**

- zkML 取得了显著进展：GPT-2 证明时间从 **>1 小时（2024 年）降至 <25 秒（2025 年）**
- 小型模型（<10 亿参数）**目前已可投入生产**使用 zkML（证明仅需数秒）
- 大型模型（70 亿+）进行完整 ZK 证明仍不现实——LLaMA-3 需要 150 秒/token
- **乐观式 ZK 混合方案**正成为行业共识：乐观执行 + 仅在争议时生成 ZK 证明
- QFC 应采用**分层验证策略**：小型模型使用完整 ZK，中型模型使用混合方案，大型模型使用抽检

**建议**：不要完全替代抽检机制，而是在其基础上根据模型大小构建分层 zkML 系统。

---

## 2. 主要 zkML 项目

### 2.1 生产就绪框架

| 项目 | 证明系统 | 方法 | 关键基准 | 成熟度 |
|---------|-------------|----------|---------------|----------|
| **EZKL** | Halo2 (zkSNARK) | ONNX → Halo2 电路 | 比 RISC Zero 快 65.88 倍，支持 GPU | 最成熟的通用 zkML |
| **Remainder** (Modulus Labs) | GKR 协议 | 针对 AI 优化的自定义 GKR | 效率是传统方案的 180 倍；以太坊主网上 10 万+ 证明 | 以太坊上已投产 |
| **zkPyTorch** (Polyhedra) | Expander 后端 | PyTorch → ZK 电路 | **VGG-16 仅需 2.2 秒** | 2025 年 3 月发布 |
| **DeepProve** (Lagrange) | 自定义 | 完整计算图证明 | 首个完整 GPT-2 证明；已扩展至 Gemma-3 | 2025 年 8 月发布 |

### 2.2 专用 LLM 证明器

| 项目 | 目标 | 关键基准 | 状态 |
|---------|--------|---------------|--------|
| **zkGPT** | GPT 系列 LLM | GPT-2 完整证明 **<25 秒**（比先前方案快 279 倍） | USENIX Security 2025 |
| **zkLLM** | 大型 LLM | **130 亿参数模型 <15 分钟**，证明大小 <200KB | ACM CCS 2024，基准测试阶段 |
| **zkPyTorch** | 通用 PyTorch | LLaMA-3 每 token 150 秒 | 2025 年 3 月 |

### 2.3 替代方案

| 项目 | 方法 | 核心优势 | 权衡 |
|---------|----------|-------------|-----------|
| **OPml** (ORA Protocol) | 乐观式欺诈证明（非 ZK） | 正常路径**几乎零开销**；消费级 PC 支持 70 亿+模型 | 经济安全性而非数学安全性；挑战期增加延迟 |
| **RISC Zero** | 通用 zkVM (RISC-V) | 支持任意计算 | ML 场景比 EZKL 慢 65.88 倍；通用 = 昂贵 |
| **Giza/Orion** | Cairo/StarkNet STARKs | StarkNet 原生 | 比 EZKL 慢 2.92 倍；部分模型在 1TB 内存下仍失败 |

---

## 3. 性能基准

### 3.1 证明生成时间

| 模型 | 参数量 | 框架 | 证明时间 | 推理时间 | 开销 |
|-------|-----------|-----------|-------------|----------------|----------|
| VGG-16 | 1.38 亿 | zkPyTorch | **2.2 秒** | ~5ms | ~440 倍 |
| ResNet-18 | 1100 万 | EZKL | ~数秒 | ~2ms | ~500 倍 |
| GPT-2 | 15 亿 | zkGPT | **<25 秒** | ~100ms | ~250 倍 |
| GPT-2 | 15 亿 | ZKML (2024) | ~3,652 秒 | ~100ms | ~36,500 倍 |
| 130 亿 LLM | 130 亿 | zkLLM | **<15 分钟** | ~数秒 | ~100-500 倍 |
| LLaMA-3 8B | 80 亿 | zkPyTorch | **150 秒/token** | ~50ms/tok | ~3,000 倍 |
| 7B LLaMA | 70 亿 | OPml | **~0（正常路径）** | ~50ms/tok | ~0 倍 |

**趋势**：开销从 10,000 倍（2023 年）→ 500 倍（2024 年）→ 100-500 倍（2025 年），正在快速改善。

### 3.2 证明大小

| 系统 | 证明大小 | 备注 |
|--------|-----------|-------|
| Groth16（通用） | **256 字节**固定 | 紧凑性的黄金标准 |
| zkLLM（130 亿模型） | **<200 KB** | 相对模型规模非常紧凑 |
| ResNet-18 (EZKL) | ~15.3 KB | 小型模型 |
| ResNet-50（基于折叠） | <100 KB | 相比折叠前（~1.27 GB）提升 10,000 倍 |
| EZKL (Halo2) | 比 Groth16 大 15.75 倍 | 验证密钥可达 4.2 MB |

### 3.3 链上验证成本

| 验证方法 | Gas 消耗 | 美元成本（30 gwei） |
|--------------------|----------|-------------------|
| Groth16 链上验证 | ~220,000 gas | ~$0.50-2.00 |
| EZKL (Halo2) | 配对运算是 Groth16 的 173 倍 | 显著更高 |
| L2 (Arbitrum) | — | <$0.004 |
| L2 (Optimism, EIP-4844) | — | <$0.001 |
| 2025 年末平均水平 | — | 部分任务约 $0.02 |

### 3.4 证明器硬件要求

| 框架 | 最低配置 | 生产配置 |
|-----------|---------|------------|
| EZKL（小型模型） | 16 GB 内存，8 核 CPU | A10/A100 GPU，32GB+ 显存 |
| zkPyTorch (VGG-16) | <8 GB 内存 | 笔记本电脑可行 |
| RISC Zero | 非常高（内存需求比 EZKL 多 98%） | 服务器级 |
| Orion/Giza | 非常高 | 部分模型在 1TB 内存下仍失败 |

---

## 4. 技术方案对比

### 4.1 zkSNARK vs zkSTARK 用于 ML

| 属性 | zkSNARK | zkSTARK |
|----------|---------|---------|
| 证明大小 | **小**（Groth16 为 256B） | 大（KB 到 MB） |
| 验证成本 | **低**（~220K gas） | 较高 |
| 可信设置 | 需要（Groth16）或不需要（Halo2） | **不需要** |
| 抗量子 | 否 | **是** |
| 证明器速度 | 通常较慢 | 大型电路通常更快 |
| ML 适用性 | **更优**（链上验证成本） | 证明器可扩展性更优 |

**行业共识**：大多数生产级 zkML 使用 SNARKs（EZKL/Halo2、Remainder/GKR、zkGPT），因为链上验证成本至关重要。

### 4.2 乐观式 ML (OPml) vs ZK

| 属性 | zkML | OPml |
|----------|------|------|
| 安全性 | **数学级** | 经济安全（质押 + 欺诈证明） |
| 最大模型规模 | ~130 亿 (zkLLM) | **无限制**（消费级硬件支持 70 亿+） |
| 开销（正常路径） | 100-500 倍 | **~0 倍** |
| 最终性 | 证明验证后**立即确认** | 挑战期（数小时到数天） |
| 每次推理成本 | $0.02 - $100+ | **接近零** |

### 4.3 混合式"乐观 ZK"（2026 年新兴模式）

行业正趋向于：**99% 推理采用乐观执行，仅在争议步骤时生成 ZK 证明**。

- 正常路径享受 OPml 的低成本
- 争议时具备 ZK 的数学级无信任保证
- **乐观 TEE-Rollups (OTR)**：增加 TEE 证明作为中间层。声称比纯 zkML 快 1400 倍，比纯 OPml 延迟降低 99%

---

## 5. "zkML 奇点"（2025 年末）

三项趋同的技术进展"攻克"了 Transformer 架构：

1. **改进的多项式承诺方案** —— 大型电路的证明器更快
2. **tlookup** —— 针对非线性运算（ReLU、Softmax、GELU）的并行化查找参数，消除了比特分解瓶颈
3. **系统级工程** —— DeepProve 等框架支持任意计算图，不再局限于顺序层堆叠

### 关键里程碑时间线

| 日期 | 里程碑 | 影响 |
|------|-----------|--------|
| 2025 年 2 月 | Remainder (Modulus Labs) 正式上线 | 180 倍提升，以太坊上 10 万+ 证明 |
| 2025 年 3 月 | zkPyTorch —— VGG-16 仅需 2.2 秒 | CNN 类模型变为可行 |
| 2025 年 4 月 | R0VM 2.0 —— 44 秒以太坊区块证明 | 通用 zkVM 追赶上来 |
| 2025 年 8 月 | DeepProve —— 首个完整 GPT-2 证明 | 突破 LLM 壁垒 |
| 2025 年 10 月 | Pico Prism —— GPU 集群上的实时区块证明 | 基础设施就绪 |
| 2025 年末 | zkGPT —— GPT-2 <25 秒 | 279 倍加速，LLM 证明已具实用性 |

---

## 6. 对 QFC 的影响

### 6.1 当前验证架构

```
矿工提交证明 → 基本检查（所有证明）
                    ├── 时间戳新鲜度（最大 120 秒）
                    ├── 模型审批检查
                    ├── 输出哈希验证
                    └── FLOPS 声明合理性
                → 抽检（5% 的证明）
                    ├── 通过 InferenceEngine 重新执行
                    ├── 比较输出哈希
                    └── 不匹配时：削减 5% 质押，禁闭 6 小时
```

### 6.2 建议：分层验证策略

| 层级 | 模型规模 | 验证方法 | 理由 |
|------|-----------|-------------------|-----------|
| **第一层** | <10 亿参数（嵌入、分类、小型 LLM） | **每次推理完整 zkML 证明** | 证明时间仅数秒；成本约 $0.02；数学级保证 |
| **第二层** | 10-130 亿参数（中型 LLM） | **乐观执行 + 挑战时 ZK** | 证明需数分钟；使用乐观执行，仅在争议时生成 ZK 证明 |
| **第三层** | 130 亿+参数（大型 LLM） | **当前抽检重新执行** | ZK 证明仍不现实；抽检 + 质押/削减仍是最佳方案 |

### 6.3 第一层：完整 zkML（小型模型）

QFC 当前的小型模型（qfc-embed-small、qfc-embed-medium、qfc-classify-small、qfc-llm-0.5b）均 <10 亿参数，是完整 zkML 的理想候选。

**集成方案**：
- 矿工运行推理并使用 EZKL 或 zkPyTorch 生成 ZK 证明
- 证明随 InferenceProof 一同提交
- 验证者在链上（或链下验证 + 链上结算）验证 ZK 证明
- 无需抽检重新执行——数学级保证

**预估开销**：
- qfc-embed-small (80MB, 2200 万参数)：证明约 1 秒
- qfc-embed-medium (120MB, 1.1 亿参数)：证明约 2-5 秒
- qfc-classify-small (440MB, BERT-base)：证明约 5-15 秒
- qfc-llm-0.5b (990MB, 5 亿参数)：证明约 15-30 秒

### 6.4 第二层：乐观式 ZK（中型模型）

针对 70-130 亿参数模型（未来 QFC 模型注册表）：

```
1. 矿工执行推理（正常速度）
2. 矿工以结果质押抵押品
3. 挑战窗口开启（例如 30 分钟）
4. 如被挑战：
   a. 挑战者质押抵押品
   b. 矿工生成 ZK 证明（需数分钟）
   c. 链上验证证明
   d. 失败方的质押归胜方所有
5. 如未被挑战：窗口结束后结果最终确认
```

这借鉴了乐观 Rollup 的设计，但应用于 AI 推理。

### 6.5 第三层：增强型抽检（大型模型）

对于 700 亿+参数模型，维持当前方案并增强：
- 提高新矿工/低信誉矿工的抽检率（已实现：新矿工 10%，低信誉 8%，标准 5%）
- 添加 TEE 证明作为可选中间层（见文档 #19）
- 高价值任务跨 2-3 个矿工冗余执行

### 6.6 实施考量

**QFC 框架选择**：
- **EZKL** 是最稳妥的选择：最成熟，支持 ONNX（QFC 已有 OnnxInference），GPU 加速
- **zkPyTorch** 适用于超越 ONNX 的 PyTorch 原生模型
- **Remainder (GKR)** 适用于 QFC 希望针对类以太坊链上验证进行优化的场景

**新增 ComputeTaskType 变体**：
```rust
// Addition to existing enum
ComputeTaskType::VerifiedInference {
    model_id: ModelId,
    input_hash: Hash,
    zk_proof: Vec<u8>,          // The ZK proof bytes
    proof_system: ProofSystem,  // EZKL, Groth16, etc.
}
```

**Gas/费用影响**：
- 矿工承担 ZK 证明成本 → 第一层验证推理需要更高费用
- 用户为数学级保证（相比抽检的统计保证）支付溢价
- 预估溢价：第一层为基础费用的 2-5 倍，第二层为 1.2-1.5 倍

---

## 7. 竞争定位

| 项目 | 验证方法 | 最大模型规模 | 最终性 |
|---------|-------------------|----------------|----------|
| Bittensor | 主观验证者评分 | 无限制 | 即时（但可被博弈） |
| ORA Protocol | OPml 欺诈证明 | 70 亿+ | 挑战期 |
| Ritual | TEE 证明 | 无限制 | 即时 |
| Modulus/Remainder | 完整 zkML (GKR) | ~10 亿（实际可行） | 即时 |
| Giza | zkSTARK (Cairo) | 小型模型 | 即时 |
| **QFC（目标）** | **分层：zkML + OPml + 抽检** | **无限制** | **即时（第一层）/ 挑战期（第二层）/ 统计（第三层）** |

QFC 的分层方案比任何单一方法的竞争对手都更加务实。它在可行范围内提供最强保证（小型模型），为中型模型提供合理保证，为大型模型提供实用保证。

---

## 8. 实施路线图

### 阶段一：嵌入模型的 zkML（3-4 周）

| 任务 | 描述 |
|------|-------------|
| 集成 EZKL | 在 qfc-inference 中添加 EZKL 作为可选依赖 |
| 证明生成 | 矿工为嵌入任务生成 ZK 证明 |
| 证明验证 | 验证者验证 ZK 证明替代抽检 |
| 费用调整 | 第一层验证推理定价 |

### 阶段二：中型模型的乐观式 ZK（6-8 周）

| 任务 | 描述 |
|------|-------------|
| 挑战协议 | 链上挑战/响应机制 |
| 质押管理 | 乐观执行的抵押品 |
| ZK 争议解决 | 挑战时生成并验证 ZK 证明 |
| 超时处理 | 矿工未能生成证明时自动削减 |

### 阶段三：统一验证框架（4-6 周）

| 任务 | 描述 |
|------|-------------|
| 自动层级选择 | 根据模型大小确定验证层级 |
| 证明系统抽象 | 支持多种证明系统（EZKL、Groth16、GKR） |
| SDK 支持 | qfc-sdk-js/python 支持验证推理请求 |
| 仪表板 | 浏览器显示每个任务的验证方法 |

---

## 参考文献

- [The Definitive Guide to ZKML (2025) - ICME](https://blog.icme.io/the-definitive-guide-to-zkml-2025/)
- [The zkML Singularity - Extropy Academy](https://academy.extropy.io/pages/articles/zkml-singularity.html)
- [Benchmarking ZKML Frameworks - EZKL Blog](https://blog.ezkl.xyz/post/benchmarks/)
- [State of EZKL: 2025](https://blog.ezkl.xyz/post/state_of_ezkl/)
- [DeepProve-1 - Lagrange](https://lagrange.dev/blog/deepprove-1)
- [opML - ORA Documentation](https://docs.ora.io/doc/onchain-ai-oracle-oao/fraud-proof-virtual-machine-fpvm-and-frameworks/opml)
- [zkLLM Paper - arXiv](https://arxiv.org/abs/2404.16109)
- [zkPyTorch - Polyhedra Network](https://polyhedra.network/zkPyTorch)
- [zkGPT Paper - USENIX Security 2025](https://www.usenix.org/system/files/usenixsecurity25-qu-zkgpt.pdf)
- [Groth16 Verification Gas Cost](https://hackmd.io/@nebra-one/ByoMB8Zf6)
- [Optimistic TEE-Rollups - arXiv](https://arxiv.org/html/2512.20176)
- [Introduction to ZKML - Worldcoin](https://world.org/blog/engineering/intro-to-zkml)
