# QFC Project Status & Next Steps

> Last updated: 2026-04-07

---

## 1. Current Status

### 1.1 Infrastructure

| Component | Status | Notes |
|-----------|--------|-------|
| Testnet block production | ✅ Normal | Block height 140,000+, producing continuously |
| 4-VPS cluster | ✅ Stable | VPS-A (App), B (Node), C (DB), D (Observability) |
| Terraform | ✅ Synced | State stored in S3, code matches AWS actual state |
| Monitoring & alerts | ✅ Running | Prometheus + Grafana + AlertManager + Telegram Bot |
| CI/CD | ✅ Automated | GitHub Actions → GHCR → auto image tag updates |
| Disk usage | ✅ Healthy | VPS-A: 13% (58GB), VPS-D: 9% (116GB) |

### 1.2 Chain & Miners

| Component | Status | Notes |
|-----------|--------|-------|
| Nodes (3) | ✅ Healthy | geth-compatible, 100% EVM compatible |
| Miners (2) | ✅ Running | AI inference tasks submitted continuously, proofs accepted |
| Chain ID | 9000 | Testnet |
| Block time | ~19s | |
| Inference models | qfc-embed-small, qfc-embed-medium | candle ML backend |

### 1.3 Live Services

| Service | URL | Status |
|---------|-----|--------|
| Block Explorer | explorer.testnet.qfc.network | ✅ 200 |
| Explorer API | api.explorer.testnet.qfc.network | ✅ 200 |
| DEX | dex.testnet.qfc.network | ✅ 200 |
| DeFi Dashboard | defi.testnet.qfc.network | ✅ 200 |
| NFT Marketplace | nft.testnet.qfc.network | ✅ 200 |
| Cross-chain Bridge | bridge.testnet.qfc.network | ✅ 200 |
| Faucet | faucet.testnet.qfc.network | ✅ 200 |
| Game Center | games.testnet.qfc.network | ✅ 200 |
| Agent Hub | agenthub.testnet.qfc.network | ✅ 200 |

### 1.4 Client Tools

| Tool | Status | Notes |
|------|--------|-------|
| Browser Wallet | ✅ Feature-complete | Swap, NFT, Inference Submit, Speed Up/Cancel Tx |
| JS SDK | ✅ Complete | ethers.js wrapper |
| Python SDK | ✅ Complete | web3.py wrapper |
| CLI Tool | ✅ Complete | Node.js + commander |
| Mobile Wallet | ✅ Complete | React Native + Expo |

### 1.5 Smart Contracts (Deployed to Testnet)

| Contract | Description |
|----------|-------------|
| DEX (Factory + Router + WQFC) | Uniswap V2-style AMM |
| NFT (CollectionFactory + Marketplace + AuctionHouse) | NFT creation, trading, auctions |
| Bridge (LockRelease + MintBurn) | QFC ↔ ETH/BSC cross-chain bridge |
| qUSD Stablecoin | CDP-style minting |
| DeFi (Lending Pool, Staking, Liquid Staking, Vaults, Launchpad) | Full DeFi protocol suite |

### 1.6 Known Issues

| Issue | Severity | Description |
|-------|----------|-------------|
| DeFi/NFT/DEX frontends use mock data | 🟡 Medium | Pages are live but no real contract interaction |
| AgentHub is an empty shell | 🟡 Medium | Design docs exist, no actual functionality |
| Wallet not on Chrome Web Store | 🟢 Low | Fully functional, just not published |
| Contracts not audited | 🟡 Medium | Acceptable for testnet, mandatory before mainnet |
| Only our own nodes producing blocks | 🟡 Medium | No external validators |

---

## 2. Roadmap

### Phase 1: Product Usability (Now → 4 weeks)

**Goal:** Enable real DeFi and NFT operations on testnet

#### 1.1 Wire Frontends to Contracts (Highest Priority)

The defi, nft-marketplace, and dex frontends all use mock data. They need to be wired to real contract calls.

| Project | Current State | Effort |
|---------|---------------|--------|
| DEX (qfc-dex) | Contracts deployed, frontend has hooks but addresses are zero | Small — fill in addresses, test interactions |
| NFT Marketplace (qfc-nft-marketplace) | Contracts deployed, frontend has ABIs but addresses are zero | Medium — needs indexer integration |
| DeFi Dashboard (qfc-defi) | Contracts deployed, frontend fully mocked | Large — every feature page needs wiring |

Priority: DEX → NFT → DeFi

#### 1.2 Publish Browser Wallet

- Package Chrome extension and submit to Chrome Web Store
- Prepare Store listing assets (screenshots, descriptions)
- Review cycle approximately 1–2 weeks

#### 1.3 Faucet Improvements

- Currently dispenses 10 QFC per request — sufficient but UX can be improved
- Add Captcha to prevent abuse

### Phase 2: AgentHub MVP (4 → 8 weeks)

**Goal:** Complete the minimal loop of Agent registration → task assignment → execution → receipt

AgentHub is QFC's differentiator. QFC is not "yet another EVM chain" — it's an "AI inference chain." AgentHub makes that positioning real.

#### 2.1 Core Flow

```
Agent Registration (ERC-721 NFT)
      ↓
GitHub Issue triggers Webhook
      ↓
Task assigned to Agent
      ↓
Agent executes (calls QFC inference API)
      ↓
Execution receipt written to GitHub + on-chain
```

#### 2.2 Components

| Component | Description | Repo |
|-----------|-------------|------|
| Agent Registry | ERC-721 contract, on-chain identity | qfc-contracts |
| Webhook Bridge | GitHub → AgentHub event forwarding | qfc-agenthub |
| Task Router | Capability-based Agent matching | qfc-agenthub |
| Receipt Store | Execution records, anchored on-chain | qfc-agenthub |
| AgentHub UI | Registration, monitoring, management | qfc-agenthub |

### Phase 3: Mainnet Preparation (8 → 16 weeks)

**Goal:** Meet mainnet launch requirements

#### 3.1 Security

- [ ] Core contract security audit (at minimum: DEX, Bridge, qUSD)
- [ ] Penetration testing (RPC nodes, Explorer API)
- [ ] Bug Bounty program

#### 3.2 Decentralization

- [ ] Open validator applications
- [ ] At least 10 external validator nodes
- [ ] Finalize validator economics (staking, slashing)

#### 3.3 Documentation & Developer Experience

- [ ] Complete developer documentation (qfc-docs)
- [ ] Contract deployment tutorials
- [ ] SDK usage examples
- [ ] API documentation (Explorer API, RPC extensions)

#### 3.4 Mainnet Configuration

- [ ] Chain ID 9001
- [ ] Finalize genesis configuration
- [ ] Execute initial token distribution
- [ ] Multi-region node deployment (at least 3 geographic regions)

### Phase 4: Ecosystem Expansion (Post-Mainnet)

- **Cross-chain AI Oracle** — Other chains call AI inference through QFC (see 25-CROSS-CHAIN-AI-ORACLE)
- **Model Marketplace** — Developers upload custom models to the QFC network
- **Agent Token Factory** — Agents issue their own tokens (see 36-AGENT-TOKEN-FACTORY)
- **CEX Listings** — Exchange partnerships

---

## 3. Technical Debt

| Item | Issue | Priority |
|------|-------|----------|
| Dockerfiles | Multiple Next.js projects missing `COPY public`, fixed incrementally | ✅ Resolved |
| VPS-A .env drift | docker-compose image tags managed manually in .env | Low |
| VPS-D Loki | Retaining only error/warn logs, 7-day retention | ✅ Optimized |
| Terraform state | Migrated to S3 backend, no longer at risk of loss | ✅ Resolved |
| Node.js 20 deprecation | GitHub Actions warns Node 20 removal by 2026-09 | Low — upgrade action versions before June |

---

## 4. Key Metrics (Testnet)

| Metric | Current | Target |
|--------|---------|--------|
| Block height | 140,000+ | Continuous growth |
| Active validators | 3 (internal) | 10+ (including external) |
| Deployed contracts | 15+ | 50+ |
| Daily active addresses | ~1 (dev team) | 100+ (after public test) |
| Inference tasks/day | ~8,600 (10s/task × 2 miners) | Scale on demand |
| Service uptime | 99%+ (last 7 days) | 99.9% |
