# AI 模型支持策略：QFC 应支持哪些模型？

> 最后更新：2026-03-08 | 版本 1.1
> GitHub Issue: #10
> 评审：#11（已纳入 qfc-core 实现反馈）
> 作者：Alex Wei，QFC Network 产品经理

---

## 1. 执行摘要

本文档调研了去中心化推理平台上的 AI 模型生态，分析了消费级 GPU 的可行性，并为 QFC 推荐了分层模型支持策略。

**核心发现：**

- **HuggingFace 上 92.48% 的下载量来自 10 亿参数以下的模型**——小型模型主导了真实需求
- QFC 当前注册表（4 个模型，均小于 1B）是一个好的起点，但对于市场而言过于狭窄
- 消费级 GPU（RTX 3060-4090）可以流畅运行 7B-14B 的量化模型；高端显卡可运行 32B 模型
- 企业需求集中在：LLM 聊天机器人（38.91%）、语音转文字、嵌入和图像生成
- **建议**：扩展至 15-20 个模型，覆盖 6 个类别，映射到 QFC 的 Cold/Warm/Hot GPU 层级

---

## 2. 竞争格局：其他平台支持什么

### 2.1 Bittensor（128 个子网）

| 子网 | 任务 | 热门模型 |
|--------|------|---------------|
| SN1 | 文本生成 | DeepSeek V3（主导 token 使用量） |
| SN4 | AI 内容检测 | 确定性验证模型 |
| SN17 | 3D 生成 | 高斯飞溅、NeRF、3D 扩散 |
| SN19 | 超低延迟推理 | 图像 + 文本组合 |
| SN64 | 无服务器 AI 算力 | 任意模型（自由部署） |

**关键洞察**：Bittensor 的开放子网模型意味着任何模型都可以被支持。DeepSeek V3 主导了实际使用量。

### 2.2 Ritual (Infernet)

- 支持**任何 ONNX、PyTorch 或 HuggingFace 模型**
- 通过 TGI 支持 LLM：LLaMA、Falcon、StarCoder、BLOOM、GPT-NeoX、T5
- 无固定模型注册表——节点自行选择服务哪些模型
- 也支持闭源 API 调用（OpenAI GPT-4）

### 2.3 Akash Network

- 最热门模型：**GPT-OSS-120B、Qwen3-Next-80B、DeepSeek-V3.1**
- 常见工作负载：LLM 推理、Whisper 转录、隐私模型
- 硬件：A100/H100，正在为 2026 年采购约 7,200 张 GB200 GPU
- 企业客户租用数十张 GPU 进行生成式 AI

### 2.4 Nosana

- 在节点上预加载模型：LLaMA 2、Stable Diffusion
- 专注于 Solana 生态

---

## 3. 按类别划分的模型生态（2025-2026）

### 3.1 LLM（文本生成）

| 模型 | 参数量 | 显存（Q4） | 核心优势 |
|-------|-----------|-----------|--------------|
| **Qwen 2.5/3** | 0.5B-235B | 0.5-120 GB | HuggingFace 下载量最高；多语言、推理、代码 |
| **DeepSeek R1/V3** | 7B-671B | 4-340 GB | 推理、数学；以更低成本匹配前沿水平 |
| **LLaMA 3/4** | 8B-405B | 5-200 GB | 多模态、长上下文（128K） |
| **Mistral/Mixtral** | 7B-8x22B | 4-60 GB | MoE 高效率 |
| **Phi-4** | 14B | 9 GB | 最佳指令遵循 |
| **Gemma 2** | 2B-27B | 1.5-16 GB | Google 的高效小模型 |
| **GPT-OSS 20B** | 20B | 12 GB | 16GB 显存上最快（42 tok/s） |

### 3.2 嵌入模型

| 模型 | 参数量 | 显存 | 优势 |
|-------|-----------|------|----------|
| **all-MiniLM-L6-v2** | 22M | ~200 MB | 速度、效率（QFC 已支持） |
| **all-MiniLM-L12-v2** | 33M | ~300 MB | 更好的质量（QFC 已支持） |
| **BGE-M3** | 560M | ~4 GB | 多语言、长上下文检索 |
| **E5-large-instruct** | 700M | ~5 GB | 最佳全能选手 |
| **all-mpnet-base-v2** | 110M | ~500 MB | 质量与速度的平衡 |

### 3.3 图像生成

| 模型 | 显存 | 备注 |
|-------|------|-------|
| **Stable Diffusion 1.5** | 4-6 GB | 老一代但有海量 LoRA 生态 |
| **Stable Diffusion XL** | 8 GB | 当前主流 |
| **FLUX.1** | 6 GB（NF4 量化）- 24 GB（完整） | 最先进的质量 |
| **FLUX-2** | 8 GB（group_offloading）- 24 GB | 最新一代 |

### 3.4 语音转文字

| 模型 | 显存 | 备注 |
|-------|------|-------|
| **Whisper large-v3** | ~3 GB (fp16) | 部署最广泛的 ASR |
| **Faster-Whisper** | 比 Whisper 少 40% | 4 倍速度提升，INT8 量化 |
| **MeloTTS** | 可在 CPU 运行 | 无需 GPU |
| **XTTS v2** | ~2.7 GB | 语音克隆 TTS |

### 3.5 多模态（视觉-语言）

| 模型 | 显存（Q4） | 备注 |
|-------|-----------|-------|
| **Qwen3-VL-2B** | 4 GB | 适配 RTX 3060 |
| **Qwen3-VL-7B** | 8 GB | 适配 RTX 4070 |
| **LLaVA-1.5/NeXT** | 8-16 GB | 视觉指令微调 |

### 3.6 代码生成

| 模型 | 参数量 | 显存（Q4） | 备注 |
|-------|-----------|-----------|-------|
| **Qwen 2.5 Coder 14B** | 14B | ~9 GB | 超越 CodeStral-22B |
| **DeepSeek Coder V2 Lite** | 16B MoE（2.4B 激活） | ~6 GB | 速度极快，内存高效 |
| **CodeLlama 13B** | 13B | ~8 GB | 在 73% 的任务中超越 Copilot |

---

## 4. 消费级 GPU 可行性

### 4.1 GPU 显存参考

| GPU | 显存 | 价格区间 | 最大模型（Q4） | QFC 层级 |
|-----|------|-------------|-----------------|----------|
| RTX 3060 | 12 GB | $250-350 | 8B 流畅，14B 较慢 | Cold |
| RTX 3070 | 8 GB | $300-400 | 7-8B | Cold |
| RTX 3080 | 10 GB | $400-550 | 8B 流畅 | Cold |
| RTX 4060 | 8 GB | $280-350 | 7-8B | Cold |
| RTX 4070 | 12 GB | $500-600 | 14B | Warm |
| RTX 4070 Ti Super | 16 GB | $700-800 | 14B 快速，32B 较慢 | Warm |
| RTX 4080 | 16 GB | $900-1100 | 14B 快速，32B 较慢 | Warm |
| RTX 4090 | 24 GB | $1500-2000 | 32B 流畅，70B 紧张 | Hot |
| A100 | 80 GB | $10K-15K | 70B 流畅 | Hot |
| H100 | 80 GB | $25K-35K | 70B+ 快速 | Hot |

### 4.2 显存快速估算

```
FP16:  参数量 (B) × 2 = 所需 GB
FP8:   参数量 (B) × 1 = 所需 GB
INT4:  参数量 (B) × 0.5 = 所需 GB
+ 长上下文场景需额外 20-40% 的 KV 缓存空间
```

### 4.3 量化格式

| 格式 | 质量保留率 | 最适场景 |
|--------|------------------|----------|
| **AWQ** | ~95% | RTX 4070-4090，最高质量 |
| **GGUF Q4_K_M** | ~92% | llama.cpp/Ollama，最佳平衡 |
| **GPTQ** | ~90% | CUDA 张量核心，吞吐量快 20% |

**建议**：以 GGUF 为主要格式（与 llama.cpp 生态兼容性最广），嵌入/分类模型使用 ONNX。

### 4.4 跨后端确定性（关键实现约束）

> **Issue #11 反馈**：这是一个关键缺口。QFC 的抽查验证要求矿工和验证者的
> `output_hash` 匹配，但浮点运算结果在不同后端间存在差异（GPU 与 CPU、NVIDIA 与 AMD 与 Apple Silicon、FP16 与 FP32）。

**问题所在**：
- FP16（GPU）与 FP32（CPU）产生不同的舍入结果
- 不同的 GPU 架构（CUDA 与 Metal 与 ROCm）具有不同的浮点精度
- 量化模型（GGUF Q4）可能在不同硬件上产生不同结果
- 当前 `verification.rs` 使用严格的 `output_hash` 匹配——这在多后端支持下会失效

**分层验证策略建议**：

| 模型类型 | 验证方法 | 理由 |
|------------|-------------------|-----------|
| 嵌入 | **余弦相似度 > 0.999** | 微小的浮点差异可以接受；语义含义保留 |
| 分类 | **Top-K 类别匹配** | 相同的最高预测即为正确，即使 logit 值略有差异 |
| 文本生成（temp=0） | **Token 级匹配** | 比较解码后的 token 序列，而非原始 logit |
| 文本生成（temp>0） | **统计验证** | 本质上非确定性；使用已知输出的挑战任务 |
| 图像生成 | **LPIPS 感知相似度 < 阈值** | 跨后端不可能实现像素精确匹配 |
| 语音转文字 | **WER（词错误率）匹配** | 比较转录文本，而非音频特征 |

**实现方案**：
1. 为每个 `ComputeTaskType` 定义 `VerificationMode` 枚举
2. 嵌入/分类：计算相似度指标而非哈希相等
3. 文本生成：对解码后的 token ID 计算哈希（而非原始浮点输出）
4. 抽查时：验证者必须使用与矿工**相同的量化格式和后端**，或使用近似匹配

**近期临时方案**：要求所有矿工和验证者使用相同的规范模型权重（固定的 GGUF 文件）和确定性种子。这限制了后端多样性，但确保了哈希匹配。

### 4.5 量化基础设施

> **Issue #11 反馈**：candle 的量化模型加载路径（`quantized_qwen2.rs`）
> 与 safetensors 路径完全不同。GGUF 文件位于不同的 HF 仓库中。

**`qfc-inference` 所需变更**：

```
ModelRegistry 条目需要：
  - quantization_format: Option<QuantFormat>  // GGUF, GPTQ, AWQ, None (FP16)
  - hf_repo: String                           // 例如 "Qwen/Qwen2.5-3B-Instruct-GGUF"
  - hf_revision: String                       // 固定的 commit 哈希（见 4.6）
  - weight_filename: String                   // 例如 "qwen2.5-3b-instruct-q4_k_m.gguf"

download.rs 变更：
  - 支持 GGUF 文件下载（单文件，非分片 safetensors）
  - 使用 blake3 哈希验证下载的权重与注册表对照
  - 不同的模型加载分支：candle::quantized 与 candle::safetensors
```

### 4.6 模型版本锁定

> **Issue #11 反馈**：HuggingFace 模型可以被作者静默更新。
> 不同矿工在不同时间下载可能获得不同的权重 → 哈希不匹配。

**解决方案**：将每个模型锁定到特定的 HuggingFace commit 版本。

```rust
ModelInfo {
    id: ModelId::new("qfc-llm-3b", "v1.0"),
    hf_repo: "Qwen/Qwen2.5-3B-Instruct-GGUF",
    hf_revision: "abc123def456",              // 固定的 commit 哈希
    weight_hash: Hash::from_hex("..."),       // 权重文件的 Blake3 哈希
    weight_filename: "qwen2.5-3b-instruct-q4_k_m.gguf",
    // ...
}
```

- 矿工在注册模型前验证下载后的 `weight_hash`
- 模型升级（例如 Qwen2.5 → Qwen3）通过治理流程作为新模型提案处理
- 过渡期间旧模型版本保持活跃（见第 9 节）

---

## 5. QFC 现状与建议扩展

### 5.1 当前模型注册表（v2.0）

| QFC 模型 ID | 实际模型 | 大小 | 层级 | 任务类型 |
|-------------|-------------|------|------|-----------|
| qfc-embed-small | all-MiniLM-L6-v2 | 80 MB | Cold | Embedding |
| qfc-embed-medium | all-MiniLM-L12-v2 | 120 MB | Cold | Embedding |
| qfc-classify-small | bert-base-uncased | 440 MB | Warm | Classification |
| qfc-llm-0.5b | Qwen2.5-0.5B-Instruct | 990 MB | Cold | Text Generation |

**不足**：仅 4 个模型，仅 3 种任务类型（Embedding、Classification、TextGeneration + OnnxInference）。没有图像生成、语音、代码和多模态。

### 5.2 当前 ComputeTaskType 缺口

```rust
// 已有
TextGeneration, ImageClassification, Embedding, OnnxInference

// 缺失（需要添加）
ImageGeneration,    // Stable Diffusion, FLUX
SpeechToText,       // Whisper
TextToSpeech,       // XTTS, Bark
VisionLanguage,     // Qwen-VL, LLaVA
```

> **注意**：代码生成模型（Qwen2.5-Coder、DeepSeek-Coder）使用 `TextGeneration` 任务类型，
> 搭配代码专用的 model_id。无需单独的 `CodeGeneration` 变体——模型架构和解码逻辑
> 与标准 LLM 文本生成完全相同。

---

## 6. 建议模型注册表（v2.1）

### 6.1 层级：Cold（消费级 GPU，8-12 GB 显存）

目标用户：拥有游戏 GPU 的休闲矿工。

| QFC 模型 ID | 实际模型 | 大小 | 任务类型 | 显存 |
|-------------|-------------|------|-----------|------|
| qfc-embed-small | all-MiniLM-L6-v2 | 80 MB | Embedding | 200 MB |
| qfc-embed-medium | all-MiniLM-L12-v2 | 120 MB | Embedding | 300 MB |
| qfc-embed-multilingual | BGE-M3 | 2.2 GB | Embedding | 4 GB |
| qfc-llm-0.5b | Qwen2.5-0.5B-Instruct | 990 MB | TextGeneration | 1 GB |
| qfc-llm-3b | Qwen2.5-3B-Instruct (Q4) | 1.8 GB | TextGeneration | 3 GB |
| qfc-whisper-base | Faster-Whisper base | 150 MB | SpeechToText | 1 GB |
| qfc-sd-1.5 | Stable Diffusion 1.5 | 4 GB | ImageGeneration | 6 GB |
| qfc-classify-small | bert-base-uncased | 440 MB | Classification | 2 GB |

### 6.2 层级：Warm（中端 GPU，12-16 GB 显存）

目标用户：拥有 RTX 4070/4080 的专业矿工。

| QFC 模型 ID | 实际模型 | 大小 | 任务类型 | 显存 |
|-------------|-------------|------|-----------|------|
| qfc-llm-7b | Qwen2.5-7B-Instruct (Q4) | 4.5 GB | TextGeneration | 8 GB |
| qfc-llm-14b | Qwen2.5-14B-Instruct (Q4) | 8.5 GB | TextGeneration | 12 GB |
| qfc-coder-14b | Qwen2.5-Coder-14B (Q4) | 8.5 GB | TextGeneration | 12 GB |
| qfc-whisper-large | Faster-Whisper large-v3 | 1.5 GB | SpeechToText | 3 GB |
| qfc-sdxl | Stable Diffusion XL | 6.5 GB | ImageGeneration | 8 GB |
| qfc-vl-7b | Qwen3-VL-7B (Q4) | 4.5 GB | VisionLanguage | 8 GB |

### 6.3 层级：Hot（高端 GPU，24-80 GB 显存）

目标用户：拥有 RTX 4090 / A100 / H100 的专业矿工。

| QFC 模型 ID | 实际模型 | 大小 | 任务类型 | 显存 |
|-------------|-------------|------|-----------|------|
| qfc-llm-32b | Qwen2.5-32B-Instruct (Q4) | 18 GB | TextGeneration | 24 GB |
| qfc-llm-72b | Qwen2.5-72B-Instruct (Q4) | 40 GB | TextGeneration | 48 GB |
| qfc-flux | FLUX.1 dev (NF4) | 12 GB | ImageGeneration | 16 GB |
| qfc-deepseek-r1 | DeepSeek-R1-Distill-32B (Q4) | 18 GB | TextGeneration | 24 GB |

---

## 7. 新 ComputeTaskType 定义

```rust
pub enum ComputeTaskType {
    // 已有
    TextGeneration { model_id, prompt_hash, max_tokens, temperature_fp, seed },
    ImageClassification { model_id, input_hash },
    Embedding { model_id, input_hash },
    OnnxInference { model_hash, input_hash },

    // 新任务类型
    ImageGeneration {
        model_id: ModelId,
        prompt_hash: Hash,          // 文本提示词的哈希
        negative_prompt_hash: Hash, // 负面提示词的哈希
        width: u32,
        height: u32,
        steps: u32,
        seed: u64,                  // 用于验证的确定性种子
    },
    SpeechToText {
        model_id: ModelId,
        audio_hash: Hash,           // 输入音频的哈希
        language: Option<String>,   // 为 None 时自动检测
    },
    VisionLanguage {
        model_id: ModelId,
        image_hash: Hash,           // 输入图像的哈希
        prompt_hash: Hash,          // 文本提示词的哈希
        max_tokens: u32,
        seed: u64,
    },
    // 注意：CodeGeneration 不是单独的变体。
    // 代码模型（Qwen2.5-Coder、DeepSeek-Coder）使用 TextGeneration，
    // 搭配代码专用的 model_id。架构和解码方式完全相同。
}
```

### 7.1 大文件输入传输策略

> **Issue #11 反馈**：`InferenceTask.input_data: Vec<u8>` 对文本（KB 级别）有效，
> 但 `ImageGeneration` 带参考图的提示词和 `SpeechToText` 的音频输入
> 可能达到 MB 到数十 MB。P2P gossip 不适用于大负载。

**建议方案**：基于内容寻址的外部存储，链上仅引用哈希。

```
对于大于 64 KB 的输入：
  1. 用户将输入上传到 IPFS（或 QFC 的存储层）
  2. 任务提交仅包含内容哈希（input_hash）
  3. 矿工使用哈希从 IPFS 获取输入数据
  4. 矿工在执行前验证数据与哈希匹配
  5. 结果沿用现有模式（<1MB 内联，>1MB 使用 IPFS CID）

InferenceTask {
    input_data: Vec<u8>,          // 用于小输入（文本提示词）
    input_cid: Option<String>,    // 用于大输入（音频、图像）— IPFS CID
}
```

这复用了推理结果存储中现有的 IPFS 基础设施。

---

## 8. GPU 层级重新定义

### 当前层级体系

```rust
pub enum GpuTier {
    Cold,   // 最低可用（8 GB）
    Warm,   // 中端（12-16 GB）
    Hot,    // 高端（24+ GB）
}
```

### 扩展方案

```rust
pub enum GpuTier {
    Cold,    // 消费级入门（8-10 GB）— RTX 3060/3070/4060
    Warm,    // 消费级中端（12-16 GB）— RTX 4070/4080
    Hot,     // 消费级高端（24 GB）— RTX 4090
    Ultra,   // 数据中心（48-80 GB）— A100/H100
    Secure,  // 支持 TEE（H100/B200 CC）— 机密推理（见文档 #19）
}
```

`Ultra` 层级支持需要数据中心 GPU 的大模型（70B+）。`Secure` 层级（来自隐私研究，见 [19-PRIVACY-AI-INFERENCE.md](19-PRIVACY-AI-INFERENCE.md)）支持机密推理。

> **序列化兼容性警告**（Issue #11）：`GpuTier` 使用 Borsh 序列化。
> 新增枚举变体（`Ultra`、`Secure`）将导致旧节点反序列化失败
>（类似于 qfc-core #31 中修复的 Account 结构体问题）。
>
> **迁移策略选项**：
> 1. **版本字段**：在序列化消息中添加协议版本；旧节点忽略未知层级
> 2. **硬分叉**：协调网络升级，所有节点同时更新
> 3. **保留变体**：现在预分配枚举槽位（例如 `Reserved1 = 3, Reserved2 = 4`）以避免未来的兼容性问题
>
> **建议**：选项 1（版本字段）最灵活。在添加新层级之前实施。

---

## 9. 模型治理演进

### 当前：静态注册表

模型在 `ModelRegistry::default_v2()` 中硬编码。添加新模型需要代码变更和节点升级。

### 建议：链上治理

```
1. 社区成员提交 ModelProposal（governance.rs 中已存在）
2. 验证者投票批准
3. 批准的模型添加到链上注册表
4. 矿工根据自身层级自动下载已批准的模型
5. 通过治理投票废弃模型
```

### 治理冷启动策略

> **Issue #11 反馈**：在治理系统参与者不足时，谁来批准模型？

| 阶段 | 审批权限 | 标准 |
|-------|-------------------|----------|
| **测试网 / 主网早期** | 核心团队多签（3-of-5） | 快速迭代，精选质量 |
| **增长阶段** | 核心团队 + PoC 分数前 10 的验证者 | 更广泛的输入，仍可管理 |
| **成熟阶段** | 完全链上治理投票 | 去中心化，社区驱动 |

### 模型下架流程

当模型被废弃时（例如 Qwen2.5 → Qwen3）：

```
1. 治理提案："废弃 qfc-llm-7b v1.0，替换为 qfc-llm-7b v2.0"
2. 公告期：2 周——两个版本同时活跃
3. 过渡期：2 周——旧模型在任务路由中权重降至 50%
4. 下架：旧模型从活跃注册表中移除
   - 引用旧模型的现有证明在链上仍然有效
   - 新任务不能使用旧模型
   - 矿工可以从缓存中清除旧模型以释放存储空间
```

### 模型质量保证

在批准前，模型应通过以下检查：
- **确定性检查**：相同输入 + 种子 → 在规范后端上产生相同输出（验证所需）
- **资源限制**：内存和计算在层级限制范围内
- **安全扫描**：无已知的模型投毒或后门风险
- **基准测试**：在标准数据集上达到最低质量阈值
- **权重哈希验证**：权重文件的 Blake3 哈希记录在提案中（见第 4.6 节）

---

## 10. 定价策略

### 当前费用模型

```
基础：1 GFLOP = 1e12 wei (0.000001 QFC)
层级乘数：Cold=1x，Warm=1.5x，Hot=2x
最低费用：0.0001 QFC
```

### 按任务类型的建议费用模型

| 任务类型 | 计价单位 | 基础费用乘数 | 理由 |
|-----------|-------------|-------------------|-----------|
| Embedding | 按请求 | 1x | 轻量、快速、固定成本 |
| Classification | 按请求 | 1x | 轻量、快速、固定成本 |
| SpeechToText | **按音频秒数** | 2x | 随输入时长扩展 |
| TextGeneration | **按输出 token 数** | 1.5x | 随生成长度扩展 |
| ImageGeneration | **按步数 × 分辨率** | 5x | 20 步 512px 与 50 步 1024px 成本差异巨大 |
| VisionLanguage | **按输出 token 数** | 3x | 图像编码（固定）+ 文本生成（可变） |

> **Issue #11 反馈**：静态乘数无法反映实际成本差异。
> 生成 10 个 token 与 1000 个 token 不应收取相同费用。

**动态费用公式**：
```
fee = base_rate × task_units × tier_multiplier × model_size_factor

其中：
  task_units =
    TextGeneration: actual_output_tokens
    SpeechToText: audio_duration_seconds
    ImageGeneration: steps × (width × height / 512²)
    Embedding/Classification: 1（固定）

  tier_multiplier = Cold:1x, Warm:1.5x, Hot:2x, Ultra:3x, Secure:4x
  model_size_factor = params_billions / 7  （以 7B 为基准归一化）
```

费用在提交时预估（用户支付最大值），完成后计算实际成本，差额退还。

---

## 11. 实施路线图

### 阶段 1：量化基础设施 + 文本模型扩展（3-4 周）

- 在 `download.rs` 和推理后端中实现 GGUF 模型加载路径
- 为 `ModelCache` 添加权重哈希验证（blake3）
- 为 `ModelInfo` 添加 HF revision 锁定
- 将 Qwen2.5-3B-GGUF 和 Qwen2.5-7B-GGUF 加入注册表
- 更新 `model_tier_and_memory()` 以适应新的模型规模分类
- 为每种任务类型定义 `VerificationMode` 以解决跨后端确定性问题

### 阶段 2a：SpeechToText（3-4 周）

- 为 `ComputeTaskType` 添加 `SpeechToText` 变体
- 通过 candle 实现 Whisper 后端
- 大文件输入通过 IPFS CID 传输（音频文件）
- 按音频秒数的动态定价

### 阶段 2b：ImageGeneration（6-8 周，独立分支）

> **Issue #11 反馈**：扩散管线是多模型的（Text Encoder → U-Net × N 步 → VAE Decoder）。
> 工程复杂度显著高于 LLM 自回归解码。
> 原先 4-6 周的估计过于乐观。

- 为 `ComputeTaskType` 添加 `ImageGeneration` 变体
- 通过 candle 实现 Stable Diffusion 1.5 管线（3 个子模型）
- 确定性种子验证策略（相同种子 + 相同 GGUF = 相同图像）
- 按步数 × 分辨率的动态定价

### 阶段 3：VisionLanguage + 治理（4-6 周）

- 为 `ComputeTaskType` 添加 `VisionLanguage` 变体
- 实现 Qwen-VL 后端
- 激活 `ModelGovernance` 的提案/投票工作流
- 实现模型下架流程
- 冷启动：核心团队多签审批

### 阶段 4：Ultra/Secure 层级（6-8 周）

- 添加 Ultra 和 Secure GPU 层级（附带序列化迁移策略）
- 大模型支持（70B+ 多 GPU）
- TEE 认证集成（见 [19-PRIVACY-AI-INFERENCE.md](19-PRIVACY-AI-INFERENCE.md)）

---

## 12. 企业需求对齐

基于市场数据（Akash、io.net、行业报告）：

| 企业使用场景 | 市场份额 | QFC 覆盖范围 |
|--------------------|-------------|--------------|
| 聊天机器人与推荐 | 38.91% | TextGeneration（Qwen/DeepSeek） |
| 语音转录 | 高 | SpeechToText（Whisper） |
| 嵌入/RAG | 高 | Embedding（MiniLM、BGE-M3） |
| 图像生成 | 增长中 | ImageGeneration（SD、FLUX） |
| 代码辅助 | 增长中 | TextGeneration（Qwen Coder 模型） |
| 隐私推理 | 新兴 | Secure 层级（TEE） |

QFC 扩展后的模型注册表将覆盖**超过 90% 的企业推理需求**。

---

## 参考文献

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
