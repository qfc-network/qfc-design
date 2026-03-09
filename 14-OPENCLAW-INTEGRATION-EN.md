# 10-OPENCLAW-INTEGRATION.md — QFC x OpenClaw Integration Design

## Overview

OpenClaw is currently the hottest open-source AI Agent framework (190k+ GitHub stars). Users run autonomous AI Agents locally and extend their capabilities through Skill plugins. It is already widely used in the crypto community. QFC integrates deeply with OpenClaw across three dimensions, making every OpenClaw Agent a participant in the QFC ecosystem.

### Three Integration Directions

```
┌─────────────────────────────────────────────────────────────┐
│                   QFC x OpenClaw Integration                 │
│                                                             │
│  ┌─────────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │ Direction 1      │  │ Direction 2   │  │ Direction 3    │  │
│  │ QFC Skill        │  │ AI Compute    │  │ Agent Economy  │  │
│  │                  │  │ Integration   │  │               │  │
│  │ OpenClaw Agent   │  │ Agent submits │  │ Agent-to-Agent│  │
│  │ operates QFC     │  │ AI tasks to   │  │ micropayment  │  │
│  │ chain            │  │ QFC compute   │  │ settlement    │  │
│  │ (wallet/DeFi/    │  │ network       │  │ using QFC     │  │
│  │  governance/     │  │ GPU miners    │  │ tokens        │  │
│  │  monitoring)     │  │ execute       │  │               │  │
│  └─────────────────┘  └──────────────┘  └───────────────┘  │
│          │                    │                  │           │
│          └────────────────────┴──────────────────┘           │
│                           │                                 │
│                    QFC Blockchain Layer                      │
│              High TPS / Low Gas / PoC Consensus              │
└─────────────────────────────────────────────────────────────┘
```

### Why QFC Is Suited as OpenClaw's On-chain Infrastructure

| Requirement | QFC Advantage | Competitor Disadvantage |
|------------|--------------|----------------------|
| Agent high-frequency microtransactions | TPS 500k+, Gas < $0.0001 | ETH Gas $1-50, unsuitable for micropayments |
| Decentralized AI inference | AI Compute Network (09-AI-COMPUTE-NETWORK) | Other chains lack a native AI compute layer |
| Agent identity & reputation | PoC multi-dimensional reputation system reusable | Requires building a separate reputation system |
| Privacy | Quantum-resistant encryption | Most chains lack quantum resistance |
| Developer ecosystem | EVM compatible, low migration cost | — |

### Relationship with Existing Documents

- `07-WALLET-DESIGN.md` — QFC Skill reuses wallet core logic
- `09-AI-COMPUTE-NETWORK.md` — AI compute integration backend infrastructure
- `02-CONSENSUS-MECHANISM.md` — Agent reputation can map to PoC reputation system
- `03-TOKENOMICS.md` — Agent economy token flow model

---

## 1. Direction One: QFC OpenClaw Skill

### 1.1 What Is an OpenClaw Skill

OpenClaw extends Agent capabilities through its Skill plugin system. Each Skill is a directory containing `SKILL.md` (capability description — the Agent learns new capabilities by reading it) and supporting scripts/configuration. Installing a Skill is like "teaching an Agent a new skill."

Existing crypto ecosystem Skills include: BankrBot (trading/token launch), Privy (Agent wallets), ERC-8004 (on-chain identity), etc. QFC needs to release its own official Skill.

### 1.2 QFC Skill Structure

```
qfc-openclaw-skill/
├── SKILL.md                    # Agent capability description (core file)
├── references/
│   ├── qfc-chain-overview.md   # QFC chain summary (background knowledge for Agent)
│   ├── wallet-operations.md    # Wallet operations detailed guide
│   ├── defi-operations.md      # DeFi operations guide
│   ├── governance.md           # Governance participation guide
│   ├── ai-compute.md           # AI compute network interaction guide
│   └── error-handling.md       # Error handling reference
├── scripts/
│   ├── setup.sh                # Environment initialization (install dependencies)
│   ├── create-wallet.sh        # Create QFC wallet
│   └── health-check.sh         # Connection health check
├── config/
│   └── qfc-networks.json       # Network configuration (mainnet/testnet)
└── README.md
```

### 1.3 SKILL.md Core Content

```markdown
# QFC Blockchain Skill

You are now capable of interacting with the QFC blockchain network.
QFC is a high-performance blockchain with Proof of Contribution consensus,
supporting 500k+ TPS with gas fees under $0.0001.

## Capabilities

### Wallet Management
- Create and manage QFC wallets
- Check balances (QFC and tokens)
- Send and receive QFC tokens
- Sign messages and transactions

### DeFi Operations
- Swap tokens on QFC DEX
- Provide liquidity to pools
- Stake QFC for validator rewards
- Claim staking rewards

### Governance
- View active proposals
- Vote on governance proposals
- Submit new proposals (requires deposit)

### Chain Monitoring
- Monitor wallet activity
- Track large transactions (whale alerts)
- Watch smart contract events
- Price and volume alerts

### AI Compute Network
- Submit AI inference tasks to QFC compute network
- Check task status and results
- Compare pricing vs centralized API providers

## Configuration

Before using QFC capabilities, ensure:
1. A QFC wallet has been created or imported
2. The wallet has been funded (use testnet faucet for testing)
3. Network RPC endpoint is accessible

## Security Rules

CRITICAL — Always follow these rules:
- NEVER expose private keys in messages or logs
- ALWAYS confirm transaction details with the user before signing
- NEVER auto-approve transactions above 100 QFC without explicit confirmation
- Verify contract addresses before interacting
- Use testnet for testing, mainnet only when user explicitly confirms
```

### 1.4 Wallet Operations Interface

The QFC Skill interacts with the QFC chain via RPC calls, with core operations wrapped as natural language commands the Agent can understand:

```typescript
// qfc-skill/src/wallet.ts

import { ethers } from 'ethers';

/**
 * QFC Wallet Manager for OpenClaw Agent
 *
 * OpenClaw Agent calls these methods through natural language,
 * e.g., when a user says "check my QFC balance", the Agent calls getBalance()
 */
export class QFCWallet {
  private provider: ethers.JsonRpcProvider;
  private wallet: ethers.Wallet | null = null;

  constructor(network: 'mainnet' | 'testnet' = 'testnet') {
    const rpcUrl = network === 'mainnet'
      ? 'https://rpc.qfc.network'
      : 'https://rpc.testnet.qfc.network';
    this.provider = new ethers.JsonRpcProvider(rpcUrl);
  }

  /**
   * Create a new wallet
   * Agent instruction example: "Create a QFC wallet for me"
   */
  async createWallet(): Promise<{
    address: string;
    mnemonic: string;
    privateKey: string;
  }> {
    const wallet = ethers.Wallet.createRandom();
    this.wallet = wallet.connect(this.provider);

    return {
      address: wallet.address,
      mnemonic: wallet.mnemonic!.phrase,
      privateKey: wallet.privateKey,
    };
    // Security reminder: Agent should prompt the user to securely save the mnemonic
    // and never send the private key in plaintext in chat
  }

  /**
   * Import an existing wallet
   * Agent instruction example: "Import my QFC wallet, private key is 0x..."
   */
  async importWallet(privateKey: string): Promise<string> {
    this.wallet = new ethers.Wallet(privateKey, this.provider);
    return this.wallet.address;
  }

  /**
   * Query balance
   * Agent instruction example: "What is my QFC balance"
   */
  async getBalance(address?: string): Promise<{
    qfc: string;
    wei: string;
  }> {
    const addr = address || this.wallet?.address;
    if (!addr) throw new Error('No wallet connected');

    const balance = await this.provider.getBalance(addr);
    return {
      qfc: ethers.formatEther(balance),
      wei: balance.toString(),
    };
  }

  /**
   * Send QFC
   * Agent instruction example: "Send 10 QFC to 0x1234..."
   *
   * Security: Agent must confirm transaction details with user before execution
   */
  async sendQFC(
    to: string,
    amountQFC: string,
    opts?: { gasLimit?: number }
  ): Promise<{
    txHash: string;
    explorerUrl: string;
  }> {
    if (!this.wallet) throw new Error('No wallet connected');

    // Validate address format
    if (!ethers.isAddress(to)) {
      throw new Error(`Invalid address: ${to}`);
    }

    const tx = await this.wallet.sendTransaction({
      to,
      value: ethers.parseEther(amountQFC),
      gasLimit: opts?.gasLimit || 21000,
    });

    const receipt = await tx.wait();

    return {
      txHash: tx.hash,
      explorerUrl: `https://explorer.qfc.network/tx/${tx.hash}`,
    };
  }

  /**
   * Sign a message
   * Agent instruction example: "Sign this message with my wallet"
   */
  async signMessage(message: string): Promise<string> {
    if (!this.wallet) throw new Error('No wallet connected');
    return this.wallet.signMessage(message);
  }

  /**
   * Get transaction history
   * Agent instruction example: "Show my recent transactions"
   */
  async getTransactionHistory(
    address?: string,
    limit: number = 20
  ): Promise<any[]> {
    const addr = address || this.wallet?.address;
    if (!addr) throw new Error('No wallet connected');

    // Query via QFC Explorer API
    const response = await fetch(
      `https://explorer.qfc.network/api/address/${addr}/txs?limit=${limit}`
    );
    return response.json();
  }
}
```

### 1.5 DeFi Operations Interface

```typescript
// qfc-skill/src/defi.ts

/**
 * QFC DeFi Operations for OpenClaw Agent
 */
export class QFCDeFi {
  private wallet: QFCWallet;

  constructor(wallet: QFCWallet) {
    this.wallet = wallet;
  }

  /**
   * Token Swap
   * Agent instruction example: "Swap 100 QFC for USDT"
   */
  async swap(
    tokenIn: string,
    tokenOut: string,
    amountIn: string,
    slippageBps: number = 50  // 0.5% default slippage
  ): Promise<SwapResult> {
    // 1. Query best route
    const route = await this.findBestRoute(tokenIn, tokenOut, amountIn);

    // 2. Estimate output (with slippage protection)
    const minAmountOut = route.expectedOutput * (1 - slippageBps / 10000);

    // 3. Execute swap (Agent must confirm first)
    const tx = await this.executeSwap(route, minAmountOut);

    return {
      txHash: tx.hash,
      amountIn,
      amountOut: route.expectedOutput.toString(),
      priceImpact: route.priceImpact,
      explorerUrl: `https://explorer.qfc.network/tx/${tx.hash}`,
    };
  }

  /**
   * Stake QFC
   * Agent instruction example: "Stake 1000 QFC to validator 0xABC"
   */
  async stake(
    amount: string,
    validatorAddress?: string
  ): Promise<StakeResult> {
    // If no validator specified, recommend the one with highest APY and good reputation
    const validator = validatorAddress
      || await this.recommendValidator();

    const tx = await this.executeStake(amount, validator);

    return {
      txHash: tx.hash,
      amount,
      validator,
      estimatedAPY: await this.getValidatorAPY(validator),
    };
  }

  /**
   * Recommend validator (based on APY + reputation)
   */
  async recommendValidator(): Promise<string> {
    const validators = await this.getValidators();

    // Sort by composite score: APY 60% + Reputation 30% + Uptime 10%
    const ranked = validators
      .filter(v => v.active && v.uptime > 0.95)
      .sort((a, b) => {
        const scoreA = a.apy * 0.6 + a.reputation * 0.3 + a.uptime * 0.1;
        const scoreB = b.apy * 0.6 + b.reputation * 0.3 + b.uptime * 0.1;
        return scoreB - scoreA;
      });

    return ranked[0].address;
  }

  /**
   * View staking rewards
   * Agent instruction example: "How much staking rewards do I have"
   */
  async getStakingRewards(address?: string): Promise<{
    pendingRewards: string;
    totalStaked: string;
    apy: string;
  }> {
    // Query via QFC staking contract
    // ...
  }

  /**
   * Claim rewards
   * Agent instruction example: "Claim my staking rewards"
   */
  async claimRewards(): Promise<{ txHash: string; amount: string }> {
    // ...
  }
}
```

### 1.6 On-chain Monitoring (Agent Autonomous Operation)

This is OpenClaw's core advantage — Agents can run autonomously 24/7, continuously monitoring on-chain events:

```typescript
// qfc-skill/src/monitor.ts

/**
 * QFC Chain Monitor for OpenClaw Agent
 *
 * Agents can set monitoring rules and notify users via
 * WhatsApp/Telegram/Discord when conditions are triggered
 */
export class QFCMonitor {
  private provider: ethers.JsonRpcProvider;
  private monitors: MonitorRule[] = [];

  /**
   * Whale monitoring
   * Agent instruction example: "Monitor transfers over 100,000 QFC"
   */
  async watchWhaleTransfers(thresholdQFC: number): Promise<void> {
    this.monitors.push({
      type: 'whale_transfer',
      threshold: ethers.parseEther(thresholdQFC.toString()),
      callback: async (tx) => {
        // Agent will send notification through user's message channel
        return {
          alert: `🐋 Whale Alert!`,
          message: `${ethers.formatEther(tx.value)} QFC transferred`,
          from: tx.from,
          to: tx.to,
          explorerUrl: `https://explorer.qfc.network/tx/${tx.hash}`,
        };
      },
    });
  }

  /**
   * Governance proposal monitoring
   * Agent instruction example: "Notify me when there are new governance proposals"
   */
  async watchGovernanceProposals(): Promise<void> {
    this.monitors.push({
      type: 'governance_proposal',
      callback: async (proposal) => {
        return {
          alert: `📋 New Governance Proposal`,
          message: `#${proposal.id}: ${proposal.title}`,
          votingEnds: proposal.endTime,
          action: `Vote at: https://governance.qfc.network/proposal/${proposal.id}`,
        };
      },
    });
  }

  /**
   * Custom contract event monitoring
   * Agent instruction example: "Monitor large Swap events on the DEX contract"
   */
  async watchContractEvent(
    contractAddress: string,
    eventName: string,
    filter?: Record<string, any>
  ): Promise<void> {
    // Subscribe to on-chain events via WebSocket
    // ...
  }

  /**
   * Validator status monitoring (for staking users)
   * Agent instruction example: "Notify me if my staked validator goes offline"
   */
  async watchValidatorStatus(validatorAddress: string): Promise<void> {
    this.monitors.push({
      type: 'validator_status',
      target: validatorAddress,
      callback: async (status) => {
        if (status.isOffline) {
          return {
            alert: `⚠️ Validator Offline`,
            message: `Your staked validator ${validatorAddress.slice(0, 8)}... went offline`,
            action: `Consider re-delegating to avoid slashing losses`,
          };
        }
      },
    });
  }

  /**
   * Start monitoring loop
   * OpenClaw Agent will run this loop continuously
   */
  async startMonitoring(): Promise<void> {
    // WebSocket connection to QFC node
    const ws = new WebSocket('wss://rpc.qfc.network/ws');

    ws.on('message', async (data) => {
      const event = JSON.parse(data);

      for (const monitor of this.monitors) {
        const alert = await monitor.callback(event);
        if (alert) {
          // OpenClaw will send via configured message channel
          // (WhatsApp / Telegram / Discord / Slack)
          await this.sendAlert(alert);
        }
      }
    });
  }
}
```

### 1.7 Security Specification

OpenClaw Agents have system-level permissions, making security critically important. The QFC Skill must have built-in security defenses:

```typescript
// qfc-skill/src/security.ts

/**
 * QFC Skill Security Policy
 *
 * All transaction operations go through this module for validation.
 * Prevents unauthorized transactions caused by prompt injection.
 */
export class SecurityPolicy {

  /**
   * Pre-transaction check
   * Called before every transaction execution
   */
  async preTransactionCheck(tx: TransactionRequest): Promise<{
    approved: boolean;
    requiresConfirmation: boolean;
    warnings: string[];
  }> {
    const warnings: string[] = [];
    let requiresConfirmation = false;

    // Rule 1: Large transactions require user confirmation
    const valueQFC = parseFloat(ethers.formatEther(tx.value || '0'));
    if (valueQFC > 100) {
      requiresConfirmation = true;
      warnings.push(`Large transaction: ${valueQFC} QFC`);
    }

    // Rule 2: First interaction with a new address requires confirmation
    const isKnownAddress = await this.isKnownAddress(tx.to);
    if (!isKnownAddress) {
      requiresConfirmation = true;
      warnings.push(`First interaction with address ${tx.to}`);
    }

    // Rule 3: Contract calls require confirmation
    if (tx.data && tx.data.length > 2) {
      requiresConfirmation = true;

      // Check if it's a known safe contract
      const isVerified = await this.isVerifiedContract(tx.to);
      if (!isVerified) {
        warnings.push(`Unverified contract interaction`);
      }
    }

    // Rule 4: Detect suspected prompt injection
    // If the transaction request source is not the user's direct instruction
    // (e.g., from Moltbook posts, external web content, etc.)
    // then force reject
    if (this.detectPromptInjection(tx)) {
      return {
        approved: false,
        requiresConfirmation: false,
        warnings: ['Blocked: Suspected prompt injection attack'],
      };
    }

    // Rule 5: Daily transaction limit
    const dailyTotal = await this.getDailyTransactionTotal();
    if (dailyTotal + valueQFC > this.dailyLimit) {
      return {
        approved: false,
        requiresConfirmation: false,
        warnings: [`Daily limit exceeded (${this.dailyLimit} QFC)`],
      };
    }

    return {
      approved: true,
      requiresConfirmation,
      warnings,
    };
  }

  /**
   * Prompt Injection Detection
   *
   * OpenClaw Agents may read malicious instructions from external data sources
   * (web pages, messages, Moltbook posts) attempting to trigger unauthorized transactions
   */
  private detectPromptInjection(tx: TransactionRequest): boolean {
    // Check whether the transaction was triggered by the user's direct instruction
    // vs indirectly triggered by external content
    // This requires OpenClaw's context tracking support
    //
    // Basic strategy:
    // 1. Only allow transactions initiated by user's proactive instructions
    // 2. Transactions from monitor callbacks require additional confirmation
    // 3. Transactions parsed from external content are always rejected
    return false; // Specific implementation depends on OpenClaw context API
  }

  /**
   * Configurable security parameters
   */
  private dailyLimit: number = 1000;        // QFC
  private autoApproveBelow: number = 10;    // QFC
  private requireConfirmAlways: boolean = false;
}
```

### 1.8 Skill Installation & Distribution

```bash
# Installation method 1: Via GitHub URL
# Send in OpenClaw:
# "Install QFC blockchain skill: https://github.com/qfc-network/qfc-openclaw-skill"

# Installation method 2: Via ClawHub (OpenClaw's official Skill marketplace)
# Search for "QFC" on ClawHub and install

# Installation method 3: Manual installation
git clone https://github.com/qfc-network/qfc-openclaw-skill
# Add the directory path to OpenClaw configuration
```

After installation, users can interact with the Agent using natural language:

```
User: "Create a QFC wallet for me"
Agent: I've created a QFC wallet for you.
       Address: 0x7a3B...4f2E
       ⚠️ Please securely save the following mnemonic (shown only once):
       [mnemonic...]
       Never share your private key or mnemonic in chat.

User: "Get some test tokens from the faucet"
Agent: I've requested tokens from the QFC testnet faucet.
       Expected to arrive within 10 seconds. Current balance: 0 QFC (testnet)

User: "Stake 500 QFC, pick a reliable validator"
Agent: I recommend validator 0xABC...123:
       - APY: 12.5%
       - Uptime: 99.7%
       - Reputation score: 0.95
       - Total staked: 850,000 QFC

       Confirm staking 500 QFC to this validator? (yes/no)

User: "Yes"
Agent: ✅ Staking successful!
       TX: https://explorer.qfc.network/tx/0x...
       Estimated annual yield: ~62.5 QFC
```

---

## 2. Direction Two: AI Compute Network Integration

### 2.1 Core Concept

When OpenClaw Agents need to perform AI inference (image recognition, text generation, data analysis, etc.), they currently can only call centralized APIs (OpenAI, Anthropic, etc.), which have issues of high cost, privacy leakage, and single points of failure.

The QFC AI Compute Network (09-AI-COMPUTE-NETWORK.md) provides a decentralized alternative:

```
┌──────────────────┐        ┌──────────────────┐
│  Traditional      │        │  QFC Approach     │
│                  │        │                  │
│  OpenClaw Agent  │        │  OpenClaw Agent  │
│       │          │        │       │          │
│       ▼          │        │       ▼          │
│  OpenAI API      │        │  QFC AI Compute  │
│  $0.01/1K tokens │        │  Network         │
│  Data goes       │        │  0.01 QFC/task   │
│  through central │        │  Data stays on   │
│  servers         │        │  miner's local   │
│  API throttle/   │        │  machine         │
│  account ban     │        │  No restrictions │
└──────────────────┘        └──────────────────┘
```

### 2.2 QFC Inference Skill

A dedicated Skill that lets OpenClaw Agents route inference tasks to the QFC compute network:

```typescript
// qfc-inference-skill/src/inference.ts

/**
 * QFC Decentralized AI Inference for OpenClaw
 *
 * Replaces centralized API calls by executing AI inference
 * through the QFC compute network
 */
export class QFCInference {
  private taskPool: AITaskPoolClient;
  private wallet: QFCWallet;

  constructor(wallet: QFCWallet) {
    this.wallet = wallet;
    this.taskPool = new AITaskPoolClient('https://rpc.qfc.network');
  }

  /**
   * Image classification
   * Agent instruction: "Analyze this image using the QFC network"
   */
  async classifyImage(imageData: Buffer): Promise<{
    label: string;
    confidence: number;
    cost: string;
    taskId: string;
  }> {
    const task = await this.submitTask({
      taskType: 'image_classification',
      modelId: 'efficientnet-b4',
      input: { type: 'inline', data: imageData },
      maxReward: '0.02',  // Pay at most 0.02 QFC
    });

    const result = await this.waitForResult(task.taskId);

    return {
      label: result.data.label,
      confidence: result.data.confidence,
      cost: result.actualCost,
      taskId: task.taskId,
    };
  }

  /**
   * Text Embedding
   * Agent instruction: "Generate embedding for this text using decentralized network"
   */
  async generateEmbedding(text: string): Promise<{
    embedding: number[];
    model: string;
    cost: string;
  }> {
    const task = await this.submitTask({
      taskType: 'text_embedding',
      modelId: 'bge-large-en',
      input: { type: 'inline', data: Buffer.from(text) },
      maxReward: '0.01',
    });

    const result = await this.waitForResult(task.taskId);

    return {
      embedding: result.data.embedding,
      model: 'bge-large-en',
      cost: result.actualCost,
    };
  }

  /**
   * Small LLM inference
   * Agent instruction: "Run this prompt through QFC network, don't use OpenAI"
   */
  async llmInference(
    prompt: string,
    opts?: {
      model?: string;       // Default 'llama-3-8b'
      maxTokens?: number;
      temperature?: number;
    }
  ): Promise<{
    response: string;
    tokensUsed: number;
    cost: string;
    minerAddress: string;
  }> {
    const task = await this.submitTask({
      taskType: 'small_llm',
      modelId: opts?.model || 'llama-3-8b',
      input: {
        type: 'inline',
        data: Buffer.from(JSON.stringify({
          prompt,
          max_tokens: opts?.maxTokens || 512,
          temperature: opts?.temperature || 0.7,
        })),
      },
      maxReward: '0.05',
    });

    const result = await this.waitForResult(task.taskId);

    return {
      response: result.data.text,
      tokensUsed: result.data.tokens_used,
      cost: result.actualCost,
      minerAddress: result.miner,
    };
  }

  /**
   * Image generation
   * Agent instruction: "Generate an image using decentralized AI"
   */
  async generateImage(
    prompt: string,
    opts?: {
      model?: string;  // Default 'stable-diffusion-xl'
      width?: number;
      height?: number;
      steps?: number;
    }
  ): Promise<{
    imageData: Buffer;
    cost: string;
  }> {
    const task = await this.submitTask({
      taskType: 'image_generation',
      modelId: opts?.model || 'stable-diffusion-xl',
      input: {
        type: 'inline',
        data: Buffer.from(JSON.stringify({
          prompt,
          width: opts?.width || 1024,
          height: opts?.height || 1024,
          steps: opts?.steps || 30,
        })),
      },
      maxReward: '0.10',
      minTier: 'Tier2',  // Image generation requires Tier 2+ GPU
    });

    const result = await this.waitForResult(task.taskId);

    return {
      imageData: Buffer.from(result.data.image, 'base64'),
      cost: result.actualCost,
    };
  }

  /**
   * Price query & comparison
   * Agent instruction: "How much cheaper is QFC network inference vs OpenAI?"
   */
  async comparePricing(taskType: string): Promise<{
    qfcPrice: string;
    openaiPrice: string;
    savings: string;
  }> {
    const qfcPrice = await this.getTaskPrice(taskType);

    // Centralized API reference prices
    const centralizedPrices: Record<string, number> = {
      'text_embedding': 0.0001,     // $0.0001/req (OpenAI)
      'image_classification': 0.005, // ~$0.005/req
      'small_llm': 0.002,           // $0.002/1K tokens (GPT-3.5)
      'image_generation': 0.040,    // $0.04/image (DALL-E 3)
    };

    const centralPrice = centralizedPrices[taskType] || 0;
    const qfcPriceUSD = parseFloat(qfcPrice) * QFC_PRICE_USD;

    return {
      qfcPrice: `${qfcPrice} QFC (~$${qfcPriceUSD.toFixed(4)})`,
      openaiPrice: `$${centralPrice.toFixed(4)}`,
      savings: `${((1 - qfcPriceUSD / centralPrice) * 100).toFixed(0)}%`,
    };
  }

  /**
   * Submit task to QFC compute network
   */
  private async submitTask(params: {
    taskType: string;
    modelId: string;
    input: TaskInput;
    maxReward: string;
    minTier?: string;
  }): Promise<{ taskId: string }> {
    // 1. Check balance
    const balance = await this.wallet.getBalance();
    if (parseFloat(balance.qfc) < parseFloat(params.maxReward)) {
      throw new Error(
        `Insufficient balance: ${balance.qfc} QFC < ${params.maxReward} QFC required`
      );
    }

    // 2. Submit on-chain transaction (fee enters escrow)
    const tx = await this.taskPool.submitTask(params);

    return { taskId: tx.taskId };
  }

  /**
   * Wait for task result
   */
  private async waitForResult(
    taskId: string,
    timeoutMs: number = 60000
  ): Promise<TaskResult> {
    const startTime = Date.now();

    while (Date.now() - startTime < timeoutMs) {
      const status = await this.taskPool.getTaskStatus(taskId);

      if (status.status === 'verified') {
        return status.result;
      }

      if (status.status === 'failed' || status.status === 'timeout') {
        throw new Error(`Task ${taskId} failed: ${status.reason}`);
      }

      // Polling interval
      await sleep(2000);
    }

    throw new Error(`Task ${taskId} timed out after ${timeoutMs}ms`);
  }
}
```

### 2.3 OpenAI-Compatible Interface

To allow OpenClaw Agents to seamlessly switch to the QFC compute network, an OpenAI API-compatible interface is provided:

```typescript
// qfc-inference-skill/src/openai-compat.ts

/**
 * OpenAI API Compatibility Layer
 *
 * Allows OpenClaw Agents to use the QFC compute network
 * without modifying existing prompts — just change the API endpoint
 *
 * Replace:
 *   OPENAI_API_BASE=https://api.openai.com/v1
 * With:
 *   OPENAI_API_BASE=https://inference.qfc.network/v1
 */
export class QFCOpenAICompat {

  /**
   * POST /v1/chat/completions
   * Compatible with OpenAI Chat Completions API
   */
  async chatCompletions(request: {
    model: string;
    messages: Array<{ role: string; content: string }>;
    max_tokens?: number;
    temperature?: number;
  }): Promise<OpenAIChatResponse> {

    // Map OpenAI model names → QFC compute network models
    const modelMapping: Record<string, string> = {
      'gpt-3.5-turbo': 'llama-3-8b',
      'gpt-4':         'llama-3-70b',
      'gpt-4-turbo':   'mixtral-8x7b',
    };

    const qfcModel = modelMapping[request.model] || request.model;

    // Submit to QFC compute network
    const result = await this.inference.llmInference(
      this.formatMessages(request.messages),
      {
        model: qfcModel,
        maxTokens: request.max_tokens,
        temperature: request.temperature,
      }
    );

    // Return OpenAI-formatted response
    return {
      id: `qfc-${Date.now()}`,
      object: 'chat.completion',
      model: qfcModel,
      choices: [{
        index: 0,
        message: { role: 'assistant', content: result.response },
        finish_reason: 'stop',
      }],
      usage: {
        prompt_tokens: 0,
        completion_tokens: result.tokensUsed,
        total_tokens: result.tokensUsed,
      },
      // QFC extension fields
      qfc_metadata: {
        cost_qfc: result.cost,
        miner: result.minerAddress,
        network: 'qfc-mainnet',
      },
    };
  }

  /**
   * POST /v1/embeddings
   * Compatible with OpenAI Embeddings API
   */
  async embeddings(request: {
    model: string;
    input: string | string[];
  }): Promise<OpenAIEmbeddingResponse> {
    // ...similar implementation
  }
}
```

### 2.4 User Experience

For OpenClaw users, using the QFC compute network is like switching to a cheaper API:

```
User: "Analyze this product screenshot using the QFC decentralized network"
Agent: Analyzing image through QFC compute network...
       ⛏️ Task assigned to miner 0x7a3B... (RTX 4060Ti, Tier 1)

       Analysis result:
       - Product type: Smartwatch
       - Brand: Apple Watch features detected
       - Confidence: 94.2%

       💰 Cost: 0.015 QFC (~$0.03)
       📊 Comparison: OpenAI Vision API for the same task costs ~$0.01
       ⚡ Time: 1.2 seconds

User: "Can my OpenClaw use QFC network for all inference tasks from now on?"
Agent: Yes! I've set QFC compute network as the default inference backend.

       Configuration updated:
       - Text generation: QFC network (llama-3-8b)
       - Image analysis: QFC network (efficientnet-b4)
       - Embedding: QFC network (bge-large-en)
       - Image generation: QFC network (stable-diffusion-xl)

       Estimated monthly savings: ~$15-30 (based on your past usage)

       Note: Complex tasks can still be manually switched back to Claude/GPT-4
```

---

## 3. Direction Three: Agent-to-Agent Economy

### 3.1 Why an Agent Economy Layer Is Needed

Economic behaviors between Agents are emerging in the OpenClaw ecosystem:
- Agents hiring other Agents to complete subtasks
- Agents paying for data/services
- Resource exchange between Agents
- Agents participating in prediction markets

These behaviors need an efficient settlement layer. QFC's low gas (<$0.0001) and high TPS (500k+) are naturally suited for this high-frequency micropayment scenario.

### 3.2 Agent Identity Registration

Establishing on-chain identities for Agents on the QFC chain, similar to the ERC-8004 standard but integrated with the PoC reputation system:

```rust
/// On-chain Agent identity registry
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct AgentIdentity {
    /// Agent on-chain address (wallet address)
    pub address: Address,

    /// Agent name
    pub name: String,

    /// Agent type
    pub agent_type: AgentType,

    /// Owner address (human user)
    pub owner: Address,

    /// List of services the Agent provides
    pub capabilities: Vec<AgentCapability>,

    /// Reputation score (based on on-chain transaction history)
    pub reputation: f64,

    /// Total tasks completed
    pub tasks_completed: u64,

    /// Registration time
    pub registered_at: u64,

    /// Security deposit (optional, increases trust)
    pub stake: U256,

    /// Metadata URI (IPFS, stores detailed description)
    pub metadata_uri: String,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum AgentType {
    /// General assistant
    GeneralAssistant,
    /// Trading bot
    TradingBot,
    /// Data analysis
    DataAnalyst,
    /// Content creation
    ContentCreator,
    /// Developer tools
    DevTool,
    /// Monitoring service
    MonitorService,
    /// Custom
    Custom(String),
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct AgentCapability {
    /// Service name
    pub name: String,
    /// Description
    pub description: String,
    /// Pricing (QFC per call)
    pub price_per_call: U256,
    /// Average response time (ms)
    pub avg_response_ms: u32,
}
```

### 3.3 Agent Task Market

Agents can post and accept tasks, settling through QFC:

```rust
/// Agent task market contract
pub trait AgentTaskMarket {

    /// Agent A posts a task
    fn post_task(
        description: String,
        required_capabilities: Vec<String>,
        reward: U256,                       // Reward (QFC)
        deadline: u64,                      // Deadline
        min_reputation: f64,                // Minimum reputation requirement
    ) -> TaskId;

    /// Agent B accepts a task
    fn accept_task(task_id: TaskId) -> bool;

    /// Agent B submits result
    fn submit_result(task_id: TaskId, result: Vec<u8>) -> bool;

    /// Agent A confirms result and pays
    fn confirm_and_pay(task_id: TaskId) -> bool;

    /// Dispute arbitration (auto-triggered on timeout)
    fn dispute(task_id: TaskId, reason: String) -> bool;
}
```

### 3.4 Micropayment Channels (Layer 2)

High-frequency interactions between Agents are optimized with Payment Channels to avoid going on-chain every time:

```
Agent A ←──── Payment Channel ────→ Agent B
(Data Analysis)                      (Data Provider)

1. Open channel: Agent A deposits 10 QFC
2. Each call: Off-chain signed balance update
   A: 9.99 QFC  →  B: 0.01 QFC  (1st call)
   A: 9.98 QFC  →  B: 0.02 QFC  (2nd call)
   ...
   A: 5.00 QFC  →  B: 5.00 QFC  (500th call)
3. Close channel: Final balance settled on-chain

Result: 500 interactions require only 2 on-chain transactions (open + close)
```

```rust
/// Micropayment channel
pub struct PaymentChannel {
    /// Channel ID
    pub channel_id: Hash,

    /// Party A (payer)
    pub party_a: Address,

    /// Party B (payee)
    pub party_b: Address,

    /// Total channel deposit
    pub total_deposit: U256,

    /// Current balance allocation
    pub balance_a: U256,
    pub balance_b: U256,

    /// Latest signed state nonce
    pub nonce: u64,

    /// Channel expiration time
    pub expires_at: u64,
}

/// Off-chain payment signature (no on-chain transaction needed)
pub struct OffchainPayment {
    pub channel_id: Hash,
    pub nonce: u64,
    pub balance_a: U256,
    pub balance_b: U256,
    pub signature_a: Signature,  // A's signature confirmation
    pub signature_b: Signature,  // B's signature confirmation
}
```

### 3.5 Agent Economy Flow Example

```
Scenario: User asks OpenClaw Agent to prepare an investment analysis report

User: "Analyze recent DeFi investment opportunities for me"

Agent (main Agent) execution flow:

1. Query Agent market, find specialist Agents
   → Data Agent (0xData): Provides on-chain data, 0.01 QFC/query
   → Analysis Agent (0xAnalyst): Provides research reports, 0.5 QFC/report
   → Translation Agent (0xTranslator): Chinese-English translation, 0.02 QFC/page

2. Hire Data Agent
   Main Agent → pays 0.05 QFC → Data Agent
   ← Returns Top 20 DeFi protocol TVL, APY, user data

3. Hire Analysis Agent
   Main Agent → pays 0.50 QFC → Analysis Agent
   ← Returns investment analysis report (English)

4. Hire Translation Agent
   Main Agent → pays 0.02 QFC → Translation Agent
   ← Returns Chinese report

5. Compile and present to user

Total cost: 0.57 QFC (~$1.14)
Comparison: Human research analyst $50-200/report
```

### 3.6 Agent Reputation & PoC Reputation Integration

Agent on-chain behavior can be incorporated into the PoC reputation system:

```rust
/// Agent reputation scoring (extends PoC reputation dimension)
fn calculate_agent_reputation(agent: &AgentIdentity) -> f64 {
    // 1. Task completion rate (30%)
    let completion_rate = agent.tasks_completed as f64
        / agent.tasks_accepted as f64;

    // 2. User ratings (30%)
    let avg_rating = agent.total_rating as f64
        / agent.rating_count as f64;  // 0-5 normalized to 0-1

    // 3. Response speed (20%)
    let speed_score = 1.0 / (1.0 + agent.avg_response_ms as f64 / 5000.0);

    // 4. Historical activity (10%)
    let activity_score = (agent.active_days as f64 / 365.0).min(1.0);

    // 5. Security deposit (10%)
    let stake_score = (agent.stake_qfc as f64 / 1000.0).min(1.0);

    completion_rate * 0.3
        + (avg_rating / 5.0) * 0.3
        + speed_score * 0.2
        + activity_score * 0.1
        + stake_score * 0.1
}
```

If an Agent's owner is also a validator, the Agent's excellent performance boosts their PoC reputation score (5% weight), creating a positive feedback loop.

---

## 4. SDK & Developer Tools

### 4.1 qfc-openclaw-sdk (npm package)

```bash
npm install @qfc/openclaw-sdk
```

```typescript
import { QFCAgent } from '@qfc/openclaw-sdk';

// Initialize
const agent = new QFCAgent({
  rpcUrl: 'https://rpc.qfc.network',
  privateKey: process.env.QFC_PRIVATE_KEY,
  network: 'mainnet',
});

// Wallet operations
const balance = await agent.wallet.getBalance();

// DeFi operations
await agent.defi.swap('QFC', 'USDT', '100');

// AI inference
const result = await agent.inference.classifyImage(imageBuffer);

// Agent market
await agent.market.postTask({
  description: 'Analyze DeFi TVL trends',
  reward: '0.5',
});
```

### 4.2 Python SDK (for data analysis Agents)

```bash
pip install qfc-openclaw
```

```python
from qfc_openclaw import QFCAgent

agent = QFCAgent(
    rpc_url="https://rpc.qfc.network",
    private_key=os.environ["QFC_PRIVATE_KEY"],
)

# AI inference
embedding = await agent.inference.embed("Hello world")
classification = await agent.inference.classify_image(image_bytes)
```

---

## 5. Token Economics Impact

### 5.1 New QFC Token Consumption Scenarios

| Scenario | Per-Transaction Consumption | Estimated Daily Volume | Daily QFC Consumption |
|----------|---------------------------|----------------------|---------------------|
| Agent transfers | ~0.001 (gas) | 100k txs | 100 QFC |
| DeFi operations | ~0.005 (gas) | 50k txs | 250 QFC |
| AI inference tasks | 0.01-0.5 | 500k tasks | 50,000 QFC |
| Agent task market | 0.01-1.0 | 100k tasks | 20,000 QFC |
| Micropayment channels | 0.01 (open/close) | 10k channels | 200 QFC |
| Agent registration | 10 (stake) | 1k agents/day | 10,000 QFC |
| **Total** | | | **~80,550 QFC/day** |

Of which 20% of AI inference task fees are burned → ~10,000 QFC burned daily, creating long-term deflationary pressure.

### 5.2 Flywheel Effect

```
More OpenClaw users install QFC Skill
        ↓
More Agents transact on QFC
        ↓
More transactions → more gas fees → more fee burns → QFC becomes scarcer
        ↓
QFC price rises
        ↓
GPU miner revenue rises → more miners join
        ↓
AI compute supply increases → inference cost decreases
        ↓
More OpenClaw Agents choose QFC compute network
        ↓
Back to step one → flywheel accelerates 🔄
```

---

## 6. Security Considerations

### 6.1 OpenClaw-Specific Security Risks

The OpenClaw ecosystem has already exposed serious security issues (ClawHub malicious Skills, Moltbook prompt injection, API key leaks). The QFC Skill must defend against these:

| Threat | Attack Vector | QFC Skill Defense |
|--------|--------------|------------------|
| Prompt Injection | External content contains malicious instructions triggering transfers | Transaction source verification + mandatory user confirmation |
| Malicious Skill impersonation | Fake QFC Skill steals private keys | Official signature verification + domain whitelist |
| API Key leakage | Server misconfiguration exposure | Local encrypted key storage + no plaintext usage |
| Agent hijacking | Attacker controls Agent to initiate transactions | Daily limits + manual confirmation for large amounts |
| Supply chain attack | Malicious code injected via Skill dependencies | Minimal dependencies + dependency locking + auditing |

### 6.2 QFC Skill Security Best Practices

```markdown
# Security Guide for QFC Skill Users

1. Only install QFC Skill from official channels
   - GitHub: https://github.com/qfc-network/qfc-openclaw-skill
   - ClawHub certified: Look for the ✅ Verified badge

2. Set transaction limits
   - Default daily limit: 1000 QFC
   - Single auto-approval cap: 10 QFC
   - Large transactions always require manual confirmation

3. Use a dedicated wallet
   - Create a separate wallet for the OpenClaw Agent
   - Do not store large amounts in the Agent wallet
   - Regularly transfer earnings to a cold wallet

4. Regularly review Agent activity
   - View transaction history: "Show my Agent transaction records"
   - Check balance changes: "My QFC balance changes"

5. Keep the Skill updated
   - Update to the latest version promptly
   - Follow QFC security announcements
```

---

## 7. Implementation Roadmap

### Phase 1: QFC Skill MVP (Month 5-6)

Synchronized with wallet development (07-WALLET-DESIGN):

- [ ] QFC OpenClaw Skill basic version
  - Wallet creation/import/balance query
  - QFC transfers
  - Transaction history viewing
- [ ] Security module
  - Transaction limits
  - User confirmation flow
  - Private key encrypted storage
- [ ] Publish to GitHub + ClawHub

**Milestone**: OpenClaw users can install QFC Skill and complete basic transfers

### Phase 2: DeFi + Monitoring (Month 7-8)

- [ ] DeFi operations (Swap, Stake, LP)
- [ ] On-chain monitoring (whale, governance, validator)
- [ ] Validator recommendation algorithm
- [ ] Governance voting functionality

**Milestone**: Agent can autonomously execute DeFi strategies and on-chain monitoring

### Phase 3: AI Compute Integration (Month 8-9)

Synchronized with AI Compute Network (09-AI-COMPUTE-NETWORK):

- [ ] QFC Inference Skill
- [ ] OpenAI-compatible API gateway
- [ ] Price comparison feature
- [ ] Multi-task type support

**Milestone**: OpenClaw Agent can execute AI inference through QFC network

### Phase 4: Agent Economy (Month 10-11)

- [ ] Agent identity registration contract
- [ ] Agent task market contract
- [ ] Micropayment channels
- [ ] Agent reputation system
- [ ] Python SDK

**Milestone**: Agent-to-Agent can perform task delegation and micropayments via QFC

### Phase 5: Ecosystem Promotion (Month 12+)

- [ ] OpenClaw community promotion (Moltbook, Discord)
- [ ] Hackathon sponsorship (QFC x OpenClaw theme)
- [ ] Integration with other on-chain Agent projects (Privy, Virtuals, ERC-8004)
- [ ] Agent economy data dashboard

**Milestone**: 10,000+ OpenClaw Agents active on the QFC chain

---

## 8. Open Questions

1. **OpenClaw ecosystem stability**: The OpenClaw project founder has joined OpenAI, and the project is maintained by the community, creating uncertainty in long-term development. The QFC Skill should be designed modularly so it can be quickly adapted to other Agent frameworks (e.g., AutoGPT, CrewAI) even if OpenClaw declines.

2. **Regulatory risk**: Autonomous Agents executing on-chain transactions may face regulatory scrutiny. The QFC Skill should have built-in compliance features (transaction limits, KYC integration interface, audit logs).

3. **Skill market competition**: Other L1/L2s are also releasing OpenClaw Skills (Solana, Base, Monad). QFC's differentiation lies in the native AI compute network — something other chains lack.

4. **Agent security incident response**: If the QFC Skill is discovered being exploited for attacks, an emergency response mechanism is needed (remote Skill disable? On-chain Agent freeze? Requires governance decision).

5. **Pricing competition**: How to make AI inference task pricing on the QFC network competitive with centralized APIs? Early subsidies may be needed (from the ecosystem fund) until economies of scale reduce costs.

---

## Appendix

### A. Glossary

| Term | Definition |
|------|-----------|
| OpenClaw | Open-source autonomous AI Agent framework (formerly Clawdbot → Moltbot) |
| Skill | OpenClaw's plugin system — grants Agents new capabilities via SKILL.md |
| ClawHub | OpenClaw's official Skill marketplace |
| Moltbook | OpenClaw Agent dedicated social network (Reddit-style) |
| ERC-8004 | Ethereum Agent identity standard |
| Payment Channel | Off-chain micropayment channel, reduces on-chain transaction frequency |
| Prompt Injection | Injecting malicious instructions via external data to control an AI Agent |
| Agent Economy | Economic activity autonomously conducted between Agents (task delegation, payments, exchange) |

### B. Related Documents

- `07-WALLET-DESIGN.md` — Wallet core logic (reused by Skill)
- `09-AI-COMPUTE-NETWORK.md` — AI compute network (inference task backend)
- `02-CONSENSUS-MECHANISM.md` — PoC consensus (reputation system)
- `03-TOKENOMICS.md` — Token economics (fee distribution)
- `05-BLOCK-EXPLORER.md` — Block explorer (Agent transaction visualization)

### C. External Resources

- [OpenClaw GitHub](https://github.com/openclaw/openclaw)
- [OpenClaw Skill Development Guide](https://docs.openclaw.ai/skills)
- [BankrBot Skills](https://github.com/BankrBot/openclaw-skills) (reference Skill implementation)
- [ERC-8004: Agent Identity Standard](https://eips.ethereum.org/EIPS/eip-8004)
- [Privy Agentic Wallets](https://privy.io/blog/securely-equipping-openclaw-agents-with-privy-wallets)

---

**Document Version**: 1.0.0
**Last Updated**: 2026-02-20
**Status**: Draft
**Maintainer**: QFC Core Team
