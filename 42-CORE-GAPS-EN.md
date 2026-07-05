# QFC Core Gaps: Three Life-or-Death Questions

**English** | [中文](./42-CORE-GAPS-CN.md)

> Last updated: 2026-07-04
>
> Status: **ARCHIVED (read-only)**. See the T+12 verdict at the end of this document. The criteria framework has been taken over — with the clock restarted — by [44-L1-MASTER-PLAN-EN.md](./44-L1-MASTER-PLAN-EN.md); this document is no longer updated.
>
> ~~Status: **Focus phase**. If none of these three gaps shows verifiable progress within 8–12 weeks, there is no reason to keep building this chain.~~

---

## Why this document exists

Over the past few months we built a lot of periphery: NFT marketplace, DEX, Bridge, Explorer, Faucet, Wallet, testnet tx bot, Grafana alerts… These make the chain "look alive", but **not one of them** touches QFC's real value proposition:

> QFC is not just another EVM chain. Its reason to exist is: **miners run AI inference in exchange for block rewards, and users/agents pay on-chain to invoke inference**.

If this loop can't be made to run, we are just another slow EVM-compatible chain. This document locks in the three core gaps that must be solved. Each one comes with: **success criteria / abandonment criteria / a first step within two weeks**. The timebox is 8–12 weeks — if there is no progress when it expires, shut down QFC and redirect the effort to a project with more traction.

---

## Gap A — Miner Onboarding: external miners running QFC inference nodes

### The problem
Right now only the 2 miners we run ourselves are producing inference proofs, and 3 internal nodes are producing blocks. No external miner has joined at all. Without external miners, a "decentralized inference network" is empty talk.

**The infrastructure layer is actually already in place** — this is a judgment we corrected during this review:

- ✅ The standalone GitHub repo `qfc-network/qfc-miner` already exists
- ✅ Release v2.3.2 (2026-03-15) already ships precompiled binaries for 9 platforms: macOS arm64/intel, Linux x86_64/arm64 (± CUDA/OpenCL), Windows x86_64 (± CUDA)
- ✅ One-click scripts: `start-miner.sh` (mac/Linux) + `install.ps1` (Windows)
- ✅ The README has a GPU tier table, minimum hardware requirements, troubleshooting, and how to use the faucet

So what Gap A is really missing is not "building the path" but three things:

1. **Exposure**: external developers have no idea this repo exists. No twitter/HN/reddit launch, no standalone landing page.
2. **Real-world validation**: we have never walked the README end-to-end on a clean VPS. The scripts very likely contain "works on my machine" friction points.
3. **Compatibility confirmation**: the v2.3.2 binaries were released on 2026-03-15, and the chain protocol/contracts may have changed over the past month. `start-miner.sh` still downloads v2.3.2 — we need to confirm it still runs against today's testnet.

### Success criteria (within 6 weeks)
- [ ] **10 external miners** producing valid inference proofs continuously for ≥ 7 days
- [ ] People spontaneously asking setup questions on Telegram/Discord (a sign that onboarding has reached the "has friction, but you can get in" stage)
- [ ] One tweet / one blog post driving traffic to the getting-started page with > 5% conversion (share of readers who complete the install)

### Abandonment criteria
- After 6 weeks, fewer than 3 external miners and new onboarding inquiries < 1 person per week → the miner route does not hold; consider repositioning QFC as a pure inference API (dropping the decentralized-miner route)

### First steps within two weeks
1. **Self-test a clean install**: rent a lowest-tier hetzner/vultr VPS (Linux x86_64), with no local development traces, and follow `qfc-miner/README.md` end to end. Note every point where you get stuck → fix the README or the script on the spot. Success criterion: the explorer shows inference proofs produced by this miner's address.
2. **Compatibility regression**: do the v2.3.2 binaries still run against today's testnet? If not, trigger a release → rebuild the binaries for all 9 platforms.
3. **First wave of exposure**: build a simple one-page landing (`miner.qfc.network`?), copy no longer than one screen, centered on the `curl | sh` command + an estimate of how much QFC you can earn. Post one tweet + one HN "Show HN" post, drive traffic, and watch day-one conversion.
4. **Day-one dashboard**: the things a miner wants to see on day one — my address, number of proofs produced, cumulative QFC rewards. If it doesn't exist, add a minimal version (could be a `/miner/[address]` page added to the explorer).

---

## Gap B — Inference Demand: who is paying to call QFC inference?

### The problem
Even with 100 miners, if **nobody calls** inference, miners are just burning electricity producing proofs that no testnet demand supports. In the long run there must be paid demand, otherwise the token can only live on speculative value.

Currently:
- The inference API (`qfc_submitInference` or similar) is not exposed as a public, rate-limited service billable via API key
- There is no SDK snippet that lets an external developer make a call in one line of code
- Not a single real user case runs in production (AgentHub is still a design doc; the games are sample projects)
- Compared with centralized APIs like OpenAI/Replicate/together.ai, QFC has no latency advantage, no price advantage, no model diversity — **the differentiation has to be "verifiable" + "censorship-resistant", and neither has been shown to users yet**

### Success criteria (within 8 weeks)
- [ ] A public inference API endpoint, with billing (per token or per task) and a `requests_per_day` metric reported
- [ ] At least **3 real callers who are not our team** (can be small projects or hackathon participants — not bots)
- [ ] A demo we can pitch to investors/users: **"why QFC inference"** — must be a pitch understandable within 1 minute, demonstrating one concrete scenario of verifiability or censorship resistance

### Abandonment criteria
- After 8 weeks, no external callers at all → no PMF on the demand side; no matter how much supply the miner side adds, it just idles

### First steps within two weeks
1. Wrap `qfc_submitInference` (or the equivalent interface) as a public REST API (`api.qfc.network/v1/inference`), behind Traefik + rate limiting
2. Ship SDK snippets: JS/Python, each completing "call + get result + verify proof" in under 20 lines
3. List 5 **concrete potential use cases** (agent decision-making, content moderation, game AI, etc.), pick 1 and build the demo ourselves, then openly evaluate whether it lands with target users
4. Talk to 3 external developers: "under what circumstances would you use a verifiable inference chain?" — no substantive answers is also a signal

---

## Gap C — Economic Incentives: is the reward model self-consistent?

### The problem
The multi-dimensional scoring of PoC consensus (stake 30%, compute 20%, uptime 15%, validation accuracy 15%, network quality 10%, storage 5%, reputation 5%) is self-consistent at the whitepaper level, but it has **never been validated to produce reasonable miner economics under real distributions**.

Concretely unanswered questions:
- How much QFC can a miner actually earn per day? Does it cover electricity / hardware amortization? (This needs estimation, not token-price assumptions)
- If external miners flood in, how is reward inflation controlled? How does the inflation rate step down during the testnet → mainnet transition?
- When inference-task demand is insufficient, what funds the rewards of "idling" miners? (If it's pure inflation, token value dilutes continuously)
- Are the slashing trigger conditions too strict / too loose? Has slashing ever actually fired on the testnet?
- Is the staking threshold reasonably friendly to "letting strangers join"?

### Success criteria (within 4 weeks)
- [ ] A **Miner Economics Model** document that, based on current testnet data, gives "per-miner daily earnings in QFC / daily earnings in USD (under several token-price assumptions) / break-even point"
- [ ] The model whiteboard-reviewed by at least 2 external people who understand blockchain economics, with no obvious logic holes found
- [ ] Mainnet parameters decided: initial inflation rate, reward distribution curve, minimum staking threshold

### Abandonment criteria
- After 4 weeks the economic model still can't be worked out, or the math comes out as "nobody will run one unless the token is > $10" → economically unviable before the demand side arrives; shelve it

### First steps within two weeks
1. Export from current testnet data: mean per-miner daily reward, per-inference-task duration/gas, total staked amount, current active miner count
2. Turn the PoC scoring function into a Python notebook: input external-miner join counts n = [10, 100, 1000], output each miner's expected earnings
3. Find 1–2 people familiar with PoS economics (past Cosmos / Ethereum economics research) for a paid review; 45 minutes is enough

---

## Decision framework

The three gaps are **not three parallel tracks** — they are strongly dependent:

```
Gap C (economic self-consistency)
   ↓ decides whether it is worth letting outsiders join
Gap A (Miner Onboarding) ←───── Gap B (Inference Demand)
                   mutual backstop: miners need demand to share revenue from;
                   demand needs miners to prove availability
```

- **Gap C fails → do not keep pushing A and B.** Economics that don't hold means miners who join either never break even or end up in a run on the token.
- **C passes & A done but B not → miners idle, token runs on speculation.** Worse than not doing it at all.
- **C passes & B done but A not → demand hits an empty supply.** Doesn't work.

So the order is **C (4 weeks) → A and B in parallel (6–8 weeks)**.

---

## Milestones and kill switch

| Point in time | Verdict |
|--------|------|
| **T+4 weeks** | Gap C delivers the economic model. If the model shows it doesn't hold → **shut down QFC** and redirect the effort to another project |
| **T+8 weeks** | Gap A has ≥ 3 external miners, Gap B has ≥ 1 external caller → keep pushing forward |
| **T+12 weeks** | Gap A has ≥ 10 miners, Gap B has ≥ 3 callers, plus 1 demo that can impress strangers → declare PMF initially validated, enter mainnet preparation |
| **At any time** | If all three gaps show no substantive progress within 8 weeks (not commit counts — external participation) → **stop** |

---

## What we will not do

During this period, unless directly related to the three gaps above, **the following work is paused**:

- New DeFi features (lending stays undeployed)
- New NFT / game frontend features
- Bridge expansion to more chains
- AgentHub UI polish (unless as an Inference Demand showcase)
- Nice-to-haves for Explorer / Wallet

Before any PR goes in, first ask: **does this help Gap A/B/C?** If not, defer it.

---

## Collaboration interface

- **Weekly update (every Sunday)**: append a section at the end of this document with the week's progress on the three gaps
- **On direction disagreements / external feedback needing a decision**: pull it into a dedicated discussion; don't stuff it into day-to-day commit messages
- **When the kill switch fires**: do not silently keep going. If it fires, stop and admit it

---

## T+12 verdict (2026-07-04, back-filled from the record)

This document was written on 2026-04-13; today is T+11.9 weeks — the timebox has expired. The verdict:

**Result: none of the three gaps saw external progress, but this is not a clean kill signal — the criteria were never truly put to the test.**

1. **The window was swallowed by the consensus fork.** On 2026-06-14 we discovered the testnet's 3 validators had been in a three-way fork since block #1 and never converged (6 compound defects in qfc-core, 5 fixed: PR #126/#128/#129; the 6th being fixed). With the chain itself not converging, miner recruitment and demand validation had no runnable foundation at all — the Gap A/B criteria never got a chance to be tested.
2. **Work actually completed** (not recorded via this document's weekly-update system; back-filled from the record):
   - **The bulk of Gap C is done**: miner-economics/ model v2 (04-14) → v3 (07-04, PR #48). Conclusion: **conditional pass** — with annual emission halving and zero demand growth, the fee share reaches 87% by year 4; the abandonment gate ("token price > $10") is far from triggered, worst realistic case $2.11. Weekly snapshots ran for 12 straight weeks (only 5 usable, due to forks/resets). **The single unfinished item: the external review was never sent out** (the template and outreach copy were ready back in April).
   - **Gap A partially advanced**: the onboarding-path review was completed (04-14), finding 2 real bugs (start-miner.sh download source points at the wrong repo; version drift unverified) — neither fixed.
   - **Gap B zero progress**: `unique_submitters_last_100` fell from 2–3 in April to 0 — the demand side went backwards instead of forwards.
   - In the same period we also completed SRE T1–T8 (PR #103–#123) and the AI-V3 core (B-1, A0–A6, B-2 spike) — valuable, but outside this document's three gaps, which precisely confirms this document's worry that "the periphery runs faster than the core".
3. **Lessons**: this document's weekly-update system was never executed even once (data collection kept running; the decision-oriented reviews never happened); not one of the "first steps within two weeks" was started within two weeks. A system without execution checks is no system at all.
4. **Disposition**: the criteria framework is handed over to 44-L1-MASTER-PLAN — Phase 0 (the chain runs) is a newly added hard prerequisite, the Gap C wrap-up merges into Phase 1, and the Gap A/B criteria (with testability fixes) merge into Phase 2 with the clock restarted (the 8/12-week gates + kill gates are retained). **This document is archived read-only.**
