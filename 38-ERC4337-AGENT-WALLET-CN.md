# ERC-4337 Agent 钱包

[English](./38-ERC4337-AGENT-WALLET-EN.md) | **中文**

> 最后更新：2026-03-11 | 版本 1.0
> GitHub Issue: #23
> 作者：Alex Wei，产品经理 @ QFC Network

---

## 1. 执行摘要

本文档定义一个基于 ERC-4337（account abstraction，账户抽象）的 AI Agent 智能合约钱包模板。该钱包提供可编程的安全策略——支出限额、合约白名单、时间锁、多方审批——在钱包层面链上强制执行，而非应用层面。

**核心合约**：
- `QFCAgentAccount.sol` — 带 session key 的 IAccount 实现
- `QFCAccountFactory.sol` — 基于 CREATE2 的确定性部署
- `QFCPaymaster.sol` — 为 Agent 代付 gas
- `PolicyManager.sol` — 安全策略库

---

## 2. ERC-4337 背景

### 核心概念

| 组件 | 说明 |
|-----------|-------------|
| **EntryPoint** | 校验并执行 UserOperation 的单例合约 |
| **UserOperation** | 表示交易执行意图的结构体（替代原始交易） |
| **Account** | 校验 UserOp 的智能合约钱包（实现 `IAccount`） |
| **Bundler** | 将多个 UserOp 打包并提交到 EntryPoint 的链下服务 |
| **Paymaster** | 为 UserOp 代付 gas 的合约（gas 抽象） |

### 流程

```
Agent 运行时
    │
    ├─1─► 构造 UserOperation（target、calldata、签名）
    │
Bundler
    ├─2─► 将多个 UserOp 打包为单笔交易
    ├─3─► 提交到 EntryPoint.handleOps()
    │
EntryPoint
    ├─4─► 调用 account.validateUserOp() → 校验签名 + 策略
    ├─5─► 调用 paymaster.validatePaymasterUserOp() → 校验代付资格
    ├─6─► 调用 account.execute() → 执行实际操作
    └─7─► 调用 paymaster.postOp() → 结算 gas 费用
```

---

## 3. 合约架构

```
┌─────────────────────────────────────────────────────────┐
│                     EntryPoint (v0.7)                    │
│                   （ERC-4337 单例合约）                  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────┐    ┌────────────────────────────┐ │
│  │ QFCAccountFactory │    │      QFCPaymaster          │ │
│  │ - CREATE2 部署    │    │ - Gas 代付                 │ │
│  │ - getAddress()    │    │ - 按 Agent 设定预算        │ │
│  └────────┬─────────┘    │ - 速率限制                 │ │
│           │               └────────────────────────────┘ │
│           ▼                                              │
│  ┌──────────────────────────────────────────────┐       │
│  │            QFCAgentAccount                    │       │
│  │  ┌────────────────────────────────────────┐  │       │
│  │  │           PolicyManager                │  │       │
│  │  │  - SpendingLimits（支出限额）          │  │       │
│  │  │  - ContractAllowlist（合约白名单）     │  │       │
│  │  │  - TimeLock（时间锁）                  │  │       │
│  │  │  - MultiPartyApproval（多方审批）      │  │       │
│  │  └────────────────────────────────────────┘  │       │
│  │  ┌────────────────────────────────────────┐  │       │
│  │  │        SessionKeyManager               │  │       │
│  │  │  - 注册/撤销密钥                       │  │       │
│  │  │  - 权限范围限定                        │  │       │
│  │  │  - TTL + nonce 防护                    │  │       │
│  │  └────────────────────────────────────────┘  │       │
│  └──────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────┘
```

---

## 4. QFCAgentAccount.sol

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@account-abstraction/contracts/interfaces/IAccount.sol";
import "@account-abstraction/contracts/interfaces/IEntryPoint.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import "./PolicyManager.sol";

contract QFCAgentAccount is IAccount, Initializable, UUPSUpgradeable {
    using PolicyManager for PolicyManager.Policies;

    // ─── State ───
    IEntryPoint public immutable entryPoint;
    address public owner;
    PolicyManager.Policies internal policies;

    // Session keys
    mapping(address => SessionKey) public sessionKeys;
    address[] public sessionKeyList;

    struct SessionKey {
        uint64 permissions;         // Bitmask: INFERENCE=0x01, TRANSFER=0x02, STAKE=0x04
        uint256 spendingLimit;      // Per-period limit
        uint256 spentThisPeriod;
        uint64 periodStart;
        uint64 periodDuration;      // Seconds (e.g., 86400 for daily)
        uint64 expiresAt;           // Absolute expiry timestamp
        uint64 nonce;               // Replay protection
        bool active;
    }

    // Permission constants
    uint64 public constant PERM_INFERENCE = 0x01;
    uint64 public constant PERM_TRANSFER = 0x02;
    uint64 public constant PERM_STAKE = 0x04;
    uint64 public constant PERM_REGISTER = 0x08;
    uint64 public constant PERM_ALL = 0xFF;

    // ─── Events ───
    event SessionKeyAdded(address indexed key, uint64 permissions, uint64 expiresAt);
    event SessionKeyRemoved(address indexed key);
    event Executed(address indexed target, uint256 value, bytes data);
    event OwnerChanged(address indexed oldOwner, address indexed newOwner);

    // ─── Modifiers ───
    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    modifier onlyEntryPoint() {
        require(msg.sender == address(entryPoint), "Not EntryPoint");
        _;
    }

    modifier onlyOwnerOrEntryPoint() {
        require(msg.sender == owner || msg.sender == address(entryPoint), "Unauthorized");
        _;
    }

    // ─── Initialization ───
    constructor(IEntryPoint _entryPoint) {
        entryPoint = _entryPoint;
        _disableInitializers();
    }

    function initialize(address _owner) external initializer {
        owner = _owner;
        policies.initialize();
    }

    // ─── IAccount ───

    /// @notice Validate a UserOperation
    function validateUserOp(
        PackedUserOperation calldata userOp,
        bytes32 userOpHash,
        uint256 missingAccountFunds
    ) external override onlyEntryPoint returns (uint256 validationData) {
        // Decode signature to get signer
        address signer = _recoverSigner(userOpHash, userOp.signature);

        if (signer == owner) {
            // Owner signature — always valid
            validationData = 0; // SIG_VALIDATION_SUCCESS
        } else if (sessionKeys[signer].active) {
            // Session key — validate constraints
            SessionKey storage sk = sessionKeys[signer];

            // Check expiry
            if (block.timestamp >= sk.expiresAt) {
                return 1; // SIG_VALIDATION_FAILED
            }

            // Check nonce
            uint64 providedNonce = uint64(bytes8(userOp.signature[65:73]));
            if (providedNonce != sk.nonce) {
                return 1;
            }
            sk.nonce++;

            // Check permissions (decode from calldata)
            uint64 requiredPerm = _extractPermission(userOp.callData);
            if (sk.permissions & requiredPerm == 0) {
                return 1;
            }

            // Check spending limit
            uint256 value = _extractValue(userOp.callData);
            if (!_checkSpendingLimit(sk, value)) {
                return 1;
            }

            validationData = 0;
        } else {
            validationData = 1; // SIG_VALIDATION_FAILED
        }

        // Pay prefund if needed
        if (missingAccountFunds > 0) {
            (bool success,) = payable(msg.sender).call{value: missingAccountFunds}("");
            require(success);
        }
    }

    // ─── Execution ───

    /// @notice Execute a single call
    function execute(
        address target,
        uint256 value,
        bytes calldata data
    ) external onlyOwnerOrEntryPoint {
        // Policy checks
        require(policies.isContractAllowed(target), "Contract not allowed");
        require(policies.checkPerTxLimit(value), "Exceeds per-tx limit");
        require(policies.checkPerPeriodLimit(value), "Exceeds per-period limit");

        // Time-lock check for large amounts
        if (value > policies.timeLockThreshold) {
            require(policies.isTimeLockSatisfied(target, value, data), "Time-lock pending");
        }

        (bool success, bytes memory result) = target.call{value: value}(data);
        require(success, string(result));
        emit Executed(target, value, data);
    }

    /// @notice Execute a batch of calls
    function executeBatch(
        address[] calldata targets,
        uint256[] calldata values,
        bytes[] calldata datas
    ) external onlyOwnerOrEntryPoint {
        require(targets.length == values.length && values.length == datas.length, "Length mismatch");
        for (uint256 i = 0; i < targets.length; i++) {
            this.execute(targets[i], values[i], datas[i]);
        }
    }

    // ─── Session Key Management ───

    function addSessionKey(
        address key,
        uint64 permissions,
        uint256 spendingLimit,
        uint64 periodDuration,
        uint64 ttl
    ) external onlyOwner {
        require(!sessionKeys[key].active, "Key exists");
        sessionKeys[key] = SessionKey({
            permissions: permissions,
            spendingLimit: spendingLimit,
            spentThisPeriod: 0,
            periodStart: uint64(block.timestamp),
            periodDuration: periodDuration,
            expiresAt: uint64(block.timestamp) + ttl,
            nonce: 0,
            active: true
        });
        sessionKeyList.push(key);
        emit SessionKeyAdded(key, permissions, uint64(block.timestamp) + ttl);
    }

    function removeSessionKey(address key) external onlyOwner {
        require(sessionKeys[key].active, "Key not found");
        sessionKeys[key].active = false;
        emit SessionKeyRemoved(key);
    }

    // ─── Policy Management ───

    function setPerTxLimit(uint256 limit) external onlyOwner {
        policies.perTxLimit = limit;
    }

    function setPerPeriodLimit(uint256 limit, uint64 periodDuration) external onlyOwner {
        policies.perPeriodLimit = limit;
        policies.periodDuration = periodDuration;
    }

    function addAllowedContract(address contract_) external onlyOwner {
        policies.allowedContracts[contract_] = true;
    }

    function removeAllowedContract(address contract_) external onlyOwner {
        policies.allowedContracts[contract_] = false;
    }

    function setTimeLockThreshold(uint256 threshold, uint64 delay) external onlyOwner {
        policies.timeLockThreshold = threshold;
        policies.timeLockDelay = delay;
    }

    // ─── Owner Management ───

    function transferOwnership(address newOwner) external onlyOwner {
        require(newOwner != address(0), "Invalid owner");
        emit OwnerChanged(owner, newOwner);
        owner = newOwner;
    }

    // ─── UUPS Upgrade ───

    function _authorizeUpgrade(address) internal override onlyOwner {}

    // ─── Internal Helpers ───

    function _recoverSigner(bytes32 hash, bytes calldata signature)
        internal pure returns (address) {
        // ECDSA.recover(hash, signature[:65])
    }

    function _extractPermission(bytes calldata callData)
        internal pure returns (uint64) {
        // Decode target contract + function selector to determine required permission
        // e.g., AI Coordinator submit → PERM_INFERENCE
        //        ERC20 transfer → PERM_TRANSFER
    }

    function _extractValue(bytes calldata callData)
        internal pure returns (uint256) {
        // Extract ETH value or token amount from calldata
    }

    function _checkSpendingLimit(SessionKey storage sk, uint256 amount)
        internal returns (bool) {
        // Reset period if needed
        if (block.timestamp >= sk.periodStart + sk.periodDuration) {
            sk.spentThisPeriod = 0;
            sk.periodStart = uint64(block.timestamp);
        }
        if (sk.spentThisPeriod + amount > sk.spendingLimit) return false;
        sk.spentThisPeriod += amount;
        return true;
    }

    receive() external payable {}
}
```

---

## 5. PolicyManager.sol

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

library PolicyManager {

    struct Policies {
        // Spending limits
        uint256 perTxLimit;             // Max value per single transaction
        uint256 perPeriodLimit;         // Max total value per period
        uint64 periodDuration;          // Period length in seconds
        uint256 spentThisPeriod;
        uint64 periodStart;

        // Contract allowlist
        mapping(address => bool) allowedContracts;
        bool allowlistEnabled;         // If false, all contracts allowed

        // Time-lock
        uint256 timeLockThreshold;     // Amounts above this require time-lock
        uint64 timeLockDelay;          // Delay in seconds
        mapping(bytes32 => TimeLockRequest) pendingTimeLocks;

        // Multi-party approval
        uint8 approvalThreshold;        // Required signatures (e.g., 2 of 3)
        address[] approvers;
        mapping(bytes32 => mapping(address => bool)) approvals;
    }

    struct TimeLockRequest {
        address target;
        uint256 value;
        bytes data;
        uint64 executeAfter;
        bool executed;
    }

    function initialize(Policies storage self) internal {
        self.perTxLimit = type(uint256).max;    // No limit by default
        self.perPeriodLimit = type(uint256).max;
        self.periodDuration = 86400;             // 1 day
        self.periodStart = uint64(block.timestamp);
        self.allowlistEnabled = false;
        self.timeLockThreshold = type(uint256).max;
        self.timeLockDelay = 24 hours;
        self.approvalThreshold = 1;
    }

    function isContractAllowed(Policies storage self, address target)
        internal view returns (bool) {
        if (!self.allowlistEnabled) return true;
        return self.allowedContracts[target];
    }

    function checkPerTxLimit(Policies storage self, uint256 value)
        internal pure returns (bool) {
        return value <= self.perTxLimit;
    }

    function checkPerPeriodLimit(Policies storage self, uint256 value)
        internal returns (bool) {
        // Reset period if needed
        if (block.timestamp >= self.periodStart + self.periodDuration) {
            self.spentThisPeriod = 0;
            self.periodStart = uint64(block.timestamp);
        }
        if (self.spentThisPeriod + value > self.perPeriodLimit) return false;
        self.spentThisPeriod += value;
        return true;
    }

    /// @notice Request a time-locked operation
    function requestTimeLock(
        Policies storage self,
        address target,
        uint256 value,
        bytes calldata data
    ) internal returns (bytes32 requestId) {
        requestId = keccak256(abi.encodePacked(target, value, data, block.timestamp));
        self.pendingTimeLocks[requestId] = TimeLockRequest({
            target: target,
            value: value,
            data: data,
            executeAfter: uint64(block.timestamp) + self.timeLockDelay,
            executed: false
        });
    }

    function isTimeLockSatisfied(
        Policies storage self,
        address target,
        uint256 value,
        bytes calldata data
    ) internal view returns (bool) {
        bytes32 requestId = keccak256(abi.encodePacked(target, value, data));
        TimeLockRequest storage req = self.pendingTimeLocks[requestId];
        return req.executeAfter > 0 &&
               block.timestamp >= req.executeAfter &&
               !req.executed;
    }
}
```

---

## 6. QFCAccountFactory.sol

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/proxy/ERC1967/ERC1967Proxy.sol";
import "./QFCAgentAccount.sol";

contract QFCAccountFactory {
    QFCAgentAccount public immutable accountImplementation;

    constructor(IEntryPoint _entryPoint) {
        accountImplementation = new QFCAgentAccount(_entryPoint);
    }

    /// @notice Deploy a new agent account (deterministic address via CREATE2)
    function createAccount(
        address owner,
        uint256 salt
    ) external returns (QFCAgentAccount account) {
        address addr = getAddress(owner, salt);

        // If already deployed, return existing
        if (addr.code.length > 0) {
            return QFCAgentAccount(payable(addr));
        }

        // Deploy proxy
        account = QFCAgentAccount(payable(
            new ERC1967Proxy{salt: bytes32(salt)}(
                address(accountImplementation),
                abi.encodeCall(QFCAgentAccount.initialize, (owner))
            )
        ));
    }

    /// @notice Compute the counterfactual address
    function getAddress(
        address owner,
        uint256 salt
    ) public view returns (address) {
        return Create2.computeAddress(
            bytes32(salt),
            keccak256(abi.encodePacked(
                type(ERC1967Proxy).creationCode,
                abi.encode(
                    address(accountImplementation),
                    abi.encodeCall(QFCAgentAccount.initialize, (owner))
                )
            ))
        );
    }
}
```

---

## 7. QFCPaymaster.sol

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@account-abstraction/contracts/interfaces/IPaymaster.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";

contract QFCPaymaster is IPaymaster, Ownable {
    using ECDSA for bytes32;

    IEntryPoint public immutable entryPoint;
    address public verifyingSigner;

    // Sponsor deposits and per-agent config
    mapping(address => uint256) public sponsorDeposits;

    struct AgentSponsorConfig {
        address sponsor;
        uint256 maxPerOp;
        uint256 maxPerDay;
        uint256 spentToday;
        uint64 dayStart;
        bool active;
    }

    mapping(address => AgentSponsorConfig) public agentConfigs;

    // ─── Events ───
    event SponsorDeposited(address indexed sponsor, uint256 amount);
    event SponsorWithdrawn(address indexed sponsor, uint256 amount);
    event AgentSponsored(address indexed agent, address indexed sponsor, uint256 maxPerDay);
    event AgentSponsorRevoked(address indexed agent, address indexed sponsor);
    event GasPaid(address indexed agent, address indexed sponsor, uint256 gasUsed);

    constructor(IEntryPoint _entryPoint, address _verifyingSigner) Ownable(msg.sender) {
        entryPoint = _entryPoint;
        verifyingSigner = _verifyingSigner;
    }

    // ─── Sponsor Management ───

    function deposit() external payable {
        sponsorDeposits[msg.sender] += msg.value;
        entryPoint.depositTo{value: msg.value}(address(this));
        emit SponsorDeposited(msg.sender, msg.value);
    }

    function withdraw(uint256 amount) external {
        require(sponsorDeposits[msg.sender] >= amount, "Insufficient deposit");
        sponsorDeposits[msg.sender] -= amount;
        entryPoint.withdrawTo(payable(msg.sender), amount);
        emit SponsorWithdrawn(msg.sender, amount);
    }

    function sponsorAgent(
        address agent,
        uint256 maxPerOp,
        uint256 maxPerDay
    ) external {
        agentConfigs[agent] = AgentSponsorConfig({
            sponsor: msg.sender,
            maxPerOp: maxPerOp,
            maxPerDay: maxPerDay,
            spentToday: 0,
            dayStart: uint64(block.timestamp),
            active: true
        });
        emit AgentSponsored(agent, msg.sender, maxPerDay);
    }

    function revokeSponsorship(address agent) external {
        require(agentConfigs[agent].sponsor == msg.sender, "Not sponsor");
        agentConfigs[agent].active = false;
        emit AgentSponsorRevoked(agent, msg.sender);
    }

    // ─── IPaymaster ───

    function validatePaymasterUserOp(
        PackedUserOperation calldata userOp,
        bytes32 userOpHash,
        uint256 maxCost
    ) external override returns (bytes memory context, uint256 validationData) {
        require(msg.sender == address(entryPoint), "Not EntryPoint");

        address agent = userOp.sender;
        AgentSponsorConfig storage config = agentConfigs[agent];

        require(config.active, "No sponsorship");
        require(maxCost <= config.maxPerOp, "Exceeds per-op limit");

        // Reset daily counter if new day
        if (block.timestamp >= config.dayStart + 1 days) {
            config.spentToday = 0;
            config.dayStart = uint64(block.timestamp);
        }

        require(config.spentToday + maxCost <= config.maxPerDay, "Daily limit exceeded");
        config.spentToday += maxCost;

        context = abi.encode(agent, config.sponsor, maxCost);
        validationData = 0;
    }

    function postOp(
        PostOpMode mode,
        bytes calldata context,
        uint256 actualGasCost,
        uint256 actualUserOpFeePerGas
    ) external override {
        require(msg.sender == address(entryPoint), "Not EntryPoint");

        (address agent, address sponsor, uint256 maxCost) =
            abi.decode(context, (address, address, uint256));

        // Refund over-estimate
        uint256 refund = maxCost - actualGasCost;
        if (refund > 0) {
            agentConfigs[agent].spentToday -= refund;
        }

        // Deduct from sponsor deposit
        sponsorDeposits[sponsor] -= actualGasCost;

        emit GasPaid(agent, sponsor, actualGasCost);
    }
}
```

---

## 8. Session Key 设计

### 8.1 生命周期

```
Owner                          QFCAgentAccount                    Agent 运行时
  │                                 │                                  │
  ├── addSessionKey(key, perms) ───►│                                  │
  │                                 │── emit SessionKeyAdded ─────────►│
  │                                 │                                  │
  │                                 │◄── 使用 session key 签名的 UserOp│
  │                                 │── validateUserOp()               │
  │                                 │   ├── 校验有效期                 │
  │                                 │   ├── 校验 nonce                 │
  │                                 │   ├── 校验权限                   │
  │                                 │   └── 校验支出限额               │
  │                                 │── execute()                      │
  │                                 │                                  │
  ├── removeSessionKey(key) ───────►│                                  │
  │                                 │── emit SessionKeyRemoved ───────►│
  │                                 │   （密钥立即失效）               │
```

### 8.2 权限范围

| 位 | 权限 | 允许的操作 |
|-----|-----------|-------------------|
| `0x01` | INFERENCE | 向 AI Coordinator 提交推理任务 |
| `0x02` | TRANSFER | ERC-20 代币转账（受支出限额约束） |
| `0x04` | STAKE | 质押/解押 QFC 代币 |
| `0x08` | REGISTER | 注册子 Agent |
| `0xFF` | ALL | 所有操作（在支出限额有效期内等同于 owner） |

### 8.3 推荐配置

| 使用场景 | 权限 | 支出限额 | TTL |
|----------|------------|----------------|-----|
| 仅推理 Agent | `0x01` | 50 QFC/天 | 7 天 |
| 交易 Agent | `0x03` | 500 QFC/天 | 24 小时 |
| 完全自治（受监管） | `0xFF` | 1000 QFC/天 | 1 小时 |

---

## 9. 安全分析

### 9.1 攻击向量与缓解措施

| 攻击 | 向量 | 缓解措施 |
|--------|--------|------------|
| **Session key 被盗** | 攻击者获取 session key | TTL 自动过期；支出限额封顶损失 |
| **提示词注入** | LLM 被诱导调用未授权合约 | 合约白名单拦截未知目标 |
| **大量小额交易抽干资金** | 每笔都低于单笔限额 | 周期限额拦截累计支出 |
| **闪电贷攻击** | 单笔交易内借入 → 操纵 → 归还 | 合约白名单拦截未知 DeFi 合约 |
| **重放攻击** | 重用旧 UserOp | session key 的 nonce 防护 + EntryPoint nonce |
| **抽干 Paymaster** | Agent 耗尽赞助方全部存款 | 代付设有单次和每日上限 |
| **升级攻击** | 恶意实现合约升级 | UUPS 要求 owner 签名 |
| **多 Agent 合谋** | 多个被攻陷的 Agent 协同作案 | 每个 Agent 独立限额；无共享密钥 |

### 9.2 应急流程

1. **立即处置**：Owner 对所有活跃密钥调用 `removeSessionKey()`
2. **若 owner 密钥被盗**：通过 QVM kill switch 由治理触发冻结
3. **若 EntryPoint 存在漏洞**：Factory 部署指向新 EntryPoint 的账户（升级代理）

### 9.3 熔断机制

可选：若某账户在 1 小时内触发 3 次以上校验失败，自动冻结所有 session key。需 owner 手动重新启用。

---

## 10. 与 QFC AI Coordinator 集成

### 端到端：Agent 通过 UserOp 提交推理

```
Agent 运行时
    │
    ├─► 构造 calldata: account.execute(
    │       aiCoordinator,    // target
    │       0,                 // 无 ETH value
    │       abi.encodeCall(AICoordinator.submitTask, (model, input, maxFee))
    │   )
    │
    ├─► 使用 session key 签名（需要 PERM_INFERENCE）
    │
    ├─► 附加 paymasterAndData（QFCPaymaster 地址 + 赞助方签名）
    │
    ├─► 将 UserOp 提交到 Bundler
    │
Bundler → EntryPoint
    ├─► validateUserOp()  → session key 有效？权限满足？支出合规？
    ├─► validatePaymasterUserOp() → 赞助方预算充足？
    ├─► execute() → AI Coordinator 接收任务
    └─► postOp() → 向赞助方结算 gas
```

### AI Agent 的白名单配置

```solidity
// Recommended allowlist for inference-only agent:
account.addAllowedContract(AI_COORDINATOR_ADDRESS);
account.addAllowedContract(QFC_TOKEN_ADDRESS);  // For fee payment

// For trading agent, also add:
account.addAllowedContract(DEX_ROUTER_ADDRESS);
account.addAllowedContract(WQFC_ADDRESS);
```

---

## 11. SDK 集成

### TypeScript (qfc-sdk-js)

```typescript
import { QFCClient } from '@qfc/sdk-js';

interface AgentAccountConfig {
    owner: string;
    salt?: bigint;
    perTxLimit?: bigint;
    perPeriodLimit?: bigint;
    periodDuration?: number;
    allowedContracts?: string[];
}

class AgentAccountSDK {
    constructor(private client: QFCClient) {}

    /// Deploy a new agent account
    async createAccount(config: AgentAccountConfig): Promise<{
        address: string;
        txHash: string;
    }> { ... }

    /// Get counterfactual address before deployment
    async getAddress(owner: string, salt: bigint): Promise<string> { ... }

    /// Add a session key to an account
    async addSessionKey(params: {
        accountAddress: string;
        sessionKey: string;
        permissions: number;
        spendingLimit: bigint;
        periodDuration: number;
        ttlSeconds: number;
    }): Promise<string> { ... }

    /// Submit a UserOp through the account
    async submitUserOp(params: {
        accountAddress: string;
        target: string;
        value: bigint;
        data: string;
        sessionKey?: string; // If using session key
    }): Promise<{ userOpHash: string; txHash: string }> { ... }

    /// Configure paymaster sponsorship
    async sponsorAgent(params: {
        agentAddress: string;
        maxPerOp: bigint;
        maxPerDay: bigint;
    }): Promise<string> { ... }
}
```

### 使用示例

```typescript
const sdk = new AgentAccountSDK(qfcClient);

// 1. Deploy agent wallet
const { address: agentWallet } = await sdk.createAccount({
    owner: ownerAddress,
    perTxLimit: parseEther('10'),
    perPeriodLimit: parseEther('100'),
    allowedContracts: [AI_COORDINATOR, QFC_TOKEN],
});

// 2. Add session key for inference
await sdk.addSessionKey({
    accountAddress: agentWallet,
    sessionKey: agentKeyPair.publicKey,
    permissions: 0x01, // INFERENCE only
    spendingLimit: parseEther('50'),
    periodDuration: 86400,
    ttlSeconds: 7 * 86400,
});

// 3. Sponsor gas
await sdk.sponsorAgent({
    agentAddress: agentWallet,
    maxPerOp: parseEther('0.01'),
    maxPerDay: parseEther('1'),
});

// 4. Agent submits inference (signed with session key)
await sdk.submitUserOp({
    accountAddress: agentWallet,
    target: AI_COORDINATOR,
    value: 0n,
    data: encodeFunctionData('submitTask', [model, input, maxFee]),
    sessionKey: agentKeyPair.privateKey,
});
```

---

## 12. Gas 估算

| 操作 | 预估 Gas | 说明 |
|-----------|--------------|-------|
| `createAccount()` | ~350,000 | 首次代理部署 |
| `addSessionKey()` | ~80,000 | 存储写入 |
| `removeSessionKey()` | ~30,000 | 存储更新 |
| `execute()`（简单转账） | ~60,000 | + 目标合约执行 gas |
| `execute()`（提交推理） | ~120,000 | + AI Coordinator gas |
| `executeBatch(3)` | ~250,000 | 3 个操作 |
| `validateUserOp()` | ~40,000 | 签名恢复 + 策略检查 |
| `validatePaymasterUserOp()` | ~25,000 | 代付资格检查 |
| `setPerTxLimit()` | ~30,000 | 存储写入 |
| `addAllowedContract()` | ~45,000 | mapping 更新 |
| `transferOwnership()` | ~30,000 | 存储写入 |
| `requestTimeLock()` | ~70,000 | 存储写入 |

---

## 13. 测试策略

### Foundry 测试套件

| 套件 | 测试数 | 关键场景 |
|-------|-------|---------------|
| `QFCAgentAccount.t.sol` | ~35 | Owner 操作、session key、执行、策略执行 |
| `SessionKey.t.sol` | ~25 | 添加/移除、权限、支出限额、TTL、nonce |
| `PolicyManager.t.sol` | ~20 | 单笔限额、周期限额、白名单、时间锁 |
| `QFCPaymaster.t.sol` | ~20 | 存款、代付、校验、postOp 退款、每日上限 |
| `QFCAccountFactory.t.sol` | ~10 | CREATE2、确定性地址、重复部署 |
| `Integration.t.sol` | ~15 | 完整 UserOp 流程、paymaster + account + session key |

### 关键测试场景

```solidity
function test_sessionKey_inferenceOnly() public {
    // Session key with PERM_INFERENCE can submit inference
    // but cannot do ERC20 transfers
}

function test_spendingLimit_perPeriod() public {
    // 3 transactions within limit succeed
    // 4th transaction exceeding limit reverts
    // After period reset, succeeds again
}

function test_timeLock_largeWithdrawal() public {
    // Withdrawal above threshold: requestTimeLock() → wait → execute
    // Withdrawal below threshold: immediate
}

function test_paymaster_dailyCapEnforced() public {
    // Sponsor sets 1 ETH/day cap
    // After 1 ETH spent, next UserOp rejected
    // Next day: counter resets
}

function test_sessionKey_expired() public {
    // Create key with 1-hour TTL
    // Warp 2 hours
    // UserOp with expired key → SIG_VALIDATION_FAILED
}
```

### 测试网部署计划

1. 部署 EntryPoint（或使用现有 ERC-4337 单例）
2. 部署 QFCAccountFactory
3. 部署 QFCPaymaster
4. 用多种策略配置创建测试账户
5. 通过 bundler 提交 UserOp
6. 测试 session key 生命周期（添加 → 使用 → 过期 → 移除）
7. 测试 paymaster 代付及每日限额
8. 模拟攻击场景（重放、超额支出、未授权合约）

---

## 14. 部署检查清单

- [ ] EntryPoint v0.7 已部署（或使用规范地址）
- [ ] QFCAccountFactory 已部署并验证
- [ ] QFCPaymaster 已部署并配置初始签名者
- [ ] Bundler 已运行并连接 EntryPoint
- [ ] SDK 已更新 factory/paymaster 地址
- [ ] 区块浏览器已索引 UserOp 事件
- [ ] 文档已发布

---

## 参考资料

- [24-AI-AGENT-FRAMEWORK.md](./24-AI-AGENT-FRAMEWORK-CN.md) — Agent 安全模式
- [28-V3-ROADMAP.md](./28-V3-ROADMAP-CN.md) — v3.0 Phase 4.3
- [ERC-4337: Account Abstraction](https://eips.ethereum.org/EIPS/eip-4337)
- [eth-infinitism/account-abstraction](https://github.com/eth-infinitism/account-abstraction)
- [OpenZeppelin ERC-4337 Utilities](https://docs.openzeppelin.com/contracts/5.x/api/account)
- [Account Abstraction Overview — Alchemy](https://www.alchemy.com/overviews/what-is-account-abstraction)
