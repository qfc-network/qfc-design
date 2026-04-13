## Emission schedule (from protocol constants)

| Year | QFC/block | Blocks/day | QFC/day network-wide |
|-----:|----------:|-----------:|---------------------:|
| 0 |   10.0000 | 4,547 |               45,470 |
| 1 |    5.0000 | 4,547 |               22,735 |
| 2 |    2.5000 | 4,547 |               11,368 |
| 3 |    1.2500 | 4,547 |                5,684 |
| 4 |    0.6250 | 4,547 |                2,842 |
| 5 |    0.6250 | 4,547 |                2,842 |

Floor: 0.625 QFC/block after year 4. Block time: 19s measured on testnet.

**Implication for the 75/25 baseline:** today's inflation subsidy is year-0 emission. By year 4 the absolute QFC subsidy is 1/16 of today. If task volume grows even 4× by year 4 at today's 0.1 QFC/task fee, fees surpass inflation and the chain becomes demand-funded without any parameter change. The question is whether demand shows up.

## Baseline (measured, 2026-04-14)

- Active miners: 1 (miner `0xdb7c460a...`, single one running tasks)
- Daily reward: **3,427 QFC/day**
- Daily tasks: 8,635
- Implied inflation subsidy: 2,563 QFC/day
- Implied fees captured: 864 QFC/day
- Submitters observed: 2 addresses (internal, not external users yet)

## Scenario: daily reward per miner (QFC)

Task demand held constant at measured baseline (8,635/day). Inflation pool split 1/n.

| Miners | Inflation share | Fee share | Total QFC/day |
|-------:|----------------:|----------:|--------------:|
|      1 |        2,563.41 |    863.50 |      3,426.91 |
|     10 |          256.34 |     86.35 |        342.69 |
|    100 |           25.63 |      8.63 |         34.27 |
|    500 |            5.13 |      1.73 |          6.85 |
|  1,000 |            2.56 |      0.86 |          3.43 |
| 10,000 |            0.26 |      0.09 |          0.34 |

## Scenario: USD daily profit per miner

Rows = token price. Columns = miner count. Inner values = daily profit in USD, assuming:

- RTX 3060 rig (180W, amort $167/yr)
- $0.15/kWh electricity

Daily opex = $1.10 (electricity $0.65 + amort $0.46)

| Token $ | n=1 | n=10 | n=100 | n=500 | n=1,000 | n=10,000 |
|---------|--------|--------|--------|--------|--------|--------|
| $ 0.001 |   +2.32 |   -0.76 |   -1.07 |   -1.10 |   -1.10 |   -1.10 |
| $ 0.010 |  +33.16 |   +2.32 |   -0.76 |   -1.04 |   -1.07 |   -1.10 |
| $ 0.100 | +341.59 |  +33.16 |   +2.32 |   -0.42 |   -0.76 |   -1.07 |
| $ 1.000 | +3425.81 | +341.59 |  +33.16 |   +5.75 |   +2.32 |   -0.76 |
| $10.000 | +34268.00 | +3425.81 | +341.59 |  +67.43 |  +33.16 |   +2.32 |

## Break-even token price (USD) per hardware tier

At what QFC/USD price does a miner recover daily cost?

| Hardware | Miners | QFC/day | Opex USD/day | Breakeven $ |
|----------|-------:|--------:|-------------:|------------:|
| Cheap VPS (4vCPU, CPU-only)  |      1 | 3,426.9 |         0.20 |     $0.0001 |
| Cheap VPS (4vCPU, CPU-only)  |     10 |   342.7 |         0.20 |     $0.0006 |
| Cheap VPS (4vCPU, CPU-only)  |    100 |    34.3 |         0.20 |     $0.0058 |
| Cheap VPS (4vCPU, CPU-only)  |  1,000 |     3.4 |         0.20 |     $0.0576 |
| Old laptop (2017 MBP Intel)  |      1 | 3,426.9 |         0.16 |     $0.0000 |
| Old laptop (2017 MBP Intel)  |     10 |   342.7 |         0.16 |     $0.0005 |
| Old laptop (2017 MBP Intel)  |    100 |    34.3 |         0.16 |     $0.0047 |
| Old laptop (2017 MBP Intel)  |  1,000 |     3.4 |         0.16 |     $0.0473 |
| RTX 3060 rig (home PC)       |      1 | 3,426.9 |         1.10 |     $0.0003 |
| RTX 3060 rig (home PC)       |     10 |   342.7 |         1.10 |     $0.0032 |
| RTX 3060 rig (home PC)       |    100 |    34.3 |         1.10 |     $0.0322 |
| RTX 3060 rig (home PC)       |  1,000 |     3.4 |         1.10 |     $0.3223 |
| Apple M2 Mac mini            |      1 | 3,426.9 |         0.48 |     $0.0001 |
| Apple M2 Mac mini            |     10 |   342.7 |         0.48 |     $0.0014 |
| Apple M2 Mac mini            |    100 |    34.3 |         0.48 |     $0.0141 |
| Apple M2 Mac mini            |  1,000 |     3.4 |         0.48 |     $0.1409 |
| RTX 4090 rig                 |      1 | 3,426.9 |         3.26 |     $0.0010 |
| RTX 4090 rig                 |     10 |   342.7 |         3.26 |     $0.0095 |
| RTX 4090 rig                 |    100 |    34.3 |         3.26 |     $0.0952 |
| RTX 4090 rig                 |  1,000 |     3.4 |         3.26 |     $0.9524 |
| A100 40GB (rented per-hour)  |      1 | 3,426.9 |        27.48 |     $0.0080 |
| A100 40GB (rented per-hour)  |     10 |   342.7 |        27.48 |     $0.0802 |
| A100 40GB (rented per-hour)  |    100 |    34.3 |        27.48 |     $0.8019 |
| A100 40GB (rented per-hour)  |  1,000 |     3.4 |        27.48 |     $8.0189 |

## Scenario: fee share over time (year × task volume)

100 miners, token price irrelevant here. Cell = fees/(fees+inflation). 
Target is fee share > 50% — the point where the chain is demand-funded.

| Tasks/day | Y0 | Y1 | Y2 | Y3 | Y4 | Y5 |
|-----------|------|------|------|------|------|------|
|     1,000 |  0.2% |  0.4% |  0.9% |  1.7% |  3.4% |  3.4% |
|    10,000 |  2.2% |  4.2% |  8.1% | 15.0% | 26.0% | 26.0% |
|   100,000 | 18.0% | 30.5% | 46.8% | 63.8% | 77.9% | 77.9% |
| 1,000,000 | 68.7% | 81.5% | 89.8% | 94.6% | 97.2% | 97.2% |

Reading: at today's 8,600 tasks/day, the chain is ~4% fee-funded at year 0 and ~39% fee-funded at year 4 — purely from emission halving, no demand growth. If demand grows to 100k/day by year 2 the chain crosses 50% fee share.

## Scenario: demand-side scaling

Fixed at 100 miners. Rows = task volume. Columns = token price. Inner = USD/day profit on RTX 3060.

| Tasks/day | $0.00 | $0.01 | $0.10 | $1.00 | $10.00 |
|-----------|--------|--------|--------|--------|--------|
|     1,000 |  -1.08 |  -0.84 |  +1.56 | +25.53 | +265.24 |
|    10,000 |  -1.07 |  -0.75 |  +2.46 | +34.53 | +355.24 |
|   100,000 |  -0.98 |  +0.15 | +11.46 | +124.53 | +1255.24 |
| 1,000,000 |  -0.08 |  +9.15 | +101.46 | +1024.53 | +10255.24 |

