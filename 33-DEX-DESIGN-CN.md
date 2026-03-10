# 33. QFC DEX — 链上去中心化交易所

> QFC 原生 AMM DEX，支持 QFC/ERC-20 代币互换 + 流动性挖矿。

## 概述

基于 Uniswap V2 恒积公式（x × y = k）的 AMM DEX，部署在 QFC 测试网。支持 QFC 原生代币与 QRC-20 代币（TTK、QDOGE 等）的双向兑换。

**核心定位：** QFC 生态的第一个 DeFi 基础设施，也是链游经济系统的交易枢纽。

## 合约架构

```
DEXRouter.sol
  └── DEXFactory.sol
        └── DEXPair.sol (x × y = k，LP Token)
```

### 核心合约

**DEXPair.sol** — 恒积 AMM，0.3% 手续费，LP Token
**DEXFactory.sol** — 创建/管理交易对
**DEXRouter.sol** — 用户入口，swap/addLiquidity/removeLiquidity

## 初始交易对

| 交易对 | 说明 |
|--------|------|
| QFC / TTK | native + `0xff9427b41587206cea2b156a9967fb4d4dbf99d0` |
| QFC / QDOGE | native + `0xb7938ce567a164a216fa2d0aa885e32608b2e621` |
| TTK / QDOGE | 两个 QRC-20 |

## 前端页面

- **Swap** — 代币兑换主页
- **Liquidity** — 添加/移除流动性，查看 LP token
- **Pools** — 所有交易对，TVL/24h 量/APR
- **My Positions** — 我的 LP 仓位 + 已赚手续费

**Tech:** Next.js + TypeScript + Tailwind CSS（复用 qfc-explorer 技术栈）

## 手续费

- Swap: 0.3%（全归流动性提供者）
- 协议费: 暂无（Phase 2 考虑 0.05% 归 DAO）

## 文件结构

```
qfc-dex/
├── contracts/
│   ├── DEXFactory.sol
│   ├── DEXPair.sol
│   ├── DEXRouter.sol
│   └── interfaces/
├── scripts/
│   ├── deploy.ts
│   └── seed.ts            # 创建初始对 + 注入流动性
├── test/
├── frontend/
│   ├── src/pages/         # swap / liquidity / pools / positions
│   ├── src/components/
│   ├── src/hooks/
│   └── src/lib/           # 合约 ABI + AMM math
├── hardhat.config.ts
└── README.md
```

## 部署计划

```
Step 1: 合约开发 + 单元测试
Step 2: 部署 Factory + Router 到 QFC 测试网
Step 3: 创建初始交易对 + 注入流动性
Step 4: 前端接入测试网合约
Step 5: 集成到 qfc-explorer（/dex 路由）
```

## 已有资源

| 资源 | 位置 |
|------|------|
| TTK | `0xff9427b41587206cea2b156a9967fb4d4dbf99d0` |
| QDOGE | `0xb7938ce567a164a216fa2d0aa885e32608b2e621` |
| QFC RPC | `https://rpc.qfc.network` |
| Hardhat 配置 | qfc-contracts |
| 钱包连接 | qfc-wallet |

## Phase 2

- 流动性挖矿（QFC 奖励）
- AI 做市商（QFC AI 推理优化定价）
- 跨链引入 ETH/USDC
- 限价单（链下签名 + 链上结算）

---

*👤 Designed by Larry Lai（来拉里）, Founder @ QFC Network*
*🤖 Written by Aria Tanaka（田中爱莉）, QA Engineer @ QFC Network — via OpenClaw*
