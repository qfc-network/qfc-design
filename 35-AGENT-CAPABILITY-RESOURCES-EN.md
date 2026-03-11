# Agent Capability Resources (QVM)

> Last Updated: 2026-03-11 | Version 1.0
> GitHub Issue: #19
> Author: Alex Wei, Product Manager @ QFC Network

---

## 1. Executive Summary

This document specifies the QVM (QuantumScript VM) resource types that enforce AI agent capabilities at the VM level. Unlike EVM contract-level permissions (which can have bugs), QVM resources are **Move-style linear types** — they cannot be forged, duplicated, or spent beyond their limits by construction.

Two core resources:
- **InferenceCapability** — right to spend a budget on AI inference tasks
- **AgentRegistration** — agent identity, discovery metadata, and stake

Together they enable capability-gated inference, agent discovery, and kill switches — all enforced at the VM level.

---

## 2. Resource Type Definitions

### 2.1 InferenceCapability

```move
module qfc::inference_capability {

    // ─── Error Codes ───
    const E_INSUFFICIENT_BUDGET: u64 = 100;
    const E_MODEL_NOT_ALLOWED: u64 = 101;
    const E_CAPABILITY_EXPIRED: u64 = 102;
    const E_CAPABILITY_FROZEN: u64 = 103;
    const E_NOT_OWNER: u64 = 104;
    const E_ZERO_BUDGET: u64 = 105;

    // ─── Events ───
    struct CapabilityCreated has copy, drop {
        capability_id: UID,
        owner: address,
        budget: u64,
        allowed_models: vector<ModelId>,
        expires_at: u64,
    }

    struct CapabilityUsed has copy, drop {
        capability_id: UID,
        model_id: ModelId,
        fee: u64,
        remaining_budget: u64,
    }

    struct CapabilityFrozen has copy, drop {
        capability_id: UID,
        frozen_by: address,
    }

    struct CapabilityDestroyed has copy, drop {
        capability_id: UID,
        remaining_budget: u64,  // Refunded to owner
    }

    struct CapabilityToppedUp has copy, drop {
        capability_id: UID,
        added: u64,
        new_budget: u64,
    }

    // ─── Core Resource ───
    resource InferenceCapability {
        id: UID,
        owner: address,
        remaining_budget: u64,
        allowed_models: vector<ModelId>,
        expires_at: u64,            // Unix timestamp, 0 = no expiry
        frozen: bool,
        total_spent: u64,           // Lifetime counter
        total_tasks: u64,           // Lifetime task count
        created_at: u64,
    }
}
```

### 2.2 AgentRegistration

```move
module qfc::agent_registry {

    // ─── Error Codes ───
    const E_INSUFFICIENT_STAKE: u64 = 200;
    const E_NOT_OWNER: u64 = 201;
    const E_AGENT_FROZEN: u64 = 202;
    const E_ALREADY_REGISTERED: u64 = 203;
    const E_INVALID_ENDPOINT: u64 = 204;
    const E_COOLDOWN_NOT_ELAPSED: u64 = 205;
    const E_BELOW_MIN_STAKE: u64 = 206;

    // ─── Events ───
    struct AgentRegistered has copy, drop {
        agent_id: UID,
        owner: address,
        capabilities: vector<String>,
        stake: u64,
    }

    struct AgentUpdated has copy, drop {
        agent_id: UID,
        field: String,  // "endpoint", "capabilities", "protocol_digests"
    }

    struct AgentFrozen has copy, drop {
        agent_id: UID,
        frozen_by: address,
        reason: String,
    }

    struct AgentUnfrozen has copy, drop {
        agent_id: UID,
        unfrozen_by: address,
    }

    struct AgentRevoked has copy, drop {
        agent_id: UID,
        stake_returned: u64,
        stake_slashed: u64,
    }

    struct AgentSlashed has copy, drop {
        agent_id: UID,
        amount: u64,
        reason: String,
    }

    // ─── Core Resource ───
    resource AgentRegistration {
        id: UID,
        owner: address,
        protocol_digests: vector<Hash>,    // Protocols this agent supports
        capabilities: vector<String>,       // "text-generation", "image-analysis", etc.
        endpoint: String,                   // How to reach this agent off-chain
        stake: u64,                         // Skin-in-the-game (minimum required)
        frozen: bool,
        reputation_score: u64,              // 0-10000 (basis points)
        total_tasks_completed: u64,
        total_tasks_failed: u64,
        last_heartbeat: u64,                // Unix timestamp
        created_at: u64,
    }
}
```

---

## 3. Module Functions

### 3.1 InferenceCapability Functions

```move
/// Create a new inference capability
public fun create(
    owner: &signer,
    budget: Coin<QFC>,
    allowed_models: vector<ModelId>,
    expires_at: u64,
): InferenceCapability {
    assert!(coin::value(&budget) > 0, E_ZERO_BUDGET);

    let cap = InferenceCapability {
        id: new_uid(),
        owner: signer::address_of(owner),
        remaining_budget: coin::value(&budget),
        allowed_models,
        expires_at,
        frozen: false,
        total_spent: 0,
        total_tasks: 0,
        created_at: timestamp::now(),
    };

    // Deposit budget into escrow
    escrow::deposit(cap.id, budget);

    event::emit(CapabilityCreated { ... });
    cap
}

/// Use capability to pay for inference (called by AI Coordinator)
public fun use_for_inference(
    cap: &mut InferenceCapability,
    model_id: ModelId,
    fee: u64,
): bool {
    assert!(!cap.frozen, E_CAPABILITY_FROZEN);
    assert!(cap.expires_at == 0 || timestamp::now() < cap.expires_at, E_CAPABILITY_EXPIRED);
    assert!(vector::contains(&cap.allowed_models, &model_id), E_MODEL_NOT_ALLOWED);
    assert!(cap.remaining_budget >= fee, E_INSUFFICIENT_BUDGET);

    cap.remaining_budget = cap.remaining_budget - fee;
    cap.total_spent = cap.total_spent + fee;
    cap.total_tasks = cap.total_tasks + 1;

    event::emit(CapabilityUsed { ... });
    true
}

/// Top up budget
public fun top_up(
    cap: &mut InferenceCapability,
    owner: &signer,
    additional: Coin<QFC>,
) {
    assert!(signer::address_of(owner) == cap.owner, E_NOT_OWNER);
    let amount = coin::value(&additional);
    cap.remaining_budget = cap.remaining_budget + amount;
    escrow::deposit(cap.id, additional);
    event::emit(CapabilityToppedUp { ... });
}

/// Freeze capability (owner or governance)
public fun freeze(
    cap: &mut InferenceCapability,
    caller: &signer,
) {
    let addr = signer::address_of(caller);
    assert!(addr == cap.owner || governance::is_authorized(addr), E_NOT_OWNER);
    cap.frozen = true;
    event::emit(CapabilityFrozen { ... });
}

/// Unfreeze (owner or governance)
public fun unfreeze(
    cap: &mut InferenceCapability,
    caller: &signer,
) {
    let addr = signer::address_of(caller);
    assert!(addr == cap.owner || governance::is_authorized(addr), E_NOT_OWNER);
    cap.frozen = false;
}

/// Destroy capability and refund remaining budget
public fun destroy(
    cap: InferenceCapability,
    owner: &signer,
): Coin<QFC> {
    assert!(signer::address_of(owner) == cap.owner, E_NOT_OWNER);
    let refund = escrow::withdraw(cap.id, cap.remaining_budget);
    event::emit(CapabilityDestroyed { ... });
    // Resource is consumed (destroyed) by Move semantics
    let InferenceCapability { id, .. } = cap;
    uid::delete(id);
    refund
}
```

### 3.2 AgentRegistration Functions

```move
/// Minimum stake tiers
const MIN_STAKE_BASIC: u64 = 100_000_000;      // 100 QFC (8 decimals)
const MIN_STAKE_VERIFIED: u64 = 1_000_000_000;  // 1,000 QFC
const MIN_STAKE_PREMIUM: u64 = 10_000_000_000;  // 10,000 QFC
const UNSTAKE_COOLDOWN: u64 = 7 * 24 * 3600;    // 7 days

/// Register a new agent
public fun register(
    owner: &signer,
    stake: Coin<QFC>,
    capabilities: vector<String>,
    endpoint: String,
    protocol_digests: vector<Hash>,
): AgentRegistration {
    assert!(coin::value(&stake) >= MIN_STAKE_BASIC, E_INSUFFICIENT_STAKE);
    assert!(string::length(&endpoint) > 0, E_INVALID_ENDPOINT);

    let agent = AgentRegistration {
        id: new_uid(),
        owner: signer::address_of(owner),
        protocol_digests,
        capabilities,
        endpoint,
        stake: coin::value(&stake),
        frozen: false,
        reputation_score: 5000,  // Start at 50%
        total_tasks_completed: 0,
        total_tasks_failed: 0,
        last_heartbeat: timestamp::now(),
        created_at: timestamp::now(),
    };

    staking::deposit(agent.id, stake);
    event::emit(AgentRegistered { ... });
    agent
}

/// Update endpoint
public fun update_endpoint(
    agent: &mut AgentRegistration,
    caller: &signer,
    new_endpoint: String,
) {
    assert!(signer::address_of(caller) == agent.owner, E_NOT_OWNER);
    assert!(!agent.frozen, E_AGENT_FROZEN);
    agent.endpoint = new_endpoint;
    event::emit(AgentUpdated { agent_id: agent.id, field: string::utf8(b"endpoint") });
}

/// Update capabilities
public fun update_capabilities(
    agent: &mut AgentRegistration,
    caller: &signer,
    new_capabilities: vector<String>,
) {
    assert!(signer::address_of(caller) == agent.owner, E_NOT_OWNER);
    assert!(!agent.frozen, E_AGENT_FROZEN);
    agent.capabilities = new_capabilities;
    event::emit(AgentUpdated { agent_id: agent.id, field: string::utf8(b"capabilities") });
}

/// Freeze agent (owner or governance)
public fun freeze(
    agent: &mut AgentRegistration,
    caller: &signer,
    reason: String,
) {
    let addr = signer::address_of(caller);
    assert!(addr == agent.owner || governance::is_authorized(addr), E_NOT_OWNER);
    agent.frozen = true;
    event::emit(AgentFrozen { agent_id: agent.id, frozen_by: addr, reason });
}

/// Unfreeze (governance only for safety)
public fun unfreeze(
    agent: &mut AgentRegistration,
    caller: &signer,
) {
    assert!(governance::is_authorized(signer::address_of(caller)), E_NOT_OWNER);
    agent.frozen = false;
    event::emit(AgentUnfrozen { ... });
}

/// Slash stake (called by verification system on misbehavior)
public fun slash(
    agent: &mut AgentRegistration,
    amount: u64,
    reason: String,
) {
    // Only callable by AI Coordinator module
    let slash_amount = if (amount > agent.stake) { agent.stake } else { amount };
    agent.stake = agent.stake - slash_amount;
    staking::slash(agent.id, slash_amount);
    agent.reputation_score = if (agent.reputation_score >= 500) {
        agent.reputation_score - 500
    } else { 0 };
    event::emit(AgentSlashed { agent_id: agent.id, amount: slash_amount, reason });
}

/// Revoke agent and reclaim stake (after cooldown)
public fun revoke(
    agent: AgentRegistration,
    owner: &signer,
): Coin<QFC> {
    assert!(signer::address_of(owner) == agent.owner, E_NOT_OWNER);
    // Cooldown check handled by staking module
    let stake_returned = staking::withdraw(agent.id, agent.stake);
    event::emit(AgentRevoked { ... });
    let AgentRegistration { id, .. } = agent;
    uid::delete(id);
    stake_returned
}

/// Heartbeat (agent signals it's alive)
public fun heartbeat(
    agent: &mut AgentRegistration,
    caller: &signer,
) {
    assert!(signer::address_of(caller) == agent.owner, E_NOT_OWNER);
    agent.last_heartbeat = timestamp::now();
}

/// Record task completion (called by AI Coordinator)
public fun record_task_result(
    agent: &mut AgentRegistration,
    success: bool,
) {
    if (success) {
        agent.total_tasks_completed = agent.total_tasks_completed + 1;
        // Increase reputation (capped at 10000)
        agent.reputation_score = min(agent.reputation_score + 10, 10000);
    } else {
        agent.total_tasks_failed = agent.total_tasks_failed + 1;
        agent.reputation_score = if (agent.reputation_score >= 50) {
            agent.reputation_score - 50
        } else { 0 };
    }
}
```

---

## 4. Capability-Gated Inference Flow

```
User / Agent Runtime
    │
    ├─1─► Submit inference request with capability_id
    │
AI Coordinator (qfc-ai-coordinator)
    │
    ├─2─► Load InferenceCapability resource from QVM state
    │     ├── Check: !frozen
    │     ├── Check: not expired
    │     ├── Check: model_id in allowed_models
    │     └── Check: remaining_budget >= estimated_fee
    │
    ├─3─► Load AgentRegistration (if agent-submitted)
    │     ├── Check: !frozen
    │     └── Check: reputation_score >= min_threshold
    │
    ├─4─► Assign task to miner (existing TaskPool flow)
    │
Miner
    ├─5─► Execute inference → submit result + proof
    │
AI Coordinator
    ├─6─► Verify result (spot-check / zkML)
    │
    ├─7─► Call use_for_inference(cap, model_id, actual_fee)
    │     └── Deducts from capability budget atomically
    │
    ├─8─► Call record_task_result(agent, success)
    │     └── Updates reputation score
    │
    └─9─► Return result to caller
```

**Key guarantee**: Step 7 is atomic. If the capability doesn't have enough budget, the entire transaction reverts — the miner doesn't execute unpaid work because the budget check happens in step 2 before assignment.

---

## 5. Kill Switch Mechanism

### 5.1 Freeze vs Destroy

| Action | Effect | Reversible | Who Can Trigger |
|--------|--------|------------|-----------------|
| **Freeze** | Agent/capability cannot be used; funds locked | Yes (unfreeze) | Owner, Governance |
| **Destroy** | Agent/capability permanently removed; stake/budget refunded | No | Owner only |

### 5.2 Emergency Scenarios

| Scenario | Action | Trigger |
|----------|--------|---------|
| Compromised session key | Revoke session key + freeze agent | Owner |
| Agent misbehavior detected | Freeze agent + slash stake | Governance / AI Coordinator |
| Owner key compromised | Governance freeze (via validator vote) | Governance multisig |
| Network-wide attack | Governance freezes all agents | Emergency governance action |

### 5.3 Governance Freeze Process

1. Any validator can propose an emergency freeze
2. Requires >2/3 validator vote within 1 hour
3. Frozen agent cannot execute any operations
4. Unfreeze requires separate governance vote (>2/3)
5. Owner cannot unfreeze a governance-frozen agent

---

## 6. Discovery API

### 6.1 RPC Endpoints

#### `qfc_listAgents`

```json
// Request
{
    "jsonrpc": "2.0",
    "method": "qfc_listAgents",
    "params": {
        "status": "active",    // "active" | "frozen" | "all"
        "limit": 20,
        "offset": 0,
        "sort_by": "reputation_score",  // "reputation_score" | "stake" | "created_at"
        "sort_order": "desc"
    }
}

// Response
{
    "agents": [
        {
            "agent_id": "0xabc...",
            "owner": "0x123...",
            "capabilities": ["text-generation", "image-analysis"],
            "endpoint": "https://agent.example.com",
            "stake": "1000000000",
            "frozen": false,
            "reputation_score": 8500,
            "total_tasks_completed": 1234,
            "last_heartbeat": 1741651200
        }
    ],
    "total": 150,
    "has_more": true
}
```

#### `qfc_queryAgentsByCapability`

```json
// Request
{
    "jsonrpc": "2.0",
    "method": "qfc_queryAgentsByCapability",
    "params": {
        "capability": "text-generation",
        "min_reputation": 5000,
        "min_stake": "1000000000",
        "limit": 10
    }
}
```

#### `qfc_queryAgentsByProtocolDigest`

```json
// Request
{
    "jsonrpc": "2.0",
    "method": "qfc_queryAgentsByProtocolDigest",
    "params": {
        "protocol_digest": "0xdef..."
    }
}
```

#### `qfc_getAgentDetails`

```json
// Request
{
    "jsonrpc": "2.0",
    "method": "qfc_getAgentDetails",
    "params": {
        "agent_id": "0xabc..."
    }
}

// Response
{
    "agent_id": "0xabc...",
    "owner": "0x123...",
    "protocol_digests": ["0xdef..."],
    "capabilities": ["text-generation"],
    "endpoint": "https://agent.example.com",
    "stake": "1000000000",
    "frozen": false,
    "reputation_score": 8500,
    "total_tasks_completed": 1234,
    "total_tasks_failed": 12,
    "last_heartbeat": 1741651200,
    "created_at": 1740000000,
    "inference_capabilities": [
        {
            "id": "0xcap...",
            "remaining_budget": "500000000",
            "allowed_models": ["qfc-llm-7b", "qfc-embed-small"],
            "expires_at": 1742256000,
            "total_spent": "250000000",
            "total_tasks": 567
        }
    ],
    "session_keys": [
        {
            "public_key": "0xkey...",
            "permissions": 3,
            "spending_limit": "100000000",
            "expires_at": 1741737600
        }
    ]
}
```

### 6.2 Rust Registry Index

```rust
// qfc-core/crates/qfc-qvm/src/agent_index.rs

/// In-memory index for fast agent discovery
pub struct AgentIndex {
    /// capability -> sorted vec of (reputation, agent_id)
    by_capability: HashMap<String, BTreeSet<(u64, AgentId)>>,
    /// protocol_digest -> set of agent_ids
    by_protocol: HashMap<Hash, HashSet<AgentId>>,
    /// All agents by ID
    agents: HashMap<AgentId, AgentRegistrationView>,
}

impl AgentIndex {
    /// Rebuild from QVM state (on node startup)
    pub fn rebuild_from_state(state: &QvmState) -> Self { ... }

    /// Incremental update on new block
    pub fn apply_events(&mut self, events: &[AgentEvent]) { ... }

    /// Query by capability with filters
    pub fn query_by_capability(
        &self,
        capability: &str,
        min_reputation: u64,
        min_stake: u64,
        limit: usize,
    ) -> Vec<&AgentRegistrationView> { ... }
}
```

---

## 7. Staking Economics

### 7.1 Stake Tiers

| Tier | Minimum Stake | Benefits |
|------|--------------|----------|
| **Basic** | 100 QFC | Can register, limited to 10 tasks/day |
| **Verified** | 1,000 QFC | Unlimited tasks, lower spot-check rate |
| **Premium** | 10,000 QFC | Priority task assignment, featured in discovery |

### 7.2 Slashing Conditions

| Violation | Slash Amount | Reputation Impact |
|-----------|-------------|-------------------|
| Failed verification (bad inference result) | 1% of stake | -50 points |
| Timeout (accepted task, no result) | 0.5% of stake | -25 points |
| Consecutive failures (3+) | 5% of stake | -500 points + auto-freeze |
| Governance-determined misconduct | Up to 100% | Set to 0 + permanent freeze |

### 7.3 Unstaking Process

1. Owner calls `revoke(agent)`
2. Stake enters **cooldown period** (7 days)
3. During cooldown: agent is frozen, stake is locked, any pending slashing is applied
4. After cooldown: remaining stake is returned to owner
5. Resource is destroyed (Move semantics)

### 7.4 Reputation Scoring

```
reputation_score: u64  // 0 - 10000 (basis points)

Starting score:     5000 (50%)
Per success:        +10
Per failure:        -50
Per slash:          -500
Maximum:            10000
Minimum:            0

Benefits of high reputation:
- reputation >= 8000: spot-check rate reduced from 10% to 5%
- reputation >= 9000: eligible for premium task assignment
- reputation < 2000: restricted to Basic tier regardless of stake
```

---

## 8. Security Analysis

### 8.1 QVM vs EVM Comparison

| Property | EVM (Contract-level) | QVM (Resource-level) |
|----------|---------------------|---------------------|
| Budget enforcement | `require(balance >= fee)` — can have reentrancy bugs | Resource arithmetic — VM prevents underflow |
| Capability forgery | Possible via contract bugs | Impossible — resources are linear types |
| Duplication | Possible via reentrancy | Impossible — Move prevents copy |
| Kill switch | Admin function (can be bypassed) | Resource freeze (VM-enforced) |
| Overflow/Underflow | Solidity 0.8+ checks, but older contracts vulnerable | VM-level bounds checking |

### 8.2 Attack Vectors & Mitigations

| Attack | Vector | Mitigation |
|--------|--------|------------|
| **Sybil registration** | Register many cheap agents | Minimum stake + QIB benchmark |
| **Capability drain** | Rapid small tasks to drain budget | Per-period spending limits + rate limiting |
| **Stale agent** | Register and never run tasks | Heartbeat requirement; agents inactive >24h deprioritized |
| **Reputation farming** | Complete easy tasks to inflate score | Weighted scoring by task difficulty |
| **Front-running** | Intercept task assignment | Task assignment is validator-internal, not in mempool |

---

## 9. Integration with EVM Layer

### 9.1 Cross-VM Architecture

```
EVM Layer                           QVM Layer
┌────────────────────┐              ┌─────────────────────┐
│ AgentTokenFactory  │◄── bridge ──►│ AgentRegistration    │
│ (ERC-20 tokens)    │              │ (Resource)           │
│                    │              │                      │
│ RevenueDistributor │              │ InferenceCapability  │
│ (60/30/10 split)   │              │ (Resource)           │
│                    │              │                      │
│ QFCAgentAccount    │              │ SessionKey           │
│ (ERC-4337 wallet)  │              │ (Resource)           │
└────────────────────┘              └─────────────────────┘
         │                                    │
         └──────── Cross-VM Message Bus ──────┘
```

### 9.2 Bridge Contract

```solidity
interface IAgentBridge {
    /// Called by QVM when an agent is registered
    function onAgentRegistered(bytes32 agentId, address owner, uint256 stake) external;

    /// Called by QVM when an agent earns revenue
    function distributeRevenue(bytes32 agentId, uint256 amount) external;

    /// Query agent status from EVM side
    function isAgentActive(bytes32 agentId) external view returns (bool);
}
```

---

## 10. Testing Strategy

### 10.1 Unit Tests

| Module | Test Count | Key Scenarios |
|--------|-----------|---------------|
| `inference_capability` | ~25 | Create, use, top-up, freeze, destroy, expiry, model allowlist |
| `agent_registry` | ~30 | Register, update, freeze, slash, revoke, heartbeat, reputation |
| `agent_index` | ~15 | Query by capability, by protocol, rebuild from state |
| `session_keys` | ~20 | Issue, validate, rotate, revoke, TTL, nonce, permissions |

### 10.2 Integration Tests

| Scenario | Components |
|----------|-----------|
| Full inference with capability | Capability + AI Coordinator + Miner |
| Agent registration → task execution → reputation update | Registry + Coordinator + Capability |
| Slash on bad result → reputation drop → auto-freeze | Registry + Verification + Slash |
| Cross-VM: register agent → create EVM token | Registry + Bridge + TokenFactory |
| Discovery: register 100 agents → query by capability | Registry + Index + RPC |

### 10.3 Adversarial Tests

- Attempt to use frozen capability → must fail
- Attempt to use expired capability → must fail
- Attempt to overspend budget → must fail
- Attempt to use model not in allowlist → must fail
- Concurrent task submissions exceeding budget → only valid ones succeed
- Sybil: register 100 agents from same owner → stake requirements hold

---

## 11. Migration Path from v2.0

### Phase 1: Additive (Week 1-2)
- Deploy `inference_capability` and `agent_registry` modules to QVM
- Existing inference flow continues unchanged
- New capability-gated path available as opt-in

### Phase 2: Soft Migration (Week 3-4)
- SDK updated to prefer capability-gated path
- Existing direct inference still works but deprecated
- Discovery API enabled

### Phase 3: Enforcement (Week 5+)
- All inference requests require InferenceCapability
- Legacy path removed
- Full agent registry with staking required

**Backwards compatibility**: During Phase 1-2, a "default capability" with unlimited budget is auto-created for existing users, preserving the v2.0 behavior.

---

## References

- [24-AI-AGENT-FRAMEWORK.md](./24-AI-AGENT-FRAMEWORK-EN.md) — Research basis
- [28-V3-ROADMAP.md](./28-V3-ROADMAP-EN.md) — v3.0 overall roadmap, Phase 3.2
- [Move Language Documentation](https://move-language.github.io/move/)
- [Sui Object Model](https://docs.sui.io/concepts/object-model)
