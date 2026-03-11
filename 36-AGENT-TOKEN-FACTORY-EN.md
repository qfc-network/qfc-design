# Agent Token Factory (EVM)

> Last Updated: 2026-03-11 | Version 1.0
> GitHub Issue: #21
> Author: Alex Wei, Product Manager @ QFC Network

---

## 1. Executive Summary

The Agent Token Factory enables AI agents to be tokenized as ERC-20 tokens on QFC's EVM layer, following the Virtuals Protocol pattern. Each agent token is launched via a bonding curve and graduates to a permanent liquidity pool. Revenue from agent operations is distributed: 60% to the agent wallet, 30% to buyback & burn of the agent token, and 10% to the QFC treasury.

**Depends on**: #19 (Agent Capability Resources) — each agent token must be linked to a QVM AgentRegistration resource.

---

## 2. Contract Architecture

```
┌─────────────────────────────────────────────┐
│              AgentTokenFactory               │
│  - createAgent() → deploys new AgentToken    │
│  - Collects launch fee (100 QFC)             │
│  - Manages bonding curve parameters          │
├─────────────────────────────────────────────┤
│                                             │
│  ┌──────────────┐  ┌──────────────────────┐ │
│  │  AgentToken   │  │    BondingCurve      │ │
│  │  (ERC-20)     │  │  - Sigmoid pricing   │ │
│  │  + metadata   │  │  - Buy/sell with     │ │
│  │  + revenue    │  │    slippage protect  │ │
│  └──────┬───────┘  └──────────┬───────────┘ │
│         │                      │             │
│  ┌──────┴──────────────────────┴───────────┐ │
│  │        RevenueDistributor               │ │
│  │  60% agent wallet                       │ │
│  │  30% buyback & burn agent token         │ │
│  │  10% QFC treasury                       │ │
│  └─────────────────────────────────────────┘ │
│                                             │
│  ┌─────────────────────────────────────────┐ │
│  │          LiquidityLock                  │ │
│  │  - Permanent LP after graduation        │ │
│  │  - No unlock function                   │ │
│  └─────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

### Deployment Order
1. `BondingCurve` (library)
2. `LiquidityLock`
3. `RevenueDistributor`
4. `AgentTokenFactory` (references above)
5. Each `AgentToken` is deployed by the factory via `CREATE2`

---

## 3. AgentTokenFactory.sol

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "./AgentToken.sol";
import "./BondingCurve.sol";

contract AgentTokenFactory is Ownable {

    // ─── Constants ───
    uint256 public constant LAUNCH_FEE = 100 * 1e18;          // 100 QFC
    uint256 public constant MAX_SUPPLY = 1_000_000_000 * 1e18; // 1B tokens per agent
    uint256 public constant GRADUATION_THRESHOLD = 42_000 * 1e18; // 42,000 QFC in curve

    // ─── State ───
    IERC20 public immutable qfcToken;
    address public treasury;
    address public revenueDistributor;

    struct AgentInfo {
        address tokenAddress;
        address creator;
        bytes32 qvmAgentId;       // Linked QVM AgentRegistration
        string metadataURI;        // IPFS URI for agent metadata
        bool graduated;            // True when LP is created
        uint256 createdAt;
    }

    mapping(bytes32 => AgentInfo) public agents;       // agentId => info
    mapping(address => bytes32) public tokenToAgent;   // token address => agentId
    bytes32[] public allAgentIds;

    // ─── Events ───
    event AgentCreated(
        bytes32 indexed agentId,
        address indexed tokenAddress,
        address indexed creator,
        string name,
        string symbol
    );

    event AgentGraduated(
        bytes32 indexed agentId,
        address indexed tokenAddress,
        address lpAddress,
        uint256 liquidityAmount
    );

    // ─── Functions ───

    constructor(address _qfcToken, address _treasury) Ownable(msg.sender) {
        qfcToken = IERC20(_qfcToken);
        treasury = _treasury;
    }

    /// @notice Launch a new agent token
    /// @param name Token name (e.g., "SentimentBot")
    /// @param symbol Token symbol (e.g., "SENT")
    /// @param qvmAgentId The QVM AgentRegistration resource ID
    /// @param metadataURI IPFS URI for agent metadata JSON
    function createAgent(
        string calldata name,
        string calldata symbol,
        bytes32 qvmAgentId,
        string calldata metadataURI
    ) external returns (bytes32 agentId, address tokenAddress) {
        // Collect launch fee
        require(qfcToken.transferFrom(msg.sender, treasury, LAUNCH_FEE), "Fee transfer failed");

        // Generate deterministic agent ID
        agentId = keccak256(abi.encodePacked(msg.sender, name, symbol, block.timestamp));
        require(agents[agentId].tokenAddress == address(0), "Agent exists");

        // Deploy agent token via CREATE2
        bytes32 salt = keccak256(abi.encodePacked(agentId));
        AgentToken token = new AgentToken{salt: salt}(
            name,
            symbol,
            address(this),
            revenueDistributor
        );
        tokenAddress = address(token);

        // Store agent info
        agents[agentId] = AgentInfo({
            tokenAddress: tokenAddress,
            creator: msg.sender,
            qvmAgentId: qvmAgentId,
            metadataURI: metadataURI,
            graduated: false,
            createdAt: block.timestamp
        });
        tokenToAgent[tokenAddress] = agentId;
        allAgentIds.push(agentId);

        emit AgentCreated(agentId, tokenAddress, msg.sender, name, symbol);
    }

    /// @notice Get total number of agents
    function agentCount() external view returns (uint256) {
        return allAgentIds.length;
    }
}
```

---

## 4. AgentToken.sol

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract AgentToken is ERC20 {

    address public immutable factory;
    address public immutable revenueDistributor;

    /// @dev Only factory can mint (during bonding curve buys)
    modifier onlyFactory() {
        require(msg.sender == factory, "Only factory");
        _;
    }

    constructor(
        string memory name_,
        string memory symbol_,
        address factory_,
        address revenueDistributor_
    ) ERC20(name_, symbol_) {
        factory = factory_;
        revenueDistributor = revenueDistributor_;
    }

    function mint(address to, uint256 amount) external onlyFactory {
        _mint(to, amount);
    }

    function burn(uint256 amount) external {
        _burn(msg.sender, amount);
    }
}
```

### Agent Metadata JSON (IPFS)

```json
{
    "name": "SentimentBot",
    "description": "AI agent that analyzes market sentiment and executes trades",
    "image": "ipfs://Qm.../avatar.png",
    "capabilities": ["text-generation", "sentiment-analysis"],
    "creator": "0x123...",
    "qvm_agent_id": "0xabc...",
    "version": "1.0.0",
    "links": {
        "website": "https://sentimentbot.example.com",
        "github": "https://github.com/example/sentimentbot"
    }
}
```

---

## 5. BondingCurve.sol

### 5.1 Price Formula

We use a **sigmoid bonding curve** to create fair price discovery:

```
P(s) = P_max / (1 + e^(-k * (s - s_mid)))

Where:
  s     = current supply (tokens sold so far)
  P_max = maximum price on the curve (before graduation)
  k     = steepness parameter
  s_mid = midpoint supply (inflection point)
```

**Default parameters**:
- `P_max` = 0.001 QFC per token
- `k` = 0.00000001 (scaled for 1e18 math)
- `s_mid` = 500,000,000 tokens (500M = half of max supply)

### 5.2 Price Examples

| Supply Sold | Price (QFC/token) | Cumulative Cost |
|------------|-------------------|-----------------|
| 0 | 0.0000001 | 0 |
| 100M | 0.0000269 | ~1,350 QFC |
| 250M | 0.0000622 | ~5,500 QFC |
| 500M | 0.0005000 | ~18,000 QFC |
| 750M | 0.0009378 | ~35,000 QFC |
| 1B (graduation) | 0.0009999 | ~42,000 QFC |

### 5.3 Implementation

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

library SigmoidLib {
    uint256 constant PRECISION = 1e18;
    uint256 constant P_MAX = 1e15;           // 0.001 QFC in wei
    uint256 constant K = 1e10;                // Steepness (scaled)
    uint256 constant S_MID = 500_000_000e18;  // Midpoint supply

    /// @notice Approximate sigmoid using 8-segment piecewise linear
    /// @param supply Current total supply
    /// @return price Price per token in QFC wei
    function getPrice(uint256 supply) internal pure returns (uint256 price) {
        // Piecewise linear approximation of sigmoid
        if (supply < 62_500_000e18) {
            price = P_MAX / 10000;  // ~0.0000001 QFC
        } else if (supply < 125_000_000e18) {
            price = P_MAX * 3 / 10000;
        } else if (supply < 250_000_000e18) {
            price = P_MAX * 7 / 1000;
        } else if (supply < 375_000_000e18) {
            price = P_MAX * 27 / 1000;
        } else if (supply < 500_000_000e18) {
            price = P_MAX * 120 / 1000;
        } else if (supply < 625_000_000e18) {
            price = P_MAX * 500 / 1000;
        } else if (supply < 750_000_000e18) {
            price = P_MAX * 880 / 1000;
        } else if (supply < 875_000_000e18) {
            price = P_MAX * 973 / 1000;
        } else {
            price = P_MAX * 999 / 1000;
        }
    }

    /// @notice Calculate QFC cost for buying `amount` tokens at current `supply`
    /// @dev Uses trapezoidal integration over small steps
    function getCostForTokens(
        uint256 currentSupply,
        uint256 amount
    ) internal pure returns (uint256 cost) {
        uint256 steps = 100; // Higher = more accurate
        uint256 stepSize = amount / steps;
        uint256 supply = currentSupply;

        for (uint256 i = 0; i < steps; i++) {
            uint256 priceStart = getPrice(supply);
            uint256 priceEnd = getPrice(supply + stepSize);
            // Trapezoidal rule: area = (p1 + p2) / 2 * width
            cost += ((priceStart + priceEnd) * stepSize) / (2 * PRECISION);
            supply += stepSize;
        }
    }

    /// @notice Calculate tokens received for `qfcAmount` QFC
    /// @dev Binary search for the token amount
    function getTokensForQfc(
        uint256 currentSupply,
        uint256 qfcAmount
    ) internal pure returns (uint256 tokens) {
        uint256 lo = 0;
        uint256 hi = 1_000_000_000e18 - currentSupply; // Max possible

        for (uint256 i = 0; i < 64; i++) { // Binary search iterations
            uint256 mid = (lo + hi) / 2;
            uint256 cost = getCostForTokens(currentSupply, mid);
            if (cost <= qfcAmount) {
                tokens = mid;
                lo = mid + 1;
            } else {
                hi = mid - 1;
            }
        }
    }
}

contract BondingCurve {
    using SigmoidLib for uint256;

    IERC20 public immutable qfcToken;
    AgentToken public immutable agentToken;
    address public immutable factory;

    uint256 public constant GRADUATION_THRESHOLD = 42_000 * 1e18;
    uint256 public totalQfcCollected;
    bool public graduated;

    // Slippage protection
    uint256 public constant MAX_SLIPPAGE_BPS = 500; // 5%

    event TokensPurchased(address indexed buyer, uint256 qfcSpent, uint256 tokensReceived);
    event TokensSold(address indexed seller, uint256 tokensSold, uint256 qfcReceived);
    event Graduated(uint256 totalQfc, uint256 totalTokens);

    /// @notice Buy agent tokens with QFC
    function buy(
        uint256 qfcAmount,
        uint256 minTokensOut  // Slippage protection
    ) external returns (uint256 tokensOut) {
        require(!graduated, "Use LP");
        require(qfcAmount > 0, "Zero amount");

        tokensOut = SigmoidLib.getTokensForQfc(agentToken.totalSupply(), qfcAmount);
        require(tokensOut >= minTokensOut, "Slippage exceeded");

        qfcToken.transferFrom(msg.sender, address(this), qfcAmount);
        agentToken.mint(msg.sender, tokensOut);
        totalQfcCollected += qfcAmount;

        // Check graduation
        if (totalQfcCollected >= GRADUATION_THRESHOLD) {
            _graduate();
        }

        emit TokensPurchased(msg.sender, qfcAmount, tokensOut);
    }

    /// @notice Sell agent tokens back to curve for QFC
    function sell(
        uint256 tokenAmount,
        uint256 minQfcOut  // Slippage protection
    ) external returns (uint256 qfcOut) {
        require(!graduated, "Use LP");
        require(tokenAmount > 0, "Zero amount");

        qfcOut = SigmoidLib.getCostForTokens(
            agentToken.totalSupply() - tokenAmount,
            tokenAmount
        );
        require(qfcOut >= minQfcOut, "Slippage exceeded");
        require(qfcOut <= totalQfcCollected, "Insufficient reserves");

        agentToken.burn(tokenAmount);  // Requires approval
        qfcToken.transfer(msg.sender, qfcOut);
        totalQfcCollected -= qfcOut;

        emit TokensSold(msg.sender, tokenAmount, qfcOut);
    }

    /// @dev Create permanent LP and lock liquidity
    function _graduate() internal {
        graduated = true;
        // Transfer all QFC + mint remaining tokens → DEX LP
        // Lock LP tokens in LiquidityLock (no unlock function)
        emit Graduated(totalQfcCollected, agentToken.totalSupply());
    }
}
```

---

## 6. RevenueDistributor.sol

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract RevenueDistributor {

    // Revenue split (basis points)
    uint256 public constant AGENT_WALLET_BPS = 6000;   // 60%
    uint256 public constant BUYBACK_BURN_BPS = 3000;    // 30%
    uint256 public constant TREASURY_BPS = 1000;        // 10%

    IERC20 public immutable qfcToken;
    address public treasury;
    AgentTokenFactory public factory;

    // Per-agent accumulated revenue
    mapping(bytes32 => uint256) public pendingRevenue;

    event RevenueDistributed(
        bytes32 indexed agentId,
        uint256 toAgentWallet,
        uint256 toBuybackBurn,
        uint256 toTreasury
    );

    /// @notice Deposit revenue for an agent
    function depositRevenue(bytes32 agentId, uint256 amount) external {
        qfcToken.transferFrom(msg.sender, address(this), amount);
        pendingRevenue[agentId] += amount;
    }

    /// @notice Distribute pending revenue for an agent
    function distribute(bytes32 agentId) external {
        uint256 amount = pendingRevenue[agentId];
        require(amount > 0, "No revenue");
        pendingRevenue[agentId] = 0;

        AgentTokenFactory.AgentInfo memory info = factory.agents(agentId);

        // 60% to agent wallet
        uint256 agentShare = (amount * AGENT_WALLET_BPS) / 10000;
        qfcToken.transfer(info.tokenAddress, agentShare);  // Agent's own wallet

        // 30% buyback & burn
        uint256 buybackShare = (amount * BUYBACK_BURN_BPS) / 10000;
        _buybackAndBurn(info.tokenAddress, buybackShare);

        // 10% treasury
        uint256 treasuryShare = amount - agentShare - buybackShare;
        qfcToken.transfer(treasury, treasuryShare);

        emit RevenueDistributed(agentId, agentShare, buybackShare, treasuryShare);
    }

    /// @dev Buy agent tokens from DEX/curve and burn them
    function _buybackAndBurn(address agentToken, uint256 qfcAmount) internal {
        // Swap QFC → agent token via bonding curve or DEX
        // Then burn the received agent tokens
        AgentToken(agentToken).burn(/* tokens received */);
    }

    /// @notice Batch distribute for multiple agents (keeper-friendly)
    function batchDistribute(bytes32[] calldata agentIds) external {
        for (uint256 i = 0; i < agentIds.length; i++) {
            if (pendingRevenue[agentIds[i]] > 0) {
                this.distribute(agentIds[i]);
            }
        }
    }
}
```

---

## 7. LiquidityLock.sol

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// @notice Permanent liquidity lock — no unlock function by design
contract LiquidityLock {
    event LiquidityLocked(address indexed lpToken, uint256 amount, address indexed agentId);

    /// @notice Lock LP tokens permanently (no unlock)
    function lock(address lpToken, uint256 amount) external {
        IERC20(lpToken).transferFrom(msg.sender, address(this), amount);
        emit LiquidityLocked(lpToken, amount, msg.sender);
    }

    // Intentionally NO unlock/withdraw function — liquidity is permanent
}
```

---

## 8. Cross-VM Bridge

### 8.1 EVM ↔ QVM Link

Each agent token on EVM is linked to a QVM `AgentRegistration` resource via `qvmAgentId`:

```
EVM: AgentToken(0x456...)  ──── qvmAgentId ────►  QVM: AgentRegistration(0xabc...)
```

### 8.2 Bridge Contract

```solidity
interface IAgentBridge {
    /// @notice Called when QVM agent is registered — links to EVM token
    function onAgentRegistered(bytes32 qvmAgentId, address owner) external;

    /// @notice Query if QVM agent is active (not frozen/revoked)
    function isAgentActive(bytes32 qvmAgentId) external view returns (bool);

    /// @notice Route inference revenue to EVM RevenueDistributor
    function routeRevenue(bytes32 qvmAgentId, uint256 amount) external;
}
```

### 8.3 Trust Model

Cross-VM messages are attested by validators (2/3 threshold), same as consensus. The bridge does not introduce additional trust assumptions.

---

## 9. SDK Integration

### TypeScript (qfc-sdk-js)

```typescript
import { QFCClient } from '@qfc/sdk-js';

class AgentTokenSDK {
    constructor(private client: QFCClient) {}

    async createAgent(params: {
        name: string;
        symbol: string;
        qvmAgentId: string;
        metadataURI: string;
    }): Promise<{ agentId: string; tokenAddress: string; txHash: string }> {
        // Approve launch fee + call factory.createAgent()
    }

    async buyTokens(params: {
        agentId: string;
        qfcAmount: bigint;
        minTokensOut: bigint;
    }): Promise<{ tokensReceived: bigint; txHash: string }> {
        // Approve QFC + call bondingCurve.buy()
    }

    async sellTokens(params: {
        agentId: string;
        tokenAmount: bigint;
        minQfcOut: bigint;
    }): Promise<{ qfcReceived: bigint; txHash: string }> {
        // Approve agent tokens + call bondingCurve.sell()
    }

    async getAgentInfo(agentId: string): Promise<AgentInfo> { ... }
    async getPrice(agentId: string): Promise<bigint> { ... }
    async distributeRevenue(agentId: string): Promise<string> { ... }
    async listAgents(offset: number, limit: number): Promise<AgentInfo[]> { ... }
}
```

### Python (qfc-sdk-python)

```python
from qfc_sdk import QFCClient

class AgentTokenClient:
    def __init__(self, client: QFCClient):
        self.client = client

    def create_agent(self, name: str, symbol: str, qvm_agent_id: str, metadata_uri: str) -> dict: ...
    def buy_tokens(self, agent_id: str, qfc_amount: int, min_tokens_out: int) -> dict: ...
    def sell_tokens(self, agent_id: str, token_amount: int, min_qfc_out: int) -> dict: ...
    def get_agent_info(self, agent_id: str) -> dict: ...
```

---

## 10. UI Requirements

### Agent Launch Wizard (4 steps)

1. **Agent Details**: Name, symbol, description, avatar upload
2. **QVM Link**: Select or create QVM AgentRegistration
3. **Configuration**: Review bonding curve params, metadata preview
4. **Launch**: Approve launch fee → create agent → confirmation

### Agent Explorer Page

- Grid/list view of all agent tokens
- Sort by: market cap, volume, creation date, reputation
- Filter by: capability, status (active/graduated)
- Each card shows: name, symbol, price, market cap, 24h change, creator

### Agent Detail Page

- Price chart (bonding curve position or DEX chart)
- Buy/sell widget
- Revenue distribution history
- Linked QVM agent info (capabilities, reputation, tasks completed)
- Holder distribution

---

## 11. Security Considerations

### Rug Pull Prevention

| Mechanism | Description |
|-----------|-------------|
| **Permanent LP lock** | LiquidityLock has no unlock function |
| **Factory-only mint** | Only the factory contract can mint agent tokens |
| **Max supply cap** | Hard cap of 1B tokens per agent |
| **Launch fee** | 100 QFC prevents spam launches |
| **No admin mint** | Creator cannot mint additional tokens post-launch |
| **Bonding curve reserves** | All QFC in the curve is backed by token supply |

### Gas Estimates

| Operation | Estimated Gas |
|-----------|--------------|
| `createAgent()` | ~350,000 |
| `buy()` | ~150,000 |
| `sell()` | ~120,000 |
| `distribute()` | ~200,000 |
| `batchDistribute(10)` | ~1,500,000 |

---

## 12. Testing Strategy

### Unit Tests (Foundry)

| Suite | Tests | Key Scenarios |
|-------|-------|---------------|
| `AgentTokenFactory.t.sol` | ~15 | Create agent, duplicate prevention, launch fee |
| `BondingCurve.t.sol` | ~20 | Buy/sell, slippage, graduation, price accuracy |
| `RevenueDistributor.t.sol` | ~12 | 60/30/10 split, buyback, batch distribute |
| `LiquidityLock.t.sol` | ~5 | Lock LP, verify no unlock path |
| `Integration.t.sol` | ~10 | Full lifecycle: create → buy → earn → distribute |

### Invariant Tests

```solidity
// Foundry invariant tests
function invariant_curveReservesMatch() public {
    // QFC balance of curve == totalQfcCollected
    assertEq(qfcToken.balanceOf(address(curve)), curve.totalQfcCollected());
}

function invariant_revenueSplitSumsTo100() public {
    assertEq(
        distributor.AGENT_WALLET_BPS() +
        distributor.BUYBACK_BURN_BPS() +
        distributor.TREASURY_BPS(),
        10000
    );
}

function invariant_maxSupplyNotExceeded() public {
    assertLe(agentToken.totalSupply(), factory.MAX_SUPPLY());
}
```

### Testnet Deployment Plan

1. Deploy to QFC testnet
2. Create 3 test agents with different parameters
3. Simulate buy/sell cycles
4. Trigger graduation for 1 agent
5. Verify revenue distribution
6. Test cross-VM bridge with QVM AgentRegistration

---

## References

- [24-AI-AGENT-FRAMEWORK.md](./24-AI-AGENT-FRAMEWORK-EN.md) — Virtuals Protocol analysis
- [28-V3-ROADMAP.md](./28-V3-ROADMAP-EN.md) — v3.0 Phase 4.1
- [Virtuals Protocol Whitepaper](https://whitepaper.virtuals.io)
- [ERC-20 Standard](https://eips.ethereum.org/EIPS/eip-20)
- [Bonding Curve Design Patterns](https://yos.io/2018/11/10/bonding-curves/)
