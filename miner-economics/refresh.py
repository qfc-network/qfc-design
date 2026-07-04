#!/usr/bin/env python3
"""
QFC Miner Economics Model — v3 refresh (2026-07-04)
====================================================
Runs fully OFFLINE. No RPC calls — the testnet is currently in a 3-way
consensus fork (see project_testnet_consensus_fork), so live numbers are
unreliable by construction. Inputs are:

  1. snapshots.jsonl — 12 weekly Gap C snapshots (2026-04-13 → 2026-06-28)
     collected by snapshot.py while the RPC was reachable.
  2. Protocol constants, verified 2026-07-04 against
     qfc-core/crates/qfc-types/src/constants.rs (read-only).

Data-quality caveat (repeated in the output header): the chain was
hard-reset with fresh genesis on 2026-06-18 and again on 2026-06-27, and
has been running as 3 independent forked chains the entire period. All
all_time_* counters are discontinuous and each snapshot reflects whichever
forked node answered. The series is indicative, not authoritative.

Usage:
  python3 refresh.py            # Markdown to stdout
  python3 refresh.py --write    # regenerate OUTPUT.md in place
  python3 refresh.py --json     # raw numbers as JSON

Plain python3, stdlib only.
"""

from __future__ import annotations
import argparse
import json
import math
import os
import sys
from dataclasses import dataclass

HERE = os.path.dirname(os.path.abspath(__file__))
SNAPSHOTS_PATH = os.path.join(HERE, "snapshots.jsonl")
OUTPUT_PATH = os.path.join(HERE, "OUTPUT.md")

# ---------------------------------------------------------------------------
# Protocol constants
# Source of truth: qfc-core/crates/qfc-types/src/constants.rs
# (verified 2026-07-04; do not edit these without re-checking the file)
# ---------------------------------------------------------------------------
BLOCK_REWARD_YEAR_0_QFC = 10.0        # BLOCK_REWARD = 10^19 wei
MIN_BLOCK_REWARD_QFC = 0.625          # MIN_BLOCK_REWARD, floor after 4 halvings
HALVING_PERIOD_YEARS = 1              # HALVING_PERIOD_YEARS
BLOCK_TIME_MS_NOMINAL = 3333          # BLOCK_TIME_MS (nominal; fork-degraded in practice)
INFERENCE_MINERS_REWARD_PERCENT = 15  # share of block reward routed to inference miners
FEE_PER_TASK_QFC = 0.1                # observed maxFee on every public task (unchanged since v2)

# NOTE on protocol fee split: FEE_PRODUCER/VOTERS/BURN/TREASURY = 47/28/20/5.
# That sums to 100 — inference miners get 0% of *gas* fees. The "fees" in this
# model are inference task fees (maxFee paid by submitters), a separate flow.


def emission_multiplier(year: int) -> float:
    """Block reward for a given year as a fraction of year 0 (halves yearly, floored)."""
    r = BLOCK_REWARD_YEAR_0_QFC / (2 ** max(0, year))
    return max(r, MIN_BLOCK_REWARD_QFC) / BLOCK_REWARD_YEAR_0_QFC


# ---------------------------------------------------------------------------
# Snapshot loading (offline baseline)
# ---------------------------------------------------------------------------

@dataclass
class Snapshot:
    date: str
    miners_registered: int
    daily_tasks: int
    daily_earnings_qfc: float
    daily_fees_qfc: float
    daily_inflation_qfc: float
    fee_share: float
    all_time_tasks: int
    per_miner: list

    @property
    def usable(self) -> bool:
        """A snapshot with zero earnings means the RPC was down or the node
        had just been reset — not that the economy was actually zero."""
        return self.daily_earnings_qfc > 0


def load_snapshots(path: str = SNAPSHOTS_PATH) -> list[Snapshot]:
    snaps = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            snaps.append(Snapshot(
                date=d["date"],
                miners_registered=d.get("miners_registered", 0),
                daily_tasks=d.get("daily_tasks", 0),
                daily_earnings_qfc=d.get("daily_earnings_qfc", 0.0),
                daily_fees_qfc=d.get("daily_fees_qfc_estimated", 0.0),
                daily_inflation_qfc=d.get("daily_inflation_qfc_estimated", 0.0),
                fee_share=d.get("fee_share_of_reward", 0.0),
                all_time_tasks=d.get("all_time_tasks", 0),
                per_miner=d.get("per_miner", []),
            ))
    return snaps


# ---------------------------------------------------------------------------
# Hardware classes (v3 — simplified to the four classes that matter for
# onboarding; v2's electricity+amortization split collapsed into one
# monthly-opex number per class, reusing v2 assumptions where sensible)
# ---------------------------------------------------------------------------

@dataclass
class Hardware:
    name: str
    opex_usd_month: float
    note: str

HARDWARE = [
    Hardware("Idle VPS (4vCPU, already rented)", 5.0,
             "~$5/mo rental; v2's 'Cheap VPS' was $6/mo"),
    Hardware("Laptop (already owned, idle)", 0.0,
             "$0 marginal cost — v2's 'Old laptop' had $0.16/day power; "
             "treated as $0 here per refreshed assumption"),
    Hardware("RTX 3060 home rig", 30.0,
             "~$30/mo power (180W @ $0.15/kWh ≈ $19.4/mo + amort); v2 said $1.10/day ≈ $33/mo"),
    Hardware("Datacenter GPU (A100-class, rented)", 300.0,
             "$300+/mo; v2's A100 hourly rental was $27.5/day ≈ $825/mo — $300 is the charitable end"),
]


def daily_opex_usd(hw: Hardware) -> float:
    return hw.opex_usd_month * 12 / 365


# ---------------------------------------------------------------------------
# Reward model
# ---------------------------------------------------------------------------
# Pool basis (changed vs v2): v2 modeled the single active miner's earnings as
# the pool. v3 uses the network-wide miner reward pool from the latest usable
# snapshot: inflation slice scales with the halving schedule; the fee slice is
# held at observed demand (no growth assumed). Split 1/n — optimistic upper
# bound for a new miner, since PoC/FLOPS weighting is uneven in practice.

def miner_pool_qfc_day(baseline: Snapshot, year: int) -> tuple[float, float]:
    """(inflation_pool, fee_pool) network-wide QFC/day for a given year."""
    return (baseline.daily_inflation_qfc * emission_multiplier(year),
            baseline.daily_fees_qfc)


def per_miner_qfc_day(baseline: Snapshot, n: int, year: int) -> float:
    infl, fee = miner_pool_qfc_day(baseline, year)
    return (infl + fee) / n


def breakeven_price_usd(daily_reward_qfc: float, opex_usd_day: float) -> float:
    if daily_reward_qfc <= 0:
        return float("inf")
    return opex_usd_day / daily_reward_qfc


# ---------------------------------------------------------------------------
# Sanity checks (deliverable 4)
# ---------------------------------------------------------------------------

def sanity_check(baseline: Snapshot, miners: list[int], years: list[int],
                 prices: list[float]) -> list[str]:
    checks = []

    def ok(cond: bool, label: str):
        checks.append(("PASS" if cond else "FAIL") + f" — {label}")
        if not cond:
            raise AssertionError(f"Sanity check failed: {label}")

    # No negative / NaN rewards anywhere in the grid
    vals = [per_miner_qfc_day(baseline, n, y) for n in miners for y in years]
    ok(all(v > 0 and not math.isnan(v) for v in vals),
       f"all {len(vals)} per-miner reward cells positive and finite")

    # Emission multipliers monotone non-increasing, floored at 1/16
    ms = [emission_multiplier(y) for y in range(0, 8)]
    ok(all(a >= b for a, b in zip(ms, ms[1:])) and ms[-1] == 0.0625,
       "emission multipliers monotone, floor = 1/16 from year 4")

    # Baseline internal consistency: fees + inflation = earnings (±0.01)
    ok(abs(baseline.daily_fees_qfc + baseline.daily_inflation_qfc
           - baseline.daily_earnings_qfc) < 0.01,
       "baseline fees + inflation = total earnings")

    # Observed fee share matches recomputed value (±0.005)
    ok(abs(baseline.daily_fees_qfc / baseline.daily_earnings_qfc
           - baseline.fee_share) < 0.005,
       f"recomputed fee share ≈ snapshot value ({baseline.fee_share})")

    # Breakeven math round-trips: breakeven_price × QFC/day = opex
    for hw in HARDWARE:
        opex = daily_opex_usd(hw)
        if opex == 0:
            continue
        r = per_miner_qfc_day(baseline, 100, 0)
        be = breakeven_price_usd(r, opex)
        ok(abs(be * r - opex) < 1e-9, f"breakeven round-trip for {hw.name}")

    # n=2 year-0 model output matches the observed per-miner split on 06-28
    modeled = per_miner_qfc_day(baseline, 2, 0)
    observed = baseline.per_miner[0]["day_qfc"] if baseline.per_miner else 0
    ok(abs(modeled - observed) / observed < 0.001,
       f"n=2 Y0 model ({modeled:.2f}) matches observed per-miner earnings ({observed:.2f})")

    return checks


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

MINERS = [2, 10, 100, 500, 1000]      # n=2 is today
PRICES = [0.01, 0.05, 0.10, 0.50]
YEARS = [0, 1, 2, 3, 4]


def render(snaps: list[Snapshot]) -> str:
    usable = [s for s in snaps if s.usable]
    baseline = usable[-1]
    out = []
    w = out.append

    w("# QFC Miner Economics — model output (v3, 2026-07-04)\n")
    w("> Generated offline — no live RPC (testnet is in a 3-way consensus fork; "
      "live numbers are unreliable).")
    w("> Command: `cd miner-economics && python3 refresh.py --write`")
    w("> Inputs: `snapshots.jsonl` (12 weekly Gap C snapshots, "
      f"{snaps[0].date} → {snaps[-1].date}) + protocol constants verified against "
      "`qfc-core/crates/qfc-types/src/constants.rs`.\n")
    w("> **Data-quality caveat:** the chain was hard-reset with fresh genesis on "
      "2026-06-18 and again on 2026-06-27, and has run as 3 independent forked "
      "chains for the whole snapshot period. `all_time_*` counters are "
      "discontinuous and each snapshot reflects whichever forked node answered. "
      "Treat the series as indicative, not authoritative.\n")

    # -- snapshot series ----------------------------------------------------
    w("## Snapshot series (12 weeks)\n")
    w("| Date | Miners reg. | Tasks/day | Earnings QFC/day | Fee share | All-time tasks | Note |")
    w("|------|------------:|----------:|-----------------:|----------:|---------------:|------|")
    notes = {
        "2026-05-03": "RPC down / node reset — all zeros",
        "2026-05-10": "RPC down / node reset — all zeros",
        "2026-05-24": "RPC down / node reset — all zeros",
        "2026-05-31": "RPC down / node reset — all zeros",
        "2026-06-07": "validators up, miners deregistered; all_time reset ~06-05",
        "2026-06-14": "same — no miner earnings",
        "2026-06-21": "post 06-18 genesis reset; counter restarted",
        "2026-06-28": "post 06-27 genesis reset; **baseline for v3**",
    }
    for s in snaps:
        fs = f"{s.fee_share:.1%}" if s.usable else "—"
        w(f"| {s.date} | {s.miners_registered} | {s.daily_tasks:,} | "
          f"{s.daily_earnings_qfc:,.0f} | {fs} | {s.all_time_tasks:,} | "
          f"{notes.get(s.date, '')} |")
    w("")
    w(f"Only {len(usable)} of {len(snaps)} snapshots are usable (non-zero). "
      "Observed fee share across usable snapshots: "
      f"{min(s.fee_share for s in usable):.3f}–{max(s.fee_share for s in usable):.3f} "
      "(v2 assumed 0.25).\n")

    # -- baseline -----------------------------------------------------------
    w(f"## Baseline (latest usable snapshot: {baseline.date})\n")
    w(f"- Active miners: **{len(baseline.per_miner)}** (both earning identical "
      "amounts — even split)")
    w(f"- Network miner reward pool: **{baseline.daily_earnings_qfc:,.2f} QFC/day**")
    w(f"- Daily tasks: {baseline.daily_tasks:,} (sum of per-miner counts; both "
      "miners report the same 6,790 — possible fork double-count)")
    w(f"- Fee slice: {baseline.daily_fees_qfc:,.1f} QFC/day "
      f"({baseline.fee_share:.0%} of reward; fee = {FEE_PER_TASK_QFC} QFC/task)")
    w(f"- Inflation slice: {baseline.daily_inflation_qfc:,.2f} QFC/day")
    w("- External paying users: still **zero** (`unique_submitters_last_100` = 0)")
    w("")
    w("Model basis (changed vs v2): pool = network-wide miner rewards from this "
      "snapshot. Inflation slice scales with the halving schedule; fee slice held "
      "at observed demand (no growth assumed). Split 1/n across miners.\n")

    # -- emission schedule ----------------------------------------------------
    w("## Emission schedule (protocol constants)\n")
    w("| Year | QFC/block | × of Y0 | Miner inflation pool QFC/day | Fee share at constant demand |")
    w("|-----:|----------:|--------:|-----------------------------:|-----------------------------:|")
    for y in YEARS + [5]:
        m = emission_multiplier(y)
        infl, fee = miner_pool_qfc_day(baseline, y)
        share = fee / (fee + infl)
        w(f"| {y} | {BLOCK_REWARD_YEAR_0_QFC * m:.4f} | {m:.4f} | {infl:,.1f} | {share:.1%} |")
    w("")
    w(f"Nominal block time {BLOCK_TIME_MS_NOMINAL} ms and "
      f"{INFERENCE_MINERS_REWARD_PERCENT}% inference-miner share imply a "
      "theoretical Y0 miner pool of "
      f"{86_400_000 / BLOCK_TIME_MS_NOMINAL * BLOCK_REWARD_YEAR_0_QFC * INFERENCE_MINERS_REWARD_PERCENT / 100:,.0f} "
      "QFC/day — the observed pool is far below that because the forked chain "
      "produces blocks erratically. The model uses the *observed* pool.\n")

    # -- per-miner QFC table --------------------------------------------------
    w("## Per-miner daily reward (QFC/day), by miner count × year\n")
    w("Constant demand (13,580 tasks/day @ 0.1 QFC); inflation halves per schedule.\n")
    w("| Miners | " + " | ".join(f"Y{y}" for y in YEARS) + " |")
    w("|-------:|" + "|".join(["---------:"] * len(YEARS)) + "|")
    for n in MINERS:
        cells = " | ".join(f"{per_miner_qfc_day(baseline, n, y):>9,.2f}" for y in YEARS)
        label = f"{n:,} (today)" if n == 2 else f"{n:,}"
        w(f"| {label} | {cells} |")
    w("")

    # -- USD tables -------------------------------------------------------------
    for y in (0, 4):
        w(f"## Per-miner daily gross revenue (USD/day), year {y}\n")
        w("| Miners | " + " | ".join(f"${p:.2f}" for p in PRICES) + " |")
        w("|-------:|" + "|".join(["--------:"] * len(PRICES)) + "|")
        for n in MINERS:
            r = per_miner_qfc_day(baseline, n, y)
            cells = " | ".join(f"${r * p:>8,.2f}" for p in PRICES)
            w(f"| {n:,} | {cells} |")
        w("")

    # -- breakeven --------------------------------------------------------------
    w("## Year-0 breakeven token price (USD) by hardware class\n")
    w("Price at which daily reward covers daily opex. Bold = the realistic "
      "danger zone (n ≥ 500).\n")
    w("| Hardware | Opex $/day | " + " | ".join(f"n={n:,}" for n in MINERS) + " |")
    w("|----------|-----------:|" + "|".join(["--------:"] * len(MINERS)) + "|")
    for hw in HARDWARE:
        opex = daily_opex_usd(hw)
        cells = []
        for n in MINERS:
            be = breakeven_price_usd(per_miner_qfc_day(baseline, n, 0), opex)
            s = "$0 (free)" if be == 0 else f"${be:.4f}"
            if n >= 500 and be >= 0.05:
                s = f"**{s}**"
            cells.append(s)
        w(f"| {hw.name} | ${opex:.2f} | " + " | ".join(cells) + " |")
    w("")
    w("Assumptions: " + "; ".join(f"{hw.name} — {hw.note}" for hw in HARDWARE) + ".\n")

    # -- sanity -------------------------------------------------------------------
    w("## Sanity checks\n")
    for c in sanity_check(baseline, MINERS, YEARS, PRICES):
        w(f"- {c}")
    w("")
    return "\n".join(out)


def as_json(snaps: list[Snapshot]) -> dict:
    usable = [s for s in snaps if s.usable]
    baseline = usable[-1]
    return {
        "baseline": {
            "date": baseline.date,
            "miners_active": len(baseline.per_miner),
            "daily_tasks": baseline.daily_tasks,
            "pool_qfc_day": baseline.daily_earnings_qfc,
            "fee_qfc_day": baseline.daily_fees_qfc,
            "inflation_qfc_day": baseline.daily_inflation_qfc,
            "fee_share": baseline.fee_share,
        },
        "per_miner_qfc_day": {
            f"n={n}": {f"y{y}": round(per_miner_qfc_day(baseline, n, y), 4)
                       for y in YEARS}
            for n in MINERS
        },
        "breakeven_y0_usd": {
            hw.name: {f"n={n}": round(breakeven_price_usd(
                per_miner_qfc_day(baseline, n, 0), daily_opex_usd(hw)), 6)
                for n in MINERS}
            for hw in HARDWARE
        },
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="regenerate OUTPUT.md")
    ap.add_argument("--json", action="store_true", help="raw numbers as JSON")
    ap.add_argument("--snapshots", default=SNAPSHOTS_PATH)
    args = ap.parse_args()

    snaps = load_snapshots(args.snapshots)
    if args.json:
        print(json.dumps(as_json(snaps), indent=2))
    else:
        md = render(snaps)
        if args.write:
            with open(OUTPUT_PATH, "w") as f:
                f.write(md)
            print(f"wrote {OUTPUT_PATH}", file=sys.stderr)
        else:
            print(md)
