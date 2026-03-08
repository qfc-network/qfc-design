# DAG Consensus Optimization for QFC's Proof of Contribution

> Last Updated: 2026-03-08 | Version 1.0
> GitHub Issue: #3

---

## 1. Executive Summary

QFC uses Proof of Contribution (PoC) consensus with multi-dimensional scoring. This report evaluates DAG-based consensus protocols that could enhance QFC's throughput and latency while preserving the PoC scoring model.

**Key Findings:**

- **Mysticeti** (Sui) achieves 390ms consensus commit with 200K-400K TPS — production-proven on mainnet
- **Shoal++** (Aptos/NSDI 2025) achieves 4.5 average message delays — 60% latency reduction over prior art
- **Block-STM** enables 160K+ TPS parallel execution — ideal for AI inference tasks (low contention)
- IOTA abandoned its Tangle DAG after years of research and adopted Mysticeti — **strong signal against unstructured DAGs**
- QFC's PoC scoring maps naturally to DAG-based leader election weights

**Recommendation**: Adopt a **Mysticeti-variant DAG consensus** with PoC-weighted leader election, Narwhal-style data availability separation, and Block-STM parallel execution.

---

## 2. DAG Consensus Protocol Survey

### 2.1 Mysticeti (Sui) — Production Leader

The current state of the art for production DAG-BFT.

**Architecture**: Uncertified DAG — eliminates explicit block certification. Every validator proposes blocks every round (multi-proposer). Blocks reference previous round blocks via DAG edges.

**Key Innovation**: Novel commit rule allowing block commitment without extra certification delays.

| Metric | Value |
|--------|-------|
| Consensus commit | **390ms** (P50), 640ms finality |
| Mysticeti v2 (2025) | ~260ms improved, P95 at 90ms, P99 at 114ms |
| Throughput | 200,000-400,000 TPS |
| Message rounds | **3** (theoretical lower bound for DAG-BFT) |
| Validators | 106+ on Sui mainnet |
| Production since | August 2024 |

**Dual-path execution**:
- **Owned objects**: Bypass consensus entirely — near-instant confirmation
- **Shared objects**: Processed through Mysticeti but with optimized latency

**Mysticeti-FPC** (fast commit variant): 175,000 TPS at 0.5s latency.

### 2.2 Narwhal / Tusk / Bullshark — The Lineage

**Narwhal** (EuroSys 2022 Best Paper) — Data Availability Layer:
- **Core innovation**: Separates reliable data dissemination from transaction ordering
- Validators build a DAG of transaction certificates
- Can be paired with any consensus mechanism for ordering
- Tolerates asynchronous networks while maintaining high throughput

**Tusk** — Original ordering layer:
- Zero-message-overhead ordering on top of Narwhal DAG
- Fully asynchronous, no leader needed

**Bullshark** (CCS 2022) — Replaced Tusk:
- Partially synchronous with better latency
- 125,000 TPS at 2 seconds latency (50 parties)
- Supports fairness properties

| Configuration | Throughput | Latency |
|--------------|-----------|---------|
| Narwhal + HotStuff | 130,000 TPS | <2s |
| Narwhal + HotStuff (scaled) | 600,000 TPS | <2s |
| Bullshark | 125,000 TPS | ~2s |
| Under fault | 70,000 TPS | 8-10s |

**Key insight for QFC**: Separating data availability from ordering is critical for AI inference — large inference results should be disseminated reliably without blocking consensus ordering.

### 2.3 Block-STM (Aptos) — Parallel Execution Engine

Not a consensus protocol but an **execution engine** based on Software Transactional Memory.

**How it works**:
1. Transactions speculatively executed in parallel
2. Memory accesses recorded during execution
3. Post-execution validation detects read/write conflicts
4. Conflicting transactions aborted and re-executed
5. Preset block order resolves conflicts deterministically

| Workload | Throughput | Improvement vs Sequential |
|----------|-----------|--------------------------|
| Low contention | 160,000+ TPS | **17x** |
| High contention | 80,000+ TPS | **8x** |
| Worst case | ~30% penalty | Overhead from aborts |

**Relevance for QFC**: AI inference tasks are naturally low-contention (different models, inputs, miners). Expected improvement: close to 17x over sequential execution.

### 2.4 Shoal++ (NSDI 2025) — Current Frontier

The most recent advancement from Aptos Labs, Cornell, and UIUC.

| Metric | Value |
|--------|-------|
| Average commit latency | **4.5 message delays** (down from 10.5 in prior DAG-BFT) |
| Latency improvement | **60% reduction** over state of the art |
| Throughput | 100,000+ TPS, sub-second latency |
| vs Mysticeti | Outperforms in benchmarks (including failure-free) |

### 2.5 Other Protocols

**DAG-Rider**: Foundational round-based structured DAG protocol. Two-layer architecture (communication + ordering). Fully asynchronous but higher latency.

**Shoal**: Built on Bullshark, reduces non-leader block latency by interleaving two Bullshark instances.

**Sailfish** (2024): First DAG-BFT with leader vertex per round. Leader vertex commit at 3-delta latency, non-leader at 5-delta.

### 2.6 Avalanche Consensus — Different Paradigm

**Approach**: Metastable, probabilistic consensus via subsampled voting (Snow protocol family: Slush → Snowflake → Snowball → Avalanche).

| Metric | Value |
|--------|-------|
| Throughput | ~3,400 TPS |
| Confirmation | ~1.35 seconds |
| Safety model | Probabilistic (not deterministic BFT) |
| Message complexity | O(k) per node regardless of network size |

**Trade-off**: Much lower throughput than DAG-BFT (3,400 vs 100,000+ TPS), but scales to thousands of validators and degrades gracefully.

**Relevance for QFC**: Subsampled voting could be useful for off-chain agreement on subjective AI inference quality scores.

### 2.7 IOTA Tangle — Cautionary Tale

**Original**: DAG without blocks; each transaction references 2 previous "tips". Weighted random walk for tip selection.

**Outcome**: After years of "Coordicide" research to decentralize, IOTA **abandoned the Tangle** and adopted:
- Mysticeti consensus protocol (same as Sui)
- MoveVM smart contracts
- 50,000+ TPS with ~400ms finality

**Lesson**: Unstructured DAGs are extremely difficult to decentralize securely. **Structured DAG-BFT is the viable path.**

---

## 3. Performance Comparison

| Protocol | TPS | Consensus Latency | Finality | Msg Delays | Status |
|----------|-----|-------------------|----------|------------|--------|
| **Mysticeti v2** | 200K-400K | ~260ms | <500ms | 3 rounds | Sui mainnet |
| **Shoal++** | 100K+ | Sub-second | Sub-second | 4.5 avg | Aptos testing |
| **Bullshark** | 125K | ~2s | ~2s | ~10.5 avg | Replaced |
| **Narwhal+HotStuff** | 130K-600K | <2s | <2s | 5+ rounds | Replaced |
| **Sailfish** | ~100K est. | 3-5 delta | 3-5 delta | 3-5 | Research |
| **Block-STM** (exec only) | 160K+ | N/A | N/A | N/A | Aptos mainnet |
| **Avalanche** | ~3,400 | ~1.35s | ~1.35s | Probabilistic | C-Chain |
| **IOTA Rebased** | 50K+ | ~400ms | ~400ms | 3 (Mysticeti) | Mainnet 2025 |

---

## 4. Integrating DAG with QFC's PoC Scoring

### 4.1 PoC Dimensions → DAG Mechanics

QFC's scoring dimensions map naturally to DAG-based consensus:

| PoC Dimension | Weight | DAG Integration |
|--------------|--------|-----------------|
| **Stake** (30%) | Standard PoS weighting of validator votes in DAG rounds |
| **Compute** (20%) | Embed inference proof hashes in DAG vertices; verified asynchronously |
| **Uptime** (15%) | **Free in DAG-BFT**: measure blocks proposed per round. Missing rounds = lower score |
| **Validation accuracy** (15%) | Track validation results in DAG metadata; rolling window |
| **Network** (10%) | Measured by data availability (Narwhal-style certificate propagation speed) |
| **Storage** (5%) | Prove IPFS pin availability; reference CIDs in DAG blocks |
| **Reputation** (5%) | Aggregated from historical on-chain scoring |

**Key insight**: Uptime scoring is free in DAG-BFT — every validator proposes every round, so participation is directly measurable without additional probes.

### 4.2 PoC-Weighted Leader Election

Replace pure stake-weighted leader election with composite PoC score:

```
leader_weight(validator) =
    stake_score * 0.30 +
    compute_score * 0.20 +
    uptime_score * 0.15 +
    validation_score * 0.15 +
    network_score * 0.10 +
    storage_score * 0.05 +
    reputation_score * 0.05
```

In a Mysticeti-style DAG:
- All validators propose blocks every round (multi-proposer)
- Leader selection for commit rule is weighted by PoC score
- Higher PoC score → higher probability of being commit leader → more influence on ordering
- This preserves decentralization (everyone proposes) while rewarding contribution

### 4.3 AI Inference Proofs in DAG Vertices

Each DAG vertex (block) contains:

```
DAGVertex {
    // Standard consensus fields
    round: u64,
    author: ValidatorId,
    parents: Vec<VertexDigest>,     // References to previous round

    // Transaction payload
    transactions: Vec<Transaction>,

    // AI inference commitments
    inference_proofs: Vec<InferenceProofCommitment> {
        task_id: Hash,
        model_hash: Hash,
        input_hash: Hash,
        output_hash: Hash,
        compute_time_ms: u64,
        ipfs_cid: Option<String>,   // For results >1MB
        zk_proof: Option<Vec<u8>>,  // Optional ZK proof (see doc #20)
    },

    // PoC score updates
    poc_updates: PoCScoreDeltas {
        compute_contribution: u64,
        validation_results: Vec<ValidationResult>,
        storage_proofs: Vec<StorageProof>,
    },
}
```

### 4.4 Dual-Path for AI Tasks

Borrowing from Sui's owned/shared object pattern:

| Task Type | Consensus Path | Latency |
|-----------|---------------|---------|
| **Private inference** (single user) | Fast path — skip consensus | Sub-second |
| **Public inference** (TaskPool) | Full consensus — shared state | ~500ms |
| **Inference verification** | Asynchronous — piggyback on DAG | Background |
| **PoC score updates** | Embedded in DAG vertices | Per-round |

---

## 5. Proposed Architecture: QFC-DAG

### 5.1 Three-Layer Design

```
┌─────────────────────────────────────────────────┐
│ Layer 3: Parallel Execution (Block-STM inspired) │
│   Optimistic parallel tx execution               │
│   AI inference tasks = low contention = fast      │
├─────────────────────────────────────────────────┤
│ Layer 2: Ordering (Mysticeti/Shoal++ inspired)   │
│   DAG-BFT with 3-round commit                    │
│   PoC-weighted leader election                   │
│   Dual-path: fast (private) vs consensus (shared) │
├─────────────────────────────────────────────────┤
│ Layer 1: Data Availability (Narwhal inspired)     │
│   Reliable dissemination of tx batches            │
│   AI inference results via IPFS CID references    │
│   Separate from ordering for throughput           │
└─────────────────────────────────────────────────┘
```

### 5.2 Block Production Flow

```
Round N:
  1. Each validator collects pending transactions and inference proofs
  2. Validator creates DAG vertex referencing ≥2f+1 vertices from round N-1
  3. Vertex includes: tx batch + inference proof commitments + PoC deltas
  4. Vertex broadcast to all validators (Narwhal-style reliable broadcast)

Round N+1:
  5. Validators reference round N vertices
  6. If round N has a commit-eligible leader (PoC-weighted selection):
     → Commit leader's causal history (all reachable vertices)
     → Execute committed transactions in parallel (Block-STM)

Round N+2:
  7. Third round confirms commit (3-round Mysticeti rule)
  8. Finalized transactions applied to state
  9. PoC scores updated based on this round's contributions
```

### 5.3 Expected Performance

| Metric | Current QFC (PoC) | QFC-DAG (Proposed) | Improvement |
|--------|-------------------|-------------------|-------------|
| Consensus latency | ~seconds (est.) | **<500ms** | 2-5x |
| Throughput | Limited by serial exec | **100K-200K TPS** | 10-50x |
| Finality | Multi-round | **<1 second** | 3-5x |
| AI task parallel exec | Sequential | **Block-STM parallel** | ~17x |

---

## 6. Avalanche Sampling for Subjective Scores

For non-deterministic AI quality scoring (text generation quality, image aesthetics), use Avalanche-style subsampled voting:

```
1. Multiple validators evaluate inference output quality
2. Each validator scores independently (0-100)
3. Snowball protocol: sample k=20 validators repeatedly
4. If α=14/20 agree on score range → converge
5. Final score used for miner reputation
```

This avoids the overhead of all-to-all communication for subjective quality metrics while reaching probabilistic consensus efficiently.

---

## 7. Implementation Roadmap

### Phase 1: Narwhal-Style Data Availability (4-6 weeks)

| Task | Description |
|------|-------------|
| DAG vertex structure | Define vertex format with inference proof commitments |
| Reliable broadcast | Implement Narwhal-style certificate-based dissemination |
| IPFS integration | Large inference results referenced by CID in vertices |
| Separate DA from ordering | DA layer runs independently of consensus ordering |

### Phase 2: Mysticeti-Variant Consensus (6-8 weeks)

| Task | Description |
|------|-------------|
| DAG construction | Round-based structured DAG with parent references |
| Commit rule | 3-round uncertified DAG commit (Mysticeti) |
| PoC-weighted leader | Leader election weighted by composite PoC score |
| Dual-path execution | Fast path for private tasks, consensus for shared |

### Phase 3: Block-STM Parallel Execution (4-6 weeks)

| Task | Description |
|------|-------------|
| STM execution engine | Optimistic parallel execution with conflict detection |
| AI task optimization | Inference verification tasks parallelized |
| Benchmark | Measure actual TPS improvement on inference workloads |

### Phase 4: Refinement (4-6 weeks)

| Task | Description |
|------|-------------|
| Snowball sampling | Subjective quality scoring for non-deterministic tasks |
| Performance tuning | Optimize for QFC's specific workload mix |
| Migration plan | Upgrade path from current PoC to QFC-DAG |

---

## References

- [Mysticeti Paper (NDSS 2025)](https://www.ndss-symposium.org/wp-content/uploads/2025-929-paper.pdf)
- [Mysticeti on Sui Blog](https://blog.sui.io/mysticeti-consensus-reduce-latency/)
- [Narwhal and Tusk (arXiv)](https://arxiv.org/abs/2105.11827)
- [Bullshark Paper (arXiv)](https://arxiv.org/pdf/2201.05677)
- [Block-STM on Aptos](https://medium.com/aptoslabs/block-stm-how-we-execute-over-160k-transactions-per-second-on-the-aptos-blockchain-3b003657e4ba)
- [Block-STM Paper (arXiv)](https://arxiv.org/abs/2203.06871)
- [Shoal++ (NSDI 2025)](https://www.usenix.org/conference/nsdi25/presentation/arun)
- [Shoal++ Paper (arXiv)](https://arxiv.org/abs/2405.20488)
- [Sailfish Paper (ePrint)](https://eprint.iacr.org/2024/472)
- [Avalanche Whitepaper](https://ipfs.io/ipfs/QmUy4jh5mGNZvLkjies1RWM4YuvJh5o2FYopNPVYwrRVGV)
- [IOTA Tangle to Rebased Analysis](https://www.mdpi.com/1424-8220/25/11/3408)
- [IOTA Rebased Mainnet](https://blog.iota.org/iota-rebased-fast-forward/)
- [DAG Meets BFT (Decentralized Thoughts)](https://decentralizedthoughts.github.io/2022-06-28-DAG-meets-BFT/)
- [SoK: DAG-based Consensus (arXiv 2025)](https://arxiv.org/abs/2411.10026)
