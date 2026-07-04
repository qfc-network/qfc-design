# QFC Miner Economics — Sobering Reality Check

> Measured on 2026-04-14 against live testnet (chain 9000, v2.2.3).
> Source data: `qfc_getMinerEarnings`, `qfc_getInferenceStats`, `qfc_listPublicTasks`, `qfc_getValidators`, `qfc_getRegisteredMiners`.
> Model + full tables: [`model.py`](./model.py) and [`OUTPUT.md`](./OUTPUT.md).

---

## TL;DR (for Gap C of 42-CORE-GAPS)

At today's task demand (~8,600 inferences/day, ~$0 in USD-terms from fees) QFC's miner rewards are **75% block-reward inflation, 25% user fees**.

**Major update vs first version of this doc** — the emission schedule is not constant. Per `qfc-core/crates/qfc-types/src/constants.rs`:

- Year 0: 10 QFC/block
- Halves yearly through year 4
- Floor: 0.625 QFC/block from year 4 onward (1/16 of year 0)

This changes the verdict. **At today's 8,600 tasks/day and zero demand growth, the chain hits 39% fee-share by year 4 purely from emission decay.** Demand growth is no longer an existence requirement; it's the difference between "OK" and "good."

Revised verdict: **Gap C passes conditionally** — the emission schedule already plans for its own sunset. Two conditions still matter:

1. **Miners must survive year 0 with 1/n-of-inflation dilution.** At n=100 and token price < $0.05, RTX 3060 rigs bleed. A hardware-mix that skews toward cheap laptops / VPSs (per Gap A onboarding) matters more than previously thought — because only those break even in year 0.
2. **Demand has to show up before miner count grows past ~500.** If we onboard 1,000 miners in month 1 with no demand signal, early joiners quit before fees take over. Pace matters.

What I was wrong about in v1: I treated inflation as perpetual. It isn't — it halves on a strict schedule. The "fragile" framing was too harsh.

What still matters for Gap C's T+4 week review: get someone external to sanity-check the halving plus ramp math, not the "is this model doomed" question.

---

## 1. Baseline — what the chain actually pays today

| Metric | Value | Source |
|---|---|---|
| Active inference miners | **1** | `qfc_getRegisteredMiners` shows 3 registered, only `0xdb7c460a...` executes tasks |
| Daily reward to that miner | **3,427 QFC** | `qfc_getMinerEarnings(..., "day")` |
| Daily tasks completed network-wide | **8,635** | Same — single active miner gets all of them |
| Fee per inference task | **0.1 QFC** | `qfc_listPublicTasks` — every task's `maxFee` was `0x16345785d8a0000` |
| Pass rate | 100% | `qfc_getInferenceStats.passRate` |
| Task volume (all-time) | 259,152 | `qfc_getInferenceStats.tasksCompleted` |

### Breakdown of the 3,427 QFC/day

- **Fees captured**: 8,635 × 0.1 = **864 QFC/day (25%)**
- **Inflation subsidy**: remaining **2,563 QFC/day (75%)**

The inflation slice is what keeps miners fed while demand is low. It is **supply-side subsidy** paid by every QFC holder (via dilution). This is fine during bootstrap. It becomes a problem if demand never catches up.

### Who is paying the fees?

Only **2 submitter addresses** across all listed public tasks, both clearly internal. **There are no external users paying for inference yet.**

This is Gap B in the same 42-CORE-GAPS doc. It is real, not hypothetical.

---

## 2. How rewards scale as miners join

We assume the inflation pool stays constant (network-wide) and splits roughly 1/n among miners. PoC weights things unequally, but 1/n is the optimistic upper-bound for a new miner.

| Miners | QFC/day per miner | As % of today |
|-------:|------------------:|---------------:|
| 1      | 3,427  | 100% |
| 10     |   343  | 10%  |
| 100    |    34  | 1%   |
| 500    |     7  | 0.2% |
| 1,000  |   3.4  | 0.1% |
| 10,000 |   0.3  | 0.01% |

The "10 miners earn 343 QFC/day each" is healthy — at even $0.01/QFC that's $3.43/day, enough to cover a home PC's electricity with profit. But this is where the realistic celebration ends.

---

## 3. Break-even by hardware tier

Daily opex (electricity at $0.15/kWh + hardware amortization):

| Hardware | Watts | Amort (USD/yr) | Opex USD/day |
|---|---:|---:|---:|
| Cheap VPS (4vCPU CPU-only) | 0 | $72 (rental) | $0.20 |
| Old laptop (2017 Intel MBP) | 45 | $0 (owned) | $0.16 |
| Apple M2 Mac mini | 20 | $150 | $0.48 |
| RTX 3060 home rig | 180 | $167 | $1.10 |
| RTX 4090 rig | 450 | $600 | $3.26 |
| A100 40GB (rented hourly) | 300 | $9,636 | $27.48 |

**Token price needed to break even** (miners share 1/n of today's emission + fee pool):

| Hardware | n=10 | n=100 | n=1,000 |
|---|---|---|---|
| Old laptop | $0.0005 | $0.0047 | $0.05 |
| Cheap VPS | $0.0006 | $0.0058 | $0.06 |
| M2 Mac mini | $0.0014 | $0.014 | $0.14 |
| RTX 3060 | $0.0032 | $0.032 | **$0.32** |
| RTX 4090 | $0.010 | $0.095 | $0.95 |
| A100 rented | $0.080 | **$0.80** | $8.02 |

The bolded cells are the realistic ones: if we get **100 RTX 3060 miners at token price $0.03** or **100 A100 miners at $0.80**, the economics work.

At **1,000 miners on $0.05 token price**, only laptop/VPS hobbyists break even. GPU rigs and cloud rentals lose money.

---

## 4. Demand-side: how much does fee growth rescue the picture?

Fix 100 miners on RTX 3060 hardware. Scale task volume:

| Tasks/day | $0.01/QFC | $0.10/QFC | $1.00/QFC |
|----------:|----------:|----------:|----------:|
|       1,000 | −$0.84 | +$1.56 | +$25.53 |
|      10,000 | −$0.75 | +$2.46 | +$34.53 |
|     100,000 | +$0.15 | +$11.46 | +$124.53 |
|   1,000,000 | +$9.15 | +$101.46 | +$1,024.53 |

**Key insight:** multiplying demand 10× barely moves the needle when the inflation pool is the dominant income source. What really dominates is **token price × miner count**. This tells us:

- Emission schedule is currently *too generous* relative to fees. A few days' inflation already exceeds the entire fee volume of the chain's lifetime.
- We either lower inflation (risk: miners quit before fees catch up) or grow paid inference demand by 100×+ to matter economically.

---

## 5. What has to be true for QFC to survive this math

Pick at least one:

1. **Paid inference demand reaches ≥ 100,000 tasks/day within 6 months.** This means real external customers, not our own bots. At $0.10 fee per task that's $10/day × 365 ≈ $3.6k/year in honest revenue — still small in absolute terms, but it changes the subsidy/fee ratio from 75/25 to something defensible.
2. **Token price finds a floor ≥ $0.05 before miner population grows past ~500.** This gives cheap-hardware miners (laptop, VPS, M2 mini) profitable operation during the ramp.
3. **Emission schedule is redesigned** to taper inflation and make fees dominant by ~N=100 miners. This is a protocol-level change (token economics parameters + governance) and the hardest of the three.

**None of these look easy today.** Path 1 is Gap B of the same doc. Path 2 requires real token-listing + liquidity, which is a business problem. Path 3 is a technical redesign.

---

## 6. Conservative 6-month milestones (proposed)

| Milestone | Target | What it tells us |
|---|---|---|
| T+4 weeks | Fee share ≥ 40% of total miner reward | Demand is actually building |
| T+8 weeks | ≥ 10 external miners surviving ≥ 7 days | Path 2 is tractable (people find the economics worthwhile) |
| T+12 weeks | ≥ 1 miner profitable on GPU (not laptop) | Pro tier viable |
| T+16 weeks | Inflation share can drop 25% without miners leaving | Real fee-driven economy emerging |

Missing any 2 of 4 of these → admit the miner model isn't working and pivot (centralized inference API with verifiability, or paid SaaS wrapper around current infra).

---

## 7. Data gaps / things this model still doesn't model

**Resolved since v1:**

- ✅ **Emission schedule** — verified in `qfc-core/crates/qfc-types/src/constants.rs`: 10 QFC/block → halves yearly → floor at 0.625 QFC/block after year 4. Model now uses this.
- ✅ **Stake denomination** — wei (standard 10^18). Mainnet min validator stake is 10,000 QFC = 10^22 wei. Testnet validators show `0xf4240` (1,000,000 wei, essentially 0 QFC) — that's a testnet-only placeholder, not the mainnet config.
- ✅ **Vesting** — 7-day cliff + 23-day linear unlock (total 30 days from earn). Enforced in `qfc_getMinerVesting`. In steady state (past day 30), liquid income ≈ daily earnings. Startup lag only.

**Still assumed / unmodeled:**

- **Block reward split between validators and miners**: today's measurement showed one miner earning 3,427 QFC/day. Network-wide year-0 emission is 45,470 QFC/day. So one miner gets 7.5% of total emission. This means there's a separate allocation rule between validators (who produce blocks) and inference miners (who serve tasks) that the model doesn't yet capture. For the Gap C review, a reviewer would want this split explicit.
- **Slashing**: haven't simulated slash events. Today's pass rate is 100% — model assumes no honest miner gets slashed.
- **Model diversity**: only 3 models are approved (`qfc-embed-small`, `qfc-embed-medium`, `qfc-classify-small`). All embedding. Per the companion [PROPOSAL-LLM-MODEL-CATALOG.md](../PROPOSAL-LLM-MODEL-CATALOG.md), adding an LLM increases fee-per-call 10-100× and the demand-scale curve above becomes much kinder.
- **Gas consumption from non-inference traffic**: transfers, DEX swaps, NFT mints also generate protocol fees. Not in the model because they don't pay miners — they burn or go to validators.

---

## 8. How to reproduce

```bash
cd qfc-design/miner-economics
python3 model.py          # Markdown tables to stdout
python3 model.py --json   # Raw numbers as JSON
```

Update the `BASELINE_*` constants at the top of `model.py` to re-run with fresh measurements from the RPC.

---

## Decision (recommended)

Take this model to 1–2 people who've done PoS / mining economics before (Cosmos validator operators, Akash folks, former Ethereum researchers). Ask them specifically:

> "If an L1 pays 75% inflation + 25% fees, and fees are zero external today, at what token price + miner count does the unit economics become self-sustaining? Is QFC's current path credibly toward that?"

If 2 out of 2 say "this doesn't close without redesigning emissions or finding demand," then Gap C has failed and the 42-CORE-GAPS kill criteria triggers at the T+4 week mark.

If at least one sees a plausible path, we scope the redesign and keep going.

---

## v3 refresh (2026-07-04)

> Refresh per Phase 1.1 of `44-L1-MASTER-PLAN-CN.md`. Model: [`refresh.py`](./refresh.py) (offline, stdlib-only); tables regenerated in [`OUTPUT.md`](./OUTPUT.md). Everything above this section is the v2 analysis, kept as-is for the record.

### Data-quality caveat — read this before the numbers

Unlike v2, this refresh does **not** query the live RPC. The testnet has been in a 3-way consensus fork (three validators, three independent chains) for the entire snapshot period, and was hard-reset with fresh genesis on **2026-06-18** and again on **2026-06-27**. Every number below comes from `snapshots.jsonl` — 12 weekly Gap C snapshots (2026-04-13 → 2026-06-28) — and each snapshot reflects whichever forked node answered that week. The `all_time_*` counters are visibly discontinuous (548,504 on 05-17 → 131,495 on 06-07 → 22,931 on 06-21 → 6,790 on 06-28), 4 of 12 snapshots are all-zero (RPC down or node mid-reset), and on 06-28 both miners report identical task counts and earnings — plausibly the same task queue served on separate fork branches, i.e. some double-counting. I treat the series as **indicative, not authoritative**. Live numbers would be worse, not better: they'd be authoritative-looking and still wrong.

### What changed vs v2

1. **Twelve weeks of observation instead of a single-day measurement.** The three pre-fork snapshots (April) were remarkably stable: ~17,280 tasks/day, ~6,700 QFC/day pool, fee share 25.6–26.2% — v2's 25% assumption was accurate when the chain was healthy.
2. **Fee share observed at 0.29 on 06-28** vs 0.25 assumed in v2. Before celebrating: it rose for the *wrong reason*. Fees didn't grow — the inflation-side pool shrank (4,990 → 3,324 QFC/day) because the forked chain produces blocks erratically. Demand-funded progress looks identical to supply-side decay in this one ratio; the decomposition matters.
3. **miners_registered went 3 → 0 → 2** across the resets. The two survivors (`0xdb7c460a…`, `0xca8d86c4…`) re-registered after the 06-27 reset; the third address (`0x31ca8b60…`) never earned anything in any snapshot and is gone. n=2 is today's real miner count, so the tables now start at n=2.
4. **Model basis changed.** v2 modeled the single active miner's earnings as the pool; v3 uses the network-wide miner reward pool from the 06-28 snapshot (4,681.69 QFC/day = 3,323.69 inflation + 1,358 fees), splits it 1/n, and decays the inflation slice on the halving schedule. The n=2 year-0 cell reproduces the observed per-miner 2,340.84 QFC/day to within 0.1%, which is the one consistency check the forked data allows.
5. **Constants re-verified** against `qfc-core/crates/qfc-types/src/constants.rs` (2026-07-04): 10 QFC/block, yearly halving, 0.625 floor — unchanged. One thing I hadn't recorded in v2: the protocol *gas*-fee split (47/28/20/5 producer/voters/burn/treasury) allocates **0% to inference miners**. Miner fee income is exclusively inference task fees (`maxFee`, 0.1 QFC/task), a separate flow. The model was already treating it that way, but now it's explicit.

### Does "conditional pass" still hold?

**Yes.** The verdict rested on a structural fact — the emission schedule sunsets itself — and that fact is protocol code, not testnet telemetry. At the refreshed baseline and *zero* demand growth, the miner-pool fee share goes 29% (Y0) → 45% (Y1) → 62% (Y2) → 87% (Y4) purely from halving. The chain becomes demand-funded on schedule even if demand never grows, at the cost of the pool shrinking to a third of today.

The master plan's abandonment gate was "refresh concludes token price > $10 needed for anyone to run." The worst realistic cell is a rented datacenter GPU at n=1,000 needing $2.11 — bad, but an order of magnitude inside the gate, and nobody should run rented A100s on this chain anyway. The gate does not trigger.

What the refresh *does* sharpen: the demand side got worse, not better. `unique_submitters_last_100` is now 0 (was 2–3 internal in April). There are not even internal-looking submitters in the window anymore; the 13,580 tasks/day are pure self-generated load. Gap B remains the actual existential issue — this model just prices what miners earn while we wait.

### The two survival conditions, restated with refreshed numbers

1. **Miners must survive year 0 on 1/n of a 4,682 QFC/day pool.** Refreshed breakevens (Y0): at n=100, an RTX 3060 rig needs ≥ **$0.021** (v2 said $0.032 — looks better only because the pool basis changed); at n=500 it needs **$0.105** and at n=1,000 **$0.211**. Idle VPS needs $0.0035 / $0.018 / $0.035 at n=100/500/1,000; an already-owned laptop is free at any n. The v2 conclusion stands, slightly sharpened: **below ~$0.02/QFC, only $0-marginal hardware should be onboarded past n≈100**, and GPU recruitment before a price floor exists is how we churn early miners.
2. **Demand must show up before miner count grows past ~500.** At n=500, year 0, the per-miner reward is 9.36 QFC/day — $0.47/day at $0.05. That covers a VPS ($0.16/day) and nothing else. By year 1 it's 6.04 QFC/day. Unless task fees grow several-fold by then, every miner beyond the hobbyist tier at n≥500 is underwater at any price below $0.10. Pace of onboarding still matters more than total count.

### What this refresh cannot tell us

- Whether the April-era ~17k tasks/day or the post-reset 13.6k/day is the "real" steady state — both are internal load generators, on a forked chain.
- Anything about PoC weighting in practice: with 2 miners splitting exactly 50/50, the 1/n assumption is untested above n=2.
- Whether the theoretical inference-miner pool (15% of block rewards ≈ 38,900 QFC/day at nominal 3.333 s blocks) would be reached on a healthy chain — observed is ~12× lower. If the consensus fix lands and block production normalizes, the year-0 pool could be substantially *larger* than modeled here, which would loosen condition 1 and tighten nothing. Re-run `refresh.py` against the first month of post-fix snapshots before quoting these tables externally.

Next step is unchanged and is not a modeling step: **1.3 — put this in front of one or two people who have done PoS/DePIN economics** (REVIEW-REQUEST.md is written; it needs to be sent). The refresh strengthens the case that the question for them is the ramp math, not existential doom.

### How to reproduce (v3)

```bash
cd qfc-design/miner-economics
python3 refresh.py            # Markdown tables to stdout
python3 refresh.py --write    # regenerate OUTPUT.md
python3 refresh.py --json     # raw numbers
```

No network access required or wanted — the model reads `snapshots.jsonl` and hard-codes the verified protocol constants, with sanity checks (`## Sanity checks` in OUTPUT.md) asserting internal consistency on every run.
