# AI Agent On-Chain Frameworks & QFC Opportunity

> Last Updated: 2026-03-08 | Version 1.0
> GitHub Issue: #6
> Author: Alex Wei, Product Manager @ QFC Network

---

## 1. Executive Summary

On-chain AI agents — autonomous programs that execute blockchain transactions — are a $3B+ market (peak $4.34B in Oct 2025). QFC's dual VM (EVM + QVM) and native AI inference coordinator create a unique opportunity to be the best platform for AI agents.

**Key Findings:**

- **Virtuals Protocol** ($915M market cap) pioneered agent tokenization; revenue-sharing model generates real value
- **ElizaOS** is the dominant open-source agent framework (3,800+ stars); TypeScript, plugin-based
- **Autonolas** has the most sophisticated composability model (components → agents → services as NFTs)
- Every existing agent framework bridges **off-chain** for AI inference — QFC can make it **on-chain native**
- QVM's Move-style Resource types provide **stronger agent security guarantees** than EVM-only approaches

**Recommendation**: Position QFC as the "agent-native AI chain" — where inference is a first-class primitive, agent capabilities are VM-enforced resources, and EVM compatibility enables tokenization.

---

## 2. Major Agent Projects

### 2.1 Virtuals Protocol (VIRTUAL, ~$915M market cap)

**Platform**: Base (Ethereum L2) + Solana. Tokenization and co-ownership of AI agents.

**GAME Framework** (General Autonomous Modular Entity):
- Composable, modular agents with separated planning and execution
- Agent launch: 100 VIRTUAL fee → bonding curve → permanent LP at 42,000 VIRTUAL
- Each agent is an ERC-20 token paired with VIRTUAL

**Revenue Distribution**:

| Recipient | Share |
|-----------|-------|
| Agent's own wallet | 60% |
| Buy-back & burn of agent token | 30% |
| Virtuals Treasury | 10% |

**Scale**: Combined agent market cap >$500M, 650K+ VIRTUAL holders.

### 2.2 ElizaOS (formerly ai16z / ELIZA)

**What**: Open-source TypeScript framework for autonomous AI agents with blockchain integration.

**Architecture**:
- Modular plugin system — core runtime extensible without modification
- Supports multiple LLM backends (OpenAI, LLaMA, Qwen) and multiple chains
- Plugins for: NFT generation, blockchain analytics, DeFi operations, portfolio management

**Products**:
- **Auto.fun** (Apr 2025): No-code agent creation platform
- **elizaOS v2** (Oct 2025): Multichain architecture

**Scale**: 3,800+ GitHub stars, 1,100+ forks, 138+ contributors.

### 2.3 Autonolas (OLAS, $13.8M raised Feb 2025)

**What**: Protocol for composable, decentralized multi-agent services (MAS).

**Architecture**:
- **Open Autonomy Framework**: Multi-agent systems running off-chain, coordinated on-chain
- **NFT Registries**: Components → Agents → Services, each registered as NFTs
- **POSE** (Protocol-Owned Services): The protocol itself owns and operates agent services

**Scale**: 700K+ transactions/month, 3.5M+ total across 9 blockchains.

**Tokenomics**: OLAS coordinates capital-code pairing. Developers earn proportional to contributions; operators earn for running services; bonders provide liquidity.

### 2.4 Spectral (Syntax)

**What**: Natural language → Solidity smart contracts, deployed autonomously.

- Each agent gets a Smart Wallet (Turnkey HSM-backed) for trustless deployment
- 60K+ users, 1M+ contracts generated, 4,700+ memecoin launches
- Building **InferChain**: Dedicated chain for AI inference verification

**QFC relevance**: QFC already has what InferChain is trying to build — native inference verification.

### 2.5 Fetch.ai

**What**: Agent communication and discovery platform.

- **uAgents Framework**: Lightweight Python library for microagents
- **Almanac Contract**: Decentralized agent registry (like DNS for agents)
- **DeltaV**: AI search interface matching requests to agents
- **Agent Communication Protocol (ACP)**: Agents discover each other by protocol digest

---

## 3. Agent Security Patterns

| Control | Description | Implementation |
|---------|-------------|---------------|
| **Spending limits** | Per-tx and per-period caps | On-chain enforcement |
| **Contract allowlists** | Agents can only interact with whitelisted contracts | Wallet policy |
| **Kill switch** | Owner freezes agent wallet / revokes signing | Admin function |
| **Time-locks** | Large withdrawals require delay | Timelock contract |
| **Multi-party approval** | Threshold signatures for high-value actions | Multi-sig |
| **Audit trails** | All actions on immutable ledger | Inherent to blockchain |
| **Circuit breakers** | Automatic halt on anomalous behavior | Monitor contract |

**Threat model** (from academic survey, arxiv 2601.04583):
- Prompt injection → unauthorized transactions
- Policy misuse → agent circumventing boundaries
- Key compromise
- Multi-agent collusion

---

## 4. Agent-Contract Interaction Models

| Model | Description | Security | Used By |
|-------|-------------|----------|---------|
| **EOA + private key** | Agent holds key directly | Weak — no on-chain policy | Early projects |
| **Account Abstraction (ERC-4337)** | UserOperations via smart contract wallet | **Strong** — programmable policies | Spectral, emerging standard |
| **Multi-agent threshold** | Multiple agents co-sign | Strongest — no single point of failure | Autonolas MAS |

**ERC-4337 is the emerging standard**: Smart contract wallets with custom validation logic (spending limits, allowlists, paymasters for gas abstraction).

---

## 5. Market Data

| Metric | Value |
|--------|-------|
| AI Agents sector market cap | ~$3.06B (Mar 2026) |
| Peak market cap | ~$4.34B (Oct 2025) |
| Number of AI agent projects | 550+ |
| Peak 24h trading volume | ~$1.09B |

**Top tokens**: VIRTUAL (~$915M), FET (ASI Alliance), TRAC (~$356M), OLAS.

---

## 6. QFC Differentiation for AI Agents

### 6.1 The Gap: Every Agent Framework Bridges Off-Chain for AI

```
Current agent architecture (Virtuals, ElizaOS, Spectral):

  Agent on-chain → calls off-chain API → AI inference → result back on-chain
                    ^^^^^^^^^^^^^^^^
                    Trust gap: who verifies the inference was correct?
```

QFC eliminates this trust gap:

```
QFC agent architecture:

  Agent on-chain → calls QFC AI Coordinator → Miner runs inference →
  → Verified result (spot-check / zkML) → Result on-chain as Resource
                                           ^^^^^^^^^^^^^^^^^^^^^^^^
                                           Verified, composable, type-safe
```

### 6.2 Resource-Typed Agent Capabilities (QVM)

On EVM, agent permissions are enforced by contract logic (can have bugs). On QVM, agent capabilities are **VM-enforced resources**:

```move
// Agent capability: right to spend up to 100 QFC on inference
resource InferenceCapability {
    id: UID,
    owner: address,
    remaining_budget: u64,    // Cannot be modified except by authorized functions
    allowed_models: vector<ModelId>,
    expires_at: u64,
}

// Agent requests inference — must present and consume capability
public fun request_inference(
    cap: &mut InferenceCapability,
    task: InferenceTask,
): InferenceResult {
    assert!(cap.remaining_budget >= task.fee, E_INSUFFICIENT_BUDGET);
    cap.remaining_budget -= task.fee;
    // Submit to AI Coordinator...
}
```

**Why this is stronger than EVM**:
- `InferenceCapability` cannot be forged, duplicated, or spent beyond its limit at the VM level
- No reentrancy risk — resources are consumed linearly
- Kill switch = simply destroy or freeze the capability resource

### 6.3 Dual-VM Composability

| Layer | VM | Role |
|-------|-----|------|
| Agent tokenization & trading | **EVM** | ERC-20 agent tokens, Uniswap-style LPs (Virtuals pattern) |
| Agent registry & composition | **QVM** | Components → Agents → Services as Resources (Autonolas pattern) |
| AI inference | **QFC AI Coordinator** | Native, verified inference as a first-class primitive |
| DeFi integration | **EVM** | Existing Solidity DeFi protocols (cross-VM calls) |
| Agent wallet | **EVM** | ERC-4337 account abstraction (already supported) |

### 6.4 Agent Registry as Resources (Fetch.ai Almanac + QVM)

```move
resource AgentRegistration {
    id: UID,
    owner: address,
    protocol_digests: vector<Hash>,    // What protocols this agent supports
    capabilities: vector<String>,       // "text-generation", "image-analysis", etc.
    endpoint: String,                   // How to reach this agent
    stake: u64,                         // Skin-in-the-game
}
```

- Agents register by creating a Resource (costs stake)
- Discovery: query by protocol_digest or capability
- Transfer: agents can be sold/transferred (Resource ownership transfer)
- Cannot be duplicated (Move guarantee)

---

## 7. Recommended Architecture

### 7.1 QFC Agent Stack

```
┌─────────────────────────────────────────────────┐
│  User / DApp                                     │
│  "I want an agent that trades based on           │
│   AI sentiment analysis"                         │
├─────────────────────────────────────────────────┤
│  Agent Runtime (ElizaOS plugin / custom)         │
│  Off-chain agent logic, LLM planning             │
├─────────────────────────────────────────────────┤
│  QFC SDK (qfc-sdk-js / qfc-sdk-python)           │
│  Submit inference tasks, manage capabilities      │
├────────────────────┬────────────────────────────┤
│  EVM Layer         │  QVM Layer                  │
│  - Agent tokens    │  - Agent registry           │
│  - ERC-4337 wallet │  - Capability resources     │
│  - DeFi protocols  │  - Inference results        │
│  - Paymasters      │  - Kill switches            │
├────────────────────┴────────────────────────────┤
│  QFC AI Coordinator                              │
│  - Task submission → Miner assignment            │
│  - Verification (spot-check / zkML)              │
│  - Result delivery as Resource                   │
└─────────────────────────────────────────────────┘
```

### 7.2 ElizaOS Integration Path

Since ElizaOS is TypeScript and plugin-based, integration is straightforward:

```typescript
// qfc-elizaos-plugin (wraps qfc-sdk-js)
export const qfcPlugin: Plugin = {
    name: "qfc-inference",
    actions: [
        {
            name: "RUN_INFERENCE",
            description: "Run AI inference on QFC network",
            handler: async (runtime, message) => {
                const result = await qfcClient.submitInference({
                    model: "qfc-llm-7b",
                    prompt: message.content,
                    maxTokens: 500,
                });
                return result.output;
            },
        },
    ],
};
```

No need to fork ElizaOS — just publish a plugin to npm.

---

## 8. Implementation Roadmap

### Phase 1: Agent Capability Resources (3-4 weeks)

| Task | Description |
|------|-------------|
| Define `AgentCapability` resource in QSC | Spending limits, model allowlists, expiry |
| Implement capability-gated inference | AI Coordinator checks capability before task assignment |
| Kill switch mechanism | Resource freeze/destroy functions |

### Phase 2: Agent Registry (3-4 weeks)

| Task | Description |
|------|-------------|
| `AgentRegistration` resource | Registry with protocol digests and capability metadata |
| Discovery API | RPC endpoints for querying agents by capability |
| Staking requirement | Agents must stake QFC to register (Sybil resistance) |

### Phase 3: SDK & Framework Integration (4-6 weeks)

| Task | Description |
|------|-------------|
| ElizaOS plugin | `qfc-elizaos-plugin` wrapping qfc-sdk-js |
| Agent wallet template | ERC-4337 smart wallet with QFC-specific validation |
| Example agents | Sentiment trading agent, AI oracle agent, content generation agent |

### Phase 4: Agent Tokenization (4-6 weeks)

| Task | Description |
|------|-------------|
| Agent token factory | EVM contract for launching agent tokens (Virtuals pattern) |
| Revenue sharing | On-chain fee distribution to agent token holders |
| Cross-VM bridge | Agent tokens (EVM) linked to agent capabilities (QVM) |

---

## 9. Competitive Positioning

| Feature | Virtuals | ElizaOS | Autonolas | Fetch.ai | **QFC (target)** |
|---------|----------|---------|-----------|----------|-----------------|
| Agent tokenization | ✅ Core feature | ❌ | ❌ | ❌ | ✅ (EVM) |
| Agent composability | Basic | Plugin-based | ✅ NFT registry | Protocol digests | ✅ Resource registry |
| Native AI inference | ❌ Off-chain | ❌ Off-chain | ❌ Off-chain | ❌ Off-chain | **✅ On-chain verified** |
| Agent security | Contract-level | Application-level | Multi-agent threshold | Application-level | **VM-enforced resources** |
| Smart contract interaction | EVM only | Multi-chain | Multi-chain | Multi-chain | **Dual VM (EVM + QVM)** |
| ERC-4337 support | ❌ | ❌ | ❌ | ❌ | ✅ |

**QFC's unique position**: The only platform where agents can request **verified AI inference as a native blockchain operation** with **VM-level capability enforcement**.

---

## References

- [Virtuals Protocol Whitepaper](https://whitepaper.virtuals.io)
- [Virtuals Protocol Review - Coin Bureau](https://coinbureau.com/review/virtuals-protocol-review)
- [ElizaOS Documentation](https://docs.elizaos.ai/)
- [ElizaOS GitHub](https://github.com/elizaOS/eliza)
- [Olas Network](https://olas.network/)
- [Spectral Labs](https://www.spectrallabs.xyz/)
- [Fetch.ai uAgents Framework](https://uagents.fetch.ai/docs)
- [Fetch.ai Architecture Paper (arxiv)](https://arxiv.org/html/2510.18699v1)
- [Autonomous Agents on Blockchains (arxiv 2601.04583)](https://arxiv.org/abs/2601.04583)
- [AI and Crypto Agentic Payments - Chainalysis](https://www.chainalysis.com/blog/ai-and-crypto-agentic-payments/)
- [AI Agents Category - CoinGecko](https://www.coingecko.com/en/categories/ai-agents)
- [Account Abstraction ERC-4337 - Alchemy](https://www.alchemy.com/overviews/what-is-account-abstraction)
