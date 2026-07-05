# QFC RPC API 规范 — `qfc_*` 命名空间

[English](./43-RPC-API-SPEC-EN.md) | **中文**

> 最后更新：2026-04-14
> 权威来源：`qfc-core/crates/qfc-rpc/src/qfc.rs`。本文档是从该源码派生的快照，可能落后 1–2 个版本。有疑问时，请直接阅读 Rust 源码。
> 链端点：`https://rpc.testnet.qfc.network`（测试网，chain id 9000）

QFC 暴露标准的 `eth_*` 方法（经由 EVM 兼容执行层），并额外提供 `qfc_*` 命名空间，用于 AI 推理、挖矿、质押、治理和链自省。本文档仅覆盖 `qfc_*`。

## 请求格式

基于 HTTP POST 的 JSON-RPC 2.0：

```json
{
  "jsonrpc": "2.0",
  "method": "qfc_<methodName>",
  "params": [ ... ],
  "id": 1
}
```

`params` 始终是数组。接受单个对象的方法将该对象包装在只含一个元素的数组中。接受多个位置参数的方法（例如 `qfc_getMinerEarnings`）使用由原始值组成的数组。

## 约定

| 字段类型 | 编码 |
|---|---|
| 地址 | 小写十六进制字符串，带或不带 `0x` 前缀 — 规范形式：`0x` + 40 个十六进制字符 |
| Wei 金额 | 带 `0x` 前缀的十六进制字符串（例如 `"0xde0b6b3a7640000"` = 1 QFC） |
| 签名 | Ed25519，十六进制编码，128 字符（不带 `0x`）或 130 字符（带 `0x`） |
| 时间戳 | 除特别说明外，均为自 Unix 纪元起的毫秒数 |
| GPU 层级 | 枚举字符串：`"Hot"`、`"Warm"`、`"Cold"` |
| 后端 | 枚举字符串：`"CUDA"`、`"Metal"`、`"CPU"`、`"ROCm"`、`"OpenCL"` |

## 错误码

| 码 | 名称 | 含义 |
|---|---|---|
| -32602 | InvalidParams | 字段缺失/字段类型错误 |
| -32000 | Execution | 请求合法，但被链上/运行时拒绝 |
| -32001 | BlockNotFound | 区块高度或哈希不存在 |
| -32002 | TransactionNotFound | 交易哈希不在链上 |
| -32003 | AccountNotFound | 地址没有关联状态 |
| -32603 | Internal | 服务端问题；请重试 |

---

## 挖矿 — 注册、状态、收益、锁仓释放

### `qfc_registerMiner`

注册一个矿工并返回分配到的 GPU 层级。必须携带签名。

**参数** — 只含一个对象的数组：
```
minerAddress:    string (hex address)
publicKey:       string (hex, Ed25519 public key)
gpuModel:        string (e.g. "RTX 3060", "CPU (8 cores)")
vramMb:          u64
benchmarkScore:  u32 (0–10000)
backend:         string (CUDA | Metal | CPU | ROCm | OpenCL)
signature:       string (Ed25519 hex)
os:              string (linux | macos | windows)
arch:            string (x86_64 | aarch64)
cpuModel:        string
cpuCores:        u32
totalMemoryMb:   u64
version:         string  (semver of the miner binary)
```

**返回**：
```
registered:    bool
assignedTier:  u8  (0=Cold, 1=Warm, 2=Hot)
message:       string
```

### `qfc_getRegisteredMiners`

**参数**：无

**返回**：数组，元素为：
```
address:          string
gpuModel:         string
benchmarkScore:   u32
tier:             u8
vramMb:           u64
backend:          string
registeredAt:     string  (unix seconds)
os, arch, cpuModel, cpuCores, totalMemoryMb, version: as registerMiner
```

### `qfc_reportMinerStatus`

矿工心跳，上报已加载的模型和待处理任务。

**参数**：只含一个对象的数组：
```
minerAddress:   string (hex)
loadedModels:   [{ name, version, loadedAt }]
pendingTasks:   u32
signature:      string (Ed25519)
```

**返回**：`bool`

### `qfc_getMinerEarnings`

**参数**：`[address, period]`，其中 period 为 `"day"`、`"week"`、`"month"` 或 `"all"`。

**返回**：
```
address:        string
totalEarnings:  string (hex wei)
totalFlops:     string (hex)
totalTasks:     string (hex)
balance:        string (hex wei — current liquid balance of this address)
records:        [{
    blockHeight:  string (hex)
    reward:       string (hex wei)
    flops:        string (hex)
    taskCount:    string (hex)
    taskType:     string
    timestamp:    u64 (ms)
}]
```

> ⚠ 对活跃矿工，`"all"` 可能返回数 MB 大小的响应体。UI 场景建议优先使用 `"day"` 或 `"week"`。

### `qfc_getMinerVesting`

**参数**：`[address]`

**返回**：
```
miner:          string
totalEarned:    string (hex wei)
locked:         string (hex wei)
available:      string (hex wei)
activeTranches: u64
tranches: [{
    blockHeight:   string (hex)
    amount:        string (hex wei)
    vested:        string (hex wei)
    cliffEnd:      u64 (ms)
    endTime:       u64 (ms)
    percentVested: u8 (0–100)
}]
```

锁仓释放：7 天 cliff + 23 天线性解锁（自获得奖励起共 30 天）。

---

## 验证者、质押、纪元

### `qfc_getValidators`

**参数**：无

**返回**：数组，元素为：
```
address:            string
stake:              string (hex wei)
contributionScore:  string (hex, 0–10000 representing 0–100%)
uptime:             string (hex, 0–10000)
isActive:           bool
providesCompute:    bool
hashrate:           string (H/s, "0" if not mining via PoW)
inferenceScore:     string (hex)
computeMode:        string (pow | inference | none)
tasksCompleted:     string (hex)
```

### `qfc_getContributionScore`

**参数**：`[address]`

**返回**：`string`（十六进制，0–10000）

### `qfc_getValidatorScoreBreakdown`

**参数**：`[address]`

**返回**：
```
address, totalScore:  string
stake, stakeScore:    string       (30% weight)
computeScore:         string       (20% weight)
uptimeScore:          string       (15% weight)
accuracyScore:        string       (15% weight)
networkScore:         string       (10% weight)
storageScore:         string       (5%  weight)
reputationScore:      string       (5%  weight)
metrics: { ... raw inputs used to compute each subscore ... }
```

### `qfc_getStake`

**参数**：`[address]`

**返回**：`string`（wei，十进制）

### `qfc_getEpoch`

**参数**：无

**返回**：
```
number:      string (hex)
startTime:   string (hex ms)
durationMs:  string (hex)
```

---

## 推理 — 矿工侧

### `qfc_getInferenceTask`

矿工调用此方法拉取与其硬件匹配的下一个任务。

**参数**：只含一个对象的数组：
```
minerAddress:       string (hex)
gpuTier:            string (Hot | Warm | Cold)
availableMemoryMb:  u64
backend:            string (CUDA | Metal | CPU)
```

**返回**：`null`（无可用任务）或：
```
taskId:        string (hex)
epoch:         u64
taskType:      string (embedding | text_generation | image_classification | onnx)
modelName:     string
modelVersion:  string
inputData:     string (hex)
deadline:      u64 (ms)
```

### `qfc_submitInferenceProof`

**参数**：只含一个对象的数组：
```
minerAddress:      string (hex)
taskId:            string (hex)
epoch:             u64
outputHash:        string (hex, blake3 of result bytes)
executionTimeMs:   u64
flopsEstimated:    u64
backend:           string
proofBytes:        string (hex)
resultData:        Option<string> (hex-encoded result bytes)
```

**返回**：
```
accepted:        bool
spotChecked:     bool  (was this proof randomly selected for challenge)
message:         string
rewardEstimate:  Option<string> (hex wei)
```

---

## 推理 — 用户侧

### `qfc_submitPublicTask`

**参数**：只含一个对象的数组：
```
taskType:      string (TextEmbedding | TextGeneration | ImageClassification | OnnxInference)
modelId:       string  ("{name}:{version}", e.g. "qfc-embed-small:v1.0")
inputData:     string (hex)
maxFee:        string (hex wei)
submitter:     string (hex)
signature:     string (Ed25519 hex of solidity_packed(submitter, modelId, inputData, maxFee))
language:      Option<string>  (BCP-47, required for speech tasks)
```

**返回**：`string` — 任务 id（十六进制）

### `qfc_getPublicTaskStatus`

**参数**：`[taskId]`

**返回**：
```
taskId:            string
status:            string (Pending | Completed | Failed | Expired)
submitter:         string (hex)
taskType:          string
modelId:           string
createdAt:         u64 (ms)
deadline:          u64 (ms)
maxFee:            string (hex wei)
result:            Option<string>  (base64, only if Completed and inline)
resultSize:        Option<usize>
resultType:        Option<string>  (inline | ipfs)
resultCid:         Option<string>  (IPFS CID if large)
resultPreview:     Option<string>  (base64, up to 1 KB of preview for IPFS results)
minerAddress:      Option<string>  (hex)
executionTimeMs:   Option<u64>
```

### `qfc_listPublicTasks`

**参数**：只含一个对象的数组：
```
submitter:  Option<string> (hex, filter)
status:     Option<string> (filter)
limit:      usize  (default 50, max 200)
offset:     usize  (default 0)
```

**返回**：`RpcPublicTaskStatus` 数组（结构与 `qfc_getPublicTaskStatus` 相同）。

### `qfc_getInferenceResult`

**参数**：`[cid]` — 来自任务 `resultCid` 字段的 IPFS CID

**返回**：`string`（base64 编码的字节）

### `qfc_estimateInferenceFee`

**参数**：只含一个对象的数组：
```
modelId:     string
taskType:    string (default "TextEmbedding")
inputSize:   u64 (bytes, default 0)
maxTokens:   u64 (default 100)
```

**返回**：
```
baseFee:           string (hex wei)
modelId:           string
gpuTier:           string (Hot | Warm | Cold)
estimatedTimeMs:   u64
minMemoryMb:       u64
estimatedFlops:    u64
```

---

## 目录 — 模型、统计、算力信息

### `qfc_getSupportedModels`

**参数**：无

**返回**：数组，元素为：
```
name, version, minTier: string
minMemoryMb:            u64
approved:               bool
```

### `qfc_getInferenceStats`

**参数**：无

**返回**：
```
tasksCompleted: string (hex)
avgTimeMs:      string (hex)
flopsTotal:     string (hex)
passRate:       string ("0.00" to "100.00" percent)
```

### `qfc_getComputeInfo`

当前*本节点*的算力档案（本地调用 — 返回本 RPC 节点自身能够提供的服务能力）。

**参数**：无

**返回**：
```
backend:           string (CUDA | Metal | CPU | none)
supportedModels:   Vec<string>
gpuMemoryMb:       u64
inferenceScore:    string (hex)
gpuTier:           string (Hot | Warm | Cold | unknown)
providesCompute:   bool
```

---

## 治理 — 模型提案

### `qfc_proposeModel`

任何人都可以提案。此方法没有 ACL。

**参数**：只含一个对象的数组：
```
proposer:      string (hex)
modelName:     string
modelVersion:  string
description:   string
minMemoryMb:   u64
minTier:       string (Hot | Warm | Cold)
sizeMb:        u64
```

**返回**：`string` — 提案 id（十六进制）

### `qfc_voteModel`

仅活跃验证者可以投票。1 个验证者 = 1 票。需要 >2/3 的绝对多数才能通过。

**参数**：只含一个对象的数组：
```
proposalId:   string (hex)
voter:        string (hex address — must be an active validator)
approve:      bool
```

**返回**：`bool`（表示该票是否被记录 — 不表示提案是否通过）

---

## 国库

### `qfc_getTreasuryInfo`

**参数**：无

**返回**：
```
address:          string (hex — treasury address)
balance:          string (hex wei)
totalDisbursed:   string (hex wei)
activeProposals:  u64
```

---

## 链自省

### `qfc_nodeInfo`

**参数**：无

**返回**：
```
version:      string (node semver)
chainId:      string (hex)
peerCount:    u64
isValidator:  bool
syncing:      bool
```

### `qfc_requestFaucet`

仅测试网可用。向指定地址发放测试 QFC。每个地址强制 24 小时冷却。

**参数**：`[address, amount]` — amount 为十六进制 wei

**返回**：
```
txHash:  string (hex)
amount:  string (hex wei)
to:      string (hex)
```

在主网（chain id ≠ 9000）上调用，或地址处于冷却期时，返回 `Execution` 错误。

---

## 示例 — 提交并轮询一个公开推理任务

```bash
# 1. Estimate fee
curl https://rpc.testnet.qfc.network -X POST -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"qfc_estimateInferenceFee","params":[{"modelId":"qfc-embed-small:v1.0","taskType":"TextEmbedding","inputSize":256,"maxTokens":100}],"id":1}'

# → { "result": { "baseFee": "0x5af3107a4000", "estimatedTimeMs": 10000, ... } }

# 2. Submit (you need a valid signature — see sdk-snippets/)
curl https://rpc.testnet.qfc.network -X POST -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"qfc_submitPublicTask","params":[{...}],"id":1}'

# → { "result": "0x<taskId>" }

# 3. Poll status
curl https://rpc.testnet.qfc.network -X POST -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"qfc_getPublicTaskStatus","params":["<taskId>"],"id":1}'
```

完整可运行示例：[`sdk-snippets/call-inference.js`](./sdk-snippets/call-inference.js)、[`sdk-snippets/call-inference.py`](./sdk-snippets/call-inference.py)。

---

## 缺失内容/已知问题

- **尚无任务事件的 websocket 订阅。** 客户端必须轮询。如果你在构建真实应用，这是一个带宽层面的顾虑 — 请以 feature request 的形式提出。
- 对拥有数千个 tranche 的矿工，**`qfc_getMinerVesting` 可能超过 10 MiB 的响应大小上限**。加一个分页参数会有帮助；截至 v2.2.3 尚未实现。
- **`qfc_getInferenceResult`** 返回不带类型信息的原始字节。客户端必须根据 `modelId` 自行推断数据形状。增加一个带 `{ dims, dtype, layout }` 的 `resultMetadata` 字段可以省去大量下游 bug。
- **没有 `qfc_cancelPublicTask` RPC。** 一旦提交，只能等待任务完成或到达截止时间。当费用变得真实后，链上取消会变得重要。
