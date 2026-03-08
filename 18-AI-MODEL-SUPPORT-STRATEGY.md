# AI Model Support Strategy: What Models Should QFC Support?

> Last Updated: 2026-03-08 | Version 1.1
> GitHub Issue: #10
> Review: #11 (qfc-core implementation feedback incorporated)
> Author: Alex Wei, Product Manager @ QFC Network

---

## 1. Executive Summary

This document surveys the AI model landscape across decentralized inference platforms, analyzes consumer GPU feasibility, and recommends a tiered model support strategy for QFC.

**Key Findings:**

- **92.48% of HuggingFace downloads are for models under 1B parameters** — small models dominate real demand
- QFC's current registry (4 models, all <1B) is a good starting point but too narrow for market relevance
- Consumer GPUs (RTX 3060-4090) can comfortably run 7B-14B quantized models; 32B is feasible on high-end cards
- Enterprise demand concentrates on: LLM chatbots (38.91%), speech-to-text, embeddings, and image generation
- **Recommendation**: Expand to 15-20 models across 6 categories, mapped to QFC's Cold/Warm/Hot GPU tiers

---

## 2. Competitive Landscape: What Others Support

### 2.1 Bittensor (128 subnets)

| Subnet | Task | Popular Models |
|--------|------|---------------|
| SN1 | Text generation | DeepSeek V3 (dominates token usage) |
| SN4 | AI content detection | Deterministic verification models |
| SN17 | 3D generation | Gaussian Splatting, NeRF, 3D Diffusion |
| SN19 | Ultra-low-latency inference | Image + text combined |
| SN64 | Serverless AI compute | Any model (deploy freely) |

**Key insight**: Bittensor's open subnet model means any model can be supported. DeepSeek V3 dominates actual usage.

### 2.2 Ritual (Infernet)

- Supports **any ONNX, PyTorch, or HuggingFace model**
- LLM via TGI: LLaMA, Falcon, StarCoder, BLOOM, GPT-NeoX, T5
- No fixed model registry — nodes self-select which models to serve
- Also supports closed-source API calls (OpenAI GPT-4)

### 2.3 Akash Network

- Most popular: **GPT-OSS-120B, Qwen3-Next-80B, DeepSeek-V3.1**
- Common workloads: LLM inference, Whisper transcription, privacy-focused models
- Hardware: A100/H100, acquiring ~7,200 GB200 GPUs for 2026
- Enterprise clients rent dozens of GPUs for generative AI

### 2.4 Nosana

- Pre-loads models on nodes: LLaMA 2, Stable Diffusion
- Focused on Solana ecosystem

---

## 3. Model Landscape by Category (2025-2026)

### 3.1 LLMs (Text Generation)

| Model | Parameters | VRAM (Q4) | Key Strength |
|-------|-----------|-----------|--------------|
| **Qwen 2.5/3** | 0.5B-235B | 0.5-120 GB | Most downloaded on HF; multilingual, reasoning, code |
| **DeepSeek R1/V3** | 7B-671B | 4-340 GB | Reasoning, math; matches frontier at lower cost |
| **LLaMA 3/4** | 8B-405B | 5-200 GB | Multimodal, long context (128K) |
| **Mistral/Mixtral** | 7B-8x22B | 4-60 GB | MoE efficiency |
| **Phi-4** | 14B | 9 GB | Best instruction following |
| **Gemma 2** | 2B-27B | 1.5-16 GB | Google's efficient small models |
| **GPT-OSS 20B** | 20B | 12 GB | Fastest on 16GB VRAM (42 tok/s) |

### 3.2 Embedding Models

| Model | Parameters | VRAM | Strength |
|-------|-----------|------|----------|
| **all-MiniLM-L6-v2** | 22M | ~200 MB | Speed, efficiency (QFC already supports) |
| **all-MiniLM-L12-v2** | 33M | ~300 MB | Better quality (QFC already supports) |
| **BGE-M3** | 560M | ~4 GB | Multilingual, long-context retrieval |
| **E5-large-instruct** | 700M | ~5 GB | Best all-rounder |
| **all-mpnet-base-v2** | 110M | ~500 MB | Quality-speed balance |

### 3.3 Image Generation

| Model | VRAM | Notes |
|-------|------|-------|
| **Stable Diffusion 1.5** | 4-6 GB | Legacy but massive LoRA ecosystem |
| **Stable Diffusion XL** | 8 GB | Current mainstream |
| **FLUX.1** | 6 GB (NF4 quantized) - 24 GB (full) | State of the art quality |
| **FLUX-2** | 8 GB (group_offloading) - 24 GB | Latest generation |

### 3.4 Speech-to-Text

| Model | VRAM | Notes |
|-------|------|-------|
| **Whisper large-v3** | ~3 GB (fp16) | Most widely deployed ASR |
| **Faster-Whisper** | 40% less than Whisper | 4x faster, INT8 quantization |
| **MeloTTS** | CPU-capable | Can run without GPU |
| **XTTS v2** | ~2.7 GB | Voice cloning TTS |

### 3.5 Multimodal (Vision-Language)

| Model | VRAM (Q4) | Notes |
|-------|-----------|-------|
| **Qwen3-VL-2B** | 4 GB | Fits RTX 3060 |
| **Qwen3-VL-7B** | 8 GB | Fits RTX 4070 |
| **LLaVA-1.5/NeXT** | 8-16 GB | Visual instruction tuning |

### 3.6 Code Generation

| Model | Parameters | VRAM (Q4) | Notes |
|-------|-----------|-----------|-------|
| **Qwen 2.5 Coder 14B** | 14B | ~9 GB | Surpasses CodeStral-22B |
| **DeepSeek Coder V2 Lite** | 16B MoE (2.4B active) | ~6 GB | Very fast, memory-efficient |
| **CodeLlama 13B** | 13B | ~8 GB | Outperforms Copilot in 73% of tasks |

---

## 4. Consumer GPU Feasibility

### 4.1 GPU VRAM Reference

| GPU | VRAM | Price Range | Max Model (Q4) | QFC Tier |
|-----|------|-------------|-----------------|----------|
| RTX 3060 | 12 GB | $250-350 | 8B comfortable, 14B slow | Cold |
| RTX 3070 | 8 GB | $300-400 | 7-8B | Cold |
| RTX 3080 | 10 GB | $400-550 | 8B comfortable | Cold |
| RTX 4060 | 8 GB | $280-350 | 7-8B | Cold |
| RTX 4070 | 12 GB | $500-600 | 14B | Warm |
| RTX 4070 Ti Super | 16 GB | $700-800 | 14B fast, 32B slow | Warm |
| RTX 4080 | 16 GB | $900-1100 | 14B fast, 32B slow | Warm |
| RTX 4090 | 24 GB | $1500-2000 | 32B comfortable, 70B tight | Hot |
| A100 | 80 GB | $10K-15K | 70B comfortable | Hot |
| H100 | 80 GB | $25K-35K | 70B+ fast | Hot |

### 4.2 VRAM Quick Estimation

```
FP16:  params (B) × 2 = GB needed
FP8:   params (B) × 1 = GB needed
INT4:  params (B) × 0.5 = GB needed
+ 20-40% headroom for KV cache at longer contexts
```

### 4.3 Quantization Formats

| Format | Quality Retention | Best For |
|--------|------------------|----------|
| **AWQ** | ~95% | RTX 4070-4090, highest quality |
| **GGUF Q4_K_M** | ~92% | llama.cpp/Ollama, best balance |
| **GPTQ** | ~90% | CUDA tensor cores, 20% faster throughput |

**Recommendation**: Support GGUF as primary format (widest compatibility with llama.cpp ecosystem), ONNX for embedding/classification models.

### 4.4 Cross-Backend Determinism (Critical Implementation Constraint)

> **Issue #11 feedback**: This is a key gap. QFC's spot-check verification requires
> `output_hash` match between miner and validator, but floating-point results differ
> across backends (GPU vs CPU, NVIDIA vs AMD vs Apple Silicon, FP16 vs FP32).

**The problem**:
- FP16 (GPU) vs FP32 (CPU) produce different rounding results
- Different GPU architectures (CUDA vs Metal vs ROCm) have different FP precision
- Quantized models (GGUF Q4) may produce different results on different hardware
- Current `verification.rs` uses strict `output_hash` matching — this will break with multi-backend support

**Proposed verification strategy (tiered)**:

| Model Type | Verification Method | Rationale |
|------------|-------------------|-----------|
| Embedding | **Cosine similarity > 0.999** | Small FP differences acceptable; semantic meaning preserved |
| Classification | **Top-K class match** | Same top prediction = correct, even if logit values differ slightly |
| TextGeneration (temp=0) | **Token-level match** | Compare decoded token sequence, not raw logits |
| TextGeneration (temp>0) | **Statistical validation** | Non-deterministic by nature; use challenge tasks with known outputs |
| ImageGeneration | **LPIPS perceptual similarity < threshold** | Pixel-exact match impossible across backends |
| SpeechToText | **WER (Word Error Rate) match** | Compare transcription text, not audio features |

**Implementation approach**:
1. Define a `VerificationMode` enum per `ComputeTaskType`
2. Embedding/Classification: compute similarity metric instead of hash equality
3. TextGeneration: hash the decoded token IDs (not raw float outputs)
4. For spot-check: validator must use the **same quantization format and backend** as the miner, or use approximate matching

**Near-term workaround**: Require all miners and validators to use the same canonical model weights (pinned GGUF file) with deterministic seed. This limits backend diversity but ensures hash match.

### 4.5 Quantization Infrastructure

> **Issue #11 feedback**: candle's quantized model loading path (`quantized_qwen2.rs`)
> is completely different from the safetensors path. GGUF files are in different HF repos.

**Required changes to `qfc-inference`**:

```
ModelRegistry entry needs:
  - quantization_format: Option<QuantFormat>  // GGUF, GPTQ, AWQ, None (FP16)
  - hf_repo: String                           // e.g., "Qwen/Qwen2.5-3B-Instruct-GGUF"
  - hf_revision: String                       // Pinned commit hash (see 4.6)
  - weight_filename: String                   // e.g., "qwen2.5-3b-instruct-q4_k_m.gguf"

download.rs changes:
  - Support GGUF file downloads (single file, not sharded safetensors)
  - Verify blake3 hash of downloaded weights against registry
  - Different model loading branch: candle::quantized vs candle::safetensors
```

### 4.6 Model Version Pinning

> **Issue #11 feedback**: HuggingFace models can be updated by authors silently.
> Different miners downloading at different times may get different weights → hash mismatch.

**Solution**: Lock every model to a specific HuggingFace commit revision.

```rust
ModelInfo {
    id: ModelId::new("qfc-llm-3b", "v1.0"),
    hf_repo: "Qwen/Qwen2.5-3B-Instruct-GGUF",
    hf_revision: "abc123def456",              // Pinned commit hash
    weight_hash: Hash::from_hex("..."),       // Blake3 hash of weight file
    weight_filename: "qwen2.5-3b-instruct-q4_k_m.gguf",
    // ...
}
```

- Miners verify `weight_hash` after download before registering the model
- Model upgrades (e.g., Qwen2.5 → Qwen3) go through governance as a new model proposal
- Old model version remains active during transition period (see Section 9)

---

## 5. QFC Current State vs Recommended Expansion

### 5.1 Current Model Registry (v2.0)

| QFC Model ID | Actual Model | Size | Tier | Task Type |
|-------------|-------------|------|------|-----------|
| qfc-embed-small | all-MiniLM-L6-v2 | 80 MB | Cold | Embedding |
| qfc-embed-medium | all-MiniLM-L12-v2 | 120 MB | Cold | Embedding |
| qfc-classify-small | bert-base-uncased | 440 MB | Warm | Classification |
| qfc-llm-0.5b | Qwen2.5-0.5B-Instruct | 990 MB | Cold | Text Generation |

**Gap**: Only 4 models, only 3 task types (Embedding, Classification, TextGeneration + OnnxInference). No image generation, no speech, no code, no multimodal.

### 5.2 Current ComputeTaskType Gaps

```rust
// Existing
TextGeneration, ImageClassification, Embedding, OnnxInference

// Missing (needed)
ImageGeneration,    // Stable Diffusion, FLUX
SpeechToText,       // Whisper
TextToSpeech,       // XTTS, Bark
VisionLanguage,     // Qwen-VL, LLaVA
```

> **Note**: Code generation models (Qwen2.5-Coder, DeepSeek-Coder) use `TextGeneration` task type
> with a code-specialized model. No separate `CodeGeneration` variant needed — the model architecture
> and decoding logic are identical to standard LLM text generation.

---

## 6. Recommended Model Registry (v2.1)

### 6.1 Tier: Cold (Consumer GPU, 8-12 GB VRAM)

Target audience: casual miners with gaming GPUs.

| QFC Model ID | Actual Model | Size | Task Type | VRAM |
|-------------|-------------|------|-----------|------|
| qfc-embed-small | all-MiniLM-L6-v2 | 80 MB | Embedding | 200 MB |
| qfc-embed-medium | all-MiniLM-L12-v2 | 120 MB | Embedding | 300 MB |
| qfc-embed-multilingual | BGE-M3 | 2.2 GB | Embedding | 4 GB |
| qfc-llm-0.5b | Qwen2.5-0.5B-Instruct | 990 MB | TextGeneration | 1 GB |
| qfc-llm-3b | Qwen2.5-3B-Instruct (Q4) | 1.8 GB | TextGeneration | 3 GB |
| qfc-whisper-base | Faster-Whisper base | 150 MB | SpeechToText | 1 GB |
| qfc-sd-1.5 | Stable Diffusion 1.5 | 4 GB | ImageGeneration | 6 GB |
| qfc-classify-small | bert-base-uncased | 440 MB | Classification | 2 GB |

### 6.2 Tier: Warm (Mid-range GPU, 12-16 GB VRAM)

Target audience: dedicated miners with RTX 4070/4080.

| QFC Model ID | Actual Model | Size | Task Type | VRAM |
|-------------|-------------|------|-----------|------|
| qfc-llm-7b | Qwen2.5-7B-Instruct (Q4) | 4.5 GB | TextGeneration | 8 GB |
| qfc-llm-14b | Qwen2.5-14B-Instruct (Q4) | 8.5 GB | TextGeneration | 12 GB |
| qfc-coder-14b | Qwen2.5-Coder-14B (Q4) | 8.5 GB | TextGeneration | 12 GB |
| qfc-whisper-large | Faster-Whisper large-v3 | 1.5 GB | SpeechToText | 3 GB |
| qfc-sdxl | Stable Diffusion XL | 6.5 GB | ImageGeneration | 8 GB |
| qfc-vl-7b | Qwen3-VL-7B (Q4) | 4.5 GB | VisionLanguage | 8 GB |

### 6.3 Tier: Hot (High-end GPU, 24-80 GB VRAM)

Target audience: professional miners with RTX 4090 / A100 / H100.

| QFC Model ID | Actual Model | Size | Task Type | VRAM |
|-------------|-------------|------|-----------|------|
| qfc-llm-32b | Qwen2.5-32B-Instruct (Q4) | 18 GB | TextGeneration | 24 GB |
| qfc-llm-72b | Qwen2.5-72B-Instruct (Q4) | 40 GB | TextGeneration | 48 GB |
| qfc-flux | FLUX.1 dev (NF4) | 12 GB | ImageGeneration | 16 GB |
| qfc-deepseek-r1 | DeepSeek-R1-Distill-32B (Q4) | 18 GB | TextGeneration | 24 GB |

---

## 7. New ComputeTaskType Definitions

```rust
pub enum ComputeTaskType {
    // Existing
    TextGeneration { model_id, prompt_hash, max_tokens, temperature_fp, seed },
    ImageClassification { model_id, input_hash },
    Embedding { model_id, input_hash },
    OnnxInference { model_hash, input_hash },

    // New task types
    ImageGeneration {
        model_id: ModelId,
        prompt_hash: Hash,          // Hash of text prompt
        negative_prompt_hash: Hash, // Hash of negative prompt
        width: u32,
        height: u32,
        steps: u32,
        seed: u64,                  // Deterministic seed for verification
    },
    SpeechToText {
        model_id: ModelId,
        audio_hash: Hash,           // Hash of input audio
        language: Option<String>,   // Auto-detect if None
    },
    VisionLanguage {
        model_id: ModelId,
        image_hash: Hash,           // Hash of input image
        prompt_hash: Hash,          // Hash of text prompt
        max_tokens: u32,
        seed: u64,
    },
    // NOTE: CodeGeneration is NOT a separate variant.
    // Code models (Qwen2.5-Coder, DeepSeek-Coder) use TextGeneration
    // with a code-specialized model_id. Architecture and decoding are identical.
}
```

### 7.1 Large Input Transfer Strategy

> **Issue #11 feedback**: `InferenceTask.input_data: Vec<u8>` works for text (KB-scale),
> but `ImageGeneration` prompts with reference images and `SpeechToText` audio inputs
> can be MB to tens of MB. P2P gossip is not viable for large payloads.

**Proposed approach**: Content-addressed external storage with hash-only on-chain reference.

```
For inputs > 64 KB:
  1. User uploads input to IPFS (or QFC's storage layer)
  2. Task submission includes only the content hash (input_hash)
  3. Miner retrieves input data from IPFS using the hash
  4. Miner verifies data matches hash before execution
  5. Result follows the existing pattern (inline <1MB, IPFS CID >1MB)

InferenceTask {
    input_data: Vec<u8>,          // For small inputs (text prompts)
    input_cid: Option<String>,    // For large inputs (audio, images) — IPFS CID
}
```

This reuses the existing IPFS infrastructure from inference result storage.

---

## 8. GPU Tier Redefinition

### Current Tier System

```rust
pub enum GpuTier {
    Cold,   // Minimum viable (8 GB)
    Warm,   // Mid-range (12-16 GB)
    Hot,    // High-end (24+ GB)
}
```

### Proposed Expansion

```rust
pub enum GpuTier {
    Cold,    // Consumer entry (8-10 GB) — RTX 3060/3070/4060
    Warm,    // Consumer mid (12-16 GB) — RTX 4070/4080
    Hot,     // Consumer high (24 GB) — RTX 4090
    Ultra,   // Data center (48-80 GB) — A100/H100
    Secure,  // TEE-enabled (H100/B200 CC) — Confidential inference (see doc #19)
}
```

The `Ultra` tier enables large models (70B+) that require data center GPUs. The `Secure` tier (from privacy research, see [19-PRIVACY-AI-INFERENCE.md](19-PRIVACY-AI-INFERENCE.md)) enables confidential inference.

> **Serialization compatibility warning** (Issue #11): `GpuTier` is Borsh-serialized.
> Adding new enum variants (`Ultra`, `Secure`) will break deserialization for older nodes
> (similar to the Account struct issue fixed in qfc-core #31).
>
> **Migration strategy options**:
> 1. **Version field**: Add a protocol version to serialized messages; old nodes ignore unknown tiers
> 2. **Hard fork**: Coordinate network upgrade where all nodes update simultaneously
> 3. **Reserved variants**: Pre-allocate enum slots now (e.g., `Reserved1 = 3, Reserved2 = 4`) to avoid future breakage
>
> **Recommendation**: Option 1 (version field) for flexibility. Implement before adding new tiers.

---

## 9. Model Governance Evolution

### Current: Static Registry

Models are hardcoded in `ModelRegistry::default_v2()`. Adding a new model requires a code change and node upgrade.

### Proposed: On-Chain Governance

```
1. Community member submits ModelProposal (already exists in governance.rs)
2. Validators vote on approval
3. Approved models added to on-chain registry
4. Miners auto-download approved models based on their tier
5. Model deprecation via governance vote
```

### Governance Cold-Start Strategy

> **Issue #11 feedback**: Who approves models before the governance system has enough participants?

| Phase | Approval Authority | Criteria |
|-------|-------------------|----------|
| **Testnet / Early mainnet** | Core team multisig (3-of-5) | Fast iteration, curated quality |
| **Growth phase** | Core team + top 10 validators by PoC score | Broader input, still manageable |
| **Mature phase** | Full on-chain governance vote | Decentralized, community-driven |

### Model Sunset Process

When a model is deprecated (e.g., Qwen2.5 → Qwen3):

```
1. Governance proposal: "Deprecate qfc-llm-7b v1.0, replace with qfc-llm-7b v2.0"
2. Announcement period: 2 weeks — both versions active
3. Transition period: 2 weeks — old model weight reduced to 50% in task routing
4. Sunset: Old model removed from active registry
   - Existing proofs referencing old model remain valid on-chain
   - New tasks cannot use the old model
   - Miners can free storage by evicting old model from cache
```

### Model Quality Assurance

Before approval, models should pass:
- **Determinism check**: Same input + seed → same output on canonical backend (required for verification)
- **Resource bounds**: Memory and compute within tier limits
- **Security scan**: No known model poisoning or backdoor risks
- **Benchmark**: Minimum quality thresholds on standard datasets
- **Weight hash verification**: Blake3 hash of weight files recorded in proposal (see Section 4.6)

---

## 10. Pricing Strategy

### Current Fee Model

```
Base: 1 GFLOP = 1e12 wei (0.000001 QFC)
Tier multiplier: Cold=1x, Warm=1.5x, Hot=2x
Minimum fee: 0.0001 QFC
```

### Proposed Fee Model by Task Type

| Task Type | Pricing Unit | Base Fee Multiplier | Rationale |
|-----------|-------------|-------------------|-----------|
| Embedding | Per request | 1x | Lightweight, fast, fixed cost |
| Classification | Per request | 1x | Lightweight, fast, fixed cost |
| SpeechToText | **Per second of audio** | 2x | Scales with input duration |
| TextGeneration | **Per output token** | 1.5x | Scales with generation length |
| ImageGeneration | **Per step × resolution** | 5x | 20-step 512px vs 50-step 1024px = very different cost |
| VisionLanguage | **Per output token** | 3x | Image encoding (fixed) + text generation (variable) |

> **Issue #11 feedback**: Static multipliers don't capture actual cost variance.
> A 10-token generation vs 1000-token generation should not cost the same.

**Dynamic fee formula**:
```
fee = base_rate × task_units × tier_multiplier × model_size_factor

Where:
  task_units =
    TextGeneration: actual_output_tokens
    SpeechToText: audio_duration_seconds
    ImageGeneration: steps × (width × height / 512²)
    Embedding/Classification: 1 (fixed)

  tier_multiplier = Cold:1x, Warm:1.5x, Hot:2x, Ultra:3x, Secure:4x
  model_size_factor = params_billions / 7  (normalized to 7B baseline)
```

Fee is estimated at submission (user pays max), actual cost calculated after completion, difference refunded.

---

## 11. Implementation Roadmap

### Phase 1: Quantization Infrastructure + Text Model Expansion (3-4 weeks)

- Implement GGUF model loading path in `download.rs` and inference backends
- Add weight hash verification (blake3) to `ModelCache`
- Add HF revision pinning to `ModelInfo`
- Add Qwen2.5-3B-GGUF and Qwen2.5-7B-GGUF to registry
- Update `model_tier_and_memory()` for new size classes
- Define `VerificationMode` per task type for cross-backend determinism

### Phase 2a: SpeechToText (3-4 weeks)

- Add `SpeechToText` variant to `ComputeTaskType`
- Implement Whisper backend via candle
- Large input transfer via IPFS CID (audio files)
- Per-second-of-audio dynamic pricing

### Phase 2b: ImageGeneration (6-8 weeks, separate track)

> **Issue #11 feedback**: Diffusion pipelines are multi-model (Text Encoder → U-Net × N steps → VAE Decoder).
> Engineering complexity is significantly higher than LLM autoregressive decoding.
> Original 4-6 week estimate was optimistic.

- Add `ImageGeneration` variant to `ComputeTaskType`
- Implement Stable Diffusion 1.5 pipeline via candle (3 sub-models)
- Deterministic seed verification strategy (same seed + same GGUF = same image)
- Per-step × resolution dynamic pricing

### Phase 3: VisionLanguage + Governance (4-6 weeks)

- Add `VisionLanguage` variant to `ComputeTaskType`
- Implement Qwen-VL backend
- Activate `ModelGovernance` for proposal/vote workflow
- Model sunset process implementation
- Cold-start: core team multisig approval

### Phase 4: Ultra/Secure Tiers (6-8 weeks)

- Add Ultra and Secure GPU tiers (with serialization migration strategy)
- Large model support (70B+ with multi-GPU)
- TEE attestation integration (see [19-PRIVACY-AI-INFERENCE.md](19-PRIVACY-AI-INFERENCE.md))

---

## 12. Enterprise Demand Alignment

Based on market data (Akash, io.net, industry reports):

| Enterprise Use Case | Market Share | QFC Coverage |
|--------------------|-------------|--------------|
| Chatbots & recommendation | 38.91% | TextGeneration (Qwen/DeepSeek) |
| Speech transcription | High | SpeechToText (Whisper) |
| Embeddings/RAG | High | Embedding (MiniLM, BGE-M3) |
| Image generation | Growing | ImageGeneration (SD, FLUX) |
| Code assistance | Growing | TextGeneration (Qwen Coder models) |
| Privacy-focused inference | Emerging | Secure tier (TEE) |

QFC's expanded model registry would cover **>90% of enterprise inference demand**.

---

## References

- [Top 10 AI Models of 2025 - Analytics Vidhya](https://www.analyticsvidhya.com/blog/2025/11/top-open-source-models-on-huggingface/)
- [State of Open Source AI Models 2025 - Red Hat](https://developers.redhat.com/articles/2026/01/07/state-open-source-ai-models-2025)
- [HuggingFace 50 Most Downloaded Models 2025](https://undercodenews.com/inside-hugging-face-the-50-most-downloaded-open-source-models-of-2025/)
- [Best Open-Source LLMs for 16GB VRAM](https://dasroot.net/posts/2026/01/best-open-source-llms-16gb-vram-2026/)
- [GPU Requirements Cheat Sheet 2026 - Spheron](https://www.spheron.network/blog/gpu-requirements-cheat-sheet-2026/)
- [GGUF vs GPTQ vs AWQ Comparison](https://localaimaster.com/blog/quantization-explained)
- [Embedding Models Comparison BGE vs E5 vs Instructor](https://dasroot.net/posts/2026/01/embedding-models-comparison-bge-e5-instructor/)
- [Best Open-Source Embedding Models 2026 - BentoML](https://www.bentoml.com/blog/a-guide-to-open-source-embedding-models)
- [Akash 2025 Year in Review](https://akash.network/blog/akash-2025-year-in-review/)
- [Decentralized GPU Networks 2026 - BlockEden](https://blockeden.xyz/blog/2026/02/07/decentralized-gpu-networks-2026/)
- [Enterprise AI Market - Mordor Intelligence](https://www.mordorintelligence.com/industry-reports/enterprise-ai-market)
- [Bittensor Subnet Ecosystem - CoinDesk](https://www.coindesk.com/business/2025/09/13/bittensor-ecosystem-surges-with-subnet-expansion-institutional-access)
- [Ritual Infernet ML Documentation](https://infernet-ml.docs.ritual.net/)
