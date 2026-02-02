# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 仓库用途

这是 QFC 区块链项目的**设计文档仓库**，包含所有组件的技术规范和架构设计。实现代码在各自独立的仓库中。

## 文档结构

| 文档 | 内容 |
|------|------|
| `START-HERE.md` | 快速开始指南，浏览器钱包实施计划 |
| `00-PROJECT-OVERVIEW.md` | 项目总览、技术栈、开发阶段 |
| `01-BLOCKCHAIN-DESIGN.md` | 区块链核心设计（数据结构、P2P、状态、RPC） |
| `02-CONSENSUS-MECHANISM.md` | PoC 共识机制详细设计 |
| `05-BLOCK-EXPLORER.md` | 区块浏览器设计 |
| `07-WALLET-DESIGN.md` | 浏览器钱包完整技术规范 |
| `09-TODO-ROADMAP.md` | **待办事项与开发路线图** |

待补充文档：
- `03-SMART-CONTRACT-SYSTEM.md` - 智能合约系统
- `04-NODE-OPERATION.md` - 节点运行
- `06-TESTNET-SETUP.md` - 测试网搭建

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

| 仓库 | 技术栈 | 状态 | 说明 |
|------|--------|------|------|
| `qfc-core` | Rust + libp2p | ✅ 95% | 区块链核心引擎 |
| `qfc-wallet` | React + TypeScript + ethers.js | ✅ 90% | 浏览器插件钱包 |
| `qfc-explorer` | Next.js + PostgreSQL | ✅ 85% | 区块浏览器 |
| `qfc-sdk-js` | TypeScript + ethers.js | ✅ 85% | JavaScript SDK |
| `qfc-faucet` | Next.js | ✅ 85% | 测试网水龙头 |
| `qfc-cli` | Node.js | ⚠️ 60% | 命令行工具 |

## 关键配置参考

### 网络配置
- **测试网 Chain ID**: 9000 (0x2328)
- **测试网 RPC**: `https://rpc.testnet.qfc.network`
- **水龙头**: `https://faucet.testnet.qfc.network`

### 钱包 EIP-1193 优先实现方法
`eth_requestAccounts`, `eth_accounts`, `eth_chainId`, `eth_sendTransaction`, `personal_sign`, `eth_getBalance`

## 使用方式

在各实现仓库开发时，引用本仓库的设计文档：

```
请根据 qfc-design/07-WALLET-DESIGN.md 中的设计实现 [具体功能]
```

各实现仓库应有自己的 CLAUDE.md 文件，包含该仓库特定的构建命令和开发指南。
