# 16-INFERENCE-PROOF-VERIFICATION.md — Inference Proof Verification Mechanism Design

## Background

After QFC v2.0 introduced AI inference mining, miners fetch inference tasks from validators, execute inference, and submit proofs. The early implementation used **global epoch matching** to verify proof validity: the validator checks `|proof.epoch - current_epoch| <= 1` and rejects any proof that falls outside this range.

This caused severe usability issues: inference tasks take time to execute (a few seconds to tens of seconds), and epochs switch every 10 seconds, resulting in roughly 1/3 of legitimate proofs being rejected due to "epoch mismatch."

## Industry Research

We analyzed how mainstream AI/compute blockchains handle this:

### Bittensor

**Approach: Validator-controlled per-request timeout; epochs are only used for reward distribution.**

- The validator (dendrite) sets a `timeout` parameter for each request (default 12s)
- Epochs (tempo = 360 blocks ~ 72 minutes) only control weight submission and emission distribution, unrelated to individual inference tasks
- **Replay protection**: Uses incrementing nonce + 30-second freshness check. Each request is signed with `(nonce, axon_hotkey, dendrite_hotkey, uuid)`, and the axon verifies:
  - Nonce is strictly incrementing
  - Nonce (Unix timestamp) is within +/-30 seconds of the current time
- **Slow but legitimate results**: Not rejected, but downweighted in scoring (latency penalty)

Key design insight: Bittensor completely avoids the staleness problem — the chain only sees aggregated weight scores, never individual task results.

### Ritual Network

**Approach: Subscription interval time windows, not tied to epochs.**

- Uses a Coordinator contract subscription model: `activeAt` (start time), `period` (interval), `frequency` (number of executions), `redundancy` (number of nodes required per round)
- Each subscription interval creates a submission acceptance window, which closes once the `redundancyCount` is reached
- Supports multiple proof modes (ZK-ML, TEE, optimistic, probabilistic)
- Optimistic mode: Accept results first, verify asynchronously, disputes go through a challenge window

### Gensyn

**Approach: Task-level checkpoint submission, not tied to a global epoch.**

- Solvers hash intermediate state (weights, gradients) at each training step and submit checkpoints
- Verification uses **Pinpoint bisection**: first locate the first inconsistent iteration, then locate the first inconsistent operation within it, and re-execute only that single operation
- Disputes can span multiple blocks; proofs are never rejected for being "stale"
- Economic penalties use staking + slashing (Truebit model)

### Render Network

**Approach: Per-job lifecycle; epochs only control emission.**

- Proof-of-Render (PoR): Nodes submit rendering tasks and verify after completion
- Verification happens after delivery, not within a specific epoch window
- The 24-hour epoch cycle is used solely for reward distribution
- Malicious behavior is handled through a reputation system

### Akash Network

**Approach: Lease-based model with no epoch-level verification.**

- Provider-tenant leases have explicit time ranges and scopes
- Payments are handled through deposit/withdrawal streams
- Does not verify computational correctness, only availability

### io.net

- Uses real-time benchmarking and containerized environment monitoring
- Relies on reputation and continuous monitoring, not cryptographic proof timing

## Comparison Summary

| Mechanism | Bittensor | Ritual | Gensyn | Render | Akash | QFC (Old) | QFC (New) |
|-----------|-----------|--------|--------|--------|-------|-----------|-----------|
| **Verification granularity** | Per-request timeout | Subscription interval | Task checkpoint | Per-job | Lease | Global epoch +/-1 | Timestamp 120s |
| **Epoch role** | Reward distribution only | None | None | Reward distribution only | None | Verification + rewards | **Rewards only** |
| **Replay protection** | Incrementing nonce + 30s freshness | Subscription interval + redundancy count | Checkpoint hash | Reputation system | Lease identity | Epoch number | **Timestamp + signature** |
| **Slow but legitimate** | Downweighted, not rejected | Accepted within window | Tolerates hardware variance | Accepted | Accepted | **Rejected** | **Accepted** |

## Design Decisions

### Core Principles

**Industry consensus: No mainstream AI blockchain uses a global epoch to gate individual inference results.**

Common patterns:
1. Epochs are used only for reward aggregation and distribution
2. Task-level deadlines are used instead
3. Replay protection relies on nonce/signature/commitment, not epoch numbers
4. Slow but legitimate results are downweighted or accepted normally, never rejected

### QFC New Approach: Timestamp-Deadline Model

```
Miner                                   Validator
  |                                        |
  |-- fetch_task ------------------------->|
  |<-- task (epoch, deadline, input) ------|
  |                                        |
  |  [Execute inference: may take 1s~60s+] |
  |                                        |
  |-- submit_proof(timestamp=now) -------->|
  |                                        |
  |    verify_basic():                     |
  |    + proof.timestamp within 120s?      |  <- Replay protection
  |    + proof.timestamp not in the future?|  <- Clock tampering prevention
  |    + model on approved list?           |
  |    + FLOPS reasonable?                 |
  |                                        |
  |<-- accepted --------------------------|
```

### Parameter Design

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `MAX_PROOF_AGE_SECS` | 120s | Covers large inference tasks (60s deadline + margin) while preventing old proof replay |
| `MAX_FUTURE_SECS` | 10s | Tolerates clock skew between nodes while preventing timestamp tampering |
| Task `deadline` | 30-60s | Set by the task pool based on task type |

### Replay Protection Mechanism

Old approach: Relied on epoch numbers to limit proof "freshness" — but epochs switched too fast, causing false rejections.

New approach:
1. **Timestamp freshness**: proof.timestamp must be within `[now - 120s, now + 10s]`
2. **Signature binding**: Each proof includes an Ed25519 signature over `(validator, epoch, task_type, input_hash, output_hash, timestamp)`
3. **Proof pool deduplication**: Proofs with the same `(input_hash, validator)` are accepted only once per epoch

### Miner-Side Optimizations

| Checkpoint | Old Logic | New Logic |
|------------|-----------|-----------|
| After receiving task | Check epoch diff | Check if task deadline has passed |
| After inference completion | Check epoch diff again | Not needed — submit directly, validator decides |
| After rejection | Computing power wasted | Almost never rejected due to timing |

## Future Improvements

1. **Nonce mechanism** (inspired by Bittensor): Maintain an incrementing nonce per miner to further strengthen replay protection
2. **Dynamic MAX_PROOF_AGE**: Adjust based on task type (embedding 30s, text generation 180s)
3. **Latency scoring** (inspired by Bittensor): Don't reject slow proofs, but downweight them in PoC scoring
4. **Challenge window** (inspired by Ritual): Accept proofs first, verify asynchronously, disputes go through an arbitration process

## Related Files

| File | Description |
|------|-------------|
| `qfc-core/crates/qfc-ai-coordinator/src/verification.rs` | Verification logic implementation |
| `qfc-core/crates/qfc-miner/src/worker.rs` | Miner worker loop |
| `qfc-core/crates/qfc-rpc/src/server.rs` | RPC proof submission handling |
| `qfc-core/crates/qfc-node/src/sync.rs` | P2P proof verification on receipt |
| PR [#30](https://github.com/qfc-network/qfc-core/pull/30) | Implementation PR |

## References

- [Bittensor Synapse SDK Reference](https://docs.learnbittensor.org/python-api/html/autoapi/bittensor/core/synapse/)
- [Bittensor Subnet Hyperparameters](https://docs.learnbittensor.org/subnets/subnet-hyperparameters)
- [Ritual Coordinator Contract](https://docs.ritual.net/infernet/sdk/reference/Coordinator)
- [Ritual Symphony Protocol](https://www.ritualfoundation.org/docs/whats-new/symphony)
- [Gensyn Verde Verification](https://www.gensyn.ai/articles/verde)
- [Gensyn Litepaper](https://docs.gensyn.ai/litepaper)
