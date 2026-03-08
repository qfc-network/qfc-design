# Decentralized Model Storage for QFC AI Inference Network

> Last Updated: 2026-03-08 | Version 1.0
> GitHub Issue: #5
> Author: Alex Wei, Product Manager @ QFC Network

---

## 1. Executive Summary

QFC miners need to download and store AI model weights (80MB–140GB) to run inference. Currently, QFC uses IPFS (Kubo) for inference results >1MB. This report evaluates decentralized storage solutions for the larger challenge: distributing and persisting AI model weights across a global miner network.

**Key Findings:**

- **IPFS alone is insufficient** for GB-scale model distribution — no persistence guarantees, pinning ecosystem fragmenting (Infura deprecated, nft.storage struggling)
- **Filecoin cold storage** is absurdly cheap (~$0.002/GB/year) but retrieval requires unsealing (45–210 seconds) — good for archival only
- **Arweave via Irys** offers permanent storage at ~$0.03/GB one-time — best for canonical model snapshots
- **Walrus** (Sui) has elegant Red Stuff erasure coding but is too immature (mainnet March 2025) and Sui-coupled
- **P2P swarm distribution** (BitTorrent-style via libp2p) is the most practical approach for miner-to-miner model sharing — zero cost, self-scaling

**Recommendation**: Adopt a **4-layer hybrid architecture** — on-chain registry → durable archival (Filecoin/Arweave) → P2P swarm distribution → optional CDN fallback. Keep IPFS for inference results as-is.

---

## 2. Storage Solutions Evaluated

### 2.1 Filecoin

**Architecture**: Proof of Replication (PoRep) + Proof of Spacetime (PoSt). Data is sealed into 32GB sectors via slow encoding, then continuously proven stored via zk-SNARK challenges.

| Property | Value |
|----------|-------|
| Cold storage cost | ~$0.002/GB/year ($0.20/TB/year) |
| Hot storage (Storacha) | ~$0.20/GB/year (CDN-level retrieval) |
| Cold retrieval latency | 45 sec (NA), 210 sec (Africa) — requires unsealing |
| Hot retrieval (Saturn CDN) | Sub-second for cached content |
| Sealing time | Hours per 32GB sector (by design) |
| FVM | Programmable storage deals via smart contracts |

**2025 Development**: Proof of Data Possession (PDP) enables fast proofs on unsealed data — transforming Filecoin into a viable hot storage platform.

**Verdict**: Excellent for archival (pennies/TB/year). Cold retrieval too slow for model distribution. Storacha + Saturn CDN layer could work for hot model serving but adds complexity.

### 2.2 Arweave

**Architecture**: Pay once, store forever. An endowment mechanism ensures miners are incentivized indefinitely. Data is woven into the blockweave structure.

| Property | Value |
|----------|-------|
| Direct Arweave cost | ~$0.48/GB one-time (permanent) |
| Via Irys (formerly Bundlr) | ~$0.03/GB one-time (16x cheaper via tx bundling) |
| 10GB model cost | $0.30 (Irys) / $4.80 (direct) |
| 100GB model cost | $3.00 (Irys) / $48.00 (direct) |
| Irys throughput | 100K TPS, millisecond confirmations |
| Arweave mainnet | ~5 TPS, minutes for confirmation |

**Caveats**: AR token price volatility directly impacts storage costs. Not optimized for frequent updates. Irys uses subscription model (not truly permanent like Arweave mainnet).

**Verdict**: Best for immutable model snapshots with permanent provenance. Attractive one-time cost model for canonical model versions.

### 2.3 Walrus (Sui Ecosystem)

**Architecture**: Red Stuff — 2D erasure coding that splits data into primary/secondary slivers distributed across storage nodes. Self-healing when nodes go offline.

| Property | Value |
|----------|-------|
| Replication factor | 4.5x (vs 3-10x for traditional replication) |
| Encoded size overhead | ~5x original blob size |
| Max storage duration | 2 years (currently capped) |
| Mainnet | March 2025 |
| Pricing | Dynamic, WAL-denominated, not yet benchmarked at scale |

**Caveats**: Very new, limited production track record. 5x encoded size overhead. Tightly coupled to Sui ecosystem.

**Verdict**: Technically elegant for large blobs, but too immature and Sui-coupled for QFC today. Worth monitoring for 2027+.

### 2.4 IPFS + Pinning Services (Current QFC Approach)

| Service | Status | Cost | Notes |
|---------|--------|------|-------|
| **Pinata** | Active | ~$20/mo for 1TB + 500GB bandwidth | Most user-friendly, no cryptographic guarantees |
| **Infura** | Deprecated | N/A | Disabled new IPFS key creation late 2024 |
| **web3.storage** | Struggling | ~$0.10/MB one-time | Publicly requested donations Apr 2025 |
| **Storacha** | Active | Not public | Filecoin-backed hot storage, best reliability |

**Core limitation**: IPFS has no built-in persistence or incentive layer. Pinning services are "essentially Web2 companies running IPFS nodes on AWS." If the company shuts down, data vanishes.

**Verdict**: Works for current inference results (<few MB) but not suitable for GB-scale model weight distribution without a robust pinning/incentive layer.

### 2.5 0G (ZeroGravity)

**Architecture**: AI-focused L1 with 0G Chain (EVM-compatible), 0G Storage, 0G DA (claims 50 Gbps throughput), 0G Compute. Aristotle Mainnet launched September 2025.

**Verdict**: Interesting AI-native positioning but too early and unproven. Performance claims (50 Gbps DA) need independent verification. Worth tracking for 2027+.

---

## 3. Cost Comparison

For storing a **10GB model** for **1 year**:

| Solution | Annual Cost | Retrieval Speed | Persistence |
|----------|------------|----------------|-------------|
| Filecoin (cold) | ~$0.02 | 45–210 sec (unsealing) | Deal-based |
| Filecoin (Storacha hot) | ~$2.40 | Sub-second (CDN) | Filecoin-backed |
| Arweave (direct) | $4.80 (one-time, permanent) | Seconds (gateway) | Permanent |
| Arweave (via Irys) | $0.30 (one-time) | Milliseconds | Irys-backed |
| IPFS + Pinata | ~$2.40 | Seconds | Service-dependent |
| AWS S3 (reference) | $27.60 | Milliseconds | AWS SLA |

For a **100GB model** — multiply accordingly. Filecoin cold: ~$0.20/year. Arweave via Irys: ~$3.00 one-time.

---

## 4. Recommended Architecture: 4-Layer Hybrid

### 4.1 Overview

```
┌─────────────────────────────────────────────────────┐
│  Layer 1: On-Chain Model Registry                    │
│  - Model metadata (hash, version, size, format)     │
│  - Content-addressed via CID                         │
│  - Governance: model approval/sunset                 │
├─────────────────────────────────────────────────────┤
│  Layer 2: Durable Archival Storage                   │
│  - Filecoin cold ($0.002/GB/year)                   │
│  - OR Arweave/Irys ($0.03/GB one-time)             │
│  - Source of truth backup for canonical versions     │
├─────────────────────────────────────────────────────┤
│  Layer 3: P2P Swarm Distribution (Primary)           │
│  - libp2p-based model distribution daemon            │
│  - Every miner = seeder + leecher                    │
│  - Chunked transfer (4GB chunks, parallel download)  │
│  - Self-scaling: more miners = faster distribution   │
├─────────────────────────────────────────────────────┤
│  Layer 4: Bootstrap / CDN Fallback                   │
│  - 3-5 foundation seed nodes (US-East, EU, APAC)    │
│  - Storacha/Saturn CDN for cold-start regions        │
│  - Used only when swarm density is low               │
└─────────────────────────────────────────────────────┘
```

### 4.2 Layer 1: On-Chain Model Registry

```move
resource ModelRegistration {
    id: UID,
    model_id: String,           // "qfc-llm-7b"
    version: String,            // "v1.2.0"
    content_hash: Hash,         // SHA-256 of model weights
    cid: String,                // IPFS-compatible content identifier
    size_bytes: u64,            // Total model size
    format: String,             // "onnx", "gguf", "safetensors"
    quantization: String,       // "fp16", "q4_k_m", "awq"
    archival_cid: Option<String>, // Filecoin/Arweave reference
    approved: bool,             // Governance-approved
    registered_at: u64,
}
```

**Integrity verification**: Miners verify downloaded model weights against the on-chain `content_hash`. Any hash mismatch → reject and re-download.

### 4.3 Layer 2: Durable Archival

For each governance-approved model version:

1. Archive to **Filecoin cold storage** via FVM storage deal (~$0.002/GB/year)
2. Optionally archive to **Arweave via Irys** for permanent backup (~$0.03/GB)
3. Store the archival CID/txID in the on-chain `ModelRegistration`

**Total cost for QFC's initial 20-model registry** (estimated ~500GB total):
- Filecoin: ~$1.00/year
- Arweave/Irys: ~$15.00 one-time

### 4.4 Layer 3: P2P Swarm Distribution

The primary distribution mechanism. Every miner that has downloaded a model becomes a seeder.

**Protocol design** (libp2p-based, similar to BitTorrent):

```
New miner joins QFC network:
  1. Query on-chain ModelRegistry for required models
  2. For each model:
     a. Discover peers who have it (libp2p DHT / PubSub announcement)
     b. Download chunks in parallel from multiple peers (4GB chunks)
     c. Verify each chunk hash against manifest
     d. Verify full model hash against on-chain content_hash
     e. Begin seeding to other peers
```

**Why this works**:
- **Zero marginal cost**: Miners share bandwidth they already have
- **Self-scaling**: Network gets faster as it grows (more seeders)
- **Already compatible**: QFC uses libp2p (via Kubo/IPFS) — swarming is a natural extension
- **Proven pattern**: This is how Petals, GOAT, and Hugging Face distribute LLM weights

**Bandwidth incentive**: Miners who seed more model data earn a small PoC network score bonus (fits existing 10% network dimension).

### 4.5 Layer 4: Bootstrap Fallback

For cold-start scenarios (new region, unpopular model):

- **3-5 foundation-operated seed nodes** in key regions (US-East, EU-West, Asia-Pacific)
- Each seed node maintains all governance-approved models
- Storacha/Saturn CDN as additional fallback
- Seed nodes are temporary — once enough miners in a region, they become the primary source

---

## 5. Model Versioning & Lifecycle

### 5.1 Version Pinning

```
Model version lifecycle:
  1. Proposed → governance vote
  2. Approved → registered on-chain, archived, seeds deployed
  3. Active → miners download and serve
  4. Deprecated → new version available, 30-day migration window
  5. Sunset → removed from registry, miners can reclaim storage
```

### 5.2 Incremental Updates

For model updates (fine-tuning, quantization changes):
- **Delta distribution**: Only distribute changed layers/weights, not the full model
- Reduces bandwidth for common operations (e.g., quantization format change)
- Full model hash still verified against on-chain registry

### 5.3 Storage Requirements per Miner Tier

| Tier | Models Required | Estimated Storage |
|------|----------------|-------------------|
| Cold | Embedding models only | ~200MB |
| Warm | Embedding + classification + small LLM | ~1.5GB |
| Hot | All standard models incl. 7B LLM | ~15GB |
| Ultra | All models incl. 70B+ | ~150GB |
| Secure (TEE) | TEE-compatible models | Varies |

---

## 6. Comparison with Existing Projects

| Feature | Bittensor | Ritual | io.net | Akash | **QFC (target)** |
|---------|-----------|--------|--------|-------|-----------------|
| Model storage | None (off-chain) | Docker images | None | Docker images | **On-chain registry + P2P swarm** |
| Model verification | None | Container hash | None | Container hash | **Content-hash on-chain** |
| Distribution | Manual | Docker Hub | Manual | Docker registry | **libp2p P2P swarm** |
| Archival | None | None | None | None | **Filecoin/Arweave** |
| Versioning | None | Docker tags | None | Docker tags | **On-chain governance** |

**QFC's advantage**: End-to-end verifiable model supply chain — from on-chain registration through content-addressed distribution to hash-verified loading.

---

## 7. Implementation Roadmap

### Phase 1: On-Chain Model Registry (2-3 weeks)

| Task | Description |
|------|-------------|
| `ModelRegistration` resource | Define resource with hash, CID, version, format |
| Registry governance | Approval/sunset functions |
| RPC query API | Query models by ID, tier, format |

### Phase 2: P2P Model Distribution (4-6 weeks)

| Task | Description |
|------|-------------|
| Model distribution daemon | libp2p-based swarm in miner software |
| Chunk protocol | 4GB chunk transfer with parallel download |
| Integrity verification | Hash verification against on-chain registry |
| Seeding incentive | PoC network score bonus for seeders |

### Phase 3: Archival Integration (2-3 weeks)

| Task | Description |
|------|-------------|
| Filecoin archival | FVM storage deals for approved models |
| Arweave/Irys backup | Permanent archival for canonical versions |
| Foundation seed nodes | Deploy 3-5 regional seed nodes |

### Phase 4: Advanced Features (3-4 weeks)

| Task | Description |
|------|-------------|
| Delta updates | Incremental model weight distribution |
| CDN fallback | Storacha/Saturn integration for cold-start |
| Storage analytics | Dashboard for model distribution health |

---

## 8. Key Design Decisions

### 8.1 Why Not a Single Storage Solution?

No single decentralized storage platform handles all requirements:
- **Filecoin**: Cheap archival, slow retrieval
- **Arweave**: Permanent but expensive for frequent updates
- **IPFS**: No persistence guarantees
- **Walrus/0G**: Too immature

The hybrid approach uses each solution for what it does best.

### 8.2 Why P2P Swarm Over CDN?

| Property | P2P Swarm | Centralized CDN |
|----------|-----------|----------------|
| Cost | Free (miners share bandwidth) | $0.01-0.10/GB transfer |
| Scaling | Self-scaling with network growth | Linear cost increase |
| Decentralization | Fully decentralized | Single point of failure |
| Cold start | Slow (needs initial seeds) | Fast |
| QFC compatibility | libp2p already in stack | Additional infrastructure |

P2P is the primary path; CDN is the fallback for cold start only.

### 8.3 Why Content-Addressing?

Content-addressed storage (CID/hash) provides:
- **Integrity**: Any peer can verify data matches the expected hash
- **Deduplication**: Same model stored once regardless of location
- **Immutability**: Model versions are permanently referenceable
- **Compatibility**: CID works across IPFS, Filecoin, and Arweave ecosystems

---

## References

- [Filecoin Storage Costs](https://docs.filecoin.cloud/developer-guides/storage/storage-costs/)
- [Filecoin Proofs System](https://docs.filecoin.io/basics/the-blockchain/proofs)
- [Filecoin 2025 Year in Review](https://filecoin.io/blog/posts/filecoin-in-2025-year-in-review/)
- [Storacha — Decentralized Hot Storage](https://storacha.network)
- [Saturn Web3 CDN](https://saturn.tech/)
- [Arweave Storage Pricing](https://www.oreateai.com/blog/arweave-storage-pricing-unpacking-the-cost-of-permanent-data/)
- [Irys vs Arweave](https://blog.mexc.com/news/irys-network-the-programmable-datachain-challenging-arweave/)
- [Walrus Red Stuff Encoding](https://www.walrus.xyz/blog/how-walrus-red-stuff-encoding-works)
- [Walrus Paper (arXiv)](https://arxiv.org/abs/2505.05370)
- [IPFS Persistence Docs](https://docs.ipfs.tech/concepts/persistence/)
- [0G Official Site](https://0g.ai/)
- [Centralized vs Decentralized Storage Cost (CoinGecko)](https://www.coingecko.com/research/publications/centralized-decentralized-storage-cost)
