# QFC Blockchain - 待办事项与路线图

> 最后更新: 2026-03-05

## 项目现状总览

| 项目 | 仓库 | 技术栈 | 状态 | 完成度 |
|------|------|--------|------|--------|
| 核心引擎 | `qfc-core` | Rust + libp2p | ✅ 生产就绪 | 95% |
| AI 推理引擎 | `qfc-core/qfc-inference` | Rust + candle | ✅ v2.0 核心完成 | 90% |
| AI 任务协调 | `qfc-core/qfc-ai-coordinator` | Rust | ✅ v2.0 核心完成 | 85% |
| 独立矿工 | `qfc-core/qfc-miner` | Rust + clap | ✅ v2.0 核心完成 | 80% |
| 浏览器钱包 | `qfc-wallet` | React + TypeScript | ✅ 功能完整 | 95% |
| 区块浏览器 | `qfc-explorer` | Next.js + PostgreSQL | ✅ 功能完整 | 95% |
| JavaScript SDK | `qfc-sdk-js` | TypeScript + ethers.js | ✅ 已完成 | 85% |
| 测试网水龙头 | `qfc-faucet` | Next.js | ✅ 可用 | 85% |
| **测试网基础设施** | `qfc-testnet` | Docker + K8s + Terraform | ✅ 已完成 | 90% |
| **开发者文档站点** | `qfc-docs` | VitePress | ✅ 已完成 | 85% |
| **Python SDK** | `qfc-sdk-python` | Python + web3.py | ✅ 已完成 | 85% |
| **CLI 工具** | `qfc-cli` | Node.js + commander | ✅ 已完成 | 90% |
| **智能合约库** | `qfc-contracts` | Solidity + Hardhat | ✅ 已完成 | 90% |
| **移动端钱包** | `qfc-wallet-mobile` | React Native + Expo | ✅ 已完成 | 85% |

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

**测试统计**: 8 测试文件, 174 测试用例全部通过

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

### 11. v2.0 AI 计算网络 🚧 进行中

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

- [x] CLI (clap): `--validator-rpc`, `--wallet`, `--backend auto|cuda|metal|cpu`, `--model-dir`, `--max-memory`
- [x] 硬件检测 + 基准测试
- [x] `InferenceWorker` 推理循环 (10s epoch)
- [x] 证明提交脚手架 (RPC)

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
- [ ] CUDA 后端: `candle-core` CUDA feature (待 GPU 测试环境)

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

#### Phase 8: 生态集成 ⬜ 待开始

- [ ] OpenClaw 集成 (按 Design Doc 14)
- [ ] 模型注册表链上治理 (验证者投票 >2/3)
- [ ] 推理 API 对外开放 (付费调用)
- [ ] Explorer 展示推理统计
- [ ] SDK 更新 (JS/Python 支持推理相关 RPC)

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

### 9. ~~区块浏览器增强~~ ✅ 已完成

**仓库**: `qfc-explorer/` (现有)

**完成内容**:

- [x] 高级分析仪表板 (/analytics)
  - [x] TPS 图表 (历史趋势)
  - [x] Gas 使用趋势
  - [x] 区块时间图表
  - [x] 验证者统计表格
- [x] 数据导出 (CSV/JSON)
  - [x] 支持 TPS、Gas、区块时间、验证者数据导出
  - [x] 支持区块和交易列表导出
- [x] 合约交互界面 (Read/Write)
  - [x] /contract/[address] 页面
  - [x] ERC-20 标准函数支持
  - [x] 自定义 ABI 输入
  - [x] 合约列表页面 (/contracts)
- [x] 代币持有者排行 (已在 /token/[address] 实现)
- [x] API 速率限制仪表板
  - [x] 内存速率限制 (100 req/min per IP)
  - [x] Admin 页面实时监控
  - [x] Top IPs 和 Recent Requests 显示

**完成时间**: 2026-02-02

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

## 优先级排序建议

```
v2.0 AI 计算网络 (当前重点):
├── ✅ Phase 1: 推理运行时 (qfc-inference, 3 后端)
├── ✅ Phase 2: 任务协调 (qfc-ai-coordinator)
├── ✅ Phase 3: 现有 crate 适配 (types/pow/consensus/node/rpc)
├── ✅ Phase 4: 独立矿工程序 (qfc-miner)
├── ✅ Phase 5: candle 模型集成 (BERT embedding, Metal)
├── ✅ Phase 6: 端到端集成 (提交→广播→验证→抽检→惩罚)
├── ✅ Phase 7: 测试网部署 (Docker + 混合模式 + 仪表板 + 分阶段脚本)
└── ⬜ Phase 8: 生态集成 (OpenClaw, 治理, API)

已完成基础设施:
├── ✅ 测试网部署 (Docker/K8s/Terraform/监控)
├── ✅ 开发者文档站点 (VitePress, 17 页)
├── ✅ Python SDK (web3.py, 31 文件)
├── ✅ CLI 工具 (commander.js, 18 文件)
├── ✅ 智能合约库 (Hardhat, 11 合约)
├── ✅ 移动端钱包 (React Native + Expo, 51 文件)
├── ✅ 区块浏览器 (Analytics, Export, Contracts)
├── ✅ 钱包 (i18n 4语言, 地址簿, 144 测试)
├── ✅ SDK 测试 (JS 174 + Core 258 测试)
└── ✅ QVM 完整栈 (编译器 + VM + 标准库 + JIT + LSP)

待完善:
├── 钱包高级功能 (硬件钱包、WalletConnect、NFT)
└── CI/CD 流水线 (GitHub Actions 自动部署)
```

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
