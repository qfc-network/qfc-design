# Intent-Based Architecture: Research & QFC Implications

> Last Updated: 2026-03-08 | Version 1.0
> GitHub Issue: #9
> Author: Alex Wei, Product Manager @ QFC Network

---

## 1. Executive Summary

Intent-based architecture is a paradigm shift from imperative transactions ("do A then B, pay C") to declarative intents ("I want outcome X, willing to pay up to C"). This report evaluates whether intent-based patterns can improve QFC's AI inference request/fulfillment UX.

**Key Findings:**

- **Anoma** is the most ambitious intent-centric protocol — full operating system with Resource Machine, solver networks, and heterogeneous consensus (Typhon). Mainnet Phase 1 launched September 2025
- **CoW Protocol** ($10B/month volume) proves solver competition works in production for DeFi batch auctions
- **UniswapX** and **1inch Fusion** demonstrate Dutch auction-based intent fulfillment at scale
- **ERC-7683** (Across + Uniswap Labs) is emerging as the cross-chain intent standard
- **Solver centralization is a real problem** — on Ethereum, 2 builders win >90% of block auctions
- AI inference requests map naturally to intents, but **solver economics are thin** (simpler optimization space than DeFi)

**Recommendation**: Adopt the **intent pattern** (declarative requests + competitive fulfillment) without the full intent infrastructure. Implement a lightweight "intent mode" for complex/batch inference jobs while keeping the direct TaskPool for latency-critical workloads.

---

## 2. Major Intent-Based Projects

### 2.1 Anoma Protocol

**What**: A distributed operating system for intent-centric applications. Users express desired outcomes; solvers find optimal execution paths.

**Core Components**:

| Component | Role |
|-----------|------|
| **Intent Gossip Network** | Broadcast intents; solvers discover matching counterparties |
| **Solvers** | Third-party actors that match intents and produce balanced transactions |
| **Validity Predicates (VPs)** | Stateless logic checking whether state changes are valid; parallelizable |
| **Anoma Resource Machine (ARM)** | Execution layer with resource model (neither account nor UTXO) |
| **Typhon** | Heterogeneous Paxos consensus — multi-chain atomic settlement |

**Resource Model**: Resources are first-class primitives that carry their own logic (validity predicates). Can represent anything — tokens, digital assets, capabilities. Related to linear types in PL theory (consumed, not copied).

**Status**:
- First devnet: January 2025
- Mainnet Phase 1: September 2025 (on Ethereum)
- Future: private solving (FHE, MPC), on-demand consensus, "Chimera chains"

**Namada** (Anoma's first chain):
- Sovereign PoS L1 using CometBFT, mainnet December 2024
- Multi-Asset Shielded Pool (MASP) — extends Zcash Sapling for arbitrary assets
- Privacy rewards: users earn NAM for contributing to shielded set

### 2.2 Essential Protocol

**What**: Declarative intent-centric L2 on Ethereum. Uses constraint-based programming instead of imperative execution.

| Property | Anoma | Essential |
|----------|-------|-----------|
| Scope | Full operating system | Focused intent layer on Ethereum |
| Language | ARM resource model | **Pint** (constraint DSL) |
| Privacy | Built-in (ZKPs, FHE) | Not primary focus |
| Consensus | Own (Typhon) | Relies on Ethereum |
| Status | Mainnet Phase 1 | Pre-alpha, status unclear |

**Pint Language**: Developers define what state changes are allowed (constraints), not how to change state. Solvers figure out the "how."

**Funding**: $11M Series A led by Archetype.

### 2.3 CoW Protocol (Coincidence of Wants)

**What**: Batch auction DEX where user intents are grouped into ~30-second windows. Solvers compete to settle each batch optimally.

| Property | Value |
|----------|-------|
| Monthly volume | $10B+ (late 2024/early 2025) |
| Mechanism | Batch auctions, uniform clearing price |
| Solver network | Largest in DeFi |
| MEV protection | Same-token-pair orders clear at uniform price |
| Innovation | Combinatorial Auctions (multiple solvers per batch) |

**How it works**: Orders in same batch, same token pair clear at uniform price — eliminates sandwich attacks and front-running within the batch.

### 2.4 UniswapX

**What**: Intent-based trading where users sign off-chain "intent to trade" messages. Dutch auction price discovery.

| Property | Value |
|----------|-------|
| Mechanism | Dutch auction — price starts above target, decays over time |
| Fillers | MEV searchers, market makers, on-chain agents compete to fill |
| Gas cost | **Gasless for users** via Permit2 signatures |
| Per-intent | Each intent individually auctioned (unlike CoW's batching) |

### 2.5 1inch Fusion

**What**: Intent-based swaps with verified professional "resolvers."

- Dutch auction among resolvers for each order
- Three-phase execution with escrow mechanism
- **Fusion+**: Cross-chain atomic swaps
- Built-in recovery: auto-cancel after timelock if resolver unresponsive

### 2.6 Across Protocol & ERC-7683

**Across Protocol**: Intent-based cross-chain bridging.
- 3-layer system: request-for-quote → relayer competition → settlement verification
- Relayers fill orders using own capital; users get funds near-instantly
- V4 (July 2025): universal architecture with intents + ZK proofs

**ERC-7683** (Cross-Chain Intent Standard):
- Co-authored by Across + Uniswap Labs
- Standardizes: `CrossChainOrder`, `ResolvedCrossChainOrder`
- Settlement interfaces: `IOriginSettler`, `IDestinationSettler`
- Enables shared filler networks across protocols
- $4.1B in cross-chain volume over 90 days

---

## 3. Solver/Filler Networks

### 3.1 How Solvers Work

Solvers take user intents, compute optimal execution paths, compete to fulfill them. They pay gas, handle routing complexity, and extract profit from the spread between user's acceptable price and achieved execution.

### 3.2 Solver Economics

- CoW Protocol: advanced solver teams earn hundreds of thousands of dollars annually
- Revenue = delta between user's max acceptable price and achieved price
- MEV extraction redirected into solver competition (ideally benefiting users)

### 3.3 Centralization Risk — Critical Warning

| Metric | Value |
|--------|-------|
| Block auction winners | **2 builders win >90%** of Ethereum block auctions (early 2025) |
| MEV volume | $561.92M total (2025), sandwich attacks = $289.76M (51.56%) |
| Trend | Execution shifting to private channels and industrial MEV supply chains |
| Effect | Reduced user-facing harm but **concentrated power in fewer intermediaries** |

**Feedback loop**: Firms with superior latency/order flow accumulate capital faster, dominate further. This is an observed and persistent phenomenon in every deployed solver network.

**Mitigation strategies**: Solver rotation, bonding requirements, minimum solver diversity thresholds, batch auctions (CoW-style).

---

## 4. Intent-Based AI Inference Analysis

### 4.1 Intent Mapping

AI inference requests map naturally to the intent pattern:

| Intent Concept | QFC Inference Equivalent |
|---------------|------------------------|
| User intent | "Classify this image with model X, accuracy ≥ threshold" |
| Constraints | max_cost, max_latency, min_accuracy, model_version |
| Solver | Miner selection algorithm / matchmaker |
| Filler/Resolver | The miner that executes inference |
| Dutch auction | Price discovery among miners (bid down from max price) |
| Settlement | Proof of inference delivery + payment |
| Validity predicate | Inference quality verification logic |

### 4.2 Current vs Intent Model

**Current TaskPool (imperative)**:
```
User creates task → task enters pool → miner picks up → executes →
submits result → verified → paid
```

**Intent model (declarative)**:
```
User expresses intent ("inference X, cost ≤ Y, latency ≤ Z") →
solvers compete to match with optimal miner → winning solver routes →
miner executes → result delivered → settled
```

### 4.3 Benefits

1. **Better UX**: Users specify outcomes, not execution details
2. **Solver competition**: Drives down cost and latency
3. **Composability**: Intents can be combined ("classify image AND if category=X then run model Y")
4. **MEV protection**: Batch auctions prevent inference pricing front-running
5. **Cross-chain**: With ERC-7683-like standards, inference intents fulfilled across chains

### 4.4 Risks

1. **Solver centralization**: 2-3 sophisticated solvers could dominate miner selection, extracting rent
2. **Latency overhead**: Intent gossip → solver matching → miner routing adds hops vs direct pool pickup
3. **Complexity**: Full intent infrastructure is significant engineering overhead
4. **Thin solver economics**: Spread between user's max price and miner's min price may be too small for solver profitability (simpler optimization space than DeFi routing)
5. **Quality verification**: DeFi intents have clear success criteria (tokens delivered); inference quality is harder to verify declaratively

### 4.5 Assessment

| Factor | Rating | Notes |
|--------|--------|-------|
| Architectural fit | Medium-High | Inference requests map well to intents |
| Implementation complexity | High | Full intent stack is heavy engineering |
| UX improvement | Medium | Main benefit: hiding miner selection complexity |
| Solver economics viability | Low-Medium | Thin margins vs DeFi trading |
| Centralization risk | High | Observed in every deployed solver network |
| Latency impact | Negative | Additional hops hurt real-time inference |
| Composability benefit | **High** | Multi-step AI pipelines benefit most |

---

## 5. Recommended Hybrid Approach for QFC

### 5.1 Two-Path Architecture

Don't build a full Anoma-style intent operating system. Instead, adopt the intent **pattern** as a protocol extension:

```
┌─────────────────────────────────────────────────────┐
│  User / DApp                                         │
│  Chooses: Direct Mode or Intent Mode                 │
├──────────────────────┬──────────────────────────────┤
│  Direct Mode         │  Intent Mode                  │
│  (latency-critical)  │  (cost-optimized / complex)   │
│                      │                                │
│  Task → TaskPool     │  Intent → Matchmaker          │
│  → First eligible    │  → Constraint evaluation      │
│  miner picks up      │  → Dutch auction among miners │
│  → Execute → Verify  │  → Best bid wins              │
│                      │  → Execute → Verify            │
│  Latency: <1 sec     │  Latency: 5-30 sec            │
│  Cost: market rate   │  Cost: optimized (lower)       │
├──────────────────────┴──────────────────────────────┤
│  Shared: AI Coordinator, Verification, Settlement    │
└─────────────────────────────────────────────────────┘
```

### 5.2 Direct Mode (Existing TaskPool)

Keep for:
- Real-time inference (chatbots, live classification)
- Simple single-model requests
- Latency-sensitive applications

No changes needed — this is QFC's current architecture.

### 5.3 Intent Mode (New)

Add for:
- **Cost-optimized batch jobs**: "Run 1000 embeddings, budget = X QFC, deadline = 1 hour"
- **Multi-model pipelines**: "Classify image → if animal, run species detection → generate description"
- **Quality-constrained requests**: "Generate text, perplexity ≤ threshold, cost ≤ Y"
- **Cross-chain inference** (see doc #25): Intent from external chain → QFC fulfills

**Intent structure**:

```move
resource InferenceIntent {
    id: UID,
    requester: address,
    // What
    model_id: Option<ModelId>,      // Specific model or any matching capability
    capability: String,              // "text-generation", "embedding", etc.
    input_hash: Hash,
    // Constraints
    max_cost: u64,                   // Maximum fee in QFC
    max_latency_ms: u64,            // Maximum acceptable latency
    min_accuracy: Option<u64>,       // Minimum quality threshold (0-100)
    // Composition
    next_intent: Option<UID>,        // Chain to next intent on completion
    condition: Option<String>,       // Conditional routing logic
    // Lifecycle
    deadline: u64,                   // Auto-cancel after this timestamp
    created_at: u64,
}
```

### 5.4 Lightweight Matchmaker (Not Full Solver Network)

**Key insight**: For AI inference, the optimization space is simpler than DeFi routing. A lightweight "matchmaker" suffices — no need for a full solver network with gossip and competition.

```
Matchmaker logic:
  1. Receive InferenceIntent
  2. Filter eligible miners (model support, tier, availability)
  3. If single-model, simple request:
     → Match to cheapest/fastest eligible miner (weighted by PoC score)
  4. If multi-model pipeline:
     → Plan execution graph
     → Assign each step to optimal miner
     → Coordinate sequential/parallel execution
  5. If cost-optimized batch:
     → Dutch auction: broadcast to eligible miners, collect bids
     → Accept lowest bid meeting constraints
     → Batch multiple intents for efficiency
```

**Why not a full solver network**:
- Solver economics are thin for AI inference (simple matching vs complex DeFi routing)
- Centralization risk is high — 2-3 solvers would dominate
- Latency overhead of gossip/competition hurts real-time use cases
- A protocol-level matchmaker avoids rent extraction

### 5.5 Dutch Auction for Non-Urgent Inference

Borrow from UniswapX/CoW Protocol for cost-optimized jobs:

```
1. User submits intent: "Run 100 embeddings, max $0.50 total, deadline 10 minutes"
2. Price starts at user's max ($0.50) and decays over time
3. Miners see the decaying price and bid when profitable
4. First miner to accept wins the batch
5. Result: user pays less than max; miner earns above minimum
```

**Batch window**: Group similar intents into 30-second windows (CoW-style) for batch efficiency.

---

## 6. Composable Intent Pipelines

The highest-value use case for intents in QFC — multi-step AI pipelines:

### 6.1 Example: Sentiment-Based Trading Agent

```
Intent Pipeline:
  Step 1: "Fetch latest 100 tweets mentioning $TOKEN"
          → External data oracle
  Step 2: "Run sentiment analysis on each tweet"
          → QFC embedding model + classification
  Step 3: "If avg sentiment > 0.7, generate buy signal"
          → QFC LLM generates structured output
  Step 4: "Execute trade on DEX if buy signal"
          → Cross-VM call to EVM DeFi protocol

Constraints: total cost ≤ 5 QFC, total latency ≤ 60 seconds
```

### 6.2 Example: Content Moderation Pipeline

```
Intent Pipeline:
  Step 1: "Classify image content"
          → QFC image classification model
  Step 2: "If NSFW confidence > 0.9, flag and stop"
          → Conditional routing
  Step 3: "If safe, generate alt-text description"
          → QFC LLM text generation
  Step 4: "Embed description for search index"
          → QFC embedding model

Constraints: accuracy ≥ 95%, cost ≤ 2 QFC
```

These pipelines are hard to express imperatively but natural as intent chains.

---

## 7. Comparison: Transaction-Centric vs Intent-Centric

| Property | Transaction-Centric (Current) | Intent-Centric (Proposed Extension) |
|----------|------------------------------|-------------------------------------|
| User specifies | Exact steps to execute | Desired outcome + constraints |
| Execution path | Fixed by user | Optimized by matchmaker/solver |
| Pricing | User sets exact fee | Dutch auction / competitive bidding |
| Composability | Manual multi-tx coordination | Declarative pipeline chains |
| Latency | Minimal overhead | Additional matching step |
| Complexity | Simple | Higher (matchmaker logic) |
| Best for | Real-time, simple requests | Batch, complex, cost-sensitive jobs |

---

## 8. Implementation Roadmap

### Phase 1: Intent Data Structures (2-3 weeks)

| Task | Description |
|------|-------------|
| `InferenceIntent` resource | Define intent structure with constraints |
| Intent submission API | RPC endpoints for creating/querying intents |
| Intent lifecycle | Create → match → execute → settle → complete/expire |

### Phase 2: Lightweight Matchmaker (3-4 weeks)

| Task | Description |
|------|-------------|
| Constraint evaluator | Filter miners by intent constraints |
| Matching algorithm | PoC-weighted matching for single intents |
| Dutch auction | Price discovery for batch/non-urgent intents |
| Batch window | Group similar intents for efficiency |

### Phase 3: Composable Pipelines (4-6 weeks)

| Task | Description |
|------|-------------|
| Pipeline definition | Chain intents with conditional routing |
| Pipeline executor | Coordinate multi-step execution across miners |
| Error handling | Partial completion, rollback, retry logic |
| SDK support | qfc-sdk-js/python pipeline builder API |

### Phase 4: Cross-Chain Intents (4-6 weeks)

| Task | Description |
|------|-------------|
| ERC-7683 compatibility | Standardized cross-chain intent format |
| Cross-chain intent receiver | Accept intents from external chains (via doc #25 oracle) |
| Settlement | Cross-chain payment and result delivery |

---

## 9. Key Takeaways

1. **Adopt the pattern, not the platform** — QFC doesn't need Anoma's full OS. The intent/solver pattern as a protocol extension is sufficient
2. **Two-path design** — Direct mode (fast, simple) + Intent mode (optimized, complex). Users choose based on their needs
3. **Lightweight matchmaker over full solver network** — Avoids centralization risk and rent extraction; AI inference matching is simpler than DeFi routing
4. **Composable pipelines are the killer feature** — Multi-step AI workflows expressed declaratively are genuinely better than imperative coordination
5. **Dutch auction for non-urgent jobs** — Proven pattern (UniswapX, CoW) that delivers cost savings through competitive bidding
6. **Solver centralization is the biggest risk** — Every deployed solver network shows power concentration. Protocol-level matchmaking mitigates this

---

## References

- [Anoma: Introduction to Intents](https://anoma.net/blog/an-introduction-to-intents-and-intent-centric-architectures)
- [Anoma Roadmap to Mainnet](https://anoma.net/blog/anomas-roadmap-to-mainnet)
- [Anoma Whitepaper (GitHub)](https://github.com/anoma/whitepaper/blob/main/whitepaper.md)
- [Anoma Intent Gossip and Matchmaking](https://anoma.net/blog/intent-gossip-and-matchmaking-system/)
- [Namada Documentation — MASP](https://docs.namada.net/users/shielded-accounts)
- [Essential: Introducing Essential](https://blog.essential.builders/introducing-essential/)
- [Essential: The First Declarative Blockchain](https://blog.essential.builders/essential-the-first-declarative-blockchain/)
- [CoW Protocol](https://cow.fi/cow-protocol)
- [CoW Protocol Batch Auctions Explained](https://metalamp.io/magazine/article/cow-protocol-batch-auctions)
- [UniswapX Dutch Auctions](https://blog.uniswap.org/how-dutch-auctions-deliver-better-swaps)
- [UniswapX Overview (Uniswap Docs)](https://docs.uniswap.org/contracts/uniswapx/overview)
- [1inch Fusion Deep Dive](https://blog.1inch.com/a-deep-dive-into-1inch-fusion/)
- [Across Protocol Intent Architecture](https://docs.across.to/concepts/intents-architecture-in-across)
- [ERC-7683 Specification](https://www.erc7683.org/spec)
- [ERC-7683 EIP](https://eips.ethereum.org/EIPS/eip-7683)
- [Paradigm: Intent-Based Architecture and Their Risks](https://www.paradigm.xyz/2023/06/intents)
- [Halborn: Intent-Centric Blockchain](https://www.halborn.com/blog/post/intent-centric-blockchain-are-intents-the-next-big-thing-in-web3)
- [ESMA MEV Risk Analysis 2025](https://www.esma.europa.eu/sites/default/files/2025-07/ESMA50-481369926-29744)
