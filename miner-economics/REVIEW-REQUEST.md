# External Economics Review — Request Template

> Purpose: get 1–2 people with real PoS / mining / crypto-economic experience to tear apart the QFC miner economics before we spend another month building on top of shaky math. Triggered by [MINER-ECONOMICS.md](./MINER-ECONOMICS.md) showing 75% inflation / 25% fees with near-zero external demand.

## Who to ask (shortlist criteria)

Pick people who have **operated or designed** at least one of:
- An L1 with its own inflation schedule (Cosmos ecosystem, Near, Polkadot, Avalanche)
- A GPU-compute marketplace (Akash, Render, Gensyn, io.net, Aethir)
- An Ethereum staking / MEV economic product (Lido, Rocket Pool, Flashbots)
- A token-emission redesign (any chain that changed emissions after launch)

Avoid pure trader / VC types. We don't need price opinions — we need emission-design opinions.

Realistic channels:
- Warpcast / X DMs to public operators (Cosmos validators often reply)
- Twitter thread asking "anyone willing to spend 45 min reviewing a small-L1 economics model in exchange for a fair hourly rate"
- Referral from any existing QFC investor / advisor
- Cosmos / Near / Akash Discord — their validator channels are surprisingly accessible

Budget: $250–$750 for a 45-minute Zoom + follow-up note. That's cheap insurance.

## The ask (copy-paste DM / email template)

---

**Subject:** 45-min paid review — small L1 miner economics (AI-inference chain)

Hi [name],

I'm looking for a 45-minute paid review ($300, negotiable) of the emission schedule and miner unit-economics on a small L1 I've been working on (QFC — an AI-inference chain, chain id 9000, currently testnet-only).

I've already measured real data from the live chain and modeled per-miner daily income at different miner counts and token prices. I'm not asking you to price the token — I'm asking whether the emission schedule can credibly transition from subsidy-dominant to fee-dominant before miner bleed-out.

**The three questions I need you to answer:**

1. Is 75% inflation / 25% fees a fatal starting ratio for an L1 where fees are today effectively zero? Or does it self-correct with time?
2. At what (miners × token price × fee volume) combination does this economy become self-sustaining without further emission dilution? Is that combination realistic on a 6-12 month horizon?
3. If the answer to (2) is "not realistic," what is the minimal redesign — lower inflation, rebate pool, vesting schedule change, demand-linked emission — that would make it work?

I have a simple Python model ([model.py](./model.py), ~150 lines) and a writeup ([MINER-ECONOMICS.md](./MINER-ECONOMICS.md)) you can read in 15 minutes. I'd want a 45-minute Zoom to go through your read, then a short write-up of your recommendation (half a page is fine).

If you think this is outside your wheelhouse, or the rate is wrong, or you can't in the next 2 weeks — please reply with a name or two of someone who could.

Thanks,
Larry

---

## What you send as attachments

1. The live chain URL: `https://rpc.testnet.qfc.network` — reviewer can hit `qfc_getMinerEarnings`, `qfc_getInferenceStats`, `qfc_getValidators` themselves if they want.
2. [MINER-ECONOMICS.md](./MINER-ECONOMICS.md) — the honest writeup.
3. [model.py](./model.py) — runnable model.
4. [OUTPUT.md](./OUTPUT.md) — pre-rendered tables (if they don't want to run Python).
5. The PoC consensus design doc ([02-POC-CONSENSUS in qfc-design](../02-POC-CONSENSUS-EN.md) if available) — so they can see the theoretical scoring function.

## What constitutes "pass" vs "fail" on the review

**Pass** — at least one reviewer says:
> "The math has a plausible path to self-sustaining fees if [specific condition]. Here's what I'd change about emissions to make that path more likely." (They'd actually sketch changes.)

**Fail** — both reviewers independently say:
> "This emission structure doesn't close. The inflation subsidy is funding miners who have no market demand to serve — you're paying people to do work no one wants yet. Either cut emissions until fees catch up (which risks losing miners before critical mass) or pivot the product."

Pay them either way. The value is in the answer, not the conclusion.

## After the review — what we commit to

1. If **pass**: publish a short note ("we got X reviewed, here's what we're changing") and proceed to Gap A + B.
2. If **fail**: document their reasoning in `42-CORE-GAPS-CN.md` under the T+4 week milestone, and trigger the redesign decision. No pretending the review didn't happen.

## Timeline

| Week | Action |
|---|---|
| Week 0 (now) | Send 5 cold outreach DMs. Expect 1-2 replies. |
| Week 1 | Schedule Zoom(s). Pay first reviewer. |
| Week 2 | Receive write-up. Decide go/no-go. |
| Week 3 | If go: publish summary + begin implementing recommendations. If no-go: redesign session. |

This is the T+4 week Gap C milestone in `42-CORE-GAPS-CN.md`.

## Template — "help me find reviewers" post for Twitter / Warpcast

> Paying $300 for a 45-min review of an L1 miner-economics model.
> Need someone who's designed or operated an L1 emission schedule, a
> GPU compute marketplace, or a token emission redesign.
> 3 yes/no questions, simple model, honest writeup. Not a pitch.
> Reply or DM if interested, or if you know someone.

Keep it boring. "Paying for time" attracts the people who actually have the time.
