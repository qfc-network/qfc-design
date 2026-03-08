# Cross-Chain AI Oracle & Interoperability for QFC

> Last Updated: 2026-03-08 | Version 1.0
> GitHub Issue: #7
> Author: Alex Wei, Product Manager @ QFC Network

---

## 1. Executive Summary

QFC runs verified AI inference on-chain. To maximize utility, inference results should be consumable by smart contracts on any chain. This report evaluates cross-chain messaging protocols and AI oracle patterns to design QFC's cross-chain AI oracle architecture.

**Key Findings:**

- **LayerZero V2** (160+ chains) and **Hyperlane** (150+ chains, permissionless) are the best fits — both allow custom verification modules (DVN/ISM) that QFC can tailor for AI inference attestation
- **Wormhole** requires Guardian network support (harder to integrate); **IBC** is trust-minimized but Cosmos-coupled
- **ORA Protocol** pioneered on-chain AI oracles via opML fraud proofs — supports 7B+ models with near-zero happy-path overhead
- **Ritual Infernet** has 8,000+ nodes running AI workloads in Docker containers — broadest compute flexibility
- The **coprocessor pattern** (read → compute off-chain → prove → verify on-chain) is the emerging standard for cross-chain AI

**Recommendation**: Implement QFC as a **cross-chain AI coprocessor** using Hyperlane or LayerZero for message delivery, with a custom verification module that attests to QFC's inference verification (validator consensus + opML escalation).

---

## 2. Cross-Chain Messaging Protocols

### 2.1 LayerZero V2

**Architecture**: Immutable, censorship-resistant messaging protocol with application-owned security.

| Component | Role |
|-----------|------|
| **Endpoints** | Entry/exit points deployed on every supported chain |
| **Ultra-Light Nodes (ULN)** | On-chain contracts that verify tx proofs without storing full block data |
| **DVNs (Decentralized Verifier Networks)** | Replace old Oracle+Relayer; verify `payloadHash` independently |
| **Executors** | Handle message delivery on destination chain |

**Message Flow**:
1. Source app sends message through Endpoint → emits `payloadHash`
2. Configured DVNs independently verify the payload hash
3. Once DVN threshold met → message nonce committed as "Verified" on destination
4. Executor delivers message to receiving application

**Key Properties**:
- **Permissionless DVNs**: Anyone can build a DVN with any verification schema (multisig, ZK, optimistic, light client)
- **Application-owned security**: Each app configures its own DVN stack
- **Hot-swappable**: Apps can replace DVNs (e.g., multisig → zkOracle) without code changes
- **160+ chains** supported

**QFC Relevance**: QFC could build a custom DVN that attests to AI inference results. No approval needed from LayerZero to integrate.

### 2.2 Hyperlane

**Architecture**: Fully permissionless interoperability — any chain can connect without approval.

| Component | Role |
|-----------|------|
| **Mailbox** | Entry/exit point on each chain (like LayerZero Endpoints) |
| **ISMs (Interchain Security Modules)** | Customizable smart contracts that verify message authenticity |
| **Validators** | Sign attestations of messages from source chain |
| **Relayers** | Deliver messages + metadata to destination chain |

**ISM Options**:

| ISM Type | Description |
|----------|-------------|
| Multisig ISM | N-of-M validator signatures |
| Optimistic ISM | Assume valid unless challenged |
| ZK Light Client ISM | Cryptographic verification via ZK proofs |
| Routing ISM | Different ISMs per source chain |
| Custom ISM | Any arbitrary verification logic |

**Key Properties**:
- **Permissionless deployment**: Deploy to any EVM, Sealevel (Solana), CosmWasm, or Move chain
- **No whitelisting** or governance vote needed
- **Multi-VM support**: EVM, Solana, CosmWasm, Move, Fuel VM
- **150+ chains**

**QFC Relevance**: Arguably the best fit. QFC could deploy Hyperlane contracts, build a custom ISM that verifies AI inference proofs, and immediately be accessible from any Hyperlane-connected chain.

### 2.3 Wormhole

**Architecture**: Guardian Network of 19 independent institutional node operators.

| Component | Role |
|-----------|------|
| **Guardians** | 19 independent validators (Jump Crypto, Certus One, etc.) |
| **VAA (Verified Action Approval)** | Signed attestation requiring 13/19 guardian signatures |
| **Core Bridge** | Contracts on each chain that emit/verify VAAs |
| **NTT (Native Token Transfers)** | Token transfers without liquidity pools |

**Properties**: Fixed guardian set is simpler but less flexible. 2025 optimizations cut latency ~40%. Strong Solana support.

**QFC Relevance**: VAA pattern is instructive — QFC inference results could be packaged similarly as signed attestations. But fixed guardian set makes custom integration harder.

### 2.4 IBC (Inter-Blockchain Communication)

**Architecture**: Light client-based verification — the gold standard for trust-minimized interoperability.

| Layer | Components |
|-------|------------|
| Transport (TAO) | Light Clients, Connections, Channels, Relayers |
| Application | Token transfers (ICS-20), Interchain Accounts (ICS-27) |

**How verification works**:
- Each chain maintains an on-chain light client of its counterparty
- Light client tracks consensus state (validator set, block headers)
- Relayers submit packets + Merkle proofs → verified against light client
- **Zero additional trust assumption** — purely cryptographic

**IBC v2 (2025)**: Aims to bring IBC beyond Cosmos to any chain.

**QFC Relevance**: Most trust-minimized option. If QFC implements deterministic finality (e.g., Mysticeti-variant consensus from doc #21), it could natively support IBC. High implementation cost but highest security.

### 2.5 Chainlink CCIP

**Architecture**: Cross-chain messaging secured by Chainlink's OCR 2.0 oracle infrastructure + independent Risk Management Network.

| Property | Value |
|----------|-------|
| Chain coverage | 60+ |
| Security model | DON consensus + Risk Management Network |
| Total value secured | $93B+ (mid-2025) |
| Integration | Requires Chainlink partnership |

**QFC Relevance**: Demonstrates the value of DON-based aggregation. QFC could position as a specialized AI compute DON — unlike Chainlink Functions (which calls external APIs), QFC runs inference natively with cryptographic/economic proofs.

---

## 3. Protocol Comparison

| Protocol | Chains | Trust Model | Custom Verification | Integration Effort | Best For |
|----------|--------|-------------|--------------------|--------------------|----------|
| **LayerZero** | 160+ | Application-configurable (DVN) | ✅ Custom DVN | Medium | Broadest EVM reach |
| **Hyperlane** | 150+ | Application-configurable (ISM) | ✅ Custom ISM | Medium | Permissionless, multi-VM |
| **Wormhole** | 30+ | 13/19 Guardians | ❌ Fixed guardian set | High | Solana ecosystem |
| **IBC** | Cosmos ecosystem | Cryptographic (light client) | ⚠️ Requires compatible consensus | Very High | Highest security |
| **Chainlink CCIP** | 60+ | DON + Risk Network | ❌ Requires partnership | High | Enterprise/institutional |

**Recommendation**: **Hyperlane** (primary) or **LayerZero** (alternative). Both allow custom verification modules without permission, and QFC can build an AI-specific verifier.

---

## 4. AI Oracle Landscape

### 4.1 ORA Protocol (OAO — Onchain AI Oracle)

**Approach**: opML (Optimistic Machine Learning) — interactive fraud proofs inspired by optimistic rollups.

| Property | Value |
|----------|-------|
| Max model size | 7B+ on consumer hardware (32GB RAM) |
| Happy-path overhead | ~0x (no proof generation unless challenged) |
| Challenge period | Minutes |
| Security model | Economic (staking + fraud proofs) |
| Deployed on | Ethereum, Arbitrum, other EVM chains |
| Models supported | LLaMA 3, Stable Diffusion |

**How it works**:
1. AI inference runs off-chain → result posted on-chain optimistically
2. Challenge window opens
3. If challenged → step-by-step re-execution via fraud proof VM
4. Challenger or prover forfeits stake

**2025 updates**: "Resilient Model Services" and "opAgent" for verifiable AI agents.

### 4.2 Ritual Infernet

**Architecture**: Off-chain Infernet Nodes execute AI workloads in Docker containers. On-chain SDK provides `CallbackConsumer` and `SubscriptionConsumer` interfaces.

| Property | Value |
|----------|-------|
| Node count | 8,000+ independent nodes |
| Compute model | Any Docker container (any model, any framework) |
| Delivery | One-time callbacks or recurring subscriptions |
| Chain | Ritual Chain (trustless execution layer) |
| Verification | Maturing (less mature than ORA) |

### 4.3 Verification Approaches Compared

| Approach | Security | Latency | Cost | Model Size |
|----------|----------|---------|------|------------|
| **zkML** | Cryptographic (highest) | Minutes–hours (large models) | Very high | <1B practical |
| **opML** | Economic (fraud proof) | Challenge period (minutes) | Low | 7B+ feasible |
| **TEE** | Hardware trust | Near-native speed | Low | Limited by enclave memory |
| **Multisig/Committee** | Honest majority | Fast | Low | Unlimited |
| **QFC tiered** (doc #20) | Adaptive | Varies by tier | Varies | Unlimited |

---

## 5. The Coprocessor Pattern

The emerging standard for cross-chain verifiable compute:

```
Read on-chain state → Compute off-chain → Prove correctness → Verify on-chain
```

### 5.1 ZK Coprocessor Projects

| Project | Approach | Key Benchmark |
|---------|----------|---------------|
| **Axiom** | Read historical Ethereum state + ZK proofs | Production on Ethereum |
| **Brevis** | zkVM-based coprocessor | 6.9s avg latency for 45M gas block proving |
| **Lagrange** | ZK coprocessor + DeepProve (zkML prover) | Fastest zkML prover |
| **Giza** | Per-inference ZK proofs on StarkNet | Small model focus |

### 5.2 QFC as AI Coprocessor

QFC is already a native AI coprocessor. The key question: how to package inference results for cross-chain consumption.

```
[Requesting Chain]              [QFC Chain]                    [Requesting Chain]

Smart Contract  ─LayerZero/→  QFC Endpoint Contract      Result + Proof
(inference req)  Hyperlane    ├─ Decode request            ─LayerZero/→  Callback
                              ├─ Route to miner pool        Hyperlane     Contract
                              ├─ Miners execute inference                 (verified
                              ├─ Consensus on result                      result)
                              ├─ Generate attestation
                              └─ Emit cross-chain message
```

---

## 6. QFC Cross-Chain AI Oracle Design

### 6.1 Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│  External Chains (Ethereum, Arbitrum, Solana, etc.)       │
│  ┌────────────────────┐  ┌────────────────────────────┐  │
│  │ Requesting Contract│  │ QFC Oracle Receiver Contract│  │
│  │ - submitRequest()  │  │ - receiveResult()           │  │
│  │ - callback handler │  │ - verify attestation        │  │
│  └────────┬───────────┘  └────────────▲───────────────┘  │
│           │                           │                    │
├───────────┼───────────────────────────┼────────────────────┤
│  Cross-Chain Layer (Hyperlane/LayerZero)                   │
│  ┌────────┴───────────────────────────┴───────────────┐   │
│  │  Custom ISM/DVN: QFC Inference Verifier             │   │
│  │  - Verify validator signatures on inference result  │   │
│  │  - Optional: verify opML fraud proof                │   │
│  │  - Optional: verify ZK proof (Tier 1 models)       │   │
│  └────────────────────────┬───────────────────────────┘   │
├───────────────────────────┼────────────────────────────────┤
│  QFC Chain                │                                │
│  ┌────────────────────────┴───────────────────────────┐   │
│  │  Cross-Chain Oracle Coordinator                     │   │
│  │  ├─ Receive cross-chain inference requests          │   │
│  │  ├─ Route to AI Coordinator (existing TaskPool)     │   │
│  │  ├─ Collect verified results                        │   │
│  │  ├─ Generate attestation (validator consensus)      │   │
│  │  └─ Emit cross-chain response                       │   │
│  └─────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────┘
```

### 6.2 Verification Strategy (Hybrid)

Mirrors QFC's tiered verification (doc #20) but adapted for cross-chain attestation:

| Path | Trigger | Verification | Latency |
|------|---------|-------------|---------|
| **Fast path** (default) | Standard request | Validator consensus with staked collateral | Seconds + cross-chain messaging |
| **Challenge path** | Disputed result | opML fraud proof or re-execution | Minutes |
| **ZK path** | High-value / Tier 1 models | Full ZK proof attached to result | Seconds (small models) |
| **TEE path** | Privacy-sensitive | TEE attestation (see doc #19) | Near-instant |

### 6.3 Cross-Chain Message Format

```solidity
struct AIInferenceResult {
    bytes32 requestId;        // Unique cross-chain request ID
    bytes32 modelHash;        // Hash of model used
    bytes32 inputHash;        // Hash of inference input
    bytes outputData;         // Result (or IPFS CID for large results >1MB)
    uint8 verificationTier;   // 1=ZK, 2=OpZK, 3=SpotCheck
    bytes attestation;        // Validator signatures or ZK proof
    uint64 timestamp;         // When inference was completed
    uint64 qfcBlockNumber;    // QFC block containing the result
}
```

### 6.4 Custom ISM/DVN Implementation

For Hyperlane (ISM):

```solidity
contract QFCInferenceISM is IInterchainSecurityModule {
    // QFC validator set (mirrors on-chain validator registry)
    mapping(address => uint256) public validatorStakes;
    uint256 public requiredSignatures;  // e.g., 2/3 of staked weight

    function verify(
        bytes calldata metadata,
        bytes calldata message
    ) external view returns (bool) {
        // Decode attestation from metadata
        (address[] memory signers, bytes[] memory signatures) =
            abi.decode(metadata, (address[], bytes[]));

        // Verify sufficient stake-weighted signatures
        uint256 totalStake = 0;
        bytes32 messageHash = keccak256(message);

        for (uint i = 0; i < signers.length; i++) {
            require(
                _verifySignature(messageHash, signers[i], signatures[i]),
                "Invalid signature"
            );
            totalStake += validatorStakes[signers[i]];
        }

        return totalStake >= requiredSignatures;
    }
}
```

For LayerZero (DVN): Similar logic wrapped in LayerZero's `ILayerZeroDVN` interface.

### 6.5 Request Flow (End-to-End)

```
1. External chain: User/contract calls QFCOracle.requestInference(model, input, callback)
   - Pays fee in native token or USDC
   - Cross-chain message sent via Hyperlane/LayerZero

2. QFC chain: Cross-Chain Oracle Coordinator receives request
   - Decodes model ID, input data
   - Submits task to existing AI Coordinator (TaskPool)
   - Miner assigned, executes inference

3. QFC chain: Result verified per tiered strategy
   - Tier 1 (small models): ZK proof generated
   - Tier 2 (medium): Optimistic with challenge window
   - Tier 3 (large): Spot-check + validator consensus

4. QFC chain: Attestation generated
   - ≥2/3 stake-weighted validator signatures on result
   - Cross-chain response emitted via Hyperlane/LayerZero

5. External chain: QFC ISM/DVN verifies attestation
   - Callback delivered to requesting contract
   - Result available for on-chain use
```

### 6.6 Latency Budget

| Step | Estimated Time |
|------|---------------|
| Cross-chain request delivery | 1–15 minutes (depends on source chain finality) |
| Task assignment + inference | 1–30 seconds |
| Verification (Tier 1 ZK) | 1–30 seconds |
| Verification (Tier 2 optimistic) | 10–30 minutes (challenge window) |
| Verification (Tier 3 spot-check) | 1–5 seconds |
| Attestation collection | 5–15 seconds |
| Cross-chain result delivery | 1–15 minutes |
| **Total (fast path)** | **2–30 minutes** |

### 6.7 Gas Cost Estimates

| Operation | Estimated Gas | USD (at 30 gwei) |
|-----------|--------------|-------------------|
| Post inference result on destination | 50K–200K | $0.10–0.40 |
| Verify multisig attestation | 50K–100K | $0.10–0.20 |
| Verify ZK proof (if attached) | 200K–500K | $0.40–1.00 |
| Cross-chain message overhead | 100K–300K | $0.20–0.60 |
| **Total per cross-chain inference** | **200K–800K** | **$0.40–1.60** |

On L2s (Arbitrum, Optimism): 10–100x cheaper.

---

## 7. Competitive Positioning

| Feature | ORA (OAO) | Ritual | Chainlink Functions | Bittensor | **QFC Oracle** |
|---------|-----------|--------|-------------------|-----------|---------------|
| Native inference | ❌ Off-chain | ❌ Docker containers | ❌ API calls | ❌ Off-chain subnets | **✅ On-chain verified** |
| Verification | opML fraud proof | Maturing | DON consensus | Subjective scoring | **Tiered (ZK/opML/spot-check)** |
| Cross-chain | EVM only | Ritual Chain | CCIP (60+ chains) | ❌ | **Hyperlane/LZ (150+)** |
| Model size | 7B+ | Unlimited | API-limited | Unlimited | **Unlimited (tiered)** |
| Decentralization | Economic (staking) | 8K+ nodes | Chainlink DON | 32K+ miners | **PoC validators** |
| Custom models | Limited | ✅ Any Docker | ❌ External APIs | Subnet-specific | **✅ On-chain registry** |

**QFC's unique value**: The only cross-chain AI oracle where inference is a **native blockchain operation** with **tiered cryptographic/economic verification** — not an API call or off-chain Docker execution.

---

## 8. Implementation Roadmap

### Phase 1: Cross-Chain Messaging Integration (4-6 weeks)

| Task | Description |
|------|-------------|
| Evaluate Hyperlane vs LayerZero | Deploy test contracts on both, benchmark fees/latency |
| Deploy Mailbox/Endpoint on QFC | Cross-chain messaging entry point |
| Custom ISM/DVN | QFC validator attestation verifier |
| Message format | Standardize `AIInferenceResult` structure |

### Phase 2: Oracle Coordinator (4-6 weeks)

| Task | Description |
|------|-------------|
| Cross-Chain Oracle Coordinator | Receive requests, route to AI Coordinator, emit responses |
| Fee management | Accept cross-chain payments (native/USDC → QFC conversion) |
| Request/response tracking | On-chain state for pending cross-chain requests |
| Timeout handling | Auto-refund if inference not completed within deadline |

### Phase 3: Destination Chain Contracts (3-4 weeks)

| Task | Description |
|------|-------------|
| QFCOracle.sol | Solidity contract for requesting inference from any EVM chain |
| Callback interface | Standard interface for receiving inference results |
| Example integrations | DeFi protocol using QFC AI oracle (e.g., sentiment-based trading) |
| SDK support | qfc-sdk-js/python for cross-chain inference requests |

### Phase 4: Advanced Features (4-6 weeks)

| Task | Description |
|------|-------------|
| Subscription model | Recurring inference (e.g., hourly sentiment updates) |
| Result caching | Cache frequently-requested inferences, serve from cache cross-chain |
| Multi-chain deployment | Deploy receiver contracts on Ethereum, Arbitrum, Base, Solana |
| Dashboard | Explorer shows cross-chain request status and latency |

---

## 9. Key Design Decisions

### 9.1 Why Hyperlane Over LayerZero?

Both are strong candidates. Hyperlane has slight advantages:
- **Permissionless**: No approval needed to deploy on QFC or any destination chain
- **Multi-VM**: Native support for Move (QVM compatible), not just EVM
- **ISM flexibility**: Custom ISM is more composable than custom DVN
- **Open source**: Fully open-source codebase

LayerZero advantages: larger chain coverage (160 vs 150), more battle-tested in production.

**Decision**: Start with Hyperlane for permissionless deployment speed. Add LayerZero as second option for broader reach.

### 9.2 Why Not Build a Native Bridge?

Custom bridges are:
- Expensive to build and maintain (6+ months of security engineering)
- Each destination chain requires custom integration
- Security responsibility falls entirely on QFC team

Using Hyperlane/LayerZero:
- Instant access to 150+ chains
- Security shared with established protocols
- Custom verification still possible via ISM/DVN

### 9.3 Large Result Handling

For inference results >1MB (e.g., image generation):
- Post output to IPFS (existing QFC mechanism)
- Cross-chain message contains only CID + proof hash
- Destination contract can verify CID against proof
- Requesting app fetches full result from IPFS using CID

This keeps cross-chain gas costs low regardless of output size.

---

## References

- [LayerZero V2 Deep Dive](https://medium.com/layerzero-official/layerzero-v2-deep-dive-869f93e09850)
- [LayerZero V2 Whitepaper](https://layerzero.network/publications/LayerZero_Whitepaper_V2.1.1.pdf)
- [LayerZero DVN Documentation](https://layerzero.network/blog/layerzero-v2-explaining-dvns)
- [Hyperlane — Permissionless Interoperability](https://medium.com/hyperlane/permissionless-interoperability-3ae02fc162de)
- [Hyperlane Documentation](https://docs.hyperlane.xyz/docs/intro)
- [Hyperlane Modular Security](https://hyperlane.xyz/post/modular-security-with-hyperlane)
- [Wormhole NTT Architecture](https://wormhole.com/docs/products/token-transfers/native-token-transfers/concepts/architecture/)
- [Understanding Wormhole — Messari](https://messari.io/report/understanding-wormhole)
- [IBC Protocol — How It Works](https://ibcprotocol.dev/how-ibc-works)
- [IBC v2 Announcement](https://ibcprotocol.dev/blog/ibc-v2-announcement)
- [Chainlink CCIP Documentation](https://docs.chain.link/ccip)
- [Chainlink Functions Documentation](https://docs.chain.link/chainlink-functions)
- [ORA Onchain AI Oracle](https://docs.ora.io/doc/onchain-ai-oracle-oao/onchain-ai-oracle)
- [opML Paper (arXiv)](https://arxiv.org/html/2401.17555v1)
- [Ritual Infernet SDK](https://github.com/ritual-net/infernet-sdk)
- [Ritual Architecture](https://ritual.academy/ritual/architecture/)
- [Lagrange ZK Coprocessor](https://lagrange.dev/zk-coprocessor)
- [Brevis ZK Coprocessor](https://medium.com/@0xjacobzhao/brevis-research-report)
- [Blockchain Interoperability 2025](https://lampros.tech/blogs/best-blockchain-interoperability-protocols-2025)
