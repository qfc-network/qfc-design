# Ethereum 2030 Roadmap & QFC Implications

> Last Updated: 2026-03-09 | Version 1.0
> GitHub Issue: #25
> Author: Alex Wei, Product Manager @ QFC Network

---

## 1. Executive Summary

Ethereum's 2030 roadmap — spanning the Surge, Scourge, Verge, Purge, Splurge, and the new Beam Chain proposal — represents the most ambitious upgrade path in blockchain history. As a new L1 building from scratch, QFC has a rare opportunity: **learn from Ethereum's decade of technical debt and build the 2030 target state as our v1 architecture**.

This document surveys each Ethereum roadmap track, extracts the core problem being solved, and identifies concrete implications for QFC's v3.0 design.

**Key Takeaway**: 6 of Ethereum's 7 major upgrade tracks are solving problems caused by legacy design decisions. QFC can avoid most of these by making the right choices now — but must act deliberately to do so.

---

## 2. The Surge: Scalability via Data Availability

### 2.1 What Ethereum Is Doing

| Milestone | Target | Status |
|-----------|--------|--------|
| **EIP-4844 (Proto-Danksharding)** | Blob transactions for rollup data | ✅ Live (Mar 2024) |
| **PeerDAS** | Peer-based Data Availability Sampling | 🚧 Pectra upgrade (2025) |
| **Full Danksharding** | 32 MB/slot blob space, erasure coding | 📋 2026-2027 |

**Why**: Ethereum chose a rollup-centric roadmap — L1 is the DA and settlement layer, execution moves to L2s. Blobs provide cheap data availability; DAS lets light nodes verify data without downloading everything.

**Core technique**: KZG commitments + erasure coding. Validators only sample random chunks; if enough chunks are available, the full data is reconstructable.

### 2.2 QFC Implications

**Problem QFC shares**: AI inference results and model metadata can be large. Full nodes shouldn't need to store everything forever.

**Action items**:
- **Adopt erasure coding for inference proofs from day one**. Instead of storing full inference traces on-chain, store KZG commitments + make the full data available via DAS for a verification window.
- **Design the DA layer to be inference-aware**. Ethereum's blobs are generic; QFC can have typed blob spaces — one for inference proofs, one for model weights, one for agent state — with different retention policies.
- **Narwhal DA integration**: Our DAG consensus already uses Narwhal for data availability. Ensure Narwhal certificates can serve as the basis for DAS, so light clients can verify inference data availability without downloading full blocks.

**Priority**: Medium. Our current design (IPFS for large results, inline for small) is adequate for testnet. DAS matters at scale.

---

## 3. The Scourge: MEV & Validator Centralization

### 3.1 What Ethereum Is Doing

| Proposal | Purpose | Status |
|----------|---------|--------|
| **ePBS (Enshrined PBS)** | Move proposer-builder separation into the protocol | 📋 Research |
| **FOCIL (Fork-Choice Enforced Inclusion Lists)** | Force builders to include certain transactions | 📋 Research |
| **MEV Burn** | Burn MEV revenue instead of giving to proposers | 📋 Research |
| **Execution Tickets / Attester-Proposer Separation** | Decouple block proposal rights from validation | 📋 Research |

**Why**: Ethereum's MEV problem is severe — sophisticated builders extract value from transaction ordering, creating centralization pressure. Today, 90%+ of blocks go through 2-3 builders via MEV-Boost (an off-protocol relay). This is an existential risk to credible neutrality.

### 3.2 QFC Implications

**Problem QFC will face**: In QFC's inference market, "MEV" manifests as:
1. **Task front-running**: Miners see high-reward inference tasks in the mempool and race to claim them
2. **Selective task execution**: Miners cherry-pick profitable tasks, leaving low-reward tasks unserved
3. **Coordinator manipulation**: If the AI Coordinator assigns tasks, whoever controls the coordinator has power

**Action items**:
- **Encrypted task submission**: Inference tasks should be encrypted until assigned to a miner (commit-reveal or threshold encryption). This prevents task front-running — the Ethereum equivalent of encrypted mempools.
- **Fair task distribution in the AI Coordinator**: Don't let miners choose tasks. The coordinator should assign tasks based on miner capability + stake + uptime, with verifiable randomness. This is QFC's equivalent of FOCIL — ensuring all valid tasks get served.
- **Anti-cherry-picking penalty**: Miners who repeatedly decline assigned tasks lose reputation score. Ethereum's inclusion lists force builders to include transactions; QFC should force miners to serve assigned tasks.
- **Revenue smoothing**: Consider a mining pool-like mechanism where inference rewards are pooled and distributed proportionally, reducing the incentive for MEV extraction. This mirrors Ethereum's MEV Burn — neutralizing the value of ordering manipulation.

**Priority**: **High**. This must be designed into the AI Coordinator from v3.0 Phase 1. Retrofitting anti-MEV is exactly the mistake Ethereum made with off-protocol PBS.

---

## 4. The Verge: Stateless Clients & Verkle Trees

### 4.1 What Ethereum Is Doing

| Milestone | Purpose | Status |
|-----------|---------|--------|
| **Verkle Trees** | Replace Merkle-Patricia tries with bandwidth-efficient proofs | 🚧 Active development |
| **Stateless Clients** | Verify blocks without storing full state | 📋 Depends on Verkle |
| **Single-Slot Finality (SSF)** | Finalize in one slot instead of 2 epochs (~13 min) | 📋 Research |

**Why**: Ethereum's Merkle-Patricia trie produces enormous proofs (~4 MB for a single state access). This makes stateless validation impractical. Verkle trees reduce proof sizes to ~150 bytes per access, enabling nodes that verify everything but store nothing.

**The migration problem**: Transitioning from Merkle to Verkle requires converting ~400M state items — one of the hardest upgrades Ethereum has ever attempted.

### 4.2 QFC Implications

**Lesson**: Choose the right state commitment scheme from day one. Migration is brutally expensive.

**Action items**:
- **Use Verkle trees (or better) from genesis**. QFC has no legacy state to migrate. We should launch with a post-Merkle commitment scheme. Options:
  - **Verkle trees** (IPA-based): Well-researched, Ethereum is validating the approach
  - **Binary Merkle trees with STARK proofs**: More ZK-friendly, aligns with our zkML direction
  - **Poseidon-based sparse Merkle trees**: ZK-native hash function, smallest proof size in ZK circuits
- **Design for stateless validation from day one**. Every block should include state witnesses (proofs for all accessed state). This means:
  - Light clients can verify inference results without storing chain state
  - New miners can start validating immediately (no sync required)
  - Mobile wallets can verify proofs directly
- **Single-slot finality is natural for DAG consensus**. Our Mysticeti-variant already achieves fast finality. Ensure we maintain sub-second finality as we scale — this is a competitive advantage over Ethereum's 13-minute finality.

**Priority**: **High** for state tree choice (must decide before mainnet). Medium for full stateless client support.

---

## 5. The Purge: State & History Expiry

### 5.1 What Ethereum Is Doing

| Proposal | Purpose | Status |
|----------|---------|--------|
| **EIP-4444 (History Expiry)** | Nodes stop serving historical blocks >1 year | 📋 Research |
| **State Expiry** | Inactive state "expires" and must be revived with proof | 📋 Research |
| **Protocol simplification** | Remove legacy features (RLP → SSZ, old opcodes) | 🚧 Ongoing |

**Why**: Ethereum's state grows ~50 GB/year. Full nodes already need 1+ TB of storage. Without expiry, running a node becomes increasingly expensive, centralizing the network.

### 5.2 QFC Implications

**Problem QFC will face**: AI-specific data is heavy:
- Inference proofs (even compressed)
- Model registrations and metadata
- Agent state and capability resources
- Historical task results

**Action items**:
- **Define data lifecycle policies at the protocol level**:

  | Data Type | Hot Storage | Warm Storage | Expiry |
  |-----------|-------------|--------------|--------|
  | Inference proofs | 7 days (on-chain) | 90 days (Narwhal DA) | Archive to IPFS/Filecoin |
  | Model registrations | Permanent (while staked) | — | Expire if stake withdrawn |
  | Agent capabilities | Permanent (while active) | — | Expire on `expires_at` |
  | Task results | 30 days | 1 year | Archive |
  | Transaction history | 1 year | Archive | EIP-4444 equivalent |

- **Build state expiry into the QVM Resource model**. Resources already have `expires_at` fields — enforce this at the protocol level so expired resources are automatically pruned.
- **Use SSZ (Simple Serialize) from day one** instead of any custom serialization. Ethereum's RLP → SSZ migration is painful. SSZ is merkleizable, which matters for state proofs.

**Priority**: Medium. Not blocking for testnet, but must be designed before mainnet.

---

## 6. The Splurge: Account Abstraction & EVM Improvements

### 6.1 What Ethereum Is Doing

| Proposal | Purpose | Status |
|----------|---------|--------|
| **EIP-7702** | EOAs can temporarily delegate to contract code | ✅ Pectra (2025) |
| **Native Account Abstraction** | All accounts are smart accounts | 📋 Long-term goal |
| **EOF (EVM Object Format)** | Structured EVM bytecode, versioned | 🚧 Pectra (2025) |

**Why**: Ethereum's account model (EOA vs contract) is a fundamental limitation. EOAs can't have custom validation logic, recovery mechanisms, or gas sponsorship. ERC-4337 is a userspace workaround; the real goal is native AA.

### 6.2 QFC Implications

**Opportunity**: QFC can leapfrog Ethereum's AA journey.

**Action items**:
- **Native Account Abstraction on QVM, ERC-4337 compatibility on EVM**. Our QVM already has Resource-based accounts. Make every QVM account programmable by default:
  - Custom signature validation (Ed25519, secp256k1, WebAuthn/passkeys, multisig)
  - Spending policies as Resources (daily limits, allowlists)
  - Gas sponsorship (paymasters) as a native concept
- **Agent wallets should be native AA accounts**, not ERC-4337 hacks. When an agent is created on QVM, its wallet is automatically a programmable account with capability-based permissions.
- **Adopt EOF for our EVM layer**. Since we control the EVM implementation, we can launch with EOF support from day one, avoiding Ethereum's bytecode compatibility concerns.

**Priority**: High for QVM native AA design. Medium for EOF adoption.

---

## 7. Beam Chain: ZK-Native Consensus Layer

### 7.1 What Ethereum Is Doing

Justin Drake proposed **Beam Chain** (Nov 2024) — a complete rewrite of Ethereum's consensus layer:

| Feature | Current | Beam Chain Target |
|---------|---------|-------------------|
| Slot time | 12 seconds | 4 seconds |
| Finality | 2 epochs (~13 min) | Single-slot (~4 sec) |
| Consensus proof | BLS signatures | ZK-SNARK proof |
| Validator set | ~1M validators | Same, but ZK-compressed |
| Randomness | RANDAO | ZK-verifiable |
| Chain verification | Download all headers | One SNARK proof |

**Why**: A ZK proof of consensus means anyone can verify the entire chain state with a single proof. This enables:
- Instant light client verification
- Trustless cross-chain bridges (verify source chain consensus with a SNARK)
- Mobile/browser nodes that are full verifiers

**Timeline**: 2029-2030 target. This is Ethereum's most ambitious proposal.

### 7.2 QFC Implications

**This is the biggest opportunity for QFC.**

Our DAG consensus (Mysticeti-variant) is simpler than Ethereum's Casper FFG + LMD-GHOST. If we design it to be ZK-provable from the start, we gain:

1. **Trustless cross-chain bridges**: Other chains can verify QFC consensus with a single SNARK. Our Cross-Chain AI Oracle (doc #25) becomes much stronger — the ISM can verify a ZK consensus proof instead of relying on validator multisigs.

2. **Light client verification of inference results**: A mobile app can verify that an inference result was included in a finalized block by checking a ZK proof. No need to trust an RPC provider.

3. **Recursive proofs for inference verification**: ZK consensus proof + zkML inference proof = end-to-end verifiable AI inference, from model execution to chain finality. This is QFC's ultimate value proposition.

**Action items**:
- **Choose ZK-friendly cryptographic primitives for consensus**:
  - Use BLS12-381 for aggregate signatures (same as Ethereum — well-supported in ZK circuits)
  - Use Poseidon hash where possible (10-100x cheaper in ZK circuits vs SHA-256/Keccak)
  - Avoid secp256k1 in consensus (expensive in ZK; keep it only for EVM compatibility)
- **Design DAG certificate structure to be SNARK-provable**. Each Narwhal certificate should be expressible as a ZK circuit. This means:
  - Fixed-size validator sets per epoch (easier to prove)
  - Deterministic leader election (provable)
  - Structured data formats (SSZ, not arbitrary encoding)
- **Phase this into v3.0 roadmap as a research track**. Full ZK consensus is 6-12 months of work, but the cryptographic primitive choices must be made in Phase 1.

**Priority**: **Critical** for primitive choices (Phase 1). Medium for full ZK consensus implementation (Phase 4+).

---

## 8. Summary: Ethereum's Mistakes We Can Avoid

| Ethereum Mistake | Cost of Retrofit | QFC Approach |
|-----------------|------------------|--------------|
| Merkle-Patricia tries → Verkle trees | 2+ years of migration work | Launch with ZK-friendly state tree |
| EOA/Contract account split → Native AA | 5+ years (ERC-4337 → EIP-7702 → Native AA) | QVM accounts are programmable from genesis |
| Off-protocol PBS (MEV-Boost) → ePBS | Builder centralization crisis | Encrypted tasks + fair assignment in AI Coordinator |
| RLP → SSZ serialization | Multi-year, still incomplete | Use SSZ from day one |
| Unbounded state growth → State expiry | Requires backward-compatible expiry scheme | Resource `expires_at` + protocol-level pruning |
| BFT-unfriendly consensus → Beam Chain rewrite | Complete consensus layer rewrite | Design DAG consensus to be ZK-provable |
| No data availability sampling → DAS | Multi-year rollout (4844 → PeerDAS → Full Danksharding) | Narwhal DA + erasure coding from genesis |

---

## 9. Recommended Additions to v3.0 Roadmap

Based on this analysis, three items should be added to the v3.0 roadmap:

### 9.1 Encrypted Task Submission (Phase 1 — AI Coordinator)

**Effort**: 1-2 weeks with Claude Code
**What**: Inference tasks encrypted until assigned. Prevents MEV-style front-running.
**Technique**: Threshold encryption with validator committee, or simpler commit-reveal scheme.

### 9.2 ZK-Friendly Cryptographic Primitives (Phase 1 — Consensus)

**Effort**: 1 week (research + decision) + 2-3 weeks (implementation)
**What**: Audit all consensus cryptographic choices. Replace ZK-unfriendly primitives (if any) before mainnet. Ensure BLS12-381 for consensus signatures, Poseidon for internal hashing.
**Why now**: Changing crypto primitives after mainnet is nearly impossible.

### 9.3 State Lifecycle & Expiry Framework (Phase 2 — QVM)

**Effort**: 2-3 weeks with Claude Code
**What**: Protocol-level data lifecycle policies. Resources auto-expire. Historical data tiered to archival storage.
**Why**: Prevents state bloat from day one. Much cheaper than retrofitting expiry later.

---

## 10. Conclusion

Ethereum's 2030 roadmap is essentially a decade-long migration from a 2015 architecture to a 2030 architecture. Every major track — Surge, Scourge, Verge, Purge, Splurge, Beam Chain — is fixing a design decision that seemed reasonable in 2015 but doesn't scale.

QFC's advantage is simple: **we haven't launched mainnet yet**. We can build the target state directly. The cost of making the right choices now is measured in weeks; the cost of retrofitting later is measured in years.

The three highest-leverage decisions:
1. **ZK-friendly primitives in consensus** (cannot change post-mainnet)
2. **Anti-MEV in the AI Coordinator** (centralization risk if deferred)
3. **State expiry in the Resource model** (exponentially harder to add later)

---

## References

- [Ethereum Roadmap - Vitalik Buterin](https://ethereum.org/en/roadmap/)
- [The Surge - Danksharding FAQ](https://notes.ethereum.org/@dankrad/new_sharding)
- [EIP-4844: Proto-Danksharding](https://eips.ethereum.org/EIPS/eip-4844)
- [PeerDAS Specification](https://ethereum.github.io/consensus-specs/specs/fulu/das-core/)
- [Endgame - Vitalik Buterin](https://vitalik.eth.limo/general/2021/12/06/endgame.html)
- [ePBS - Ethereum Research](https://ethresear.ch/t/why-enshrine-proposer-builder-separation/15710)
- [FOCIL - Fork Choice Enforced Inclusion Lists](https://ethresear.ch/t/fork-choice-enforced-inclusion-lists-focil/19870)
- [Verkle Trees - Ethereum Foundation](https://verkle.info/)
- [Beam Chain Proposal - Justin Drake (Devcon 2024)](https://www.youtube.com/watch?v=Gjucp1Xtlvg)
- [EIP-7702: Set EOA Account Code](https://eips.ethereum.org/EIPS/eip-7702)
- [EOF - EVM Object Format](https://evmobjectformat.org/)
- [SSZ Specification](https://ethereum.github.io/consensus-specs/ssz/simple-serialize/)
- [State Expiry - Ethereum Research](https://notes.ethereum.org/@vbuterin/state_expiry_eip)
