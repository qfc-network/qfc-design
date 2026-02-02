# Mainnet Validator Allocation Guidance (Official vs Community)

Last Updated: 2026-02-02

This note proposes a practical policy for validator allocation when mainnet
launches, especially if external parties spin up many nodes quickly.
It is designed for the QFC PoC model where **contribution weight** matters more
than raw node count.

---

## Core Principle

**Control risk is driven by contribution weight, not node count.**

Risk thresholds:
- **> 1/3 weight**: can delay finality (liveness risk)
- **> 2/3 weight**: can control finality (safety risk)

Goal:
- Keep **any single entity < 1/3** of total weight at all times.
- Target **official weight 10–20%** after stabilization.

---

## Recommended Allocation by Phase

### Phase A — Launch (0–3 months)
Purpose: stability, operational confidence

- **Official validators**: 30–40% of nodes  
  - **Weight target**: **< 1/3** (ideally 25–30%)
- **Community validators**: 60–70%

Additional controls:
1) **Validator admission cap** (e.g., max 50 initially)
2) **Entity weight cap** (e.g., 15–20% per entity)
3) **Progressive onboarding** (batch approvals weekly)

### Phase B — Stabilization (3–9 months)
Purpose: shift to decentralization

- **Official validators**: 15–25% of nodes  
  - **Weight target**: 15–25%
- **Community validators**: 75–85%

Controls:
1) Reduce official stake share gradually
2) Increase validator cap (e.g., 100–300)
3) Publish transparent validator and weight stats

### Phase C — Mature Network (9–18 months)
Purpose: decentralization + governance maturity

- **Official validators**: 10–15% of nodes  
  - **Weight target**: 10–15%
- **Community validators**: 85–90%

Controls:
1) Strict entity weight cap
2) Governance-based onboarding (proposal → vote)

---

## What If Someone Spins Up 30 Nodes?

### Immediate Actions
1) **Check their weight** (not node count)
2) If weight > 1/3, **freeze new admissions** temporarily
3) **Apply entity cap** on contribution weight
4) Encourage more validators to dilute total weight

### Structural Defenses
1) **Stake + quality-weighted scoring** (network quality, uptime, storage)
2) **Identity binding** (KYC or operator attestations, if desired)
3) **Rate-limit onboarding** (new validators per epoch/week)

---

## Parameter Recommendations (Initial Defaults)

```toml
# Validator set
max_validators = 50
min_stake = 10000

# Entity caps (policy layer)
max_entity_weight = 0.20
max_entity_nodes = 10

# Onboarding
max_new_validators_per_week = 5
review_period_days = 7
```

Notes:
- `max_entity_weight` should always stay below 1/3.
- Increase `max_validators` gradually when monitoring is stable.

---

## Operational Checklist (Official Team)

1) **Publish validator stats dashboard** (weights + entity grouping)
2) **Define admission policy** (criteria, SLA, scoring)
3) **Emergency pause** for validator onboarding
4) **Governance process** for weight cap changes

---

## Summary

At mainnet launch, the official team should **prioritize stability** while
**preventing any single entity from exceeding 1/3 contribution weight**.
As the network matures, reduce official weight and increase community share
with a controlled onboarding schedule.
