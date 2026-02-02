# QFC Chain Gap Analysis (Design vs. Implementation)

Last Updated: 2026-02-02

This document summarizes a high-level gap analysis between the QFC design docs
and a light code scan of `qfc-core`. It is intended as a planning aid for
prioritizing core chain work.

Scope of code scan (light):
- qfc-core/crates/qfc-consensus
- qfc-core/crates/qfc-node
- qfc-core/crates/qfc-mempool
- qfc-core/crates/qfc-rpc
- qfc-core/crates/qfc-network (shallow)

Notes:
- This is not a full audit. It highlights likely gaps and risks.
- Some items may already be implemented elsewhere; treat as "needs verification."

---

## Summary by Domain

### Consensus (PoC)
Design intent (docs/02-CONSENSUS-MECHANISM.md):
- Multi-dimensional contribution scoring with dynamic weights
- VRF-based producer selection
- Weighted vote finality (2/3)
- Slashing for misbehavior with explicit penalties

Observed in code:
- PoC scoring + dynamic weights are implemented in `qfc-consensus`.
- VRF selection and weighted voting/finality logic exist.
- Slashing logic exists in-memory in consensus engine.
- Evidence handling exists in `qfc-node` sync flow.

Primary gaps:
- Slashing and penalties are not clearly persisted to chain state (storage).
- Metrics used for scoring (latency, storage, compute) lack clear, verifiable on-chain proof.

### Node / Network
Design intent (docs/01-BLOCKCHAIN-DESIGN.md):
- P2P with libp2p (GossipSub/Kademlia/Req-Resp)
- Sync modes: full/fast/light
- Mempool: nonce, gas price ordering, expiry

Observed in code:
- P2P and sync manager exist; block sync is basic.
- Mempool ordering exists; nonce check references TODO to state.

Primary gaps:
- Fast/Light sync not implemented (only block sync).
- Mempool nonce validation not tied to state.
- P2P DoS mitigation/peer reputation not visible.

### Governance
Design intent:
- Parameter governance and proposal lifecycle

Observed in code:
- No governance module or chain parameter update workflow found.

Primary gaps:
- Proposal, voting, execution pipeline.
- On-chain parameter updates and emergency controls.

### Security
Design intent:
- Slashing for multiple offenses
- Long-range attack and nothing-at-stake defenses
- Key management and operational safeguards

Observed in code:
- Slashing functions exist but appear in-memory.
- No explicit checkpoints / weak subjectivity enforcement found.

Primary gaps:
- On-chain slashing state transitions.
- Checkpointing and replay protections for long-range attacks.

### Ecosystem / RPC
Design intent:
- Eth-compatible JSON-RPC + QFC extensions
- WebSocket subscriptions for logs/newHeads/pending

Observed in code:
- HTTP RPC implemented; eth + qfc namespaces exist.
- WebSocket subscriptions not found.

Primary gaps:
- WS subscriptions for logs/newHeads/pending.
- Filter APIs in core RPC.

---

## Gap Matrix (High-Level)

| Domain | Requirement | Status | Evidence | Priority |
|---|---|---|---|---|
| Consensus | PoC scoring + dynamic weights | Partial | qfc-consensus scoring/NetworkState | P1 |
| Consensus | VRF selection & weighted finality | Present | qfc-consensus engine | P0 |
| Consensus | Slashing persisted on-chain | Gap | in-memory slash only | P0 |
| Node | Fast/Light sync | Gap | sync.rs basic block sync | P0 |
| Node | Mempool nonce vs state | Gap | TODO in mempool | P0 |
| Network | DoS/peer scoring | Gap | not evident in scan | P1 |
| Governance | Proposal/voting/execution | Gap | no module found | P0 |
| Security | Long-range attack checkpointing | Gap | not evident | P1 |
| RPC | WS subscriptions | Gap | HTTP only | P1 |
| RPC | eth filter APIs | Partial | in core RPC not found | P1 |

---

## Suggested P0 Worklist

1) Mempool nonce validation against state
2) Implement fast/quick sync (snapshots + state pruning)
3) Slashing as chain-state transitions (balance/jail persistence)
4) Minimal governance flow for parameter updates

## Suggested P1 Worklist

1) WS subscriptions (newHeads/logs/pending)
2) Peer reputation / rate limits for P2P
3) Checkpointing / weak subjectivity

---

## References

Design docs:
- qfc-design/01-BLOCKCHAIN-DESIGN.md
- qfc-design/02-CONSENSUS-MECHANISM.md
- qfc-design/03-TOKENOMICS.md

Code scan paths:
- qfc-core/crates/qfc-consensus
- qfc-core/crates/qfc-node
- qfc-core/crates/qfc-mempool
- qfc-core/crates/qfc-rpc
