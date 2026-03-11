# ERC-4337 Agent Wallet

> Last Updated: 2026-03-11 | Version 1.0
> GitHub Issue: #23
> Author: Alex Wei, Product Manager @ QFC Network

---

## 1. Executive Summary

This document specifies a smart contract wallet template for AI agents based on ERC-4337 (Account Abstraction). The wallet provides programmable security policies — spending limits, contract allowlists, time-locks, and multi-party approval — enforced on-chain at the wallet level, not the application level.

**Key contracts**:
- `QFCAgentAccount.sol` — IAccount implementation with session keys
- `QFCAccountFactory.sol` — Deterministic CREATE2 deployment
- `QFCPaymaster.sol` — Gas sponsorship for agents
- `PolicyManager.sol` — Security policy library

---

## 2. ERC-4337 Background

### Core Concepts

| Component | Description |
|-----------|-------------|
| **EntryPoint** | Singleton contract that validates and executes UserOperations |
| **UserOperation** | Struct representing an intent to execute a transaction (replaces raw tx) |
| **Account** | Smart contract wallet that validates UserOps (implements `IAccount`) |
| **Bundler** | Off-chain service that bundles UserOps and submits to EntryPoint |
| **Paymaster** | Contract that sponsors gas for UserOps (gas abstraction) |

### Flow

```
Agent Runtime
    │
    ├─1─► Construct UserOperation (target, calldata, signature)
    │
Bundler
    ├─2─► Bundle multiple UserOps into single tx
    ├─3─► Submit to EntryPoint.handleOps()
    │
EntryPoint
    ├─4─► Call account.validateUserOp() → check signature + policies
    ├─5─► Call paymaster.validatePaymasterUserOp() → check sponsorship
    ├─6─► Call account.execute() → execute the actual operation
    └─7─► Call paymaster.postOp() → settle gas costs
```

---

## 3. Contract Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     EntryPoint (v0.7)                    │
│                   (ERC-4337 singleton)                   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────┐    ┌────────────────────────────┐ │
│  │ QFCAccountFactory │    │      QFCPaymaster          │ │
│  │ - CREATE2 deploy  │    │ - Gas sponsorship          │ │
│  │ - getAddress()    │    │ - Per-agent budgets        │ │
│  └────────┬─────────┘    │ - Rate limiting            │ │
│           │               └────────────────────────────┘ │
│           ▼                                              │
│  ┌──────────────────────────────────────────────┐       │
│  │            QFCAgentAccount                    │       │
│  │  ┌────────────────────────────────────────┐  │       │
│  │  │           PolicyManager                │  │       │
│  │  │  - SpendingLimits                      │  │       │
│  │  │  - ContractAllowlist                   │  │       │
│  │  │  - TimeLock                            │  │       │
│  │  │  - MultiPartyApproval                  │  │       │
│  │  └────────────────────────────────────────┘  │       │
│  │  ┌────────────────────────────────────────┐  │       │
│  │  │        SessionKeyManager               │  │       │
│  │  │  - Register/revoke keys                │  │       │
│  │  │  - Scoped permissions                  │  │       │
│  │  │  - TTL + nonce guard                   │  │       │
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

## 8. Session Key Design

### 8.1 Lifecycle

```
Owner                          QFCAgentAccount                    Agent Runtime
  │                                 │                                  │
  ├── addSessionKey(key, perms) ───►│                                  │
  │                                 │── emit SessionKeyAdded ─────────►│
  │                                 │                                  │
  │                                 │◄── UserOp signed with session key│
  │                                 │── validateUserOp()               │
  │                                 │   ├── check expiry               │
  │                                 │   ├── check nonce                │
  │                                 │   ├── check permissions          │
  │                                 │   └── check spending limit       │
  │                                 │── execute()                      │
  │                                 │                                  │
  ├── removeSessionKey(key) ───────►│                                  │
  │                                 │── emit SessionKeyRemoved ───────►│
  │                                 │   (key immediately invalidated)  │
```

### 8.2 Permission Scoping

| Bit | Permission | Allowed Operations |
|-----|-----------|-------------------|
| `0x01` | INFERENCE | Submit inference tasks to AI Coordinator |
| `0x02` | TRANSFER | ERC-20 token transfers (within spending limit) |
| `0x04` | STAKE | Stake/unstake QFC tokens |
| `0x08` | REGISTER | Register sub-agents |
| `0xFF` | ALL | All operations (equivalent to owner for spending limit duration) |

### 8.3 Recommended Configurations

| Use Case | Permissions | Spending Limit | TTL |
|----------|------------|----------------|-----|
| Inference-only agent | `0x01` | 50 QFC/day | 7 days |
| Trading agent | `0x03` | 500 QFC/day | 24 hours |
| Full autonomy (supervised) | `0xFF` | 1000 QFC/day | 1 hour |

---

## 9. Security Analysis

### 9.1 Attack Vectors & Mitigations

| Attack | Vector | Mitigation |
|--------|--------|------------|
| **Session key theft** | Attacker obtains session key | TTL auto-expires; spending limit caps damage |
| **Prompt injection** | LLM tricked into calling unauthorized contract | Contract allowlist blocks unknown targets |
| **Drain via many small txs** | Stay under per-tx limit | Per-period limit catches cumulative spending |
| **Flash loan attack** | Borrow → manipulate → repay in single tx | Contract allowlist blocks unknown DeFi |
| **Replay attack** | Reuse old UserOp | Nonce guard on session keys + EntryPoint nonce |
| **Paymaster drain** | Agent consumes sponsor's entire deposit | Per-op and per-day caps on sponsorship |
| **Upgrade attack** | Malicious implementation upgrade | UUPS requires owner signature |
| **Multi-agent collusion** | Multiple compromised agents coordinate | Each agent has independent limits; no shared keys |

### 9.2 Emergency Procedures

1. **Immediate**: Owner calls `removeSessionKey()` for all active keys
2. **If owner key compromised**: Governance-triggered freeze via QVM kill switch
3. **If EntryPoint bug**: Factory deploys accounts pointing to new EntryPoint (upgrade proxy)

### 9.3 Circuit Breaker

Optional: If an account triggers 3+ failed validations in 1 hour, auto-freeze all session keys. Owner must manually re-enable.

---

## 10. Integration with QFC AI Coordinator

### End-to-End: Agent Submits Inference via UserOp

```
Agent Runtime
    │
    ├─► Construct calldata: account.execute(
    │       aiCoordinator,    // target
    │       0,                 // no ETH value
    │       abi.encodeCall(AICoordinator.submitTask, (model, input, maxFee))
    │   )
    │
    ├─► Sign with session key (PERM_INFERENCE required)
    │
    ├─► Add paymasterAndData (QFCPaymaster address + sponsor signature)
    │
    ├─► Submit UserOp to Bundler
    │
Bundler → EntryPoint
    ├─► validateUserOp()  → session key valid? permission ok? spending ok?
    ├─► validatePaymasterUserOp() → sponsor has budget?
    ├─► execute() → AI Coordinator receives task
    └─► postOp() → sponsor charged for gas
```

### Allowlist Configuration for AI Agents

```solidity
// Recommended allowlist for inference-only agent:
account.addAllowedContract(AI_COORDINATOR_ADDRESS);
account.addAllowedContract(QFC_TOKEN_ADDRESS);  // For fee payment

// For trading agent, also add:
account.addAllowedContract(DEX_ROUTER_ADDRESS);
account.addAllowedContract(WQFC_ADDRESS);
```

---

## 11. SDK Integration

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

### Usage Example

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

## 12. Gas Estimates

| Operation | Estimated Gas | Notes |
|-----------|--------------|-------|
| `createAccount()` | ~350,000 | First-time proxy deployment |
| `addSessionKey()` | ~80,000 | Storage writes |
| `removeSessionKey()` | ~30,000 | Storage update |
| `execute()` (simple transfer) | ~60,000 | + target execution gas |
| `execute()` (inference submit) | ~120,000 | + AI Coordinator gas |
| `executeBatch(3)` | ~250,000 | 3 operations |
| `validateUserOp()` | ~40,000 | Signature recovery + policy checks |
| `validatePaymasterUserOp()` | ~25,000 | Sponsorship check |
| `setPerTxLimit()` | ~30,000 | Storage write |
| `addAllowedContract()` | ~45,000 | Mapping update |
| `transferOwnership()` | ~30,000 | Storage write |
| `requestTimeLock()` | ~70,000 | Storage writes |

---

## 13. Testing Strategy

### Foundry Test Suites

| Suite | Tests | Key Scenarios |
|-------|-------|---------------|
| `QFCAgentAccount.t.sol` | ~35 | Owner ops, session keys, execution, policy enforcement |
| `SessionKey.t.sol` | ~25 | Add/remove, permissions, spending limits, TTL, nonce |
| `PolicyManager.t.sol` | ~20 | Per-tx limit, per-period limit, allowlist, time-lock |
| `QFCPaymaster.t.sol` | ~20 | Deposit, sponsor, validate, postOp refund, daily cap |
| `QFCAccountFactory.t.sol` | ~10 | CREATE2, deterministic address, duplicate deploy |
| `Integration.t.sol` | ~15 | Full UserOp flow, paymaster + account + session key |

### Key Test Scenarios

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

### Testnet Deployment Plan

1. Deploy EntryPoint (or use existing ERC-4337 singleton)
2. Deploy QFCAccountFactory
3. Deploy QFCPaymaster
4. Create test accounts with various policy configs
5. Submit UserOps via bundler
6. Test session key lifecycle (add → use → expire → remove)
7. Test paymaster sponsorship with daily limits
8. Simulate attack scenarios (replay, overspend, unauthorized contract)

---

## 14. Deployment Checklist

- [ ] EntryPoint v0.7 deployed (or use canonical address)
- [ ] QFCAccountFactory deployed and verified
- [ ] QFCPaymaster deployed with initial signer
- [ ] Bundler running and connected to EntryPoint
- [ ] SDK updated with factory/paymaster addresses
- [ ] Explorer indexing UserOp events
- [ ] Documentation published

---

## References

- [24-AI-AGENT-FRAMEWORK.md](./24-AI-AGENT-FRAMEWORK-EN.md) — Agent security patterns
- [28-V3-ROADMAP.md](./28-V3-ROADMAP-EN.md) — v3.0 Phase 4.3
- [ERC-4337: Account Abstraction](https://eips.ethereum.org/EIPS/eip-4337)
- [eth-infinitism/account-abstraction](https://github.com/eth-infinitism/account-abstraction)
- [OpenZeppelin ERC-4337 Utilities](https://docs.openzeppelin.com/contracts/5.x/api/account)
- [Account Abstraction Overview — Alchemy](https://www.alchemy.com/overviews/what-is-account-abstraction)
