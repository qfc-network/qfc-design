# 测试网链参考

[English](./41-TESTNET-CHAINS-REFERENCE-EN.md) | **中文**

> ⚠️ 2026-07-05 测试网 genesis 重置后，本文档列出的合约地址已全部失效；合约重部署（Phase 0.5）完成后将统一更新。

> 最后更新：2026-04-11

QFC Bridge 生态所使用的全部测试网链的快速参考。

---

## 1. QFC 测试网

| 字段 | 值 |
|-------|-------|
| 网络名称 | QFC Testnet |
| RPC URL | `https://rpc.testnet.qfc.network` |
| Chain ID | `9000` |
| 代币符号 | `QFC` |
| 区块浏览器 | `https://explorer.testnet.qfc.network` |
| 水龙头 | `https://faucet.testnet.qfc.network` |
| Bridge 合约 | `0x47ea0e0cdc65cc1f4f7b21f922219139f23e1a27` |

## 2. Ethereum Sepolia

| 字段 | 值 |
|-------|-------|
| 网络名称 | Sepolia |
| RPC URL | `https://rpc.sepolia.org` |
| Chain ID | `11155111` |
| 代币符号 | `ETH` |
| 区块浏览器 | `https://sepolia.etherscan.io` |
| 水龙头 | https://www.alchemy.com/faucets/ethereum-sepolia |
| | https://faucets.chain.link/sepolia |
| | https://faucet.quicknode.com/ethereum/sepolia |
| Bridge 合约 | `0x8E6d4cD14EB6eEFeB040a6ecE53d11dC9ef8137C` |

## 3. BSC 测试网

| 字段 | 值 |
|-------|-------|
| 网络名称 | BSC Testnet |
| RPC URL | `https://data-seed-prebsc-1-s1.binance.org:8545` |
| Chain ID | `97` |
| 代币符号 | `tBNB` |
| 区块浏览器 | `https://testnet.bscscan.com` |
| 水龙头 | https://www.bnbchain.org/en/testnet-faucet |
| Bridge 合约 | `0x51Ef5567Afd34E1a178757C5Cf68B7132f861Fe8` |

## 4. Arbitrum Sepolia

| 字段 | 值 |
|-------|-------|
| 网络名称 | Arbitrum Sepolia |
| RPC URL | `https://sepolia-rollup.arbitrum.io/rpc` |
| Chain ID | `421614` |
| 代币符号 | `ETH` |
| 区块浏览器 | `https://sepolia.arbiscan.io` |
| 水龙头 | https://faucet.chainstack.com/arbitrum-sepolia-faucet |
| | https://www.l2faucet.com/arbitrum |
| | https://faucets.chain.link/arbitrum-sepolia |
| Bridge 合约 | `0x8E6d4cD14EB6eEFeB040a6ecE53d11dC9ef8137C` |

## 5. Polygon Amoy

| 字段 | 值 |
|-------|-------|
| 网络名称 | Polygon Amoy |
| RPC URL | `https://rpc-amoy.polygon.technology` |
| Chain ID | `80002` |
| 代币符号 | `POL` |
| 区块浏览器 | `https://amoy.polygonscan.com` |
| 水龙头 | https://faucet.polygon.technology |
| | https://www.alchemy.com/faucets/polygon-amoy |
| Bridge 合约 | `0x8E6d4cD14EB6eEFeB040a6ecE53d11dC9ef8137C` |

## 6. Base Sepolia

| 字段 | 值 |
|-------|-------|
| 网络名称 | Base Sepolia |
| RPC URL | `https://sepolia.base.org` |
| Chain ID | `84532` |
| 代币符号 | `ETH` |
| 区块浏览器 | `https://sepolia.basescan.org` |
| 水龙头 | https://www.alchemy.com/faucets/base-sepolia |
| | https://faucet.quicknode.com/base/sepolia |
| Bridge 合约 | `0x8E6d4cD14EB6eEFeB040a6ecE53d11dC9ef8137C` |

## 7. Optimism Sepolia

| 字段 | 值 |
|-------|-------|
| 网络名称 | Optimism Sepolia |
| RPC URL | `https://sepolia.optimism.io` |
| Chain ID | `11155420` |
| 代币符号 | `ETH` |
| 区块浏览器 | `https://sepolia-optimistic.etherscan.io` |
| 水龙头 | https://www.alchemy.com/faucets/optimism-sepolia |
| | https://faucet.quicknode.com/optimism/sepolia |
| | https://faucets.chain.link/optimism-sepolia |
| Bridge 合约 | *尚未部署* |

---

## 部署者钱包

| 字段 | 值 |
|-------|-------|
| 地址 | `0x46e95879eD225038760617c33362da692412a8AC` |
| 用途 | 合约部署 + relayer 运行操作 |

---

## 快速添加到 MetaMask

访问 https://chainlist.org 并按 Chain ID 搜索，或使用上文各节中的 RPC URL、Chain ID、代币符号和区块浏览器 URL，通过 设置 → 网络 → 添加网络 手动添加。

---

## Bridge 部署命令

在新的 EVM 链上部署 BridgeLock：

```bash
cd qfc-contracts
npx hardhat run scripts/deploy-bridge-lock.ts --network <networkName>
```

`hardhat.config.ts` 中已配置的网络名称：
`qfc_testnet`、`sepolia`、`bscTestnet`、`arbitrumSepolia`、`polygonAmoy`、`baseSepolia`
