# QFC v3.0 Roadmap: AI-Native Blockchain

> Last Updated: 2026-03-08 | Version 1.0
> Author: Alex Wei, Product Manager @ QFC Network
> Status: Draft — pending engineering review

---

## 1. Context

QFC v2.0 delivered a working AI inference network: miners run real inference tasks, results are verified via spot-check, and fees are settled on-chain. The full v2.0 stack includes:

- 3 new crates (`qfc-inference`, `qfc-ai-coordinator`, `qfc-miner`), 316+ tests
- CPU/CUDA/Metal inference backends with candle ML
- TaskPool → miner assignment → proof submission → spot-check verification → fee settlement
- Model governance (validator vote >2/3), public inference API, SDK integration
- Testnet deployment with mixed PoW/inference modes

**v3.0 goal**: Transform QFC from "a blockchain that can do AI inference" into **"the AI-native blockchain"** — where inference is mathematically verified, consensus is DAG-fast, tokenomics are sustainable, and any chain can use QFC as its AI backend.

---

## 2. v3.0 Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│  External Chains (Ethereum, Arbitrum, Solana, etc.)          │
│  └─ Hyperlane/LayerZero → QFC Cross-Chain AI Oracle          │
├─────────────────────────────────────────────────────────────┤
│  User Layer                                                   │
│  ├─ Direct Mode (TaskPool, real-time, <1s)                   │
│  └─ Intent Mode (declarative constraints, batch, pipelines)  │
├─────────────────────────────────────────────────────────────┤
│  EVM Layer                    │  QVM Layer                    │
│  - Agent token factory        │  - Agent capability resources │
│  - ERC-4337 agent wallets     │  - Model registry (Resource)  │
│  - DeFi protocols             │  - Inference intents          │
│  - Revenue sharing contracts  │  - Kill switches              │
├───────────────────────────────┴───────────────────────────────┤
│  AI Coordinator (enhanced)                                    │
│  ├─ Tiered verification (zkML / Optimistic ZK / spot-check) │
│  ├─ QIB benchmark scoring + multi-layer anti-gaming          │
│  ├─ Reverse auction pricing (fiat-denominated, BME)          │
│  └─ P2P model distribution (libp2p swarm)                    │
├─────────────────────────────────────────────────────────────┤
│  Consensus Layer (DAG-BFT)                                    │
│  ├─ Mysticeti-variant 3-round commit (<500ms finality)       │
│  ├─ PoC-weighted leader election (7 dimensions)              │
│  ├─ Narwhal-style data availability (separate from ordering) │
│  └─ Block-STM parallel execution (~17x for AI tasks)         │
├─────────────────────────────────────────────────────────────┤
│  Storage Layer                                                │
│  ├─ Inference results: IPFS (existing)                       │
│  ├─ Model weights: P2P swarm (primary) + Filecoin/Arweave   │
│  └─ On-chain: model registry, proofs, PoC scores            │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Feature Breakdown by Phase

### Phase 1: Performance & Verification Foundation (8-12 weeks)

> **Goal**: Make QFC fast enough and trustworthy enough to be taken seriously.

#### 1.1 DAG Consensus (Mysticeti-variant)

**Research basis**: [21-DAG-CONSENSUS-RESEARCH.md](./21-DAG-CONSENSUS-RESEARCH.md)

| Deliverable | Description | Impact |
|------------|-------------|--------|
| Narwhal-style DA layer | Separate data availability from ordering; large inference results don't block consensus | Throughput |
| Mysticeti 3-round commit | Uncertified DAG-BFT, every validator proposes every round | <500ms finality |
| PoC-weighted leader election | Replace pure-stake with composite 7-dimension PoC score | Fairer rewards |
| Block-STM parallel execution | Optimistic parallel tx execution with conflict detection | ~17x for AI tasks |
| Dual-path execution | Fast path (skip consensus) for private inference; full path for shared state | Sub-second private inference |

**Target metrics**:

| Metric | v2.0 (current) | v3.0 (target) |
|--------|----------------|---------------|
| Consensus latency | ~seconds | **<500ms** |
| Throughput | Limited by serial exec | **100K-200K TPS** |
| Finality | Multi-round | **<1 second** |
| AI task parallelism | Sequential | **Block-STM parallel** |

**Key risks**:
- Mysticeti is complex; consider forking Sui's open-source implementation as starting point
- PoC-weighted leader election needs careful simulation to avoid gaming
- Migration from current PoC consensus requires upgrade path design

**Estimated effort**: 2 engineers, 10-12 weeks

#### 1.2 Tiered zkML Verification

**Research basis**: [20-ZKML-RESEARCH.md](./20-ZKML-RESEARCH.md)

| Tier | Model Size | Method | Proving Time | Cost Premium |
|------|-----------|--------|-------------|-------------|
| Tier 1 | <1B params | Full ZK proof every inference (EZKL) | 1-30 seconds | 2-5x base fee |
| Tier 2 | 1-13B | Optimistic execution + ZK on challenge | Minutes (only if challenged) | 1.2-1.5x base fee |
| Tier 3 | 13B+ | Current spot-check (enhanced) | N/A | 1x base fee |

**Deliverables**:

| Deliverable | Description |
|------------|-------------|
| EZKL integration | Add EZKL as optional dependency in `qfc-inference`; miner generates ZK proof for Tier 1 models |
| `ComputeTaskType::VerifiedInference` | New task variant with proof_system field |
| Tier 1 proof verification | Validator verifies ZK proof on-chain instead of spot-check |
| Optimistic challenge protocol | Stake → challenge window → ZK dispute resolution for Tier 2 |
| Auto-tier selection | Determine verification tier automatically from model size |

**Tier 1 candidates** (current model registry):
- `qfc-embed-small` (22M params): proof in ~1 second
- `qfc-embed-medium` (110M params): proof in ~2-5 seconds
- `qfc-classify-small` (BERT-base): proof in ~5-15 seconds
- `qfc-llm-0.5b` (0.5B params): proof in ~15-30 seconds

**Key risks**:
- EZKL proof generation adds latency; miners need to price this in
- Proof verification gas cost on EVM side
- ONNX model compatibility (QFC already uses OnnxInference — good fit)

**Estimated effort**: 2 engineers, 8-10 weeks

#### 1.3 BME Tokenomics

**Research basis**: [22-AI-TOKENOMICS-COMPARISON.md](./22-AI-TOKENOMICS-COMPARISON.md)

| Deliverable | Description |
|------------|-------------|
| Burn-on-use | 85% of inference fee auto-buys QFC and burns |
| Fiat-denominated pricing | Users pay in USD/stablecoin; auto-convert to QFC |
| Reverse auction | Multiple eligible miners → lowest bid wins (Akash-style) |
| Miner reward vesting | 75% of rewards vest over 90 days; 25% immediate |
| Dynamic emission adjustment | Utilization >80% → reduce emissions; <20% → increase |
| Halving schedule | Bitcoin-style emission halving every 4 years |

**Fee flow**:
```
User pays $X for inference:
  → 85% auto-buys QFC → burned permanently
  → 10% → Network treasury
  → 5% → Protocol development

Miner earns:
  → Newly minted QFC (emission schedule)
  → 75% vests over 90 days, 25% immediate
```

**Key change from v2.0**: Currently fee settlement is 70/10/20 (miner/treasury/burn). v3.0 inverts to burn-dominant (85% burn) with emission-based miner rewards — decoupling user payment from miner reward.

**Key risks**:
- BME only works with real demand; during bootstrap phase, emissions must subsidize
- Reverse auction may race-to-the-bottom for low-margin inference
- Need careful simulation before deploying

**Estimated effort**: 1 engineer + 1 economist, 6-8 weeks

---

### Phase 2: Miner Ecosystem (8-10 weeks)

> **Goal**: Make it easy and profitable for anyone with a consumer GPU to mine.

#### 2.1 QFC Inference Benchmark (QIB)

**Research basis**: [26-DEPIN-HARDWARE-INCENTIVES.md](./26-DEPIN-HARDWARE-INCENTIVES.md)

Inspired by Render's OctaneBench — a standardized performance score per GPU.

| Deliverable | Description |
|------------|-------------|
| QIB benchmark suite | Standardized inference tasks (embed, classify, generate) |
| GPU profile database | Expected QIB ranges for common consumer GPUs |
| Registration challenge | One-time benchmark during miner onboarding |
| QIB-proportional rewards | `reward = base_emission * (miner_QIB / total_network_QIB) * uptime_multiplier` |

**Expected QIB scores**:

| GPU | QIB Score | Tier |
|-----|----------|------|
| RTX 3060 (12GB) | ~100 | Cold |
| RTX 4070 Ti (12GB) | ~250 | Warm |
| RTX 4090 (24GB) | ~600 | Hot |
| A100 (80GB) | ~1000 | Ultra |

#### 2.2 Multi-Layer Anti-Gaming

**Critical lesson from io.net**: 400K fake GPUs infiltrated their network. Staking alone doesn't prevent Sybil attacks.

| Layer | Trigger | What It Does |
|-------|---------|-------------|
| Registration challenge | One-time (join) | Run QIB benchmark; compare against known GPU profiles; flag anomalies |
| Periodic PoW challenge | Hourly | Random inference tasks from verified dataset; compare output hash |
| Spot-check re-execution | Per task (5-10%) | Existing v2.0 system — validator re-runs inference |
| Reputation scoring | Ongoing | Rolling window of verification results; higher rep → lower spot-check rate |

#### 2.3 P2P Model Distribution

**Research basis**: [23-DECENTRALIZED-MODEL-STORAGE.md](./23-DECENTRALIZED-MODEL-STORAGE.md)

| Deliverable | Description |
|------------|-------------|
| On-chain model registry | `ModelRegistration` resource with hash, CID, version, format |
| libp2p model swarm | BitTorrent-style P2P model distribution among miners |
| Chunked transfer | 4GB chunks, parallel download from multiple peers |
| Archival backup | Filecoin cold ($0.002/GB/yr) or Arweave/Irys ($0.03/GB one-time) |
| Foundation seed nodes | 3-5 regional nodes for bootstrap (US-East, EU-West, APAC) |

**Why P2P over CDN**: Zero marginal cost, self-scaling with network growth, already compatible (QFC uses libp2p).

#### 2.4 Miner Economics Target

| Scenario | GPU | Monthly Electricity | Monthly QFC Reward | Net Monthly |
|----------|-----|--------------------|--------------------|-------------|
| Optimistic | RTX 4090 | ~$22 | $80-120 | +$58-98 |
| Moderate | RTX 4070 Ti | ~$15 | $40-60 | +$25-45 |
| Conservative | RTX 3060 | ~$12 | $15-25 | +$3-13 |

**Design principle**: Positive ROI on electricity costs alone within 3-6 months, no hardware purchase required.

**Estimated effort**: 2 engineers, 8-10 weeks

---

### Phase 3: Cross-Chain & Composability (10-14 weeks)

> **Goal**: Make QFC the AI backend for every blockchain.

#### 3.1 Cross-Chain AI Oracle

**Research basis**: [25-CROSS-CHAIN-AI-ORACLE.md](./25-CROSS-CHAIN-AI-ORACLE.md)

| Deliverable | Description |
|------------|-------------|
| Hyperlane integration | Deploy Mailbox on QFC; custom ISM for inference attestation |
| Cross-Chain Oracle Coordinator | Receive requests → route to AI Coordinator → return verified results |
| `AIInferenceResult` message format | requestId, modelHash, inputHash, outputData, verificationTier, attestation |
| Destination chain contracts | `QFCOracle.sol` for requesting inference from any EVM chain |
| Large result handling | Output to IPFS; cross-chain message contains only CID + proof hash |

**End-to-end flow**:
```
External chain contract → Hyperlane → QFC Oracle Coordinator →
AI Coordinator → miner executes → verified → attestation →
Hyperlane → callback on external chain
```

**Latency**: 2-30 minutes end-to-end (dominated by cross-chain messaging, not inference).

**Gas cost**: $0.40-1.60 per cross-chain inference on Ethereum L1; 10-100x cheaper on L2s.

**Estimated effort**: 2 engineers, 8-10 weeks

#### 3.2 Agent Capability Resources (QVM)

**Research basis**: [24-AI-AGENT-FRAMEWORK.md](./24-AI-AGENT-FRAMEWORK.md)

| Deliverable | Description |
|------------|-------------|
| `InferenceCapability` resource | Budget, allowed models, expiry — VM-enforced, not contract-level |
| `AgentRegistration` resource | Protocol digests, capabilities, endpoint, stake |
| Capability-gated inference | AI Coordinator checks capability resource before task assignment |
| Kill switch | Resource freeze/destroy functions |
| Discovery API | RPC endpoints for querying agents by capability |

**Why stronger than EVM**: `InferenceCapability` cannot be forged, duplicated, or spent beyond its limit at the VM level. No reentrancy risk — resources consumed linearly.

#### 3.3 Intent Mode (Lightweight)

**Research basis**: [27-INTENT-BASED-ARCHITECTURE.md](./27-INTENT-BASED-ARCHITECTURE.md)

| Deliverable | Description |
|------------|-------------|
| `InferenceIntent` resource | Declarative constraints: max_cost, max_latency, model capability |
| Lightweight matchmaker | Protocol-level constraint evaluation + PoC-weighted matching |
| Dutch auction | For non-urgent/batch jobs: price decays over time, first miner to accept wins |
| Composable pipelines | Chain intents: "classify → if X → detect → describe" |
| Batch window | Group similar intents into 30-second windows (CoW-style) |

**Two-path design**: Direct Mode (existing TaskPool, <1s) for real-time; Intent Mode (5-30s) for cost-optimized/complex jobs. Users choose.

**Estimated effort**: 3 engineers, 10-14 weeks (all of Phase 3)

---

### Phase 4: Agent Economy (8-10 weeks)

> **Goal**: Enable an ecosystem of AI agents that generate real revenue.

#### 4.1 Agent Token Factory (EVM)

**Research basis**: [24-AI-AGENT-FRAMEWORK.md](./24-AI-AGENT-FRAMEWORK.md)

| Deliverable | Description |
|------------|-------------|
| Agent token factory contract | EVM contract for launching ERC-20 agent tokens (Virtuals pattern) |
| Bonding curve | Agent launch fee → bonding curve → permanent LP |
| Revenue sharing | On-chain fee distribution: 60% agent wallet, 30% buyback & burn, 10% treasury |
| Cross-VM link | Agent tokens (EVM) linked to agent capabilities (QVM) via bridge |

#### 4.2 ElizaOS Plugin

| Deliverable | Description |
|------------|-------------|
| `qfc-elizaos-plugin` | npm package wrapping `qfc-sdk-js` |
| `RUN_INFERENCE` action | Agent can call QFC inference from ElizaOS runtime |
| Capability management | Plugin manages `InferenceCapability` resource automatically |

#### 4.3 ERC-4337 Agent Wallet

| Deliverable | Description |
|------------|-------------|
| Smart contract wallet template | ERC-4337 with QFC-specific validation logic |
| Spending limits | Per-tx and per-period caps, enforced by wallet |
| Contract allowlists | Agents can only interact with whitelisted contracts |
| Paymaster | Gas abstraction for agents (sponsor pays gas) |

**Estimated effort**: 2 engineers, 8-10 weeks

---

### Phase 5: Future / Research (no fixed timeline)

These are tracked but not scheduled for v3.0 initial release:

| Feature | Research Doc | Trigger to Start |
|---------|-------------|-----------------|
| TEE confidential inference (Secure tier) | [19-PRIVACY-AI-INFERENCE.md](./19-PRIVACY-AI-INFERENCE.md) | When NVIDIA H100 TEE is widely available |
| IBC integration for Cosmos ecosystem | [25-CROSS-CHAIN-AI-ORACLE.md](./25-CROSS-CHAIN-AI-ORACLE.md) | After Hyperlane proves product-market fit |
| FHE for fully private inference | [19-PRIVACY-AI-INFERENCE.md](./19-PRIVACY-AI-INFERENCE.md) | When overhead drops below 10x |
| Full solver network for intents | [27-INTENT-BASED-ARCHITECTURE.md](./27-INTENT-BASED-ARCHITECTURE.md) | Only if matchmaker proves insufficient |
| Walrus/0G storage integration | [23-DECENTRALIZED-MODEL-STORAGE.md](./23-DECENTRALIZED-MODEL-STORAGE.md) | When platforms mature (2027+) |

---

## 4. Explicitly Not Doing

| Decision | Rationale | Research Basis |
|----------|-----------|---------------|
| No full Anoma-style intent OS | Over-engineering; lightweight matchmaker is sufficient for AI inference | doc #27 |
| No Filecoin-style high collateral | Kills decentralization; Filecoin saw provider consolidation | doc #26 |
| No Bittensor-style pure-emission model | Unsustainable without fee revenue; $0 direct revenue | doc #22 |
| No full solver network | Centralization risk; 2 builders win >90% of Ethereum block auctions | doc #27 |
| No Walrus/0G integration (yet) | Both platforms too immature (mainnet <1 year) | doc #23 |
| No FHE privacy (yet) | 100-1000x overhead; wait for hardware acceleration | doc #19 |

---

## 5. Dependencies & Critical Path

```
Phase 1 (foundation) ──────────────────────────────────────────────►
  ├── 1.1 DAG Consensus ──┐
  ├── 1.2 zkML Verification ──┤─── All three are independent, can parallel
  └── 1.3 BME Tokenomics ────┘

Phase 2 (miners) ──────────────────────────────────────────────────►
  ├── 2.1 QIB Benchmark ──────── depends on 1.1 (new consensus scoring)
  ├── 2.2 Anti-Gaming ────────── depends on 2.1 (QIB profiles)
  ├── 2.3 P2P Model Distro ──── independent
  └── 2.4 Miner Economics ────── depends on 1.3 (BME)

Phase 3 (cross-chain) ────────────────────────────────────────────►
  ├── 3.1 Cross-Chain Oracle ──── depends on 1.2 (zkML for attestation)
  ├── 3.2 Agent Resources ─────── depends on QVM (already built in v2.0)
  └── 3.3 Intent Mode ────────── depends on 1.1 (DAG for throughput)

Phase 4 (agents) ─────────────────────────────────────────────────►
  ├── 4.1 Agent Token Factory ── depends on 3.2 (agent resources)
  ├── 4.2 ElizaOS Plugin ─────── depends on 3.1 (cross-chain oracle)
  └── 4.3 ERC-4337 Wallet ────── independent
```

**Critical path**: DAG Consensus (1.1) → QIB (2.1) → Anti-Gaming (2.2). This is the longest sequential chain and should start first.

**Maximum parallelism**: Phase 1's three workstreams (DAG, zkML, BME) are independent and should run in parallel from day 1.

---

## 6. Engineering Resource Estimate

| Phase | Duration | Engineers | Key Skills |
|-------|----------|-----------|------------|
| Phase 1 | 10-12 weeks | 4-5 | Consensus (Rust), ZK cryptography, token economics |
| Phase 2 | 8-10 weeks | 2-3 | libp2p/networking (Rust), GPU/ML, benchmarking |
| Phase 3 | 10-14 weeks | 3-4 | Cross-chain (Solidity + Rust), Move/QVM, protocol design |
| Phase 4 | 8-10 weeks | 2-3 | Solidity (ERC-4337), TypeScript (ElizaOS), frontend |

**Phases 1 & 2 can overlap** (2.3 P2P model distribution is independent). With 5 engineers, total estimated timeline: **6-9 months**.

---

## 7. Success Metrics

### Phase 1 Complete

| Metric | Target |
|--------|--------|
| Consensus latency (P50) | <500ms |
| Throughput | >100K TPS |
| Tier 1 models verified via ZK | 100% of embed/classify tasks |
| BME burn rate | >0 QFC burned per day |

### Phase 2 Complete

| Metric | Target |
|--------|--------|
| Active miners | >100 |
| Fake GPU detection rate | >99% |
| Average miner monthly profit | >$20 (RTX 4070 Ti) |
| Model distribution time (10GB) | <10 minutes for new miner |

### Phase 3 Complete

| Metric | Target |
|--------|--------|
| Connected chains (via Hyperlane) | >5 |
| Cross-chain inference requests/day | >100 |
| Registered AI agents | >10 |
| Intent pipeline completion rate | >95% |

### Phase 4 Complete

| Metric | Target |
|--------|--------|
| Agent tokens launched | >5 |
| Agent token total market cap | >$1M |
| ElizaOS plugin installs | >50 |
| Revenue-generating agents | >3 |

---

## 8. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| DAG consensus migration breaks existing testnet | High | High | Implement as opt-in fork; run both consensus engines during transition |
| zkML proving too slow for user experience | Medium | Medium | Start with Tier 1 only (small models, seconds); Tier 2/3 are fallbacks |
| BME creates deflationary spiral during low demand | Medium | High | Dynamic emission adjustment; floor emission rate during bootstrap |
| Miner gaming bypasses QIB benchmark | Medium | Medium | Hourly PoW challenges + spot-check; io.net's post-incident design |
| Cross-chain messaging latency too high for real-time | High | Low | Market as "async AI oracle" not "real-time"; batch mode |
| Solver centralization in intent mode | Low | Medium | Protocol-level matchmaker, not open solver network |
| EZKL dependency introduces supply chain risk | Low | Medium | Abstract behind `ProofSystem` trait; support multiple backends |

---

## 9. Research Documents Index

All research informing this roadmap:

| # | Document | Key Recommendation | Phase |
|---|----------|-------------------|-------|
| 17 | [Smart Contract Landscape](./17-SMART-CONTRACT-LANDSCAPE.md) | Sui object model for AI tasks; dual-VM composability | Background |
| 18 | [AI Model Support Strategy](./18-AI-MODEL-SUPPORT-STRATEGY.md) | 20-model tiered registry; cross-backend determinism | Phase 2 |
| 19 | [Privacy-Preserving AI](./19-PRIVACY-AI-INFERENCE.md) | TEE for Secure tier; FHE too expensive today | Phase 5 |
| 20 | [zkML Research](./20-ZKML-RESEARCH.md) | Tiered verification: full ZK / optimistic ZK / spot-check | Phase 1 |
| 21 | [DAG Consensus](./21-DAG-CONSENSUS-RESEARCH.md) | Mysticeti-variant + Block-STM + Narwhal DA | Phase 1 |
| 22 | [AI Tokenomics](./22-AI-TOKENOMICS-COMPARISON.md) | BME + collateral + halving hybrid | Phase 1 |
| 23 | [Decentralized Model Storage](./23-DECENTRALIZED-MODEL-STORAGE.md) | 4-layer hybrid: registry → archival → P2P swarm → CDN | Phase 2 |
| 24 | [AI Agent Frameworks](./24-AI-AGENT-FRAMEWORK.md) | VM-enforced capabilities; agent tokenization on EVM | Phase 3-4 |
| 25 | [Cross-Chain AI Oracle](./25-CROSS-CHAIN-AI-ORACLE.md) | Hyperlane + custom ISM; coprocessor pattern | Phase 3 |
| 26 | [DePIN Hardware Incentives](./26-DEPIN-HARDWARE-INCENTIVES.md) | QIB scoring + multi-layer anti-gaming + low barriers | Phase 2 |
| 27 | [Intent-Based Architecture](./27-INTENT-BASED-ARCHITECTURE.md) | Lightweight matchmaker; two-path (direct + intent) | Phase 3 |

---

## 10. Open Questions for Engineering Review

1. **DAG consensus migration**: Fork Sui's Mysticeti implementation or build from scratch? Sui is Apache 2.0 licensed. Trade-off: faster start vs deeper understanding.

2. **EZKL integration**: Add as Rust dependency (via FFI) or run as sidecar process? EZKL is Python/Rust — compatibility with `qfc-inference` candle stack?

3. **BME transition**: How do we migrate from current 70/10/20 fee split to BME? Hard fork or gradual parameter adjustment?

4. **Block-STM conflict detection**: How does this interact with existing `qfc-executor`? Does our EVM (revm) support the read/write set tracking needed?

5. **Hyperlane deployment**: Who operates the QFC validators for the Hyperlane ISM? Same validators as consensus, or separate set?

6. **QIB benchmark**: What specific inference tasks should be in the benchmark suite? Need deterministic results across GPU architectures (see doc #18 Section 4.4 on cross-backend determinism).

7. **Model distribution daemon**: Separate binary or integrated into `qfc-miner`? Trade-off: simplicity vs resource management.

8. **Agent token factory**: Deploy on QFC's EVM directly, or on an L2/sidechain to avoid mainnet bloat?

9. **Vesting contract**: Implement miner reward vesting in EVM (Solidity) or QVM (QuantumScript)? QVM gives resource-level guarantees but less tooling.

10. **Testing strategy**: How do we test DAG consensus with PoC scoring in a testnet with <10 validators? Need simulation framework.
