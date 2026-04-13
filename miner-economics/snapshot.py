#!/usr/bin/env python3
"""
Gap C instrumentation — weekly snapshot of the numbers that matter.

Run this once a week (or via cron) against the live testnet. It appends
one row to snapshots.jsonl and prints a delta vs the previous snapshot.
If the 42-CORE-GAPS milestones pass/fail based on trajectory here, you
don't have to re-derive numbers from scratch each review.

Usage:
    python3 snapshot.py                  # snapshot + stdout delta
    python3 snapshot.py --rpc URL        # override RPC endpoint
    python3 snapshot.py --no-append      # print only, don't write
"""

from __future__ import annotations
import argparse
import json
import os
import sys
import time
from urllib import request

SNAPSHOTS_FILE = os.path.join(os.path.dirname(__file__), "snapshots.jsonl")


def rpc(url: str, method: str, params: list) -> dict | list | None:
    body = json.dumps({"jsonrpc": "2.0", "method": method, "params": params, "id": 1}).encode()
    req = request.Request(url, data=body, headers={"Content-Type": "application/json"})
    try:
        with request.urlopen(req, timeout=15) as r:
            resp = json.loads(r.read())
        if "error" in resp:
            print(f"WARN {method}: {resp['error'].get('message')}", file=sys.stderr)
            return None
        return resp.get("result")
    except Exception as e:
        print(f"WARN {method}: {e}", file=sys.stderr)
        return None


def hex_to_int(v: str | int | None) -> int:
    if v is None:
        return 0
    if isinstance(v, int):
        return v
    if isinstance(v, str) and v.startswith("0x"):
        return int(v, 16)
    try:
        return int(v)
    except (TypeError, ValueError):
        return 0


def snapshot(rpc_url: str) -> dict:
    miners = rpc(rpc_url, "qfc_getRegisteredMiners", []) or []
    validators = rpc(rpc_url, "qfc_getValidators", []) or []
    stats = rpc(rpc_url, "qfc_getInferenceStats", []) or {}
    models = rpc(rpc_url, "qfc_getSupportedModels", []) or []

    # Pull daily earnings for each miner, sum up
    daily_earnings_wei = 0
    daily_tasks = 0
    per_miner = []
    for m in miners:
        addr = m["address"]
        e = rpc(rpc_url, "qfc_getMinerEarnings", [addr, "day"])
        if e:
            earned = hex_to_int(e.get("totalEarnings"))
            tasks = hex_to_int(e.get("totalTasks"))
            daily_earnings_wei += earned
            daily_tasks += tasks
            per_miner.append({"addr": addr[:10] + "…", "day_qfc": earned / 1e18, "day_tasks": tasks})

    # Sample recent public tasks to count unique submitters (proxy for external demand)
    tasks_sample = rpc(rpc_url, "qfc_listPublicTasks", [{"limit": 100}]) or []
    submitters = set()
    for t in tasks_sample:
        if t.get("submitter"):
            submitters.add(t["submitter"].lower())

    # Derived ratios
    all_time_tasks = hex_to_int(stats.get("tasksCompleted"))
    daily_fees_qfc = daily_tasks * 0.1  # observed fee per task
    daily_earnings_qfc = daily_earnings_wei / 1e18
    fee_ratio = daily_fees_qfc / daily_earnings_qfc if daily_earnings_qfc > 0 else 0

    return {
        "ts": int(time.time()),
        "date": time.strftime("%Y-%m-%d", time.gmtime()),
        "miners_registered": len(miners),
        "validators_total": len(validators),
        "validators_with_compute": sum(1 for v in validators if v.get("providesCompute")),
        "all_time_tasks": all_time_tasks,
        "all_time_pass_rate": stats.get("passRate"),
        "daily_tasks": daily_tasks,
        "daily_earnings_qfc": round(daily_earnings_qfc, 2),
        "daily_fees_qfc_estimated": round(daily_fees_qfc, 2),
        "daily_inflation_qfc_estimated": round(daily_earnings_qfc - daily_fees_qfc, 2),
        "fee_share_of_reward": round(fee_ratio, 3),
        "unique_submitters_last_100": len(submitters),
        "approved_models": len(models),
        "per_miner": per_miner,
    }


def load_last() -> dict | None:
    if not os.path.exists(SNAPSHOTS_FILE):
        return None
    with open(SNAPSHOTS_FILE) as f:
        lines = [ln for ln in f if ln.strip()]
    if not lines:
        return None
    return json.loads(lines[-1])


def delta(cur: dict, prev: dict | None) -> str:
    if not prev:
        return "(first snapshot — no delta)"
    lines = []
    for k in ("miners_registered", "all_time_tasks", "daily_earnings_qfc",
             "daily_fees_qfc_estimated", "fee_share_of_reward",
             "unique_submitters_last_100", "approved_models"):
        a, b = prev.get(k), cur.get(k)
        if a is None or b is None:
            continue
        d = b - a if isinstance(a, (int, float)) else None
        arrow = "↑" if d and d > 0 else ("↓" if d and d < 0 else "→")
        lines.append(f"  {k:<35} {a}  {arrow}  {b}   (Δ {d})")
    return "\n".join(lines)


def status_flags(cur: dict) -> list[str]:
    """Warnings for Gap C milestone checks from 42-CORE-GAPS-CN.md."""
    flags = []
    if cur["fee_share_of_reward"] < 0.40:
        flags.append(f"⚠ fee share {cur['fee_share_of_reward']:.0%} < 40% T+4w target")
    if cur["unique_submitters_last_100"] < 5:
        flags.append(f"⚠ only {cur['unique_submitters_last_100']} unique submitters — no external demand")
    if cur["miners_registered"] < 3:
        flags.append(f"⚠ {cur['miners_registered']} registered miners < 3 external T+8w target")
    if cur["approved_models"] < 4:
        flags.append(f"⚠ {cur['approved_models']} approved models — no LLM in catalog blocks Gap B")
    return flags


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rpc", default="https://rpc.testnet.qfc.network")
    ap.add_argument("--no-append", action="store_true")
    ap.add_argument("--json", action="store_true", help="Emit snapshot as JSON only")
    args = ap.parse_args()

    cur = snapshot(args.rpc)

    if args.json:
        print(json.dumps(cur, indent=2))
        return

    prev = load_last()

    print(f"# Snapshot  {cur['date']}")
    print(f"Miners registered:       {cur['miners_registered']}")
    print(f"Validators w/ compute:   {cur['validators_with_compute']} / {cur['validators_total']}")
    print(f"All-time tasks:          {cur['all_time_tasks']:,}")
    print(f"Daily tasks:             {cur['daily_tasks']:,}")
    print(f"Daily earnings:          {cur['daily_earnings_qfc']:,.0f} QFC")
    print(f"  └ est. fees:           {cur['daily_fees_qfc_estimated']:,.0f} QFC ({cur['fee_share_of_reward']:.0%})")
    print(f"  └ est. inflation:      {cur['daily_inflation_qfc_estimated']:,.0f} QFC ({1-cur['fee_share_of_reward']:.0%})")
    print(f"Unique submitters:       {cur['unique_submitters_last_100']} (last 100 tasks)")
    print(f"Approved models:         {cur['approved_models']}")
    print()
    print("## Delta vs previous")
    print(delta(cur, prev))
    print()
    flags = status_flags(cur)
    if flags:
        print("## Gap C milestone flags")
        for f in flags:
            print(f"  {f}")
    else:
        print("## Gap C milestone flags\n  none — all thresholds met")
    print()

    if not args.no_append:
        with open(SNAPSHOTS_FILE, "a") as f:
            f.write(json.dumps(cur) + "\n")
        print(f"Appended to {SNAPSHOTS_FILE}")


if __name__ == "__main__":
    main()
