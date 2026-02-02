# QFC Blockchain - 待办事项与路线图

> 最后更新: 2026-02-02

## 项目现状总览

| 项目 | 仓库 | 技术栈 | 状态 | 完成度 |
|------|------|--------|------|--------|
| 核心引擎 | `qfc-core` | Rust + libp2p | ✅ 生产就绪 | 95% |
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

### 5. ~~CLI 工具增强~~ ✅ 已完成

**目标**: 提供功能完整的命令行工具

**仓库**: `qfc-cli/` - https://github.com/lai3d/qfc-cli

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

**仓库**: `qfc-wallet-mobile/` - https://github.com/lai3d/qfc-wallet-mobile

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

**仓库**: `qfc-contracts/` - https://github.com/lai3d/qfc-contracts

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

### 10. QVM 虚拟机 (进行中)

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
  - [x] 24 个单元测试通过

**待完成内容**:

- [ ] JIT 编译 (可选优化)
- [ ] 标准库实现
- [ ] 与 EVM 互操作实现
- [ ] 开发工具 (LSP, 格式化)

**完成时间**: 2026-02-02 (语言设计 + 编译器前端 + 执行引擎)

**预估剩余工作量**: 2-4 周 (标准库 + 互操作)

---

## 优先级排序建议

```
已完成:
├── ✅ 测试网部署基础设施 (Docker/K8s/Terraform/监控)
├── ✅ 开发者文档站点 (VitePress, 17 页)
├── ✅ Python SDK (web3.py, 31 文件)
├── ✅ CLI 工具增强 (commander.js, 18 文件)
├── ✅ 智能合约示例库 (Hardhat, 11 合约)
├── ✅ 移动端钱包 (React Native + Expo, 51 文件)
├── ✅ 区块浏览器增强 (Analytics, Export, Contracts, Rate Limiting)
└── ✅ 钱包多语言+地址簿 (i18n 4语言, Address Book)

第 1 阶段 (当前):
├── SDK 单元测试
├── 钱包高级功能 (硬件钱包、WalletConnect、NFT)
└── QVM 标准库 + EVM 互操作

长期:
└── QVM JIT 编译优化
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
