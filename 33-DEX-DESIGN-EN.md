# 33. QFC DEX — On-Chain Decentralized Exchange

**English** | [中文](./33-DEX-DESIGN-CN.md)

> QFC native AMM DEX, supporting QFC/ERC-20 token swaps + liquidity mining.

## Overview

An AMM DEX based on the Uniswap V2 constant-product formula (x × y = k), deployed on the QFC testnet. Supports two-way swaps between the QFC native token and QRC-20 tokens (TTK, QDOGE, etc.).

**Core positioning:** The first DeFi infrastructure in the QFC ecosystem, and the trading hub for the chain-game economy.

## Contract Architecture

```
DEXRouter.sol
  └── DEXFactory.sol
        └── DEXPair.sol (x × y = k, LP Token)
```

### Core Contracts

**DEXPair.sol** — Constant-product AMM, 0.3% fee, LP Token
**DEXFactory.sol** — Creates/manages trading pairs
**DEXRouter.sol** — User entry point: swap/addLiquidity/removeLiquidity

## Initial Trading Pairs

| Pair | Notes |
|--------|------|
| QFC / TTK | native + `0xff9427b41587206cea2b156a9967fb4d4dbf99d0` |
| QFC / QDOGE | native + `0xb7938ce567a164a216fa2d0aa885e32608b2e621` |
| TTK / QDOGE | Two QRC-20s |

## Frontend Pages

- **Swap** — Main token-swap page
- **Liquidity** — Add/remove liquidity, view LP tokens
- **Pools** — All trading pairs, TVL / 24h volume / APR
- **My Positions** — My LP positions + fees earned

**Tech:** Next.js + TypeScript + Tailwind CSS (reuses the qfc-explorer stack)

## Fees

- Swap: 0.3% (all to liquidity providers)
- Protocol fee: none for now (Phase 2: consider 0.05% to the DAO)

## File Structure

```
qfc-dex/
├── contracts/
│   ├── DEXFactory.sol
│   ├── DEXPair.sol
│   ├── DEXRouter.sol
│   └── interfaces/
├── scripts/
│   ├── deploy.ts
│   └── seed.ts            # Create initial pairs + seed liquidity
├── test/
├── frontend/
│   ├── src/pages/         # swap / liquidity / pools / positions
│   ├── src/components/
│   ├── src/hooks/
│   └── src/lib/           # Contract ABIs + AMM math
├── hardhat.config.ts
└── README.md
```

## Deployment Plan

```
Step 1: Contract development + unit tests
Step 2: Deploy Factory + Router to the QFC testnet
Step 3: Create initial trading pairs + seed liquidity
Step 4: Connect frontend to testnet contracts
Step 5: Integrate into qfc-explorer (/dex route)
```

## Existing Resources

| Resource | Location |
|------|------|
| TTK | `0xff9427b41587206cea2b156a9967fb4d4dbf99d0` |
| QDOGE | `0xb7938ce567a164a216fa2d0aa885e32608b2e621` |
| QFC RPC | `https://rpc.qfc.network` |
| Hardhat config | qfc-contracts |
| Wallet connection | qfc-wallet |

## Phase 2

- Liquidity mining (QFC rewards)
- AI market maker (QFC AI inference for pricing optimization)
- Cross-chain onboarding of ETH/USDC
- Limit orders (off-chain signing + on-chain settlement)

---

*👤 Designed by Larry Lai（来拉里）, Founder @ QFC Network*
*🤖 Written by Aria Tanaka（田中爱莉）, QA Engineer @ QFC Network — via OpenClaw*
