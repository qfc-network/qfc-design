# zkML: Zero-Knowledge Proofs for AI Inference Verification

> Last Updated: 2026-03-08 | Version 1.0
> GitHub Issue: #1

---

## 1. Executive Summary

QFC currently verifies AI inference via **5% spot-check re-execution** — randomly re-running 5% of proofs and comparing output hashes. zkML could provide mathematical verification guarantees without re-execution.

**Key Findings:**

- zkML has made dramatic progress: GPT-2 proof time dropped from **>1 hour (2024) to <25 seconds (2025)**
- Small models (<1B params) are **production-ready** for zkML today (seconds to prove)
- Large models (7B+) remain impractical for full ZK — 150 seconds/token for LLaMA-3
- **Optimistic ZK hybrid** is the emerging industry consensus: optimistic execution + ZK only on dispute
- QFC should adopt a **tiered verification strategy**: full ZK for small models, hybrid for medium, spot-check for large

**Recommendation**: Don't replace spot-check entirely. Layer zkML on top as a tiered system based on model size.

---

## 2. Major zkML Projects

### 2.1 Production-Ready Frameworks

| Project | Proof System | Approach | Key Benchmark | Maturity |
|---------|-------------|----------|---------------|----------|
| **EZKL** | Halo2 (zkSNARK) | ONNX → Halo2 circuits | 65.88x faster than RISC Zero, GPU support | Most mature general-purpose zkML |
| **Remainder** (Modulus Labs) | GKR protocol | Custom GKR optimized for AI | 180x efficiency vs traditional; 100K+ proofs on Ethereum mainnet | Production on Ethereum |
| **zkPyTorch** (Polyhedra) | Expander backend | PyTorch → ZK circuits | **VGG-16 in 2.2 seconds** | Released March 2025 |
| **DeepProve** (Lagrange) | Custom | Full computation graph proving | First full GPT-2 proof; extended to Gemma-3 | Released Aug 2025 |

### 2.2 Specialized LLM Provers

| Project | Target | Key Benchmark | Status |
|---------|--------|---------------|--------|
| **zkGPT** | GPT-family LLMs | GPT-2 full proof in **<25 seconds** (279x speedup over prior art) | USENIX Security 2025 |
| **zkLLM** | Large LLMs | **13B model in <15 minutes**, proof size <200KB | ACM CCS 2024, benchmark stage |
| **zkPyTorch** | General PyTorch | LLaMA-3 at 150 sec/token | March 2025 |

### 2.3 Alternative Approaches

| Project | Approach | Key Benefit | Trade-off |
|---------|----------|-------------|-----------|
| **OPml** (ORA Protocol) | Optimistic fraud proofs (not ZK) | **~0 overhead** for happy path; supports 7B+ on consumer PCs | Economic security, not mathematical; challenge period adds latency |
| **RISC Zero** | General zkVM (RISC-V) | Supports any computation | 65.88x slower than EZKL for ML; generic = expensive |
| **Giza/Orion** | Cairo/StarkNet STARKs | StarkNet-native | 2.92x slower than EZKL; failed on 1TB RAM for some models |

---

## 3. Performance Benchmarks

### 3.1 Proof Generation Time

| Model | Parameters | Framework | Proving Time | Inference Time | Overhead |
|-------|-----------|-----------|-------------|----------------|----------|
| VGG-16 | 138M | zkPyTorch | **2.2 seconds** | ~5ms | ~440x |
| ResNet-18 | 11M | EZKL | ~seconds | ~2ms | ~500x |
| GPT-2 | 1.5B | zkGPT | **<25 seconds** | ~100ms | ~250x |
| GPT-2 | 1.5B | ZKML (2024) | ~3,652 seconds | ~100ms | ~36,500x |
| 13B LLM | 13B | zkLLM | **<15 minutes** | ~seconds | ~100-500x |
| LLaMA-3 8B | 8B | zkPyTorch | **150 sec/token** | ~50ms/tok | ~3,000x |
| 7B LLaMA | 7B | OPml | **~0 (happy path)** | ~50ms/tok | ~0x |

**Trend**: Overhead dropped from 10,000x (2023) → 500x (2024) → 100-500x (2025), improving rapidly.

### 3.2 Proof Size

| System | Proof Size | Notes |
|--------|-----------|-------|
| Groth16 (generic) | **256 bytes** fixed | Gold standard for compactness |
| zkLLM (13B model) | **<200 KB** | Very compact for model size |
| ResNet-18 (EZKL) | ~15.3 KB | Small model |
| ResNet-50 (folding-based) | <100 KB | 10,000x improvement over pre-folding (~1.27 GB) |
| EZKL (Halo2) | 15.75x larger than Groth16 | Verification keys can reach 4.2 MB |

### 3.3 On-Chain Verification Cost

| Verification Method | Gas Cost | USD (at 30 gwei) |
|--------------------|----------|-------------------|
| Groth16 on-chain | ~220,000 gas | ~$0.50-2.00 |
| EZKL (Halo2) | 173x more pairings than Groth16 | Significantly more expensive |
| L2 (Arbitrum) | — | <$0.004 |
| L2 (Optimism, EIP-4844) | — | <$0.001 |
| Late 2025 average | — | ~$0.02 for some tasks |

### 3.4 Prover Hardware Requirements

| Framework | Minimum | Production |
|-----------|---------|------------|
| EZKL (small models) | 16 GB RAM, 8-core CPU | A10/A100 GPU, 32GB+ VRAM |
| zkPyTorch (VGG-16) | <8 GB RAM | Laptop feasible |
| RISC Zero | Very high (98% more RAM than EZKL) | Server-class |
| Orion/Giza | Very high | Failed on 1TB RAM for some models |

---

## 4. Technical Approaches Compared

### 4.1 zkSNARK vs zkSTARK for ML

| Property | zkSNARK | zkSTARK |
|----------|---------|---------|
| Proof size | **Small** (256B for Groth16) | Large (KB to MB) |
| Verification cost | **Low** (~220K gas) | Higher |
| Trusted setup | Required (Groth16) or not (Halo2) | **Not required** |
| Quantum resistance | No | **Yes** |
| Prover speed | Generally slower | Generally faster for large circuits |
| ML suitability | **Better** (on-chain verification cost) | Better for prover scalability |

**Industry consensus**: Most production zkML uses SNARKs (EZKL/Halo2, Remainder/GKR, zkGPT) because on-chain verification cost matters.

### 4.2 Optimistic ML (OPml) vs ZK

| Property | zkML | OPml |
|----------|------|------|
| Security | **Mathematical** | Economic (staking + fraud proofs) |
| Max model size | ~13B (zkLLM) | **Unlimited** (7B+ on consumer HW) |
| Overhead (happy path) | 100-500x | **~0x** |
| Finality | **Immediate** upon proof verification | Challenge period (hours to days) |
| Cost per inference | $0.02 - $100+ | **Near-zero** |

### 4.3 Hybrid "Optimistic ZK" (2026 Emerging Pattern)

The industry is converging on: **optimistic execution for 99% of inferences, ZK proof only for the disputed step**.

- Low cost of OPml for happy path
- Mathematical trustlessness of ZK for disputes
- **Optimistic TEE-Rollups (OTR)**: Add TEE attestation as middle layer. Claims 1400x speedup over pure zkML and 99% latency reduction vs pure OPml

---

## 5. The "zkML Singularity" (Late 2025)

Three converging advances "conquered" the Transformer architecture:

1. **Improved polynomial commitment schemes** — faster prover for large circuits
2. **tlookup** — parallelized lookup argument for non-linear operations (ReLU, Softmax, GELU), eliminating the bit-decomposition bottleneck
3. **System-level engineering** — frameworks like DeepProve supporting arbitrary computation graphs, not just sequential layer stacks

### Key Milestones Timeline

| Date | Milestone | Impact |
|------|-----------|--------|
| Feb 2025 | Remainder (Modulus Labs) production launch | 180x improvement, 100K+ proofs on Ethereum |
| Mar 2025 | zkPyTorch — VGG-16 in 2.2s | CNN-class models become practical |
| Apr 2025 | R0VM 2.0 — 44-second Ethereum block proofs | General zkVM catches up |
| Aug 2025 | DeepProve — first full GPT-2 proof | LLM barrier broken |
| Oct 2025 | Pico Prism — real-time block proving on GPU clusters | Infrastructure ready |
| Late 2025 | zkGPT — GPT-2 in <25 seconds | 279x speedup, LLM proving now practical |

---

## 6. Implications for QFC

### 6.1 Current Verification Architecture

```
Miner submits proof → Basic checks (all proofs)
                         ├── Timestamp freshness (120s max)
                         ├── Model approval check
                         ├── Output hash validation
                         └── FLOPS claim reasonableness
                     → Spot-check (5% of proofs)
                         ├── Re-execute via InferenceEngine
                         ├── Compare output hash
                         └── On mismatch: slash 5% stake, 6h jail
```

### 6.2 Recommended: Tiered Verification Strategy

| Tier | Model Size | Verification Method | Rationale |
|------|-----------|-------------------|-----------|
| **Tier 1** | <1B params (embeddings, classification, small LLMs) | **Full zkML proof every inference** | Proving time is seconds; cost ~$0.02; mathematical guarantee |
| **Tier 2** | 1-13B params (medium LLMs) | **Optimistic + ZK on challenge** | Proving takes minutes; use optimistic execution, generate ZK proof only if disputed |
| **Tier 3** | 13B+ params (large LLMs) | **Current spot-check re-execution** | ZK proving still impractical; spot-check + staking/slashing remains best option |

### 6.3 Tier 1: Full zkML (Small Models)

QFC's current small models (qfc-embed-small, qfc-embed-medium, qfc-classify-small, qfc-llm-0.5b) are all <1B params and perfect candidates for full zkML.

**Integration approach**:
- Miner runs inference and generates ZK proof using EZKL or zkPyTorch
- Proof is submitted alongside InferenceProof
- Validator verifies the ZK proof on-chain (or off-chain with on-chain settlement)
- No need for spot-check re-execution — mathematical guarantee

**Estimated overhead**:
- qfc-embed-small (80MB, 22M params): proof in ~1 second
- qfc-embed-medium (120MB, 110M params): proof in ~2-5 seconds
- qfc-classify-small (440MB, BERT-base): proof in ~5-15 seconds
- qfc-llm-0.5b (990MB, 0.5B params): proof in ~15-30 seconds

### 6.4 Tier 2: Optimistic ZK (Medium Models)

For 7B-13B models (future QFC model registry):

```
1. Miner executes inference (normal speed)
2. Miner stakes collateral with the result
3. Challenge window opens (e.g., 30 minutes)
4. If challenged:
   a. Challenger stakes collateral
   b. Miner generates ZK proof (takes minutes)
   c. Proof verified on-chain
   d. Loser forfeits stake to winner
5. If not challenged: result finalized after window
```

This mirrors optimistic rollup design but for AI inference.

### 6.5 Tier 3: Enhanced Spot-Check (Large Models)

For 70B+ models, maintain current approach but enhance:
- Increase spot-check rate for new/low-reputation miners (already implemented: 10% for new, 8% for low rep, 5% standard)
- Add TEE attestation as optional middle layer (see doc #19)
- Redundant execution across 2-3 miners for high-value tasks

### 6.6 Implementation Considerations

**Framework choice for QFC**:
- **EZKL** is the safest bet: most mature, ONNX support (QFC already has OnnxInference), GPU acceleration
- **zkPyTorch** for PyTorch-native models if moving beyond ONNX
- **Remainder (GKR)** if QFC wants to optimize for Ethereum-like on-chain verification

**New ComputeTaskType variant**:
```rust
// Addition to existing enum
ComputeTaskType::VerifiedInference {
    model_id: ModelId,
    input_hash: Hash,
    zk_proof: Vec<u8>,          // The ZK proof bytes
    proof_system: ProofSystem,  // EZKL, Groth16, etc.
}
```

**Gas/fee implications**:
- Miners incur ZK proving cost → need higher fee for Tier 1 verified inference
- Users pay premium for mathematical guarantee vs statistical (spot-check) guarantee
- Estimated premium: 2-5x base fee for Tier 1, 1.2-1.5x for Tier 2

---

## 7. Competitive Positioning

| Project | Verification Method | Max Model Size | Finality |
|---------|-------------------|----------------|----------|
| Bittensor | Subjective validator scoring | Unlimited | Immediate (but gameable) |
| ORA Protocol | OPml fraud proofs | 7B+ | Challenge period |
| Ritual | TEE attestation | Unlimited | Immediate |
| Modulus/Remainder | Full zkML (GKR) | ~1B practical | Immediate |
| Giza | zkSTARK (Cairo) | Small models | Immediate |
| **QFC (target)** | **Tiered: zkML + OPml + spot-check** | **Unlimited** | **Immediate (Tier 1) / Challenge (Tier 2) / Statistical (Tier 3)** |

QFC's tiered approach is more pragmatic than any single-method competitor. It provides the strongest guarantees where feasible (small models), reasonable guarantees for medium models, and practical guarantees for large models.

---

## 8. Implementation Roadmap

### Phase 1: zkML for Embedding Models (3-4 weeks)

| Task | Description |
|------|-------------|
| Integrate EZKL | Add EZKL as optional dependency in qfc-inference |
| Proof generation | Miner generates ZK proof for embedding tasks |
| Proof verification | Validator verifies ZK proof instead of spot-check |
| Fee adjustment | Tier 1 verified inference pricing |

### Phase 2: Optimistic ZK for Medium Models (6-8 weeks)

| Task | Description |
|------|-------------|
| Challenge protocol | On-chain challenge/response mechanism |
| Stake management | Collateral for optimistic execution |
| ZK dispute resolution | Generate and verify ZK proof on challenge |
| Timeout handling | Auto-slash if miner fails to produce proof |

### Phase 3: Unified Verification Framework (4-6 weeks)

| Task | Description |
|------|-------------|
| Auto-tier selection | Determine verification tier from model size |
| Proof system abstraction | Support multiple proof systems (EZKL, Groth16, GKR) |
| SDK support | qfc-sdk-js/python for verified inference requests |
| Dashboard | Explorer shows verification method per task |

---

## References

- [The Definitive Guide to ZKML (2025) - ICME](https://blog.icme.io/the-definitive-guide-to-zkml-2025/)
- [The zkML Singularity - Extropy Academy](https://academy.extropy.io/pages/articles/zkml-singularity.html)
- [Benchmarking ZKML Frameworks - EZKL Blog](https://blog.ezkl.xyz/post/benchmarks/)
- [State of EZKL: 2025](https://blog.ezkl.xyz/post/state_of_ezkl/)
- [DeepProve-1 - Lagrange](https://lagrange.dev/blog/deepprove-1)
- [opML - ORA Documentation](https://docs.ora.io/doc/onchain-ai-oracle-oao/fraud-proof-virtual-machine-fpvm-and-frameworks/opml)
- [zkLLM Paper - arXiv](https://arxiv.org/abs/2404.16109)
- [zkPyTorch - Polyhedra Network](https://polyhedra.network/zkPyTorch)
- [zkGPT Paper - USENIX Security 2025](https://www.usenix.org/system/files/usenixsecurity25-qu-zkgpt.pdf)
- [Groth16 Verification Gas Cost](https://hackmd.io/@nebra-one/ByoMB8Zf6)
- [Optimistic TEE-Rollups - arXiv](https://arxiv.org/html/2512.20176)
- [Introduction to ZKML - Worldcoin](https://world.org/blog/engineering/intro-to-zkml)
