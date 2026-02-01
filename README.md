# QFC Blockchain 项目文档

这是 QFC 区块链项目的完整设计文档集合。

## 📚 文档列表

### 🚀 快速开始
- **[START-HERE.md](START-HERE.md)** - 给 Claude Code 的快速开始指南
  - 如何开始开发
  - 第一条指令示例
  - 分步实施计划

### 📋 核心文档
1. **[00-PROJECT-OVERVIEW.md](00-PROJECT-OVERVIEW.md)** - 项目总览
   - 项目目标
   - 核心创新点
   - 技术栈
   - 项目阶段
   - 代码仓库结构

2. **[01-BLOCKCHAIN-DESIGN.md](01-BLOCKCHAIN-DESIGN.md)** - 区块链核心设计
   - 数据结构（Block、Transaction、Account）
   - P2P 网络层（libp2p）
   - 状态管理（Merkle Patricia Trie）
   - 存储层（RocksDB）
   - RPC API
   - 交易池

3. **[02-CONSENSUS-MECHANISM.md](02-CONSENSUS-MECHANISM.md)** - PoC 共识机制
   - 贡献评分算法
   - 区块生产流程
   - 激励机制
   - 惩罚机制（Slashing）
   - 安全分析

4. **[07-WALLET-DESIGN.md](07-WALLET-DESIGN.md)** - 钱包设计
   - 浏览器插件钱包（完整实现）
   - 移动端钱包（规划）
   - 安全要求
   - 测试要求

## 📦 文档统计

- 总文档数: 5
- 总行数: ~3,400
- 总字数: ~40,000

## 🎯 使用方法

### 方法 1: 本地使用

```bash
# 下载所有文件到你的项目目录
qfc-blockchain/
├── docs/
│   ├── 00-PROJECT-OVERVIEW.md
│   ├── 02-CONSENSUS-MECHANISM.md
│   ├── 07-WALLET-DESIGN.md
│   └── START-HERE.md
```

### 方法 2: Claude Projects

1. 在 Claude.ai 创建新 Project
2. 上传所有 .md 文件到 Project Knowledge
3. 设置 Project Instructions:

```
你是 QFC 区块链项目的核心开发者。

项目文档在 Knowledge 中，包括：
- START-HERE.md: 快速开始指南
- 00-PROJECT-OVERVIEW.md: 项目总览
- 02-CONSENSUS-MECHANISM.md: 共识机制
- 07-WALLET-DESIGN.md: 钱包设计

开发原则：
- 安全第一
- 代码质量高
- 详细注释
- 完整测试

在实现功能前，请先阅读相关设计文档。
```

### 方法 3: 直接给 Claude Code 指令

```
我要开始开发 QFC 区块链项目的浏览器钱包。

请阅读以下文档：
1. docs/START-HERE.md - 快速开始
2. docs/07-WALLET-DESIGN.md - 钱包设计

然后按照 START-HERE.md 中的步骤开始实现。
```

## 📝 待补充文档

以下文档在项目推进中会逐步添加：

- [ ] 03-SMART-CONTRACT-SYSTEM.md - 智能合约系统
- [ ] 04-NODE-OPERATION.md - 节点运行
- [ ] 05-BLOCK-EXPLORER.md - 区块浏览器
- [ ] 06-TESTNET-SETUP.md - 测试网搭建
- [ ] 08-IMPLEMENTATION-PLAN.md - 详细实施计划

## 🔗 相关资源

### 技术参考
- [Chrome Extension Manifest V3](https://developer.chrome.com/docs/extensions/mv3/)
- [EIP-1193: Ethereum Provider](https://eips.ethereum.org/EIPS/eip-1193)
- [ethers.js v6](https://docs.ethers.org/v6/)
- [React 18](https://react.dev/)
- [TypeScript](https://www.typescriptlang.org/)

### 类似项目
- [MetaMask](https://github.com/MetaMask/metamask-extension)
- [Ethereum](https://ethereum.org/)
- [Solana](https://solana.com/)

## 💡 文档更新

这些文档会随着项目推进持续更新。

**当前版本**: 1.0.0  
**最后更新**: 2026-02-01  
**维护者**: QFC Core Team

## 📧 反馈

如果你在使用这些文档时遇到问题，或者有改进建议，请：
1. 创建 GitHub Issue
2. 在 Discord 讨论
3. 提交 Pull Request

---

**开始你的开发之旅吧！** 🚀

建议从 **[START-HERE.md](START-HERE.md)** 开始阅读。
