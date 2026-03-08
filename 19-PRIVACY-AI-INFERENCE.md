# Privacy-Preserving AI Inference: Technology Research & QFC Strategy

> Last Updated: 2026-03-08 | Version 1.0
> GitHub Issue: #2

---

## 1. Executive Summary

QFC miners execute AI inference tasks for users. When users submit sensitive data (medical records, business secrets, personal info), the inputs must be protected from miners, validators, and other network participants.

This report evaluates four privacy-preserving approaches: TEE, FHE, MPC, and hybrid combinations.

**Key Findings:**

- **TEE (GPU) is the only production-ready path** for large model inference (7B+ parameters) with <5% overhead
- FHE remains 100-1000x slower than plaintext — impractical for interactive LLM workloads today
- MPC is 10-100x slower and 93% of overhead comes from non-linear layers (ReLU)
- **Hybrid TEE+ZK is the best near-term strategy**: TEE for speed, ZK for trustless verification
- NVIDIA Blackwell B200 achieves **near-zero overhead** for confidential AI — a game-changer

**Recommendation for QFC:**
1. **Phase 1**: NVIDIA GPU TEE (H100/B200) for confidential inference
2. **Phase 2**: Hybrid MPC+TEE for highest-sensitivity inputs
3. **Phase 3**: Monitor FHE acceleration for future trustless inference

---

## 2. Technology Overview

### 2.1 TEE (Trusted Execution Environments)

Hardware-isolated secure enclaves that protect code and data during execution.

#### Hardware Landscape

| Hardware | Vendor | Level | Status | Notes |
|----------|--------|-------|--------|-------|
| **Intel SGX** | Intel | Process | **Deprecated** (consumer since 2021) | WireTap attack (2025 ACM CCS) extracted attestation keys with <$1K equipment |
| **Intel TDX** | Intel | VM | Production (Xeon Sapphire Rapids) | SGX successor; Google Cloud GA on C3 series |
| **AMD SEV-SNP** | AMD | VM | Production (EPYC Genoa/Milan) | Most widely deployed; pairs with NVIDIA GPU TEE |
| **ARM CCA** | ARM | VM | Early stage | "Realm" concept with Granule Protection Table |
| **NVIDIA H100** | NVIDIA | GPU | **Production** | First GPU TEE; on-die root of trust |
| **NVIDIA B200** | NVIDIA | GPU | **Shipping** (Feb 2026) | TEE-I/O via NVLink; near-zero overhead |

#### NVIDIA GPU TEE Performance

| Model | H100 Overhead | B200 Overhead | Notes |
|-------|--------------|---------------|-------|
| LLaMA-3.1-8B | ~5-7% | ~0% | ~130 TPS with medium inputs on H100 |
| LLaMA-3.1-70B | ~0% (trivial) | ~0% | Overhead amortized by compute |
| General LLM inference | <5% average | Near-zero | PCIe bounce buffer is main H100 bottleneck |

**B200 Breakthrough**: TEE-I/O capability with inline NVLink encryption eliminates the PCIe bottleneck that caused H100's overhead. Preserves 2x training and 2.5x inference advantage over H200 even with confidential computing enabled.

#### Blockchain Projects Using TEE

**Phala Network** (most mature TEE-blockchain integration):
- Processed **1.34B LLM tokens in a single day**
- Production overhead: 0.5-5%
- Live on OpenRouter for confidential LLM inference
- Migrating from SGX → Intel TDX + NVIDIA GPU TEE (post-WireTap)
- Supports H100 and B200

**Oasis Protocol**:
- Sapphire: first confidential EVM in production
- ROFL (Runtime Offchain Logic) framework for offchain apps with onchain trust

**Secret Network**:
- Pivoting to confidential AI with Secret AI SDK
- SecretVM for confidential workloads
- 2026: multi-cloud support (Azure, GCP, AWS)

**iExec**:
- Healthcare PoC: epilepsy surgery evaluation on encrypted EEG data using Intel TDX
- Listed in Intel's AI Inference Solutions Catalogue

#### Trust Assumptions

- **Must trust hardware vendor** (Intel, AMD, NVIDIA) for correct implementation
- Side-channel attacks remain a concern (WireTap on SGX, Spectre-class on TDX)
- Attestation provides cryptographic proof of enclave identity and integrity
- "Trust but verify" model — attestation helps but doesn't eliminate hardware trust

---

### 2.2 FHE (Fully Homomorphic Encryption)

Compute on encrypted data without ever decrypting it. Mathematically proven privacy.

#### Key Projects

**Zama (Concrete ML, fhEVM)**:
- Open-source TFHE compiler (Python → FHE via LLVM)
- ML framework compatible with scikit-learn and PyTorch
- Supported: MLP, CNN, Transformers (sentiment analysis demonstrated)
- fhEVM: FHE-enabled EVM for confidential smart contracts

**Inco Network**:
- Modular confidential computing L1 blockchain
- Combines FHE (TFHE), ZK, TEE, MPC
- Lattice-based cryptography (NIST post-quantum endorsed)
- Roadmap: FPGA acceleration targeting 100-1000 TPS

**Sunscreen**:
- Rust-based FHE compiler ecosystem
- Developer-friendly abstractions

#### Performance Reality

| Benchmark | Performance |
|-----------|------------|
| General overhead vs plaintext | **100-1000x+ slowdown** |
| CIFAR-10 CNN inference | ~4 minutes per image (88.7% accuracy) |
| Bootstrapping latency | <1ms (down from 50ms in 2021 — major breakthrough) |
| GPU-accelerated FHE | 150-200x faster than CPU baseline |
| LLM inference | **Impractical** — seconds to minutes per token |

#### Feasibility by Model Type

| Feasibility | Model Types |
|-------------|-------------|
| **Feasible today** | Logistic regression, decision trees, small MLPs, small CNNs, sentiment classification |
| **Emerging** | Medium CNNs (ResNet-scale with hybrid), small transformers |
| **Not feasible** | Full LLM inference (GPT/LLaMA-scale), large vision models |

---

### 2.3 MPC (Multi-Party Computation)

Split computation across multiple parties so no single party sees the full data.

#### Key Projects

**Partisia Blockchain**:
- Founded by MPC pioneers
- Biometric data storage and matching without decryption
- Generic confidential smart contracts with MPC

**Nillion**:
- "Blind computation" network
- Modules: nilDB (secure database), nilAI (secure LLM), nilVM (decentralized signing)
- **Fission project (with Meta)**: fuses MPC + TEE, achieves near production-ready throughput

**Secret Network**:
- Originally MPC-focused, now pivoting to TEE-based confidential computing

#### Performance Benchmarks

| Task | MPC Time | TEE Time | Slowdown |
|------|----------|----------|----------|
| MNIST inference | 0.321s (optimized FSS) | ~instant | ~300x |
| CIFAR-10 inference | 3.695s (optimized) | ~instant | ~3700x |
| ResNet-18 | 148s | 8.15s | **18x** |

- **93% of MPC overhead comes from ReLU** (non-linear) layers
- Communication overhead grows linearly with network depth
- Semi-honest model predominates (assumes parties follow protocol)

#### Trust Model

- **Strongest trust model**: No single party sees the data
- No hardware trust required (pure cryptography)
- Trade-off: significantly worse performance

---

### 2.4 Hybrid Approaches

| Combination | Description | Status | Key Project |
|-------------|-------------|--------|-------------|
| **TEE + ZK** | TEE executes at native speed; ZK proves correctness | Early production | Phala Network |
| **MPC + TEE** | MPC for input privacy; TEE for fast compute | Prototype | Nillion Fission (with Meta) |
| **FHE + MPC** | Encrypted collaborative computation | Prototype | Arcium (mainnet alpha) |
| **ZK + FHE + TEE** | Full stack privacy | Research | Mind Network |

**TEE + ZK** is the most production-ready hybrid:
- TEE provides near-native inference speed
- ZK proves the TEE executed correctly (reducing hardware trust assumption)
- "TEE's performance with ZK's trustless verification"

**MPC + TEE (Nillion Fission)**:
- User inputs secret-shared via MPC (no single party sees raw data)
- Intermediate results (obfuscated, non-reversible) transferred to TEE
- Near production-ready throughput for certain models
- Validated through collaboration with Meta

---

## 3. Comparison Matrix

| Dimension | TEE (GPU) | FHE | MPC | Hybrid (TEE+ZK) |
|-----------|-----------|-----|-----|------------------|
| **Performance overhead** | **<5%** (H100), **~0%** (B200) | 100-1000x | 10-100x | ~5% |
| **Trust assumption** | Hardware vendor | **None** (math) | **None** (distributed) | Reduced (ZK verifies TEE) |
| **Hardware requirements** | Specific GPU (H100/B200) | Standard + FPGA | Standard, high bandwidth | TEE GPU + ZK prover |
| **Max model size** | **Unlimited** (70B+) | Small (MLP, small CNN) | Medium (ResNet) | **Unlimited** |
| **Latency** | **Near-native** | Minutes | Seconds-minutes | **Near-native** |
| **Maturity** | **Production** | Research/early | Research/limited | Early production |
| **Side-channel risk** | Yes (mitigated) | **None** | **None** | Reduced |
| **Input privacy** | From software, not hardware vendor | **Complete** | **Complete** | Strong |
| **Post-quantum ready** | Needs PQ key exchange | **Yes** (lattice-based) | Needs PQ key exchange | Partial |

---

## 4. Implications for QFC

### 4.1 Current State

QFC miners use consumer GPUs (RTX 3060-4080) and CPU backends. The miner network is permissionless — anyone with a GPU can mine. Currently, there is no privacy protection for inference inputs.

### 4.2 Challenges Specific to QFC

1. **Consumer GPU miners don't have TEE**: NVIDIA GPU TEE requires H100/B200 (data center GPUs)
2. **Verification conflict**: QFC's spot-check re-execution requires seeing the input — incompatible with encrypted inference
3. **Heterogeneous hardware**: Miners have diverse hardware; privacy solution must work across tiers
4. **Cost sensitivity**: Privacy overhead must not price out users

### 4.3 Recommended Strategy

#### Phase 1: Confidential Inference Tier (Near-term)

Introduce a **Confidential Miner** tier alongside existing Cold/Warm/Hot tiers:

```
GPU Tier System:
  Cold   → Consumer GPU (RTX 3060, 8GB) — No privacy
  Warm   → Consumer GPU (RTX 4070, 12GB) — No privacy
  Hot    → Data center GPU (A100, 80GB) — No privacy
  Secure → Data center GPU with TEE (H100/B200) — Confidential
```

- Users who need privacy pay a premium to route tasks to `Secure` tier miners
- Secure miners must provide TEE attestation during registration
- Standard (non-private) tasks continue on consumer GPUs at lower cost
- **This is a market segmentation play**: privacy as a premium feature

#### Phase 2: Hybrid Verification for Confidential Tasks

The spot-check re-execution model doesn't work when inputs are encrypted. Alternative verification approaches:

| Method | Description | Trade-off |
|--------|-------------|-----------|
| **TEE attestation only** | Trust the TEE executed correctly | Relies on hardware trust |
| **TEE + ZK proof** | TEE generates a ZK proof of correct execution | Higher cost, strongest guarantee |
| **Redundant TEE execution** | Run on 2-3 independent TEE miners, compare outputs | Higher cost, no single-point trust |
| **Challenge protocol** | Inject known test tasks into confidential pipeline | Catches lazy/dishonest miners |

**Recommendation**: Start with **TEE attestation + challenge protocol** (simplest), evolve to **TEE + ZK** as the technology matures.

#### Phase 3: Consumer GPU Privacy (Long-term)

For enabling privacy on consumer GPUs (no TEE):

- **Input splitting**: Split sensitive inputs across 2-3 miners using secret sharing (lightweight MPC)
- **Partial FHE**: Encrypt only the sensitive portion of input (e.g., encrypt the medical data, leave the model prompt in plaintext)
- Monitor FHE hardware acceleration progress (FPGA/ASIC)

### 4.4 Architecture Sketch

```
User submits confidential task:
    ↓
Task Router (checks privacy flag)
    ├── privacy=false → Standard miner pool (existing flow)
    └── privacy=true  → Confidential miner pool
                           ↓
                        TEE Attestation Check
                           ↓
                        Encrypted input transfer (TLS to enclave)
                           ↓
                        Inference inside TEE (H100/B200)
                           ↓
                        Output encrypted back to user
                           ↓
                        Verification:
                           ├── TEE attestation log (always)
                           ├── Challenge injection (5-10%)
                           └── ZK proof (future)
```

### 4.5 Smart Contract Integration

Using QVM's Resource types for confidential inference:

```
// Confidential inference result — can only be consumed by the task submitter
resource ConfidentialResult {
    task_id: Hash,
    encrypted_output: Bytes,    // Encrypted to submitter's public key
    tee_attestation: Bytes,     // Hardware attestation proof
    miner: Address,
}
```

- The `ConfidentialResult` Resource ensures the encrypted output is consumed exactly once
- TEE attestation is stored on-chain for auditability
- Cross-VM: Solidity contracts can verify attestation, QSC contracts hold the Resource

---

## 5. Competitive Positioning

| Project | Privacy Approach | AI Model Support | On-Chain Composability |
|---------|-----------------|------------------|----------------------|
| **Phala** | TEE (H100/B200) | LLM (any size) | Limited (offchain compute) |
| **Secret Network** | TEE + SecretVM | Emerging | Secret contracts only |
| **Nillion** | MPC + TEE hybrid | Medium models | No smart contracts |
| **Oasis** | TEE (Sapphire) | Not AI-focused | Confidential EVM |
| **QFC (target)** | **TEE + ZK + Resource types** | **Any model (tiered)** | **Full AI+DeFi composability** |

QFC's differentiator: **Privacy-preserving AI inference with smart contract composability**. No existing project combines confidential AI compute with programmable on-chain logic.

---

## 6. Key 2025-2026 Developments

1. **NVIDIA B200 TEE-I/O**: Near-zero overhead confidential AI — the single biggest enabler
2. **FHE bootstrapping <1ms**: Down from 50ms in 2021; enables practical small-model FHE
3. **GPU-accelerated FHE**: 150-200x speedup; still not enough for LLMs but closing gap
4. **SGX WireTap attack**: Killed SGX, accelerated migration to TDX + GPU TEE
5. **Phala 1.34B tokens/day**: Proved production-scale confidential LLM inference is real
6. **Nillion Fission (with Meta)**: Validated MPC+TEE hybrid at near-production throughput

---

## References

- [NVIDIA H100 Confidential Computing Blog](https://developer.nvidia.com/blog/confidential-computing-on-h100-gpus-for-secure-and-trustworthy-ai/)
- [H100 CC Performance Benchmark Study](https://arxiv.org/html/2409.03992v1)
- [Confidential LLM Inference Performance Study](https://www.arxiv.org/pdf/2509.18886)
- [Phala GPU TEE Deep Dive](https://phala.com/posts/Phala-GPU-TEE-Deep-Dive)
- [Phala: AMD SEV vs Intel TDX vs NVIDIA GPU TEE](https://phala.com/learn/AMD-SEV-vs-Intel-TDX-vs-NVIDIA-GPU-TEE)
- [NVIDIA B200 Blackwell GPU TEE](https://phala.com/gpu-tee/b200)
- [Privacy Stack: ZK vs FHE vs TEE vs MPC](https://blockeden.xyz/blog/2026/01/27/privacy-infrastructure-zk-fhe-tee-mpc-comparison-benchmarks/)
- [Zama Concrete ML](https://docs.zama.org/concrete-ml)
- [Nillion Tech Roadmap 2025](https://nillion.com/news/nillions-tech-roadmap-2025-advancing-the-blind-computer/)
- [Partisia MPC Technology](https://www.partisia.com/tech/technology/)
- [Secret Network 2026 Roadmap](https://scrt.network/blog/secret-network-2026-roadmap)
- [Inco Network](https://www.inco.org/)
- [Arcium Mainnet Alpha](https://blockeden.xyz/blog/2026/02/12/arcium-mainnet-alpha-encrypted-supercomputer-solana/)
- [Google Cloud Confidential Computing for AI](https://cloud.google.com/blog/products/identity-security/how-confidential-computing-lays-the-foundation-for-trusted-ai)
