# QFC Miner Economics — model output (v3, 2026-07-04)

> Generated offline — no live RPC (testnet is in a 3-way consensus fork; live numbers are unreliable).
> Command: `cd miner-economics && python3 refresh.py --write`
> Inputs: `snapshots.jsonl` (12 weekly Gap C snapshots, 2026-04-13 → 2026-06-28) + protocol constants verified against `qfc-core/crates/qfc-types/src/constants.rs`.

> **Data-quality caveat:** the chain was hard-reset with fresh genesis on 2026-06-18 and again on 2026-06-27, and has run as 3 independent forked chains for the whole snapshot period. `all_time_*` counters are discontinuous and each snapshot reflects whichever forked node answered. Treat the series as indicative, not authoritative.

## Snapshot series (12 weeks)

| Date | Miners reg. | Tasks/day | Earnings QFC/day | Fee share | All-time tasks | Note |
|------|------------:|----------:|-----------------:|----------:|---------------:|------|
| 2026-04-13 | 3 | 17,280 | 6,718 | 25.7% | 259,287 |  |
| 2026-04-19 | 3 | 17,280 | 6,607 | 26.2% | 306,420 |  |
| 2026-04-26 | 3 | 17,278 | 6,758 | 25.6% | 366,921 |  |
| 2026-05-03 | 0 | 0 | 0 | — | 0 | RPC down / node reset — all zeros |
| 2026-05-10 | 0 | 0 | 0 | — | 0 | RPC down / node reset — all zeros |
| 2026-05-17 | 3 | 17,276 | 6,707 | 25.8% | 548,504 |  |
| 2026-05-24 | 0 | 0 | 0 | — | 0 | RPC down / node reset — all zeros |
| 2026-05-31 | 0 | 0 | 0 | — | 0 | RPC down / node reset — all zeros |
| 2026-06-07 | 0 | 0 | 0 | — | 131,495 | validators up, miners deregistered; all_time reset ~06-05 |
| 2026-06-14 | 0 | 0 | 0 | — | 192,093 | same — no miner earnings |
| 2026-06-21 | 0 | 0 | 0 | — | 22,931 | post 06-18 genesis reset; counter restarted |
| 2026-06-28 | 2 | 13,580 | 4,682 | 29.0% | 6,790 | post 06-27 genesis reset; **baseline for v3** |

Only 5 of 12 snapshots are usable (non-zero). Observed fee share across usable snapshots: 0.256–0.290 (v2 assumed 0.25).

## Baseline (latest usable snapshot: 2026-06-28)

- Active miners: **2** (both earning identical amounts — even split)
- Network miner reward pool: **4,681.69 QFC/day**
- Daily tasks: 13,580 (sum of per-miner counts; both miners report the same 6,790 — possible fork double-count)
- Fee slice: 1,358.0 QFC/day (29% of reward; fee = 0.1 QFC/task)
- Inflation slice: 3,323.69 QFC/day
- External paying users: still **zero** (`unique_submitters_last_100` = 0)

Model basis (changed vs v2): pool = network-wide miner rewards from this snapshot. Inflation slice scales with the halving schedule; fee slice held at observed demand (no growth assumed). Split 1/n across miners.

## Emission schedule (protocol constants)

| Year | QFC/block | × of Y0 | Miner inflation pool QFC/day | Fee share at constant demand |
|-----:|----------:|--------:|-----------------------------:|-----------------------------:|
| 0 | 10.0000 | 1.0000 | 3,323.7 | 29.0% |
| 1 | 5.0000 | 0.5000 | 1,661.8 | 45.0% |
| 2 | 2.5000 | 0.2500 | 830.9 | 62.0% |
| 3 | 1.2500 | 0.1250 | 415.5 | 76.6% |
| 4 | 0.6250 | 0.0625 | 207.7 | 86.7% |
| 5 | 0.6250 | 0.0625 | 207.7 | 86.7% |

Nominal block time 3333 ms and 15% inference-miner share imply a theoretical Y0 miner pool of 38,884 QFC/day — the observed pool is far below that because the forked chain produces blocks erratically. The model uses the *observed* pool.

## Per-miner daily reward (QFC/day), by miner count × year

Constant demand (13,580 tasks/day @ 0.1 QFC); inflation halves per schedule.

| Miners | Y0 | Y1 | Y2 | Y3 | Y4 |
|-------:|---------:|---------:|---------:|---------:|---------:|
| 2 (today) |  2,340.85 |  1,509.92 |  1,094.46 |    886.73 |    782.87 |
| 10 |    468.17 |    301.98 |    218.89 |    177.35 |    156.57 |
| 100 |     46.82 |     30.20 |     21.89 |     17.73 |     15.66 |
| 500 |      9.36 |      6.04 |      4.38 |      3.55 |      3.13 |
| 1,000 |      4.68 |      3.02 |      2.19 |      1.77 |      1.57 |

## Per-miner daily gross revenue (USD/day), year 0

| Miners | $0.01 | $0.05 | $0.10 | $0.50 |
|-------:|--------:|--------:|--------:|--------:|
| 2 | $   23.41 | $  117.04 | $  234.08 | $1,170.42 |
| 10 | $    4.68 | $   23.41 | $   46.82 | $  234.08 |
| 100 | $    0.47 | $    2.34 | $    4.68 | $   23.41 |
| 500 | $    0.09 | $    0.47 | $    0.94 | $    4.68 |
| 1,000 | $    0.05 | $    0.23 | $    0.47 | $    2.34 |

## Per-miner daily gross revenue (USD/day), year 4

| Miners | $0.01 | $0.05 | $0.10 | $0.50 |
|-------:|--------:|--------:|--------:|--------:|
| 2 | $    7.83 | $   39.14 | $   78.29 | $  391.43 |
| 10 | $    1.57 | $    7.83 | $   15.66 | $   78.29 |
| 100 | $    0.16 | $    0.78 | $    1.57 | $    7.83 |
| 500 | $    0.03 | $    0.16 | $    0.31 | $    1.57 |
| 1,000 | $    0.02 | $    0.08 | $    0.16 | $    0.78 |

## Year-0 breakeven token price (USD) by hardware class

Price at which daily reward covers daily opex. Bold = the realistic danger zone (n ≥ 500).

| Hardware | Opex $/day | n=2 | n=10 | n=100 | n=500 | n=1,000 |
|----------|-----------:|--------:|--------:|--------:|--------:|--------:|
| Idle VPS (4vCPU, already rented) | $0.16 | $0.0001 | $0.0004 | $0.0035 | $0.0176 | $0.0351 |
| Laptop (already owned, idle) | $0.00 | $0 (free) | $0 (free) | $0 (free) | $0 (free) | $0 (free) |
| RTX 3060 home rig | $0.99 | $0.0004 | $0.0021 | $0.0211 | **$0.1053** | **$0.2107** |
| Datacenter GPU (A100-class, rented) | $9.86 | $0.0042 | $0.0211 | $0.2107 | **$1.0534** | **$2.1067** |

Assumptions: Idle VPS (4vCPU, already rented) — ~$5/mo rental; v2's 'Cheap VPS' was $6/mo; Laptop (already owned, idle) — $0 marginal cost — v2's 'Old laptop' had $0.16/day power; treated as $0 here per refreshed assumption; RTX 3060 home rig — ~$30/mo power (180W @ $0.15/kWh ≈ $19.4/mo + amort); v2 said $1.10/day ≈ $33/mo; Datacenter GPU (A100-class, rented) — $300+/mo; v2's A100 hourly rental was $27.5/day ≈ $825/mo — $300 is the charitable end.

## Sanity checks

- PASS — all 25 per-miner reward cells positive and finite
- PASS — emission multipliers monotone, floor = 1/16 from year 4
- PASS — baseline fees + inflation = total earnings
- PASS — recomputed fee share ≈ snapshot value (0.29)
- PASS — breakeven round-trip for Idle VPS (4vCPU, already rented)
- PASS — breakeven round-trip for RTX 3060 home rig
- PASS — breakeven round-trip for Datacenter GPU (A100-class, rented)
- PASS — n=2 Y0 model (2340.85) matches observed per-miner earnings (2340.84)
