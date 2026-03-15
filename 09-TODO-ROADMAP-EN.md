# QFC Blockchain - TODO & Roadmap

> Last Updated: 2026-03-08

## Project Status Overview

| Project | Repository | Tech Stack | Status | Completion |
|---------|-----------|------------|--------|------------|
| Core Engine | `qfc-core` | Rust + libp2p | ✅ Production Ready | 95% |
| AI Inference Engine | `qfc-core/qfc-inference` | Rust + candle | ✅ Production Ready | 95% |
| AI Task Coordination | `qfc-core/qfc-ai-coordinator` | Rust | ✅ Production Ready | 95% |
| Standalone Miner | `qfc-core/qfc-miner` | Rust + clap | ✅ Production Ready | 95% |
| Browser Wallet | `qfc-wallet` | React + TypeScript | ✅ Feature Complete | 95% |
| Block Explorer | `qfc-explorer` | Next.js + PostgreSQL | ✅ Feature Complete | 95% |
| JavaScript SDK | `qfc-sdk-js` | TypeScript + ethers.js | ✅ Done | 90% |
| Testnet Faucet | `qfc-faucet` | Next.js | ✅ Available | 85% |
| **Testnet Infrastructure** | `qfc-testnet` | Docker + K8s + Terraform | ✅ Done | 90% |
| **Developer Docs Site** | `qfc-docs` | VitePress | ✅ Done | 85% |
| **Python SDK** | `qfc-sdk-python` | Python + web3.py + pydantic | ✅ Done | 90% |
| **CLI Tools** | `qfc-cli` | Node.js + commander | ✅ Done | 90% |
| **Smart Contract Library** | `qfc-contracts` | Solidity + Hardhat | ✅ Done | 90% |
| **Mobile Wallet** | `qfc-wallet-mobile` | React Native + Expo | ✅ Done | 85% |
| **OpenClaw Skill** | `qfc-openclaw-skill` | TypeScript + ethers.js | ✅ Done | 80% |

---

## High Priority Tasks

### 1. ~~Testnet Deployment Infrastructure~~ ✅ Done

**Goal**: Set up a publicly accessible testnet environment

**Repository**: `qfc-testnet/` - https://github.com/qfc-network/qfc-testnet

**Completed Items**:

- [x] Docker Compose Configuration
  - [x] Multi-node (5 validators) local test configuration
  - [x] Single-node development configuration
  - [x] Full stack with Explorer, Faucet, and RPC
  - [x] Nginx load balancing configuration

- [x] Kubernetes Deployment
  - [x] Helm Charts
  - [x] StatefulSet configuration (node persistence)
  - [x] Service and Ingress configuration

- [x] Terraform Cloud Deployment
  - [x] AWS configuration (EKS + RDS + ElastiCache)
  - [x] GCP configuration (GKE + Cloud SQL + Memorystore)
  - [x] VPC modules

- [x] Monitoring System
  - [x] Prometheus metrics collection
  - [x] Grafana dashboards
  - [x] AlertManager alerting rules

- [ ] CI/CD Pipeline (to be completed)
  - [ ] GitHub Actions automated deployment
  - [ ] Release workflow

**Completed**: 2026-02-02

---

### 2. Unit Tests & Integration Tests

**Goal**: Ensure code quality and stability with >80% test coverage

**Task List**:

#### qfc-sdk-js ✅ Done (2026-02-02)
- [x] Provider Tests
  - [x] RPC method call tests (getValidators, getEpoch, getNetworkStats, etc.)
  - [x] Error handling tests
  - [x] Network switching tests
- [x] Wallet Tests
  - [x] Create/import tests (private key, mnemonic)
  - [x] Signing tests (signMessage, signTypedData)
  - [x] Staking method existence tests
- [x] Utils Tests
  - [x] Unit conversion tests (parseQfc, formatQfc, parseGwei)
  - [x] Validation function tests (isValidAddress, isValidMnemonic, isValidPrivateKey)
  - [x] Encoding function tests (encodeFunctionData, keccak256, abiEncode/Decode)
  - [x] Formatting function tests (shortenAddress, formatRelativeTime)
- [x] Contract Tests
  - [x] ERC-20/721/1155 interface tests
  - [x] Multicall3 tests
  - [x] isContract tests
- [x] Constants Tests
  - [x] Network configuration tests
  - [x] Gas limit tests
  - [x] Contract address tests

**Test Statistics**: 9 test files, 181 test cases all passing (including 7 inference tests)

#### qfc-wallet ✅ Done (2026-02-02)
- [x] Encryption module tests (encrypt/decrypt, hashPassword, generatePassword)
- [x] Validation function tests (isValidAddress, isValidMnemonic, isValidPrivateKey, validatePassword)
- [x] Storage module tests (walletStorage, txStorage, tokenStorage, networkStorage)
- [x] Constants tests (NETWORKS, STORAGE_KEYS, MESSAGE_TYPES)
- [x] Price utility tests (getTokenPrice, calculateUsdValue, formatUsd)
- [x] WalletController Tests
  - [x] Wallet creation/import
  - [x] Lock/unlock
  - [x] Account management
  - [x] Balance queries
  - [x] Message signing
  - [x] Network switching

**Test Statistics**: 6 test files, 144 test cases all passing

#### qfc-core ✅ Unit Tests Done (2026-02-03)
- [x] Core module unit tests (258 test cases)
  - [x] qfc-types: 23 tests (blocks, transactions, accounts, receipts, validators)
  - [x] qfc-crypto: 25 tests (hashing, signatures, VRF)
  - [x] qfc-storage: 34 tests (RocksDB storage layer)
  - [x] qfc-trie: 61 tests (Merkle Patricia Trie)
  - [x] qfc-state: 5 tests (state management)
  - [x] qfc-executor: 4 tests (transaction execution)
  - [x] qfc-mempool: 6 tests (transaction pool)
  - [x] qfc-consensus: 15 tests (PoC consensus)
  - [x] qfc-chain: 6 tests (chain management)
  - [x] qfc-network: 16 tests (P2P network, sync protocol)
  - [x] qfc-rpc: 14 tests (JSON-RPC types)
  - [x] qfc-snap-sync: 22 tests (snapshot sync)
  - [x] qfc-state-pruner: 8 tests (state pruning)
  - [x] qfc-node: 19 tests (node main program)
- [ ] Advanced Tests (to be completed)
  - [ ] Stress tests / benchmarks
  - [ ] Network partition tests
  - [ ] Multi-node integration tests

**Test Statistics**: 14 test modules, 258 unit tests all passing

---

### 3. ~~Developer Documentation Site~~ ✅ Done

**Goal**: Provide comprehensive developer documentation for third-party integration

**Repository**: `qfc-docs/` - https://github.com/qfc-network/qfc-docs

**Tech Stack**: VitePress 1.0

**Completed Items**:

- [x] VitePress Framework Setup
  - [x] Full navigation configuration (top + sidebar)
  - [x] Homepage hero section
  - [x] Responsive layout

- [x] Getting Started Guide
  - [x] QFC Introduction
  - [x] 5-Minute Quick Start
  - [x] Installation Guide

- [x] Core Concepts
  - [x] Blockchain Basics (blocks, transactions, accounts, state)
  - [x] PoC Consensus Mechanism

- [x] JavaScript SDK Documentation
  - [x] SDK Overview
  - [x] Provider (RPC methods)
  - [x] Wallet (signing & staking)
  - [x] Contract Helpers (ERC-20/721/1155, Multicall)
  - [x] Utility Functions (unit conversion, validation, encoding)

- [x] API Reference
  - [x] Standard JSON-RPC methods
  - [x] QFC-specific methods (validators, staking, contribution scores)

- [x] Tutorials
  - [x] Complete DApp Building Tutorial

- [ ] Content to be Completed (optional)
  - [ ] Smart Contract Development Guide
  - [ ] Validator Operation Guide
  - [ ] More tutorials (token creation, NFT deployment)
  - [ ] Python SDK Documentation (pending SDK development)

**Completed**: 2026-02-02

---

### 11. ~~v2.0 AI Compute Network~~ ✅ Done

**Goal**: Replace Blake3 PoW with real AI inference tasks, giving economic value to the 20% compute contribution dimension of PoC scoring

**Design Documents**: `13-AI-COMPUTE-NETWORK.md`, `14-OPENCLAW-INTEGRATION.md`

**Branch**: `v2.0` (integration branch) ← `v2.0-inference-runtime` (merged)

#### Phase 1: Inference Runtime ✅ Done (2026-03-05)

New crate: `qfc-inference`

- [x] `InferenceEngine` trait (async, Send + Sync)
  - [x] `run_inference()`, `load_model()`, `benchmark()`
  - [x] `BackendType` enum (Cuda / Metal / Cpu)
- [x] CPU backend (deterministic placeholder, blake3 chained hash)
- [x] CUDA backend (scaffold, nvidia-smi detection)
- [x] Metal backend (scaffold, sysctl Apple Silicon detection)
- [x] `InferenceProof` + `ComputeProof` enum (v1 PoW + v2 AI)
- [x] `ModelRegistry` (benchmark models: small/medium/large)
- [x] GPU tiering (Hot 24GB+ / Warm 8-16GB / Cold CPU)
- [x] Hardware detection (CUDA devices, Apple Silicon, memory)
- [x] 31 unit tests passing

#### Phase 2: Task Coordination ✅ Done (2026-03-05)

New crate: `qfc-ai-coordinator`

- [x] `TaskPool` (task queue, generated per epoch)
- [x] `TaskRequirements` (minimum GPU tier, memory, FLOPS)
- [x] `MinerRegistry` (miner registration, capability matching, timeout cleanup)
- [x] Synthetic benchmark tasks (one per GPU tier)
- [x] Basic verification (`verify_basic` — epoch/model/FLOPS validation)
- [x] Spot-check verification (`should_spot_check` — 5% probability re-execution)
- [x] Full spot-check (`verify_spot_check` — re-run inference, compare output hash)
- [x] 22 unit tests passing

#### Phase 3: Existing Crate Adaptation ✅ Done (2026-03-05)

- [x] `qfc-types` — Added `InferenceProof`, `ComputeProof`, `BackendType`, `ModelId`, `ComputeTaskType`; `ValidatorNode` extended with v2 fields (inference_score, gpu_memory_mb, etc.)
- [x] `qfc-pow` — Added `verify_inference_proof()`, `verify_compute_proof()`
- [x] `qfc-consensus` — v2 scoring: `inference_score = flops_norm * sqrt(tasks) * pass_rate²`; falls back to hashrate when no inference score
- [x] `qfc-node` — Dual-mode `MiningService` (`PowV1` / `InferenceV2`)
- [x] `qfc-rpc` — 3 new endpoints: `getComputeInfo`, `getSupportedModels`, `getInferenceStats`

#### Phase 4: Standalone Miner Program ✅ Done (2026-03-05)

New crate: `qfc-miner` (standalone binary)

- [x] CLI (clap): `--validator-rpc`, `--wallet`, `--private-key`, `--backend auto|cuda|metal|cpu`, `--model-dir`, `--max-memory`
- [x] Hardware detection + benchmarking
- [x] `InferenceWorker` inference loop (10s epoch)
- [x] Proof submission scaffold (RPC)
- [x] Proof signing (`--private-key` → Keypair::sign_hash, validates match with --wallet address on startup)

**Phase 1-4 Statistics**: 3 new crates, 5 modified crates, 3,372 lines of new code, 134 tests passing

**Phase 5-6 Statistics**: candle ML integration + end-to-end inference verification, 316 tests passing (as of Phase 6)

**Phase 7 Statistics**: 3 repositories updated (qfc-core 5 files, qfc-testnet 5 files, qfc-explorer 6 files), 16 new/modified files

#### Phase 5: candle Model Integration ✅ Done (2026-03-04)

- [x] Integrated `candle-core` + `candle-nn` + `candle-transformers`
- [x] CPU backend: Real BERT embedding inference (candle feature flag)
- [x] Metal backend: `candle-core` Metal feature (Apple Silicon)
- [x] Model download and caching (`ModelCache`, `download_model()`)
- [x] Benchmark model: BERT embedding (all-MiniLM-L6-v2 style)
- [x] Deterministic inference verification (blake3 output hash, fixed seed)
- [x] CUDA backend: `Dockerfile.cuda` + `Dockerfile.miner-cuda` (nvidia/cuda:12.2.0, `--features candle,cuda`)

#### Phase 6: End-to-End Integration ✅ Done (2026-03-05)

- [x] Worker → TaskCoordinator → ProofSubmission complete flow
- [x] `qfc-miner` crate: InferenceMiner inference loop + RPC submission
- [x] Miner submits proofs via RPC (`qfc_submitInferenceProof`)
- [x] Inference proof signing + P2P broadcast (ValidatorMessage::InferenceProof)
- [x] Validator node `handle_inference_proof()`:
  - [x] Signature verification + epoch/model/FLOPS basic validation
  - [x] 5% probability spot-check re-execution (`should_spot_check` + `verify_spot_check`)
  - [x] Output hash mismatch → `InvalidInference` penalty (5% stake, 6h jail)
  - [x] Pass → `update_inference_score()`
- [x] CpuEngine integrated into SyncManager for spot-check verification
- [x] CpuEngine integrated into RpcServer for RPC spot-check verification
- [x] RPC `submit_inference_proof` full pipeline: signature verification → verify_basic → 5% spot-check → slash/update_inference_score
- [x] `tasks_completed` accumulation bug fix (saturating_add)
- [x] Spot-check integration tests (test_verify_spot_check_pass, test_verify_spot_check_mismatch)
- [ ] Multi-miner concurrent submission tests
- [ ] Miner fetches tasks via RPC (`qfc_getInferenceTask`)

#### Phase 7: Testnet Deployment ✅ Done (2026-03-05)

- [x] Docker Image Updates
  - [x] Dockerfile builds qfc-node + qfc-miner dual binaries
  - [x] Dockerfile.miner standalone miner image (env vars, /models volume)
  - [x] Entry script supports `--compute-mode`, `--inference-backend`, `--model-dir`
- [x] CLI Extensions: `--compute-mode pow|inference`, `--inference-backend`, `--model-dir`
- [x] RPC Extensions: `RpcValidator` with new inference_score, compute_mode, tasks_completed fields
- [x] Testnet Mixed Mode
  - [x] docker-compose.yml with inference profile (standalone miner)
  - [x] docker-compose.mixed.yml (3 PoW + 2 inference validators + 2 standalone miners)
  - [x] Environment variables: QFC_COMPUTE_MODE, QFC_INFERENCE_BACKEND, MINER_*_WALLET
- [x] Miner Dashboard
  - [x] Grafana qfc-inference dashboard (8 panels: task count, FLOPS, pass rate, miner count)
  - [x] Prometheus inference alerting rules (miner offline, low pass rate, no tasks, FLOPS zero)
  - [x] Explorer /inference page (stats cards, compute info, validator table)
  - [x] Explorer /network page with new Compute Mode + Inference Score columns
  - [x] API: /api/inference route (15s ISR)
  - [x] Formatting: formatFlops(), formatDuration()
- [x] Transition Strategy: deploy-mixed.sh phased deployment script
  - [x] Phase A: All PoW (5 validators)
  - [x] Phase B: Mixed (3 PoW + 2 inference + 2 miners)
  - [x] Phase C: Mostly inference (1 PoW + 4 inference + 2 miners)
  - [x] Phase D: All inference (5 inference + 2 miners)

#### Phase 8: Ecosystem Integration ✅ Done (2026-03-05)

- [x] SDK Updates (JS/Python support for inference-related RPCs)
  - [x] qfc-sdk-js: 8 inference types + 7 Provider methods + 7 tests
  - [x] qfc-sdk-python: 6 Pydantic models + 7 Provider methods + 11 tests
- [x] Model Registry On-chain Governance (validator vote >2/3)
  - [x] ModelGovernance module (propose, vote, tally)
  - [x] ProposalStatus (Active/Passed/Rejected/Expired)
  - [x] Configurable voting period (default 1 day), supermajority >2/3
  - [x] 3 new RPC endpoints: proposeModel, voteModel, getModelProposals
  - [x] 7 governance unit tests
- [x] Public Inference API (paid invocation)
  - [x] PublicTask + PublicTaskStatus (Pending/Assigned/Completed/Failed/Expired)
  - [x] TaskPool extensions: submit_public_task, get_public_task, complete_public_task
  - [x] 2 new RPC endpoints: submitPublicTask, getPublicTaskStatus
- [x] Enhanced Explorer Inference Statistics
  - [x] /inference page with new Model Registry table
  - [x] /governance/models governance page (stats cards + proposal table + approved models)
  - [x] API route: /api/governance/models (15s ISR)
- [x] OpenClaw Skill MVP (new repository qfc-openclaw-skill)
  - [x] QFCWallet class (create/import/balance/transfer/sign)
  - [x] SecurityPolicy class (5 pre-transaction security rules)
  - [x] SKILL.md agent capability description
  - [x] Reference documentation (chain overview + wallet operations guide)

**Phase 8 Statistics**: 5 repositories updated, 31 files added/modified, SDK tests 188 (JS) + 18 (Python), Core 50 tests passing

---

### 12. AI Inference Pipeline: Design vs. Implementation Gap Analysis

> Updated: 2026-03-07

**Design document** `13-AI-COMPUTE-NETWORK.md` covers the complete inference pipeline. The core execution layer (task distribution, inference execution, result verification) is implemented, but the **user entry layer** and **economic settlement layer** still have implementation gaps.

#### Current Status of the 6 Pipeline Stages

| # | Stage | Design | Code | Completion | Key Gap |
|---|-------|--------|------|------------|---------|
| 1 | User submits inference request | ✅ | ✅ | 98% | Wallet/Explorer inference UI integrated; dedicated TX type added |
| 2 | Transaction routed to AI-VM | ✅ | ✅ | 95% | Fee escrow implemented; task routing + priority + timeout reassignment done |
| 3 | GPU node executes inference | ✅ | ✅ | 98% | ModelCache LRU + auto-download + GPU metrics collection done; task parallelism pending |
| 4 | Inference result verification | ✅ | ✅ | 100% | Multi-validator arbitration panel + majority vote + Proof on-chain Merkle verification all done |
| 5 | Result returned to user | ✅ | ✅ | 90% | base64 encoding + WebSocket subscription + SDK done; large result IPFS not integrated |
| 6 | Fee settlement | ✅ | ✅ | 95% | Escrow + 70/10/20 distribution + pricing formula + slashing all done |

#### Stage 1: User Submits Inference Request (90%)

**Implemented:**
- [x] RPC `submitPublicTask` endpoint + Ed25519 signature verification (`qfc-rpc/src/qfc.rs`)
- [x] `PublicTask` + `PublicTaskStatus` state machine (`qfc-ai-coordinator/src/task_pool.rs`)
- [x] Supports 4 task types: TextGeneration / ImageClassification / Embedding / OnnxInference

**To be completed:**
- [x] **Dedicated transaction type**: `TransactionType::InferenceTask = 10` defined (`qfc-types/src/transaction.rs`), executor has handling branch
- [x] **Wallet SDK integration (queries)**: qfc-sdk-js Provider has 7 inference methods + 8 types (Phase 8)
- [ ] **Wallet inference UI**: qfc-wallet inference task submission interface (not started)
- [x] **OpenClaw inference skill**: `QFCInference` class completed — submitTask/getTaskStatus/waitForResult/getModels/getStats/estimateFee/decodeResult (v3.0.2 payload alignment fix)

#### Stage 2: Transaction Routed to AI-VM (95%) ✅

**Implemented:**
- [x] `TaskPool` — Task submission, synthetic task generation (3 per epoch), capability-matched miner assignment
- [x] `TaskRouter` — Hot/Warm/Cold three-tier scheduling, load balancing, 5-minute timeout cleanup
- [x] `TaskRequirements` — GPU tier / VRAM / FLOPS matching
- [x] **Fee escrow implementation**: `submitPublicTask` RPC uses `sub_balance()` to lock fee (Phase A complete)
- [x] **RPC→TaskPool full flow**: submitPublicTask→task_pool→fetch→proof→settle, PublicTask status fully tracked (Phase C1)
- [x] **Task timeout reassignment**: `reassign_stale_tasks()` 30s timeout auto-requeue (Phase C2)
- [x] **Priority queue**: `fetch_task_for()` selects by max_fee descending, higher-paying tasks prioritized (Phase C3)

#### Stage 3: GPU Node Executes Inference (95%)

**Implemented:**
- [x] `InferenceMiner` full work loop: fetch → run → submit proof (`qfc-miner/src/worker.rs`)
- [x] Multi-backend engines: CPU (candle/BERT) / CUDA / Metal (`qfc-inference/src/backend/`)
- [x] RPC `getInferenceTask` miner task fetching
- [x] GPU tier classification + benchmark scoring + miner registration

**Implemented (Phase E):**
- [x] **Model download and cache management**: `ModelCache` LRU eviction + `ensure_model()` auto-download (`qfc-inference/src/model.rs`)
- [x] **GPU real-time monitoring**: `GpuMetrics` temperature/power/utilization collection, supports NVIDIA/Metal/CPU (`qfc-inference/src/gpu_monitor.rs`)

**Not implementing for now:**
- ~~Task parallel execution~~: Current single-task inference is only 40-80ms, the bottleneck is RPC network latency rather than inference speed; testnet task supply is limited, serial processing is sufficient; parallelism involves InferenceEngine sharing and VRAM concurrency management with high complexity. Will revisit based on actual bottlenecks after mainnet task volume increases.

#### Stage 4: Inference Result Verification (100%) ✅

**Implemented:**
- [x] `InferenceProof` structure: validator, epoch, input_hash, output_hash (blake3), flops, signature
- [x] Basic verification: epoch matching, model approval, FLOPS reasonability (`qfc-ai-coordinator/src/verification.rs`)
- [x] 5% probability spot-check: hash-determined → re-execute inference → compare output_hash
- [x] `handle_inference_proof()` full flow (`qfc-node/src/sync.rs`)
- [x] RPC `submitInferenceProof` endpoint
- [x] **Challenge arbitration**: `ArbitrationPanel` multi-validator voting + majority decision (`qfc-ai-coordinator/src/challenge.rs`)
- [x] **Proof on-chain confirmation**: `proofs_root` Merkle root written to BlockHeader, both block production and verification validated (`qfc-consensus/src/engine.rs`)

#### Stage 5: Result Returned to User (90%) ✅

**Implemented:**
- [x] RPC `getPublicTaskStatus(task_id)` query endpoint
- [x] `PublicTaskStatus::Completed { result_data, miner, execution_time_ms }`
- [x] **Result encoding format**: JSON envelope + base64 payload (B1)
- [x] **WebSocket subscription**: `qfc_subscribeTaskStatus` pushes status changes (B3)
- [x] **Timeout notification**: Expired status returned via RPC and WS push
- [x] **SDK integration**: qfc-sdk-js `getPublicTaskStatus()` + `waitForInferenceResult()` (B4)
- [x] **OpenClaw inference skill**: `QFCInference` class — query/wait/decode result (B5)

**To be completed:**
- [x] **Large result handling**: IpfsClient auto-uploads >1MB results to Kubo, `qfc_getInferenceResult(cid)` gateway proxy

#### Stage 6: Fee Settlement (95%) ✅

**Implemented:**
- [x] `calculate_inference_score()` — `sqrt(tasks) * (flops/1e9) * pass_rate` (`qfc-consensus/src/scoring.rs`)
- [x] PoC v2 scoring integration — inference_score accounts for 20% weight in compute dimension
- [x] Miner registration RPC `registerMiner()` + GPU claim verification
- [x] `ValidatorNode` includes `inference_score` / `tasks_completed` fields
- [x] **Escrow**: `submitPublicTask` RPC deducts `max_fee` (`qfc-rpc/src/server.rs:1672-1687`)
- [x] **70/10/20 revenue sharing**: `settle_inference_fees()` full implementation (`qfc-node/src/producer.rs:309-375`)
- [x] **Timeout refund**: `prune_expired_public()` + `add_balance` refunds escrow
- [x] **Slashing**: `slash_validator()` deducts 5% stake + 6h jail (`qfc-node/src/sync.rs:1003`)
- [x] **Fee pricing model**: `estimate_base_fee()` prices by GFLOPS + GPU tier (`qfc-ai-coordinator/src/task_types.rs`)
- [x] **Settlement input_hash indexing**: Fixed proof→task matching bug (previously used task_id lookup, which never matched)

**To be completed:**
- [ ] **Inference contribution in block rewards**: Scoring exists but reward allocation logic is missing

---

### 13. AI Inference Pipeline Completion Roadmap

> Goal: Fill in the gaps across all 6 stages to make the inference pipeline end-to-end functional

#### Phase A: Core Fee Settlement ✅ Done

> Stage 6 is the economic foundation of the entire pipeline — no settlement = no incentive = no miners

- [x] A1: Escrow module — `submitPublicTask` RPC uses `sub_balance()` to lock fee
- [x] A2: Settlement execution — `settle_inference_fees()` 70/10/20 revenue sharing + **fixed input_hash indexing bug**
- [x] A3: Timeout refund — `prune_expired_public()` auto-refunds escrow
- [x] A4: Slashing execution — `slash_validator()` 5% stake + 6h jail (sync.rs)
- [x] A5: Fee pricing model — `estimate_base_fee()` estimates by GFLOPS x GPU tier, RPC validates min fee

#### Phase B: Result Return Enhancement ✅ Done

> Stage 5 is the last mile of user experience

- [x] B1: Result encoding specification — JSON envelope + base64 payload + submitter/model/timestamps metadata
- [x] B2: Large result storage — IpfsClient (Kubo API) auto-uploads >1MB results, ResultStorage::Ipfs { cid, size, preview }, RPC proxy `getInferenceResult(cid)`, SDK/OpenClaw transparent retrieval
- [x] B3: Result push — `qfc_subscribeTaskStatus` WebSocket subscription, auto-pushes status changes to terminal state
- [x] B4: SDK integration — `getPublicTaskStatus()` structured return + `waitForInferenceResult()` polling
- [x] B5: OpenClaw inference skill — `QFCInference` class: getModels/getStats/getTaskStatus/waitForResult/decode

#### Phase C: Task Routing Hardening ✅ Done

> Stage 2 reliability directly affects task completion rate

- [x] C1: Flow audit + status tracking — `fetch_task_for()` updates PublicTask status to Assigned, records miner/time
- [x] C2: Timeout reassignment — `reassign_stale_tasks()` auto-requeues to pending after 30s with no proof, called by block producer each round
- [x] C3: Priority queue — `fetch_task_for()` scans all pending, selects the highest max_fee matching task

#### Phase D: User Entry Enhancement ✅ Done (2026-03-07)

> Stage 1 — lower the barrier to entry

- [x] D1: `TransactionType::InferenceTask` — Dedicated transaction type (enum variant + executor handler + RPC tx_type mapping)
- [x] D2: Wallet inference UI — qfc-wallet Inference page (task query + status display + i18n 4 languages)
- [x] D3: Explorer inference status — TaskLookup component + `/api/inference/task` API + status display

#### Phase E: Execution Layer Hardening ✅ Done (2026-03-07)

> Stages 3 and 4 — production readiness

- [x] E1: Model download manager — ModelCache LRU eviction (`evict_lru()`) + `ensure_model()` auto-download + `with_max_size()` capacity limit
- [x] E2: GPU monitoring metrics — `GpuMetrics` struct (temperature/power/utilization/VRAM), nvidia-smi collection (CUDA), system memory collection (Metal/CPU)
- [x] E3: Challenge arbitration — `ArbitrationPanel` multi-validator voting + `ArbitrationManager` dispute management + spot-check failure auto-triggers arbitration + majority vote slash

---

### Historical Record: Completed Inference Pipeline Milestones

<details>
<summary>P0/P1/P2 Completion Record (2026-03-05)</summary>

**P0 — Pipeline Foundation:** ✅ Done

- [x] **Proof → chain state update**: `submit_inference_proof()` RPC calls `update_inference_score()` after verification passes
- [x] **Proof signing**: qfc-miner `--private-key` parameter signs proof; RPC verifies signature
- [x] **Spot-check actual execution**: RPC handler injects CPU InferenceEngine, 5% probability re-runs inference verification
- [x] **Slashing trigger**: Spot-check output hash mismatch → `slash_validator(5%, 6h jail)` (trigger path exists, execution confirmed)
- [x] **tasks_completed accumulation bug**: Fixed `saturating_add`

**P1 — Framework Completeness:** ✅ Done

- [x] **Proof on-chain framework**: `proofs_root` written to BlockHeader, ProofPool buffer pool
- [x] **Fee settlement framework**: 70/10/20 revenue sharing design, public task matching during block production
- [x] **Public task flow**: submitPublicTask + Ed25519 signing + getPublicTaskStatus
- [x] **CUDA backend**: Dockerfile.cuda + Dockerfile.miner-cuda

**P2 — Advanced Features:** ✅ Done

- [x] **Miner registration on-chain**: GPU Benchmark + Tier + `qfc_registerMiner` RPC
- [x] **Challenge Tasks**: Pre-computed challenge tasks + adaptive injection rate
- [x] **Redundant verification**: High-value tasks with 3-miner majority consensus
- [x] **Three-tier model scheduling**: Hot/Warm/Cold + LRU eviction
- [x] **Task Router**: Off-chain global scheduling + heartbeat RPC

</details>

---

## Medium Priority Tasks

### 4. ~~Python SDK~~ ✅ Done

**Goal**: Provide an SDK for Python developers

**Repository**: `qfc-sdk-python/` - https://github.com/qfc-network/qfc-sdk-python

**Tech Stack**: Python 3.10+, web3.py, pydantic

**Completed Items**:

- [x] Project initialization (hatchling build)
- [x] QfcProvider (JSON-RPC provider)
  - [x] Standard Ethereum methods (getBalance, getBlock, etc.)
  - [x] QFC-specific methods (getValidators, getContributionScore)
- [x] QfcWallet (wallet management)
  - [x] Private key/mnemonic/random creation
  - [x] Staking operations (stake, delegate, claimRewards)
- [x] StakingClient (advanced staking API)
- [x] Contract helpers
  - [x] ERC-20, ERC-721, ERC-1155 wrappers
  - [x] Multicall3 batch calls
- [x] Pydantic type definitions
- [x] Utility functions (unit conversion, validation, formatting)
- [x] Unit tests
- [ ] PyPI publishing (to be completed)

**Completed**: 2026-02-02

---

### 5. ~~CLI Tool Enhancement~~ ✅ Done

**Goal**: Provide a feature-complete command-line tool

**Repository**: `qfc-cli/` - https://github.com/qfc-network/qfc-cli

**Tech Stack**: Node.js + commander.js + ethers.js v6

**Completed Items**:

- [x] Command framework refactoring (commander.js, ESM)
- [x] Account Management Commands
  - [x] create, import, list, balance, default, export
  - [x] Encrypted keystore (~/.qfc/keystore/)
- [x] Transaction Commands
  - [x] send, status, get, receipt
- [x] Staking Commands
  - [x] deposit, withdraw, delegate, undelegate, rewards, info
- [x] Contract Commands
  - [x] deploy, call, send, code
- [x] Validator Commands
  - [x] list, info, register, update-commission
- [x] Network Commands
  - [x] info, stats, epoch, list, switch, block, gas-price
- [x] Configuration Management
  - [x] get, set, unset, reset, path, env
- [x] Output formatting (JSON/Table, chalk, ora)
- [x] Direct RPC commands
- [ ] Shell auto-completion (to be completed)

**Completed**: 2026-02-02

---

### 6. ~~Mobile Wallet~~ ✅ Done

**Goal**: Native wallet application for iOS and Android

**Repository**: `qfc-wallet-mobile/` - https://github.com/qfc-network/qfc-wallet-mobile

**Tech Stack**: React Native 0.74 + Expo SDK 52 + Redux Toolkit

**Completed Items**:

- [x] Wallet creation/import (mnemonic, private key)
- [x] Biometric authentication (Face ID / Fingerprint)
- [x] Send/receive QFC (with QR scanning)
- [x] Transaction history (status tracking)
- [x] ERC-20 token management
- [x] Staking features (stake, delegate, claim)
- [x] WalletConnect v2 support (basic framework)
- [x] Deep linking (qfc://)
- [x] Theme support (light/dark/system)
- [x] Network switching (mainnet/testnet)
- [ ] Push notifications (to be completed)
- [ ] App Store/Play Store publishing (to be completed)

**Project Structure** (51 files, 6,666 lines):
- `app/` - Expo Router screens (file-based routing)
- `src/components/` - UI components
- `src/services/` - Business logic
- `src/store/` - Redux state management
- `src/hooks/` - Custom Hooks

**Completed**: 2026-02-02

---

### 7. ~~Smart Contract Example Library~~ ✅ Done

**Goal**: Provide common contract templates and examples

**Repository**: `qfc-contracts/` - https://github.com/qfc-network/qfc-contracts

**Tech Stack**: Solidity 0.8.20 + Hardhat + OpenZeppelin

**Completed Items**:

- [x] Hardhat project configuration (TypeScript, multi-network)
- [x] Token Contracts
  - [x] QFCToken.sol - ERC-20 (mint/burn/permit/batch)
  - [x] QFCNFT.sol - ERC-721 (enumerable, mint price)
  - [x] QFCMultiToken.sol - ERC-1155 (supply tracking)
- [x] Staking Contracts
  - [x] StakingPool.sol - Time-weighted rewards, lock periods
  - [x] RewardDistributor.sol - Merkle tree proof distribution
- [x] Governance Contracts
  - [x] QFCGovernor.sol - OpenZeppelin Governor + Timelock
  - [x] Treasury.sol - Role-based access control
- [x] DeFi Contracts
  - [x] SimpleSwap.sol - Constant product AMM (x*y=k), 0.3% fee
  - [x] Vault.sol - ERC4626-style yield aggregator
- [x] Utility Contracts
  - [x] Multicall.sol - Batch calls
  - [x] Create2Factory.sol - Deterministic deployment
- [x] Deployment scripts (deploy.ts, deploy-staking.ts, deploy-defi.ts)
- [x] Unit tests (QFCToken.test.ts, SimpleSwap.test.ts)
- [x] Documentation (README.md, CLAUDE.md)
- [ ] More contracts (LendingPool to be completed)

**Completed**: 2026-02-02

---

## Low Priority Tasks

### 8. Wallet Enhanced Features (Partially Complete)

**Repository**: `qfc-wallet/` (existing)

**Completed Items**:

- [x] Internationalization (i18n)
  - [x] English
  - [x] Chinese (Simplified)
  - [x] Japanese
  - [x] Korean
  - [x] Language selector (Settings page)
  - [x] Chrome Storage persistence
  - [x] All pages translated (Home, Send, Receive, Settings, CreateWallet, Unlock, AddToken, ApprovalDialog)
- [x] Address Book
  - [x] Contact CRUD operations
  - [x] Address validation
  - [x] Copy address functionality
  - [x] Access from Settings page

**Items To Be Completed**:

- [ ] Hardware Wallet Support
  - [ ] Ledger integration
  - [ ] Trezor integration
- [ ] WalletConnect v2
- [ ] Transaction acceleration/cancellation
- [ ] NFT display

**Completed**: 2026-02-02 (i18n + address book)

---

### 9. Block Explorer — Etherscan Parity

**Repository**: `qfc-explorer/` + `qfc-explorer-api/`

**v2.0 Completed Features** (2026-03-08):

- [x] Core Browsing (28 pages, 18 API routes)
  - [x] Block/transaction/address detail pages (with cursor pagination)
  - [x] Internal transactions (debug_traceTransaction)
  - [x] Event log auto ABI decoding
  - [x] Mempool/pending transaction browsing
- [x] Smart Contracts
  - [x] Contract verification (Solc compilation + Standard JSON Input)
  - [x] Contract interaction UI (Read/Write)
  - [x] Proxy contract detection (EIP-1967/1822/Beacon)
  - [x] Etherscan-compatible API (Hardhat/Foundry verify)
- [x] Tokens & NFTs
  - [x] ERC-20/721/1155 tracking
  - [x] Holder rankings + distribution charts
  - [x] NFT gallery (IPFS metadata parsing)
- [x] Analytics & Monitoring
  - [x] Analytics dashboard (TPS, Gas, block time charts)
  - [x] Gas Tracker (price statistics, block utilization, consumption rankings)
  - [x] Leaderboards (balance/activity/validator/contract)
  - [x] CSV data export
- [x] Search & Tools
  - [x] Global search (blocks/transactions/addresses/tokens/labels)
  - [x] ABI tools (keccak256, selector lookup, calldata decoding)
  - [x] Address labeling system
- [x] Infrastructure
  - [x] SEO metadata + Open Graph
  - [x] i18n 4 languages (en/zh/ja/ko)
  - [x] Skeleton loading + Error boundaries
  - [x] SSE + WebSocket real-time updates
  - [x] Prometheus monitoring (API + Indexer)
  - [x] 116 unit tests

**Gap with Etherscan** → see §14

---

### 10. ~~QVM Virtual Machine~~ ✅ Done

**Goal**: Implement the native virtual machine planned in design documents

**Repositories**:
- `qfc-core/crates/qfc-qsc/` (QuantumScript compiler)
- `qfc-core/crates/qfc-qvm/` (QVM execution engine)

**Design Document**: `10-QUANTUMSCRIPT-SPEC.md`

**Completed Items**:

- [x] QuantumScript Language Design
  - [x] Lexical structure (keywords, operators, comments)
  - [x] Type system (primitive types, composite types, resource types)
  - [x] Contract structure (state, events, errors, modifiers)
  - [x] Function types (pure, view, payable, parallel)
  - [x] Control flow (if, match, for, while, loop)
  - [x] Memory model (storage layout, ownership, borrowing)
  - [x] Parallel execution (parallel annotation, state access hints)
  - [x] Formal verification (spec, invariant, requires, ensures)
  - [x] EVM interop (cross-VM calls)
  - [x] Standard library design (math, crypto, collections, standards)
  - [x] Gas model
  - [x] Example contracts (Token, StakingPool)
  - [x] Syntax specification (EBNF)

- [x] Compiler Frontend (qfc-qsc crate)
  - [x] Lexer - Complete token definitions, supports all QuantumScript syntax
  - [x] Parser - Pratt parser, complete AST generation
  - [x] AST Definitions - Complete AST node types (Item, Expr, Stmt, Type, Pattern)
  - [x] Type Checker - Type inference, scope management, error reporting
  - [x] QVM Bytecode Generation - Opcode definitions, instruction encoding, contract compilation

- [x] QVM Execution Engine (qfc-qvm crate)
  - [x] Bytecode interpreter (Executor) - Complete opcode support
  - [x] Stack machine execution model (Stack, Memory, Storage, Heap)
  - [x] EVM-compatible gas metering (GasMeter, GasCosts)
  - [x] Execution context (ExecutionContext) - address, caller, value, block info
  - [x] Resource system runtime (ResourceTracker)
    - [x] Linear type checking
    - [x] Ownership tracking
    - [x] Borrow checking (immutable/mutable)
  - [x] Storage access (warm/cold, EIP-2929 style)
  - [x] Log emission (Log0-Log4)
  - [x] 42 unit tests passing

- [x] Standard Library Implementation (stdlib module)
  - [x] math: min, max, abs, sqrt, pow, log2, clamp, mulDiv, mulDivUp
  - [x] crypto: keccak256, sha256, blake3, ecrecover, verify (Ed25519)
  - [x] collections: array (length, push, pop, get, set, slice, concat)
  - [x] bytes/string: length, concat, slice
  - [x] abi: encode, encodePacked, decode, encodeCall
  - [x] StdlibRegistry function registry

- [x] EVM Interop Module (interop module)
  - [x] InteropManager: Cross-VM call coordination
  - [x] CallBridge: QVM → EVM call execution
  - [x] MultiCall: Batch cross-VM calls
  - [x] Erc20Helper: ERC-20 token advanced interface
  - [x] StateCoordinator: Cross-VM state tracking
  - [x] ReentrancyGuard: Reentrancy attack protection
  - [x] EIP-2929/2930 compatible (warm/cold, access list)

- [x] End-to-End Tests (e2e tests)
  - [x] Compile + execute full flow verification
  - [x] Arithmetic operations (add, mul, sub)
  - [x] Comparison operations (gt, lt, eq)
  - [x] Conditional jumps (if/else)
  - [x] Loop execution (while with locals)
  - [x] Bitwise operations (and, or, shl, shr)
  - [x] Storage operations (sload, sstore)
  - [x] Context access (caller, value)
  - [x] Gas metering and OutOfGas errors
  - [x] 70 tests passing (60 unit + 10 e2e)

- [x] JIT Compilation (Cranelift)
  - [x] JitCompiler: Function compilation to native code
  - [x] CodeGenerator: QVM opcodes → Cranelift IR
  - [x] JitRuntime: Runtime support (storage, context)
  - [x] Compilation result caching (configurable size)
  - [x] Arithmetic, comparison, bitwise, control flow support
  - [x] Optional feature: `--features jit`

- [x] Developer Tools (Dev Tools)
  - [x] VS Code Extension (qfc-vscode)
    - [x] TextMate syntax highlighting (.qs, .qsc files)
    - [x] 25+ code snippets (contract, fn, event, erc20, spec, etc.)
    - [x] LSP client (connects to qsc-lsp)
    - [x] Commands: Restart Server, Format, Compile
    - [x] Configuration: LSP path, trace level
  - [x] qsc-lsp Language Server (qfc-core/crates/qfc-lsp)
    - [x] Real-time diagnostics (lexical, syntax, type errors)
    - [x] Code completion (keywords, types, built-in functions)
    - [x] Hover information (language construct descriptions)
    - [x] Document outline (contracts, functions, structs, events)
    - [x] stdio transport protocol
    - [x] 6 unit tests passing
  - [x] qsc fmt Code Formatter (qfc-core/crates/qfc-qsc)
    - [x] AST pretty printing
    - [x] Configurable indentation (spaces/tabs, size)
    - [x] Configurable max line width
    - [x] CLI: `qsc fmt <file> [--check] [--write]`
    - [x] 3 unit tests passing
  - [x] qsc CLI Tool (qfc-core/crates/qfc-qsc)
    - [x] `qsc compile` - Compile to bytecode
    - [x] `qsc fmt` - Code formatting
    - [x] `qsc check` - Type checking
    - [x] `qsc parse` - Debug AST output

**Completed**: 2026-02-02 (language design + compiler frontend + execution engine + standard library + EVM interop + developer tools + JIT compilation)

**Status**: ✅ Done

---

### 14. Explorer — Etherscan Parity Roadmap

> Goal: Close the feature gap with Etherscan, prioritizing essential features for mainnet launch

#### Phase A: User System ✅ Done (2026-03-08)

- [x] A1: User registration/login (email + OAuth) — JWT + bcrypt + refresh token
- [x] A2: Watchlist — Watch addresses, balance change notifications — up to 50 addresses, balance enrichment
- [x] A3: API Key Management — 3-tier quotas (free/standard/pro), token bucket rate limiting
- [x] A4: User address notes — Private address labels, up to 500 characters
- [x] A5: Transaction notes — Private transaction notes

#### Phase B: Market Data Integration ✅ Done (2026-03-08)

- [x] B1: Token price integration — CoinGecko API + manual pricing, 15-minute cache, SVG sparkline
- [x] B2: Token ranking page — Sort by market cap/holder count/volume/price, type filtering
- [x] B3: Address balance valuation — Holdings USD value, portfolio total value
- [x] B4: Gas price oracle — Percentile slow/standard/fast, homepage widget + detail page

#### Phase C: Contract Enhancement ✅ Done (2026-03-08)

- [x] C1: Read as Proxy — EIP-1967/1822/Beacon proxy detection, Read/Write as Proxy tabs
- [x] C2: Multi-file verification — Standard JSON Input, drag-and-drop upload, entry contract selector
- [x] C3: Vyper contract verification — CLI/Docker compilation, metadata stripping, Vyper verification tab
- [x] C4: Contract Diff — LCS line diff, side-by-side DiffView, ABI diff summary

#### Phase D: Advanced Filtering & Search ✅ Done (2026-03-08)

- [x] D1: Advanced transaction filtering — By amount range, method name, time range, transaction type
- [x] D2: Token Approval management page — Scan Approval/ApprovalForAll, generate revoke calldata
- [x] D3: Address label classification — Exchange, DeFi, bridge, MEV bot, etc. category labels, color-coded
- [x] D4: Batch address query — POST /batch/addresses, up to 20 addresses, CSV export

#### Phase E: Community & Ecosystem ✅ Done (2026-03-08)

- [x] E1: Contract comment system — Star ratings + Markdown comments, reporting/moderation
- [x] E2: DeFi protocol identification — 30+ function selectors, 7 categories, colored labels
- [x] E3: Address profile — GitHub-style heatmap, interaction summary, activity analysis
- [x] E4: Transaction visualization — Pure SVG Sankey diagram, native/ERC-20/internal flow
- [x] E5: Multi-sig wallet detection — Safe/Gnosis proxy detection, owners/threshold display

---

## Priority Recommendations

```
v2.0 AI Compute Network (✅ All Complete):
├── ✅ Phase 1: Inference Runtime (qfc-inference, 3 backends)
├── ✅ Phase 2: Task Coordination (qfc-ai-coordinator)
├── ✅ Phase 3: Existing Crate Adaptation (types/pow/consensus/node/rpc)
├── ✅ Phase 4: Standalone Miner Program (qfc-miner)
├── ✅ Phase 5: candle Model Integration (BERT embedding, Metal, CUDA Docker)
├── ✅ Phase 6: End-to-End Integration (submit→broadcast→verify→spot-check→slash)
├── ✅ Phase 7: Testnet Deployment (Docker + mixed mode + dashboards + phased script)
├── ✅ Phase 8: Ecosystem Integration (SDK inference, governance, public API, Explorer, OpenClaw)
├── ✅ P1 Feature Completeness (proof on-chain, fee settlement 70/10/20, public task flow, CUDA images)
└── ✅ P2 Production Readiness (miner registration, challenge tasks, redundant verification, three-tier scheduling, Task Router)

Completed Infrastructure:
├── ✅ Testnet Deployment (Docker/K8s/Terraform/monitoring)
├── ✅ Developer Docs Site (VitePress, 17 pages)
├── ✅ Python SDK (web3.py, 31 files)
├── ✅ CLI Tools (commander.js, 18 files)
├── ✅ Smart Contract Library (Hardhat, 11 contracts)
├── ✅ Mobile Wallet (React Native + Expo, 51 files)
├── ✅ Block Explorer (Analytics, Export, Contracts)
├── ✅ Wallet (i18n 4 languages, address book, 144 tests)
├── ✅ SDK Tests (JS 181 + Python 18 + Core 258 tests)
├── ✅ QVM Full Stack (compiler + VM + stdlib + JIT + LSP)
└── ✅ OpenClaw Skill (wallet management + security policy)

🔴 Inference Pipeline Completion (v2.1):
├── Phase A: Core Fee Settlement (escrow, transfer, slashing execution, fee pricing)
├── Phase B: Result Return Enhancement (encoding format, IPFS, WebSocket, SDK)
├── Phase C: Task Routing Hardening (flow audit, timeout reassignment, priority queue)
├── Phase D: User Entry Enhancement (dedicated TX type, wallet UI, Explorer)
└── Phase E: Execution Layer Hardening (model management, GPU monitoring, challenge arbitration)

✅ Explorer Etherscan Parity (§14) — 18/18 items all complete:
├── ✅ Phase A: User System (registration/Watchlist/API Key/notes)
├── ✅ Phase B: Market Data (Token prices/market cap/rankings/USD valuation/Gas oracle)
├── ✅ Phase C: Contract Enhancement (Read as Proxy/multi-file verification/Vyper/Diff)
├── ✅ Phase D: Advanced Filtering (transaction filters/Approval management/label classification/batch query)
└── ✅ Phase E: Community Ecosystem (comments & ratings/DeFi identification/address profile/Sankey/multi-sig detection)

🔵 qUSD Stablecoin Enhancement (§15):
├── Phase A: Decentralized Oracle (multi-source aggregation, TWAP, circuit breaker)
├── Phase B: Emergency Shutdown & Global Settlement (multi-sig trigger, tiered pause, redemption)
├── Phase C: PSM Peg Stability Module (USDC/USDT 1:1 swap)
├── Phase D: Multi-Collateral Support (ETH/BTC/wstETH, CollateralManager)
└── Phase E: DAO Governance (stability fee/collateral ratio governance, Timelock)

🟣 qUSD Privacy Layer (§16):
├── Phase A: Privacy Pool (ShieldedPool, ZK proof, Merkle tree, multi-denomination)
├── Phase B: Stealth Address (EIP-5564, one-time receive addresses, scanning)
└── Phase C: Compliance Proof (Association Set, inclusion/exclusion proof)

✅ Completed:
├── ✅ Wallet Advanced Features (Ledger/Trezor, WalletConnect v2, NFT Gallery)
└── ✅ CI/CD Pipeline (qfc-contracts: compile+test+lint+docker, qfc-wallet: lint+typecheck+test+build)
```

---

### 15. qUSD Stablecoin Enhancement Roadmap

> Goal: Upgrade the existing CDP-based qUSD stablecoin from MVP to production-ready, enhancing peg stability, security, and decentralization

**GitHub Project**: [QFC DeFi Suite](https://github.com/orgs/qfc-network/projects/5)

**Existing Foundation**: qUSDToken + CDPVault + PriceFeed + Liquidator (implemented, 150% collateral ratio, 2% stability fee)

#### Phase A: Decentralized Oracle 🔴 P0

> [#50](https://github.com/qfc-network/qfc-contracts/issues/50) — Current centralized PriceFeed is the biggest single point of failure

- [ ] A1: Multi-source aggregation (Chainlink / Pyth / self-hosted nodes)
- [ ] A2: Price deviation detection (>5% deviation triggers circuit breaker)
- [ ] A3: TWAP (Time-Weighted Average Price) calculation
- [ ] A4: Heartbeat check (stale price auto-pauses minting)
- [ ] A5: Multi-sig/DAO emergency price override
- [ ] A6: On-chain price history storage (last N rounds)

#### Phase B: Emergency Shutdown & Global Settlement 🔴 P0

> [#54](https://github.com/qfc-network/qfc-contracts/issues/54) — Security critical, black swan protection

- [ ] B1: `EmergencyShutdown.sol` — Multi-sig triggered shutdown (≥3/5)
- [ ] B2: Freeze all CDP operations post-shutdown, allow pro-rata redemption
- [ ] B3: Global settlement flow (snapshot → liquidation price → qUSD exchange → surplus return)
- [ ] B4: Tiered pause (L1 pause minting / L2 pause all / L3 global settlement)
- [ ] B5: L1-L2 DAO vote recovery mechanism

#### Phase C: PSM Peg Stability Module 🟡 P1

> [#52](https://github.com/qfc-network/qfc-contracts/issues/52) — Strengthen de-peg defense

- [ ] C1: `PSM.sol` — USDC/USDT ↔ qUSD 1:1 swap
- [ ] C2: Configurable fees (tin/tout)
- [ ] C3: Per-asset debt ceiling
- [ ] C4: Reserve audit interface
- [ ] C5: Emergency pause switch

#### Phase D: Multi-Collateral Support 🟡 P1

> [#51](https://github.com/qfc-network/qfc-contracts/issues/51) — Scale minting capacity

- [ ] D1: `CollateralManager.sol` — Manage multiple collateral types
- [ ] D2: Per-asset collateral ratio / liquidation threshold
- [ ] D3: Wrapped asset support (wBTC, wETH)
- [ ] D4: LST yield-bearing asset support (wstETH, rETH)
- [ ] D5: Global + per-asset debt ceiling
- [ ] D6: Collateral risk parameter governance interface

#### Phase E: DAO Governance 🟢 P2

> [#53](https://github.com/qfc-network/qfc-contracts/issues/53) — Decentralized parameter management

- [ ] E1: `qUSDGovernance.sol` — Parameter governance contract
- [ ] E2: Governable: stability fee, collateral ratio, liquidation threshold, debt ceiling, PSM fees
- [ ] E3: Timelock delayed execution
- [ ] E4: Parameter change range limit (±20%)
- [ ] E5: Integration with QFCGovernor + Treasury

---

### 16. qUSD Privacy Layer Roadmap

> Goal: Add on-chain privacy protection for qUSD to address user concerns about transaction traceability. Combines Privacy Pools + Stealth Addresses to protect privacy while supporting compliance proofs.

**GitHub Project**: [QFC DeFi Suite](https://github.com/orgs/qfc-network/projects/5)

**Motivation**: qUSD has no USDT-style blacklist/freeze, but on-chain transfers are fully transparent — anyone can trace fund flows.

#### Phase A: Privacy Pool (ShieldedPool) ✅ Complete

> [#55](https://github.com/qfc-network/qfc-contracts/issues/55) — Core privacy feature, break on-chain fund linkability

- [x] A1: `ShieldedPool.sol` + `ShieldedPoolV2.sol` — Fixed-denomination deposit/withdraw (100/1K/10K/100K qUSD)
- [x] A2: `PoseidonMerkleTree.sol` — Poseidon incremental Merkle tree, 20 levels (~1M deposits)
- [x] A3: Nullifier replay protection (on-chain mapping + ZK circuit constraint)
- [x] A4: ZK circuit (Groth16, circom 2.2.2) — `withdraw.circom` 5381 constraints
  - [x] `hasher.circom` — Poseidon commitment + nullifier hash
  - [x] `merkleTree.circom` — Merkle proof checker (DualMux + HashLeftRight)
  - [x] Trusted setup: Powers of Tau (BN128 2^14) + contribution + beacon finalization
  - [x] `circuits/build.sh` — One-click compile + setup script
- [x] A5: `Groth16Verifier.sol` — Auto-generated on-chain ZK proof verifier (snarkjs)
- [x] A6: Relayer service (`relayer/index.ts`) — Express.js, POST /relay + GET /jobs/:id
- [x] A7: Frontend UI (`qfc-defi/src/app/privacy/page.tsx`) — Deposit/withdraw, denomination selector, proof status
- [x] A8: SDK (`qfc-defi/src/lib/shieldedPool.ts`) — Note generation/serialization, relayer client
- [x] E2E test: deposit → Poseidon commitment → Merkle insert → off-chain Groth16 proof → on-chain verify → withdraw
- [x] A9: Browser-side ZK proof generation (`qfc-defi/src/lib/zkProver.ts`) — Dynamic snarkjs loading, supports both standard and compliance circuits
- [ ] Launch checklist:
  - [ ] Formal trusted setup ceremony (multi-party)
  - [ ] Relayer deployment + gas funding
  - [ ] ZK circuit + contract audit

#### Phase B: Stealth Address (EIP-5564) ✅ Complete

> [#56](https://github.com/qfc-network/qfc-contracts/issues/56) — Private receiving, prevent linking multiple receipts

- [x] B1: `StealthAddress.sol` — Stealth meta-address registry (spending + viewing pubkeys)
- [x] B2: `generateStealthAddress()` — Sender generates one-time stealth address
- [x] B3: `announceTransfer()` — Publish ephemeral pubkey + viewTag for recipient scanning
- [x] B4: `scanByViewTag()` — viewTag filtering + paginated announcement queries
- [x] B5: SDK integration (`qfc-defi/src/lib/stealthAddress.ts`) — Key generation/serialization, stealth address computation, viewTag scanning, contract helpers
- [x] B6: Wallet "private receive" page (`qfc-defi/src/app/stealth/page.tsx`) — Setup Receive / Send Privately / Scan Incoming tabs

#### Phase C: Compliance Proof (Privacy Pools Extension) ✅ Complete

> [#57](https://github.com/qfc-network/qfc-contracts/issues/57) — Balance privacy and compliance

- [x] C1: `AssociationSet.sol` — DAO-governed address set registry
  - [x] Inclusion sets (KYC compliant) + Exclusion sets (sanctioned addresses)
  - [x] Curator role management, Poseidon Merkle root storage
  - [x] Activate/deactivate, query by type
- [x] C2: `ComplianceVerifier.sol` — Three-tier compliance verification
  - [x] None (no proof) / Basic (inclusion proof) / Full (inclusion + exclusion)
  - [x] Root consistency validation, duplicate prevention
- [x] C3: DeFi integration interface — `meetsComplianceLevel(nullifierHash, minLevel)`
  - [x] Protocols can query withdrawal compliance level to gate access
- [x] C4: `withdrawCompliant.circom` — Extended ZK circuit (10,517 constraints), proves both pool membership + association set membership
  - [x] `ComplianceGroth16Verifier.sol` — On-chain verifier (5 public inputs)
  - [x] WASM + zkey generated, ready for browser-side proving

---

## How to Contribute

1. Choose a task
2. Create an Issue in the corresponding repository
3. Fork and create a feature branch
4. Submit a PR and link the Issue
5. Merge after code review

## Related Documents

- [Project Overview](./00-PROJECT-OVERVIEW.md)
- [Blockchain Design](./01-BLOCKCHAIN-DESIGN.md)
- [Consensus Mechanism](./02-CONSENSUS-MECHANISM.md)
- [Wallet Design](./07-WALLET-DESIGN.md)
- [AI Compute Network Design](./13-AI-COMPUTE-NETWORK.md)
- [OpenClaw Integration](./14-OPENCLAW-INTEGRATION.md)
