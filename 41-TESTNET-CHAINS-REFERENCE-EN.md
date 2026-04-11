# Testnet Chains Reference

> Last updated: 2026-04-11

Quick reference for all testnet chains used in the QFC Bridge ecosystem.

---

## 1. QFC Testnet

| Field | Value |
|-------|-------|
| Network Name | QFC Testnet |
| RPC URL | `https://rpc.testnet.qfc.network` |
| Chain ID | `9000` |
| Symbol | `QFC` |
| Explorer | `https://explorer.testnet.qfc.network` |
| Faucet | `https://faucet.testnet.qfc.network` |
| Bridge Contract | `0x47ea0e0cdc65cc1f4f7b21f922219139f23e1a27` |

## 2. Ethereum Sepolia

| Field | Value |
|-------|-------|
| Network Name | Sepolia |
| RPC URL | `https://rpc.sepolia.org` |
| Chain ID | `11155111` |
| Symbol | `ETH` |
| Explorer | `https://sepolia.etherscan.io` |
| Faucets | https://www.alchemy.com/faucets/ethereum-sepolia |
| | https://faucets.chain.link/sepolia |
| | https://faucet.quicknode.com/ethereum/sepolia |
| Bridge Contract | `0x8E6d4cD14EB6eEFeB040a6ecE53d11dC9ef8137C` |

## 3. BSC Testnet

| Field | Value |
|-------|-------|
| Network Name | BSC Testnet |
| RPC URL | `https://data-seed-prebsc-1-s1.binance.org:8545` |
| Chain ID | `97` |
| Symbol | `tBNB` |
| Explorer | `https://testnet.bscscan.com` |
| Faucet | https://www.bnbchain.org/en/testnet-faucet |
| Bridge Contract | `0x51Ef5567Afd34E1a178757C5Cf68B7132f861Fe8` |

## 4. Arbitrum Sepolia

| Field | Value |
|-------|-------|
| Network Name | Arbitrum Sepolia |
| RPC URL | `https://sepolia-rollup.arbitrum.io/rpc` |
| Chain ID | `421614` |
| Symbol | `ETH` |
| Explorer | `https://sepolia.arbiscan.io` |
| Faucets | https://faucet.chainstack.com/arbitrum-sepolia-faucet |
| | https://www.l2faucet.com/arbitrum |
| | https://faucets.chain.link/arbitrum-sepolia |
| Bridge Contract | `0x8E6d4cD14EB6eEFeB040a6ecE53d11dC9ef8137C` |

## 5. Polygon Amoy

| Field | Value |
|-------|-------|
| Network Name | Polygon Amoy |
| RPC URL | `https://rpc-amoy.polygon.technology` |
| Chain ID | `80002` |
| Symbol | `POL` |
| Explorer | `https://amoy.polygonscan.com` |
| Faucets | https://faucet.polygon.technology |
| | https://www.alchemy.com/faucets/polygon-amoy |
| Bridge Contract | `0x8E6d4cD14EB6eEFeB040a6ecE53d11dC9ef8137C` |

## 6. Base Sepolia

| Field | Value |
|-------|-------|
| Network Name | Base Sepolia |
| RPC URL | `https://sepolia.base.org` |
| Chain ID | `84532` |
| Symbol | `ETH` |
| Explorer | `https://sepolia.basescan.org` |
| Faucets | https://www.alchemy.com/faucets/base-sepolia |
| | https://faucet.quicknode.com/base/sepolia |
| Bridge Contract | `0x8E6d4cD14EB6eEFeB040a6ecE53d11dC9ef8137C` |

## 7. Optimism Sepolia

| Field | Value |
|-------|-------|
| Network Name | Optimism Sepolia |
| RPC URL | `https://sepolia.optimism.io` |
| Chain ID | `11155420` |
| Symbol | `ETH` |
| Explorer | `https://sepolia-optimistic.etherscan.io` |
| Faucets | https://www.alchemy.com/faucets/optimism-sepolia |
| | https://faucet.quicknode.com/optimism/sepolia |
| | https://faucets.chain.link/optimism-sepolia |
| Bridge Contract | *Not yet deployed* |

---

## Deployer Wallet

| Field | Value |
|-------|-------|
| Address | `0x46e95879eD225038760617c33362da692412a8AC` |
| Used for | Contract deployment + relayer operations |

---

## Quick Add to MetaMask

Visit https://chainlist.org and search by chain ID, or manually add via Settings → Networks → Add Network using the RPC URL, Chain ID, Symbol, and Explorer URL from each section above.

---

## Bridge Deployment Command

To deploy BridgeLock on a new EVM chain:

```bash
cd qfc-contracts
npx hardhat run scripts/deploy-bridge-lock.ts --network <networkName>
```

Network names configured in `hardhat.config.ts`:
`qfc_testnet`, `sepolia`, `bscTestnet`, `arbitrumSepolia`, `polygonAmoy`, `baseSepolia`
