# QFC Blockchain - 待办事项与路线图

> 最后更新: 2026-03-08

## 项目现状总览

| 项目 | 仓库 | 技术栈 | 状态 | 完成度 |
|------|------|--------|------|--------|
| 核心引擎 | `qfc-core` | Rust + libp2p | ✅ 生产就绪 | 95% |
| AI 推理引擎 | `qfc-core/qfc-inference` | Rust + candle | ✅ 生产就绪 | 95% |
| AI 任务协调 | `qfc-core/qfc-ai-coordinator` | Rust | ✅ 生产就绪 | 95% |
| 独立矿工 | `qfc-core/qfc-miner` | Rust + clap | ✅ 生产就绪 | 95% |
| 浏览器钱包 | `qfc-wallet` | React + TypeScript | ✅ 功能完整 | 95% |
| 区块浏览器 | `qfc-explorer` | Next.js + PostgreSQL | ✅ 功能完整 | 95% |
| JavaScript SDK | `qfc-sdk-js` | TypeScript + ethers.js | ✅ 已完成 | 90% |
| 测试网水龙头 | `qfc-faucet` | Next.js | ✅ 可用 | 85% |
| **测试网基础设施** | `qfc-testnet` | Docker + K8s + Terraform | ✅ 已完成 | 90% |
| **开发者文档站点** | `qfc-docs` | VitePress | ✅ 已完成 | 85% |
| **Python SDK** | `qfc-sdk-python` | Python + web3.py + pydantic | ✅ 已完成 | 90% |
| **CLI 工具** | `qfc-cli` | Node.js + commander | ✅ 已完成 | 90% |
| **智能合约库** | `qfc-contracts` | Solidity + Hardhat | ✅ 已完成 | 90% |
| **移动端钱包** | `qfc-wallet-mobile` | React Native + Expo | ✅ 已完成 | 85% |
| **OpenClaw 技能** | `qfc-openclaw-skill` | TypeScript + ethers.js | ✅ 已完成 | 80% |

---

## 高优先级任务

### 1. ~~测试网部署基础设施~~ ✅ 已完成

**目标**: 搭建可公开访问的测试网环境

**仓库**: `qfc-testnet/` - https://github.com/qfc-network/qfc-testnet

**完成内容**:

- [x] Docker Compose 配置
  - [x] 多节点 (5 个验证者) 本地测试配置
  - [x] 单节点开发配置
  - [x] 包含 Explorer、Faucet、RPC 的完整栈
  - [x] Nginx 负载均衡配置

- [x] Kubernetes 部署
  - [x] Helm Charts
  - [x] StatefulSet 配置 (节点持久化)
  - [x] Service 和 Ingress 配置

- [x] Terraform 云部署
  - [x] AWS 配置 (EKS + RDS + ElastiCache)
  - [x] GCP 配置 (GKE + Cloud SQL + Memorystore)
  - [x] VPC 模块

- [x] 监控系统
  - [x] Prometheus 指标收集
  - [x] Grafana 仪表板
  - [x] AlertManager 告警规则

- [ ] CI/CD 流水线 (待完善)
  - [ ] GitHub Actions 自动部署
  - [ ] 版本发布流程

**完成时间**: 2026-02-02

---

### 2. 单元测试与集成测试

**目标**: 确保代码质量和稳定性，测试覆盖率 >80%

**任务清单**:

#### qfc-sdk-js ✅ 已完成 (2026-02-02)
- [x] Provider 测试
  - [x] RPC 方法调用测试 (getValidators, getEpoch, getNetworkStats 等)
  - [x] 错误处理测试
  - [x] 网络切换测试
- [x] Wallet 测试
  - [x] 创建/导入测试 (私钥, 助记词)
  - [x] 签名测试 (signMessage, signTypedData)
  - [x] 质押方法存在性测试
- [x] Utils 测试
  - [x] 单位转换测试 (parseQfc, formatQfc, parseGwei)
  - [x] 验证函数测试 (isValidAddress, isValidMnemonic, isValidPrivateKey)
  - [x] 编码函数测试 (encodeFunctionData, keccak256, abiEncode/Decode)
  - [x] 格式化函数测试 (shortenAddress, formatRelativeTime)
- [x] Contract 测试
  - [x] ERC-20/721/1155 接口测试
  - [x] Multicall3 测试
  - [x] isContract 测试
- [x] Constants 测试
  - [x] 网络配置测试
  - [x] Gas 限制测试
  - [x] 合约地址测试

**测试统计**: 9 测试文件, 181 测试用例全部通过 (含 7 个推理测试)

#### qfc-wallet ✅ 已完成 (2026-02-02)
- [x] 加密模块测试 (encrypt/decrypt, hashPassword, generatePassword)
- [x] 验证函数测试 (isValidAddress, isValidMnemonic, isValidPrivateKey, validatePassword)
- [x] 存储模块测试 (walletStorage, txStorage, tokenStorage, networkStorage)
- [x] 常量测试 (NETWORKS, STORAGE_KEYS, MESSAGE_TYPES)
- [x] 价格工具测试 (getTokenPrice, calculateUsdValue, formatUsd)
- [x] WalletController 测试
  - [x] 钱包创建/导入
  - [x] 锁定/解锁
  - [x] 账户管理
  - [x] 余额查询
  - [x] 消息签名
  - [x] 网络切换

**测试统计**: 6 测试文件, 144 测试用例全部通过

#### qfc-core ✅ 单元测试已完成 (2026-02-03)
- [x] 核心模块单元测试 (258 测试用例)
  - [x] qfc-types: 23 测试 (区块、交易、账户、收据、验证者)
  - [x] qfc-crypto: 25 测试 (哈希、签名、VRF)
  - [x] qfc-storage: 34 测试 (RocksDB 存储层)
  - [x] qfc-trie: 61 测试 (Merkle Patricia Trie)
  - [x] qfc-state: 5 测试 (状态管理)
  - [x] qfc-executor: 4 测试 (交易执行)
  - [x] qfc-mempool: 6 测试 (交易池)
  - [x] qfc-consensus: 15 测试 (PoC 共识)
  - [x] qfc-chain: 6 测试 (链管理)
  - [x] qfc-network: 16 测试 (P2P 网络、同步协议)
  - [x] qfc-rpc: 14 测试 (JSON-RPC 类型)
  - [x] qfc-snap-sync: 22 测试 (快照同步)
  - [x] qfc-state-pruner: 8 测试 (状态剪枝)
  - [x] qfc-node: 19 测试 (节点主程序)
- [ ] 高级测试 (待完善)
  - [ ] 压力测试 / 基准测试
  - [ ] 网络分区测试
  - [ ] 多节点集成测试

**测试统计**: 14 测试模块, 258 单元测试全部通过

---

### 3. ~~开发者文档站点~~ ✅ 已完成

**目标**: 提供完整的开发者文档，方便第三方集成

**仓库**: `qfc-docs/` - https://github.com/qfc-network/qfc-docs

**技术栈**: VitePress 1.0

**完成内容**:

- [x] VitePress 框架搭建
  - [x] 完整导航配置 (顶部 + 侧边栏)
  - [x] 首页 Hero 区域
  - [x] 响应式布局

- [x] 入门指南
  - [x] QFC 介绍
  - [x] 5 分钟快速开始
  - [x] 安装指南

- [x] 核心概念
  - [x] 区块链基础 (区块、交易、账户、状态)
  - [x] PoC 共识机制

- [x] JavaScript SDK 文档
  - [x] SDK 概览
  - [x] Provider (RPC 方法)
  - [x] Wallet (签名与质押)
  - [x] 合约助手 (ERC-20/721/1155, Multicall)
  - [x] 工具函数 (单位转换、验证、编码)

- [x] API 参考
  - [x] 标准 JSON-RPC 方法
  - [x] QFC 特有方法 (验证者、质押、贡献分)

- [x] 教程
  - [x] 构建 DApp 完整教程

- [ ] 待完善内容 (可选)
  - [ ] 智能合约开发指南
  - [ ] 验证者运行指南
  - [ ] 更多教程 (创建代币、NFT 部署)
  - [ ] Python SDK 文档 (待 SDK 开发)

**完成时间**: 2026-02-02

---

### 11. ~~v2.0 AI 计算网络~~ ✅ 已完成

**目标**: 用真实 AI 推理任务替代 Blake3 PoW，使 PoC 评分中 20% 计算贡献维度产生经济价值

**设计文档**: `13-AI-COMPUTE-NETWORK.md`, `14-OPENCLAW-INTEGRATION.md`

**分支**: `v2.0` (集成分支) ← `v2.0-inference-runtime` (已合并)

#### Phase 1: 推理运行时 ✅ 已完成 (2026-03-05)

新建 crate: `qfc-inference`

- [x] `InferenceEngine` trait (异步, Send + Sync)
  - [x] `run_inference()`, `load_model()`, `benchmark()`
  - [x] `BackendType` enum (Cuda / Metal / Cpu)
- [x] CPU 后端 (确定性占位实现, blake3 链式哈希)
- [x] CUDA 后端 (脚手架, nvidia-smi 检测)
- [x] Metal 后端 (脚手架, sysctl 检测 Apple Silicon)
- [x] `InferenceProof` + `ComputeProof` 枚举 (v1 PoW + v2 AI)
- [x] `ModelRegistry` (基准模型: small/medium/large)
- [x] GPU 分级 (Hot 24GB+ / Warm 8-16GB / Cold CPU)
- [x] 硬件检测 (CUDA 设备、Apple 芯片、内存)
- [x] 31 个单元测试通过

#### Phase 2: 任务协调 ✅ 已完成 (2026-03-05)

新建 crate: `qfc-ai-coordinator`

- [x] `TaskPool` (任务队列, 按 epoch 生成)
- [x] `TaskRequirements` (最低 GPU 分级、内存、FLOPS)
- [x] `MinerRegistry` (矿工注册、能力匹配、超时清理)
- [x] 合成基准任务 (每个 GPU 分级一个)
- [x] 基础验证 (`verify_basic` — epoch/模型/FLOPS 校验)
- [x] 抽检验证 (`should_spot_check` — 5% 概率重执行)
- [x] 完整抽检 (`verify_spot_check` — 重跑推理, 比对输出哈希)
- [x] 22 个单元测试通过

#### Phase 3: 现有 crate 适配 ✅ 已完成 (2026-03-05)

- [x] `qfc-types` — 新增 `InferenceProof`, `ComputeProof`, `BackendType`, `ModelId`, `ComputeTaskType`; `ValidatorNode` 增加 v2 字段 (inference_score, gpu_memory_mb, 等)
- [x] `qfc-pow` — 新增 `verify_inference_proof()`, `verify_compute_proof()`
- [x] `qfc-consensus` — v2 评分: `inference_score = flops_norm * sqrt(tasks) * pass_rate²`; 无推理分时回退到 hashrate
- [x] `qfc-node` — 双模式 `MiningService` (`PowV1` / `InferenceV2`)
- [x] `qfc-rpc` — 3 个新端点: `getComputeInfo`, `getSupportedModels`, `getInferenceStats`

#### Phase 4: 独立矿工程序 ✅ 已完成 (2026-03-05)

新建 crate: `qfc-miner` (独立二进制)

- [x] CLI (clap): `--validator-rpc`, `--wallet`, `--private-key`, `--backend auto|cuda|metal|cpu`, `--model-dir`, `--max-memory`
- [x] 硬件检测 + 基准测试
- [x] `InferenceWorker` 推理循环 (10s epoch)
- [x] 证明提交脚手架 (RPC)
- [x] Proof 签名 (`--private-key` → Keypair::sign_hash, 启动时验证与 --wallet 地址一致)

**Phase 1-4 统计**: 3 个新 crate, 5 个修改 crate, 3,372 行新代码, 134 个测试通过

**Phase 5-6 统计**: candle ML 集成 + 端到端推理验证, 316 个测试通过 (截至 Phase 6)

**Phase 7 统计**: 3 仓库更新 (qfc-core 5 文件, qfc-testnet 5 文件, qfc-explorer 6 文件), 16 个新/修改文件

#### Phase 5: candle 模型集成 ✅ 已完成 (2026-03-04)

- [x] 集成 `candle-core` + `candle-nn` + `candle-transformers`
- [x] CPU 后端: 真实 BERT embedding 推理 (candle feature flag)
- [x] Metal 后端: `candle-core` Metal feature (Apple Silicon)
- [x] 模型下载与缓存 (`ModelCache`, `download_model()`)
- [x] 基准模型: BERT embedding (all-MiniLM-L6-v2 式)
- [x] 确定性推理验证 (blake3 输出哈希, 固定 seed)
- [x] CUDA 后端: `Dockerfile.cuda` + `Dockerfile.miner-cuda` (nvidia/cuda:12.2.0, `--features candle,cuda`)

#### Phase 6: 端到端集成 ✅ 已完成 (2026-03-05)

- [x] Worker → TaskCoordinator → ProofSubmission 完整流程
- [x] `qfc-miner` crate: InferenceMiner 推理循环 + RPC 提交
- [x] 矿工通过 RPC 提交证明 (`qfc_submitInferenceProof`)
- [x] 推理证明签名 + P2P 广播 (ValidatorMessage::InferenceProof)
- [x] 验证者节点 `handle_inference_proof()`:
  - [x] 签名验证 + epoch/模型/FLOPS 基础校验
  - [x] 5% 概率抽检重执行 (`should_spot_check` + `verify_spot_check`)
  - [x] 输出哈希不匹配 → `InvalidInference` 惩罚 (5% stake, 6h jail)
  - [x] 通过 → `update_inference_score()`
- [x] CpuEngine 接入 SyncManager 用于抽检验证
- [x] CpuEngine 接入 RpcServer 用于 RPC 抽检验证
- [x] RPC `submit_inference_proof` 完整链路：签名验证 → verify_basic → 5% spot-check → slash/update_inference_score
- [x] `tasks_completed` 累加 bug 修复 (saturating_add)
- [x] 抽检集成测试 (test_verify_spot_check_pass, test_verify_spot_check_mismatch)
- [ ] 多矿工并发提交测试
- [ ] 矿工通过 RPC 获取任务 (`qfc_getInferenceTask`)

#### Phase 7: 测试网部署 ✅ 已完成 (2026-03-05)

- [x] Docker 镜像更新
  - [x] Dockerfile 构建 qfc-node + qfc-miner 双二进制
  - [x] Dockerfile.miner 独立矿工镜像 (env vars, /models 卷)
  - [x] 入口脚本支持 `--compute-mode`, `--inference-backend`, `--model-dir`
- [x] CLI 扩展: `--compute-mode pow|inference`, `--inference-backend`, `--model-dir`
- [x] RPC 扩展: `RpcValidator` 新增 inference_score, compute_mode, tasks_completed
- [x] 测试网混合模式
  - [x] docker-compose.yml 新增 inference profile (独立矿工)
  - [x] docker-compose.mixed.yml (3 PoW + 2 inference 验证者 + 2 独立矿工)
  - [x] 环境变量: QFC_COMPUTE_MODE, QFC_INFERENCE_BACKEND, MINER_*_WALLET
- [x] 矿工仪表板
  - [x] Grafana qfc-inference dashboard (8 面板: 任务数、FLOPS、通过率、矿工数)
  - [x] Prometheus inference 告警规则 (矿工离线、低通过率、无任务、FLOPS 归零)
  - [x] Explorer /inference 页面 (统计卡片、计算信息、验证者表格)
  - [x] Explorer /network 页面新增 Compute Mode + Inference Score 列
  - [x] API: /api/inference 路由 (15s ISR)
  - [x] 格式化: formatFlops(), formatDuration()
- [x] 过渡策略: deploy-mixed.sh 分阶段部署脚本
  - [x] Phase A: 全 PoW (5 验证者)
  - [x] Phase B: 混合 (3 PoW + 2 inference + 2 矿工)
  - [x] Phase C: 大部分推理 (1 PoW + 4 inference + 2 矿工)
  - [x] Phase D: 全推理 (5 inference + 2 矿工)

#### Phase 8: 生态集成 ✅ 已完成 (2026-03-05)

- [x] SDK 更新 (JS/Python 支持推理相关 RPC)
  - [x] qfc-sdk-js: 8 个推理类型 + 7 个 Provider 方法 + 7 个测试
  - [x] qfc-sdk-python: 6 个 Pydantic 模型 + 7 个 Provider 方法 + 11 个测试
- [x] 模型注册表链上治理 (验证者投票 >2/3)
  - [x] ModelGovernance 模块 (propose, vote, tally)
  - [x] ProposalStatus (Active/Passed/Rejected/Expired)
  - [x] 投票期可配置 (默认 1 天), 超级多数 >2/3
  - [x] 3 个新 RPC 端点: proposeModel, voteModel, getModelProposals
  - [x] 7 个治理单元测试
- [x] 推理 API 对外开放 (付费调用)
  - [x] PublicTask + PublicTaskStatus (Pending/Assigned/Completed/Failed/Expired)
  - [x] TaskPool 扩展: submit_public_task, get_public_task, complete_public_task
  - [x] 2 个新 RPC 端点: submitPublicTask, getPublicTaskStatus
- [x] Explorer 展示推理统计增强
  - [x] /inference 页面新增 Model Registry 表格
  - [x] /governance/models 治理页面 (统计卡片 + 提案表格 + 已批准模型)
  - [x] API 路由: /api/governance/models (15s ISR)
- [x] OpenClaw 技能 MVP (新仓库 qfc-openclaw-skill)
  - [x] QFCWallet 类 (创建/导入/余额/转账/签名)
  - [x] SecurityPolicy 类 (5 条预交易安全规则)
  - [x] SKILL.md 代理能力描述
  - [x] 参考文档 (链概览 + 钱包操作指南)

**Phase 8 统计**: 5 仓库更新, 31 文件新增/修改, SDK 测试 188 (JS) + 18 (Python), Core 50 测试通过

---

### 12. AI 推理链路：设计 vs 代码落地差距分析

> 更新: 2026-03-07

**设计文档** `13-AI-COMPUTE-NETWORK.md` 已覆盖完整推理链路。核心执行层（任务分发、推理执行、结果验证）已实现，但**用户入口层**和**经济结算层**仍有落地差距。

#### 完整链路 6 个环节现状

| # | 环节 | 设计 | 代码 | 完成度 | 主要差距 |
|---|------|------|------|--------|---------|
| 1 | 用户发起推理请求 | ✅ | ✅ | 98% | 钱包/Explorer 已集成推理 UI；专用 TX 类型已添加 |
| 2 | 交易路由到 AI-VM | ✅ | ✅ | 95% | Fee escrow 已实现；任务路由+优先级+超时重分配完成 |
| 3 | GPU 节点执行推理 | ✅ | ✅ | 98% | ModelCache LRU+自动下载+GPU 指标采集完成；任务并行待实现 |
| 4 | 推理结果验证 | ✅ | ✅ | 100% | 多验证者仲裁面板+多数投票+Proof 上链 Merkle 验证全部完成 |
| 5 | 结果返回用户 | ✅ | ✅ | 90% | base64 编码+WebSocket 订阅+SDK 完成；大结果 IPFS 未集成 |
| 6 | 费用结算 | ✅ | ✅ | 95% | Escrow+70/10/20 分配+定价公式+slashing 全部完成 |

#### 环节 1: 用户发起推理请求 (90%)

**已实现:**
- [x] RPC `submitPublicTask` 端点 + Ed25519 签名验证 (`qfc-rpc/src/qfc.rs`)
- [x] `PublicTask` + `PublicTaskStatus` 状态机 (`qfc-ai-coordinator/src/task_pool.rs`)
- [x] 支持 4 种任务类型: TextGeneration / ImageClassification / Embedding / OnnxInference

**待完成:**
- [x] **专用交易类型**: `TransactionType::InferenceTask = 10` 已定义 (`qfc-types/src/transaction.rs`)，executor 已有处理分支
- [x] **钱包 SDK 集成 (查询)**: qfc-sdk-js Provider 已有 7 个推理方法 + 8 个类型 (Phase 8)
- [ ] **钱包推理 UI**: qfc-wallet 添加推理任务提交界面 (未开始)
- [x] **OpenClaw 推理技能**: `QFCInference` 类已完成 — submitTask/getTaskStatus/waitForResult/getModels/getStats/estimateFee/decodeResult (v3.0.2 修复 payload 对齐)

#### 环节 2: 交易路由到 AI-VM (95%) ✅

**已实现:**
- [x] `TaskPool` — 任务提交、合成任务生成 (每 epoch 3 个)、按能力匹配矿工
- [x] `TaskRouter` — Hot/Warm/Cold 三层调度、负载均衡、5 分钟超时清理
- [x] `TaskRequirements` — GPU tier / VRAM / FLOPS 匹配
- [x] **Fee escrow 实现**: `submitPublicTask` RPC 中 `sub_balance()` 锁定 fee (Phase A 完成)
- [x] **RPC→TaskPool 完整流转**: submitPublicTask→task_pool→fetch→proof→settle，PublicTask 状态完整追踪 (Phase C1)
- [x] **任务超时重分配**: `reassign_stale_tasks()` 30s 超时自动回队列 (Phase C2)
- [x] **优先级队列**: `fetch_task_for()` 按 max_fee 降序选择，高价任务优先 (Phase C3)

#### 环节 3: GPU 节点执行推理 (95%)

**已实现:**
- [x] `InferenceMiner` 完整工作循环: fetch → run → submit proof (`qfc-miner/src/worker.rs`)
- [x] 多后端引擎: CPU (candle/BERT) / CUDA / Metal (`qfc-inference/src/backend/`)
- [x] RPC `getInferenceTask` 矿工拉取任务
- [x] GPU tier 分类 + benchmark 评分 + 矿工注册

**已实现 (Phase E):**
- [x] **模型下载与缓存管理**: `ModelCache` LRU 驱逐 + `ensure_model()` 自动下载 (`qfc-inference/src/model.rs`)
- [x] **GPU 实时监控**: `GpuMetrics` 温度/功率/利用率采集，支持 NVIDIA/Metal/CPU (`qfc-inference/src/gpu_monitor.rs`)

**暂不实现:**
- ~~任务并行执行~~: 当前单任务推理仅 40-80ms，瓶颈在 RPC 网络延迟而非推理速度；测试网任务供给有限，串行即可处理；并行涉及 InferenceEngine 共享和显存并发管理，复杂度高。等主网任务量上来后根据实际瓶颈再做。

#### 环节 4: 推理结果验证 (100%) ✅

**已实现:**
- [x] `InferenceProof` 结构: validator, epoch, input_hash, output_hash (blake3), flops, signature
- [x] 基础验证: epoch 匹配、模型审批、FLOPS 合理性 (`qfc-ai-coordinator/src/verification.rs`)
- [x] 5% 概率抽查: hash 决定 → 重新执行推理 → 比对 output_hash
- [x] `handle_inference_proof()` 完整流程 (`qfc-node/src/sync.rs`)
- [x] RPC `submitInferenceProof` 端点
- [x] **Challenge 仲裁**: `ArbitrationPanel` 多验证者投票 + 多数决裁定 (`qfc-ai-coordinator/src/challenge.rs`)
- [x] **Proof 上链确认**: `proofs_root` Merkle root 写入 BlockHeader，出块+验证双向校验 (`qfc-consensus/src/engine.rs`)

#### 环节 5: 结果返回用户 (90%) ✅

**已实现:**
- [x] RPC `getPublicTaskStatus(task_id)` 查询端点
- [x] `PublicTaskStatus::Completed { result_data, miner, execution_time_ms }`
- [x] **结果编码格式**: JSON envelope + base64 payload (B1)
- [x] **WebSocket 订阅**: `qfc_subscribeTaskStatus` 推送状态变更 (B3)
- [x] **超时通知**: Expired 状态通过 RPC 和 WS 推送返回
- [x] **SDK 集成**: qfc-sdk-js `getPublicTaskStatus()` + `waitForInferenceResult()` (B4)
- [x] **OpenClaw 推理技能**: `QFCInference` 类 — 查询/等待/解码结果 (B5)

**待完成:**
- [x] **大结果处理**: IpfsClient 自动上传 >1MB 结果到 Kubo, `qfc_getInferenceResult(cid)` 网关代理

#### 环节 6: 费用结算 (95%) ✅

**已实现:**
- [x] `calculate_inference_score()` — `sqrt(tasks) * (flops/1e9) * pass_rate` (`qfc-consensus/src/scoring.rs`)
- [x] PoC v2 评分集成 — inference_score 占计算维度 20% 权重
- [x] 矿工注册 RPC `registerMiner()` + GPU 声明验证
- [x] `ValidatorNode` 包含 `inference_score` / `tasks_completed` 字段
- [x] **Escrow**: `submitPublicTask` RPC 扣除 `max_fee` (`qfc-rpc/src/server.rs:1672-1687`)
- [x] **分润 70/10/20**: `settle_inference_fees()` 完整实现 (`qfc-node/src/producer.rs:309-375`)
- [x] **超时退款**: `prune_expired_public()` + `add_balance` 退还 escrow
- [x] **Slashing**: `slash_validator()` 扣 5% stake + 6h jail (`qfc-node/src/sync.rs:1003`)
- [x] **Fee 定价模型**: `estimate_base_fee()` 按 GFLOPS + GPU tier 估价 (`qfc-ai-coordinator/src/task_types.rs`)
- [x] **结算 input_hash 索引**: 修复 proof→task 匹配 bug (之前用 task_id 查找，永远不匹配)

**待完成:**
- [ ] **区块奖励中的推理贡献**: scoring 有但奖励分配逻辑缺失

---

### 13. AI 推理链路补全路线图

> 目标: 逐项补齐上述 6 个环节的空白，使推理链路端到端可用

#### Phase A: 费用结算核心 ✅ 完成

> 环节 6 是整个链路的经济基础，不结算 = 无激励 = 无矿工

- [x] A1: Escrow 模块 — `submitPublicTask` RPC 中 `sub_balance()` 锁定 fee
- [x] A2: 结算执行 — `settle_inference_fees()` 70/10/20 分润 + **修复 input_hash 索引 bug**
- [x] A3: 超时退款 — `prune_expired_public()` 自动退还 escrow
- [x] A4: Slashing 执行 — `slash_validator()` 5% stake + 6h jail (sync.rs)
- [x] A5: Fee 定价模型 — `estimate_base_fee()` 按 GFLOPS×GPU tier 估算，RPC 校验 min fee

#### Phase B: 结果返回完善 ✅ 完成

> 环节 5 是用户体验的最后一公里

- [x] B1: 结果编码规范 — JSON envelope + base64 payload + submitter/model/timestamps 元信息
- [x] B2: 大结果存储 — IpfsClient (Kubo API) 自动上传 >1MB 结果, ResultStorage::Ipfs { cid, size, preview }, RPC 代理 `getInferenceResult(cid)`, SDK/OpenClaw 透明获取
- [x] B3: 结果推送 — `qfc_subscribeTaskStatus` WebSocket 订阅，自动推送状态变更至终态
- [x] B4: SDK 集成 — `getPublicTaskStatus()` 结构化返回 + `waitForInferenceResult()` 轮询
- [x] B5: OpenClaw 推理技能 — `QFCInference` 类: getModels/getStats/getTaskStatus/waitForResult/decode

#### Phase C: 任务路由加固 ✅ 完成

> 环节 2 的可靠性直接影响任务完成率

- [x] C1: 流转审计 + 状态追踪 — `fetch_task_for()` 时 PublicTask 状态更新为 Assigned，记录 miner/时间
- [x] C2: 超时重分配 — `reassign_stale_tasks()` 30s 内无 proof 自动回 pending 队列，block producer 每轮调用
- [x] C3: 优先级队列 — `fetch_task_for()` 扫描全 pending，选择 max_fee 最高的匹配任务

#### Phase D: 用户入口增强 ✅ 已完成 (2026-03-07)

> 环节 1 降低使用门槛

- [x] D1: `TransactionType::InferenceTask` — 专用交易类型 (enum variant + executor handler + RPC tx_type 映射)
- [x] D2: 钱包推理 UI — qfc-wallet Inference 页面 (任务查询 + 状态展示 + i18n 4语言)
- [x] D3: Explorer 推理状态 — TaskLookup 组件 + `/api/inference/task` API + 状态展示

#### Phase E: 执行层加固 ✅ 已完成 (2026-03-07)

> 环节 3、4 的生产化

- [x] E1: 模型下载管理器 — ModelCache LRU 驱逐 (`evict_lru()`) + `ensure_model()` 自动下载 + `with_max_size()` 容量限制
- [x] E2: GPU 监控指标 — `GpuMetrics` struct (温度/功率/利用率/显存)，nvidia-smi 采集 (CUDA)，系统内存采集 (Metal/CPU)
- [x] E3: Challenge 仲裁 — `ArbitrationPanel` 多验证者投票 + `ArbitrationManager` 争议管理 + spot-check 失败自动开启仲裁 + 多数投票 slash

---

### 历史记录: 已完成的推理链路里程碑

<details>
<summary>P0/P1/P2 完成记录 (2026-03-05)</summary>

**P0 — 链路基础：** ✅ 已完成

- [x] **Proof → 链状态更新**: `submit_inference_proof()` RPC 验证通过后调用 `update_inference_score()`
- [x] **Proof 签名**: qfc-miner `--private-key` 参数签名 proof；RPC 端验证签名
- [x] **Spot-check 实际执行**: RPC handler 注入 CPU InferenceEngine，5% 概率重跑推理验证
- [x] **Slashing 触发**: 抽检输出哈希不匹配 → `slash_validator(5%, 6h jail)` (触发路径有，执行待确认)
- [x] **tasks_completed 累加 bug**: 修复 `saturating_add`

**P1 — 框架完整：** ✅ 已完成

- [x] **Proof 上链框架**: `proofs_root` 写入 BlockHeader, ProofPool 缓冲池
- [x] **费用结算框架**: 70/10/20 分润设计，出块时匹配公共任务
- [x] **公共任务流**: submitPublicTask + Ed25519 签名 + getPublicTaskStatus
- [x] **CUDA 后端**: Dockerfile.cuda + Dockerfile.miner-cuda

**P2 — 高级功能：** ✅ 已完成

- [x] **矿工注册上链**: GPU Benchmark + Tier + `qfc_registerMiner` RPC
- [x] **Challenge Tasks**: 预计算挑战任务 + 自适应注入率
- [x] **冗余验证**: 高价值任务 3 矿工多数一致
- [x] **三层模型调度**: Hot/Warm/Cold + LRU 驱逐
- [x] **Task Router**: 链下全局调度 + 心跳 RPC

</details>

---

## 中优先级任务

### 4. ~~Python SDK~~ ✅ 已完成

**目标**: 为 Python 开发者提供 SDK

**仓库**: `qfc-sdk-python/` - https://github.com/qfc-network/qfc-sdk-python

**技术栈**: Python 3.10+, web3.py, pydantic

**完成内容**:

- [x] 项目初始化 (hatchling 构建)
- [x] QfcProvider (JSON-RPC 提供者)
  - [x] 标准以太坊方法 (getBalance, getBlock, etc.)
  - [x] QFC 特有方法 (getValidators, getContributionScore)
- [x] QfcWallet (钱包管理)
  - [x] 私钥/助记词/随机创建
  - [x] 质押操作 (stake, delegate, claimRewards)
- [x] StakingClient (高级质押 API)
- [x] 合约助手
  - [x] ERC-20, ERC-721, ERC-1155 封装
  - [x] Multicall3 批量调用
- [x] Pydantic 类型定义
- [x] 工具函数 (单位转换、验证、格式化)
- [x] 单元测试
- [ ] PyPI 发布 (待完善)

**完成时间**: 2026-02-02

---

### 5. ~~CLI 工具增强~~ ✅ 已完成

**目标**: 提供功能完整的命令行工具

**仓库**: `qfc-cli/` - https://github.com/qfc-network/qfc-cli

**技术栈**: Node.js + commander.js + ethers.js v6

**完成内容**:

- [x] 命令框架重构 (commander.js, ESM)
- [x] 账户管理命令
  - [x] create, import, list, balance, default, export
  - [x] 加密 keystore (~/.qfc/keystore/)
- [x] 交易命令
  - [x] send, status, get, receipt
- [x] 质押命令
  - [x] deposit, withdraw, delegate, undelegate, rewards, info
- [x] 合约命令
  - [x] deploy, call, send, code
- [x] 验证者命令
  - [x] list, info, register, update-commission
- [x] 网络命令
  - [x] info, stats, epoch, list, switch, block, gas-price
- [x] 配置管理
  - [x] get, set, unset, reset, path, env
- [x] 输出格式化 (JSON/Table, chalk, ora)
- [x] 直接 RPC 命令
- [ ] Shell 自动补全 (待完善)

**完成时间**: 2026-02-02

---

### 6. ~~移动端钱包~~ ✅ 已完成

**目标**: iOS 和 Android 原生钱包应用

**仓库**: `qfc-wallet-mobile/` - https://github.com/qfc-network/qfc-wallet-mobile

**技术栈**: React Native 0.74 + Expo SDK 52 + Redux Toolkit

**完成内容**:

- [x] 钱包创建/导入 (助记词, 私钥)
- [x] 生物识别 (Face ID / 指纹)
- [x] 发送/接收 QFC (含 QR 扫描)
- [x] 交易历史 (状态追踪)
- [x] ERC-20 代币管理
- [x] 质押功能 (stake, delegate, claim)
- [x] WalletConnect v2 支持 (基础框架)
- [x] 深度链接 (qfc://)
- [x] 主题支持 (亮色/暗色/系统)
- [x] 网络切换 (主网/测试网)
- [ ] 推送通知 (待完善)
- [ ] App Store/Play Store 发布 (待完善)

**项目结构** (51 文件, 6,666 行):
- `app/` - Expo Router 屏幕 (文件路由)
- `src/components/` - UI 组件
- `src/services/` - 业务逻辑
- `src/store/` - Redux 状态管理
- `src/hooks/` - 自定义 Hooks

**完成时间**: 2026-02-02

---

### 7. ~~智能合约示例库~~ ✅ 已完成

**目标**: 提供常用合约模板和示例

**仓库**: `qfc-contracts/` - https://github.com/qfc-network/qfc-contracts

**技术栈**: Solidity 0.8.20 + Hardhat + OpenZeppelin

**完成内容**:

- [x] Hardhat 项目配置 (TypeScript, 多网络)
- [x] 代币合约
  - [x] QFCToken.sol - ERC-20 (mint/burn/permit/batch)
  - [x] QFCNFT.sol - ERC-721 (enumerable, mint price)
  - [x] QFCMultiToken.sol - ERC-1155 (supply tracking)
- [x] 质押合约
  - [x] StakingPool.sol - 时间加权奖励, 锁定期
  - [x] RewardDistributor.sol - Merkle 树证明分发
- [x] 治理合约
  - [x] QFCGovernor.sol - OpenZeppelin Governor + Timelock
  - [x] Treasury.sol - 角色访问控制
- [x] DeFi 合约
  - [x] SimpleSwap.sol - 恒定乘积 AMM (x*y=k), 0.3% 费率
  - [x] Vault.sol - ERC4626 风格收益聚合
- [x] 工具合约
  - [x] Multicall.sol - 批量调用
  - [x] Create2Factory.sol - 确定性部署
- [x] 部署脚本 (deploy.ts, deploy-staking.ts, deploy-defi.ts)
- [x] 单元测试 (QFCToken.test.ts, SimpleSwap.test.ts)
- [x] 文档 (README.md, CLAUDE.md)
- [ ] 更多合约 (LendingPool 待完善)

**完成时间**: 2026-02-02

---

## 低优先级任务

### 8. 钱包增强功能 (部分完成)

**仓库**: `qfc-wallet/` (现有)

**已完成内容**:

- [x] 多语言支持 (i18n)
  - [x] 英文 (English)
  - [x] 中文 (简体中文)
  - [x] 日文 (日本語)
  - [x] 韩文 (한국어)
  - [x] 语言选择器 (Settings 页面)
  - [x] Chrome Storage 持久化
  - [x] 所有页面翻译完成 (Home, Send, Receive, Settings, CreateWallet, Unlock, AddToken, ApprovalDialog)
- [x] 地址簿
  - [x] 联系人 CRUD 操作
  - [x] 地址验证
  - [x] 复制地址功能
  - [x] 在 Settings 页面入口

**待完成内容**:

- [ ] 硬件钱包支持
  - [ ] Ledger 集成
  - [ ] Trezor 集成
- [ ] WalletConnect v2
- [ ] 交易加速/取消
- [ ] NFT 展示

**完成时间**: 2026-02-02 (i18n + 地址簿)

---

### 9. 区块浏览器 — Etherscan 对标

**仓库**: `qfc-explorer/` + `qfc-explorer-api/`

**v2.0 已完成功能** (2026-03-08):

- [x] 核心浏览 (28 页面, 18 API 路由)
  - [x] 区块/交易/地址详情页 (含 cursor 分页)
  - [x] 内部交易 (debug_traceTransaction)
  - [x] 事件日志自动 ABI 解码
  - [x] Mempool/待处理交易浏览
- [x] 智能合约
  - [x] 合约验证 (Solc 编译 + Standard JSON Input)
  - [x] 合约交互 UI (Read/Write)
  - [x] 代理合约检测 (EIP-1967/1822/Beacon)
  - [x] Etherscan 兼容 API (Hardhat/Foundry verify)
- [x] Token & NFT
  - [x] ERC-20/721/1155 跟踪
  - [x] 持有者排行 + 分布图
  - [x] NFT 画廊 (IPFS 元数据解析)
- [x] 分析与监控
  - [x] Analytics 面板 (TPS, Gas, 出块时间图表)
  - [x] Gas Tracker (价格统计, 区块利用率, 消耗排行)
  - [x] 排行榜 (余额/活跃度/验证者/合约)
  - [x] CSV 数据导出
- [x] 搜索 & 工具
  - [x] 全局搜索 (区块/交易/地址/Token/标签)
  - [x] ABI 工具 (keccak256, selector 查询, calldata 解码)
  - [x] 地址标签系统
- [x] 基础设施
  - [x] SEO metadata + Open Graph
  - [x] i18n 4 语言 (en/zh/ja/ko)
  - [x] Skeleton loading + Error boundaries
  - [x] SSE + WebSocket 实时更新
  - [x] Prometheus 监控 (API + Indexer)
  - [x] 116 个单元测试

**与 Etherscan 的差距** → 见 §14

---

### 10. ~~QVM 虚拟机~~ ✅ 已完成

**目标**: 实现设计文档中规划的原生虚拟机

**仓库**:
- `qfc-core/crates/qfc-qsc/` (QuantumScript 编译器)
- `qfc-core/crates/qfc-qvm/` (QVM 执行引擎)

**设计文档**: `10-QUANTUMSCRIPT-SPEC.md`

**已完成内容**:

- [x] QuantumScript 语言设计
  - [x] 词法结构 (关键字、运算符、注释)
  - [x] 类型系统 (原始类型、复合类型、资源类型)
  - [x] 合约结构 (状态、事件、错误、修饰符)
  - [x] 函数类型 (pure, view, payable, parallel)
  - [x] 控制流 (if, match, for, while, loop)
  - [x] 内存模型 (存储布局、所有权、借用)
  - [x] 并行执行 (parallel 注解、状态访问提示)
  - [x] 形式化验证 (spec, invariant, requires, ensures)
  - [x] EVM 互操作 (跨 VM 调用)
  - [x] 标准库设计 (math, crypto, collections, standards)
  - [x] Gas 模型
  - [x] 示例合约 (Token, StakingPool)
  - [x] 语法规范 (EBNF)

- [x] 编译器前端 (qfc-qsc crate)
  - [x] 词法分析器 (Lexer) - 完整 Token 定义, 支持所有 QuantumScript 语法
  - [x] 语法分析器 (Parser) - Pratt 解析器, 完整 AST 生成
  - [x] AST 定义 - 完整 AST 节点类型 (Item, Expr, Stmt, Type, Pattern)
  - [x] 类型检查器 - 类型推导、作用域管理、错误报告
  - [x] QVM 字节码生成 - 操作码定义、指令编码、合约编译

- [x] QVM 执行引擎 (qfc-qvm crate)
  - [x] 字节码解释器实现 (Executor) - 完整操作码支持
  - [x] 栈机执行模型 (Stack, Memory, Storage, Heap)
  - [x] EVM 兼容 Gas 计量 (GasMeter, GasCosts)
  - [x] 执行上下文 (ExecutionContext) - address, caller, value, block info
  - [x] 资源系统运行时 (ResourceTracker)
    - [x] 线性类型检查
    - [x] 所有权追踪
    - [x] 借用检查 (immutable/mutable)
  - [x] 存储访问 (warm/cold, EIP-2929 style)
  - [x] 日志发射 (Log0-Log4)
  - [x] 42 个单元测试通过

- [x] 标准库实现 (stdlib module)
  - [x] math: min, max, abs, sqrt, pow, log2, clamp, mulDiv, mulDivUp
  - [x] crypto: keccak256, sha256, blake3, ecrecover, verify (Ed25519)
  - [x] collections: array (length, push, pop, get, set, slice, concat)
  - [x] bytes/string: length, concat, slice
  - [x] abi: encode, encodePacked, decode, encodeCall
  - [x] StdlibRegistry 函数注册表

- [x] EVM 互操作模块 (interop module)
  - [x] InteropManager: 跨 VM 调用协调
  - [x] CallBridge: QVM → EVM 调用执行
  - [x] MultiCall: 批量跨 VM 调用
  - [x] Erc20Helper: ERC-20 代币高级接口
  - [x] StateCoordinator: 跨 VM 状态追踪
  - [x] ReentrancyGuard: 重入攻击保护
  - [x] EIP-2929/2930 兼容 (warm/cold, access list)

- [x] 端到端测试 (e2e tests)
  - [x] 编译 + 执行完整流程验证
  - [x] 算术运算 (add, mul, sub)
  - [x] 比较运算 (gt, lt, eq)
  - [x] 条件跳转 (if/else)
  - [x] 循环执行 (while with locals)
  - [x] 位运算 (and, or, shl, shr)
  - [x] 存储操作 (sload, sstore)
  - [x] 上下文访问 (caller, value)
  - [x] Gas 计量和 OutOfGas 错误
  - [x] 70 个测试通过 (60 unit + 10 e2e)

- [x] JIT 编译 (Cranelift)
  - [x] JitCompiler: 函数编译到原生代码
  - [x] CodeGenerator: QVM 操作码 → Cranelift IR
  - [x] JitRuntime: 运行时支持 (storage, context)
  - [x] 编译结果缓存 (可配置大小)
  - [x] 算术、比较、位运算、控制流支持
  - [x] 可选 feature: `--features jit`

- [x] 开发工具 (Dev Tools)
  - [x] VS Code 扩展 (qfc-vscode)
    - [x] TextMate 语法高亮 (.qs, .qsc 文件)
    - [x] 25+ 代码片段 (contract, fn, event, erc20, spec 等)
    - [x] LSP 客户端 (连接 qsc-lsp)
    - [x] 命令: Restart Server, Format, Compile
    - [x] 配置: LSP 路径, 跟踪级别
  - [x] qsc-lsp 语言服务器 (qfc-core/crates/qfc-lsp)
    - [x] 实时诊断 (词法、语法、类型错误)
    - [x] 代码补全 (关键字、类型、内置函数)
    - [x] 悬停信息 (语言构造说明)
    - [x] 文档大纲 (contracts, functions, structs, events)
    - [x] stdio 传输协议
    - [x] 6 个单元测试通过
  - [x] qsc fmt 代码格式化 (qfc-core/crates/qfc-qsc)
    - [x] AST 美化输出
    - [x] 可配置缩进 (空格/制表符, 大小)
    - [x] 可配置最大行宽
    - [x] CLI: `qsc fmt <file> [--check] [--write]`
    - [x] 3 个单元测试通过
  - [x] qsc CLI 工具 (qfc-core/crates/qfc-qsc)
    - [x] `qsc compile` - 编译到字节码
    - [x] `qsc fmt` - 代码格式化
    - [x] `qsc check` - 类型检查
    - [x] `qsc parse` - 调试 AST 输出

**完成时间**: 2026-02-02 (语言设计 + 编译器前端 + 执行引擎 + 标准库 + EVM 互操作 + 开发工具 + JIT 编译)

**状态**: ✅ 完成

---

### 14. Explorer — 对标 Etherscan 路线图

> 目标: 补齐与 Etherscan 的功能差距，优先面向主网上线的必备功能

#### Phase A: 用户系统 ✅ 已完成 (2026-03-08)

- [x] A1: 用户注册/登录 (邮箱 + OAuth) — JWT + bcrypt + refresh token
- [x] A2: Watchlist — 关注地址，余额变动通知 — 最多50地址，余额enrichment
- [x] A3: API Key 管理 — 3级配额 (free/standard/pro)，token bucket rate limit
- [x] A4: 用户地址备注 — 私有地址标签，最多500字符
- [x] A5: 交易备注 — 私有交易备注

#### Phase B: 市场数据集成 ✅ 已完成 (2026-03-08)

- [x] B1: Token 价格集成 — CoinGecko API + 手动价格，15分钟缓存，SVG sparkline
- [x] B2: Token 排行页 — 按市值/持有人数/交易量/价格排序，类型筛选
- [x] B3: 地址余额估值 — 持仓 USD 价值，组合总价值
- [x] B4: Gas 价格预言机 — 百分位 slow/standard/fast，homepage widget + 详情页

#### Phase C: 合约增强 ✅ 已完成 (2026-03-08)

- [x] C1: Read as Proxy — EIP-1967/1822/Beacon 代理检测，Read/Write as Proxy tabs
- [x] C2: 多文件验证 — Standard JSON Input，拖拽上传，入口合约选择器
- [x] C3: Vyper 合约验证 — CLI/Docker 编译，metadata stripping，Vyper 验证 tab
- [x] C4: 合约 Diff — LCS line diff，side-by-side DiffView，ABI diff 摘要

#### Phase D: 高级过滤与搜索 ✅ 已完成 (2026-03-08)

- [x] D1: 高级交易过滤 — 按金额范围、方法名、时间范围、交易类型
- [x] D2: Token Approval 管理页 — 扫描 Approval/ApprovalForAll，生成撤销 calldata
- [x] D3: 地址标签分类 — 交易所、DeFi、桥、MEV bot 等分类标签，颜色编码
- [x] D4: 批量地址查询 — POST /batch/addresses，最多20地址，CSV 导出

#### Phase E: 社区 & 生态 ✅ 已完成 (2026-03-08)

- [x] E1: 合约评论系统 — 星级评分 + Markdown 评论，举报/审核
- [x] E2: DeFi 协议识别 — 30+ 函数选择器，7个分类，彩色标签
- [x] E3: 地址画像 — GitHub 风格热力图，交互摘要，活跃度分析
- [x] E4: 交易可视化 — 纯 SVG Sankey diagram，native/ERC-20/internal 流向
- [x] E5: 多签钱包检测 — Safe/Gnosis 代理检测，owners/threshold 展示

---

## 优先级排序建议

```
v2.0 AI 计算网络 (✅ 全部完成):
├── ✅ Phase 1: 推理运行时 (qfc-inference, 3 后端)
├── ✅ Phase 2: 任务协调 (qfc-ai-coordinator)
├── ✅ Phase 3: 现有 crate 适配 (types/pow/consensus/node/rpc)
├── ✅ Phase 4: 独立矿工程序 (qfc-miner)
├── ✅ Phase 5: candle 模型集成 (BERT embedding, Metal, CUDA Docker)
├── ✅ Phase 6: 端到端集成 (提交→广播→验证→抽检→惩罚)
├── ✅ Phase 7: 测试网部署 (Docker + 混合模式 + 仪表板 + 分阶段脚本)
├── ✅ Phase 8: 生态集成 (SDK推理, 治理, 公开API, Explorer, OpenClaw)
├── ✅ P1 功能完整性 (证明上链, 费用结算70/10/20, 公共任务流, CUDA镜像)
└── ✅ P2 生产就绪 (矿工注册, 挑战任务, 冗余验证, 三层调度, Task Router)

已完成基础设施:
├── ✅ 测试网部署 (Docker/K8s/Terraform/监控)
├── ✅ 开发者文档站点 (VitePress, 17 页)
├── ✅ Python SDK (web3.py, 31 文件)
├── ✅ CLI 工具 (commander.js, 18 文件)
├── ✅ 智能合约库 (Hardhat, 11 合约)
├── ✅ 移动端钱包 (React Native + Expo, 51 文件)
├── ✅ 区块浏览器 (Analytics, Export, Contracts)
├── ✅ 钱包 (i18n 4语言, 地址簿, 144 测试)
├── ✅ SDK 测试 (JS 181 + Python 18 + Core 258 测试)
├── ✅ QVM 完整栈 (编译器 + VM + 标准库 + JIT + LSP)
└── ✅ OpenClaw 技能 (钱包管理 + 安全策略)

🔴 推理链路补全 (v2.1):
├── Phase A: 费用结算核心 (escrow, 转账, slashing 执行, fee 定价)
├── Phase B: 结果返回完善 (编码格式, IPFS, WebSocket, SDK)
├── Phase C: 任务路由加固 (流转审计, 超时重分配, 优先级队列)
├── Phase D: 用户入口增强 (专用 TX 类型, 钱包 UI, Explorer)
└── Phase E: 执行层加固 (模型管理, GPU 监控, Challenge 仲裁)

✅ Explorer 对标 Etherscan (§14) — 18/18 项全部完成:
├── ✅ Phase A: 用户系统 (注册/Watchlist/API Key/备注)
├── ✅ Phase B: 市场数据 (Token 价格/市值/排行/USD估值/Gas预言机)
├── ✅ Phase C: 合约增强 (Read as Proxy/多文件验证/Vyper/Diff)
├── ✅ Phase D: 高级过滤 (交易过滤/Approval 管理/标签分类/批量查询)
└── ✅ Phase E: 社区生态 (评论评分/DeFi 识别/地址画像/Sankey/多签检测)

🔵 qUSD 稳定币完善 (§15):
├── Phase A: 去中心化预言机 (多源聚合, TWAP, 断路器)
├── Phase B: 全局结算与紧急关停 (多签触发, 分级暂停, 赎回)
├── Phase C: PSM 锚定稳定模块 (USDC/USDT 1:1 兑换)
├── Phase D: 多资产抵押 (ETH/BTC/wstETH, CollateralManager)
└── Phase E: DAO 治理 (稳定费/抵押率参数治理, Timelock)

🟣 qUSD 隐私层 (§16):
├── Phase A: Privacy Pool (ShieldedPool, ZK proof, Merkle tree, 多面额)
├── Phase B: Stealth Address (EIP-5564, 一次性收款地址, 扫描)
└── Phase C: 合规证明 (Association Set, inclusion/exclusion proof)

待完善:
├── 钱包高级功能 (硬件钱包、WalletConnect、NFT)
└── CI/CD 流水线 (GitHub Actions 自动部署)
```

---

### 15. qUSD 稳定币完善路线图

> 目标: 将现有 CDP 模型的 qUSD 稳定币从 MVP 升级为生产就绪，增强锚定稳定性、安全性和去中心化程度

**GitHub Project**: [QFC DeFi Suite](https://github.com/orgs/qfc-network/projects/5)

**现有基础**: qUSDToken + CDPVault + PriceFeed + Liquidator (已实现，150% 抵押率，2% 稳定费)

#### Phase A: 去中心化预言机 🔴 P0

> [#50](https://github.com/qfc-network/qfc-contracts/issues/50) — 当前中心化 PriceFeed 是最大单点故障

- [ ] A1: 多数据源聚合 (Chainlink / Pyth / 自建节点)
- [ ] A2: 价格偏差检测 (>5% 偏差触发断路器)
- [ ] A3: TWAP 时间加权平均价格计算
- [ ] A4: 心跳检查 (价格过期自动暂停铸造)
- [ ] A5: 多签/DAO 紧急价格覆写
- [ ] A6: 价格历史存储 (链上最近 N 轮)

#### Phase B: 全局结算与紧急关停 🔴 P0

> [#54](https://github.com/qfc-network/qfc-contracts/issues/54) — 安全关键，黑天鹅事件保护

- [ ] B1: `EmergencyShutdown.sol` — 多签触发关停 (≥3/5)
- [ ] B2: 关停后冻结 CDP 操作，允许按比例赎回
- [ ] B3: 全局结算流程 (快照→清算价→qUSD 兑换→剩余退还)
- [ ] B4: 分级暂停 (L1 暂停铸造 / L2 暂停全部 / L3 全局结算)
- [ ] B5: L1-L2 DAO 投票恢复机制

#### Phase C: PSM 锚定稳定模块 🟡 P1

> [#52](https://github.com/qfc-network/qfc-contracts/issues/52) — 增强脱锚防御

- [ ] C1: `PSM.sol` — USDC/USDT ↔ qUSD 1:1 兑换
- [ ] C2: 可配置手续费 (tin/tout)
- [ ] C3: 单资产债务上限
- [ ] C4: 储备金审计接口
- [ ] C5: 紧急暂停开关

#### Phase D: 多资产抵押 🟡 P1

> [#51](https://github.com/qfc-network/qfc-contracts/issues/51) — 扩大铸造规模

- [ ] D1: `CollateralManager.sol` — 管理多种抵押品类型
- [ ] D2: 每种资产独立抵押率/清算阈值
- [ ] D3: Wrapped 资产支持 (wBTC, wETH)
- [ ] D4: LST 生息资产支持 (wstETH, rETH)
- [ ] D5: 全局 + 单资产债务上限
- [ ] D6: 抵押品风险参数治理接口

#### Phase E: DAO 治理 🟢 P2

> [#53](https://github.com/qfc-network/qfc-contracts/issues/53) — 去中心化参数管理

- [ ] E1: `qUSDGovernance.sol` — 参数治理合约
- [ ] E2: 可治理: 稳定费、抵押率、清算阈值、债务上限、PSM 费率
- [ ] E3: Timelock 延迟执行
- [ ] E4: 参数变更范围限制 (±20%)
- [ ] E5: 与 QFCGovernor + Treasury 集成

---

### 16. qUSD 隐私层路线图

> 目标: 为 qUSD 添加链上隐私保护，解决用户被追踪的顾虑。采用 Privacy Pools + Stealth Address 组合，在保护隐私的同时支持合规证明。

**GitHub Project**: [QFC DeFi Suite](https://github.com/orgs/qfc-network/projects/5)

**动机**: qUSD 没有 USDT 式的 blacklist/freeze 功能，但链上转账完全透明，资金流向可被任何人追踪。

#### Phase A: Privacy Pool (ShieldedPool) ✅ 已完成

> [#55](https://github.com/qfc-network/qfc-contracts/issues/55) — 核心隐私功能，断开链上资金链路

- [x] A1: `ShieldedPool.sol` + `ShieldedPoolV2.sol` — 固定面额存款/提取 (100/1K/10K/100K qUSD)
- [x] A2: `PoseidonMerkleTree.sol` — Poseidon 增量 Merkle Tree, 20 层 (~1M 存款)
- [x] A3: Nullifier 防重放机制 (链上 mapping + ZK 电路约束)
- [x] A4: ZK 电路 (Groth16, circom 2.2.2) — `withdraw.circom` 5381 constraints
  - [x] `hasher.circom` — Poseidon commitment + nullifier hash
  - [x] `merkleTree.circom` — Merkle proof checker (DualMux + HashLeftRight)
  - [x] Trusted setup: Powers of Tau (BN128 2^14) + 贡献 + beacon 最终化
  - [x] `circuits/build.sh` — 一键编译+setup 脚本
- [x] A5: `Groth16Verifier.sol` — snarkjs 自动生成的链上 ZK proof 验证器
- [x] A6: Relayer 服务 (`relayer/index.ts`) — Express.js, POST /relay + GET /jobs/:id
- [x] A7: 前端 UI (`qfc-defi/src/app/privacy/page.tsx`) — 存款/提取, 面额选择, proof 状态
- [x] A8: SDK (`qfc-defi/src/lib/shieldedPool.ts`) — note 生成/序列化, relayer 客户端
- [x] E2E 测试: 存款→Poseidon commitment→Merkle insert→离线 Groth16 proof→链上验证→提款
- [ ] 上线 checklist:
  - [ ] 正式 Trusted Setup 仪式 (多方参与)
  - [ ] Relayer 部署 + 充 gas
  - [ ] 前端集成 snarkjs WASM (浏览器端 proof 生成)
  - [ ] 审计 ZK 电路 + 合约

#### Phase B: Stealth Address (EIP-5564) ✅ 已完成

> [#56](https://github.com/qfc-network/qfc-contracts/issues/56) — 隐私收款，防止多笔收款被关联

- [x] B1: `StealthAddress.sol` — stealth meta-address 注册 (spending + viewing pubkey)
- [x] B2: `generateStealthAddress()` — 发送方生成一次性 stealth 地址
- [x] B3: `announceTransfer()` — 发布 ephemeral pubkey + viewTag 供收款方扫描
- [x] B4: `scanByViewTag()` — viewTag 过滤 + 分页查询 announcements
- [ ] B5: SDK 集成 (生成/扫描/领取) — 前端集成待完成
- [ ] B6: 钱包"隐私收款"模式 — 待完成

#### Phase C: 合规证明 (Privacy Pools 扩展) ✅ 已完成

> [#57](https://github.com/qfc-network/qfc-contracts/issues/57) — 隐私+合规的平衡点

- [x] C1: `AssociationSet.sol` — DAO 治理的地址集合注册表
  - [x] Inclusion 集合 (KYC 合规地址) + Exclusion 集合 (制裁地址)
  - [x] Curator 角色管理, Poseidon Merkle root 存储
  - [x] 激活/停用, 按类型查询
- [x] C2: `ComplianceVerifier.sol` — 三级合规验证
  - [x] None (无证明) / Basic (inclusion proof) / Full (inclusion + exclusion)
  - [x] Root 一致性验证, 防重复提交
- [x] C3: DeFi 集成接口 — `meetsComplianceLevel(nullifierHash, minLevel)`
  - [x] 协议可查询提款的合规等级, 决定是否允许参与
- [ ] C4: 扩展 ZK 电路 — 将合规证明嵌入 Groth16 电路 (目前链下验证, 待集成)

---

## 如何贡献

1. 选择一个任务
2. 在对应仓库创建 Issue
3. Fork 并创建 feature 分支
4. 提交 PR 并关联 Issue
5. Code Review 后合并

## 相关文档

- [项目总览](./00-PROJECT-OVERVIEW.md)
- [区块链设计](./01-BLOCKCHAIN-DESIGN.md)
- [共识机制](./02-CONSENSUS-MECHANISM.md)
- [钱包设计](./07-WALLET-DESIGN.md)
- [AI 计算网络设计](./13-AI-COMPUTE-NETWORK.md)
- [OpenClaw 集成](./14-OPENCLAW-INTEGRATION.md)
