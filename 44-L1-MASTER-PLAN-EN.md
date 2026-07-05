# QFC L1 Master Plan

**English** | [中文](./44-L1-MASTER-PLAN-CN.md)

> Last updated: 2026-07-04
>
> Positioning: this document is the **single top-level plan** for QFC L1. It replaces 39 (its status snapshot is stale) and inherits the gate framework of 42 (the three gaps). 42's timebox has expired but was never actually tested — the entire window was eaten by the consensus fork, so the gates are reset and the clock restarts here; the discipline is unchanged.

---

## 0. Status Snapshot (2026-07-04, unvarnished)

**Chain core (qfc-core)**
- ❌ **The testnet has never reached multi-node consensus** — 3 validators forked three ways from block #1. 6 compounding defects located, 5 fixed (PR #126 leader-election convergence, #128 forward catch-up, #129 wall-clock slot/epoch); **the 6th is unfixed**: no "no block production until caught up" gating at fresh node startup, so a fresh boot immediately produces its own block #1.
- ⚠️ Both resets failed (each one exposed a new defect). Conclusion from the last session: stop the fix-one-try-again loop; instead do **one consolidated review of the entire block-production/sync path**, find all remaining defects in one pass, fix them together, and do one final reset.
- ✅ SRE T1–T8 all merged (PR #103–#123) but deployment is blocked on the reset. Image pipeline is ready (staging branch builds, VPS-B can pull).
- ✅ AI-V3: B-1 + Feature A (A0–A6) core complete, B-2 spike complete (interactive WAN inference is a no-go; batch is bandwidth-gated). Everything remaining requires node integration or real cross-region hardware.

**Ecosystem periphery**
- ✅ The full suite is online (explorer/dex/defi/nft/bridge/faucet/games/agenthub/wallets ×3/SDKs ×2/CLI), at 60–95% completion.
- ❌ **External participation is zero**: 0 external miners, 0 external inference callers, 0 external validators.

**Actual progress on 42's three gaps** (corrected by this stocktake: it is not "nothing done")
- **The bulk of Gap C is done**: `miner-economics/` has model v2 (MINER-ECONOMICS.md + model.py, measured against the live chain 2026-04-14); weekly snapshots snapshots.jsonl have run 8 consecutive weeks since 05-10. Conclusion: **conditional pass** — emission halves yearly (10 → 0.625 QFC/block, bottoming out in year 4), and the current 75% inflation / 25% fee structure, even with zero demand growth, naturally reaches ~39% fee share by year 4 as emission decays. Two survival conditions: ① miners must survive year-0 dilution (at a token price < $0.05, RTX 3060-class hardware runs at a loss; only low-cost devices break even); ② demand must show up before miner count exceeds ~500. The external review template (REVIEW-REQUEST.md) and outreach copy (OUTREACH-POSTS.md, $300/45min) are ready but **were never sent**.
- **The Gap A review is done**: MINER-ONBOARDING-REVIEW.md (04-14) found 2 real bugs, **neither fixed**: ① `start-miner.sh` downloads from the `qfc-core` release (v2.3.1, 5 platforms) instead of the `qfc-miner` repo (v2.3.2, 9 platforms) — CUDA/Windows/ARM64 users fall straight into building from source; ② the chain-v2.2.3 vs binary-v2.3.x version drift was never verified end to end.
- **Gap B untouched.**

**Core conclusion**: the periphery is far ahead of the core. If the chain itself doesn't converge, every externalization move (miner recruitment, demand validation, mainnet) is meaningless. The plan must start with fixing the chain.

---

## 1. Strategic Through-Line

QFC has exactly one reason to exist, a single loop:

> **Miners run AI inference for block rewards (supply) ↔ users/agents pay to call verifiable inference (demand)**, running on a chain that **converges and is economically self-sustaining**.

All work is ranked by "does this advance the loop?" If loop validation fails, mainnet does not launch; only after it passes does mainnet earn a place on the schedule.

```
Phase 0 Chain runs ──→ Phase 1 Economic viability ──→ Phase 2 External loop validation ──→ Phase 3 Mainnet prep
  (hard prerequisite)       (Gap C)                       (Gap A + Gap B)                     (only after PMF)
```

---

## Phase 0 — Chain Runs (now → convergence verified)

**Goal**: 3 validators converge continuously for ≥ 7 days from a fresh genesis; SRE T2–T8 deployed; all contracts redeployed.

| # | Work item | Notes |
|---|-----------|-------|
| 0.1 | **Consolidated consensus review** | One adversarial review (multi-agent) of the full producer/sync/consensus/networking path; goal is to find, in one pass, every defect beyond category 6 that "only surfaces in multi-node runtime". Focus: sync-before-produce gating, startup grace, fork choice, clock-drift tolerance, epoch-boundary races |
| 0.2 | **Fix all findings** | Including the known 6th defect: producer must be aware of SyncManager.highest_peer_block and not produce while strictly behind; a bootnode with no peers may produce immediately to bootstrap the chain |
| 0.3 | **Final reset (3rd — intended to be the last)** | New image → wipe all three nodes → fresh genesis → verify item by item: peering, epoch agreement, identical hashes for block #1/#100/#10k |
| 0.4 | **7-day convergence soak** | Add a "multi-node head-hash agreement" alert in Grafana (a fork = immediate alarm, no more discovery by hand) |
| 0.5 | **Deploy T2–T8 + redeploy all contracts** | All DEX/NFT/Bridge/qUSD/DeFi contract addresses change → update every frontend env, document 41, and the faucet in lockstep |

**Exit gate (hard)**: 3 nodes at the same height with the same hash for 7 consecutive days; miner proofs accepted; explorer data consistent. **If this gate is not passed, no subsequent Phase starts.**

**Effort**: roughly 5–8 Claude session hours (review 1–2, fixes 2–3, reset+deploy+verify 2–3). Wall clock roughly 1.5–2 weeks, dominated by the 7-day soak.

---

## Phase 1 — Economic Viability (Gap C wrap-up, in parallel with Phase 0)

Model v2 already exists (see §0); this Phase is **wrap-up**, not modeling from scratch. Purely offline — **can start immediately**.

| # | Work item | Notes |
|---|-----------|-------|
| 1.1 | **Model refresh** | Refresh model.py outputs with the 8 weeks of measured snapshots.jsonl data + the post-reset chain parameters; add sensitivity at miner scales n = [10, 100, 1000] and a year-0 break-even table |
| 1.2 | **Mainnet parameter draft** | Initial inflation rate (the emission halving schedule is already in protocol constants), reward distribution curve, staking threshold, slashing thresholds (revised against 03-TOKENOMICS and 12-VALIDATOR-ALLOCATION) |
| 1.3 | **Send out the external review** | REVIEW-REQUEST.md + OUTREACH-POSTS.md are both written; the blocker is literally "sending them" — post, book people, pay $300/45min, run 1–2 sessions |

**Exit gate**: the refreshed model sustains its "conditional pass" and the external review finds no major logical flaw.
**Abandonment gate**: if the refreshed conclusion degrades to "nobody mines below a $10 token price" → the decentralized-miner route is economically unviable; pivot to a pure inference-API positioning (keep the chain, stop pushing miner recruitment).

**Effort**: roughly 1–2 Claude session hours (model refresh + parameter draft). 1.3, posting and booking people, is a **manual task — duration outside Claude's control** — and is currently the only real blocker on Gap C.

---

## Phase 2 — External Loop Validation (Gap A + B; starts after both Phase 0 and Phase 1 gates pass)

Document 42's gates **restart the clock here**: A/B in parallel, 8-week window.

### 2A. Miner Onboarding (supply side)

| # | Work item |
|---|-----------|
| 2A.1 | First fix the 2 known bugs from MINER-ONBOARDING-REVIEW.md: point the `start-miner.sh` download source at the `qfc-miner` repo (not qfc-core); verify the version drift end to end |
| 2A.2 | Cut a miner release aligned with the post-reset chain protocol (old binaries will necessarily break — genesis changed), rebuild all 9 platform binaries; then self-test the full README flow on a clean VPS; success criterion = the address's inference proofs visible on the explorer. **While at it**: ① rebuild the CUDA build with the latest toolkit and confirm PTX forward compatibility (new architectures like Blackwell/Rubin run via driver JIT, no dedicated port needed); ② confirm inference-proof verification uses tolerance-based comparison across GPU generations rather than bit-exact (otherwise floating-point differences on new architectures get misjudged as cheating; see AI-V3 A4b tolerance-band and document 16) |
| 2A.3 | Landing page (miner.qfc.network): one-screen copy + `curl \| sh` + earnings estimator (directly referencing the Phase 1 model) |
| 2A.4 | Miner day-one dashboard: explorer `/miner/[address]` page (proof count, cumulative rewards) |
| 2A.5 | Exposure: Twitter + Show HN + relevant Discord/TG — **manual task** (posting, answering questions, community ops) |

### 2B. Inference Demand (demand side)

| # | Work item |
|---|-----------|
| 2B.1 | Public inference REST API (api.qfc.network/v1/inference, Traefik + rate limit + API key + requests_per_day metric) — qfc-inference-router already provides the base |
| 2B.2 | SDK snippets: ≤20 lines each in JS/Python to "call + get result + verify proof" |
| 2B.3 | **Differentiation demo**: one concrete scenario that explains "verifiable inference" in 1 minute (candidates: agent decision auditing, on-chain game AI fairness, traceable content moderation). This is the first thing a stranger sees |
| 2B.4 | Interview outline for 5 use cases + talk to 3 external developers — **manual task** |

### Gates (fixing 42's measurability problem)

- **8-week gate**: ≥ 3 external miners (distinct IP ranges + distinct signup channels, sybil excluded) producing proofs for 7 consecutive days; ≥ 1 external caller (a non-team API key with sustained calls).
- **12-week gate**: ≥ 10 miners, ≥ 3 callers, 1 demo that impresses a stranger → declare initial PMF validated, enter Phase 3.
- **Kill gate**: 8 weeks with zero external miners and zero onboarding inquiries → shut down the miner route, execute Phase 1's pure-API fallback positioning; 8 weeks with zero external calls → no demand-side PMF, mainnet shelved indefinitely.
- Measurement first: landing-page analytics, per-key API metrics, signup-channel tagging on miner addresses — **for every number a gate uses, define how it is collected before the clock starts**.

**Effort**: roughly 10–14 Claude session hours (2A about 5–6, 2B about 5–8). Wall clock 8–12 weeks; the bottleneck is external adoption signal, not development.

---

## Phase 3 — Mainnet Prep (only if the 12-week gate passes)

Checklist only, no elaboration (a detailed plan gets written separately when we get there):

1. **Security**: contract audit (external, weeks of wall clock + cost), consensus/node code audit, bug bounty
2. **AI-V3 node integration**: Feature A's apply_settlement wired to real chain state, P2P broadcast, N-of-M operator consensus, VRF sampling entropy (all already flagged in qfc-ai-coordinator)
3. **B-2 sharded-inference build**: gated on "rerun the calculator with real RTT/BW from cross-region miners" — unlocks naturally once Phase 2 recruits multi-region miners
   - **Datacenter GPU tier** (Grace/Vera + Blackwell/Rubin class): utilization only exists once training + large-model batch inference launch; at that point add native cubin (CUDA 13.x), write it into the GPU tier table, and break out its earnings tier in the economic model. Under year-0's small embedding workloads this hardware is a pure loss (model v2 conclusion); Phase 2 neither recommends nor advertises it
4. **Performance**: the BLAKE3 portable backend and sync-log write amplification found by T1 profiling; benchmark toward the 500k TPS target
5. **Mainnet parameter finalization**: Phase 1 draft + revisions from measured testnet data; genesis ceremony, validator allocation (document 12)
6. **Minimum governance set**: upgrade mechanism, emergency pause, governance proposal_id bound to model_info (B-1 leftover, must-fix before mainnet)

**Effort**: roughly 15–25 Claude session hours; the external audit dominates wall clock — **manual task (choosing an audit firm, paying, scheduling)**.

---

## 3. Parallelism and Dependency Map

```
now ──────────────────────────────────────────────────────▶
Phase 0 Chain runs   ████████░░ (1.5–2 wks, soak dominates)
Phase 1 Econ model   ██████░░ (parallel with P0; external review scheduling is on you)
Phase 2 A+B          ░░████████████████ (8–12 wks, starts after both gates pass)
Phase 3 Mainnet                       ░░░░░░████ (only after PMF)
Freeze list: new DeFi features / NFT & game frontends / Bridge chain expansion / UI polish ── frozen throughout ──
```

**Freeze discipline** (inherited from 42): every PR first answers "does this advance the current Phase?" If not → defer. Sole exception: AgentHub, if chosen as the 2B.3 demo vehicle.

---

## 4. Governance Cadence

- **Weekly update**: every Sunday, append one paragraph of progress per Phase to §5 of this document (42's lesson: a process written down but not executed equals none — this rule itself is part of the weekly-update check).
- **Gate decisions**: when each exit gate/kill gate comes due, open a dedicated session to make the call and record it in §5. **Silently sliding past is not allowed.**
- **Document 42**: write the missing T+12 verdict ("window swallowed by the consensus fork, gates never tested, reset per document 44"), then archive it read-only.

---

## 5. Progress Log

*(appended every Sunday)*

- **2026-07-04**: Document created. Stocktake corrections: Gap C model v2 + 8 weeks of snapshots already exist (conditional pass), the Gap A review is done (2 bugs unfixed), Gap B untouched. Phase 0 pending (6th defect unfixed, testnet still forked at 7ce54c5); Phase 1 has only the model refresh + sending the external review left.
- **2026-07-05 (weekly update #1)**:
  - **Phase 0**: 0.1+0.2 done — the consolidated review found all remaining defects in one pass, actually **7 of them, D6–D12** (not just the known 6th); qfc-core PR #130 merged (deterministic execution, self-contained validation, fork choice, sync-before-produce gating, vote-once, finality hardening; ADR-0012 + 16 review fixes). #131 bakes qfc-watchdog into the image (for the T6 sidecar). Staging image building. **Next: 0.3 reset #3 → 0.4 seven-day soak → 0.5 deploy T2–T8 + contract redeploy**. The testnet is currently still running the old v2.2.3 image (forked, harmless).
  - **Phase 1**: 1.1+1.2 done — model v3 (PR #48, conditional pass sustained, worst-case break-even token price $2.11); document 45 mainnet parameter draft + document 42 T+12 verdict archived (PR #49). Of the 7 inconsistencies in the §6 conflict list, 2 are qfc-core implementation bugs (three conflicting slashing definitions, dead-code 1% staking cap), verified still present after #130; issues to be opened. **Sole remainder of Phase 1: 1.3 send the outreach and book the external review (manual task)**.
  - **Phase 2 pulled-forward item**: 2A.1 done — install.ps1 download source corrected + version-drift warning in both scripts (qfc-miner PR #10, verified against the real RPC, correctly detects the v2.3.2 vs v2.2.3 drift). E2E clean-VPS verification stays scheduled for 2A.2 (post-reset) as planned.
  - **Risks/reminders**: ① the staging image build for #130 concluded as failure (suspected known dispatch-step issue; the image itself may be fine) — the image must be confirmed genuinely usable before the reset; ② the v3 model may overstate miner fee income by 1.43× (counts 100%, protocol actually pays 70%); logged as document 45 OQ-3, to be corrected together when the snapshots rerun after the reset.
- **2026-07-06 (supplement — weekly update #1 was written BEFORE the reset; the following 24 hours were dense, recorded here honestly)**:
  - **Phase 0 milestone: 0.3 done, 0.4 underway.** Reset #3 executed 2026-07-05 (image staging-sha-cd5bafd = #130+#131); **all three validators converged for the first time ever** — block 100 and tip-5 hashes byte-identical across nodes (independently verified), 50+ blocks with zero rejections. **7-day soak until ~07-12.** SRE T2–T8 deployed the same day (watchdog sidecars, SLO alerts live); firing alerts went 12→0.
  - **Soak-window fixes (all merged AND deployed; the running image contains all of them)**: #134 enforces the 20% stake cap + single-source slashing constants (closes issues #132/#133; both review advisories addressed); #136 mempool import-time eviction + periodic expiry (closes #135 — zombie txs kept the oldest-tx-age alert permanently red; measured 45min→0.5min after the fix); #137 phantom receipts + reorg cleanup, #138 CREATE address nonce, #139 EVM timestamp/gas — the latter three clear the execution-layer blockers for **0.5 contract redeployment**.
  - **Ops**: explorer memory-alert root cause fixed (qfc-explorer #124: cheap not-found rendering + robots blocking deep-pagination crawl; crawler traffic on stale pre-reset URLs was the memory driver); Grafana T2 dashboard datasource fixed (qfc-testnet #6).
  - **Docs**: English versions of 44/45 (#52) + full bilingual backfill, 11 pairs (#53); doc 41 now carries a dead-contract-addresses warning, refresh due after 0.5.
  - **Next**: 0.4 soak through 07-12 (recommend adding a cross-node head-hash fork alert) → 0.5 full contract redeployment + frontend envs / doc 41 refresh → pass the Phase 0 exit gate. Phase 1 still owes only 1.3, the manual outreach.
