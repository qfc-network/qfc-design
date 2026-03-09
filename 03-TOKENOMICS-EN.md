# QFC Tokenomics Design

## Overview

QFC (Quantum-Flux Coin) is the native token of the QFC blockchain, used for transaction fee payments, validator staking, network governance, and ecosystem incentives.

## Basic Parameters

| Parameter | Value |
|-----------|-------|
| **Token Name** | Quantum-Flux Coin |
| **Token Symbol** | QFC |
| **Decimals** | 18 |
| **Initial Supply** | 1,000,000,000 QFC (1 billion) |
| **Maximum Supply** | 2,000,000,000 QFC (2 billion) |
| **Inflation Model** | Decreasing inflation → long-term deflation |

## Initial Distribution

### Allocation Breakdown

```
┌────────────────────────────────────────────────────────────┐
│                Total: 1,000,000,000 QFC                    │
├────────────────────────────────────────────────────────────┤
│  ████████████████████████████ 30% Ecosystem Fund           │
│  ████████████████████ 20% Validator Incentives             │
│  ███████████████ 15% Team & Advisors                       │
│  ███████████████ 15% Early Investors                       │
│  ██████████ 10% Community Airdrop                          │
│  █████ 5% Liquidity Reserve                                │
│  █████ 5% Foundation Reserve                               │
└────────────────────────────────────────────────────────────┘
```

### Detailed Description

| Category | Percentage | Amount (QFC) | Purpose |
|----------|-----------|--------------|---------|
| **Ecosystem Fund** | 30% | 300,000,000 | Developer incentives, grants, hackathons, ecosystem project incubation |
| **Validator Incentives** | 20% | 200,000,000 | Testnet/early mainnet validator reward subsidies |
| **Team & Advisors** | 15% | 150,000,000 | Core development team, technical advisors |
| **Early Investors** | 15% | 150,000,000 | Seed round, Series A investors |
| **Community Airdrop** | 10% | 100,000,000 | Testnet participants, early community contributors |
| **Liquidity Reserve** | 5% | 50,000,000 | DEX liquidity, CEX listings |
| **Foundation Reserve** | 5% | 50,000,000 | Operations, legal, emergency reserve |

## Unlock Schedule

### Cliff and Vesting Periods

```
Timeline (TGE = Token Generation Event, mainnet launch)
│
├── TGE ──────────────────────────────────────────────────────►
│    │
│    ├─ Community Airdrop: 25% unlocked immediately, 75% linear release over 6 months
│    │
│    ├─ Liquidity Reserve: 100% available immediately
│    │
│    ├─ Ecosystem Fund: 10% immediately, 90% linear release over 48 months
│    │
│    ├─ Validator Incentives: Released via block rewards (48 months)
│    │
│    ├─ Early Investors: 12-month cliff, 24-month linear release
│    │
│    ├─ Team & Advisors: 12-month cliff, 36-month linear release
│    │
│    └─ Foundation Reserve: 6-month cliff, 48-month linear release
```

### Unlock Details

| Category | Cliff | Vesting | TGE Unlock | Monthly Release |
|----------|-------|---------|------------|-----------------|
| Community Airdrop | 0 | 6 months | 25% | 12.5% |
| Liquidity Reserve | 0 | 0 | 100% | - |
| Ecosystem Fund | 0 | 48 months | 10% | 1.875% |
| Validator Incentives | 0 | 48 months | 0% | Per block release |
| Early Investors | 12 months | 24 months | 0% | 4.17% |
| Team & Advisors | 12 months | 36 months | 0% | 2.78% |
| Foundation Reserve | 6 months | 48 months | 0% | 2.08% |

## Inflation and Deflation Mechanisms

### Block Rewards (Source of Inflation)

```rust
/// Block reward calculation formula
fn block_reward(year: u64) -> U256 {
    let base_reward = 10 * ONE_QFC;  // 10 QFC

    // Halving each year, minimum 0.625 QFC
    let halvings = year.min(4);
    base_reward >> halvings
}
```

| Year | Block Reward | Annual Issuance (approx.) | Inflation Rate (approx.) |
|------|-------------|--------------------------|--------------------------|
| Year 1 | 10 QFC | 94,608,000 | 9.46% |
| Year 2 | 5 QFC | 47,304,000 | 4.31% |
| Year 3 | 2.5 QFC | 23,652,000 | 2.07% |
| Year 4 | 1.25 QFC | 11,826,000 | 1.01% |
| Year 5+ | 0.625 QFC | 5,913,000 | 0.49% |

*Assuming one block every 3 seconds, approximately 10,512,000 blocks per year*

### Burn Mechanisms (Source of Deflation)

1. **Transaction Fee Burn (20%)**
   - 20% of every transaction fee is permanently burned
   - Similar to EIP-1559 base fee burn

2. **Penalty Burn**
   - Slashed validator stakes are burned directly
   - Double signing: 50% slashed and burned
   - Other violations burned proportionally

3. **Governance Burn**
   - Failed proposal deposits are burned
   - Malicious proposal penalties are burned

### Long-term Supply Curve

```
Supply
(billion QFC)
   │
20 │                                        ─────────────────── Maximum Supply
   │                                   ╱
   │                              ╱────
   │                         ╱────
15 │                    ╱────
   │               ╱────
   │          ╱────
   │     ╱────
10 │────╱                                    ← Initial Supply
   │
   └──────────────────────────────────────────────────────────► Year
      TGE   1    2    3    4    5    10   15   20   ...

Note: If transaction activity is high and burn volume > issuance, supply will decrease
```

## Validator Economics

### Staking Requirements

| Parameter | Value |
|-----------|-------|
| Minimum Stake | 10,000 QFC |
| Maximum Active Validators | 1,000 |
| Unstaking Waiting Period | 7 days |
| Minimum Delegation Amount | 100 QFC |

### Revenue Sources

```
Validator Revenue = Block Rewards + Transaction Fee Income
                  = (Block Reward × 70%) + (Transaction Fee × 50%)  [Producer]
                  = (Block Reward × 30%) + (Transaction Fee × 30%)  [Voter]
```

### Estimated Annual Percentage Yield (APY)

Assumptions:
- Total staked: 200 million QFC (20% of circulating supply)
- Daily transactions: 1 million
- Average transaction fee: 0.001 QFC

| Validator Stake | Block Production Probability | APY (approx.) |
|----------------|------------------------------|---------------|
| 10,000 QFC | 0.005% | 8-12% |
| 100,000 QFC | 0.05% | 10-15% |
| 1,000,000 QFC | 0.5% | 12-18% |

*Actual returns depend on contribution score, network activity, and staking competition*

### Delegation Mechanism

- Delegators can delegate QFC to validators
- Validators set commission rates (0-20%)
- Delegator revenue = Validator revenue share × (1 - commission rate)
- Delegators are also subject to validator penalties

## Fee Structure

### Gas Pricing

```rust
// Dynamic gas pricing
struct GasPrice {
    base_fee: U256,      // Base fee (adjusted based on block utilization)
    priority_fee: U256,  // Priority fee (tip for validators)
}

// Base fee adjustment algorithm (similar to EIP-1559)
fn adjust_base_fee(parent_gas_used: u64, parent_gas_limit: u64, parent_base_fee: U256) -> U256 {
    let target = parent_gas_limit / 2;

    if parent_gas_used > target {
        // Block overfull, increase fee
        let increase = parent_base_fee * (parent_gas_used - target) / target / 8;
        parent_base_fee + increase.max(1)
    } else {
        // Block underfull, decrease fee
        let decrease = parent_base_fee * (target - parent_gas_used) / target / 8;
        parent_base_fee - decrease.min(parent_base_fee)
    }
}
```

### Fee Parameters

| Operation | Gas Cost | Fee (at 1 Gwei base fee) |
|-----------|---------|--------------------------|
| Simple Transfer | 21,000 | 0.000021 QFC |
| ERC-20 Transfer | ~65,000 | 0.000065 QFC |
| Contract Deployment | ~500,000 | 0.0005 QFC |
| DEX Swap | ~150,000 | 0.00015 QFC |
| NFT Minting | ~100,000 | 0.0001 QFC |

### Fee Distribution Flow

```
User Pays Fee
      │
      ▼
┌─────────────────┐
│ Total Fee = 100% │
└────────┬────────┘
         │
    ┌────┴────┬─────────────┐
    ▼         ▼             ▼
┌───────┐ ┌───────┐   ┌──────────┐
│ 50%   │ │ 30%   │   │ 20%      │
│Producer│ │Voter  │   │ Burned   │
└───────┘ └───────┘   └──────────┘
```

## Governance Token Functions

### Voting Rights

- 1 QFC = 1 vote
- Staked QFC can be used for voting
- Delegated QFC voting rights belong to the validator

### Proposal Types

| Proposal Type | Deposit | Voting Period | Approval Threshold |
|--------------|---------|---------------|-------------------|
| Parameter Adjustment | 1,000 QFC | 7 days | 50% + 1 |
| Protocol Upgrade | 10,000 QFC | 14 days | 66.7% |
| Fund Allocation | 5,000 QFC | 7 days | 50% + 1 |
| Emergency Proposal | 50,000 QFC | 3 days | 80% |

### Adjustable Parameters

- Block gas limit
- Minimum staking requirement
- Penalty ratios
- Fee distribution ratios
- Maximum validator count

## Incentive Alignment Design

### Validator Incentives

```
Contribution Score = Stake Weight × 30%
                   + Computation Contribution × 20%
                   + Uptime × 15%
                   + Validation Accuracy × 15%
                   + Network Service × 10%
                   + Storage Contribution × 5%
                   + Historical Reputation × 5%
```

**Design Rationale:**
- Multi-dimensional evaluation prevents single-capital control
- Long-term participants receive higher reputation weight
- Encourages providing diversified network services

### Developer Incentives

1. **Gas Fee Rebate**
   - Contract creators receive 5% of the gas fees generated by their contracts
   - Incentivizes development of high-quality DApps

2. **Grant Program**
   - Ecosystem fund sponsors quality projects
   - Quarterly review, up to 1,000,000 QFC per project

3. **Bug Bounty**
   - Security vulnerability rewards: 1,000 - 1,000,000 QFC
   - Tiered by severity

### User Incentives

1. **Early User Airdrop**
   - Active testnet users
   - Community contributors

2. **Liquidity Mining**
   - DEX liquidity provider rewards
   - Lending protocol incentives

3. **Referral Rewards**
   - Transaction fee rebates for inviting new users

## Risks and Mitigations

### Centralization Risk

**Risk**: Whales controlling the network

**Mitigations**:
- Multi-dimensional contribution scoring (not pure PoS)
- Validator count cap at 1,000
- Staking cap (single validator max 1% of total stake)

### Inflation Risk

**Risk**: Token devaluation

**Mitigations**:
- Decreasing inflation model
- 20% transaction fee burn
- Penalty burn mechanism

### Liquidity Risk

**Risk**: Staking lockups causing insufficient liquidity

**Mitigations**:
- Liquid staking derivatives (stQFC)
- Reasonable unstaking waiting period (7 days)
- Liquidity reserve

## Competitive Comparison

| Metric | QFC | Ethereum | Solana | Avalanche |
|--------|-----|----------|--------|-----------|
| Initial Supply | 1B | ~120M | 500M | 720M |
| Inflation Model | Decreasing | Low inflation | Fixed inflation | Limited supply |
| Minimum Stake | 10,000 | 32 ETH | ~1 SOL | 2,000 AVAX |
| Transaction Fee Burn | 20% | Partial | 50% | 100% |
| Validator Returns | 8-18% | 4-7% | 6-8% | 8-12% |

## Implementation Timeline

| Phase | Timeframe | Milestone |
|-------|-----------|-----------|
| Testnet | M1-M3 | Token functionality testing, no real value |
| Incentivized Testnet | M4-M6 | Testnet tokens redeemable for mainnet tokens (1:1) |
| TGE | M7 | Mainnet launch, token generation |
| Listing | M7+1 week | DEX liquidity, CEX listing |
| Full Unlock | M55 | All tokens fully vested |

## Code Implementation

### Constants Definition Update

```rust
// crates/qfc-types/src/constants.rs additions

/// Initial total supply (1 billion QFC)
pub const INITIAL_SUPPLY: u128 = 1_000_000_000 * ONE_QFC;

/// Maximum supply (2 billion QFC)
pub const MAX_SUPPLY: u128 = 2_000_000_000 * ONE_QFC;

/// Annual block reward halving period
pub const HALVING_PERIOD_YEARS: u64 = 1;

/// Minimum block reward (0.625 QFC)
pub const MIN_BLOCK_REWARD: u128 = 625_000_000_000_000_000; // 0.625 * 10^18

/// Unstaking waiting period (seconds)
pub const UNSTAKE_DELAY_SECS: u64 = 7 * 24 * 60 * 60; // 7 days

/// Minimum delegation amount (100 QFC)
pub const MIN_DELEGATION: u128 = 100 * ONE_QFC;

/// Maximum stake percentage per validator (1%)
pub const MAX_VALIDATOR_STAKE_PERCENT: u64 = 1;

/// Contract creator fee rebate percentage (5%)
pub const CONTRACT_CREATOR_FEE_PERCENT: u64 = 5;
```

## Appendix

### A. Glossary

| Term | Definition |
|------|-----------|
| TGE | Token Generation Event |
| Cliff | Lock-up period during which no tokens can be unlocked |
| Vesting | Period during which tokens are released linearly over time |
| APY | Annual Percentage Yield |
| TVL | Total Value Locked |

### B. Risk Disclaimer

This document is a technical design proposal only and does not constitute investment advice. Cryptocurrency investments carry high risk; please make decisions carefully.

---

**Document Version**: 1.0.0
**Last Updated**: 2026-02-01
**Status**: Draft (pending community discussion)
