# QFC RPC API Specification — `qfc_*` namespace

> Last updated: 2026-04-14
> Source of truth: `qfc-core/crates/qfc-rpc/src/qfc.rs`. This doc is a snapshot derived from that source and may lag by 1–2 releases. When in doubt, read the Rust.
> Chain endpoint: `https://rpc.testnet.qfc.network` (testnet, chain id 9000)

QFC exposes the standard `eth_*` methods (via the EVM-compatible execution layer) plus a `qfc_*` namespace for AI inference, mining, staking, governance, and chain introspection. This document covers only `qfc_*`.

## Request format

JSON-RPC 2.0 over HTTP POST:

```json
{
  "jsonrpc": "2.0",
  "method": "qfc_<methodName>",
  "params": [ ... ],
  "id": 1
}
```

`params` is always an array. Single-object methods wrap the object in a one-element array. Methods taking multiple positional args (e.g. `qfc_getMinerEarnings`) use an array of primitives.

## Conventions

| Field type | Encoding |
|---|---|
| Addresses | lowercase hex string with or without `0x` prefix — canonical: `0x` + 40 hex chars |
| Wei amounts | hex string with `0x` prefix (e.g. `"0xde0b6b3a7640000"` = 1 QFC) |
| Signatures | Ed25519, hex-encoded, 128 chars (no `0x`) or 130 chars (with `0x`) |
| Timestamps | milliseconds since Unix epoch unless noted |
| GPU tier | enum string: `"Hot"`, `"Warm"`, `"Cold"` |
| Backend | enum string: `"CUDA"`, `"Metal"`, `"CPU"`, `"ROCm"`, `"OpenCL"` |

## Error codes

| Code | Name | Meaning |
|---|---|---|
| -32602 | InvalidParams | Missing / wrong field type |
| -32000 | Execution | Valid request but on-chain / runtime rejected it |
| -32001 | BlockNotFound | Block height or hash doesn't exist |
| -32002 | TransactionNotFound | Tx hash not on chain |
| -32003 | AccountNotFound | Address has no associated state |
| -32603 | Internal | Server-side issue; retry |

---

## Mining — register, status, earnings, vesting

### `qfc_registerMiner`

Registers a miner and returns the assigned GPU tier. Must be signed.

**Params** — array of one object:
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

**Returns**:
```
registered:    bool
assignedTier:  u8  (0=Cold, 1=Warm, 2=Hot)
message:       string
```

### `qfc_getRegisteredMiners`

**Params**: none

**Returns**: array of:
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

Miner heartbeat reporting loaded models and pending tasks.

**Params**: array of one object:
```
minerAddress:   string (hex)
loadedModels:   [{ name, version, loadedAt }]
pendingTasks:   u32
signature:      string (Ed25519)
```

**Returns**: `bool`

### `qfc_getMinerEarnings`

**Params**: `[address, period]` where period is `"day"`, `"week"`, `"month"`, or `"all"`.

**Returns**:
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

> ⚠ `"all"` can return multi-megabyte bodies on an active miner. Prefer `"day"` or `"week"` for UIs.

### `qfc_getMinerVesting`

**Params**: `[address]`

**Returns**:
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

Vesting: 7-day cliff + 23-day linear unlock (total 30 days from earn).

---

## Validators, staking, epoch

### `qfc_getValidators`

**Params**: none

**Returns**: array of:
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

**Params**: `[address]`

**Returns**: `string` (hex, 0–10000)

### `qfc_getValidatorScoreBreakdown`

**Params**: `[address]`

**Returns**:
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

**Params**: `[address]`

**Returns**: `string` (wei, decimal)

### `qfc_getEpoch`

**Params**: none

**Returns**:
```
number:      string (hex)
startTime:   string (hex ms)
durationMs:  string (hex)
```

---

## Inference — miner-side

### `qfc_getInferenceTask`

Miners call this to pull the next task matching their hardware.

**Params**: array of one object:
```
minerAddress:       string (hex)
gpuTier:            string (Hot | Warm | Cold)
availableMemoryMb:  u64
backend:            string (CUDA | Metal | CPU)
```

**Returns**: `null` (no task available) or:
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

**Params**: array of one object:
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

**Returns**:
```
accepted:        bool
spotChecked:     bool  (was this proof randomly selected for challenge)
message:         string
rewardEstimate:  Option<string> (hex wei)
```

---

## Inference — user-side

### `qfc_submitPublicTask`

**Params**: array of one object:
```
taskType:      string (TextEmbedding | TextGeneration | ImageClassification | OnnxInference)
modelId:       string  ("{name}:{version}", e.g. "qfc-embed-small:v1.0")
inputData:     string (hex)
maxFee:        string (hex wei)
submitter:     string (hex)
signature:     string (Ed25519 hex of solidity_packed(submitter, modelId, inputData, maxFee))
language:      Option<string>  (BCP-47, required for speech tasks)
```

**Returns**: `string` — task id (hex)

### `qfc_getPublicTaskStatus`

**Params**: `[taskId]`

**Returns**:
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

**Params**: array of one object:
```
submitter:  Option<string> (hex, filter)
status:     Option<string> (filter)
limit:      usize  (default 50, max 200)
offset:     usize  (default 0)
```

**Returns**: array of `RpcPublicTaskStatus` (same shape as `qfc_getPublicTaskStatus`).

### `qfc_getInferenceResult`

**Params**: `[cid]` — IPFS CID from a task's `resultCid`

**Returns**: `string` (base64-encoded bytes)

### `qfc_estimateInferenceFee`

**Params**: array of one object:
```
modelId:     string
taskType:    string (default "TextEmbedding")
inputSize:   u64 (bytes, default 0)
maxTokens:   u64 (default 100)
```

**Returns**:
```
baseFee:           string (hex wei)
modelId:           string
gpuTier:           string (Hot | Warm | Cold)
estimatedTimeMs:   u64
minMemoryMb:       u64
estimatedFlops:    u64
```

---

## Catalog — models, stats, compute info

### `qfc_getSupportedModels`

**Params**: none

**Returns**: array of:
```
name, version, minTier: string
minMemoryMb:            u64
approved:               bool
```

### `qfc_getInferenceStats`

**Params**: none

**Returns**:
```
tasksCompleted: string (hex)
avgTimeMs:      string (hex)
flopsTotal:     string (hex)
passRate:       string ("0.00" to "100.00" percent)
```

### `qfc_getComputeInfo`

Current *this-node*'s compute profile (local call — returns what this RPC node itself can serve).

**Params**: none

**Returns**:
```
backend:           string (CUDA | Metal | CPU | none)
supportedModels:   Vec<string>
gpuMemoryMb:       u64
inferenceScore:    string (hex)
gpuTier:           string (Hot | Warm | Cold | unknown)
providesCompute:   bool
```

---

## Governance — model proposals

### `qfc_proposeModel`

Anyone can propose. No ACL on this method.

**Params**: array of one object:
```
proposer:      string (hex)
modelName:     string
modelVersion:  string
description:   string
minMemoryMb:   u64
minTier:       string (Hot | Warm | Cold)
sizeMb:        u64
```

**Returns**: `string` — proposal id (hex)

### `qfc_voteModel`

Only active validators can vote. 1 validator = 1 vote. >2/3 supermajority required to pass.

**Params**: array of one object:
```
proposalId:   string (hex)
voter:        string (hex address — must be an active validator)
approve:      bool
```

**Returns**: `bool` (whether the vote was recorded — not whether the proposal passed)

---

## Treasury

### `qfc_getTreasuryInfo`

**Params**: none

**Returns**:
```
address:          string (hex — treasury address)
balance:          string (hex wei)
totalDisbursed:   string (hex wei)
activeProposals:  u64
```

---

## Chain introspection

### `qfc_nodeInfo`

**Params**: none

**Returns**:
```
version:      string (node semver)
chainId:      string (hex)
peerCount:    u64
isValidator:  bool
syncing:      bool
```

### `qfc_requestFaucet`

Testnet-only. Dispenses test QFC to an address. Enforced 24-hour cooldown per address.

**Params**: `[address, amount]` — amount is hex wei

**Returns**:
```
txHash:  string (hex)
amount:  string (hex wei)
to:      string (hex)
```

Errors with `Execution` if called on mainnet (chain id ≠ 9000) or if the address is in cooldown.

---

## Example — submit and poll a public inference task

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

Full working examples: [`sdk-snippets/call-inference.js`](./sdk-snippets/call-inference.js), [`sdk-snippets/call-inference.py`](./sdk-snippets/call-inference.py).

---

## What's missing / known issues

- **No websocket subscriptions for task events yet.** Clients must poll. If you're building a real app, that's a bandwidth concern — raise it as a feature request.
- **`qfc_getMinerVesting` can exceed the 10 MiB response size cap** for miners with thousands of tranches. Pagination parameter would help; not implemented as of v2.2.3.
- **`qfc_getInferenceResult`** returns raw bytes without type info. The client has to know the shape from `modelId`. A `resultMetadata` field with `{ dims, dtype, layout }` would save a lot of downstream bugs.
- **No RPC for `qfc_cancelPublicTask`.** Once submitted, you wait for completion or deadline. On-chain cancel would matter when fees get real.
