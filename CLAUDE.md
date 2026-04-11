# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 仓库用途

这是 QFC 区块链项目的**设计文档仓库**，包含所有组件的技术规范和架构设计。实现代码在各自独立的仓库中。

## 文档结构

All docs are bilingual: `XX-NAME-cn.md` (Chinese) / `XX-NAME-en.md` (English).

| 编号 | 内容 |
|------|------|
| `START-HERE` | 快速开始指南，浏览器钱包实施计划 |
| `00` | 项目总览、技术栈、开发阶段 |
| `01` | 区块链核心设计（数据结构、P2P、状态、RPC） |
| `02` | PoC 共识机制详细设计 |
| `03` | 代币经济学 |
| `05` | 区块浏览器设计 |
| `07` | 浏览器钱包完整技术规范 |
| `09` | **待办事项与开发路线图** |
| `10` | QuantumScript 语言规范 |
| `11` | 链差距分析 |
| `12` | 主网验证者分配 |
| `13` | AI 算力网络设计 |
| `14` | OpenClaw 集成 |
| `15` | 竞品分析 |
| `16` | 推理证明验证 |
| `17-29` | v3.0 研究文档（智能合约、AI模型、隐私推理、zkML、DAG共识、代币经济学对比、去中心化模型存储、AI Agent、跨链预言机、DePIN、意图架构、v3.0路线图、Ethereum 2030启发） |
| `30-38` | 虚拟办公室、链游研究、部署策略、DEX设计、Agent钱包、ERC-4337等 |
| `39` | **项目现状与下一步规划**（替代09） |
| `40` | Bridge 多链扩展路线图 |
| `41` | 测试网链参考（RPC、水龙头、合约地址） |

## 项目核心创新

### PoC (Proof of Contribution) 共识
多维度贡献评分：
- 质押 30%、计算 20%、在线时间 15%
- 验证准确率 15%、网络质量 10%
- 存储 5%、信誉 5%

### 多虚拟机架构
- **QVM** - 原生高性能虚拟机 (QuantumScript)
- **EVM** - Solidity 100% 兼容
- **WASM** - Rust/AssemblyScript 支持
- **AI-VM** - AI 模型作为合约逻辑

### 性能目标
- TPS: 500,000+
- 确认时间: <0.3 秒
- Gas 费: <$0.0001

## 相关实现仓库

GitHub 组织: https://github.com/qfc-network

| 仓库 | 技术栈 | 状态 | 说明 |
|------|--------|------|------|
| `qfc-core` | Rust + libp2p | ✅ 95% | 区块链核心引擎 (258 测试, QVM+JIT+LSP) |
| `qfc-wallet` | React + TypeScript + ethers.js | ✅ 95% | 浏览器插件钱包 (i18n 4语言, 地址簿, 144 测试) |
| `qfc-explorer` | Next.js + PostgreSQL | ✅ 95% | 区块浏览器 (分析仪表板, 合约交互, 数据导出) |
| `qfc-sdk-js` | TypeScript + ethers.js | ✅ 85% | JavaScript SDK (174 测试) |
| `qfc-sdk-python` | Python + web3.py + pydantic | ✅ 85% | Python SDK |
| `qfc-cli` | Node.js + commander.js | ✅ 90% | 命令行工具 |
| `qfc-contracts` | Solidity + Hardhat + OpenZeppelin | ✅ 90% | 智能合约库 (11 合约) |
| `qfc-docs` | VitePress | ✅ 85% | 开发者文档站点 (17 页) |
| `qfc-faucet` | Next.js | ✅ 85% | 测试网水龙头 |
| `qfc-testnet` | Docker + Terraform | ✅ 90% | 测试网基础设施 (4-VPS, 监控) |
| `qfc-bridge` | Next.js + ethers.js | ✅ 90% | 跨链桥 (7 条 EVM 链) |
| `qfc-dex` | Next.js + Hardhat | ✅ 90% | DEX (Uniswap V2 风格 AMM) |
| `qfc-nft-marketplace` | Next.js | ✅ 80% | NFT 市场 |
| `qfc-defi` | Next.js | ✅ 70% | DeFi 仪表盘 |
| `qfc-agenthub` | Node.js + TypeScript | ✅ 60% | AI Agent 管理平台 |
| `qfc-games` | Vite + nginx | ✅ 80% | 游戏中心 |
| `qfc-wallet-mobile` | React Native + Expo | ✅ 85% | 移动端钱包 (iOS/Android) |

## 关键配置参考

### 网络配置
- **测试网 Chain ID**: 9000 (0x2328)
- **测试网 RPC**: `https://rpc.testnet.qfc.network`

### 线上服务
| 服务 | URL |
|------|-----|
| 水龙头 | https://faucet.testnet.qfc.network |
| 浏览器 | https://explorer.testnet.qfc.network |
| DEX | https://dex.testnet.qfc.network |
| DeFi | https://defi.testnet.qfc.network |
| NFT | https://nft.testnet.qfc.network |
| Bridge | https://bridge.testnet.qfc.network |
| Games | https://games.testnet.qfc.network |
| AgentHub | https://agenthub.testnet.qfc.network |
| Grafana | https://grafana.testnet.qfc.network |

### 钱包 EIP-1193 优先实现方法
`eth_requestAccounts`, `eth_accounts`, `eth_chainId`, `eth_sendTransaction`, `personal_sign`, `eth_getBalance`

## 使用方式

在各实现仓库开发时，引用本仓库的设计文档：

```
请根据 qfc-design/07-WALLET-DESIGN-cn.md 中的设计实现 [具体功能]
```

各实现仓库应有自己的 CLAUDE.md 文件，包含该仓库特定的构建命令和开发指南。
