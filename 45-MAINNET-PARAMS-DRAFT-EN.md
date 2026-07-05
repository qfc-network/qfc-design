# Mainnet Parameter Decision Draft (Phase 1.2)

**English** | [中文](./45-MAINNET-PARAMS-DRAFT-CN.md)

> Last updated: 2026-07-04
>
> Positioning: this document is the deliverable of `44-L1-MASTER-PLAN-EN.md` **Phase 1.2** — a **decision draft** for mainnet economic/consensus parameters, not a research report. For every parameter it gives: the current value (with source), the proposed mainnet value, the rationale (citing concrete numbers from the miner-economics v3 model), and open questions awaiting external review.
>
> Finalization flow: this draft → Phase 1.3 external economics review (REVIEW-REQUEST.md, 1–2 sessions) → Phase 2 testnet measurement revisions → Phase 3.5 mainnet parameter finalization.
>
> Status: **DRAFT (not finalized — do NOT implement from this document)**

---

## 0. Reading Notes and Method

**Precedence for "current value"**: protocol constants (`qfc-core/crates/qfc-types/src/constants.rs`, verified 2026-07-04) > actual runtime code behavior > design docs (02/03/12). Where the three disagree, the conflict is **explicitly flagged** and no side is taken by default (see the conflict register in §6).

**Quantitative basis**: the `miner-economics/` v3 refresh (2026-07-04, `refresh.py` + `OUTPUT.md`, based on 12 weeks of snapshots.jsonl). The v3 data comes from a **forking testnet** (only 5 of 12 snapshots usable) and can only be treated as indicative; wherever a conclusion depends on real demand or healthy-chain behavior, confidence is uniformly marked **low** — we do not pretend to precision.

**Two facts that run through everything**:
1. **The testnet has never actually triggered any slashing** (v3: pass rate 100%, and no slash events were recorded even during the fork). None of the severity recommendations in §4 are backed by battle data.
2. **The testnet has never reached multi-node consensus** (doc 44 §0). For any "observed vs theoretical" deviation (such as the 12× gap in §2.2), suspect the fork first, parameters second.

**Confidence level definitions**: high = protocol already implemented and internally consistent, only needs confirmation; medium = direction is grounded but the number needs external review; low = depends on data that does not yet exist (real demand, real attacks, a healthy chain) — any current number is a placeholder.

---

## 1. Initial Inflation Rate / Emission

### 1.1 Current values (protocol constants, implemented)

| Item | Value | Source |
|---|---|---|
| Initial block reward | 10 QFC/block | `BLOCK_REWARD = 10^19 wei`, constants.rs |
| Halving period | Once per year, at most 4 times | `HALVING_PERIOD_YEARS = 1`; `year.min(4)` in `block_reward_for_year()` |
| Reward floor | 0.625 QFC/block (from year 4) | `MIN_BLOCK_REWARD = 625_000_000_000_000_000` |
| Initial supply | 1 billion QFC | `INITIAL_SUPPLY` |
| Supply cap | 2 billion QFC | `MAX_SUPPLY` |
| Nominal block time | 3333 ms | `BLOCK_TIME_MS` → ~9.46M blocks/year |
| Year calculation method | **By block height** | `producer.rs::calculate_year()`: `block_height / blocks_per_year` |

Corresponding annual inflation (against the initial 1 billion): Y0 ≈ 9.5% → Y1 ≈ 4.3% → Y2 ≈ 2.1% → Y3 ≈ 1.0% → Y4+ ≈ 0.5% (the table in doc 03 matches this; its footnote "one block every 3 seconds, ~10,512,000 blocks per year" contradicts its own table — see §6 conflict 5).

### 1.2 Proposed mainnet value: **keep the existing halving schedule unchanged**

**Rationale (concrete v3 numbers)**:
- The halving schedule is the structural foundation of the Gap C "conditional pass" conclusion: on the refreshed baseline (miner pool 4,681.69 QFC/day) and with **zero demand growth**, the miner pool's fee share climbs purely on emission decay: 29% (Y0) → 45% (Y1) → 62% (Y2) → 76.6% (Y3) → 86.7% (Y4). The chain automatically transitions from subsidy-driven to demand-driven on schedule, with no governance intervention required.
- The key lesson from v2 (MINER-ECONOMICS §4): a 10× demand expansion barely moves miner income — **token price × miner count** is the dominant variable. Tweaking the emission curve does not solve the real problem (zero demand); it only breaks a model already validated as self-consistent.
- The abandonment gate in doc 44 ("nobody runs it unless the token is > $10") has not been triggered: the worst realistic cell is a rented data-center GPU at n=1,000 needing $2.11, and that hardware should not be running this chain in the first place.

**Record of rejected modification proposals**: v2 §5 path 3 (redesign emission so fees dominate at n≈100) was rejected by v3 — the decay is already built in, and cutting the Y0 subsidy early only worsens the first survival condition, "miners must survive year 0" (RTX 3060 loses money below $0.05/QFC; break-even price at n=100 is $0.021).

### 1.3 The testnet → mainnet year-0 clock

**Proposal: mainnet fresh genesis restarts year 0 from height 0 (i.e. a clock reset); halving progress consumed on testnet does not carry over.**

- This is in fact the **protocol's default behavior**: `calculate_year()` computes by height, mainnet's new genesis resets height to zero, and the clock resets automatically. This item confirms the default; it is not a new mechanism.
- Rationale: the year-0 subsidy window for mainnet miners/validators is the core cold-start resource (v3 survival condition 1) and should not be burned by the testnet; moreover, the testnet's multiple resets (06-18, 06-27) have already implicitly reset this clock several times — there is no precedent or mechanism for "carrying the clock over".
- Incidental finding: the comment on `calculate_year()` says "~262,800 blocks per year", while the actual formula yields ~9,462,046 blocks/year — **the comment is wrong, the code is correct**. Fix the comment before mainnet (no behavioral impact).

**Confidence: high** (protocol implemented and model-validated as self-consistent; the reset is default behavior).

### 1.4 Open questions (external review)

- **OQ-1**: With years counted by height, if actual block time persistently deviates from 3333 ms (as it did during the testnet fork), the wall-clock timing of halvings drifts. Is that acceptable, or should years be counted from the genesis timestamp? (Bitcoin counts by height — precedent supports the status quo.)
- **OQ-2**: The dynamic `reward_multiplier` adjustment (producer.rs, scales rewards with staking ratio/congestion) stacks on top of the halving schedule, and the v3 model **did not model** this multiplier. Before mainnet its value range must be pinned down and added to the model, otherwise actual inflation can deviate from the table in this section.

---

## 2. Reward Distribution

### 2.1 PoC contribution weights

**Current values** (constants.rs `WEIGHT_*`, consistent with doc 02): stake 30% / compute 20% / uptime 15% / accuracy 15% / network 10% / storage 5% / reputation 5%.

**Proposed mainnet value: keep unchanged.**

Rationale: no data supports a change — v3 explicitly notes "at n=2 the two miners split exactly 50/50; the 1/n assumption is completely untested for n>2", and the distributional effect of the PoC weights in practice has likewise never been observed. Adjusting multi-dimensional weights with zero observational data is false precision. Re-examine with real distributions after Phase 2 recruits ≥10 external miners.

**Confidence: medium** (the reason for keeping is "no evidence supports changing", not "evidence supports the current values").

### 2.2 Block reward split and the miner pool share

**Current values** (constants.rs + producer.rs, implemented):
- Block reward: producer 60% / voters 25% / **inference miners 15%** (`PRODUCER/VOTERS/INFERENCE_MINERS_REWARD_PERCENT`; miners split by FLOPS share of proofs in the block; with no proofs, the 15% flows back 70/30 to producer/voters).
- Note: doc 02 §block reward distribution and doc 03's income formula still say 70/30 with **no miner share** — outdated, see §6 conflict 1.
- The 15% is nominal; `adjustments.inference_miner_percent` in producer.rs can adjust it dynamically.

**The v3 12× gap — answering "what is the mainnet target value" head-on**:
- Theory: 15% × 10 QFC/block × 9.46M blocks/year ⇒ miner inflation pool ≈ **38,884 QFC/day** (OUTPUT.md).
- Observed (06-28 snapshot): the inflation slice was only **3,323.69 QFC/day**, roughly **1/11.7** of theory.
- **Attribution call: this is a symptom of chaotic block production on a forked chain, not a parameter design error.** v3 verbatim: "If the consensus fix lands and block production normalizes, the year-0 pool could be substantially larger than modeled here."

**Proposed mainnet target: keep the nominal 15%; make "measured miner pool ≥ 80% of theory (~31,000 QFC/day @ Y0)" an acceptance metric after the Phase 0 exit gate** — i.e. after the consensus fix + final reset, re-run `refresh.py` on the first month's snapshots to verify the gap disappears. If the gap is still >2× on a healthy chain, that indicates an implementation-level bug in the distribution path (rather than a consensus symptom); fix the bug first, then revisit parameters. **Until healthy-chain data exists, do not adjust the 15% itself based on fork data.**

**Confidence: medium** (the absolute level of 15% lacks external benchmarks — one of the core questions for REVIEW-REQUEST; the attribution of the 12× gap is grounded but not yet confirmed on a healthy chain).

### 2.3 Gas fee split — the inference-miner-0% question, addressed head-on

**Current values** (constants.rs `FEE_*`, implemented in producer.rs): producer 47% / voters 28% / burn 20% / treasury 5%, **inference miners 0%**. (Doc 03 says 50/30/20 with no treasury — outdated, see §6 conflict 2.)

**Proposed mainnet value: keep 0%, but record it as an explicit decision and make it a must-answer question for external review.**

Rationale:
- Inference miners already have two dedicated income streams: the 15% block reward pool (§2.2) + inference task fees (`INFERENCE_FEE_*`: miner 70% / validators 10% / burn 20%). Gas fees come from transfers/DEX/NFT and other traffic causally unrelated to inference; v3 §7 explicitly excludes them from the miner model ("they don't pay miners — they burn or go to validators").
- Adding a gas slice for miners necessarily dilutes the validator/burn shares, while validator incentives during mainnet launch are equally fragile (doc 12 requires the official operator to shoulder stability first).
- The v3 model shows the bottleneck of miner economics is not how the income slices are cut but **demand itself being zero** (`unique_submitters_last_100 = 0`). Touching the gas split is a patch at the wrong layer.

**Counter-argument (recorded faithfully)**: long term (Y4+), the emission pool shrinks to 207.7 QFC/day; if by then inference task fees still have not taken off while gas volume has, miners will have no structural income in the fee-dominated era. If external review judges that scenario non-negligible, the fallback is "carve part of the 5% treasury slice into a targeted miner subsidy", without touching 47/28/20.

**Incidental accounting question (OQ-3)**: the v3 model credits 0.1 QFC/task to miner fee income **in full** (1,358 = 13,580 × 0.1), but the protocol constant is `INFERENCE_FEE_MINER_PERCENT = 70`. If the RPC accounting is actually 70%, v3's fee slice is overstated by ~1.43× (the 29% fee share is really ~22%). Verify the `qfc_getMinerEarnings` accounting on a healthy chain, then correct the model. See §6 conflict 6.

**Confidence: medium** (keeping 0% is internally consistent, but relies on the unverified assumption that inference fees will eventually take off).

---

## 3. Staking Thresholds

### 3.1 Validator

**Current values**:

| Item | Value | Source |
|---|---|---|
| Minimum stake | 10,000 QFC | `MIN_VALIDATOR_STAKE = 10^22 wei`; docs 03 and 12 agree |
| Protocol validator cap | 1,000 | `MAX_ACTIVE_VALIDATORS` |
| Doc 12 launch-period cap | 50 (policy layer) | Doc 12 §parameter recommendations, `max_validators = 50` |
| Per-validator stake share cap | 1% | `MAX_VALIDATOR_STAKE_PERCENT` |
| Doc 12 entity weight cap | 20% (policy layer) | `max_entity_weight = 0.20` |
| Unstaking delay | 7 days | `UNSTAKE_DELAY_SECS` |
| Minimum delegation | 100 QFC | `MIN_DELEGATION` |

**Proposed mainnet values**:
- Minimum stake: **keep 10,000 QFC**. All three docs and the constant fully agree — the least contested parameter in this draft. Anchor: doc 12's risk model is based on contribution weights, not absolute stake; the threshold only needs to filter sybils, not carry security duty.
- Launch-period validator cap: **50 (policy-layer admission), keep the protocol cap of 1,000 untouched** — adopt doc 12's Stage A scheme (official weight 25–30%, weekly admission batches ≤5).
- **Adopt doc 12's 20% entity weight cap (policy layer); `MAX_VALIDATOR_STAKE_PERCENT = 1%` must be changed before mainnet** — it is **mathematically incompatible** with a 50-validator launch set: 50 validators at ≤1% of total stake each sum to ≤50% < 100%, which has no solution. The constant is only satisfiable with ≥100 validators. See §6 conflict 4. **Proposed change: 20%** (aligned with doc 12's entity cap, still far below the 1/3 liveness threshold), to be lowered via governance as the network matures.

**Confidence**: minimum stake **high**; the cap system **medium** (the 1% → 20% change magnitude needs external review confirmation, and it must be checked whether the constant is actually enforced at all — if it never took effect, the testnet's 3 validators have long been in violation of it).

### 3.2 Inference Miner (separate from validator)

**Current values**:
- **Inference miner registration has no stake threshold** — no miner minimum-stake constant exists in `qfc-ai-coordinator/src/registry.rs` or associated code; registration is open.
- Exception for training tasks (AI-V3): dynamic stake floor = `slash_multiple(40) × per_step_reward × steps_per_epoch` (`training.rs`, ADR-0008). This is the "cheating is economically guaranteed to lose" security floor, not an admission threshold.

**Proposed mainnet value: keep the zero stake threshold for inference miners (deposit-free registration); keep the dynamic floor formula for training miners unchanged.**

Rationale (v3 numbers directly determine the direction):
- v3 survival condition 1: "miners must survive year 0", and the Y0 break-even table (OUTPUT.md) shows only $0-marginal-cost devices break even broadly: an idle laptop breaks even at any n, an idle VPS needs only $0.035 even at n=1,000, while an RTX 3060 already needs **$0.105** at n=500 and **$0.211** at n=1,000. The target population is low-cost device owners running it "on the side" — **any noticeable stake threshold would precisely drive away the only group that breaks even**.
- v3 conclusion verbatim: "below ~$0.02/QFC, only $0-marginal hardware should be onboarded past n≈100". The threshold must be zero or near zero.
- Anti-cheat does not rely on admission stakes: spot-checks (5% sampling) + InvalidInference slashing (§4) + the 40× dynamic floor on the training side already cover it. Sybil-flooding miners' returns are naturally suppressed by the 1/n dilution mechanism (extra registered identities do not increase FLOPS share).

**Open question (OQ-4)**: with a zero threshold, what does slashing a malicious miner actually seize? InvalidInference executes as "5% of stake", and a deposit-free miner's stake may be 0 ⇒ the slash amount is 0, leaving only a 6h jail. **This is a real mechanism gap**: either give inference miners a small deposit (e.g. 10–100 QFC, sized so as not to drive away VPS players), or change InvalidInference to an absolute-amount slash like the training side. Submit to external review for a ruling.

**Confidence**: the **direction** of a zero/near-zero threshold is **high** (directly supported by v3 data); the specific deposit amount is **low** (depends on observing real cheating behavior, of which there is currently none).

---

## 4. Slashing

### 4.1 Status inventory — three conflicting definitions, and never actually triggered

**The testnet has not experienced a single real slashing to date** (v3: pass rate 100%; three months of forking produced no slash records either — the fork itself in fact shows the double-sign/false-vote detection has never fired in battle). All severities below are paper values.

| Trigger | constants.rs (`SLASH_*`) | Runtime actual (`qfc-node/src/sync.rs` evidence distribution path, hardcoded) | Doc 02 |
|---|---|---|---|
| DoubleSign | 50% | **10% + jail 24h** | 50% + permanent ban |
| InvalidBlock | 10% | **5% + jail 12h** | 10% + 7 days |
| Censorship | 5% | **3% + jail 6h** | 5% + 3 days |
| Offline | 1% | 1% + jail 1h | 1% + 1 day |
| FalseVote | 2% | 2% + jail 2h | 2% + 1 day |
| InvalidInference | (no constant) | 5% + jail 6h | (not covered by 02; qfc-core CLAUDE.md Phase 7 records the same values) |
| InvalidTraining (AI-V3) | (no constant) | Absolute amount: `slash_multiple × per_step_reward`, default **40×** (`qfc-ps/lib.rs PsConfig::default`, ADR-0008/0009); goes only through the A5 absolute-amount path — sync.rs explicitly rejects it from the percentage path | (not covered) |

**Worse still, DoubleSign has a dual-path split**: the `DoubleSignEvidence` handling in `qfc-consensus/engine.rs` (with cryptographic evidence) executes at `SLASH_DOUBLE_SIGN_PERCENT` = 50% + **permanent jail**, while the generic `SlashingEvidence` gossip path in `sync.rs` hardcodes 10% + 24h for the same offense. Two punishments for one act, depending on which pipe the evidence travels. See §6 conflict 3.

### 4.2 Proposed mainnet values

**First principle: fix consistency before debating severity.** Before mainnet, all slash parameters must converge to constants.rs as the single source of truth, with hardcoding banned from runtime paths (InvalidInference should also get a constant).

Proposed severities (baselined on the constants.rs / doc 02 side, i.e. **the stricter one**):

| Trigger | Proposed slash | Proposed jail | Argument |
|---|---|---|---|
| DoubleSign | **50%** | **Permanent (appealable via governance)** | Double-signing is the bottom-line offense against consensus safety; the 10%/24h sync.rs path fines a 10,000 QFC staker only 1,000 QFC — insufficient to deter a fork attack. Aligning with the already-implemented engine.rs behavior is the smallest change |
| InvalidBlock | 10% | 7 days | Keep the constants/02 values; no data supports adjustment |
| Censorship | 5% | 3 days | Same as above; note: the **detection mechanism** for censorship does not yet exist, so this parameter is not actually enforceable in early mainnet — flagged honestly |
| Offline | **1%, but with a warning buffer** | 24h | Early-mainnet node operations are immature (our own testnet failed to converge for three months); immediate no-buffer slashing would harm honest small validators. Proposal: first offline event jails only, no slash; repeat offenses get the 1% |
| FalseVote | 2% | 24h | Keep |
| InvalidInference | 5% | 6h | Keep the implemented values; but **first close the zero-stake gap of §3.2 OQ-4**, otherwise this clause is a dead letter against deposit-free miners |
| InvalidTraining | **40 × per_step_reward (absolute amount), keep** | 6h (following v2.x convention, `training_verification.rs`) | ADR-0008's economic argument holds: at a 5% spot-check rate, making expected cheating returns negative requires a multiple ≥ 1/0.05 = 20; 40× provides a 2× safety margin. The mainnet value of `per_step_reward` is undecided (OQ-7) |

**Confidence: low** (except InvalidTraining's 40×, which has an explicit economic derivation and is **medium**, none of these severities have ever been tested by a real trigger — this must be disclosed honestly to external reviewers in REVIEW-REQUEST).

### 4.3 Open questions

- **OQ-5**: The **determination threshold** for Offline (how long without a heartbeat counts as offline) is absent from the constants layer; it must be defined and written into constants.rs before mainnet.
- **OQ-6**: The governance un-jailing process for permanent jail (doc 03's governance chapter has proposal types but does not cover "appeals").
- **OQ-7**: The mainnet value of `per_step_reward` is undecided; both InvalidTraining's actual deterrence and the training-miner stake floor scale with it.
- **OQ-8**: Destination of slashed funds — docs 02/03 say burn; whether the absolute-amount path in `settlement.rs` also burns must be confirmed during node integration (Phase 3.2).

---

## 5. One-Page Summary Table

Confidence: high = only needs confirmation; medium = direction grounded, number pending review; low = lacks real data, placeholder value.

| # | Parameter | Current value (source) | Proposed mainnet value | Confidence | Which external review it depends on |
|---|------|------------|-----------|------|--------------------|
| 1 | Initial block reward | 10 QFC/block (constants.rs) | Keep | High | Phase 1.3 economics review (confirmatory) |
| 2 | Halving schedule | Yearly halving ×4, floor 0.625 (constants.rs) | Keep | High | Same — the ramp math is a core REVIEW-REQUEST question |
| 3 | Year-0 clock | Years counted by height (producer.rs) | Reset at mainnet genesis; testnet progress does not carry over | High | No external review needed (protocol default behavior) |
| 4 | Supply | 1B initial / 2B cap (constants.rs) | Keep | High | Phase 1.3 (confirmatory) |
| 5 | PoC weights | 30/20/15/15/10/5/5 (constants.rs = doc 02) | Keep | Medium | Re-check after Phase 2 with ≥10 miners measured |
| 6 | Block reward split | 60/25/15 producer/voters/miners (constants.rs; docs 02/03 outdated) | Keep the 15% miner pool; verify measured pool ≥ 80% of theory (~31,000 QFC/day) in the first healthy-chain month | Medium | Phase 1.3 + re-run refresh.py after Phase 0 |
| 7 | Gas fee split | 47/28/20/5, miners 0% (constants.rs; doc 03 outdated) | Keep 0% (explicit decision); fallback: targeted subsidy from the treasury slice | Medium | Phase 1.3 must-answer question |
| 8 | Inference fee split | 70/10/20 miner/validators/burn (constants.rs) | Keep; first verify the v3 model accounting (100% vs 70%) | Medium | Healthy-chain RPC verification |
| 9 | Validator minimum stake | 10,000 QFC (constants.rs = 03 = 12) | Keep | High | Phase 1.3 (confirmatory) |
| 10 | Launch-period validator cap | Protocol 1,000 / policy 50 (doc 12) | Policy 50, relax per doc 12 stages A→C | Medium | Phase 1.3 |
| 11 | Per-validator stake share cap | 1% (constants.rs) — mathematically incompatible with a 50-validator launch set | **Change to 20%**, aligned with doc 12's entity cap | Medium | Phase 1.3 must-answer question |
| 12 | Minimum delegation / unstaking delay | 100 QFC / 7 days (constants.rs) | Keep | High | None |
| 13 | Miner stake threshold | None (deposit-free registration, registry.rs) | Keep zero threshold; small deposit (10–100 QFC) TBD | Direction high / number low | Phase 1.3 (OQ-4 gap) |
| 14 | Training stake floor | 40 × r × steps/epoch, dynamic (training.rs) | Keep formula; mainnet r undecided | Medium | Phase 1.3 + Phase 3.2 |
| 15 | DoubleSign | 50% (constants) vs 10%/24h (sync.rs) vs 50%+permanent (doc 02) | **50% + permanent jail**, converge to a single path | Low | Phase 1.3 + security audit (Phase 3.1) |
| 16 | InvalidBlock | 10% vs 5%/12h (same three-way inconsistency) | 10% + 7 days | Low | Same as above |
| 17 | Censorship | 5% vs 3%/6h | 5% + 3 days (detection mechanism missing, not enforceable for now) | Low | Same as above |
| 18 | Offline | 1% (all three agree; jail terms disagree) | 1% + 24h, first offense jail-only with no slash | Low | Same as above |
| 19 | FalseVote | 2% | 2% + 24h | Low | Same as above |
| 20 | InvalidInference | 5%/6h (hardcoded in sync.rs only, no constant) | Keep, add to constants.rs; close the zero-stake gap first | Low | Same as above |
| 21 | InvalidTraining | 40× (qfc-ps default, ADR-0008) | Keep 40× | Medium | Phase 1.3 (economic derivation independently checkable) |

---

## 6. Conflict Register (doc / constant / runtime inconsistencies to be eliminated before mainnet)

1. **Block reward split**: constants.rs + producer.rs implement 60/25/15 (with a miner pool); doc 02 §block reward distribution and doc 03's income formula say 70/30 with no miner share. Docs 02/03 are outdated (70/30 is now only the "flow-back ratio of the miner pool when there are no proofs"). → Revise docs 02/03.
2. **Gas fee split**: constants.rs 47/28/20/5 (with 5% treasury); doc 03 says 50/30/20 with no treasury. → Revise doc 03.
3. **Three-way slashing split**: constants.rs `SLASH_*` (50/10/5/1/2) is never used by the evidence distribution path — `sync.rs` hardcodes a different set (10/5/3/1/2 + hour-scale jail); doc 02 has yet a third set of jail terms (day-scale/permanent). DoubleSign additionally has a dual path (engine.rs 50%+permanent vs sync.rs 10%+24h). → Converge to constants.rs as the single source of truth before mainnet (§4.2).
4. **`MAX_VALIDATOR_STAKE_PERCENT = 1%` is mathematically incompatible with doc 12's launch scheme**: 50 validators at ≤1% each ⇒ total stake ≤50%, no solution. Moreover, if the constraint were in effect, the testnet's 3 validators would already violate it — confirm whether it is enforced at all. → Change to 20%, or confirm it is dead code and re-set it.
5. **Internal contradiction in doc 03**: the inflation table computes with ~9.46M blocks/year (3.333 s), but the footnote says "one block every 3 seconds, ~10,512,000 blocks per year". → Fix the footnote.
6. **Inference fee accounting**: the v3 model credits 0.1 QFC/task 100% to miners; the protocol says `INFERENCE_FEE_MINER_PERCENT = 70`. If 70% is real, v3's fee slice is overstated ~1.43×, and the Y0 fee share drops 29% → ~22% (each year's fee-share curve shifts down in step, but the structural conclusion of §1.2 is unchanged). → Verify the `qfc_getMinerEarnings` accounting on a healthy chain, then fix the model.
7. **`calculate_year()` comment error**: "~262,800 blocks per year" should be ~9,462,046. The code is correct; only the comment misleads. → Fix the comment.

---

## 7. Consolidated Open Questions for External Review (for citation by REVIEW-REQUEST.md)

| # | Question | Section |
|---|------|--------|
| OQ-1 | Halving counted by height: block-time drift shifts halvings' wall-clock timing — acceptable? | §1.4 |
| OQ-2 | The dynamic `reward_multiplier` is not in the v3 model; its value range must be bounded | §1.4 |
| OQ-3 | Inference fee miner accounting: 100% (model assumption) or 70% (protocol constant)? | §2.3 |
| OQ-4 | Deposit-free inference miners make InvalidInference's "5% of stake" slash zero — small deposit, or switch to absolute-amount slashing? | §3.2 |
| OQ-5 | Offline determination threshold undefined | §4.3 |
| OQ-6 | Governance appeal/un-jail process for permanent jail | §4.3 |
| OQ-7 | Mainnet value of `per_step_reward` (determines training slash absolute amounts and the stake floor) | §4.3 |
| OQ-8 | Destination of slashed funds (burn vs treasury) unconfirmed on the absolute-amount path | §4.3 |
| Core question | Can the 15% miner pool + halving ramp keep miners alive until the fee-dominated era in the "n≈100–500, token price $0.02–0.10" range? (v3 break-even table as evidence) | §2.2 / REVIEW-REQUEST |

**Every number that depends on real demand** (the absolute trajectory of fee shares, the absolute mainnet target for the miner pool, deposit amounts) cannot responsibly be given today while demand is zero (`unique_submitters_last_100 = 0`); this draft uniformly marks them confidence = low and defers them to Phase 2 measured data — no false precision is manufactured.

---

*This draft is derived from the Phase 1.1 v3 model (`miner-economics/refresh.py`, 2026-07-04) and the qfc-core protocol constants (verified the same day). Next step: Phase 1.3 — put this draft + MINER-ECONOMICS v3 in front of 1–2 practicing PoS/DePIN economists.*
