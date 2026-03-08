# QFC Blockchain Project Documentation

This is the complete collection of design documents for the QFC blockchain project.

## 📚 Document List

### 🚀 Quick Start
- **[START-HERE.md](START-HERE.md)** - Quick start guide for Claude Code
  - How to begin development
  - First command examples
  - Step-by-step implementation plan

### 📋 Core Documents
1. **[00-PROJECT-OVERVIEW.md](00-PROJECT-OVERVIEW.md)** - Project Overview
   - Project goals
   - Core innovations
   - Technology stack
   - Project phases
   - Repository structure

2. **[01-BLOCKCHAIN-DESIGN.md](01-BLOCKCHAIN-DESIGN.md)** - Blockchain Core Design
   - Data structures (Block, Transaction, Account)
   - P2P network layer (libp2p)
   - State management (Merkle Patricia Trie)
   - Storage layer (RocksDB)
   - RPC API
   - Transaction pool

3. **[02-CONSENSUS-MECHANISM.md](02-CONSENSUS-MECHANISM.md)** - PoC Consensus Mechanism
   - Contribution scoring algorithm
   - Block production workflow
   - Incentive mechanism
   - Slashing mechanism
   - Security analysis

4. **[07-WALLET-DESIGN.md](07-WALLET-DESIGN.md)** - Wallet Design
   - Browser extension wallet (full implementation)
   - Mobile wallet (planned)
   - Security requirements
   - Testing requirements

## 📦 Documentation Statistics

- Total documents: 5
- Total lines: ~3,400
- Total words: ~40,000

## 🎯 How to Use

### Method 1: Local Usage

```bash
# Download all files to your project directory
qfc-blockchain/
├── docs/
│   ├── 00-PROJECT-OVERVIEW.md
│   ├── 02-CONSENSUS-MECHANISM.md
│   ├── 07-WALLET-DESIGN.md
│   └── START-HERE.md
```

### Method 2: Claude Projects

1. Create a new Project on Claude.ai
2. Upload all .md files to Project Knowledge
3. Set Project Instructions:

```
You are a core developer of the QFC blockchain project.

Project documents are in Knowledge, including:
- START-HERE.md: Quick start guide
- 00-PROJECT-OVERVIEW.md: Project overview
- 02-CONSENSUS-MECHANISM.md: Consensus mechanism
- 07-WALLET-DESIGN.md: Wallet design

Development principles:
- Security first
- High code quality
- Detailed comments
- Comprehensive testing

Before implementing any feature, please read the relevant design documents.
```

### Method 3: Direct Instructions to Claude Code

```
I want to start developing the browser wallet for the QFC blockchain project.

Please read the following documents:
1. docs/START-HERE.md - Quick start
2. docs/07-WALLET-DESIGN.md - Wallet design

Then follow the steps in START-HERE.md to begin implementation.
```

## 📝 Documents To Be Added

The following documents will be added progressively as the project advances:

- [ ] 03-SMART-CONTRACT-SYSTEM.md - Smart contract system
- [ ] 04-NODE-OPERATION.md - Node operation
- [ ] 05-BLOCK-EXPLORER.md - Block explorer
- [ ] 06-TESTNET-SETUP.md - Testnet setup
- [ ] 08-IMPLEMENTATION-PLAN.md - Detailed implementation plan

## 🔗 Related Resources

### Technical References
- [Chrome Extension Manifest V3](https://developer.chrome.com/docs/extensions/mv3/)
- [EIP-1193: Ethereum Provider](https://eips.ethereum.org/EIPS/eip-1193)
- [ethers.js v6](https://docs.ethers.org/v6/)
- [React 18](https://react.dev/)
- [TypeScript](https://www.typescriptlang.org/)

### Similar Projects
- [MetaMask](https://github.com/MetaMask/metamask-extension)
- [Ethereum](https://ethereum.org/)
- [Solana](https://solana.com/)

## 💡 Documentation Updates

These documents will be continuously updated as the project progresses.

**Current version**: 1.0.0
**Last updated**: 2026-02-01
**Maintainer**: QFC Core Team

## 📧 Feedback

If you encounter any issues while using these documents, or have suggestions for improvement, please:
1. Create a GitHub Issue
2. Discuss on Discord
3. Submit a Pull Request

---

**Start your development journey!** 🚀

We recommend starting with **[START-HERE.md](START-HERE.md)**.
