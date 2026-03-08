# 09-AI-COMPUTE-NETWORK.md — QFC AI 算力网络设计

## 概述

QFC AI 算力网络将 PoC 共识机制中的"计算贡献"维度（20% 权重）从传统 PoW 哈希计算升级为**有实际价值的 AI 推理算力**。用户提供 GPU 算力执行 AI 推理任务，获得 QFC 代币奖励——让闲置显卡变成"AI 矿机"。

### 核心价值主张

| 传统 PoW 挖矿 | QFC AI 算力挖矿 |
|---------------|-----------------|
| 算力浪费在无意义哈希 | 算力用于真实 AI 推理任务 |
| 需要专用 ASIC 矿机 | 消费级 GPU 即可参与 |
| 只有一个维度：算力 | 多维度贡献（PoC 体系） |
| 矿工之间纯竞争 | 矿工之间可协作 |

### 与现有架构的关系

```
┌─────────────────────────────────────────────────────┐
│              QFC 区块链生态                           │
│                                                     │
│  ┌───────────────┐    本文档定义     ┌────────────┐  │
│  │ PoC 共识机制   │◄──────────────►│ AI 算力网络  │  │
│  │ (02-CONSENSUS) │  计算贡献维度    │ (本文档)     │  │
│  └───────┬───────┘                └─────┬──────┘  │
│          │                              │         │
│  ┌───────┴───────┐              ┌───────┴──────┐  │
│  │ 代币经济学     │              │ AI-VM        │  │
│  │ (03-TOKENOMICS)│              │ (智能合约层)  │  │
│  └───────────────┘              └──────────────┘  │
└─────────────────────────────────────────────────────┘
```

- **02-CONSENSUS-MECHANISM.md**：PoC 评分公式中的 `compute` 维度由本文档定义
- **03-TOKENOMICS.md**：AI 任务费用的分配规则与代币经济学对齐
- **AI-VM**（00-PROJECT-OVERVIEW.md 中规划）：链上合约可直接调用 AI 推理能力

---

## 1. 系统架构

### 1.1 总体架构

```
┌──────────────────────────────────────────────────────────┐
│                   任务提交方                              │
│   DApp / 企业 API / 链上合约（AI-VM）                     │
│   提交 AI 推理请求 + 支付 QFC                             │
└────────────────────────┬─────────────────────────────────┘
                         ▼
┌──────────────────────────────────────────────────────────┐
│              链上 AI Task Pool（智能合约）                 │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │ 任务注册      │  │ 费用托管      │  │ 结果验证       │  │
│  │ Task Registry │  │ Fee Escrow   │  │ Result Verify  │  │
│  └──────────────┘  └──────────────┘  └───────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │ 矿工注册      │  │ 模型注册      │  │ 奖励结算       │  │
│  │ Miner Reg.   │  │ Model Reg.   │  │ Reward Settle  │  │
│  └──────────────┘  └──────────────┘  └───────────────┘  │
└────────────────────────┬─────────────────────────────────┘
                         ▼
┌──────────────────────────────────────────────────────────┐
│              链下任务调度层 (Task Router)                  │
│                                                          │
│  - 按 GPU 能力匹配任务（Tier 分级）                       │
│  - 负载均衡 & 就近调度                                    │
│  - 任务超时重分配                                         │
│  - 挑战任务注入（防作弊）                                  │
└──────┬──────────────┬──────────────┬─────────────────────┘
       ▼              ▼              ▼
┌────────────┐ ┌────────────┐ ┌────────────┐
│ Tier 1     │ │ Tier 2     │ │ Tier 3     │
│ 4060Ti等   │ │ 3090/4080  │ │ A100/H100  │
│ 小型推理    │ │ 中型推理    │ │ 大型推理    │
│ qfc-miner  │ │ qfc-miner  │ │ qfc-miner  │
└────────────┘ └────────────┘ └────────────┘
```

### 1.2 组件职责

| 组件 | 位置 | 职责 |
|------|------|------|
| AI Task Pool | 链上（智能合约） | 任务/矿工/模型注册、费用托管、结果上链 |
| Task Router | 链下（P2P 网络层） | 任务分发、负载均衡、挑战注入 |
| qfc-miner | 矿工本地 | GPU 推理执行、结果提交、模型管理 |
| Verification Module | 链上 + 链下 | 结果验证、作弊检测、slash 触发 |

---

## 2. GPU 分级与任务类型

### 2.1 GPU Tier 分级

矿工注册时执行标准 Benchmark，链上记录能力等级：

```rust
#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum GpuTier {
    /// Tier 1: 消费级入门 (4-8 GB VRAM)
    /// 4060Ti, 3060, RX 7600 等
    Tier1,

    /// Tier 2: 消费级高端 (12-24 GB VRAM)
    /// 3090, 4080, 4090, RX 7900 XTX 等
    Tier2,

    /// Tier 3: 专业/数据中心 (40-80 GB VRAM)
    /// A100, H100, L40S 等
    Tier3,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct GpuProfile {
    /// GPU 型号（自动检测）
    pub model: String,

    /// 显存大小 (MB)
    pub vram_mb: u32,

    /// Benchmark 分数（标准化 0-10000）
    pub benchmark_score: u32,

    /// 自动分配的 Tier
    pub tier: GpuTier,

    /// 支持的推理框架
    pub supported_runtimes: Vec<InferenceRuntime>,
}
```

### 2.2 Benchmark 标准

```rust
/// 标准 Benchmark 任务集（注册时执行）
pub struct GpuBenchmark {
    tasks: Vec<BenchmarkTask>,
}

impl GpuBenchmark {
    pub fn standard() -> Self {
        Self {
            tasks: vec![
                // 1. 矩阵乘法吞吐（衡量原始算力）
                BenchmarkTask::MatMul { size: 4096, iterations: 100 },

                // 2. ResNet-50 推理（衡量 CV 推理能力）
                BenchmarkTask::ModelInference {
                    model: "resnet50",
                    batch_size: 32,
                    iterations: 50,
                },

                // 3. BERT-base 推理（衡量 NLP 推理能力）
                BenchmarkTask::ModelInference {
                    model: "bert-base",
                    batch_size: 16,
                    iterations: 50,
                },

                // 4. 显存带宽测试
                BenchmarkTask::MemoryBandwidth { size_mb: 1024 },
            ],
        }
    }

    /// 执行 Benchmark，返回分数 + Tier
    pub fn run(&self) -> BenchmarkResult {
        let scores: Vec<f64> = self.tasks.iter()
            .map(|task| task.execute())
            .collect();

        let total_score = (scores.iter().sum::<f64>() / scores.len() as f64 * 1000.0) as u32;

        let tier = match total_score {
            0..=2999     => GpuTier::Tier1,
            3000..=6999  => GpuTier::Tier2,
            _            => GpuTier::Tier3,
        };

        BenchmarkResult { score: total_score, tier }
    }
}
```

**参考分数范围：**

| GPU | Benchmark 分数 (预估) | Tier | VRAM |
|-----|----------------------|------|------|
| RTX 4060 Ti | ~2,800 | Tier 1 | 8 GB |
| RTX 3060 12GB | ~2,200 | Tier 1 | 12 GB |
| RTX 3090 | ~4,500 | Tier 2 | 24 GB |
| RTX 4080 | ~5,200 | Tier 2 | 16 GB |
| RTX 4090 | ~6,800 | Tier 2 | 24 GB |
| A100 80GB | ~8,500 | Tier 3 | 80 GB |
| H100 | ~9,800 | Tier 3 | 80 GB |

### 2.3 任务类型与 Tier 匹配

```rust
#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum TaskType {
    /// 图像分类 (ResNet, EfficientNet 等)
    ImageClassification,

    /// 目标检测 (YOLO 等)
    ObjectDetection,

    /// OCR 文字识别
    OCR,

    /// 文本 Embedding 生成
    TextEmbedding,

    /// 图像生成 (Stable Diffusion 等)
    ImageGeneration,

    /// 小型 LLM 推理 (<=7B 参数)
    SmallLLM,

    /// 中型 LLM 推理 (7B-30B 参数)
    MediumLLM,

    /// 大型 LLM 推理 (>30B 参数)
    LargeLLM,

    /// 语音转文字
    SpeechToText,

    /// 自定义 ONNX 模型
    CustomONNX,
}

impl TaskType {
    /// 该任务类型需要的最低 Tier
    pub fn min_tier(&self) -> GpuTier {
        match self {
            Self::ImageClassification => GpuTier::Tier1,
            Self::ObjectDetection     => GpuTier::Tier1,
            Self::OCR                 => GpuTier::Tier1,
            Self::TextEmbedding       => GpuTier::Tier1,
            Self::SpeechToText        => GpuTier::Tier1,
            Self::CustomONNX          => GpuTier::Tier1,  // 取决于模型大小
            Self::ImageGeneration     => GpuTier::Tier2,
            Self::SmallLLM            => GpuTier::Tier2,
            Self::MediumLLM           => GpuTier::Tier2,
            Self::LargeLLM            => GpuTier::Tier3,
        }
    }

    /// 预估 VRAM 需求 (MB)
    pub fn estimated_vram_mb(&self) -> u32 {
        match self {
            Self::ImageClassification => 512,
            Self::ObjectDetection     => 1024,
            Self::OCR                 => 512,
            Self::TextEmbedding       => 1024,
            Self::SpeechToText        => 1536,
            Self::CustomONNX          => 2048,  // 默认值，实际按模型
            Self::ImageGeneration     => 6144,
            Self::SmallLLM            => 8192,
            Self::MediumLLM           => 16384,
            Self::LargeLLM            => 40960,
        }
    }
}
```

---

## 3. 任务生命周期

### 3.1 状态机

```
                    提交任务
                       │
                       ▼
               ┌───────────────┐
               │   Pending     │ 等待分配
               └───────┬───────┘
                       │ Task Router 分配
                       ▼
               ┌───────────────┐
               │   Assigned    │ 已分配给矿工
               └───────┬───────┘
                       │
              ┌────────┼────────┐
              ▼        │        ▼
     ┌──────────┐      │  ┌──────────┐
     │ Running  │      │  │ Timeout  │ 超时 → 重新分配
     └────┬─────┘      │  └──────────┘
          │            │
          ▼            │
  ┌───────────────┐    │
  │  Submitted    │ 矿工提交结果
  └───────┬───────┘    │
          │            │
     ┌────┴────┐       │
     ▼         ▼       │
┌────────┐ ┌────────┐  │
│Verified│ │Disputed│  │ 验证通过 / 被挑战
└────┬───┘ └────┬───┘  │
     │          │      │
     ▼          ▼      │
┌────────┐ ┌────────┐  │
│  Paid  │ │Slashed │  │ 结算 / 惩罚
└────────┘ └────────┘  │
```

### 3.2 任务数据结构

```rust
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct AITask {
    /// 任务 ID（链上唯一）
    pub task_id: Hash,

    /// 任务类型
    pub task_type: TaskType,

    /// 使用的模型 ID（链上模型注册表）
    pub model_id: Hash,

    /// 输入数据（或 IPFS/Arweave CID）
    pub input: TaskInput,

    /// 最大执行时间 (秒)
    pub timeout_secs: u32,

    /// 任务报酬 (QFC wei)
    pub reward: U256,

    /// 要求的最低 GPU Tier
    pub min_tier: GpuTier,

    /// 提交者地址
    pub submitter: Address,

    /// 当前状态
    pub status: TaskStatus,

    /// 分配的矿工（如已分配）
    pub assigned_miner: Option<Address>,

    /// 创建时间
    pub created_at: u64,

    /// 是否为挑战任务（验证用，矿工不可见此字段）
    pub is_challenge: bool,

    /// 挑战任务的预期结果（仅链下存储）
    pub expected_result: Option<Vec<u8>>,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum TaskInput {
    /// 内联数据（小于 256KB）
    Inline(Vec<u8>),

    /// IPFS CID
    IPFS(String),

    /// Arweave TX ID
    Arweave(String),
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum TaskStatus {
    Pending,
    Assigned { miner: Address, assigned_at: u64 },
    Running { started_at: u64 },
    Submitted { result_hash: Hash, submitted_at: u64 },
    Verified { result: Vec<u8> },
    Disputed { challenger: Address },
    Paid { amount: U256 },
    Slashed { miner: Address, amount: U256 },
    Timeout,
    Cancelled,
}
```

### 3.3 任务提交（链上合约）

```rust
/// AI Task Pool 合约接口
pub trait AITaskPool {
    /// 提交 AI 推理任务
    /// 调用者需同时支付 reward 金额到合约（escrow）
    fn submit_task(
        task_type: TaskType,
        model_id: Hash,
        input: TaskInput,
        timeout_secs: u32,
        min_tier: GpuTier,
    ) -> TaskId;

    /// 取消未分配的任务（退还 reward）
    fn cancel_task(task_id: TaskId);

    /// 矿工认领任务
    fn claim_task(task_id: TaskId);

    /// 矿工提交结果
    fn submit_result(task_id: TaskId, result_hash: Hash, result_data: Vec<u8>);

    /// 挑战某个结果（需缴纳保证金）
    fn challenge_result(task_id: TaskId, deposit: U256);

    /// 仲裁（由 N 个验证节点重新执行）
    fn arbitrate(task_id: TaskId, results: Vec<(Address, Vec<u8>)>);
}
```

---

## 4. 矿工客户端 (qfc-miner)

### 4.1 架构

```
qfc-miner
├── 网络模块
│   ├── P2P 节点（libp2p）          # 与 Task Router 通信
│   └── RPC Client                  # 与 QFC 链交互
│
├── 任务管理
│   ├── Task Fetcher                # 拉取/接收任务
│   ├── Task Queue                  # 本地任务队列
│   └── Result Submitter            # 结果提交
│
├── 推理引擎
│   ├── ONNX Runtime                # 通用推理后端
│   ├── TensorRT (可选)             # NVIDIA 优化推理
│   └── Model Manager               # 模型下载/缓存/版本管理
│
├── GPU 管理
│   ├── Device Monitor              # GPU 使用率/温度/功耗
│   ├── VRAM Allocator              # 显存分配
│   └── Power Limiter               # 功耗限制
│
└── 身份与安全
    ├── Wallet Signer               # 结果签名
    └── Benchmark Runner            # GPU 基准测试
```

### 4.2 配置文件

```yaml
# qfc-miner.yaml

# ===== 基础配置 =====
wallet_address: "0xYourWalletAddress"
private_key_file: "./miner.key"       # 加密存储的私钥文件
rpc_endpoint: "https://rpc.testnet.qfc.network"

# ===== GPU 配置 =====
gpu:
  device_id: 0                        # GPU 设备编号（多卡选择）
  max_vram_usage_mb: 7168             # 最大显存使用（留 1GB 给系统）
  max_power_watts: 150                # 功耗限制
  max_temperature_c: 83               # 温度上限，超过自动降频
  runtime: "onnxruntime"              # 推理后端: onnxruntime / tensorrt

# ===== 模型管理（三层调度） =====
# 详见 4.5 节 模型调度策略
models:
  # Hot Layer: 常驻 GPU，即时响应 (<50ms)
  hot:
    - id: "efficientnet-b4"           # 图像分类, ~200MB
    - id: "bge-base-en-v1.5"         # 文本 Embedding, ~400MB
    - id: "yolov8s"                  # 目标检测, ~100MB

  # Warm Pool: 大模型按需加载 (2-5s cold load)
  warm:
    max_vram_mb: 5000                 # Warm 层最大显存
    allowed_models:                   # 白名单，不在列表里的不接
      - "llama-3-8b-q4"
      - "mistral-7b-q4"
      - "whisper-small"
    preload: "llama-3-8b-q4"         # 启动时预加载

  # Cold Cache: 磁盘缓存
  cache:
    dir: "./models"
    max_disk_gb: 20
    auto_download: true
    eviction_policy: "lru"

  # VRAM 预算分配
  vram_budget:
    reserved_mb: 800                  # 系统预留
    hot_max_mb: 1000                  # Hot 层上限
    warm_max_mb: 5000                 # Warm 层上限
    buffer_mb: 1200                   # 推理缓冲 (KV Cache 等)

# ===== 挖矿配置 =====
mining:
  # 接受的任务类型（不配置则接受所有匹配 Tier 的任务）
  task_types:
    - image_classification
    - text_embedding
    - ocr
    - object_detection
    - speech_to_text
    - small_llm                       # 需要 warm 层有对应模型

  max_concurrent_tasks: 3             # 小模型并发数（LLM 固定为 1）
  min_reward_qfc: 0.005               # 最低接受的单任务报酬

# ===== 网络配置 =====
network:
  p2p_port: 30304
  p2p_bootnodes:
    - "/ip4/bootnode1.qfc.network/tcp/30304/p2p/12D3..."
  bandwidth_limit_mbps: 100

# ===== 可选：同时做验证者 =====
validator:
  enabled: false
  # stake_amount: 10000               # 质押数量（QFC）

# ===== 监控 =====
monitoring:
  prometheus_port: 9100               # Prometheus metrics 端口
  log_level: "info"                   # debug / info / warn / error
  log_file: "./logs/miner.log"
```

### 4.3 启动流程

```rust
pub async fn run_miner(config: MinerConfig) -> Result<(), Error> {
    // 1. 检测 GPU
    let gpu = detect_gpu(config.gpu.device_id)?;
    info!("GPU detected: {} ({} MB VRAM)", gpu.model, gpu.vram_mb);

    // 2. 运行 Benchmark（首次或版本更新时）
    let benchmark = if needs_benchmark(&gpu) {
        info!("Running GPU benchmark...");
        let result = GpuBenchmark::standard().run(&gpu);
        info!("Benchmark score: {} ({})", result.score, result.tier);
        save_benchmark(&result)?;
        result
    } else {
        load_benchmark()?
    };

    // 3. 连接 QFC 网络
    let rpc = RpcClient::new(&config.rpc_endpoint);
    let p2p = P2PNode::new(&config.network).await?;

    // 4. 链上注册矿工（如果未注册）
    if !is_miner_registered(&rpc, &config.wallet_address).await? {
        info!("Registering as compute provider...");
        register_miner(&rpc, &config, &benchmark).await?;
    }

    // 5. 初始化推理引擎
    let engine = InferenceEngine::new(&config.gpu)?;

    // 6. 初始化模型管理器
    let model_manager = ModelManager::new(
        &config.mining.model_cache_dir,
        config.mining.model_cache_max_gb,
    );

    // 7. 启动任务循环
    let task_queue = TaskQueue::new(config.mining.max_concurrent_tasks);

    info!("Miner started. Waiting for tasks...");

    loop {
        tokio::select! {
            // 接收新任务
            task = p2p.receive_task() => {
                if let Ok(task) = task {
                    if should_accept(&task, &config, &benchmark) {
                        task_queue.enqueue(task);
                    }
                }
            }

            // 执行队列中的任务
            _ = task_queue.has_pending() => {
                if let Some(task) = task_queue.dequeue() {
                    let engine = engine.clone();
                    let model_mgr = model_manager.clone();
                    let rpc = rpc.clone();

                    tokio::spawn(async move {
                        match execute_task(&task, &engine, &model_mgr).await {
                            Ok(result) => {
                                submit_result(&rpc, &task, &result).await;
                                info!("+{} QFC ✓ (task: {})",
                                    format_qfc(task.reward), short_hash(task.task_id));
                            }
                            Err(e) => {
                                warn!("Task failed: {} (task: {})",
                                    e, short_hash(task.task_id));
                            }
                        }
                    });
                }
            }

            // GPU 健康监控
            _ = tokio::time::sleep(Duration::from_secs(10)) => {
                let status = gpu.get_status()?;
                if status.temperature_c > config.gpu.max_temperature_c {
                    warn!("GPU temperature {}°C exceeds limit, throttling...",
                        status.temperature_c);
                    task_queue.pause();
                }
            }
        }
    }
}
```

### 4.4 任务执行流程

```rust
async fn execute_task(
    task: &AITask,
    engine: &InferenceEngine,
    model_scheduler: &mut ModelScheduler,
) -> Result<TaskResult, Error> {
    // 1. 通过调度器获取模型（Hot/Warm 命中或 Cold 加载）
    let (model, latency) = model_scheduler.get_model(&task.model_id).await?;

    match latency {
        ScheduleLatency::Immediate => {
            debug!("Model {} hit in Hot/Warm layer", task.model_id);
        }
        ScheduleLatency::ColdLoad { ms } => {
            info!("Model {} loaded from disk in {}ms", task.model_id, ms);
        }
    }

    // 2. 获取输入数据
    let input_data = match &task.input {
        TaskInput::Inline(data) => data.clone(),
        TaskInput::IPFS(cid)   => fetch_from_ipfs(cid).await?,
        TaskInput::Arweave(id) => fetch_from_arweave(id).await?,
    };

    // 3. 预处理输入
    let preprocessed = preprocess(&input_data, &task.task_type)?;

    // 4. 执行推理
    let start = Instant::now();
    let output = model.session.run(preprocessed)?;
    let inference_time = start.elapsed();

    // 5. 后处理输出
    let result = postprocess(output, &task.task_type)?;

    // 6. 签名结果
    let result_hash = blake3::hash(&result);
    let signature = sign_result(&result_hash)?;

    Ok(TaskResult {
        task_id: task.task_id,
        result_data: result,
        result_hash,
        inference_time_ms: inference_time.as_millis() as u32,
        signature,
    })
}
```

### 4.5 模型调度策略

每个矿工**不是只跑一个模型**，而是同时管理多个模型，通过三层缓存实现高效调度：

#### VRAM 分层架构

```
┌──────────────────────────────────────────────────────┐
│                   GPU VRAM                            │
│                                                      │
│  ┌────────────────────────────────────────────────┐  │
│  │  Hot Layer (常驻，即时响应 <50ms)               │  │
│  │                                                │  │
│  │  多个小模型可以同时常驻：                        │  │
│  │  efficientnet-b4    200MB  ← 图像分类          │  │
│  │  bge-base-en        400MB  ← 文本 Embedding    │  │
│  │  yolov8s            100MB  ← 目标检测          │  │
│  │                     ─────                      │  │
│  │                     700MB                      │  │
│  └────────────────────────────────────────────────┘  │
│                                                      │
│  ┌────────────────────────────────────────────────┐  │
│  │  Warm Layer (已加载，可立即执行 <100ms)          │  │
│  │                                                │  │
│  │  同一时刻只放 1 个大模型：                       │  │
│  │  llama-3-8b-q4      4.5GB  ← LLM 推理         │  │
│  │                                                │  │
│  │  按 LRU 淘汰，新大模型进来时卸载旧的            │  │
│  └────────────────────────────────────────────────┘  │
│                                                      │
│  预留: ~2.8GB (系统 + 峰值缓冲)                      │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│              本地磁盘 Cold Layer                      │
│                                                      │
│  whisper-small        500MB   ← 按需加载 (2-5s)     │
│  mistral-7b-q4        4.2GB   ← 按需加载 (3-5s)     │
│  ...更多模型按需下载                                  │
│                                                      │
│  磁盘缓存上限: 可配置 (默认 20GB)                     │
└──────────────────────────────────────────────────────┘
```

#### 4060Ti 8GB 典型 VRAM 分配

| 层级 | 分配 | 用途 |
|------|------|------|
| 系统预留 | ~800MB | CUDA 上下文、驱动 |
| Hot Layer | ~700MB | 3-4 个小模型常驻，秒级响应 |
| Warm Layer | ~4500MB | 1 个 7B-8B LLM，按需加载 |
| 缓冲 | ~2000MB | 推理时的临时张量、KV Cache |

关键约束：**小模型可以并发 2-3 个任务，但 LLM 同一时刻只能跑 1 个推理请求**。

#### 模型调度器实现

```rust
/// 三层模型调度器
pub struct ModelScheduler {
    /// Hot: 常驻 GPU，<50ms 响应
    hot_models: Vec<LoadedModel>,

    /// Warm: 已在 GPU 但可被卸载，<100ms 响应
    warm_model: Option<LoadedModel>,

    /// Cold: 在磁盘，需要 2-5s 加载
    cold_cache: LruCache<Hash, CachedModel>,

    /// VRAM 预算
    vram_budget: VramBudget,
}

pub struct VramBudget {
    pub total_mb: u32,
    pub hot_budget_mb: u32,    // 小模型固定预算
    pub warm_budget_mb: u32,   // 大模型弹性预算
    pub reserved_mb: u32,      // 系统预留
}

impl ModelScheduler {
    /// 收到任务时的调度决策
    pub async fn get_model(
        &mut self,
        model_id: &Hash,
    ) -> Result<(&LoadedModel, ScheduleLatency), Error> {

        // 1. Hot 命中 → 直接跑，零等待
        if let Some(model) = self.hot_models.iter().find(|m| m.id == *model_id) {
            return Ok((model, ScheduleLatency::Immediate));
        }

        // 2. Warm 命中 → 几乎不等
        if let Some(ref model) = self.warm_model {
            if model.id == *model_id {
                return Ok((model, ScheduleLatency::Immediate));
            }
        }

        // 3. Cold 命中 → 需要从磁盘加载到 GPU
        if let Some(cached) = self.cold_cache.get(model_id) {
            let needed_mb = cached.vram_required_mb;

            // 如果 warm 槽被占用，先卸载
            if self.warm_model.is_some() && needed_mb > self.available_warm_vram() {
                let old = self.warm_model.take().unwrap();
                old.unload_from_gpu()?;
                info!("Evicted warm model: {} (freed {}MB)",
                    old.name, old.vram_mb);
            }

            let load_start = Instant::now();
            let model = cached.load_to_gpu()?;
            let load_time = load_start.elapsed();

            info!("Loaded model to warm: {} ({}MB, took {:?})",
                model.name, model.vram_mb, load_time);

            self.warm_model = Some(model);
            return Ok((
                self.warm_model.as_ref().unwrap(),
                ScheduleLatency::ColdLoad { ms: load_time.as_millis() as u32 },
            ));
        }

        // 4. 本地没有 → 需要先下载再加载
        Err(Error::ModelNotCached(*model_id))
    }

    /// 注册矿工时，上报当前已加载的模型列表
    /// Task Router 用这个信息做全局调度
    pub fn report_loaded_models(&self) -> Vec<ModelStatus> {
        let mut models = Vec::new();

        for m in &self.hot_models {
            models.push(ModelStatus {
                model_id: m.id,
                layer: ModelLayer::Hot,
                ready: true,
            });
        }

        if let Some(ref m) = self.warm_model {
            models.push(ModelStatus {
                model_id: m.id,
                layer: ModelLayer::Warm,
                ready: true,
            });
        }

        for (id, _) in self.cold_cache.iter() {
            models.push(ModelStatus {
                model_id: *id,
                layer: ModelLayer::Cold,
                ready: false,  // 需要加载时间
            });
        }

        models
    }
}

pub enum ScheduleLatency {
    /// Hot/Warm 命中，无等待
    Immediate,
    /// 从磁盘加载，有延迟
    ColdLoad { ms: u32 },
}
```

#### Task Router 全局模型感知调度

Task Router 维护所有矿工的模型加载状态，优先把任务分给已加载对应模型的矿工：

```rust
/// Task Router 的矿工模型状态表
pub struct MinerModelRegistry {
    /// 矿工地址 → 当前加载的模型列表
    miner_models: HashMap<Address, Vec<ModelStatus>>,
}

impl MinerModelRegistry {
    /// 为任务选择最优矿工
    pub fn select_miner(
        &self,
        task: &AITask,
        available_miners: &[MinerInfo],
    ) -> Option<Address> {
        let model_id = &task.model_id;

        // 优先级 1: 模型在 Hot 层的矿工（零切换成本）
        let hot_miners: Vec<_> = available_miners.iter()
            .filter(|m| self.has_model_in_layer(m.address, model_id, ModelLayer::Hot))
            .collect();
        if !hot_miners.is_empty() {
            return Some(select_least_loaded(&hot_miners));
        }

        // 优先级 2: 模型在 Warm 层的矿工
        let warm_miners: Vec<_> = available_miners.iter()
            .filter(|m| self.has_model_in_layer(m.address, model_id, ModelLayer::Warm))
            .collect();
        if !warm_miners.is_empty() {
            return Some(select_least_loaded(&warm_miners));
        }

        // 优先级 3: 模型在 Cold 层的矿工（需要加载，但不用下载）
        let cold_miners: Vec<_> = available_miners.iter()
            .filter(|m| self.has_model_in_layer(m.address, model_id, ModelLayer::Cold))
            .collect();
        if !cold_miners.is_empty() {
            return Some(select_least_loaded(&cold_miners));
        }

        // 优先级 4: 任意满足 Tier 要求的矿工（需要下载模型）
        let any_miners: Vec<_> = available_miners.iter()
            .filter(|m| m.gpu_tier >= task.min_tier)
            .collect();
        if !any_miners.is_empty() {
            return Some(select_least_loaded(&any_miners));
        }

        None  // 无可用矿工
    }
}
```

**全局效果**：网络中 1000 个矿工可以覆盖上百种模型，但每个矿工只需维护几个。Task Router 确保任务被分配到最合适的矿工，最小化模型切换开销。

#### 矿工配置文件（模型部分）

```yaml
# qfc-miner.yaml — 模型管理配置

models:
  # ===== Hot Layer: 常驻 GPU，适合高频小任务 =====
  hot:
    - id: "efficientnet-b4"       # 图像分类
      vram_mb: 200
    - id: "bge-base-en-v1.5"     # 文本 Embedding
      vram_mb: 400
    - id: "yolov8s"              # 目标检测
      vram_mb: 100

  # ===== Warm Pool: 允许加载的大模型 =====
  warm:
    max_vram_mb: 5000             # Warm 层最大显存预算
    allowed_models:               # 白名单（不在列表里的 LLM 任务不接）
      - "llama-3-8b-q4"
      - "mistral-7b-q4"
      - "whisper-small"
    preload: "llama-3-8b-q4"     # 启动时预加载的默认大模型

  # ===== Cold Cache: 磁盘缓存 =====
  cache:
    dir: "./models"
    max_disk_gb: 20               # 磁盘缓存上限
    auto_download: true           # 自动下载白名单中的模型
    eviction_policy: "lru"        # 磁盘满时淘汰策略

  # ===== VRAM 预算 =====
  vram_budget:
    reserved_mb: 800              # 系统预留
    hot_max_mb: 1000              # Hot 层上限
    warm_max_mb: 5000             # Warm 层上限
    buffer_mb: 1200               # 推理缓冲（KV Cache 等）
```

#### 实际运行中的 4060Ti 8GB 表现

```
场景 1: 持续接收 Embedding 任务
  → bge-base-en 在 Hot 层，每个请求 ~10ms
  → 可并发 3 个请求
  → 吞吐: ~300 requests/s

场景 2: 交替接收分类 + Embedding 任务
  → 两个模型都在 Hot 层，零切换
  → 总吞吐: ~200-400 requests/s

场景 3: 接收一个 LLM 推理任务
  → 如果 llama-3-8b 在 Warm 层: 立即开始，~40 tokens/s
  → 如果需要从磁盘加载: 等 3-5 秒，然后 ~40 tokens/s
  → LLM 执行期间，Hot 层的小模型仍可并发接其他任务

场景 4: 连续接收同一个 LLM 的多个请求
  → 第一个请求可能有加载延迟
  → 后续请求零延迟（模型已在 Warm 层）
  → Task Router 会把同模型任务连续分给同一矿工
```

---

## 5. 防作弊与验证机制

### 5.1 三层验证体系

```
┌──────────────────────────────────────────────────────┐
│ Layer 1: 注册验证                                     │
│ - GPU Benchmark 分数校验                               │
│ - 已知 GPU 型号 → 分数范围比对                          │
│ - 虚假硬件声明 → 拒绝注册                              │
└──────────────────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────┐
│ Layer 2: 运行时挑战 (Challenge Tasks)                  │
│ - 随机插入已知答案的任务（占总任务 ~5%）                 │
│ - 矿工无法区分挑战任务和真实任务                        │
│ - 答案偏差超过阈值 → 扣信誉分                          │
│ - 连续失败 → slash + 禁入                              │
└──────────────────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────┐
│ Layer 3: 冗余验证 (Redundant Execution)               │
│ - 高价值任务（reward > 阈值）发给 3 个矿工              │
│ - 取多数一致结果                                       │
│ - 不一致的矿工触发更多挑战任务                          │
│ - 持续不一致 → slash                                  │
└──────────────────────────────────────────────────────┘
```

### 5.2 挑战任务机制

```rust
/// 挑战任务生成器（由 Task Router 运行）
pub struct ChallengeGenerator {
    /// 预计算的挑战任务库
    challenge_pool: Vec<ChallengeTask>,

    /// 挑战任务注入比例
    challenge_ratio: f64,  // 默认 0.05 (5%)
}

#[derive(Clone)]
pub struct ChallengeTask {
    /// 伪装成普通任务
    pub task: AITask,

    /// 预期的正确结果
    pub expected_output: Vec<u8>,

    /// 允许的误差范围（浮点数结果）
    pub tolerance: f64,
}

impl ChallengeGenerator {
    /// 决定下一个任务是否应该是挑战任务
    pub fn should_inject_challenge(&self, miner: &Address) -> bool {
        let miner_stats = get_miner_stats(miner);

        // 新矿工：更高挑战频率（10%）
        if miner_stats.total_tasks < 100 {
            return random::<f64>() < 0.10;
        }

        // 信誉低的矿工：更高挑战频率
        if miner_stats.reputation < 0.8 {
            return random::<f64>() < 0.08;
        }

        // 正常矿工：标准 5%
        random::<f64>() < self.challenge_ratio
    }

    /// 验证挑战任务结果
    pub fn verify_challenge(
        &self,
        challenge: &ChallengeTask,
        actual_output: &[u8],
    ) -> ChallengeVerdict {
        let similarity = compute_similarity(
            &challenge.expected_output,
            actual_output,
        );

        if similarity >= (1.0 - challenge.tolerance) {
            ChallengeVerdict::Passed
        } else if similarity >= 0.5 {
            ChallengeVerdict::Suspicious { similarity }
        } else {
            ChallengeVerdict::Failed { similarity }
        }
    }
}

pub enum ChallengeVerdict {
    Passed,
    Suspicious { similarity: f64 },
    Failed { similarity: f64 },
}
```

### 5.3 惩罚规则（与 PoC Slashing 对齐）

| 违规行为 | 惩罚 | 禁入时间 |
|---------|------|---------|
| 挑战任务失败（单次） | 信誉分 -5% | 无 |
| 挑战任务连续失败 3 次 | 罚没质押 5% + 信誉分 -20% | 3 天 |
| 提交伪造结果 | 罚没质押 20% | 30 天 |
| 虚假 GPU 声明 | 罚没质押 50% | 永久 |
| 冗余验证不一致 | 信誉分 -10% | 无（触发更多挑战） |

```rust
/// AI 矿工惩罚（扩展 02-CONSENSUS 的 SlashableOffense）
pub enum MinerOffense {
    /// 挑战失败
    ChallengeFailed { consecutive_count: u32 },

    /// 提交伪造结果（证据：冗余执行对比）
    FakeResult { task_id: Hash, evidence: Vec<u8> },

    /// 虚假硬件声明
    FakeGpuClaim { claimed: GpuProfile, actual: GpuProfile },

    /// 任务超时率过高（>30%）
    HighTimeoutRate { rate: f64 },
}

fn slash_miner(miner: Address, offense: MinerOffense) -> SlashResult {
    let stake = get_stake(miner);

    let (slash_percent, jail_days) = match offense {
        MinerOffense::ChallengeFailed { consecutive_count } => {
            if consecutive_count >= 3 {
                (5, 3)
            } else {
                (0, 0)  // 只扣信誉分
            }
        },
        MinerOffense::FakeResult { .. } => (20, 30),
        MinerOffense::FakeGpuClaim { .. } => (50, 365 * 100),  // 永久
        MinerOffense::HighTimeoutRate { .. } => (1, 1),
    };

    execute_slash(miner, stake * slash_percent / 100, jail_days)
}
```

---

## 6. 与 PoC 共识集成

### 6.1 计算贡献分更新

替换 `02-CONSENSUS-MECHANISM.md` 中的计算贡献维度：

```rust
/// 更新后的计算贡献评分（替代原始 hashrate 方式）
fn calculate_compute_contribution(node: &ValidatorNode) -> f64 {
    // 如果节点不提供 AI 算力，此项为 0
    if !node.provides_ai_compute {
        return 0.0;
    }

    let miner_stats = get_miner_stats(&node.address);

    // 1. 任务完成量占比 (40%)
    let task_completion_ratio = miner_stats.completed_tasks as f64
        / total_completed_tasks as f64;

    // 2. 推理准确率 (40%)
    //    基于挑战任务通过率
    let accuracy = miner_stats.challenge_pass_rate;

    // 3. 响应速度 (20%)
    //    相对于任务 timeout 的执行效率
    let speed_score = if miner_stats.avg_completion_ratio > 0.0 {
        (1.0 - miner_stats.avg_completion_ratio).max(0.0)
    } else {
        0.0
    };

    task_completion_ratio * 0.4 + accuracy * 0.4 + speed_score * 0.2
}
```

### 6.2 完整 PoC 评分公式（含 AI 算力）

```rust
/// 完整贡献评分（更新版）
fn calculate_contribution_score(node: &ValidatorNode) -> f64 {
    let mut score = 0.0;

    // 1. 质押贡献 (30%)
    let stake_ratio = node.stake as f64 / total_stake as f64;
    score += stake_ratio * 0.30;

    // 2. AI 计算贡献 (20%) ← 从 PoW hashrate 改为 AI 算力
    let compute = calculate_compute_contribution(node);
    score += compute * 0.20;

    // 3. 在线时长 (15%)
    score += node.uptime_percentage * 0.15;

    // 4. 验证准确率 (15%)
    score += node.validation_accuracy * 0.15;

    // 5. 网络服务质量 (10%)
    let latency_score = 1.0 / (1.0 + node.avg_latency_ms / 100.0);
    let bandwidth_score = (node.bandwidth_mbps / 1000.0).min(1.0);
    score += (latency_score * 0.6 + bandwidth_score * 0.4) * 0.10;

    // 6. 存储贡献 (5%)
    let storage_ratio = node.storage_provided_gb as f64 / total_storage_gb as f64;
    score += storage_ratio * 0.05;

    // 7. 历史信誉 (5%)
    score += calculate_reputation(&node.history) * 0.05;

    // 应用网络状态乘数
    score *= get_network_multiplier(node);

    score
}
```

### 6.3 纯 GPU 矿工（不质押）的收益路径

PoC 的核心优势：**不质押也能参与，不提供算力也能参与**。

```
场景 A：纯 GPU 矿工（有 4060Ti，没有 QFC 质押）

  贡献分 = 质押(30%) × 0.0     = 0.000
         + 计算(20%) × 0.8     = 0.160  ← 持续跑 AI 任务
         + 在线(15%) × 0.95    = 0.143  ← 7×24 在线
         + 准确率(15%) × 0.98  = 0.147  ← 高质量完成
         + 网络(10%) × 0.70    = 0.070
         + 存储(5%) × 0.10     = 0.005
         + 信誉(5%) × 0.50     = 0.025  ← 新矿工，还在积累
         ─────────────────────────────
         总分 ≈ 0.55

  收益来源：
  ① AI 任务的直接报酬（与贡献分无关，按任务计费）
  ② 区块奖励分成（按贡献分比例）

场景 B：纯质押用户（有 QFC，没有 GPU）

  贡献分 = 质押(30%) × 0.5     = 0.150  ← 质押了不少
         + 计算(20%) × 0.0     = 0.000  ← 不提供算力
         + 在线(15%) × 0.90    = 0.135
         + 准确率(15%) × 0.95  = 0.143
         + 网络(10%) × 0.60    = 0.060
         + 存储(5%) × 0.05     = 0.003
         + 信誉(5%) × 0.80     = 0.040
         ─────────────────────────────
         总分 ≈ 0.53

场景 C：GPU + 质押（既有 4060Ti，又质押了 QFC）

  贡献分 = 质押(30%) × 0.3     = 0.090
         + 计算(20%) × 0.8     = 0.160
         + 在线(15%) × 0.95    = 0.143
         + 准确率(15%) × 0.98  = 0.147
         + 网络(10%) × 0.70    = 0.070
         + 存储(5%) × 0.10     = 0.005
         + 信誉(5%) × 0.80     = 0.040
         ─────────────────────────────
         总分 ≈ 0.65  ← 最高，因为多维度都有贡献
```

---

## 7. 代币经济学扩展

### 7.1 AI 任务费用流

与 `03-TOKENOMICS.md` 的费用分配框架一致：

```
任务提交者支付 QFC
         │
         ▼
┌─────────────────────┐
│   总任务费 = 100%    │
└─────────┬───────────┘
          │
   ┌──────┴──────┬──────────────┐
   ▼             ▼              ▼
┌────────┐  ┌────────┐   ┌──────────┐
│  70%   │  │  10%   │   │   20%    │
│ 执行矿工│  │验证节点 │   │   销毁   │
└────────┘  └────────┘   └──────────┘
```

### 7.2 AI 任务定价

```rust
/// 任务定价参考（链上可通过治理调整）
pub struct TaskPricing {
    /// 基础费 = task_type 基础价 × 模型大小系数
    pub base_fee: U256,

    /// 优先费 = 用户自定义（加速匹配）
    pub priority_fee: U256,
}

impl TaskPricing {
    /// 参考价格表 (单位: QFC)
    pub fn reference_price(task_type: &TaskType) -> f64 {
        match task_type {
            TaskType::ImageClassification => 0.01,
            TaskType::ObjectDetection     => 0.02,
            TaskType::OCR                 => 0.01,
            TaskType::TextEmbedding       => 0.01,
            TaskType::SpeechToText        => 0.03,
            TaskType::CustomONNX          => 0.02,
            TaskType::ImageGeneration     => 0.10,
            TaskType::SmallLLM            => 0.05,
            TaskType::MediumLLM           => 0.15,
            TaskType::LargeLLM            => 0.50,
        }
    }
}
```

### 7.3 矿工收益预估

#### 4060Ti 8GB 实际推理吞吐量（基于 Benchmark 数据）

| 任务类型 | 模型 | 调度层 | 单任务耗时 | 吞吐量/小时 |
|---------|------|--------|-----------|------------|
| 图像分类 | EfficientNet-B4 | Hot | ~5ms | ~720 (并发3) |
| 文本 Embedding | BGE-base-en | Hot | ~10ms | ~360 (并发3) |
| OCR | PaddleOCR | Hot | ~50-100ms | ~60 |
| 目标检测 | YOLOv8s | Hot | ~15ms | ~240 (并发2) |
| LLM (256 tokens) | Llama-3-8B Q4 | Warm | ~6.4s (40 t/s) | ~560 |
| LLM (512 tokens) | Llama-3-8B Q4 | Warm | ~12.8s (40 t/s) | ~280 |
| 语音转文字 | Whisper-small | Cold→Warm | ~3s/分钟音频 | ~20 段 |

> 注：LLM 吞吐量单位为 requests/小时，且 LLM 不可并发，执行 LLM 期间小模型仍可并发处理。
> 4060Ti 的主要瓶颈是 288 GB/s 内存带宽，LLM token 生成是带宽受限任务。

#### 各 Tier 收益预估

| GPU | Tier | 典型混合任务场景 | 日任务量 | 日收入 (QFC) | 日电费 | 日净收入 |
|-----|------|---------------|---------|-------------|--------|---------|
| 4060 Ti 8GB | T1 | 80% 小模型 + 20% LLM(8B) | ~8,000 | 10-18 | ~$0.50 | $19-35* |
| 3090 24GB | T2 | 50% 小模型 + 50% LLM(13B-30B) | ~3,000 | 24-48 | ~$1.00 | $47-95* |
| 4090 24GB | T2 | 40% 小模型 + 60% LLM(13B-30B) | ~4,500 | 36-90 | ~$1.10 | $71-179* |
| A100 80GB | T3 | 30% 小模型 + 70% LLM(70B) | ~2,000 | 72-180 | ~$3.00 | $141-357* |

*假设 QFC = $2。实际收益取决于：任务供给量、网络竞争、模型命中率（频繁切换会降低吞吐）*

**4060Ti 收益优化建议**：
- 专注小模型高频任务（分类/Embedding/OCR），吞吐量优势明显
- LLM 只接 ≤8B 的短请求（256 tokens 以下），长文本生成留给 Tier 2
- 保持 warm 层模型稳定，避免频繁切换（Task Router 会优化调度）
- 16GB 版 4060Ti 可额外接 13B Q4 模型，覆盖面更广

---

## 8. 模型注册表

### 8.1 链上模型管理

```rust
/// 链上模型注册表
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct ModelRegistry {
    pub model_id: Hash,

    /// 模型名称
    pub name: String,

    /// 模型版本
    pub version: String,

    /// 模型格式
    pub format: ModelFormat,

    /// 模型大小 (bytes)
    pub size_bytes: u64,

    /// 模型文件的 IPFS CID
    pub ipfs_cid: String,

    /// 模型 checksum（完整性校验）
    pub checksum: Hash,

    /// 最低 GPU Tier 要求
    pub min_tier: GpuTier,

    /// 预估 VRAM 需求 (MB)
    pub vram_required_mb: u32,

    /// 注册者地址
    pub registrant: Address,

    /// 是否经过审核
    pub verified: bool,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum ModelFormat {
    ONNX,
    TensorRT,
    SafeTensors,
    GGUF,       // llama.cpp 格式
}
```

### 8.2 模型安全审核

为防止恶意模型（例如包含后门或执行恶意代码）：

- 新模型提交后进入 `pending` 状态
- 由信誉 > 0.9 的验证节点审核
- 审核通过后标记为 `verified`
- 矿工默认只接受 `verified` 模型的任务
- 模型注册者需质押保证金，恶意模型罚没

---

## 9. 监控与运维

### 9.1 矿工 Prometheus Metrics

```
# GPU 指标
qfc_miner_gpu_temperature_celsius{device="0"}
qfc_miner_gpu_utilization_percent{device="0"}
qfc_miner_gpu_vram_used_mb{device="0"}
qfc_miner_gpu_power_watts{device="0"}

# 任务指标
qfc_miner_tasks_completed_total
qfc_miner_tasks_failed_total
qfc_miner_tasks_timeout_total
qfc_miner_task_inference_duration_ms
qfc_miner_task_queue_length

# 收益指标
qfc_miner_rewards_total_qfc
qfc_miner_rewards_24h_qfc

# 网络指标
qfc_miner_p2p_peers_connected
qfc_miner_contribution_score
```

### 9.2 Grafana Dashboard 建议面板

- GPU 温度/使用率/功耗（时间线）
- 任务完成量（每小时柱状图）
- 收益趋势（日/周/月）
- 任务类型分布（饼图）
- 挑战任务通过率（关键指标）
- P2P 网络连接状态

---

## 10. 实施路线图

### Phase 1: 基础原型 (Month 5-6)

与共识机制 Phase 2（多维度评分）同步：

- [ ] 定义 GPU Benchmark 标准
- [ ] 实现 qfc-miner 基础框架（Rust）
  - GPU 检测 + Benchmark
  - ONNX Runtime 推理引擎集成
  - 单任务执行流程
- [ ] 链上 AI Task Pool 合约（简化版）
  - 任务提交 / 认领 / 结果提交
  - 基础费用托管
- [ ] 链下 Task Router（简化版）
  - 单节点任务分发
  - 基础 Tier 匹配

**里程碑**：单矿工可接收并执行一个图像分类任务，获得 QFC 奖励

### Phase 2: 验证与安全 (Month 7-8)

- [ ] 挑战任务系统
- [ ] 冗余验证机制
- [ ] 矿工惩罚 (Slashing) 集成
- [ ] 模型注册表 + 审核流程
- [ ] 任务定价 Oracle

**里程碑**：10+ 矿工在测试网稳定运行，挑战通过率 >95%

### Phase 3: 生态扩展 (Month 9-10)

- [ ] AI-VM 集成（链上合约可调用 AI 推理）
- [ ] 支持更多推理框架（TensorRT、GGUF）
- [ ] 矿工收益 Dashboard
- [ ] SDK：开发者提交 AI 任务的 JS/Python 库
- [ ] 分布式训练原型（联邦学习）

**里程碑**：DApp 可通过智能合约调用 AI 推理，端到端闭环

### Phase 4: 优化与主网 (Month 11-12)

- [ ] 性能优化（任务调度、模型缓存）
- [ ] 安全审计（合约 + 矿工客户端）
- [ ] 经济模型压力测试
- [ ] 主网参数确定
- [ ] 文档 + 矿工教程

**里程碑**：AI 算力网络随主网一同上线

---

## 11. 开放问题（待讨论）

1. **任务数据隐私**：推理输入数据是否需要加密？如果是医疗/金融场景，矿工不应看到明文数据。可考虑可信执行环境 (TEE) 或同态加密。

2. **模型知识产权**：如果任务使用商业模型，如何防止矿工复制模型？可能需要模型加密 + TEE 方案。

3. **任务来源冷启动**：早期可能没有足够的真实 AI 任务。可考虑：
   - 网络自生成的"有用计算"（如：为链上数据建索引、生成链上数据的统计分析）
   - 与 AI 公司合作，导入推理需求

4. **跨 Tier 任务拆分**：大型任务能否拆分给多个 Tier 1 矿工协作完成？

5. **GPU 虚拟化检测**：如何防止矿工使用云 GPU 但声称是本地硬件？（是否有必要限制？）

---

## 附录

### A. qfc-miner CLI 参考

```bash
# 启动矿工
qfc-miner start --config ./qfc-miner.yaml

# 运行 Benchmark
qfc-miner benchmark --device 0

# 查看状态
qfc-miner status

# 查看收益
qfc-miner earnings --period 24h

# 停止矿工
qfc-miner stop
```

### B. 术语表

| 术语 | 定义 |
|------|------|
| qfc-miner | QFC AI 算力矿工客户端 |
| Task Router | 链下任务调度器，负责匹配任务和矿工 |
| Challenge Task | 带有已知答案的验证任务，用于检测作弊 |
| GPU Tier | GPU 能力分级（Tier 1/2/3） |
| Inference | AI 模型推理，即用训练好的模型处理新数据 |
| ONNX Runtime | 开源跨平台推理引擎 |
| Model Registry | 链上模型注册表，管理可用的 AI 模型 |

### C. 相关文档

- `00-PROJECT-OVERVIEW.md` — 项目总览，AI-VM 规划
- `02-CONSENSUS-MECHANISM.md` — PoC 共识，计算贡献维度定义
- `03-TOKENOMICS.md` — 代币经济学，费用分配规则
- `01-BLOCKCHAIN-DESIGN.md` — 核心区块链设计，P2P 网络层

---

**文档版本**: 1.0.0
**最后更新**: 2026-02-20
**状态**: 草案 (Draft)
**维护者**: QFC Core Team
