# AI-Native Agent Wallet Roadmap (Execution Plan)

> Last Updated: 2026-03-11 | Version 1.0
> GitHub Issue: #34
> Author: Alex Wei, Product Manager @ QFC Network

---

## 1. Executive Summary

This document is the execution plan for turning QFC's AI-native agent wallet from partial v2.0 implementation into a production-ready capability. The work spans four repos (qfc-core, qfc-contracts, qfc-explorer, qfc-openclaw-skill) and is structured into four milestones:

| Milestone | Priority | Goal |
|-----------|----------|------|
| **M1** | P0 | Agent lifecycle write APIs + session-key enforcement + e2e tests |
| **M2** | P1 | Gas sponsorship / paymaster flow for agent actions |
| **M3** | P1 | Explorer control / visibility upgrades |
| **M4** | P2 | OpenClaw native integration + docs + demos |

**Definition of Done**: An AI agent can be registered, funded, and revoked with on-chain enforcement. Session keys enforce TTL, permissions, and spending limits. The explorer exposes operator-grade visibility. OpenClaw can execute agent actions without a long-lived owner key.

---

## 2. Current State Assessment

### What exists in v2.0

| Component | Status | Location |
|-----------|--------|----------|
| AI Coordinator (task pool → miner → verify → settle) | ✅ Working | `qfc-core/crates/qfc-ai-coordinator` |
| Inference proof verification (spot-check) | ✅ Working | `qfc-core/crates/qfc-inference` |
| QVM with Move-style resources | ✅ Working | `qfc-core/crates/qfc-qvm` |
| EVM (revm) with ERC-4337 EntryPoint | ✅ Partial | `qfc-core/crates/qfc-executor` |
| OpenClaw inference skill | ✅ Working | `qfc-openclaw-skill` |
| Explorer with tx/block views | ✅ Working | `qfc-explorer` |

### What's missing

| Gap | Impact |
|-----|--------|
| No `AgentRegistration` resource in QVM | Cannot register agents on-chain |
| No session-key module | Agents must use owner key for every action |
| No ERC-4337 agent wallet contract | No programmable security policies |
| No paymaster contract | Agents must hold QFC for gas |
| No agent views in explorer | Operators cannot monitor agent activity |
| OpenClaw has no agent wallet commands | Cannot manage agents from OpenClaw |

---

## 3. Milestone M1: Agent Lifecycle + Session Keys (P0)

### 3.1 QVM Agent Registration Resource

```move
module qfc::agent_registry {

    /// Error codes
    const E_INSUFFICIENT_STAKE: u64 = 1;
    const E_NOT_OWNER: u64 = 2;
    const E_ALREADY_FROZEN: u64 = 3;
    const E_AGENT_FROZEN: u64 = 4;
    const E_INVALID_ENDPOINT: u64 = 5;

    /// Events
    struct AgentRegistered has copy, drop {
        agent_id: UID,
        owner: address,
        stake: u64,
    }

    struct AgentRevoked has copy, drop {
        agent_id: UID,
        owner: address,
    }

    /// Core resource
    resource AgentRegistration {
        id: UID,
        owner: address,
        protocol_digests: vector<Hash>,
        capabilities: vector<String>,
        endpoint: String,
        stake: u64,
        frozen: bool,
        created_at: u64,
    }

    /// Register a new agent (requires minimum stake)
    public fun register(
        owner: &signer,
        stake: Coin<QFC>,
        capabilities: vector<String>,
        endpoint: String,
    ): AgentRegistration { ... }

    /// Revoke and reclaim stake (after cooldown)
    public fun revoke(agent: AgentRegistration): Coin<QFC> { ... }

    /// Freeze agent (owner or governance)
    public fun freeze(agent: &mut AgentRegistration, caller: &signer) { ... }

    /// Update endpoint
    public fun update_endpoint(
        agent: &mut AgentRegistration,
        caller: &signer,
        new_endpoint: String,
    ) { ... }
}
```

### 3.2 Session Key Module

```move
module qfc::session_keys {

    /// Permission bitmask
    const PERM_INFERENCE: u64    = 0x01;  // Submit inference tasks
    const PERM_TRANSFER: u64    = 0x02;  // Transfer tokens
    const PERM_STAKE: u64       = 0x04;  // Stake/unstake
    const PERM_REGISTER: u64   = 0x08;  // Register sub-agents

    resource SessionKey {
        id: UID,
        agent_id: UID,
        public_key: vector<u8>,
        permissions: u64,           // Bitmask
        spending_limit: u64,        // Max spend per period
        spent_this_period: u64,
        period_start: u64,
        period_duration: u64,       // e.g., 86400 for daily
        expires_at: u64,            // Absolute TTL
        nonce: u64,                 // Replay protection
    }

    /// Issue a new session key
    public fun issue(
        agent: &AgentRegistration,
        owner: &signer,
        public_key: vector<u8>,
        permissions: u64,
        spending_limit: u64,
        period_duration: u64,
        ttl: u64,
    ): SessionKey { ... }

    /// Validate a session key for an operation
    public fun validate(
        key: &mut SessionKey,
        operation: u64,     // Permission bit
        amount: u64,        // Spend amount
        provided_nonce: u64,
    ): bool { ... }

    /// Rotate: revoke old, issue new
    public fun rotate(
        old_key: SessionKey,
        owner: &signer,
        new_public_key: vector<u8>,
    ): SessionKey { ... }

    /// Revoke (destroy resource)
    public fun revoke(key: SessionKey, caller: &signer) { ... }
}
```

### 3.3 EVM Agent Account Contract

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@account-abstraction/contracts/interfaces/IAccount.sol";
import "@openzeppelin/contracts/proxy/utils/UUPSUpgradeable.sol";

contract QFCAgentAccount is IAccount, UUPSUpgradeable {
    address public owner;
    address public entryPoint;

    // Session keys
    mapping(address => SessionKeyData) public sessionKeys;

    struct SessionKeyData {
        uint64 permissions;
        uint256 spendingLimit;
        uint256 spentThisPeriod;
        uint64 periodStart;
        uint64 periodDuration;
        uint64 expiresAt;
        uint64 nonce;
        bool active;
    }

    // Spending limits
    uint256 public perTxLimit;
    uint256 public perPeriodLimit;

    // Contract allowlist
    mapping(address => bool) public allowedContracts;

    function validateUserOp(
        PackedUserOperation calldata userOp,
        bytes32 userOpHash,
        uint256 missingAccountFunds
    ) external override returns (uint256 validationData) {
        // 1. Check if signer is owner or valid session key
        // 2. Enforce spending limits
        // 3. Check contract allowlist
        // 4. Return SIG_VALIDATION_SUCCESS or SIG_VALIDATION_FAILED
    }

    function execute(address dest, uint256 value, bytes calldata data) external {
        require(msg.sender == entryPoint || msg.sender == owner);
        require(allowedContracts[dest] || dest == address(0), "Not allowed");
        require(value <= perTxLimit, "Exceeds per-tx limit");
        (bool success,) = dest.call{value: value}(data);
        require(success);
    }

    // Session key management (owner only)
    function addSessionKey(address key, SessionKeyData calldata data) external;
    function removeSessionKey(address key) external;

    // Policy management (owner only)
    function setPerTxLimit(uint256 limit) external;
    function setPerPeriodLimit(uint256 limit) external;
    function addAllowedContract(address contract_) external;
    function removeAllowedContract(address contract_) external;
}
```

### 3.4 JSON-RPC API Endpoints

| Method | Params | Returns |
|--------|--------|---------|
| `qfc_registerAgent` | `{owner, stake, capabilities, endpoint}` | `{agent_id, tx_hash}` |
| `qfc_revokeAgent` | `{agent_id, owner_sig}` | `{tx_hash, stake_returned}` |
| `qfc_freezeAgent` | `{agent_id, caller_sig}` | `{tx_hash}` |
| `qfc_getAgent` | `{agent_id}` | `AgentRegistration` |
| `qfc_listAgents` | `{capability?, limit, offset}` | `AgentRegistration[]` |
| `qfc_issueSessionKey` | `{agent_id, pubkey, permissions, limit, ttl}` | `{session_key_id, tx_hash}` |
| `qfc_revokeSessionKey` | `{session_key_id, owner_sig}` | `{tx_hash}` |
| `qfc_getSessionKeys` | `{agent_id}` | `SessionKey[]` |
| `qfc_fundAgent` | `{agent_id, amount}` | `{tx_hash}` |
| `qfc_getAgentBalance` | `{agent_id}` | `{balance, stake}` |

### 3.5 E2E Test Scenarios

| ID | Scenario | Expected |
|----|----------|----------|
| T1 | Register agent with minimum stake | Success, agent_id returned |
| T2 | Register agent with insufficient stake | Revert `E_INSUFFICIENT_STAKE` |
| T3 | Issue session key with PERM_INFERENCE | Key created, can submit inference |
| T4 | Session key exceeds spending limit | Revert, tx rejected |
| T5 | Session key expired (TTL passed) | Revert, key invalid |
| T6 | Session key wrong permission (has INFERENCE, tries TRANSFER) | Revert |
| T7 | Owner revokes session key, key tries to act | Revert, key destroyed |
| T8 | Freeze agent, then try any operation | All operations revert |
| T9 | Revoke agent, stake returned after cooldown | Stake returned to owner |
| T10 | Non-owner tries to freeze agent | Revert `E_NOT_OWNER` |

---

## 4. Milestone M2: Gas Sponsorship / Paymaster (P1)

### 4.1 Paymaster Contract

```solidity
contract QFCPaymaster is IPaymaster {
    address public entryPoint;
    address public owner;

    // Sponsor deposits
    mapping(address => uint256) public sponsorDeposits;

    // Per-agent sponsorship config
    struct SponsorshipConfig {
        address sponsor;
        uint256 maxPerOp;          // Max gas cost per UserOp
        uint256 maxPerDay;         // Daily cap
        uint256 spentToday;
        uint64 dayStart;
        bool active;
    }

    mapping(address => SponsorshipConfig) public agentSponsorship;

    function validatePaymasterUserOp(
        PackedUserOperation calldata userOp,
        bytes32 userOpHash,
        uint256 maxCost
    ) external override returns (bytes memory context, uint256 validationData) {
        address agent = userOp.sender;
        SponsorshipConfig storage config = agentSponsorship[agent];

        require(config.active, "No sponsorship");
        require(maxCost <= config.maxPerOp, "Exceeds per-op limit");

        // Reset daily counter if new day
        if (block.timestamp >= config.dayStart + 1 days) {
            config.spentToday = 0;
            config.dayStart = uint64(block.timestamp);
        }

        require(config.spentToday + maxCost <= config.maxPerDay, "Daily limit");
        config.spentToday += maxCost;

        return (abi.encode(agent, maxCost), 0);
    }

    function postOp(
        PostOpMode mode,
        bytes calldata context,
        uint256 actualGasCost,
        uint256 actualUserOpFeePerGas
    ) external override {
        (address agent, uint256 maxCost) = abi.decode(context, (address, uint256));
        // Refund over-charge
        uint256 refund = maxCost - actualGasCost;
        if (refund > 0) {
            agentSponsorship[agent].spentToday -= refund;
        }
    }

    // Sponsor management
    function deposit() external payable;
    function withdraw(uint256 amount) external;
    function sponsorAgent(address agent, uint256 maxPerOp, uint256 maxPerDay) external;
    function revokeSponsor(address agent) external;
}
```

### 4.2 Sponsorship Flow

```
Owner/Sponsor                    Paymaster                 EntryPoint
    │                               │                          │
    ├── deposit() ─────────────────►│                          │
    ├── sponsorAgent(agent) ───────►│                          │
    │                               │                          │
Agent (via session key)             │                          │
    ├── UserOp (paymasterAndData) ──┼─────────────────────────►│
    │                               │◄── validatePaymasterUserOp
    │                               │── check limits ──────────►│
    │                               │                          ├── execute
    │                               │◄──────── postOp (refund) │
```

---

## 5. Milestone M3: Explorer Upgrades (P1)

### 5.1 New Explorer Pages

| Page | URL | Content |
|------|-----|---------|
| Agent List | `/agents` | All registered agents, status, capabilities, stake |
| Agent Detail | `/agents/:id` | Agent info, session keys, tx history, spending |
| Agent Dashboard | `/agents/dashboard` | Operator view: all owned agents, alerts, spending trends |
| Session Key Manager | `/agents/:id/keys` | Active keys, permissions, usage, revoke button |

### 5.2 Explorer API Endpoints

| Endpoint | Method | Returns |
|----------|--------|---------|
| `GET /api/agents` | List | Paginated agent list with filters |
| `GET /api/agents/:id` | Detail | Full agent info + recent activity |
| `GET /api/agents/:id/transactions` | History | Agent's transaction history |
| `GET /api/agents/:id/session-keys` | Keys | Active session keys with usage stats |
| `GET /api/agents/:id/spending` | Analytics | Spending by period, by contract |
| `GET /api/agents/stats` | Overview | Total agents, total stake, active count |

### 5.3 Indexer Requirements

The explorer indexer must subscribe to these on-chain events:

```solidity
event AgentRegistered(bytes32 indexed agentId, address indexed owner, uint256 stake);
event AgentRevoked(bytes32 indexed agentId, address indexed owner, uint256 stakeReturned);
event AgentFrozen(bytes32 indexed agentId, address indexed caller);
event SessionKeyIssued(bytes32 indexed agentId, address indexed key, uint64 permissions, uint64 expiresAt);
event SessionKeyRevoked(bytes32 indexed agentId, address indexed key);
event AgentFunded(bytes32 indexed agentId, uint256 amount);
event SponsorshipConfigured(address indexed agent, address indexed sponsor, uint256 maxPerDay);
```

### 5.4 Database Schema

```sql
CREATE TABLE agents (
    agent_id        TEXT PRIMARY KEY,
    owner           TEXT NOT NULL,
    capabilities    JSONB,
    endpoint        TEXT,
    stake           NUMERIC NOT NULL,
    frozen          BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMP NOT NULL,
    revoked_at      TIMESTAMP,
    tx_hash         TEXT NOT NULL
);

CREATE TABLE session_keys (
    key_id          TEXT PRIMARY KEY,
    agent_id        TEXT REFERENCES agents(agent_id),
    public_key      TEXT NOT NULL,
    permissions     BIGINT NOT NULL,
    spending_limit  NUMERIC,
    spent_this_period NUMERIC DEFAULT 0,
    period_duration INTEGER,
    expires_at      TIMESTAMP NOT NULL,
    revoked_at      TIMESTAMP,
    created_tx      TEXT NOT NULL
);

CREATE TABLE agent_transactions (
    tx_hash         TEXT PRIMARY KEY,
    agent_id        TEXT REFERENCES agents(agent_id),
    session_key     TEXT,
    action          TEXT NOT NULL,  -- 'inference', 'transfer', 'stake', etc.
    value           NUMERIC,
    target_contract TEXT,
    timestamp       TIMESTAMP NOT NULL,
    status          TEXT NOT NULL   -- 'success', 'reverted'
);

CREATE TABLE agent_sponsorships (
    agent_address   TEXT NOT NULL,
    sponsor         TEXT NOT NULL,
    max_per_op      NUMERIC,
    max_per_day     NUMERIC,
    spent_today     NUMERIC DEFAULT 0,
    active          BOOLEAN DEFAULT TRUE,
    PRIMARY KEY (agent_address, sponsor)
);

CREATE INDEX idx_agents_owner ON agents(owner);
CREATE INDEX idx_agent_tx_agent ON agent_transactions(agent_id, timestamp DESC);
CREATE INDEX idx_session_keys_agent ON session_keys(agent_id);
```

---

## 6. Milestone M4: OpenClaw Integration (P2)

### 6.1 New OpenClaw Commands

| Command | Description |
|---------|-------------|
| `agent register` | Register a new agent with stake and capabilities |
| `agent fund <agent_id> <amount>` | Fund an agent's wallet |
| `agent revoke <agent_id>` | Revoke agent and reclaim stake |
| `agent list` | List all agents owned by the current wallet |
| `agent status <agent_id>` | Show agent status, balance, active session keys |
| `session-key issue <agent_id>` | Issue a new session key with permissions |
| `session-key revoke <key_id>` | Revoke a session key |
| `session-key list <agent_id>` | List active session keys |

### 6.2 OpenClaw Agent Wallet Client

```typescript
// qfc-openclaw-skill/src/agent-wallet.ts
import { QFCClient } from '@qfc/sdk-js';

export class AgentWalletClient {
    constructor(
        private qfc: QFCClient,
        private sessionKey?: { privateKey: string; agentId: string }
    ) {}

    // Use session key instead of owner key for operations
    async submitInference(task: InferenceTask): Promise<InferenceResult> {
        if (this.sessionKey) {
            return this.qfc.submitInferenceWithSessionKey(
                task,
                this.sessionKey.privateKey,
                this.sessionKey.agentId
            );
        }
        return this.qfc.submitInference(task);
    }

    async register(params: RegisterParams): Promise<AgentRegistration> { ... }
    async fund(agentId: string, amount: bigint): Promise<TxHash> { ... }
    async revoke(agentId: string): Promise<{ txHash: string; stakeReturned: bigint }> { ... }
    async issueSessionKey(params: SessionKeyParams): Promise<SessionKey> { ... }
    async revokeSessionKey(keyId: string): Promise<TxHash> { ... }
}
```

### 6.3 Demo Scenarios

| Demo | Description |
|------|-------------|
| **Autonomous Trader** | Register agent → issue session key (INFERENCE + TRANSFER) → agent runs sentiment analysis → executes trades → owner monitors via explorer |
| **Content Generator** | Register agent → issue session key (INFERENCE only) → agent generates content on schedule → results stored on-chain |
| **AI Oracle** | Register agent → sponsor gas via paymaster → agent answers on-chain queries → revenue shared to token holders |
| **Multi-Agent Pipeline** | Register 3 agents → chain them via intents → classify → analyze → summarize |

---

## 7. Cross-Repo Dependency Map

```
qfc-contracts (Solidity)
  ├── QFCAgentAccount.sol        ─── M1
  ├── QFCAccountFactory.sol      ─── M1
  ├── QFCPaymaster.sol           ─── M2
  └── PolicyManager.sol          ─── M1

qfc-core (Rust)
  ├── qfc-qvm/agent_registry     ─── M1
  ├── qfc-qvm/session_keys       ─── M1
  ├── qfc-rpc/agent_endpoints    ─── M1
  └── qfc-executor/erc4337       ─── M1

qfc-sdk-js (TypeScript)
  ├── AgentWalletClient          ─── M1
  └── PaymasterClient            ─── M2

qfc-explorer (Next.js)
  ├── /agents pages               ─── M3
  ├── API endpoints               ─── M3
  └── Indexer events              ─── M3

qfc-openclaw-skill (TypeScript)
  ├── agent commands              ─── M4
  ├── session-key commands        ─── M4
  └── AgentWalletClient           ─── M4
```

### Execution Timeline

```
Week:  1   2   3   4   5   6   7   8
       ├───────────────┤
       M1: Core + Session Keys + Tests
                ├───────────┤
                M2: Paymaster
                    ├───────────┤
                    M3: Explorer
                            ├───────┤
                            M4: OpenClaw
```

**Total: ~8 weeks with 1-2 developers + Claude Code.**

---

## 8. Security Model

### 8.1 Defense-in-Depth Layers

| Layer | Mechanism | Enforced By |
|-------|-----------|-------------|
| 1. VM-level | Resources cannot be forged/duplicated | QVM |
| 2. Session key | TTL + permission bitmask + spending limit | QVM + EVM |
| 3. Wallet policy | Per-tx limit, per-period limit, contract allowlist | EVM (QFCAgentAccount) |
| 4. Time-lock | Large withdrawals require delay | EVM (PolicyManager) |
| 5. Kill switch | Owner/governance can freeze agent | QVM |
| 6. Audit trail | All actions on immutable ledger | Blockchain |

### 8.2 Threat Model

| Threat | Mitigation |
|--------|------------|
| Prompt injection → unauthorized tx | Session key permissions limit blast radius |
| Session key compromise | TTL auto-expires; owner can revoke instantly |
| Owner key compromise | Time-lock on large withdrawals; multi-party approval for high-value |
| Paymaster drain | Per-agent daily caps; sponsor can revoke |
| Malicious agent drains funds | Per-tx and per-period spending limits |
| Multi-agent collusion | Contract allowlist limits interaction surface |
| Replay attack | Nonce guard on session keys |

### 8.3 Key Rotation Policy

- Session keys: recommended max TTL of 7 days
- Owner key: support rotation via `transferOwnership()`
- Automatic key rotation: OpenClaw can issue new key before old one expires

---

## 9. Testing Strategy

### 9.1 Test Pyramid

| Level | Count | Repo | Framework |
|-------|-------|------|-----------|
| Unit (QVM) | ~30 | qfc-core | Rust `#[test]` |
| Unit (Solidity) | ~50 | qfc-contracts | Foundry |
| Integration | ~20 | qfc-core | Rust integration tests |
| E2E | ~10 | qfc-core | Multi-node testnet |
| UI | ~15 | qfc-explorer | Playwright |

### 9.2 Acceptance Criteria

1. ✅ Agent registered with stake on QVM
2. ✅ Session key issued with permissions bitmask
3. ✅ Session key enforces spending limit per period
4. ✅ Expired session key rejected
5. ✅ Revoked session key rejected
6. ✅ Agent frozen → all operations fail
7. ✅ Agent revoked → stake returned after cooldown
8. ✅ ERC-4337 UserOp validated through QFCAgentAccount
9. ✅ Paymaster sponsors gas for agent operations
10. ✅ Paymaster enforces daily spending cap
11. ✅ Explorer shows agent list with status
12. ✅ Explorer shows session key details
13. ✅ Explorer shows agent transaction history
14. ✅ OpenClaw `agent register` command works
15. ✅ OpenClaw `session-key issue` command works
16. ✅ OpenClaw can execute inference with session key (no owner key)
17. ✅ Full demo: register → fund → issue key → inference → monitor → revoke

---

## References

- [24-AI-AGENT-FRAMEWORK.md](./24-AI-AGENT-FRAMEWORK-EN.md) — Research basis
- [28-V3-ROADMAP.md](./28-V3-ROADMAP-EN.md) — v3.0 overall roadmap
- [ERC-4337 Specification](https://eips.ethereum.org/EIPS/eip-4337)
- [Account Abstraction Overview — Alchemy](https://www.alchemy.com/overviews/what-is-account-abstraction)
