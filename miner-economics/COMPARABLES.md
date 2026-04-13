# QFC vs comparable GPU-compute networks

> Companion to [MINER-ECONOMICS.md](./MINER-ECONOMICS.md). Public-knowledge snapshot — numbers approximate, verify before citing externally.
> Purpose: position QFC against prior art so the Gap C external reviewer can say "this is like X" or "this copies Y's mistake."

## At a glance

| Chain | Total supply | Emission | Provider earnings | Subsidy vs fee today | Best design idea | Worst design idea |
|---|---|---|---|---|---|---|
| **Akash (AKT)** | 388M (raised from 100M) | Inflationary, Cosmos-style, ~13-15%/yr, no halving | Lease fees (AKT/USDC) | Subsidy dominant (>90% of validator income) | Clean split: providers earn fees, validators earn inflation | Paying providers with inflation no one asked for |
| **Render (RNDR)** | ~644M | **Burn-Mint Equilibrium (BME)** — mints are gated by user burns | Minted RENDER (protocol subsidy) | Architecturally 100% subsidy, but gated by demand — no demand = no mint | Emissions tied to realized demand | — |
| **io.net (IO)** | 800M cap | Disinflationary, ~8% → decays 1.02%/mo over ~20 years | Both — user payments (USDC) + IO block rewards | Subsidy-dominant at launch | Hybrid payment stack | Rewards for "proof of availability" → Sybil GPU spam with no workload |
| **QFC (today)** | See [tokenomics doc] | Year 0: 10 QFC/block, halves yearly, floor 0.625 at year 4+ | Inflation + fees | 75% / 25% at baseline — by year 4 drops to ~39% subsidy without demand growth | Halving schedule is already hard-coded (io.net-style discipline) | Only 3 embedding models in catalog — no market for fees to form against |

## Akash — what to copy, what not to

**Copy:** role separation. `Provider` (sells compute) and `Validator` (secures chain) are different economic agents with different income streams. QFC today mixes them — the same actors can be validators AND inference miners, and their rewards come from the same pot. That makes it hard to see which subsidy is rewarding what.

**Don't copy:** 13-15% annual inflation that never taper. Akash's tokenomics have no "demand must catch up" forcing function. After 5 years of low usage, subsidy dilution is the same as year 1. QFC's halving avoids this trap.

## Render — the BME insight

Render's Burn-Mint Equilibrium is the single best idea in this space for a protocol that wants to transition from subsidy to fees without a hard emission cut:

- Users burn RENDER to buy work credits.
- Node operators get newly-minted RENDER for verified work.
- Net issuance = mint - burn. No demand → no mint.

**QFC does not use BME today.** Our emission is a fixed halving schedule, burned gas separately. That works if demand grows exponentially (halving + 4× demand/yr = fee-dominant by year 4, per our model). But if demand grows slowly, we're still handing out full yearly emission, just less each year.

**Gap C reviewer question:** should QFC shift to BME? The answer isn't obvious:
- Pro: automatic demand-gating, no "empty inflation" like Akash.
- Con: at bootstrap (today, 0 external users) mint ≈ 0, so miners get nothing. A hybrid (fixed floor + BME upside) might make more sense.

A post-launch emission redesign is feasible — io.net already modified theirs twice. But it's a protocol-level governance action, not a config tweak.

## io.net — what to actively avoid

io.net pays GPU providers for "uptime" independent of real workload. The result (as any quick search of their community channels reveals): **farms of idle GPUs running the minimum heartbeat to collect rewards**. Sybil resistance is weak because you can stand up many "providers" that do nothing but prove they're online.

**QFC is not doing this today** — rewards flow through `qfc_submitInferenceProof` which attaches attested work. Good. But be careful as the protocol evolves: any "we'll pay validators just for being online" rule is a path to Sybil farming.

## Where does QFC actually fit

| Axis | QFC's position |
|---|---|
| Subsidy-to-fee transition plan | Has one (halving). Better than Akash, similar shape to io.net, weaker than Render's BME. |
| Proof of useful work | Strong — miner rewards require attested inference, spot-checked. Better than io.net. |
| Role separation (validator vs miner) | Weak — same addresses can do both. Worse than Akash. |
| Model diversity in catalog | Worst — 3 embedding models only. Render has hundreds of models available, Akash is model-agnostic (runs whatever containers), io.net focuses on GPU rental not model serving. |
| Token economy maturity | Pre-launch. All three comparables have tokens trading, real fees. We're measuring testnet-only data. |

## Implications for the Gap C kill-switch

If an external economics reviewer concludes "QFC's emission schedule is credible, but the chain won't survive year 0 without demand," the options (ranked by reversibility):

1. **Add more models to catalog** (reversible, 1-week governance action) — [PROPOSAL-LLM-MODEL-CATALOG.md](../PROPOSAL-LLM-MODEL-CATALOG.md) already drafted.
2. **Slow the miner-onboarding pace** (reversible, operational). Accept 3-5 external miners in month 1, not 50.
3. **Separate validator vs inference-miner rewards** (schema change, 1-release protocol work). Akash-style role split.
4. **Introduce BME for the inference-fee portion** (protocol change, 3-6 months). Demand-gated mint above the floor rate. Render-style.
5. **Cut block reward schedule to halve every 6 months instead of yearly** (hard fork, governance drama). Unfortunate precedent.

The cheap options (1, 2) don't require protocol changes. They're what we should do while waiting for Gap C reviewer input on whether 3-5 are needed.

## Sources and verification

Numbers above are from public sources (project docs, CoinGecko, community channels) and may be stale. Before quoting any of these in an external-facing pitch, verify against:

- Akash: https://akash.network + https://docs.akash.network
- Render: https://rendernetwork.com + https://tokenomics.renderfoundation.com
- io.net: https://io.net + https://docs.io.net/reference/ignition-rewards

**Do not fabricate numbers** for pitching. If you don't know a current figure, say "approximate as of early 2026" and move on.
