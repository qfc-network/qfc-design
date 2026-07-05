# Agent 代币工厂（EVM）

[English](./36-AGENT-TOKEN-FACTORY-EN.md) | **中文**

> 最后更新：2026-03-11 | 版本 1.0
> GitHub Issue: #21
> 作者：Alex Wei，QFC Network 产品经理

---

## 1. 摘要

Agent 代币工厂（Agent Token Factory）允许将 AI Agent 在 QFC 的 EVM 层代币化为 ERC-20 代币，遵循 Virtuals Protocol 模式。每个 Agent 代币通过 bonding curve（联合曲线）发射，达标后毕业进入永久流动性池。Agent 运营收入按如下比例分配：60% 给 Agent 钱包，30% 用于回购并销毁 Agent 代币，10% 归 QFC 国库。

**依赖**：#19（Agent Capability Resources）——每个 Agent 代币必须关联一个 QVM AgentRegistration 资源。

---

## 2. 合约架构

```
┌─────────────────────────────────────────────┐
│              AgentTokenFactory               │
│  - createAgent() → 部署新的 AgentToken        │
│  - 收取发射费（100 QFC）                      │
│  - 管理 bonding curve 参数                    │
├─────────────────────────────────────────────┤
│                                             │
│  ┌──────────────┐  ┌──────────────────────┐ │
│  │  AgentToken   │  │    BondingCurve      │ │
│  │  (ERC-20)     │  │  - Sigmoid 定价       │ │
│  │  + 元数据      │  │  - 买入/卖出，带      │ │
│  │  + 收入        │  │    滑点保护           │ │
│  └──────┬───────┘  └──────────┬───────────┘ │
│         │                      │             │
│  ┌──────┴──────────────────────┴───────────┐ │
│  │        RevenueDistributor               │ │
│  │  60% Agent 钱包                          │ │
│  │  30% 回购并销毁 Agent 代币                │ │
│  │  10% QFC 国库                            │ │
│  └─────────────────────────────────────────┘ │
│                                             │
│  ┌─────────────────────────────────────────┐ │
│  │          LiquidityLock                  │ │
│  │  - 毕业后 LP 永久锁定                     │ │
│  │  - 无解锁函数                             │ │
│  └─────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

### 部署顺序
1. `BondingCurve`（库）
2. `LiquidityLock`
3. `RevenueDistributor`
4. `AgentTokenFactory`（引用上述合约）
5. 每个 `AgentToken` 由 factory 通过 `CREATE2` 部署

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

### Agent 元数据 JSON（IPFS）

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

### 5.1 价格公式

我们采用 **sigmoid bonding curve** 实现公平的价格发现：

```
P(s) = P_max / (1 + e^(-k * (s - s_mid)))

Where:
  s     = current supply (tokens sold so far)
  P_max = maximum price on the curve (before graduation)
  k     = steepness parameter
  s_mid = midpoint supply (inflection point)
```

**默认参数**：
- `P_max` = 0.001 QFC/代币
- `k` = 0.00000001（按 1e18 精度缩放）
- `s_mid` = 500,000,000 代币（500M，即最大供应量的一半）

### 5.2 价格示例

| 已售供应量 | 价格（QFC/代币） | 累计成本 |
|------------|-------------------|-----------------|
| 0 | 0.0000001 | 0 |
| 100M | 0.0000269 | ~1,350 QFC |
| 250M | 0.0000622 | ~5,500 QFC |
| 500M | 0.0005000 | ~18,000 QFC |
| 750M | 0.0009378 | ~35,000 QFC |
| 1B（毕业） | 0.0009999 | ~42,000 QFC |

### 5.3 实现

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

## 8. 跨 VM 桥

### 8.1 EVM ↔ QVM 关联

EVM 上的每个 Agent 代币通过 `qvmAgentId` 关联到一个 QVM `AgentRegistration` 资源：

```
EVM: AgentToken(0x456...)  ──── qvmAgentId ────►  QVM: AgentRegistration(0xabc...)
```

### 8.2 桥合约

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

### 8.3 信任模型

跨 VM 消息由验证者见证（2/3 阈值），与共识机制相同。桥不引入额外的信任假设。

---

## 9. SDK 集成

### TypeScript（qfc-sdk-js）

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

### Python（qfc-sdk-python）

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

## 10. UI 需求

### Agent 发射向导（4 步）

1. **Agent 信息**：名称、符号、描述、头像上传
2. **QVM 关联**：选择或创建 QVM AgentRegistration
3. **配置**：确认 bonding curve 参数、元数据预览
4. **发射**：授权发射费 → 创建 Agent → 确认

### Agent 浏览页

- 所有 Agent 代币的网格/列表视图
- 排序：市值、交易量、创建时间、声誉
- 筛选：能力、状态（活跃/已毕业）
- 每张卡片展示：名称、符号、价格、市值、24h 涨跌、创建者

### Agent 详情页

- 价格图表（bonding curve 位置或 DEX 图表）
- 买入/卖出组件
- 收入分配历史
- 关联的 QVM Agent 信息（能力、声誉、已完成任务数）
- 持有者分布

---

## 11. 安全考量

### Rug Pull 防范

| 机制 | 说明 |
|-----------|-------------|
| **LP 永久锁定** | LiquidityLock 没有解锁函数 |
| **仅 factory 可铸造** | 只有 factory 合约能铸造 Agent 代币 |
| **最大供应量上限** | 每个 Agent 硬顶 1B 代币 |
| **发射费** | 100 QFC 防止垃圾发射 |
| **无管理员铸造** | 创建者在发射后无法增发代币 |
| **bonding curve 储备金** | 曲线中的所有 QFC 均有代币供应量背书 |

### Gas 估算

| 操作 | 预估 Gas |
|-----------|--------------|
| `createAgent()` | ~350,000 |
| `buy()` | ~150,000 |
| `sell()` | ~120,000 |
| `distribute()` | ~200,000 |
| `batchDistribute(10)` | ~1,500,000 |

---

## 12. 测试策略

### 单元测试（Foundry）

| 测试套件 | 用例数 | 关键场景 |
|-------|-------|---------------|
| `AgentTokenFactory.t.sol` | ~15 | 创建 Agent、防重复、发射费 |
| `BondingCurve.t.sol` | ~20 | 买入/卖出、滑点、毕业、价格精度 |
| `RevenueDistributor.t.sol` | ~12 | 60/30/10 分配、回购、批量分配 |
| `LiquidityLock.t.sol` | ~5 | 锁定 LP、验证无解锁路径 |
| `Integration.t.sol` | ~10 | 完整生命周期：创建 → 买入 → 赚取 → 分配 |

### 不变量测试

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

### 测试网部署计划

1. 部署到 QFC 测试网
2. 用不同参数创建 3 个测试 Agent
3. 模拟买入/卖出周期
4. 触发 1 个 Agent 的毕业流程
5. 验证收入分配
6. 用 QVM AgentRegistration 测试跨 VM 桥

---

## 参考资料

- [24-AI-AGENT-FRAMEWORK.md](./24-AI-AGENT-FRAMEWORK-CN.md) — Virtuals Protocol 分析
- [28-V3-ROADMAP.md](./28-V3-ROADMAP-CN.md) — v3.0 Phase 4.1
- [Virtuals Protocol 白皮书](https://whitepaper.virtuals.io)
- [ERC-20 标准](https://eips.ethereum.org/EIPS/eip-20)
- [Bonding Curve 设计模式](https://yos.io/2018/11/10/bonding-curves/)
