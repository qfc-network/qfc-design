# 09-AI-COMPUTE-NETWORK.md — QFC AI Compute Network Design

## Overview

The QFC AI Compute Network upgrades the "compute contribution" dimension (20% weight) in the PoC consensus mechanism from traditional PoW hash computation to **real-world AI inference compute with actual economic value**. Users provide GPU compute power to execute AI inference tasks and earn QFC token rewards — turning idle graphics cards into "AI mining rigs."

### Core Value Proposition

| Traditional PoW Mining | QFC AI Compute Mining |
|----------------------|----------------------|
| Compute power wasted on meaningless hashes | Compute power used for real AI inference tasks |
| Requires specialized ASIC miners | Consumer-grade GPUs can participate |
| Only one dimension: hash power | Multi-dimensional contribution (PoC system) |
| Pure competition between miners | Miners can collaborate |

### Relationship with Existing Architecture

```
┌─────────────────────────────────────────────────────┐
│              QFC Blockchain Ecosystem                │
│                                                     │
│  ┌───────────────┐   Defined by     ┌────────────┐  │
│  │ PoC Consensus  │◄──this doc────►│ AI Compute   │  │
│  │ (02-CONSENSUS) │  Compute dim.   │ Network      │  │
│  │                │                 │ (this doc)   │  │
│  └───────┬───────┘                └─────┬──────┘  │
│          │                              │         │
│  ┌───────┴───────┐              ┌───────┴──────┐  │
│  │ Token          │              │ AI-VM        │  │
│  │ Economics      │              │ (Smart       │  │
│  │ (03-TOKENOMICS)│              │  Contract)   │  │
│  └───────────────┘              └──────────────┘  │
└─────────────────────────────────────────────────────┘
```

- **02-CONSENSUS-MECHANISM.md**: The `compute` dimension in the PoC scoring formula is defined by this document
- **03-TOKENOMICS.md**: AI task fee distribution rules align with token economics
- **AI-VM** (planned in 00-PROJECT-OVERVIEW.md): On-chain contracts can directly invoke AI inference capabilities

---

## 1. System Architecture

### 1.1 Overall Architecture

```
┌──────────────────────────────────────────────────────────┐
│                   Task Submitters                         │
│   DApp / Enterprise API / On-chain Contract (AI-VM)      │
│   Submit AI inference request + pay QFC                   │
└────────────────────────┬─────────────────────────────────┘
                         ▼
┌──────────────────────────────────────────────────────────┐
│           On-chain AI Task Pool (Smart Contract)          │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │ Task          │  │ Fee          │  │ Result         │  │
│  │ Registry      │  │ Escrow       │  │ Verify         │  │
│  └──────────────┘  └──────────────┘  └───────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │ Miner         │  │ Model        │  │ Reward         │  │
│  │ Registry      │  │ Registry     │  │ Settlement     │  │
│  └──────────────┘  └──────────────┘  └───────────────┘  │
└────────────────────────┬─────────────────────────────────┘
                         ▼
┌──────────────────────────────────────────────────────────┐
│           Off-chain Task Scheduling Layer (Task Router)   │
│                                                          │
│  - Match tasks by GPU capability (Tier classification)    │
│  - Load balancing & proximity scheduling                  │
│  - Task timeout reassignment                              │
│  - Challenge task injection (anti-cheating)                │
└──────┬──────────────┬──────────────┬─────────────────────┘
       ▼              ▼              ▼
┌────────────┐ ┌────────────┐ ┌────────────┐
│ Tier 1     │ │ Tier 2     │ │ Tier 3     │
│ 4060Ti etc │ │ 3090/4080  │ │ A100/H100  │
│ Small      │ │ Medium     │ │ Large      │
│ inference  │ │ inference  │ │ inference  │
│ qfc-miner  │ │ qfc-miner  │ │ qfc-miner  │
└────────────┘ └────────────┘ └────────────┘
```

### 1.2 Component Responsibilities

| Component | Location | Responsibility |
|-----------|----------|---------------|
| AI Task Pool | On-chain (smart contract) | Task/miner/model registration, fee escrow, result on-chain |
| Task Router | Off-chain (P2P network layer) | Task distribution, load balancing, challenge injection |
| qfc-miner | Miner local | GPU inference execution, result submission, model management |
| Verification Module | On-chain + off-chain | Result verification, cheat detection, slash triggering |

---

## 2. GPU Tiering & Task Types

### 2.1 GPU Tier Classification

Miners run a standard benchmark upon registration, and their capability tier is recorded on-chain:

```rust
#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum GpuTier {
    /// Tier 1: Consumer entry-level (4-8 GB VRAM)
    /// 4060Ti, 3060, RX 7600, etc.
    Tier1,

    /// Tier 2: Consumer high-end (12-24 GB VRAM)
    /// 3090, 4080, 4090, RX 7900 XTX, etc.
    Tier2,

    /// Tier 3: Professional/data center (40-80 GB VRAM)
    /// A100, H100, L40S, etc.
    Tier3,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct GpuProfile {
    /// GPU model (auto-detected)
    pub model: String,

    /// VRAM size (MB)
    pub vram_mb: u32,

    /// Benchmark score (normalized 0-10000)
    pub benchmark_score: u32,

    /// Automatically assigned tier
    pub tier: GpuTier,

    /// Supported inference runtimes
    pub supported_runtimes: Vec<InferenceRuntime>,
}
```

### 2.2 Benchmark Standard

```rust
/// Standard benchmark task set (executed during registration)
pub struct GpuBenchmark {
    tasks: Vec<BenchmarkTask>,
}

impl GpuBenchmark {
    pub fn standard() -> Self {
        Self {
            tasks: vec![
                // 1. Matrix multiplication throughput (measures raw compute)
                BenchmarkTask::MatMul { size: 4096, iterations: 100 },

                // 2. ResNet-50 inference (measures CV inference capability)
                BenchmarkTask::ModelInference {
                    model: "resnet50",
                    batch_size: 32,
                    iterations: 50,
                },

                // 3. BERT-base inference (measures NLP inference capability)
                BenchmarkTask::ModelInference {
                    model: "bert-base",
                    batch_size: 16,
                    iterations: 50,
                },

                // 4. VRAM bandwidth test
                BenchmarkTask::MemoryBandwidth { size_mb: 1024 },
            ],
        }
    }

    /// Run benchmark, returns score + tier
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

**Reference Score Ranges:**

| GPU | Benchmark Score (estimated) | Tier | VRAM |
|-----|---------------------------|------|------|
| RTX 4060 Ti | ~2,800 | Tier 1 | 8 GB |
| RTX 3060 12GB | ~2,200 | Tier 1 | 12 GB |
| RTX 3090 | ~4,500 | Tier 2 | 24 GB |
| RTX 4080 | ~5,200 | Tier 2 | 16 GB |
| RTX 4090 | ~6,800 | Tier 2 | 24 GB |
| A100 80GB | ~8,500 | Tier 3 | 80 GB |
| H100 | ~9,800 | Tier 3 | 80 GB |

### 2.3 Task Types & Tier Matching

```rust
#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum TaskType {
    /// Image classification (ResNet, EfficientNet, etc.)
    ImageClassification,

    /// Object detection (YOLO, etc.)
    ObjectDetection,

    /// OCR text recognition
    OCR,

    /// Text embedding generation
    TextEmbedding,

    /// Image generation (Stable Diffusion, etc.)
    ImageGeneration,

    /// Small LLM inference (<=7B parameters)
    SmallLLM,

    /// Medium LLM inference (7B-30B parameters)
    MediumLLM,

    /// Large LLM inference (>30B parameters)
    LargeLLM,

    /// Speech to text
    SpeechToText,

    /// Custom ONNX model
    CustomONNX,
}

impl TaskType {
    /// Minimum tier required for this task type
    pub fn min_tier(&self) -> GpuTier {
        match self {
            Self::ImageClassification => GpuTier::Tier1,
            Self::ObjectDetection     => GpuTier::Tier1,
            Self::OCR                 => GpuTier::Tier1,
            Self::TextEmbedding       => GpuTier::Tier1,
            Self::SpeechToText        => GpuTier::Tier1,
            Self::CustomONNX          => GpuTier::Tier1,  // Depends on model size
            Self::ImageGeneration     => GpuTier::Tier2,
            Self::SmallLLM            => GpuTier::Tier2,
            Self::MediumLLM           => GpuTier::Tier2,
            Self::LargeLLM            => GpuTier::Tier3,
        }
    }

    /// Estimated VRAM requirement (MB)
    pub fn estimated_vram_mb(&self) -> u32 {
        match self {
            Self::ImageClassification => 512,
            Self::ObjectDetection     => 1024,
            Self::OCR                 => 512,
            Self::TextEmbedding       => 1024,
            Self::SpeechToText        => 1536,
            Self::CustomONNX          => 2048,  // Default, actual varies by model
            Self::ImageGeneration     => 6144,
            Self::SmallLLM            => 8192,
            Self::MediumLLM           => 16384,
            Self::LargeLLM            => 40960,
        }
    }
}
```

---

## 3. Task Lifecycle

### 3.1 State Machine

```
                    Submit Task
                       │
                       ▼
               ┌───────────────┐
               │   Pending     │ Awaiting assignment
               └───────┬───────┘
                       │ Task Router assigns
                       ▼
               ┌───────────────┐
               │   Assigned    │ Assigned to miner
               └───────┬───────┘
                       │
              ┌────────┼────────┐
              ▼        │        ▼
     ┌──────────┐      │  ┌──────────┐
     │ Running  │      │  │ Timeout  │ Timeout → reassign
     └────┬─────┘      │  └──────────┘
          │            │
          ▼            │
  ┌───────────────┐    │
  │  Submitted    │ Miner submits result
  └───────┬───────┘    │
          │            │
     ┌────┴────┐       │
     ▼         ▼       │
┌────────┐ ┌────────┐  │
│Verified│ │Disputed│  │ Verified / Challenged
└────┬───┘ └────┬───┘  │
     │          │      │
     ▼          ▼      │
┌────────┐ ┌────────┐  │
│  Paid  │ │Slashed │  │ Settlement / Penalty
└────────┘ └────────┘  │
```

### 3.2 Task Data Structure

```rust
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct AITask {
    /// Task ID (unique on-chain)
    pub task_id: Hash,

    /// Task type
    pub task_type: TaskType,

    /// Model ID used (on-chain model registry)
    pub model_id: Hash,

    /// Input data (or IPFS/Arweave CID)
    pub input: TaskInput,

    /// Maximum execution time (seconds)
    pub timeout_secs: u32,

    /// Task reward (QFC wei)
    pub reward: U256,

    /// Required minimum GPU tier
    pub min_tier: GpuTier,

    /// Submitter address
    pub submitter: Address,

    /// Current status
    pub status: TaskStatus,

    /// Assigned miner (if assigned)
    pub assigned_miner: Option<Address>,

    /// Creation time
    pub created_at: u64,

    /// Whether this is a challenge task (for verification; this field is invisible to miners)
    pub is_challenge: bool,

    /// Expected result for challenge tasks (stored off-chain only)
    pub expected_result: Option<Vec<u8>>,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum TaskInput {
    /// Inline data (less than 256KB)
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

### 3.3 Task Submission (On-chain Contract)

```rust
/// AI Task Pool contract interface
pub trait AITaskPool {
    /// Submit an AI inference task
    /// The caller must also pay the reward amount to the contract (escrow)
    fn submit_task(
        task_type: TaskType,
        model_id: Hash,
        input: TaskInput,
        timeout_secs: u32,
        min_tier: GpuTier,
    ) -> TaskId;

    /// Cancel an unassigned task (refund reward)
    fn cancel_task(task_id: TaskId);

    /// Miner claims a task
    fn claim_task(task_id: TaskId);

    /// Miner submits result
    fn submit_result(task_id: TaskId, result_hash: Hash, result_data: Vec<u8>);

    /// Challenge a result (requires deposit)
    fn challenge_result(task_id: TaskId, deposit: U256);

    /// Arbitrate (N validator nodes re-execute)
    fn arbitrate(task_id: TaskId, results: Vec<(Address, Vec<u8>)>);
}
```

---

## 4. Miner Client (qfc-miner)

### 4.1 Architecture

```
qfc-miner
├── Network Module
│   ├── P2P Node (libp2p)            # Communicates with Task Router
│   └── RPC Client                    # Interacts with QFC chain
│
├── Task Management
│   ├── Task Fetcher                  # Pull/receive tasks
│   ├── Task Queue                    # Local task queue
│   └── Result Submitter              # Result submission
│
├── Inference Engine
│   ├── ONNX Runtime                  # General inference backend
│   ├── TensorRT (optional)           # NVIDIA optimized inference
│   └── Model Manager                 # Model download/cache/version management
│
├── GPU Management
│   ├── Device Monitor                # GPU utilization/temperature/power
│   ├── VRAM Allocator                # VRAM allocation
│   └── Power Limiter                 # Power limit
│
└── Identity & Security
    ├── Wallet Signer                 # Result signing
    └── Benchmark Runner              # GPU benchmarking
```

### 4.2 Configuration File

```yaml
# qfc-miner.yaml

# ===== Basic Configuration =====
wallet_address: "0xYourWalletAddress"
private_key_file: "./miner.key"       # Encrypted private key file
rpc_endpoint: "https://rpc.testnet.qfc.network"

# ===== GPU Configuration =====
gpu:
  device_id: 0                        # GPU device number (multi-GPU selection)
  max_vram_usage_mb: 7168             # Max VRAM usage (leave 1GB for system)
  max_power_watts: 150                # Power limit
  max_temperature_c: 83               # Temperature cap, auto-throttle if exceeded
  runtime: "onnxruntime"              # Inference backend: onnxruntime / tensorrt

# ===== Model Management (Three-tier Scheduling) =====
# See Section 4.5 for model scheduling strategy
models:
  # Hot Layer: Resident on GPU, instant response (<50ms)
  hot:
    - id: "efficientnet-b4"           # Image classification, ~200MB
    - id: "bge-base-en-v1.5"         # Text embedding, ~400MB
    - id: "yolov8s"                  # Object detection, ~100MB

  # Warm Pool: Large models loaded on demand (2-5s cold load)
  warm:
    max_vram_mb: 5000                 # Warm layer max VRAM
    allowed_models:                   # Whitelist — models not listed won't be accepted
      - "llama-3-8b-q4"
      - "mistral-7b-q4"
      - "whisper-small"
    preload: "llama-3-8b-q4"         # Preload on startup

  # Cold Cache: Disk cache
  cache:
    dir: "./models"
    max_disk_gb: 20
    auto_download: true
    eviction_policy: "lru"

  # VRAM Budget Allocation
  vram_budget:
    reserved_mb: 800                  # System reserved
    hot_max_mb: 1000                  # Hot layer cap
    warm_max_mb: 5000                 # Warm layer cap
    buffer_mb: 1200                   # Inference buffer (KV Cache, etc.)

# ===== Mining Configuration =====
mining:
  # Accepted task types (if not configured, accepts all tasks matching tier)
  task_types:
    - image_classification
    - text_embedding
    - ocr
    - object_detection
    - speech_to_text
    - small_llm                       # Requires corresponding model in warm layer

  max_concurrent_tasks: 3             # Small model concurrency (LLM fixed at 1)
  min_reward_qfc: 0.005               # Minimum acceptable reward per task

# ===== Network Configuration =====
network:
  p2p_port: 30304
  p2p_bootnodes:
    - "/ip4/bootnode1.qfc.network/tcp/30304/p2p/12D3..."
  bandwidth_limit_mbps: 100

# ===== Optional: Also run as validator =====
validator:
  enabled: false
  # stake_amount: 10000               # Stake amount (QFC)

# ===== Monitoring =====
monitoring:
  prometheus_port: 9100               # Prometheus metrics port
  log_level: "info"                   # debug / info / warn / error
  log_file: "./logs/miner.log"
```

### 4.3 Startup Flow

```rust
pub async fn run_miner(config: MinerConfig) -> Result<(), Error> {
    // 1. Detect GPU
    let gpu = detect_gpu(config.gpu.device_id)?;
    info!("GPU detected: {} ({} MB VRAM)", gpu.model, gpu.vram_mb);

    // 2. Run benchmark (first time or after version update)
    let benchmark = if needs_benchmark(&gpu) {
        info!("Running GPU benchmark...");
        let result = GpuBenchmark::standard().run(&gpu);
        info!("Benchmark score: {} ({})", result.score, result.tier);
        save_benchmark(&result)?;
        result
    } else {
        load_benchmark()?
    };

    // 3. Connect to QFC network
    let rpc = RpcClient::new(&config.rpc_endpoint);
    let p2p = P2PNode::new(&config.network).await?;

    // 4. Register miner on-chain (if not registered)
    if !is_miner_registered(&rpc, &config.wallet_address).await? {
        info!("Registering as compute provider...");
        register_miner(&rpc, &config, &benchmark).await?;
    }

    // 5. Initialize inference engine
    let engine = InferenceEngine::new(&config.gpu)?;

    // 6. Initialize model manager
    let model_manager = ModelManager::new(
        &config.mining.model_cache_dir,
        config.mining.model_cache_max_gb,
    );

    // 7. Start task loop
    let task_queue = TaskQueue::new(config.mining.max_concurrent_tasks);

    info!("Miner started. Waiting for tasks...");

    loop {
        tokio::select! {
            // Receive new task
            task = p2p.receive_task() => {
                if let Ok(task) = task {
                    if should_accept(&task, &config, &benchmark) {
                        task_queue.enqueue(task);
                    }
                }
            }

            // Execute tasks in queue
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

            // GPU health monitoring
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

### 4.4 Task Execution Flow

```rust
async fn execute_task(
    task: &AITask,
    engine: &InferenceEngine,
    model_scheduler: &mut ModelScheduler,
) -> Result<TaskResult, Error> {
    // 1. Get model through scheduler (Hot/Warm hit or Cold load)
    let (model, latency) = model_scheduler.get_model(&task.model_id).await?;

    match latency {
        ScheduleLatency::Immediate => {
            debug!("Model {} hit in Hot/Warm layer", task.model_id);
        }
        ScheduleLatency::ColdLoad { ms } => {
            info!("Model {} loaded from disk in {}ms", task.model_id, ms);
        }
    }

    // 2. Fetch input data
    let input_data = match &task.input {
        TaskInput::Inline(data) => data.clone(),
        TaskInput::IPFS(cid)   => fetch_from_ipfs(cid).await?,
        TaskInput::Arweave(id) => fetch_from_arweave(id).await?,
    };

    // 3. Preprocess input
    let preprocessed = preprocess(&input_data, &task.task_type)?;

    // 4. Execute inference
    let start = Instant::now();
    let output = model.session.run(preprocessed)?;
    let inference_time = start.elapsed();

    // 5. Postprocess output
    let result = postprocess(output, &task.task_type)?;

    // 6. Sign result
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

### 4.5 Model Scheduling Strategy

Each miner **does not run just one model** — instead, it manages multiple models simultaneously through a three-tier cache for efficient scheduling:

#### VRAM Layered Architecture

```
┌──────────────────────────────────────────────────────┐
│                   GPU VRAM                            │
│                                                      │
│  ┌────────────────────────────────────────────────┐  │
│  │  Hot Layer (resident, instant response <50ms)   │  │
│  │                                                │  │
│  │  Multiple small models can reside together:     │  │
│  │  efficientnet-b4    200MB  ← Image classif.    │  │
│  │  bge-base-en        400MB  ← Text embedding    │  │
│  │  yolov8s            100MB  ← Object detection  │  │
│  │                     ─────                      │  │
│  │                     700MB                      │  │
│  └────────────────────────────────────────────────┘  │
│                                                      │
│  ┌────────────────────────────────────────────────┐  │
│  │  Warm Layer (loaded, ready to execute <100ms)   │  │
│  │                                                │  │
│  │  Only 1 large model at a time:                  │  │
│  │  llama-3-8b-q4      4.5GB  ← LLM inference    │  │
│  │                                                │  │
│  │  Evicted by LRU; old model unloaded when new   │  │
│  │  large model arrives                            │  │
│  └────────────────────────────────────────────────┘  │
│                                                      │
│  Reserved: ~2.8GB (system + peak buffer)             │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│              Local Disk Cold Layer                     │
│                                                      │
│  whisper-small        500MB   ← Load on demand (2-5s)│
│  mistral-7b-q4        4.2GB   ← Load on demand (3-5s)│
│  ...more models downloaded on demand                  │
│                                                      │
│  Disk cache limit: Configurable (default 20GB)        │
└──────────────────────────────────────────────────────┘
```

#### 4060Ti 8GB Typical VRAM Allocation

| Layer | Allocation | Usage |
|-------|-----------|-------|
| System Reserved | ~800MB | CUDA context, driver |
| Hot Layer | ~700MB | 3-4 small models resident, instant response |
| Warm Layer | ~4500MB | 1 x 7B-8B LLM, loaded on demand |
| Buffer | ~2000MB | Temporary tensors during inference, KV Cache |

Key constraint: **Small models can handle 2-3 concurrent tasks, but LLM can only run 1 inference request at a time.**

#### Model Scheduler Implementation

```rust
/// Three-tier model scheduler
pub struct ModelScheduler {
    /// Hot: Resident on GPU, <50ms response
    hot_models: Vec<LoadedModel>,

    /// Warm: On GPU but can be evicted, <100ms response
    warm_model: Option<LoadedModel>,

    /// Cold: On disk, requires 2-5s to load
    cold_cache: LruCache<Hash, CachedModel>,

    /// VRAM budget
    vram_budget: VramBudget,
}

pub struct VramBudget {
    pub total_mb: u32,
    pub hot_budget_mb: u32,    // Small model fixed budget
    pub warm_budget_mb: u32,   // Large model flexible budget
    pub reserved_mb: u32,      // System reserved
}

impl ModelScheduler {
    /// Scheduling decision when a task is received
    pub async fn get_model(
        &mut self,
        model_id: &Hash,
    ) -> Result<(&LoadedModel, ScheduleLatency), Error> {

        // 1. Hot hit → run directly, zero wait
        if let Some(model) = self.hot_models.iter().find(|m| m.id == *model_id) {
            return Ok((model, ScheduleLatency::Immediate));
        }

        // 2. Warm hit → almost no wait
        if let Some(ref model) = self.warm_model {
            if model.id == *model_id {
                return Ok((model, ScheduleLatency::Immediate));
            }
        }

        // 3. Cold hit → needs loading from disk to GPU
        if let Some(cached) = self.cold_cache.get(model_id) {
            let needed_mb = cached.vram_required_mb;

            // If warm slot is occupied, evict first
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

        // 4. Not available locally → needs download then load
        Err(Error::ModelNotCached(*model_id))
    }

    /// Reports currently loaded models when registering the miner
    /// Task Router uses this information for global scheduling
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
                ready: false,  // Requires load time
            });
        }

        models
    }
}

pub enum ScheduleLatency {
    /// Hot/Warm hit, no wait
    Immediate,
    /// Loaded from disk, has latency
    ColdLoad { ms: u32 },
}
```

#### Task Router Global Model-Aware Scheduling

The Task Router maintains the model loading status of all miners and preferentially assigns tasks to miners that already have the corresponding model loaded:

```rust
/// Task Router's miner model status table
pub struct MinerModelRegistry {
    /// Miner address → currently loaded model list
    miner_models: HashMap<Address, Vec<ModelStatus>>,
}

impl MinerModelRegistry {
    /// Select the optimal miner for a task
    pub fn select_miner(
        &self,
        task: &AITask,
        available_miners: &[MinerInfo],
    ) -> Option<Address> {
        let model_id = &task.model_id;

        // Priority 1: Miners with model in Hot layer (zero switching cost)
        let hot_miners: Vec<_> = available_miners.iter()
            .filter(|m| self.has_model_in_layer(m.address, model_id, ModelLayer::Hot))
            .collect();
        if !hot_miners.is_empty() {
            return Some(select_least_loaded(&hot_miners));
        }

        // Priority 2: Miners with model in Warm layer
        let warm_miners: Vec<_> = available_miners.iter()
            .filter(|m| self.has_model_in_layer(m.address, model_id, ModelLayer::Warm))
            .collect();
        if !warm_miners.is_empty() {
            return Some(select_least_loaded(&warm_miners));
        }

        // Priority 3: Miners with model in Cold layer (needs loading, but no download)
        let cold_miners: Vec<_> = available_miners.iter()
            .filter(|m| self.has_model_in_layer(m.address, model_id, ModelLayer::Cold))
            .collect();
        if !cold_miners.is_empty() {
            return Some(select_least_loaded(&cold_miners));
        }

        // Priority 4: Any miner meeting tier requirements (needs model download)
        let any_miners: Vec<_> = available_miners.iter()
            .filter(|m| m.gpu_tier >= task.min_tier)
            .collect();
        if !any_miners.is_empty() {
            return Some(select_least_loaded(&any_miners));
        }

        None  // No available miner
    }
}
```

**Global Effect**: 1,000 miners in the network can cover hundreds of models, but each miner only needs to maintain a few. The Task Router ensures tasks are assigned to the most suitable miner, minimizing model switching overhead.

#### Miner Configuration File (Model Section)

```yaml
# qfc-miner.yaml — Model Management Configuration

models:
  # ===== Hot Layer: Resident on GPU, suitable for high-frequency small tasks =====
  hot:
    - id: "efficientnet-b4"       # Image classification
      vram_mb: 200
    - id: "bge-base-en-v1.5"     # Text embedding
      vram_mb: 400
    - id: "yolov8s"              # Object detection
      vram_mb: 100

  # ===== Warm Pool: Allowed large models =====
  warm:
    max_vram_mb: 5000             # Warm layer max VRAM budget
    allowed_models:               # Whitelist (LLM tasks not on this list are rejected)
      - "llama-3-8b-q4"
      - "mistral-7b-q4"
      - "whisper-small"
    preload: "llama-3-8b-q4"     # Default large model preloaded on startup

  # ===== Cold Cache: Disk cache =====
  cache:
    dir: "./models"
    max_disk_gb: 20               # Disk cache cap
    auto_download: true           # Auto-download whitelisted models
    eviction_policy: "lru"        # Eviction policy when disk is full

  # ===== VRAM Budget =====
  vram_budget:
    reserved_mb: 800              # System reserved
    hot_max_mb: 1000              # Hot layer cap
    warm_max_mb: 5000             # Warm layer cap
    buffer_mb: 1200               # Inference buffer (KV Cache, etc.)
```

#### Actual 4060Ti 8GB Performance in Practice

```
Scenario 1: Continuous embedding tasks
  → bge-base-en in Hot layer, ~10ms per request
  → Can handle 3 concurrent requests
  → Throughput: ~300 requests/s

Scenario 2: Alternating classification + embedding tasks
  → Both models in Hot layer, zero switching
  → Total throughput: ~200-400 requests/s

Scenario 3: Receives an LLM inference task
  → If llama-3-8b in Warm layer: starts immediately, ~40 tokens/s
  → If needs disk load: wait 3-5 seconds, then ~40 tokens/s
  → During LLM execution, Hot layer small models can still handle other tasks concurrently

Scenario 4: Consecutive requests for the same LLM
  → First request may have loading latency
  → Subsequent requests have zero latency (model already in Warm layer)
  → Task Router will route same-model tasks consecutively to the same miner
```

---

## 5. Anti-Cheating & Verification Mechanism

### 5.1 Three-Layer Verification System

```
┌──────────────────────────────────────────────────────┐
│ Layer 1: Registration Verification                     │
│ - GPU benchmark score validation                       │
│ - Known GPU model → score range comparison             │
│ - Fake hardware claim → registration rejected          │
└──────────────────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────┐
│ Layer 2: Runtime Challenges (Challenge Tasks)          │
│ - Randomly inject tasks with known answers (~5%)       │
│ - Miners cannot distinguish challenges from real tasks │
│ - Answer deviation beyond threshold → reputation loss  │
│ - Consecutive failures → slash + ban                   │
└──────────────────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────┐
│ Layer 3: Redundant Verification (Redundant Execution)  │
│ - High-value tasks (reward > threshold) sent to 3      │
│   miners                                               │
│ - Majority-consistent result is accepted               │
│ - Inconsistent miners trigger more challenge tasks     │
│ - Persistent inconsistency → slash                     │
└──────────────────────────────────────────────────────┘
```

### 5.2 Challenge Task Mechanism

```rust
/// Challenge task generator (run by Task Router)
pub struct ChallengeGenerator {
    /// Pre-computed challenge task pool
    challenge_pool: Vec<ChallengeTask>,

    /// Challenge task injection ratio
    challenge_ratio: f64,  // Default 0.05 (5%)
}

#[derive(Clone)]
pub struct ChallengeTask {
    /// Disguised as a regular task
    pub task: AITask,

    /// Expected correct result
    pub expected_output: Vec<u8>,

    /// Allowed tolerance range (for floating-point results)
    pub tolerance: f64,
}

impl ChallengeGenerator {
    /// Decide whether the next task should be a challenge
    pub fn should_inject_challenge(&self, miner: &Address) -> bool {
        let miner_stats = get_miner_stats(miner);

        // New miners: higher challenge frequency (10%)
        if miner_stats.total_tasks < 100 {
            return random::<f64>() < 0.10;
        }

        // Low-reputation miners: higher challenge frequency
        if miner_stats.reputation < 0.8 {
            return random::<f64>() < 0.08;
        }

        // Normal miners: standard 5%
        random::<f64>() < self.challenge_ratio
    }

    /// Verify challenge task result
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

### 5.3 Penalty Rules (Aligned with PoC Slashing)

| Violation | Penalty | Ban Duration |
|-----------|---------|-------------|
| Challenge task failure (single) | -5% reputation | None |
| 3 consecutive challenge failures | 5% stake slashed + -20% reputation | 3 days |
| Submitting fake results | 20% stake slashed | 30 days |
| Fake GPU claim | 50% stake slashed | Permanent |
| Redundant verification inconsistency | -10% reputation | None (triggers more challenges) |

```rust
/// AI miner penalties (extends SlashableOffense from 02-CONSENSUS)
pub enum MinerOffense {
    /// Challenge failure
    ChallengeFailed { consecutive_count: u32 },

    /// Submitted fake result (evidence: redundant execution comparison)
    FakeResult { task_id: Hash, evidence: Vec<u8> },

    /// Fake hardware claim
    FakeGpuClaim { claimed: GpuProfile, actual: GpuProfile },

    /// Excessive timeout rate (>30%)
    HighTimeoutRate { rate: f64 },
}

fn slash_miner(miner: Address, offense: MinerOffense) -> SlashResult {
    let stake = get_stake(miner);

    let (slash_percent, jail_days) = match offense {
        MinerOffense::ChallengeFailed { consecutive_count } => {
            if consecutive_count >= 3 {
                (5, 3)
            } else {
                (0, 0)  // Only deduct reputation
            }
        },
        MinerOffense::FakeResult { .. } => (20, 30),
        MinerOffense::FakeGpuClaim { .. } => (50, 365 * 100),  // Permanent
        MinerOffense::HighTimeoutRate { .. } => (1, 1),
    };

    execute_slash(miner, stake * slash_percent / 100, jail_days)
}
```

---

## 6. Integration with PoC Consensus

### 6.1 Compute Contribution Score Update

Replaces the compute contribution dimension in `02-CONSENSUS-MECHANISM.md`:

```rust
/// Updated compute contribution scoring (replaces original hashrate approach)
fn calculate_compute_contribution(node: &ValidatorNode) -> f64 {
    // If the node does not provide AI compute, this score is 0
    if !node.provides_ai_compute {
        return 0.0;
    }

    let miner_stats = get_miner_stats(&node.address);

    // 1. Task completion ratio (40%)
    let task_completion_ratio = miner_stats.completed_tasks as f64
        / total_completed_tasks as f64;

    // 2. Inference accuracy (40%)
    //    Based on challenge task pass rate
    let accuracy = miner_stats.challenge_pass_rate;

    // 3. Response speed (20%)
    //    Execution efficiency relative to task timeout
    let speed_score = if miner_stats.avg_completion_ratio > 0.0 {
        (1.0 - miner_stats.avg_completion_ratio).max(0.0)
    } else {
        0.0
    };

    task_completion_ratio * 0.4 + accuracy * 0.4 + speed_score * 0.2
}
```

### 6.2 Complete PoC Scoring Formula (with AI Compute)

```rust
/// Complete contribution score (updated version)
fn calculate_contribution_score(node: &ValidatorNode) -> f64 {
    let mut score = 0.0;

    // 1. Staking contribution (30%)
    let stake_ratio = node.stake as f64 / total_stake as f64;
    score += stake_ratio * 0.30;

    // 2. AI compute contribution (20%) ← Changed from PoW hashrate to AI compute
    let compute = calculate_compute_contribution(node);
    score += compute * 0.20;

    // 3. Uptime (15%)
    score += node.uptime_percentage * 0.15;

    // 4. Validation accuracy (15%)
    score += node.validation_accuracy * 0.15;

    // 5. Network service quality (10%)
    let latency_score = 1.0 / (1.0 + node.avg_latency_ms / 100.0);
    let bandwidth_score = (node.bandwidth_mbps / 1000.0).min(1.0);
    score += (latency_score * 0.6 + bandwidth_score * 0.4) * 0.10;

    // 6. Storage contribution (5%)
    let storage_ratio = node.storage_provided_gb as f64 / total_storage_gb as f64;
    score += storage_ratio * 0.05;

    // 7. Historical reputation (5%)
    score += calculate_reputation(&node.history) * 0.05;

    // Apply network state multiplier
    score *= get_network_multiplier(node);

    score
}
```

### 6.3 Revenue Path for GPU-Only Miners (No Staking)

The core advantage of PoC: **You can participate without staking, and you can participate without providing compute.**

```
Scenario A: GPU-only miner (has a 4060Ti, no QFC staked)

  Contribution = Stake(30%)  × 0.0     = 0.000
               + Compute(20%) × 0.8     = 0.160  ← Continuously running AI tasks
               + Uptime(15%)  × 0.95    = 0.143  ← 24/7 online
               + Accuracy(15%) × 0.98   = 0.147  ← High-quality completion
               + Network(10%) × 0.70    = 0.070
               + Storage(5%)  × 0.10    = 0.005
               + Reputation(5%) × 0.50  = 0.025  ← New miner, still building
               ─────────────────────────────
               Total ≈ 0.55

  Revenue sources:
  ① Direct reward from AI tasks (independent of contribution score, billed per task)
  ② Block reward share (proportional to contribution score)

Scenario B: Staking-only user (has QFC, no GPU)

  Contribution = Stake(30%)  × 0.5     = 0.150  ← Staked a significant amount
               + Compute(20%) × 0.0     = 0.000  ← Not providing compute
               + Uptime(15%)  × 0.90    = 0.135
               + Accuracy(15%) × 0.95   = 0.143
               + Network(10%) × 0.60    = 0.060
               + Storage(5%)  × 0.05    = 0.003
               + Reputation(5%) × 0.80  = 0.040
               ─────────────────────────────
               Total ≈ 0.53

Scenario C: GPU + Staking (has both a 4060Ti and staked QFC)

  Contribution = Stake(30%)  × 0.3     = 0.090
               + Compute(20%) × 0.8     = 0.160
               + Uptime(15%)  × 0.95    = 0.143
               + Accuracy(15%) × 0.98   = 0.147
               + Network(10%) × 0.70    = 0.070
               + Storage(5%)  × 0.10    = 0.005
               + Reputation(5%) × 0.80  = 0.040
               ─────────────────────────────
               Total ≈ 0.65  ← Highest, due to multi-dimensional contributions
```

---

## 7. Token Economics Extension

### 7.1 AI Task Fee Flow

Consistent with the fee distribution framework in `03-TOKENOMICS.md`:

```
Task submitter pays QFC
         │
         ▼
┌─────────────────────┐
│   Total Task Fee     │
│      = 100%          │
└─────────┬───────────┘
          │
   ┌──────┴──────┬──────────────┐
   ▼             ▼              ▼
┌────────┐  ┌────────┐   ┌──────────┐
│  70%   │  │  10%   │   │   20%    │
│Executing│  │Validator│   │  Burned  │
│ Miner  │  │ Nodes  │   │         │
└────────┘  └────────┘   └──────────┘
```

### 7.2 AI Task Pricing

```rust
/// Task pricing reference (adjustable via on-chain governance)
pub struct TaskPricing {
    /// Base fee = task_type base price × model size coefficient
    pub base_fee: U256,

    /// Priority fee = user-defined (accelerates matching)
    pub priority_fee: U256,
}

impl TaskPricing {
    /// Reference price table (unit: QFC)
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

### 7.3 Miner Revenue Estimates

#### 4060Ti 8GB Actual Inference Throughput (Based on Benchmark Data)

| Task Type | Model | Scheduling Layer | Time per Task | Throughput/Hour |
|-----------|-------|-----------------|--------------|-----------------|
| Image Classification | EfficientNet-B4 | Hot | ~5ms | ~720 (3 concurrent) |
| Text Embedding | BGE-base-en | Hot | ~10ms | ~360 (3 concurrent) |
| OCR | PaddleOCR | Hot | ~50-100ms | ~60 |
| Object Detection | YOLOv8s | Hot | ~15ms | ~240 (2 concurrent) |
| LLM (256 tokens) | Llama-3-8B Q4 | Warm | ~6.4s (40 t/s) | ~560 |
| LLM (512 tokens) | Llama-3-8B Q4 | Warm | ~12.8s (40 t/s) | ~280 |
| Speech to Text | Whisper-small | Cold→Warm | ~3s/min audio | ~20 segments |

> Note: LLM throughput is in requests/hour, and LLM cannot run concurrently. During LLM execution, small models in the Hot layer can still process tasks concurrently.
> The 4060Ti's main bottleneck is its 288 GB/s memory bandwidth; LLM token generation is a bandwidth-limited task.

#### Revenue Estimates by Tier

| GPU | Tier | Typical Mixed Task Scenario | Daily Tasks | Daily Income (QFC) | Daily Power Cost | Daily Net Income |
|-----|------|---------------------------|------------|-------------------|-----------------|-----------------|
| 4060 Ti 8GB | T1 | 80% small models + 20% LLM(8B) | ~8,000 | 10-18 | ~$0.50 | $19-35* |
| 3090 24GB | T2 | 50% small models + 50% LLM(13B-30B) | ~3,000 | 24-48 | ~$1.00 | $47-95* |
| 4090 24GB | T2 | 40% small models + 60% LLM(13B-30B) | ~4,500 | 36-90 | ~$1.10 | $71-179* |
| A100 80GB | T3 | 30% small models + 70% LLM(70B) | ~2,000 | 72-180 | ~$3.00 | $141-357* |

*Assuming QFC = $2. Actual revenue depends on: task supply volume, network competition, model hit rate (frequent switching reduces throughput)*

**4060Ti Revenue Optimization Tips**:
- Focus on high-frequency small model tasks (classification/embedding/OCR) where throughput advantage is clear
- Only accept LLM tasks <=8B with short requests (256 tokens or less); leave long text generation to Tier 2
- Keep the warm layer model stable to avoid frequent switching (Task Router will optimize scheduling)
- The 16GB 4060Ti variant can additionally handle 13B Q4 models, expanding coverage

---

## 8. Model Registry

### 8.1 On-chain Model Management

```rust
/// On-chain model registry
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct ModelRegistry {
    pub model_id: Hash,

    /// Model name
    pub name: String,

    /// Model version
    pub version: String,

    /// Model format
    pub format: ModelFormat,

    /// Model size (bytes)
    pub size_bytes: u64,

    /// IPFS CID of model file
    pub ipfs_cid: String,

    /// Model checksum (integrity verification)
    pub checksum: Hash,

    /// Minimum GPU tier requirement
    pub min_tier: GpuTier,

    /// Estimated VRAM requirement (MB)
    pub vram_required_mb: u32,

    /// Registrant address
    pub registrant: Address,

    /// Whether verified
    pub verified: bool,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum ModelFormat {
    ONNX,
    TensorRT,
    SafeTensors,
    GGUF,       // llama.cpp format
}
```

### 8.2 Model Security Audit

To prevent malicious models (e.g., containing backdoors or executing malicious code):

- Newly submitted models enter `pending` status
- Reviewed by validator nodes with reputation > 0.9
- Marked as `verified` after review passes
- Miners by default only accept tasks for `verified` models
- Model registrants must post a security deposit; malicious models result in forfeiture

---

## 9. Monitoring & Operations

### 9.1 Miner Prometheus Metrics

```
# GPU Metrics
qfc_miner_gpu_temperature_celsius{device="0"}
qfc_miner_gpu_utilization_percent{device="0"}
qfc_miner_gpu_vram_used_mb{device="0"}
qfc_miner_gpu_power_watts{device="0"}

# Task Metrics
qfc_miner_tasks_completed_total
qfc_miner_tasks_failed_total
qfc_miner_tasks_timeout_total
qfc_miner_task_inference_duration_ms
qfc_miner_task_queue_length

# Revenue Metrics
qfc_miner_rewards_total_qfc
qfc_miner_rewards_24h_qfc

# Network Metrics
qfc_miner_p2p_peers_connected
qfc_miner_contribution_score
```

### 9.2 Recommended Grafana Dashboard Panels

- GPU temperature/utilization/power consumption (timeline)
- Task completion count (hourly bar chart)
- Revenue trends (daily/weekly/monthly)
- Task type distribution (pie chart)
- Challenge task pass rate (key metric)
- P2P network connection status

---

## 10. Implementation Roadmap

### Phase 1: Basic Prototype (Month 5-6)

Synchronized with consensus mechanism Phase 2 (multi-dimensional scoring):

- [ ] Define GPU benchmark standard
- [ ] Implement qfc-miner basic framework (Rust)
  - GPU detection + benchmark
  - ONNX Runtime inference engine integration
  - Single-task execution flow
- [ ] On-chain AI Task Pool contract (simplified version)
  - Task submission / claiming / result submission
  - Basic fee escrow
- [ ] Off-chain Task Router (simplified version)
  - Single-node task distribution
  - Basic tier matching

**Milestone**: A single miner can receive and execute an image classification task and earn QFC rewards

### Phase 2: Verification & Security (Month 7-8)

- [ ] Challenge task system
- [ ] Redundant verification mechanism
- [ ] Miner penalty (slashing) integration
- [ ] Model registry + audit workflow
- [ ] Task pricing oracle

**Milestone**: 10+ miners running stably on testnet, challenge pass rate >95%

### Phase 3: Ecosystem Expansion (Month 9-10)

- [ ] AI-VM integration (on-chain contracts can call AI inference)
- [ ] Support for more inference frameworks (TensorRT, GGUF)
- [ ] Miner revenue dashboard
- [ ] SDK: JS/Python libraries for developers to submit AI tasks
- [ ] Distributed training prototype (federated learning)

**Milestone**: DApps can invoke AI inference through smart contracts, end-to-end closed loop

### Phase 4: Optimization & Mainnet (Month 11-12)

- [ ] Performance optimization (task scheduling, model caching)
- [ ] Security audit (contracts + miner client)
- [ ] Economic model stress testing
- [ ] Mainnet parameter finalization
- [ ] Documentation + miner tutorials

**Milestone**: AI compute network launches alongside mainnet

---

## 11. Open Questions (For Discussion)

1. **Task data privacy**: Should inference input data be encrypted? For medical/financial scenarios, miners should not see plaintext data. Consider Trusted Execution Environments (TEE) or homomorphic encryption.

2. **Model intellectual property**: If tasks use commercial models, how to prevent miners from copying them? May need model encryption + TEE solutions.

3. **Task source cold start**: There may not be enough real AI tasks in the early days. Consider:
   - Network-generated "useful computation" (e.g., indexing on-chain data, generating statistical analysis of on-chain data)
   - Partnering with AI companies to import inference demand

4. **Cross-tier task splitting**: Can large tasks be split across multiple Tier 1 miners for collaborative execution?

5. **GPU virtualization detection**: How to prevent miners from using cloud GPUs while claiming local hardware? (Is it even necessary to restrict this?)

---

## Appendix

### A. qfc-miner CLI Reference

```bash
# Start miner
qfc-miner start --config ./qfc-miner.yaml

# Run benchmark
qfc-miner benchmark --device 0

# View status
qfc-miner status

# View earnings
qfc-miner earnings --period 24h

# Stop miner
qfc-miner stop
```

### B. Glossary

| Term | Definition |
|------|-----------|
| qfc-miner | QFC AI compute miner client |
| Task Router | Off-chain task scheduler responsible for matching tasks and miners |
| Challenge Task | Verification task with a known answer, used to detect cheating |
| GPU Tier | GPU capability classification (Tier 1/2/3) |
| Inference | AI model inference — processing new data with a trained model |
| ONNX Runtime | Open-source cross-platform inference engine |
| Model Registry | On-chain model registry managing available AI models |

### C. Related Documents

- `00-PROJECT-OVERVIEW.md` — Project overview, AI-VM planning
- `02-CONSENSUS-MECHANISM.md` — PoC consensus, compute contribution dimension definition
- `03-TOKENOMICS.md` — Token economics, fee distribution rules
- `01-BLOCKCHAIN-DESIGN.md` — Core blockchain design, P2P network layer

---

**Document Version**: 1.0.0
**Last Updated**: 2026-02-20
**Status**: Draft
**Maintainer**: QFC Core Team
