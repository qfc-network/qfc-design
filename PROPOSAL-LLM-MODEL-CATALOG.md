# Proposal: add the first LLM to the QFC inference catalog

> Status: **DRAFT — needs a proposer with validator support before on-chain submission**
> Author: Larry
> Related: [`42-CORE-GAPS-CN.md`](./42-CORE-GAPS-CN.md) Gap B; [`miner-economics/MINER-ECONOMICS.md`](./miner-economics/MINER-ECONOMICS.md)
> Governance path: `qfc_proposeModel` → 1-day voting window → >2/3 active validators approve → `ModelGovernance::tally()` marks Passed

## Motivation — the single hard block on Gap B

Today QFC's approved model catalog is:

| Model | Task type | Min tier |
|---|---|---|
| qfc-embed-small | TextEmbedding | Cold |
| qfc-embed-medium | TextEmbedding | Warm |
| qfc-classify-small | Classification | Warm |

All three are embedding / classification models. They're **useful for internal indexer/search workflows but useless for user-facing demos**. The standard OpenAI / Claude comparison an external dev will reach for is "can I get text generation out of it?" — and today the answer is "no."

That single fact is why:
- The SDK snippets in [`sdk-snippets/`](./sdk-snippets/) feel like toys
- The "1-minute pitch" demo (Gap B milestone T+8w) has nothing interesting to demo
- The 2 submitter addresses producing all current inference traffic are internal bots — external devs have nothing to point at

**Adding one small LLM unblocks the entire demand-side story.**

## Proposal

Add `qwen2.5-1.5b-instruct` to the approved model catalog as the first text-generation model.

### Why Qwen2.5-1.5B specifically

| Criterion | Qwen2.5-1.5B | Alternatives considered |
|---|---|---|
| License | Apache 2.0 | Llama-3.2 (Meta custom, commercial-friendly but not Apache), Phi-3.5 (MIT) |
| Weights size | ~3 GB fp16 / ~1 GB GGUF Q4 | 0.5B: too weak for compelling demos. 7B+: doesn't fit on Cold tier miners (<16 GB VRAM). |
| Hardware tier | Cold (works on CPU + every GPU rig) | 7B+ excludes the 2017-MBP / laptop / cheap VPS tier we need for Gap A onboarding |
| Inference quality | MT-Bench 7.2 for 1.5B class, multilingual incl. Chinese | Phi-3.5-mini (3.8B) slightly better but 2× size; TinyLlama 1.1B noticeably weaker |
| Weights source | Stable on HuggingFace under `Qwen/Qwen2.5-1.5B-Instruct` + GGUF at `unsloth/Qwen2.5-1.5B-Instruct-GGUF` | — |
| QFC audience fit | Native Chinese + English. Matches likely user base for a Chinese-led project. | — |

### Proposal fields

Fields map to `ModelInfo` in `qfc-core/crates/qfc-inference/src/model.rs`:

```
id.name:         "qwen2.5-1.5b-instruct"
id.version:      "v1.0"
description:     "Qwen2.5-1.5B-Instruct — open-weights text generation and chat.
                  Apache-2.0 licensed. ~1 GB quantized, runs on CPU and consumer GPU.
                  Adds the first text-generation capability to the QFC inference network."
min_memory_mb:   2048          # 2 GB — covers Q4 GGUF + modest context
min_tier:        Cold          # any tier works
size_mb:         1100          # Q4_K_M GGUF roughly
canonical_format: GgufQ4KM
weights_hash:    <blake3 of the canonical weights file — filled in after benchmark bundle>
```

`canonical_format: GgufQ4KM` is deliberate — Q4 quantization brings the file to ~1 GB (download is fast on a cheap VPS) and inference runs well on CPU via candle-core. Fp16 safetensors would require 16 GB RAM minimum and excludes most of the miner population we're trying to attract.

## Rollout plan

### Week 1: validate before proposing

Someone on the miner ops side runs the candidate GGUF through the miner binary (`qfc-miner`) and confirms:

1. Weights file downloads successfully and the blake3 hash matches the proposal.
2. Inference works on a Cold-tier miner (2017 Intel MBP or equivalent) — not just hot GPU rigs. Target latency < 5 s for a 100-token generation.
3. Output is coherent on a smoke-test suite of 10 prompts (5 English, 5 Chinese).
4. No malicious behavior — the model file isn't executing arbitrary code during load.

Publish the validation report in this directory (`PROPOSAL-LLM-MODEL-CATALOG-VALIDATION.md`).

### Week 2: submit on-chain proposal

Any address (anyone can propose) calls:

```
qfc_proposeModel(
  proposer:        <proposer address>,
  model_name:      "qwen2.5-1.5b-instruct",
  model_version:   "v1.0",
  description:     <as above>,
  min_memory_mb:   2048,
  min_tier:        "Cold",
  size_mb:         1100
)
```

Voting window: 1 day. Need >2/3 of active validators to approve. **This requires coordinating validators in advance** — send a heads-up 48 h before the on-chain proposal so they know what's coming and can review the validation report.

### Week 3: post-approval

Once passed:

1. Update `qfc_getSupportedModels` (automatic — reads from on-chain registry).
2. Miners that want to serve this model download weights and register capability via `qfc_registerMiner`.
3. Update [`sdk-snippets/call-inference.js`](./sdk-snippets/call-inference.js) and `.py` to use the new model as the primary example — the pitch becomes "paste text, get generated reply, see proof on explorer."
4. Add a `qwen2.5-1.5b-instruct` demo pane to the demo page (see `demo/` directory — WIP).

## Risks

| Risk | Mitigation |
|---|---|
| Miners serve outputs that differ from expected weights (integrity failure) | `weights_hash` is verified on load; mismatch = miner refuses to run |
| LLM outputs political/offensive content that embarrasses QFC on launch | Qwen2.5 has standard safety training. For a testnet demo we accept this risk; mainnet launch may want an extra layer |
| Model size exceeds Cold-tier RAM on very constrained miners | Q4 GGUF at ~1.1 GB + 700 MB KV cache fits comfortably in 2 GB. We explicitly ship Q4, not fp16. |
| License misunderstanding | Apache-2.0 is explicit; no commercial clause. QFC redistributes weights, users use them. Clean. |
| Proposal fails to hit 2/3 quorum | Pre-socialize with validator operators before submitting. Our validators today are internal — this week it's a rubber stamp. Post-mainnet it matters more. |

## Why now

The [42-CORE-GAPS](./42-CORE-GAPS-CN.md) doc commits to a T+8 week external-demand milestone. A model-catalog change has:

- A 1-week validation cycle
- A 1-day voting window
- A 1-week SDK/demo update cycle

Three weeks of lead time. If we want demand-side signal by T+8w, the proposal needs to go on-chain **within the next 2 weeks** — otherwise we're chasing Gap B with no ammunition.

## What I need from the reader

- [ ] Agreement that Qwen2.5-1.5B is the right first LLM (or a concrete counter-proposal with reasoning)
- [ ] Volunteer to run the Week 1 validation (miner ops)
- [ ] Confirmation that validator operators will vote on a pre-socialized proposal
- [ ] Who submits the proposal tx on-chain (anyone qualified — just pick one)

Once those four are resolved, Week 1 starts and we're on the clock.
