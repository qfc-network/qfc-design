# QFC Blockchain - 待办事项与路线图

> 最后更新: 2026-02-02

## 项目现状总览

| 项目 | 仓库 | 技术栈 | 状态 | 完成度 |
|------|------|--------|------|--------|
| 核心引擎 | `qfc-core` | Rust + libp2p | ✅ 生产就绪 | 95% |
| 浏览器钱包 | `qfc-wallet` | React + TypeScript | ✅ 功能完整 | 90% |
| 区块浏览器 | `qfc-explorer` | Next.js + PostgreSQL | ✅ 功能完整 | 85% |
| JavaScript SDK | `qfc-sdk-js` | TypeScript + ethers.js | ✅ 已完成 | 85% |
| 测试网水龙头 | `qfc-faucet` | Next.js | ✅ 可用 | 85% |
| **测试网基础设施** | `qfc-testnet` | Docker + K8s + Terraform | ✅ 已完成 | 90% |
| **开发者文档站点** | `qfc-docs` | VitePress | ✅ 已完成 | 85% |
| **Python SDK** | `qfc-sdk-python` | Python + web3.py | ✅ 已完成 | 85% |
| CLI 工具 | `qfc-cli` | Node.js | ⚠️ 基础实现 | 60% |

---

## 高优先级任务

### 1. ~~测试网部署基础设施~~ ✅ 已完成

**目标**: 搭建可公开访问的测试网环境

**仓库**: `qfc-testnet/` - https://github.com/lai3d/qfc-testnet

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

#### qfc-sdk-js
- [ ] Provider 测试
  - [ ] RPC 方法调用测试
  - [ ] 错误处理测试
  - [ ] 网络切换测试
- [ ] Wallet 测试
  - [ ] 签名测试
  - [ ] 质押操作测试
- [ ] Utils 测试
  - [ ] 单位转换测试
  - [ ] 验证函数测试
  - [ ] 编码函数测试
- [ ] Contract 测试
  - [ ] ERC-20 交互测试
  - [ ] Multicall 测试

#### qfc-wallet
- [ ] 加密存储测试
- [ ] Provider 注入测试
- [ ] 交易签名测试
- [ ] UI 组件测试

#### qfc-core
- [ ] 共识算法测试扩展
- [ ] 跨分片交易测试
- [ ] 压力测试 / 基准测试
- [ ] 网络分区测试

**预估工作量**: 2 周

---

### 3. ~~开发者文档站点~~ ✅ 已完成

**目标**: 提供完整的开发者文档，方便第三方集成

**仓库**: `qfc-docs/` - https://github.com/lai3d/qfc-docs

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

## 中优先级任务

### 4. ~~Python SDK~~ ✅ 已完成

**目标**: 为 Python 开发者提供 SDK

**仓库**: `qfc-sdk-python/` - https://github.com/lai3d/qfc-sdk-python

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

### 5. CLI 工具增强

**目标**: 提供功能完整的命令行工具

**仓库**: `qfc-cli/` (现有)

**技术栈**: 建议迁移到 Rust (与 qfc-core 统一) 或保持 Node.js

**功能规划**:

```bash
# 账户管理
qfc account create              # 创建新账户
qfc account import              # 导入私钥/助记词
qfc account list                # 列出账户
qfc account balance <address>   # 查询余额

# 交易
qfc tx send --to <addr> --value <amount>
qfc tx status <hash>
qfc tx history <address>

# 质押
qfc stake deposit <amount>
qfc stake withdraw <amount>
qfc stake delegate <validator> <amount>
qfc stake rewards

# 合约
qfc contract deploy <file> [args...]
qfc contract call <address> <method> [args...]
qfc contract verify <address> <source>

# 验证者
qfc validator register --commission <rate>
qfc validator info <address>
qfc validator list

# 网络
qfc network info
qfc network peers
qfc network switch <testnet|mainnet|local>

# 配置
qfc config set rpc-url <url>
qfc config set default-account <address>
```

**任务清单**:

- [ ] 命令框架重构 (commander.js 或 clap)
- [ ] 账户管理命令
- [ ] 交易命令
- [ ] 质押命令
- [ ] 合约部署/交互命令
- [ ] 配置管理
- [ ] 输出格式化 (JSON/Table)
- [ ] Shell 自动补全

**预估工作量**: 1-2 周

---

### 6. 移动端钱包

**目标**: iOS 和 Android 原生钱包应用

**仓库**: `qfc-wallet-mobile/` (新建)

**技术栈**: React Native + Expo

**功能规划**:

- [ ] 钱包创建/导入
- [ ] 生物识别 (Face ID / 指纹)
- [ ] 发送/接收 QFC
- [ ] 交易历史
- [ ] 代币管理
- [ ] 质押功能
- [ ] WalletConnect v2 支持
- [ ] 推送通知
- [ ] 深度链接 (qfc://)

**预估工作量**: 4-6 周

---

### 7. 智能合约示例库

**目标**: 提供常用合约模板和示例

**仓库**: `qfc-contracts/` (新建)

**目录结构**:

```
qfc-contracts/
├── contracts/
│   ├── tokens/
│   │   ├── QFCToken.sol        # ERC-20 示例
│   │   ├── QFCNFT.sol          # ERC-721 示例
│   │   └── QFCMultiToken.sol   # ERC-1155 示例
│   ├── staking/
│   │   ├── StakingPool.sol
│   │   └── RewardDistributor.sol
│   ├── governance/
│   │   ├── Governor.sol
│   │   ├── Timelock.sol
│   │   └── Treasury.sol
│   ├── defi/
│   │   ├── SimpleSwap.sol      # 简单 DEX
│   │   ├── LendingPool.sol
│   │   └── Vault.sol
│   └── utils/
│       ├── Multicall.sol
│       └── Create2Factory.sol
├── scripts/
│   ├── deploy.ts
│   └── verify.ts
├── test/
└── hardhat.config.ts
```

**任务清单**:

- [ ] Hardhat 项目配置
- [ ] ERC-20/721/1155 模板
- [ ] 质押合约
- [ ] 治理合约 (基于 OpenZeppelin)
- [ ] 简单 DEX 示例
- [ ] 部署脚本
- [ ] 测试用例
- [ ] 文档

**预估工作量**: 2 周

---

## 低优先级任务

### 8. 钱包增强功能

**仓库**: `qfc-wallet/` (现有)

- [ ] 硬件钱包支持
  - [ ] Ledger 集成
  - [ ] Trezor 集成
- [ ] 多语言支持 (i18n)
  - [ ] 英文
  - [ ] 中文
  - [ ] 日文
  - [ ] 韩文
- [ ] WalletConnect v2
- [ ] 交易加速/取消
- [ ] 地址簿
- [ ] NFT 展示

**预估工作量**: 2-3 周

---

### 9. 区块浏览器增强

**仓库**: `qfc-explorer/` (现有)

- [ ] 高级分析仪表板
  - [ ] TPS 图表
  - [ ] Gas 使用趋势
  - [ ] 验证者统计
- [ ] 数据导出 (CSV/JSON)
- [ ] 合约源码验证
- [ ] 合约交互界面 (Read/Write)
- [ ] 代币持有者排行
- [ ] API 速率限制仪表板

**预估工作量**: 1-2 周

---

### 10. QVM 虚拟机 (长期)

**目标**: 实现设计文档中规划的原生虚拟机

**仓库**: `qfc-core/vm/qvm/` (现有结构)

**说明**: 目前只实现了 EVM 兼容层，QVM 和 QuantumScript 语言尚未开发

**任务清单**:

- [ ] QuantumScript 语言设计
- [ ] 编译器开发 (LLVM 后端)
- [ ] QVM 执行引擎
- [ ] 标准库
- [ ] 与 EVM 互操作
- [ ] 开发工具 (LSP, 格式化)

**预估工作量**: 3-6 个月

---

## 优先级排序建议

```
已完成:
├── ✅ 测试网部署基础设施 (Docker/K8s/Terraform/监控)
├── ✅ 开发者文档站点 (VitePress, 17 页)
└── ✅ Python SDK (web3.py, 31 文件)

第 1 阶段 (当前):
└── SDK 单元测试

第 2 阶段 (2-3 周):
├── CLI 工具增强
└── 智能合约示例库

第 3 阶段 (4+ 周):
├── 移动端钱包
└── 钱包/浏览器增强功能

长期:
└── QVM 虚拟机
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
