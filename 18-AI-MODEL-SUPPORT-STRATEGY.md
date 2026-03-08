# AI Model Support Strategy: What Models Should QFC Support?

> Last Updated: 2026-03-08 | Version 1.0
> GitHub Issue: #10

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
CodeGeneration,     // CodeLlama, DeepSeek Coder
VisionLanguage,     // Qwen-VL, LLaVA
```

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
| qfc-coder-14b | Qwen2.5-Coder-14B (Q4) | 8.5 GB | CodeGeneration | 12 GB |
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
    CodeGeneration {
        model_id: ModelId,
        prompt_hash: Hash,
        max_tokens: u32,
        temperature_fp: u32,
        seed: u64,
    },
    VisionLanguage {
        model_id: ModelId,
        image_hash: Hash,           // Hash of input image
        prompt_hash: Hash,          // Hash of text prompt
        max_tokens: u32,
        seed: u64,
    },
}
```

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

The `Ultra` tier enables large models (70B+) that require data center GPUs. The `Secure` tier (from privacy research) enables confidential inference.

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

### Model Quality Assurance

Before approval, models should pass:
- **Determinism check**: Same input + seed → same output (required for verification)
- **Resource bounds**: Memory and compute within tier limits
- **Security scan**: No known model poisoning or backdoor risks
- **Benchmark**: Minimum quality thresholds on standard datasets

---

## 10. Pricing Strategy

### Current Fee Model

```
Base: 1 GFLOP = 1e12 wei (0.000001 QFC)
Tier multiplier: Cold=1x, Warm=1.5x, Hot=2x
Minimum fee: 0.0001 QFC
```

### Proposed Fee Model by Task Type

| Task Type | Base Fee Multiplier | Rationale |
|-----------|-------------------|-----------|
| Embedding | 1x | Lightweight, fast |
| Classification | 1x | Lightweight, fast |
| SpeechToText | 2x | Audio processing overhead |
| TextGeneration | 1.5x (per token) | Scales with output length |
| CodeGeneration | 1.5x (per token) | Same as text gen |
| ImageGeneration | 5x | High compute (20-50 steps of diffusion) |
| VisionLanguage | 3x | Image encoding + text generation |

Add tier multipliers: Cold=1x, Warm=1.5x, Hot=2x, Ultra=3x, Secure=4x

---

## 11. Implementation Roadmap

### Phase 1: Expand Text Models (2-3 weeks)

- Add Qwen2.5-3B and Qwen2.5-7B to registry
- Update `model_tier_and_memory()` for new size classes
- Test quantized model loading in qfc-inference

### Phase 2: New Task Types (4-6 weeks)

- Add `ImageGeneration`, `SpeechToText`, `CodeGeneration`, `VisionLanguage` to `ComputeTaskType`
- Implement inference backends (Stable Diffusion via candle, Whisper via candle)
- Update task routing and fee calculation

### Phase 3: On-Chain Model Governance (4-6 weeks)

- Activate `ModelGovernance` for proposal/vote workflow
- Auto-download system for newly approved models
- Model deprecation and sunset process

### Phase 4: Ultra/Secure Tiers (6-8 weeks)

- Add Ultra and Secure GPU tiers
- Large model support (70B+ with multi-GPU)
- TEE attestation integration (see doc #19)

---

## 12. Enterprise Demand Alignment

Based on market data (Akash, io.net, industry reports):

| Enterprise Use Case | Market Share | QFC Coverage |
|--------------------|-------------|--------------|
| Chatbots & recommendation | 38.91% | TextGeneration (Qwen/DeepSeek) |
| Speech transcription | High | SpeechToText (Whisper) |
| Embeddings/RAG | High | Embedding (MiniLM, BGE-M3) |
| Image generation | Growing | ImageGeneration (SD, FLUX) |
| Code assistance | Growing | CodeGeneration (Qwen Coder) |
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
