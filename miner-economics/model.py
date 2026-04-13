#!/usr/bin/env python3
"""
QFC Miner Economics Model
=========================
Inputs:
  - Measured per-miner daily earnings on the testnet (as of 2026-04-14)
  - Assumed hardware cost and electricity cost
  - Range of external miner counts and token prices

Outputs:
  - Daily reward per miner at different network sizes
  - Break-even token price curve
  - Markdown tables (stdout) + PNG plots (optional)
"""

from __future__ import annotations
import argparse
import json
import sys
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Measured baseline (testnet, 2026-04-14)
# ---------------------------------------------------------------------------
# Active miner 0xdb7c460a... (the only miner currently running tasks) earns:
BASELINE_DAILY_REWARD_QFC = 3_426.91
BASELINE_DAILY_TASKS = 8_635
BASELINE_PASS_RATE = 1.0  # 100% per qfc_getInferenceStats

# Fee per inference (all public tasks observed used this maxFee)
FEE_PER_TASK_QFC = 0.1

# Emission breakdown (inferred):
#   Current single miner gets 3,427 QFC/day.
#   Fees at 8,635 × 0.1 = 863 QFC/day
#   → block reward (inflation) = 2,564 QFC/day to this miner
#   That's the "supply-side subsidy" portion.
BASELINE_DAILY_FEES_TO_MINER = BASELINE_DAILY_TASKS * FEE_PER_TASK_QFC  # 863.5
BASELINE_DAILY_INFLATION_TO_MINER = BASELINE_DAILY_REWARD_QFC - BASELINE_DAILY_FEES_TO_MINER


# ---------------------------------------------------------------------------
# Operational cost assumptions (US / EU median)
# ---------------------------------------------------------------------------

@dataclass
class Hardware:
    name: str
    power_watts: float        # sustained wattage while mining
    amortization_usd_year: float  # hw cost / useful years

HARDWARE = [
    Hardware("Cheap VPS (4vCPU, CPU-only)",    0,   72),    # $6/mo rental, zero amort (rented)
    Hardware("Old laptop (2017 MBP Intel)",    45,  0),     # already owned
    Hardware("RTX 3060 rig (home PC)",         180, 500/3), # $500 card / 3 years
    Hardware("Apple M2 Mac mini",              20,  600/4), # $600 / 4 years
    Hardware("RTX 4090 rig",                   450, 1800/3),
    Hardware("A100 40GB (rented per-hour)",    300, 8760 * 1.1), # ~$1.1/hr cloud
]

ELECTRICITY_USD_PER_KWH = 0.15  # US/EU residential average


def daily_opex_usd(hw: Hardware, kwh_cost: float = ELECTRICITY_USD_PER_KWH) -> float:
    """Electricity + hardware amortization (USD/day)."""
    kwh_per_day = hw.power_watts * 24 / 1000
    power_cost = kwh_per_day * kwh_cost
    amort_daily = hw.amortization_usd_year / 365
    return power_cost + amort_daily


# ---------------------------------------------------------------------------
# Reward scaling model
# ---------------------------------------------------------------------------
# Assumption: total emission pool per day stays roughly constant; with more
# external miners, each miner's share of the INFLATION slice shrinks roughly
# 1/n (PoC weights everyone equally for demo purposes — in reality it's
# weighted by stake/compute/uptime, but 1/n is the optimistic upper bound).
#
# Fee slice scales with actual inference demand (independent variable).

def reward_per_miner_qfc(
    miners: int,
    daily_task_volume: int,
    inflation_pool_qfc_day: float = BASELINE_DAILY_INFLATION_TO_MINER,
    fee_per_task_qfc: float = FEE_PER_TASK_QFC,
) -> tuple[float, float]:
    """Returns (inflation_share, fee_share) in QFC per miner per day."""
    inflation_share = inflation_pool_qfc_day / miners
    fee_share = (daily_task_volume * fee_per_task_qfc) / miners
    return inflation_share, fee_share


# ---------------------------------------------------------------------------
# Break-even analysis
# ---------------------------------------------------------------------------

def breakeven_token_price_usd(daily_reward_qfc: float, daily_opex_usd: float) -> float:
    """Token price at which daily USD income = daily USD cost."""
    if daily_reward_qfc <= 0:
        return float("inf")
    return daily_opex_usd / daily_reward_qfc


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def report(miners_scenarios: list[int], demand_scenarios: list[int], token_prices: list[float]) -> str:
    out = []
    out.append("## Baseline (measured, 2026-04-14)\n")
    out.append(f"- Active miners: 1 (miner `0xdb7c460a...`, single one running tasks)")
    out.append(f"- Daily reward: **{BASELINE_DAILY_REWARD_QFC:,.0f} QFC/day**")
    out.append(f"- Daily tasks: {BASELINE_DAILY_TASKS:,}")
    out.append(f"- Implied inflation subsidy: {BASELINE_DAILY_INFLATION_TO_MINER:,.0f} QFC/day")
    out.append(f"- Implied fees captured: {BASELINE_DAILY_FEES_TO_MINER:,.0f} QFC/day")
    out.append(f"- Submitters observed: 2 addresses (internal, not external users yet)")
    out.append("")

    out.append("## Scenario: daily reward per miner (QFC)\n")
    out.append("Task demand held constant at measured baseline (8,635/day). Inflation pool split 1/n.\n")
    out.append("| Miners | Inflation share | Fee share | Total QFC/day |")
    out.append("|-------:|----------------:|----------:|--------------:|")
    for n in miners_scenarios:
        infl, fee = reward_per_miner_qfc(n, BASELINE_DAILY_TASKS)
        out.append(f"| {n:>6,} | {infl:>15,.2f} | {fee:>9,.2f} | {infl+fee:>13,.2f} |")
    out.append("")

    out.append("## Scenario: USD daily profit per miner\n")
    out.append("Rows = token price. Columns = miner count. Inner values = daily profit in USD, assuming:\n")
    out.append("- RTX 3060 rig (180W, amort $167/yr)")
    out.append("- $0.15/kWh electricity\n")
    hw = HARDWARE[2]  # RTX 3060
    opex = daily_opex_usd(hw)
    out.append(f"Daily opex = ${opex:.2f} (electricity ${hw.power_watts*24/1000*ELECTRICITY_USD_PER_KWH:.2f} + amort ${hw.amortization_usd_year/365:.2f})\n")
    hdr = "| Token $ | " + " | ".join(f"n={n:,}" for n in miners_scenarios) + " |"
    sep = "|---------|" + "|".join(["-" * 8] * len(miners_scenarios)) + "|"
    out.append(hdr)
    out.append(sep)
    for p in token_prices:
        row = [f"| ${p:>6.3f} "]
        for n in miners_scenarios:
            infl, fee = reward_per_miner_qfc(n, BASELINE_DAILY_TASKS)
            daily_usd = (infl + fee) * p - opex
            row.append(f"| {daily_usd:>+7.2f} ")
        row.append("|")
        out.append("".join(row))
    out.append("")

    out.append("## Break-even token price (USD) per hardware tier\n")
    out.append("At what QFC/USD price does a miner recover daily cost?\n")
    out.append("| Hardware | Miners | QFC/day | Opex USD/day | Breakeven $ |")
    out.append("|----------|-------:|--------:|-------------:|------------:|")
    for hw in HARDWARE:
        opex = daily_opex_usd(hw)
        for n in [1, 10, 100, 1000]:
            infl, fee = reward_per_miner_qfc(n, BASELINE_DAILY_TASKS)
            total = infl + fee
            be = breakeven_token_price_usd(total, opex)
            be_str = f"${be:.4f}" if be < 100 else ">$100"
            out.append(f"| {hw.name[:28]:<28} | {n:>6,} | {total:>7,.1f} | {opex:>12.2f} | {be_str:>11} |")
    out.append("")

    out.append("## Scenario: demand-side scaling\n")
    out.append("Fixed at 100 miners. Rows = task volume. Columns = token price. Inner = USD/day profit on RTX 3060.\n")
    hw = HARDWARE[2]
    opex = daily_opex_usd(hw)
    n = 100
    hdr = "| Tasks/day | " + " | ".join(f"${p:.2f}" for p in token_prices) + " |"
    sep = "|-----------|" + "|".join(["-" * 8] * len(token_prices)) + "|"
    out.append(hdr)
    out.append(sep)
    for tasks in demand_scenarios:
        row = [f"| {tasks:>9,} "]
        for p in token_prices:
            infl, fee = reward_per_miner_qfc(n, tasks)
            daily_usd = (infl + fee) * p - opex
            row.append(f"| {daily_usd:>+6.2f} ")
        row.append("|")
        out.append("".join(row))
    out.append("")

    return "\n".join(out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true", help="Emit raw numbers as JSON")
    args = ap.parse_args()

    miners_scenarios = [1, 10, 100, 500, 1000, 10000]
    demand_scenarios = [1_000, 10_000, 100_000, 1_000_000]
    token_prices = [0.001, 0.01, 0.10, 1.00, 10.00]

    if args.json:
        data = {
            "baseline": {
                "daily_reward_qfc": BASELINE_DAILY_REWARD_QFC,
                "daily_tasks": BASELINE_DAILY_TASKS,
                "fees_qfc": BASELINE_DAILY_FEES_TO_MINER,
                "inflation_qfc": BASELINE_DAILY_INFLATION_TO_MINER,
            },
            "scenarios": {
                f"n={n}": {
                    "inflation_per_miner_qfc": reward_per_miner_qfc(n, BASELINE_DAILY_TASKS)[0],
                    "fees_per_miner_qfc": reward_per_miner_qfc(n, BASELINE_DAILY_TASKS)[1],
                }
                for n in miners_scenarios
            },
            "hardware": [
                {
                    "name": hw.name,
                    "opex_usd_day": daily_opex_usd(hw),
                    "breakeven_at_n100_usd": breakeven_token_price_usd(
                        sum(reward_per_miner_qfc(100, BASELINE_DAILY_TASKS)),
                        daily_opex_usd(hw),
                    ),
                }
                for hw in HARDWARE
            ],
        }
        print(json.dumps(data, indent=2))
    else:
        print(report(miners_scenarios, demand_scenarios, token_prices))
