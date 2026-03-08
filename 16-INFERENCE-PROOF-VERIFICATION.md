# 16-INFERENCE-PROOF-VERIFICATION.md — 推理证明验证机制设计

## 背景

QFC v2.0 引入 AI 推理挖矿后，矿工从 validator 领取推理任务 → 执行推理 → 提交 proof。早期实现使用 **全局 epoch 匹配** 来验证 proof 的有效性：validator 检查 `|proof.epoch - current_epoch| ≤ 1`，超出则拒绝。

这导致了严重的可用性问题：推理任务需要时间执行（几秒到几十秒），epoch 每 10 秒切换一次，导致约 1/3 的合法 proof 因 "epoch mismatch" 被拒绝。

## 行业调研

我们分析了主流 AI/计算区块链的做法：

### Bittensor

**方案：Validator 控制的 per-request timeout，epoch 仅用于奖励分发。**

- Validator（dendrite）给每个请求设 `timeout` 参数（默认 12s）
- Epoch（tempo = 360 blocks ≈ 72 分钟）仅控制 weight 提交和 emission 分发，与单个推理任务无关
- **防重放**：使用递增 nonce + 30 秒新鲜度检查。每个请求用 `(nonce, axon_hotkey, dendrite_hotkey, uuid)` 签名，axon 验证：
  - nonce 严格递增
  - nonce（Unix timestamp）在当前时间 ±30 秒内
- **慢但合法的结果**：不被拒绝，而是在评分中降权（latency penalty）

关键设计：Bittensor 完全避免了 staleness 问题——链上只看聚合后的 weight scores，从不看单个任务结果。

### Ritual Network

**方案：Subscription interval 时间窗口，不绑定 epoch。**

- 使用 Coordinator 合约的 subscription 模型：`activeAt`（开始时间）、`period`（间隔）、`frequency`（执行次数）、`redundancy`（每轮所需节点数）
- 每个 subscription interval 创建一个接受提交的窗口，达到 `redundancyCount` 后关闭
- 支持多种证明模式（ZK-ML、TEE、optimistic、probabilistic）
- Optimistic 模式：先接受结果，异步验证，dispute 走 challenge window

### Gensyn

**方案：Task 级别的 checkpoint 提交，不绑定全局 epoch。**

- Solver 在每个训练步骤 hash 中间状态（权重、梯度），提交 checkpoint
- 验证使用 **Pinpoint 双层二分法**：先定位第一个不一致的 iteration，再定位其中第一个不一致的 operation，只重新执行那一个操作
- Dispute 可以跨多个 block 进行，proof 不会因为"过时"而被拒
- 经济惩罚用 staking + slashing（Truebit 模型）

### Render Network

**方案：Per-job 生命周期，epoch 仅控制 emission。**

- Proof-of-Render（PoR）：节点提交渲染任务后验证
- 验证在交付后发生，不在特定 epoch 窗口内
- 24 小时 epoch 周期仅用于奖励发放
- 通过声誉系统处理恶意行为

### Akash Network

**方案：Lease-based 模型，无 epoch 级别验证。**

- Provider-tenant 的 lease 有明确的时间和范围
- 支付通过 deposit/withdrawal stream
- 不验证计算正确性，只验证可用性

### io.net

- 使用实时基准测试和容器化环境监控
- 依赖声誉和持续监控，非密码学 proof 计时

## 对比总结

| 机制 | Bittensor | Ritual | Gensyn | Render | Akash | QFC (旧) | QFC (新) |
|------|-----------|--------|--------|--------|-------|----------|----------|
| **验证粒度** | Per-request timeout | Subscription interval | Task checkpoint | Per-job | Lease | 全局 epoch ±1 | Timestamp 120s |
| **Epoch 作用** | 仅奖励分发 | 无 | 无 | 仅奖励分发 | 无 | 验证 + 奖励 | **仅奖励** |
| **防重放** | 递增 nonce + 30s 新鲜度 | Subscription interval + redundancy count | Checkpoint hash | 声誉系统 | Lease 身份 | Epoch 号 | **Timestamp + 签名** |
| **慢但合法** | 降分不拒绝 | 窗口内接受 | 容忍硬件差异 | 接受 | 接受 | **拒绝** ❌ | **接受** ✅ |

## 设计决策

### 核心原则

**行业共识：没有主流 AI 区块链用全局 epoch 来卡单个推理结果。**

通用模式：
1. Epoch 仅用于奖励聚合和分发
2. 使用 task 级别的 deadline
3. 防重放用 nonce/签名/commitment，不靠 epoch 号
4. 慢但合法的结果降分或正常接受，不拒绝

### QFC 新方案：Timestamp-Deadline 模型

```
矿工                                    Validator
  │                                        │
  │── fetch_task ──────────────────────────►│
  │◄── task (epoch, deadline, input) ──────│
  │                                        │
  │  [执行推理: 可能 1s ~ 60s+]            │
  │                                        │
  │── submit_proof(timestamp=now) ────────►│
  │                                        │
  │    verify_basic():                     │
  │    ✓ proof.timestamp 在 120s 内？      │  ← 防重放
  │    ✓ proof.timestamp 不是未来？        │  ← 防时钟篡改
  │    ✓ model 在批准列表？                │
  │    ✓ FLOPS 合理？                      │
  │                                        │
  │◄── accepted ──────────────────────────│
```

### 参数设计

| 参数 | 值 | 理由 |
|------|-----|------|
| `MAX_PROOF_AGE_SECS` | 120s | 覆盖大型推理任务（60s deadline + 余量），同时防止旧 proof 重放 |
| `MAX_FUTURE_SECS` | 10s | 容忍节点间时钟偏差，但防止时间戳篡改 |
| Task `deadline` | 30-60s | 由 task pool 根据任务类型设定 |

### 防重放机制

旧方案：依赖 epoch 号限制 proof 的"新鲜度"——但 epoch 切换太快导致误杀。

新方案：
1. **Timestamp 新鲜度**：proof.timestamp 必须在 `[now - 120s, now + 10s]` 范围内
2. **签名绑定**：每个 proof 包含 `(validator, epoch, task_type, input_hash, output_hash, timestamp)` 的 Ed25519 签名
3. **Proof pool 去重**：相同 `(input_hash, validator)` 的 proof 在同一个 epoch 内只接受一次

### 矿工侧优化

| 检查点 | 旧逻辑 | 新逻辑 |
|--------|--------|--------|
| 拿到任务后 | 检查 epoch diff | 检查 task deadline 是否已过 |
| 推理完成后 | 再次检查 epoch diff | 不需要——直接提交，由 validator 判断 |
| 被拒绝后 | 浪费了算力 | 几乎不会因时间问题被拒 |

## 未来改进

1. **Nonce 机制**（参考 Bittensor）：为每个 miner 维护递增 nonce，进一步强化防重放
2. **动态 MAX_PROOF_AGE**：根据任务类型调整（embedding 30s，text generation 180s）
3. **Latency scoring**（参考 Bittensor）：不拒绝慢的 proof，但在 PoC 评分中降权
4. **Challenge window**（参考 Ritual）：先接受 proof，异步验证，dispute 走仲裁流程

## 相关文件

| 文件 | 说明 |
|------|------|
| `qfc-core/crates/qfc-ai-coordinator/src/verification.rs` | 验证逻辑实现 |
| `qfc-core/crates/qfc-miner/src/worker.rs` | 矿工 worker 循环 |
| `qfc-core/crates/qfc-rpc/src/server.rs` | RPC 提交 proof 处理 |
| `qfc-core/crates/qfc-node/src/sync.rs` | P2P 收到 proof 的验证 |
| PR [#30](https://github.com/qfc-network/qfc-core/pull/30) | 实现 PR |

## 参考资料

- [Bittensor Synapse SDK Reference](https://docs.learnbittensor.org/python-api/html/autoapi/bittensor/core/synapse/)
- [Bittensor Subnet Hyperparameters](https://docs.learnbittensor.org/subnets/subnet-hyperparameters)
- [Ritual Coordinator Contract](https://docs.ritual.net/infernet/sdk/reference/Coordinator)
- [Ritual Symphony Protocol](https://www.ritualfoundation.org/docs/whats-new/symphony)
- [Gensyn Verde Verification](https://www.gensyn.ai/articles/verde)
- [Gensyn Litepaper](https://docs.gensyn.ai/litepaper)
