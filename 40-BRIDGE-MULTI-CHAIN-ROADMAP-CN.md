# QFC Bridge — 多链扩展路线图

> 最后更新: 2026-04-07

---

## 1. 当前状态

| # | 链 | Chain ID | 类型 | 状态 |
|---|------|----------|------|------|
| 1 | QFC Testnet | 9000 | EVM | ✅ 已上线 |
| 2 | Ethereum Sepolia | 11155111 | EVM (ERC20) | ✅ 已上线 |
| 3 | BSC Testnet | 97 | EVM (BEP20) | ✅ 已上线 |

**支持代币：** QFC、USDT、USDC、TTK

**架构：** Lock-and-unlock 桥，链下 relayer。同一套 BridgeLock 合约部署到每条链上。Relayer 监听 `BridgeRequest` 事件，在目标链调用 `unlock()`。

---

## 2. 扩展计划

### Phase 1：EVM 链（1-2 周）

新增 3 条 EVM 测试网。合约相同，relayer 逻辑相同，只需配置。

| # | 链 | Chain ID | RPC | Explorer |
|---|------|----------|-----|----------|
| 4 | Arbitrum Sepolia | 421614 | https://sepolia-rollup.arbitrum.io/rpc | https://sepolia.arbiscan.io |
| 5 | Polygon Amoy | 80002 | https://rpc-amoy.polygon.technology | https://amoy.polygonscan.com |
| 6 | Base Sepolia | 84532 | https://sepolia.base.org | https://sepolia.basescan.org |

**每条链的工作：**

1. 部署 BridgeLock 合约（通过 `qfc-contracts` 的 Hardhat）
2. 前端 `src/lib/chains.ts` 加链配置
3. 前端 `src/lib/tokens.ts` 加代币地址
4. Relayer `relayer/src/config.ts` 加链
5. Relayer `listener.ts` 和 `prover.ts` 加 chain ID 映射
6. 更新 `.env.example`（前端 + relayer）
7. 从水龙头给 relayer 钱包充 gas
8. 测试 lock → relay → unlock 往返

**工作量：** 每条链约 2 小时（主要是部署 + 配置），可并行。

### Phase 2：Tron Nile（2-3 周）

Tron 类似 EVM 但不兼容，需要单独适配。

| 差异 | 影响 |
|------|------|
| 地址格式 | Base58 (T...) 而非 0x，需要 TronWeb |
| SDK | TronWeb 而非 ethers.js |
| 事件监听 | TronGrid API 而非 eth_getLogs |
| 钱包 | TronLink 而非 MetaMask |

**工作：**
1. 合约用 TronBox 部署（Solidity 微调）
2. 前端加 TronLink 钱包检测
3. Relayer 新增 `TronListener` + `TronSubmitter`
4. 代币映射：部署 TRC20 包装代币

### Phase 3：Solana Devnet（4-6 周）

完全不同的架构，工作量最大。

| 差异 | 影响 |
|------|------|
| 编程模型 | Account-based，非 contract-based |
| 语言 | Rust (Anchor) |
| 代币标准 | SPL Token，非 ERC20 |
| 钱包 | Phantom/Solflare，非 MetaMask |

**工作：**
1. 用 Anchor 写 Rust 桥接程序
2. 前端加 Solana wallet adapter
3. Relayer 新增 `SolanaListener` + `SolanaSubmitter`
4. 在 Devnet 创建 SPL Token mint

---

## 3. 时间线

```
第 1-2 周:   Phase 1 — Arbitrum + Polygon + Base（EVM，纯配置）
第 3-5 周:   Phase 2 — Tron Nile（新 SDK 适配）
第 6-11 周:  Phase 3 — Solana Devnet（新程序 + 钱包 + relayer）
```

---

## 4. 架构演进

### 当前（仅 EVM）

```
前端 (ethers.js) → BridgeLock.lock() → BridgeRequest 事件
                                              ↓
                                        Relayer (ethers.js)
                                              ↓
                                    BridgeLock.unlock() 目标链
```

### 目标（多 VM）

```
前端
  ├─ EVM 链 (ethers.js)     → BridgeLock.lock()
  ├─ Tron (TronWeb)          → BridgeLock.lock()
  └─ Solana (wallet-adapter) → bridge_program.lock()
                                        ↓
                                   Relayer（多 VM 事件聚合器）
                  ├─ EVMListener (ethers.js)     ─┐
                  ├─ TronListener (TronWeb)       ├→ SQLite 队列
                  └─ SolanaListener (web3.js)    ─┘
                                        ↓
                                   Submitter
                  ├─ EVMSubmitter   → unlock()
                  ├─ TronSubmitter  → unlock()
                  └─ SolanaSubmitter → unlock instruction
```

---

## 5. 开始前的准备

- [ ] 修复 relayer QFC chainId 不一致（7701 → 9000）
- [ ] 获取 Arbitrum Sepolia、Polygon Amoy、Base Sepolia 测试网 gas
- [ ] 确认 BridgeLock 合约可编译部署
- [ ] 确保 relayer 私钥在所有目标链上有 gas
