# 隐私保护 AI 推理：技术研究与 QFC 策略

> 最后更新：2026-03-08 | 版本 1.0
> GitHub Issue: #2
> 作者：Alex Wei，QFC Network 产品经理

---

## 1. 执行摘要

QFC 矿工为用户执行 AI 推理任务。当用户提交敏感数据（医疗记录、商业秘密、个人信息）时，输入数据必须对矿工、验证者和其他网络参与者保密。

本报告评估了四种隐私保护方案：TEE、FHE、MPC 以及混合组合方案。

**核心发现：**

- **GPU TEE 是唯一可投入生产的路径**，适用于大模型推理（7B+ 参数），开销低于 5%
- FHE 仍比明文慢 100-1000 倍——对于交互式 LLM 工作负载目前不切实际
- MPC 慢 10-100 倍，93% 的开销来自非线性层（ReLU）
- **混合 TEE+ZK 是最佳近期策略**：TEE 保证速度，ZK 保证无信任验证
- NVIDIA Blackwell B200 实现了**接近零开销**的机密 AI——这是一个里程碑

**QFC 建议方案：**
1. **阶段 1**：NVIDIA GPU TEE（H100/B200）用于机密推理
2. **阶段 2**：混合 MPC+TEE 用于最高敏感度的输入
3. **阶段 3**：关注 FHE 加速进展，为未来无信任推理做准备

---

## 2. 技术概览

### 2.1 TEE（可信执行环境）

硬件隔离的安全飞地，在执行期间保护代码和数据。

#### 硬件生态

| 硬件 | 厂商 | 层级 | 状态 | 备注 |
|----------|--------|-------|--------|-------|
| **Intel SGX** | Intel | 进程级 | **已弃用**（消费级自 2021 年起） | WireTap 攻击（2025 ACM CCS）以不到 1000 美元的设备提取了认证密钥 |
| **Intel TDX** | Intel | 虚拟机级 | 生产可用（Xeon Sapphire Rapids） | SGX 的继任者；Google Cloud 在 C3 系列上已 GA |
| **AMD SEV-SNP** | AMD | 虚拟机级 | 生产可用（EPYC Genoa/Milan） | 部署最广泛；与 NVIDIA GPU TEE 配合使用 |
| **ARM CCA** | ARM | 虚拟机级 | 早期阶段 | "Realm"概念，配合粒度保护表 |
| **NVIDIA H100** | NVIDIA | GPU 级 | **生产可用** | 首款 GPU TEE；芯片上集成信任根 |
| **NVIDIA B200** | NVIDIA | GPU 级 | **已出货**（2026 年 2 月） | 通过 NVLink 实现 TEE-I/O；接近零开销 |

#### NVIDIA GPU TEE 性能

| 模型 | H100 开销 | B200 开销 | 备注 |
|-------|--------------|---------------|-------|
| LLaMA-3.1-8B | ~5-7% | ~0% | H100 上中等输入约 130 TPS |
| LLaMA-3.1-70B | ~0%（可忽略） | ~0% | 计算量大时开销可以被摊薄 |
| 通用 LLM 推理 | 平均 <5% | 接近零 | PCIe 反弹缓冲区是 H100 的主要瓶颈 |

**B200 突破**：TEE-I/O 能力配合内联 NVLink 加密，消除了导致 H100 开销的 PCIe 瓶颈。即使启用机密计算，仍保持相对 H200 的 2 倍训练和 2.5 倍推理优势。

#### 使用 TEE 的区块链项目

**Phala Network**（最成熟的 TEE-区块链集成）：
- 单日处理 **13.4 亿 LLM token**
- 生产环境开销：0.5-5%
- 在 OpenRouter 上提供机密 LLM 推理服务
- 正从 SGX 迁移至 Intel TDX + NVIDIA GPU TEE（WireTap 事件后）
- 支持 H100 和 B200

**Oasis Protocol**：
- Sapphire：首个生产环境机密 EVM
- ROFL（Runtime Offchain Logic）框架用于具有链上信任的链下应用

**Secret Network**：
- 正转向机密 AI，提供 Secret AI SDK
- SecretVM 用于机密工作负载
- 2026 年：多云支持（Azure、GCP、AWS）

**iExec**：
- 医疗健康 PoC：使用 Intel TDX 在加密 EEG 数据上进行癫痫手术评估
- 被列入 Intel 的 AI 推理解决方案目录

#### 信任假设

- **必须信任硬件厂商**（Intel、AMD、NVIDIA）的正确实现
- 侧信道攻击仍是隐患（SGX 的 WireTap、TDX 的 Spectre 类攻击）
- 远程认证提供飞地身份和完整性的密码学证明
- "信任但验证"模型——认证有帮助但不能消除对硬件的信任

---

### 2.2 FHE（全同态加密）

在不解密的情况下对加密数据进行计算。具有数学证明的隐私保障。

#### 关键项目

**Zama (Concrete ML, fhEVM)**：
- 开源 TFHE 编译器（Python → FHE，通过 LLVM）
- 兼容 scikit-learn 和 PyTorch 的机器学习框架
- 已支持：MLP、CNN、Transformer（已演示情感分析）
- fhEVM：支持 FHE 的 EVM，用于机密智能合约

**Inco Network**：
- 模块化机密计算 L1 区块链
- 结合 FHE（TFHE）、ZK、TEE、MPC
- 基于格的密码学（NIST 后量子标准认可）
- 路线图：FPGA 加速目标 100-1000 TPS

**Sunscreen**：
- 基于 Rust 的 FHE 编译器生态
- 开发者友好的抽象

#### 性能现实

| 基准测试 | 性能 |
|-----------|------------|
| 相对明文的总体开销 | **慢 100-1000 倍以上** |
| CIFAR-10 CNN 推理 | 每张图片约 4 分钟（88.7% 准确率） |
| 自举延迟 | <1ms（从 2021 年的 50ms 降下来——重大突破） |
| GPU 加速 FHE | 比 CPU 基线快 150-200 倍 |
| LLM 推理 | **不切实际**——每个 token 需要数秒到数分钟 |

#### 按模型类型的可行性

| 可行性 | 模型类型 |
|-------------|-------------|
| **目前可行** | 逻辑回归、决策树、小型 MLP、小型 CNN、情感分类 |
| **正在发展** | 中型 CNN（ResNet 级别配合混合方案）、小型 Transformer |
| **不可行** | 完整 LLM 推理（GPT/LLaMA 级别）、大型视觉模型 |

---

### 2.3 MPC（多方安全计算）

将计算拆分到多个参与方，使任何单一方都无法看到完整数据。

#### 关键项目

**Partisia Blockchain**：
- 由 MPC 先驱创立
- 生物识别数据存储和匹配，无需解密
- 基于 MPC 的通用机密智能合约

**Nillion**：
- "盲计算"网络
- 模块：nilDB（安全数据库）、nilAI（安全 LLM）、nilVM（去中心化签名）
- **Fission 项目（与 Meta 合作）**：融合 MPC + TEE，实现接近生产可用的吞吐量

**Secret Network**：
- 最初以 MPC 为重点，现转向基于 TEE 的机密计算

#### 性能基准

| 任务 | MPC 时间 | TEE 时间 | 慢倍数 |
|------|----------|----------|----------|
| MNIST 推理 | 0.321s（优化 FSS） | 约即时 | 约 300 倍 |
| CIFAR-10 推理 | 3.695s（优化） | 约即时 | 约 3700 倍 |
| ResNet-18 | 148s | 8.15s | **18 倍** |

- **93% 的 MPC 开销来自 ReLU**（非线性）层
- 通信开销随网络深度线性增长
- 半诚实模型占主导（假设参与方遵循协议）

#### 信任模型

- **最强信任模型**：没有任何单一方能看到数据
- 不需要硬件信任（纯密码学）
- 权衡：性能显著下降

---

### 2.4 混合方案

| 组合 | 描述 | 状态 | 关键项目 |
|-------------|-------------|--------|-------------|
| **TEE + ZK** | TEE 以原生速度执行；ZK 证明正确性 | 早期生产 | Phala Network |
| **MPC + TEE** | MPC 保护输入隐私；TEE 提供快速计算 | 原型 | Nillion Fission（与 Meta 合作） |
| **FHE + MPC** | 加密协作计算 | 原型 | Arcium（主网 alpha） |
| **ZK + FHE + TEE** | 全栈隐私 | 研究 | Mind Network |

**TEE + ZK** 是最接近生产可用的混合方案：
- TEE 提供接近原生的推理速度
- ZK 证明 TEE 执行正确（减少对硬件的信任假设）
- "TEE 的性能 + ZK 的无信任验证"

**MPC + TEE（Nillion Fission）**：
- 用户输入通过 MPC 进行秘密分享（没有任何单一方看到原始数据）
- 中间结果（经过混淆，不可逆）转移到 TEE
- 对某些模型实现接近生产可用的吞吐量
- 已通过与 Meta 的合作进行验证

---

## 3. 对比矩阵

| 维度 | TEE（GPU） | FHE | MPC | 混合（TEE+ZK） |
|-----------|-----------|-----|-----|------------------|
| **性能开销** | **<5%**（H100），**~0%**（B200） | 100-1000 倍 | 10-100 倍 | ~5% |
| **信任假设** | 硬件厂商 | **无**（数学） | **无**（分布式） | 降低（ZK 验证 TEE） |
| **硬件要求** | 特定 GPU（H100/B200） | 标准 + FPGA | 标准，高带宽 | TEE GPU + ZK 证明器 |
| **最大模型规模** | **无限**（70B+） | 小型（MLP、小型 CNN） | 中型（ResNet） | **无限** |
| **延迟** | **接近原生** | 分钟级 | 秒到分钟 | **接近原生** |
| **成熟度** | **生产可用** | 研究/早期 | 研究/有限 | 早期生产 |
| **侧信道风险** | 有（已缓解） | **无** | **无** | 降低 |
| **输入隐私** | 对软件保密，对硬件厂商不保密 | **完全** | **完全** | 强 |
| **后量子就绪** | 需要后量子密钥交换 | **是**（基于格） | 需要后量子密钥交换 | 部分 |

---

## 4. QFC 的影响

### 4.1 当前状态

QFC 矿工使用消费级 GPU（RTX 3060-4080）和 CPU 后端。矿工网络是无许可的——任何拥有 GPU 的人都可以挖矿。目前推理输入没有隐私保护。

### 4.2 QFC 面临的特定挑战

1. **消费级 GPU 矿工没有 TEE**：NVIDIA GPU TEE 需要 H100/B200（数据中心 GPU）
2. **验证冲突**：QFC 的抽查重新执行需要看到输入——与加密推理不兼容
3. **硬件异构**：矿工拥有多样化的硬件；隐私方案必须跨层级工作
4. **成本敏感**：隐私开销不能让用户望而却步

### 4.3 建议策略

#### 阶段 1：机密推理层级（近期）

在现有 Cold/Warm/Hot 层级基础上引入**机密矿工**层级：

```
GPU 层级体系：
  Cold   → 消费级 GPU（RTX 3060，8GB）— 无隐私
  Warm   → 消费级 GPU（RTX 4070，12GB）— 无隐私
  Hot    → 数据中心 GPU（A100，80GB）— 无隐私
  Secure → 带 TEE 的数据中心 GPU（H100/B200）— 机密
```

- 需要隐私的用户支付溢价，将任务路由到 `Secure` 层级矿工
- Secure 矿工在注册时必须提供 TEE 认证
- 标准（非隐私）任务继续在消费级 GPU 上以更低成本运行
- **这是一种市场细分策略**：隐私作为高级功能

#### 阶段 2：机密任务的混合验证

抽查重新执行模型在输入加密时不适用。替代验证方案：

| 方法 | 描述 | 权衡 |
|--------|-------------|-----------|
| **仅 TEE 认证** | 信任 TEE 执行正确 | 依赖硬件信任 |
| **TEE + ZK 证明** | TEE 生成正确执行的 ZK 证明 | 成本更高，保障最强 |
| **冗余 TEE 执行** | 在 2-3 个独立 TEE 矿工上运行，比较输出 | 成本更高，无单点信任 |
| **挑战协议** | 向机密管线注入已知测试任务 | 能发现懒惰/不诚实的矿工 |

**建议**：从 **TEE 认证 + 挑战协议**（最简单）开始，随技术成熟演进到 **TEE + ZK**。

#### 阶段 3：消费级 GPU 隐私（长期）

在消费级 GPU（无 TEE）上实现隐私：

- **输入分割**：使用秘密分享将敏感输入分割到 2-3 个矿工（轻量 MPC）
- **部分 FHE**：仅加密输入中的敏感部分（例如加密医疗数据，模型提示词保持明文）
- 关注 FHE 硬件加速进展（FPGA/ASIC）

### 4.4 架构草图

```
用户提交机密任务：
    ↓
任务路由器（检查隐私标志）
    ├── privacy=false → 标准矿工池（现有流程）
    └── privacy=true  → 机密矿工池
                           ↓
                        TEE 认证检查
                           ↓
                        加密输入传输（TLS 到飞地）
                           ↓
                        TEE 内推理（H100/B200）
                           ↓
                        输出加密后返回用户
                           ↓
                        验证：
                           ├── TEE 认证日志（始终）
                           ├── 挑战注入（5-10%）
                           └── ZK 证明（未来）
```

### 4.5 智能合约集成

使用 QVM 的 Resource 类型实现机密推理：

```
// 机密推理结果——仅能被任务提交者消费
resource ConfidentialResult {
    task_id: Hash,
    encrypted_output: Bytes,    // 用提交者公钥加密
    tee_attestation: Bytes,     // 硬件认证证明
    miner: Address,
}
```

- `ConfidentialResult` Resource 确保加密输出恰好被消费一次
- TEE 认证存储在链上，供审计使用
- 跨虚拟机：Solidity 合约可以验证认证，QSC 合约持有 Resource

---

## 5. 竞争定位

| 项目 | 隐私方案 | AI 模型支持 | 链上可组合性 |
|---------|-----------------|------------------|----------------------|
| **Phala** | TEE（H100/B200） | LLM（任意规模） | 有限（链下计算） |
| **Secret Network** | TEE + SecretVM | 正在发展 | 仅限 Secret 合约 |
| **Nillion** | MPC + TEE 混合 | 中型模型 | 无智能合约 |
| **Oasis** | TEE（Sapphire） | 非 AI 重点 | 机密 EVM |
| **QFC（目标）** | **TEE + ZK + Resource 类型** | **任意模型（分层）** | **完整 AI+DeFi 可组合性** |

QFC 的差异化优势：**隐私保护的 AI 推理与智能合约可组合性相结合**。目前没有任何项目能将机密 AI 计算与可编程链上逻辑结合起来。

---

## 6. 2025-2026 年关键进展

1. **NVIDIA B200 TEE-I/O**：接近零开销的机密 AI——最大的推动因素
2. **FHE 自举 <1ms**：从 2021 年的 50ms 下降；使小模型 FHE 变得实用
3. **GPU 加速 FHE**：150-200 倍加速；对 LLM 仍不够但差距在缩小
4. **SGX WireTap 攻击**：终结了 SGX，加速向 TDX + GPU TEE 迁移
5. **Phala 日处理 13.4 亿 token**：证明了生产规模的机密 LLM 推理是现实的
6. **Nillion Fission（与 Meta 合作）**：验证了 MPC+TEE 混合方案在接近生产级吞吐量下的可行性

---

## 参考文献

- [NVIDIA H100 Confidential Computing Blog](https://developer.nvidia.com/blog/confidential-computing-on-h100-gpus-for-secure-and-trustworthy-ai/)
- [H100 CC Performance Benchmark Study](https://arxiv.org/html/2409.03992v1)
- [Confidential LLM Inference Performance Study](https://www.arxiv.org/pdf/2509.18886)
- [Phala GPU TEE Deep Dive](https://phala.com/posts/Phala-GPU-TEE-Deep-Dive)
- [Phala: AMD SEV vs Intel TDX vs NVIDIA GPU TEE](https://phala.com/learn/AMD-SEV-vs-Intel-TDX-vs-NVIDIA-GPU-TEE)
- [NVIDIA B200 Blackwell GPU TEE](https://phala.com/gpu-tee/b200)
- [Privacy Stack: ZK vs FHE vs TEE vs MPC](https://blockeden.xyz/blog/2026/01/27/privacy-infrastructure-zk-fhe-tee-mpc-comparison-benchmarks/)
- [Zama Concrete ML](https://docs.zama.org/concrete-ml)
- [Nillion Tech Roadmap 2025](https://nillion.com/news/nillions-tech-roadmap-2025-advancing-the-blind-computer/)
- [Partisia MPC Technology](https://www.partisia.com/tech/technology/)
- [Secret Network 2026 Roadmap](https://scrt.network/blog/secret-network-2026-roadmap)
- [Inco Network](https://www.inco.org/)
- [Arcium Mainnet Alpha](https://blockeden.xyz/blog/2026/02/12/arcium-mainnet-alpha-encrypted-supercomputer-solana/)
- [Google Cloud Confidential Computing for AI](https://cloud.google.com/blog/products/identity-security/how-confidential-computing-lays-the-foundation-for-trusted-ai)
