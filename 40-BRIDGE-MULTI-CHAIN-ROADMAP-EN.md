# QFC Bridge — Multi-Chain Expansion Roadmap

> Last updated: 2026-04-07

---

## 1. Current State

| # | Chain | Chain ID | Type | Status |
|---|-------|----------|------|--------|
| 1 | QFC Testnet | 9000 | EVM | ✅ Live |
| 2 | Ethereum Sepolia | 11155111 | EVM (ERC20) | ✅ Live |
| 3 | BSC Testnet | 97 | EVM (BEP20) | ✅ Live |

**Supported tokens:** QFC, USDT, USDC, TTK

**Architecture:** Lock-and-unlock bridge with off-chain relayer. Same BridgeLock contract deployed on each chain. Relayer listens for `BridgeRequest` events and calls `unlock()` on the destination chain.

---

## 2. Expansion Plan

### Phase 1: EVM Chains (1–2 weeks)

Adding 3 more EVM testnets. Same contract, same relayer logic — config-only changes.

| # | Chain | Chain ID | RPC | Explorer |
|---|-------|----------|-----|----------|
| 4 | Arbitrum Sepolia | 421614 | https://sepolia-rollup.arbitrum.io/rpc | https://sepolia.arbiscan.io |
| 5 | Polygon Amoy | 80002 | https://rpc-amoy.polygon.technology | https://amoy.polygonscan.com |
| 6 | Base Sepolia | 84532 | https://sepolia.base.org | https://sepolia.basescan.org |

**Work per chain:**

1. Deploy BridgeLock contract (via Hardhat in `qfc-contracts`)
2. Add chain config to `src/lib/chains.ts` (frontend)
3. Add token addresses to `src/lib/tokens.ts` (frontend)
4. Add chain to `relayer/src/config.ts`
5. Add chain ID mappings in `relayer/src/listener.ts` and `relayer/src/prover.ts`
6. Add env vars to `.env.example` (frontend + relayer)
7. Fund relayer wallet on new chain (testnet faucet)
8. Test lock → relay → unlock round-trip

**Effort:** ~2 hours per chain (mostly deploy + config). Can be parallelized.

**Files to modify:**

| File | Change |
|------|--------|
| `src/lib/chains.ts` | Add 3 chain entries |
| `src/lib/tokens.ts` | Add addresses per chain |
| `relayer/src/config.ts` | Add 3 chains to `loadConfig()` |
| `relayer/src/listener.ts` | Add to `CHAIN_ID_TO_KEY` |
| `relayer/src/prover.ts` | Add to `KEY_TO_CHAIN_ID` |
| `.env.example` | Add RPC + bridge address vars |
| `relayer/.env.example` | Add RPC + bridge address vars |

### Phase 2: Tron Nile (2–3 weeks)

Tron is EVM-like but not EVM-compatible. Requires separate adapter.

| Difference | Impact |
|------------|--------|
| Address format | Base58 (T...) instead of 0x, need TronWeb |
| SDK | TronWeb instead of ethers.js |
| ABI encoding | Same Solidity but different parameter encoding |
| Transaction signing | Different signature scheme |
| Event listening | TronGrid API instead of eth_getLogs |

**Work:**

1. **Contract:** Rewrite in Tron-compatible Solidity (minor tweaks), deploy via TronBox
2. **Frontend:** Add TronLink wallet detection alongside MetaMask, chain-specific transaction flow
3. **Relayer:** New `TronListener` class using TronGrid events, new `TronSubmitter` using TronWeb for unlock calls
4. **Token mapping:** Deploy wrapped tokens on Tron Nile or use existing TRC20 tokens

**Key decisions:**
- Support TronLink wallet only? Or WalletConnect?
- Use TronGrid (centralized) or self-hosted Tron fullnode for events?

### Phase 3: Solana Devnet (4–6 weeks)

Completely different architecture. Biggest lift.

| Difference | Impact |
|------------|--------|
| Programming model | Account-based, not contract-based |
| Language | Rust (Anchor framework) |
| Token standard | SPL Token, not ERC20 |
| Wallet | Phantom/Solflare, not MetaMask |
| Transaction | Instructions + accounts, not ABI calls |
| Events | Program logs, not EVM events |

**Work:**

1. **Contract:** Write Anchor program (Rust) implementing lock/unlock with PDA vaults
2. **Frontend:** Add Solana wallet adapter (@solana/wallet-adapter), build Solana-specific bridge UI flow
3. **Relayer:** New `SolanaListener` using @solana/web3.js for log parsing, new `SolanaSubmitter` for unlock instructions
4. **Token mapping:** Create SPL token mint for bridged assets on Devnet

**Key decisions:**
- Use Anchor or raw Solana program?
- Wrapped tokens: who holds mint authority? (relayer multisig)
- Finality: Solana confirms in ~400ms vs EVM 12s — how to handle?

---

## 3. Implementation Order & Timeline

```
Week 1-2:   Phase 1 — Arbitrum + Polygon + Base (EVM, config-only)
Week 3-5:   Phase 2 — Tron Nile (new SDK adapter)
Week 6-11:  Phase 3 — Solana Devnet (new program + wallet + relayer)
```

### Dependencies

| Phase | Blocker | Notes |
|-------|---------|-------|
| Phase 1 | None | Can start immediately |
| Phase 2 | TronGrid API key | Free tier available |
| Phase 3 | Anchor toolchain setup | `anchor init`, Solana CLI |

### Risk Matrix

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| EVM chain RPC instability | Medium | Low | Use multiple RPC providers, fallback URLs |
| Tron event delivery delays | Medium | Medium | Polling fallback + retry logic |
| Solana program audit | High | High | Use battle-tested Anchor patterns, limit TVL |
| Relayer key compromise | Low | Critical | Multisig unlock on high-value chains |

---

## 4. Architecture Changes

### Current (EVM-only)

```
Frontend (ethers.js) → BridgeLock contract → BridgeRequest event
                                                    ↓
                                              Relayer (ethers.js)
                                                    ↓
                                        BridgeLock.unlock() on dest chain
```

### Target (Multi-VM)

```
Frontend
  ├─ EVM chains (ethers.js) → BridgeLock.lock()
  ├─ Tron (TronWeb)         → BridgeLock.lock()
  └─ Solana (wallet-adapter) → bridge_program.lock()
                                        ↓
                                   Relayer
                  ├─ EVMListener (ethers.js)     ─┐
                  ├─ TronListener (TronWeb)       ├→ SQLite queue
                  └─ SolanaListener (web3.js)    ─┘
                                        ↓
                                   Submitter
                  ├─ EVMSubmitter (ethers.js)     → unlock()
                  ├─ TronSubmitter (TronWeb)      → unlock()
                  └─ SolanaSubmitter (web3.js)    → unlock instruction
```

Relayer becomes a multi-VM event aggregator with chain-specific listener/submitter plugins.

---

## 5. Pre-requisites Before Starting

- [ ] Fix relayer QFC chainId discrepancy (7701 → 9000)
- [ ] Get testnet faucet funds on Arbitrum Sepolia, Polygon Amoy, Base Sepolia
- [ ] Verify BridgeLock contract compiles with latest Hardhat
- [ ] Ensure relayer private key has funds on all target chains
