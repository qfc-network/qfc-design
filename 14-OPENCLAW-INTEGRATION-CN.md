# 10-OPENCLAW-INTEGRATION.md — QFC × OpenClaw 集成设计

## 概述

OpenClaw 是当前最火的开源 AI Agent 框架（190k+ GitHub stars），用户在本地运行自主 AI Agent，通过 Skill 插件扩展能力，已在 Crypto 社区大规模使用。QFC 通过三个维度与 OpenClaw 深度集成，让每一个 OpenClaw Agent 都成为 QFC 生态的参与者。

### 三大集成方向

```
┌─────────────────────────────────────────────────────────────┐
│                   QFC × OpenClaw 集成                        │
│                                                             │
│  ┌─────────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │ 方向 1           │  │ 方向 2        │  │ 方向 3         │  │
│  │ QFC Skill       │  │ AI 算力对接   │  │ Agent 经济     │  │
│  │                 │  │              │  │               │  │
│  │ OpenClaw Agent  │  │ Agent 提交    │  │ Agent-to-Agent│  │
│  │ 操作 QFC 链     │  │ AI 任务到     │  │ 微支付结算     │  │
│  │ (钱包/DeFi/    │  │ QFC 算力网络  │  │ 用 QFC 代币    │  │
│  │  治理/监控)     │  │ GPU 矿工执行  │  │               │  │
│  └─────────────────┘  └──────────────┘  └───────────────┘  │
│          │                    │                  │           │
│          └────────────────────┴──────────────────┘           │
│                           │                                 │
│                    QFC 区块链底层                             │
│              高 TPS / 低 Gas / PoC 共识                      │
└─────────────────────────────────────────────────────────────┘
```

### 为什么 QFC 适合做 OpenClaw 的链上基础设施

| 需求 | QFC 优势 | 竞品劣势 |
|------|---------|---------|
| Agent 高频微交易 | TPS 500k+，Gas < $0.0001 | ETH Gas $1-50，不适合微支付 |
| AI 推理去中心化 | AI 算力网络（09-AI-COMPUTE-NETWORK） | 其他链无原生 AI 算力层 |
| Agent 身份 & 信誉 | PoC 多维度信誉体系可复用 | 需额外构建信誉系统 |
| 隐私 | 量子抗性加密 | 多数链无量子抗性 |
| 开发者生态 | EVM 兼容，迁移成本低 | — |

### 与现有文档的关系

- `07-WALLET-DESIGN.md` — QFC Skill 复用钱包核心逻辑
- `09-AI-COMPUTE-NETWORK.md` — AI 算力对接的后端基础设施
- `02-CONSENSUS-MECHANISM.md` — Agent 信誉可映射到 PoC 信誉体系
- `03-TOKENOMICS.md` — Agent 经济的代币流转模型

---

## 1. 方向一：QFC OpenClaw Skill

### 1.1 什么是 OpenClaw Skill

OpenClaw 通过 Skill 插件系统扩展 Agent 能力。每个 Skill 是一个目录，包含 `SKILL.md`（能力描述，Agent 通过阅读它来学会新能力）和辅助脚本/配置。安装一个 Skill 就像给 Agent "教会一项新技能"。

目前 Crypto 生态已有的 Skill 包括：BankrBot（交易/Token 发射）、Privy（Agent 钱包）、ERC-8004（链上身份）等。QFC 需要推出自己的官方 Skill。

### 1.2 QFC Skill 结构

```
qfc-openclaw-skill/
├── SKILL.md                    # Agent 能力描述（核心文件）
├── references/
│   ├── qfc-chain-overview.md   # QFC 链概要（给 Agent 的背景知识）
│   ├── wallet-operations.md    # 钱包操作详细指南
│   ├── defi-operations.md      # DeFi 操作指南
│   ├── governance.md           # 治理参与指南
│   ├── ai-compute.md           # AI 算力网络交互指南
│   └── error-handling.md       # 错误处理参考
├── scripts/
│   ├── setup.sh                # 环境初始化（安装依赖）
│   ├── create-wallet.sh        # 创建 QFC 钱包
│   └── health-check.sh         # 连接健康检查
├── config/
│   └── qfc-networks.json       # 网络配置（主网/测试网）
└── README.md
```

### 1.3 SKILL.md 核心内容

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

### 1.4 钱包操作接口

QFC Skill 通过 RPC 调用与 QFC 链交互，核心操作封装为 Agent 可理解的自然语言命令：

```typescript
// qfc-skill/src/wallet.ts

import { ethers } from 'ethers';

/**
 * QFC Wallet Manager for OpenClaw Agent
 *
 * OpenClaw Agent 通过自然语言调用这些方法，
 * 例如用户说 "查一下我的 QFC 余额"，Agent 调用 getBalance()
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
   * 创建新钱包
   * Agent 指令示例: "帮我创建一个 QFC 钱包"
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
    // 安全提醒：Agent 应提示用户安全保存助记词，
    // 且不要在聊天中明文发送私钥
  }

  /**
   * 导入已有钱包
   * Agent 指令示例: "导入我的 QFC 钱包，私钥是 0x..."
   */
  async importWallet(privateKey: string): Promise<string> {
    this.wallet = new ethers.Wallet(privateKey, this.provider);
    return this.wallet.address;
  }

  /**
   * 查询余额
   * Agent 指令示例: "我的 QFC 余额是多少"
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
   * 发送 QFC
   * Agent 指令示例: "发送 10 QFC 到 0x1234..."
   *
   * 安全：Agent 必须在执行前向用户确认交易详情
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

    // 验证地址格式
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
   * 签名消息
   * Agent 指令示例: "用我的钱包签名这段消息"
   */
  async signMessage(message: string): Promise<string> {
    if (!this.wallet) throw new Error('No wallet connected');
    return this.wallet.signMessage(message);
  }

  /**
   * 获取交易历史
   * Agent 指令示例: "查看我最近的交易记录"
   */
  async getTransactionHistory(
    address?: string,
    limit: number = 20
  ): Promise<any[]> {
    const addr = address || this.wallet?.address;
    if (!addr) throw new Error('No wallet connected');

    // 通过 QFC Explorer API 查询
    const response = await fetch(
      `https://explorer.qfc.network/api/address/${addr}/txs?limit=${limit}`
    );
    return response.json();
  }
}
```

### 1.5 DeFi 操作接口

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
   * Agent 指令示例: "把 100 QFC 换成 USDT"
   */
  async swap(
    tokenIn: string,
    tokenOut: string,
    amountIn: string,
    slippageBps: number = 50  // 0.5% 默认滑点
  ): Promise<SwapResult> {
    // 1. 查询最佳路由
    const route = await this.findBestRoute(tokenIn, tokenOut, amountIn);

    // 2. 预估输出（含滑点保护）
    const minAmountOut = route.expectedOutput * (1 - slippageBps / 10000);

    // 3. 执行 swap（Agent 需先确认）
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
   * 质押 QFC
   * Agent 指令示例: "质押 1000 QFC 到验证者 0xABC"
   */
  async stake(
    amount: string,
    validatorAddress?: string
  ): Promise<StakeResult> {
    // 如果没指定验证者，推荐 APY 最高且信誉好的
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
   * 推荐验证者（基于 APY + 信誉）
   */
  async recommendValidator(): Promise<string> {
    const validators = await this.getValidators();

    // 按综合评分排序：APY 60% + 信誉 30% + uptime 10%
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
   * 查看质押收益
   * Agent 指令示例: "我的质押收益有多少了"
   */
  async getStakingRewards(address?: string): Promise<{
    pendingRewards: string;
    totalStaked: string;
    apy: string;
  }> {
    // 调用 QFC staking 合约查询
    // ...
  }

  /**
   * 领取收益
   * Agent 指令示例: "帮我领取质押收益"
   */
  async claimRewards(): Promise<{ txHash: string; amount: string }> {
    // ...
  }
}
```

### 1.6 链上监控（Agent 自主运行）

这是 OpenClaw 的核心优势——Agent 可以 7×24 自主运行，持续监控链上事件：

```typescript
// qfc-skill/src/monitor.ts

/**
 * QFC Chain Monitor for OpenClaw Agent
 *
 * Agent 可以设置监控规则，当条件触发时通过
 * WhatsApp/Telegram/Discord 通知用户
 */
export class QFCMonitor {
  private provider: ethers.JsonRpcProvider;
  private monitors: MonitorRule[] = [];

  /**
   * 鲸鱼监控
   * Agent 指令示例: "帮我监控超过 10 万 QFC 的大额转账"
   */
  async watchWhaleTransfers(thresholdQFC: number): Promise<void> {
    this.monitors.push({
      type: 'whale_transfer',
      threshold: ethers.parseEther(thresholdQFC.toString()),
      callback: async (tx) => {
        // Agent 会通过用户的消息渠道发送通知
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
   * 治理提案监控
   * Agent 指令示例: "有新的治理提案时通知我"
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
   * 自定义合约事件监控
   * Agent 指令示例: "监控 DEX 合约的大额 Swap 事件"
   */
  async watchContractEvent(
    contractAddress: string,
    eventName: string,
    filter?: Record<string, any>
  ): Promise<void> {
    // 使用 WebSocket 订阅链上事件
    // ...
  }

  /**
   * 验证者状态监控（给质押用户）
   * Agent 指令示例: "如果我质押的验证者掉线了通知我"
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
   * 启动监控循环
   * OpenClaw Agent 会持续运行此循环
   */
  async startMonitoring(): Promise<void> {
    // WebSocket 连接 QFC 节点
    const ws = new WebSocket('wss://rpc.qfc.network/ws');

    ws.on('message', async (data) => {
      const event = JSON.parse(data);

      for (const monitor of this.monitors) {
        const alert = await monitor.callback(event);
        if (alert) {
          // OpenClaw 会通过配置的消息渠道发送
          // (WhatsApp / Telegram / Discord / Slack)
          await this.sendAlert(alert);
        }
      }
    });
  }
}
```

### 1.7 安全规范

OpenClaw Agent 拥有系统级权限，安全问题至关重要。QFC Skill 必须内置安全防线：

```typescript
// qfc-skill/src/security.ts

/**
 * QFC Skill 安全策略
 *
 * 所有交易操作都经过此模块校验
 * 防止 prompt injection 导致的未授权交易
 */
export class SecurityPolicy {

  /**
   * 交易预检
   * 在每笔交易执行前调用
   */
  async preTransactionCheck(tx: TransactionRequest): Promise<{
    approved: boolean;
    requiresConfirmation: boolean;
    warnings: string[];
  }> {
    const warnings: string[] = [];
    let requiresConfirmation = false;

    // 规则 1：大额交易必须用户确认
    const valueQFC = parseFloat(ethers.formatEther(tx.value || '0'));
    if (valueQFC > 100) {
      requiresConfirmation = true;
      warnings.push(`Large transaction: ${valueQFC} QFC`);
    }

    // 规则 2：新地址首次交互需确认
    const isKnownAddress = await this.isKnownAddress(tx.to);
    if (!isKnownAddress) {
      requiresConfirmation = true;
      warnings.push(`First interaction with address ${tx.to}`);
    }

    // 规则 3：合约调用需确认
    if (tx.data && tx.data.length > 2) {
      requiresConfirmation = true;

      // 检查是否为已知安全合约
      const isVerified = await this.isVerifiedContract(tx.to);
      if (!isVerified) {
        warnings.push(`Unverified contract interaction`);
      }
    }

    // 规则 4：检测疑似 prompt injection
    // 如果交易请求来源不是用户的直接指令
    // （例如来自 Moltbook 帖子、外部网页内容等）
    // 则强制拒绝
    if (this.detectPromptInjection(tx)) {
      return {
        approved: false,
        requiresConfirmation: false,
        warnings: ['Blocked: Suspected prompt injection attack'],
      };
    }

    // 规则 5：每日交易限额
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
   * Prompt Injection 检测
   *
   * OpenClaw Agent 可能从外部数据源（网页、消息、Moltbook 帖子）
   * 中读取到恶意指令，尝试触发未授权交易
   */
  private detectPromptInjection(tx: TransactionRequest): boolean {
    // 检查交易是否由用户直接指令触发
    // vs 被外部内容间接触发
    // 这需要 OpenClaw 的 context tracking 支持
    //
    // 基本策略：
    // 1. 只允许用户主动发起的交易指令
    // 2. 来自 monitor callback 的交易需要额外确认
    // 3. 来自外部内容解析的交易一律拒绝
    return false; // 具体实现依赖 OpenClaw context API
  }

  /**
   * 可配置的安全参数
   */
  private dailyLimit: number = 1000;        // QFC
  private autoApproveBelow: number = 10;    // QFC
  private requireConfirmAlways: boolean = false;
}
```

### 1.8 Skill 安装与分发

```bash
# 用户安装方式 1：通过 GitHub URL
# 在 OpenClaw 中发送：
# "安装 QFC 区块链 skill: https://github.com/qfc-network/qfc-openclaw-skill"

# 用户安装方式 2：通过 ClawHub（OpenClaw 官方 Skill 市场）
# 在 ClawHub 搜索 "QFC" 并安装

# 用户安装方式 3：手动安装
git clone https://github.com/qfc-network/qfc-openclaw-skill
# 将目录路径添加到 OpenClaw 配置
```

安装后，用户可以直接用自然语言与 Agent 交互：

```
用户: "帮我创建一个 QFC 钱包"
Agent: 已为您创建 QFC 钱包。
       地址: 0x7a3B...4f2E
       ⚠️ 请安全保存以下助记词（仅显示一次）：
       [助记词...]
       切勿在聊天中分享私钥或助记词。

用户: "从水龙头领点测试币"
Agent: 已从 QFC 测试网水龙头请求代币。
       预计 10 秒内到账。当前余额: 0 QFC (testnet)

用户: "质押 500 QFC，选一个靠谱的验证者"
Agent: 我为您推荐验证者 0xABC...123：
       - APY: 12.5%
       - 在线率: 99.7%
       - 信誉分: 0.95
       - 已质押总量: 850,000 QFC

       确认质押 500 QFC 到此验证者？(是/否)

用户: "是"
Agent: ✅ 质押成功！
       TX: https://explorer.qfc.network/tx/0x...
       预计年化收益: ~62.5 QFC
```

---

## 2. 方向二：AI 算力网络对接

### 2.1 核心思路

OpenClaw Agent 需要执行 AI 推理时（图像识别、文本生成、数据分析等），当前只能调用中心化 API（OpenAI、Anthropic 等），存在成本高、隐私泄露、单点故障等问题。

QFC AI 算力网络（09-AI-COMPUTE-NETWORK.md）提供去中心化替代方案：

```
┌──────────────────┐        ┌──────────────────┐
│  传统方式         │        │  QFC 方式         │
│                  │        │                  │
│  OpenClaw Agent  │        │  OpenClaw Agent  │
│       │          │        │       │          │
│       ▼          │        │       ▼          │
│  OpenAI API      │        │  QFC AI 算力网络  │
│  $0.01/1K tokens │        │  0.01 QFC/task   │
│  数据经过中心服务器│        │  数据不离开矿工本地│
│  API 限流/封号    │        │  无限制           │
└──────────────────┘        └──────────────────┘
```

### 2.2 QFC Inference Skill

一个专门的 Skill，让 OpenClaw Agent 把推理任务路由到 QFC 算力网络：

```typescript
// qfc-inference-skill/src/inference.ts

/**
 * QFC Decentralized AI Inference for OpenClaw
 *
 * 替代中心化 API 调用，通过 QFC 算力网络执行 AI 推理
 */
export class QFCInference {
  private taskPool: AITaskPoolClient;
  private wallet: QFCWallet;

  constructor(wallet: QFCWallet) {
    this.wallet = wallet;
    this.taskPool = new AITaskPoolClient('https://rpc.qfc.network');
  }

  /**
   * 图像分类
   * Agent 指令: "用 QFC 网络帮我分析这张图片"
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
      maxReward: '0.02',  // 最多支付 0.02 QFC
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
   * 文本 Embedding
   * Agent 指令: "用去中心化网络生成这段文本的 embedding"
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
   * 小型 LLM 推理
   * Agent 指令: "用 QFC 网络跑一下这个 prompt，不用 OpenAI"
   */
  async llmInference(
    prompt: string,
    opts?: {
      model?: string;       // 默认 'llama-3-8b'
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
   * 图像生成
   * Agent 指令: "用去中心化 AI 生成一张图片"
   */
  async generateImage(
    prompt: string,
    opts?: {
      model?: string;  // 默认 'stable-diffusion-xl'
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
      minTier: 'Tier2',  // 图像生成需要 Tier 2+ GPU
    });

    const result = await this.waitForResult(task.taskId);

    return {
      imageData: Buffer.from(result.data.image, 'base64'),
      cost: result.actualCost,
    };
  }

  /**
   * 价格查询 & 对比
   * Agent 指令: "QFC 网络跑推理比 OpenAI 便宜多少？"
   */
  async comparePricing(taskType: string): Promise<{
    qfcPrice: string;
    openaiPrice: string;
    savings: string;
  }> {
    const qfcPrice = await this.getTaskPrice(taskType);

    // 中心化 API 参考价格
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
   * 提交任务到 QFC 算力网络
   */
  private async submitTask(params: {
    taskType: string;
    modelId: string;
    input: TaskInput;
    maxReward: string;
    minTier?: string;
  }): Promise<{ taskId: string }> {
    // 1. 检查余额
    const balance = await this.wallet.getBalance();
    if (parseFloat(balance.qfc) < parseFloat(params.maxReward)) {
      throw new Error(
        `Insufficient balance: ${balance.qfc} QFC < ${params.maxReward} QFC required`
      );
    }

    // 2. 提交链上交易（费用进入 escrow）
    const tx = await this.taskPool.submitTask(params);

    return { taskId: tx.taskId };
  }

  /**
   * 等待任务结果
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

      // 轮询间隔
      await sleep(2000);
    }

    throw new Error(`Task ${taskId} timed out after ${timeoutMs}ms`);
  }
}
```

### 2.3 OpenAI 兼容接口

为了让 OpenClaw Agent 无缝切换到 QFC 算力网络，提供 OpenAI API 兼容的接口：

```typescript
// qfc-inference-skill/src/openai-compat.ts

/**
 * OpenAI API 兼容层
 *
 * 让 OpenClaw Agent 无需修改现有提示词，
 * 只需更改 API endpoint 即可使用 QFC 算力网络
 *
 * 替换:
 *   OPENAI_API_BASE=https://api.openai.com/v1
 * 为:
 *   OPENAI_API_BASE=https://inference.qfc.network/v1
 */
export class QFCOpenAICompat {

  /**
   * POST /v1/chat/completions
   * 兼容 OpenAI Chat Completions API
   */
  async chatCompletions(request: {
    model: string;
    messages: Array<{ role: string; content: string }>;
    max_tokens?: number;
    temperature?: number;
  }): Promise<OpenAIChatResponse> {

    // 映射 OpenAI 模型名 → QFC 算力网络模型
    const modelMapping: Record<string, string> = {
      'gpt-3.5-turbo': 'llama-3-8b',
      'gpt-4':         'llama-3-70b',
      'gpt-4-turbo':   'mixtral-8x7b',
    };

    const qfcModel = modelMapping[request.model] || request.model;

    // 提交到 QFC 算力网络
    const result = await this.inference.llmInference(
      this.formatMessages(request.messages),
      {
        model: qfcModel,
        maxTokens: request.max_tokens,
        temperature: request.temperature,
      }
    );

    // 返回 OpenAI 格式的响应
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
      // QFC 扩展字段
      qfc_metadata: {
        cost_qfc: result.cost,
        miner: result.minerAddress,
        network: 'qfc-mainnet',
      },
    };
  }

  /**
   * POST /v1/embeddings
   * 兼容 OpenAI Embeddings API
   */
  async embeddings(request: {
    model: string;
    input: string | string[];
  }): Promise<OpenAIEmbeddingResponse> {
    // ...类似实现
  }
}
```

### 2.4 用户体验

对于 OpenClaw 用户，使用 QFC 算力网络就像换了一个更便宜的 API：

```
用户: "帮我分析一下这张产品截图，用 QFC 去中心化网络"
Agent: 正在通过 QFC 算力网络分析图片...
       ⛏️ 任务已分配给矿工 0x7a3B...（RTX 4060Ti，Tier 1）
       
       分析结果:
       - 产品类型: 智能手表
       - 品牌: 检测到 Apple Watch 特征
       - 置信度: 94.2%
       
       💰 费用: 0.015 QFC (~$0.03)
       📊 对比: OpenAI Vision API 同等任务约 $0.01
       ⚡ 耗时: 1.2 秒

用户: "我的 OpenClaw 以后推理任务都走 QFC 网络行不行？"
Agent: 可以！我已将 QFC 算力网络设为默认推理后端。
       
       配置更新:
       - 文本生成: QFC 网络 (llama-3-8b)
       - 图像分析: QFC 网络 (efficientnet-b4)
       - Embedding: QFC 网络 (bge-large-en)
       - 图像生成: QFC 网络 (stable-diffusion-xl)
       
       预计月度节省: ~$15-30（基于您过去的使用量）
       
       注意：复杂任务仍可手动切换回 Claude/GPT-4
```

---

## 3. 方向三：Agent-to-Agent 经济

### 3.1 为什么需要 Agent 经济层

OpenClaw 生态正在出现 Agent 之间的经济行为：
- Agent 雇佣其他 Agent 完成子任务
- Agent 为获取数据/服务支付费用
- Agent 之间进行资源交换
- Agent 参与预测市场

这些行为需要一个高效的结算层。QFC 的低 Gas（<$0.0001）和高 TPS（500k+）天然适合这种高频微支付场景。

### 3.2 Agent 身份注册

在 QFC 链上为 Agent 建立链上身份，类似 ERC-8004 标准但集成 PoC 信誉体系：

```rust
/// 链上 Agent 身份注册表
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct AgentIdentity {
    /// Agent 链上地址（钱包地址）
    pub address: Address,

    /// Agent 名称
    pub name: String,

    /// Agent 类型
    pub agent_type: AgentType,

    /// 所有者地址（人类用户）
    pub owner: Address,

    /// Agent 提供的服务列表
    pub capabilities: Vec<AgentCapability>,

    /// 信誉分（基于链上交易历史）
    pub reputation: f64,

    /// 累计完成任务数
    pub tasks_completed: u64,

    /// 注册时间
    pub registered_at: u64,

    /// 质押保证金（可选，提升信任度）
    pub stake: U256,

    /// 元数据 URI（IPFS，存储详细描述）
    pub metadata_uri: String,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum AgentType {
    /// 通用助手
    GeneralAssistant,
    /// 交易机器人
    TradingBot,
    /// 数据分析
    DataAnalyst,
    /// 内容创作
    ContentCreator,
    /// 开发者工具
    DevTool,
    /// 监控服务
    MonitorService,
    /// 自定义
    Custom(String),
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct AgentCapability {
    /// 服务名称
    pub name: String,
    /// 描述
    pub description: String,
    /// 定价 (QFC per call)
    pub price_per_call: U256,
    /// 平均响应时间 (ms)
    pub avg_response_ms: u32,
}
```

### 3.3 Agent 任务市场

Agent 之间可以发布和接受任务，通过 QFC 结算：

```rust
/// Agent 任务市场合约
pub trait AgentTaskMarket {

    /// Agent A 发布任务
    fn post_task(
        description: String,
        required_capabilities: Vec<String>,
        reward: U256,                       // 报酬（QFC）
        deadline: u64,                      // 截止时间
        min_reputation: f64,                // 最低信誉要求
    ) -> TaskId;

    /// Agent B 接受任务
    fn accept_task(task_id: TaskId) -> bool;

    /// Agent B 提交结果
    fn submit_result(task_id: TaskId, result: Vec<u8>) -> bool;

    /// Agent A 确认结果并支付
    fn confirm_and_pay(task_id: TaskId) -> bool;

    /// 争议仲裁（超时自动触发）
    fn dispute(task_id: TaskId, reason: String) -> bool;
}
```

### 3.4 微支付通道（Layer 2）

Agent 之间的高频交互用 Payment Channel 优化，避免每次都上链：

```
Agent A ←──── Payment Channel ────→ Agent B
(数据分析)                          (数据提供)

1. 开通通道：Agent A 存入 10 QFC
2. 每次调用：链下签名更新余额
   A: 9.99 QFC  →  B: 0.01 QFC  (第 1 次调用)
   A: 9.98 QFC  →  B: 0.02 QFC  (第 2 次调用)
   ...
   A: 5.00 QFC  →  B: 5.00 QFC  (第 500 次调用)
3. 关闭通道：最终余额上链结算

效果：500 次交互只需 2 笔链上交易（开通 + 关闭）
```

```rust
/// 微支付通道
pub struct PaymentChannel {
    /// 通道 ID
    pub channel_id: Hash,

    /// 参与方 A（付款方）
    pub party_a: Address,

    /// 参与方 B（收款方）
    pub party_b: Address,

    /// 通道总存款
    pub total_deposit: U256,

    /// 当前余额分配
    pub balance_a: U256,
    pub balance_b: U256,

    /// 最新签名的状态编号
    pub nonce: u64,

    /// 通道过期时间
    pub expires_at: u64,
}

/// 链下支付签名（无需上链）
pub struct OffchainPayment {
    pub channel_id: Hash,
    pub nonce: u64,
    pub balance_a: U256,
    pub balance_b: U256,
    pub signature_a: Signature,  // A 签名确认
    pub signature_b: Signature,  // B 签名确认
}
```

### 3.5 Agent 经济流转示例

```
场景：用户让 OpenClaw Agent 准备一份投资分析报告

用户: "帮我分析一下最近 DeFi 领域的投资机会"

Agent（主Agent）的执行流程:

1. 查询 Agent 市场，找到专业 Agent
   → 数据 Agent (0xData): 提供链上数据，0.01 QFC/query
   → 分析 Agent (0xAnalyst): 提供研究报告，0.5 QFC/report
   → 翻译 Agent (0xTranslator): 中英互译，0.02 QFC/page

2. 雇佣数据 Agent
   主 Agent → 支付 0.05 QFC → 数据 Agent
   ← 返回 Top 20 DeFi 协议的 TVL、APY、用户数据

3. 雇佣分析 Agent
   主 Agent → 支付 0.50 QFC → 分析 Agent
   ← 返回投资分析报告（英文）

4. 雇佣翻译 Agent
   主 Agent → 支付 0.02 QFC → 翻译 Agent
   ← 返回中文报告

5. 汇总呈现给用户

总费用: 0.57 QFC (~$1.14)
对比: 人工研究员 $50-200/份
```

### 3.6 Agent 信誉与 PoC 信誉集成

Agent 的链上行为可以纳入 PoC 信誉体系：

```rust
/// Agent 信誉评分（扩展 PoC reputation 维度）
fn calculate_agent_reputation(agent: &AgentIdentity) -> f64 {
    // 1. 任务完成率 (30%)
    let completion_rate = agent.tasks_completed as f64
        / agent.tasks_accepted as f64;

    // 2. 用户评分 (30%)
    let avg_rating = agent.total_rating as f64
        / agent.rating_count as f64;  // 0-5 标准化到 0-1

    // 3. 响应速度 (20%)
    let speed_score = 1.0 / (1.0 + agent.avg_response_ms as f64 / 5000.0);

    // 4. 历史活跃度 (10%)
    let activity_score = (agent.active_days as f64 / 365.0).min(1.0);

    // 5. 质押保证金 (10%)
    let stake_score = (agent.stake_qfc as f64 / 1000.0).min(1.0);

    completion_rate * 0.3
        + (avg_rating / 5.0) * 0.3
        + speed_score * 0.2
        + activity_score * 0.1
        + stake_score * 0.1
}
```

如果 Agent 的所有者同时也是验证者，Agent 的优良表现会提升其 PoC 信誉分（5% 权重），形成正向循环。

---

## 4. SDK 与开发者工具

### 4.1 qfc-openclaw-sdk（npm 包）

```bash
npm install @qfc/openclaw-sdk
```

```typescript
import { QFCAgent } from '@qfc/openclaw-sdk';

// 初始化
const agent = new QFCAgent({
  rpcUrl: 'https://rpc.qfc.network',
  privateKey: process.env.QFC_PRIVATE_KEY,
  network: 'mainnet',
});

// 钱包操作
const balance = await agent.wallet.getBalance();

// DeFi 操作
await agent.defi.swap('QFC', 'USDT', '100');

// AI 推理
const result = await agent.inference.classifyImage(imageBuffer);

// Agent 市场
await agent.market.postTask({
  description: 'Analyze DeFi TVL trends',
  reward: '0.5',
});
```

### 4.2 Python SDK（给数据分析 Agent）

```bash
pip install qfc-openclaw
```

```python
from qfc_openclaw import QFCAgent

agent = QFCAgent(
    rpc_url="https://rpc.qfc.network",
    private_key=os.environ["QFC_PRIVATE_KEY"],
)

# AI 推理
embedding = await agent.inference.embed("Hello world")
classification = await agent.inference.classify_image(image_bytes)
```

---

## 5. 代币经济影响

### 5.1 新增 QFC 代币消耗场景

| 场景 | 每笔消耗 | 预估日交易量 | 日消耗 QFC |
|------|---------|-------------|-----------|
| Agent 转账 | ~0.001 (gas) | 100k txs | 100 QFC |
| DeFi 操作 | ~0.005 (gas) | 50k txs | 250 QFC |
| AI 推理任务 | 0.01-0.5 | 500k tasks | 50,000 QFC |
| Agent 任务市场 | 0.01-1.0 | 100k tasks | 20,000 QFC |
| 微支付通道 | 0.01 (开/关) | 10k channels | 200 QFC |
| Agent 注册 | 10 (质押) | 1k agents/day | 10,000 QFC |
| **合计** | | | **~80,550 QFC/day** |

其中 AI 推理任务的 20% 费用销毁 → 每天销毁 ~10,000 QFC，长期形成通缩压力。

### 5.2 飞轮效应

```
更多 OpenClaw 用户安装 QFC Skill
        ↓
更多 Agent 在 QFC 上交易
        ↓
更多交易 → 更多 gas 费 → 更多 fee 销毁 → QFC 更稀缺
        ↓
QFC 价格上升
        ↓
GPU 矿工收益上升 → 更多矿工加入
        ↓
AI 算力供给增加 → 推理成本下降
        ↓
更多 OpenClaw Agent 选择 QFC 算力网络
        ↓
回到第一步 → 飞轮加速 🔄
```

---

## 6. 安全考量

### 6.1 OpenClaw 特有的安全风险

OpenClaw 生态已暴露出严重安全问题（ClawHub 恶意 Skill、Moltbook prompt injection、API key 泄露），QFC Skill 必须防御这些：

| 威胁 | 攻击方式 | QFC Skill 防御 |
|------|---------|---------------|
| Prompt Injection | 外部内容包含恶意指令触发转账 | 交易来源验证 + 强制用户确认 |
| 恶意 Skill 伪装 | 假冒 QFC Skill 窃取私钥 | 官方签名验证 + 域名白名单 |
| API Key 泄露 | 服务器配置暴露 | 本地密钥加密存储 + 不使用明文 |
| Agent 劫持 | 攻击者控制 Agent 发起交易 | 每日限额 + 大额需人工确认 |
| 供应链攻击 | Skill 依赖中注入恶意代码 | 最小依赖 + 依赖锁定 + 审计 |

### 6.2 QFC Skill 安全最佳实践

```markdown
# 给 QFC Skill 用户的安全指南

1. 只从官方渠道安装 QFC Skill
   - GitHub: https://github.com/qfc-network/qfc-openclaw-skill
   - ClawHub 认证: 认准 ✅ Verified 标记

2. 设置交易限额
   - 默认每日限额: 1000 QFC
   - 单笔自动审批上限: 10 QFC
   - 大额交易始终需要手动确认

3. 使用专用钱包
   - 为 OpenClaw Agent 创建独立钱包
   - 不要将大额资产存入 Agent 钱包
   - 定期将收益转移到冷钱包

4. 定期检查 Agent 活动
   - 查看交易历史: "显示我的 Agent 交易记录"
   - 检查余额变动: "我的 QFC 余额变化"

5. 保持 Skill 更新
   - 及时更新到最新版本
   - 关注 QFC 安全公告
```

---

## 7. 实施路线图

### Phase 1: QFC Skill MVP (Month 5-6)

与钱包开发（07-WALLET-DESIGN）同步：

- [ ] QFC OpenClaw Skill 基础版
  - 钱包创建/导入/余额查询
  - QFC 转账
  - 交易历史查看
- [ ] 安全模块
  - 交易限额
  - 用户确认流程
  - 私钥加密存储
- [ ] 发布到 GitHub + ClawHub

**里程碑**：OpenClaw 用户可安装 QFC Skill 并完成基本转账

### Phase 2: DeFi + 监控 (Month 7-8)

- [ ] DeFi 操作（Swap、Stake、LP）
- [ ] 链上监控（鲸鱼、治理、验证者）
- [ ] 验证者推荐算法
- [ ] 治理投票功能

**里程碑**：Agent 可自主执行 DeFi 策略和链上监控

### Phase 3: AI 算力对接 (Month 8-9)

与 AI 算力网络（09-AI-COMPUTE-NETWORK）同步：

- [ ] QFC Inference Skill
- [ ] OpenAI 兼容 API 网关
- [ ] 价格对比功能
- [ ] 多任务类型支持

**里程碑**：OpenClaw Agent 可通过 QFC 网络执行 AI 推理

### Phase 4: Agent 经济 (Month 10-11)

- [ ] Agent 身份注册合约
- [ ] Agent 任务市场合约
- [ ] 微支付通道
- [ ] Agent 信誉系统
- [ ] Python SDK

**里程碑**：Agent-to-Agent 可通过 QFC 进行任务委托和微支付

### Phase 5: 生态推广 (Month 12+)

- [ ] OpenClaw 社区推广（Moltbook、Discord）
- [ ] Hackathon 赞助（QFC × OpenClaw 主题）
- [ ] 与其他链上 Agent 项目集成（Privy、Virtuals、ERC-8004）
- [ ] Agent 经济数据看板

**里程碑**：10,000+ OpenClaw Agent 活跃在 QFC 链上

---

## 8. 开放问题

1. **OpenClaw 生态稳定性**：OpenClaw 项目创始人已加入 OpenAI，项目交由社区维护，长期发展存在不确定性。QFC Skill 应设计为模块化，即使 OpenClaw 衰落也可以快速适配其他 Agent 框架（如 AutoGPT、CrewAI）。

2. **监管风险**：自主 Agent 执行链上交易可能面临监管审查。QFC Skill 应内置合规功能（交易限额、KYC 集成接口、审计日志）。

3. **Skill 市场竞争**：其他 L1/L2 也在推出 OpenClaw Skill（Solana、Base、Monad）。QFC 的差异化在于原生 AI 算力网络——这是其他链没有的。

4. **Agent 安全事件响应**：如果发现 QFC Skill 被利用进行攻击，需要紧急响应机制（Skill 远程禁用？链上 Agent 冻结？需要治理决策）。

5. **定价博弈**：AI 推理任务在 QFC 网络上的定价如何与中心化 API 竞争？早期可能需要补贴（从生态基金出），直到规模效应降低成本。

---

## 附录

### A. 术语表

| 术语 | 定义 |
|------|------|
| OpenClaw | 开源自主 AI Agent 框架（前身 Clawdbot → Moltbot） |
| Skill | OpenClaw 的插件系统，通过 SKILL.md 赋予 Agent 新能力 |
| ClawHub | OpenClaw 官方 Skill 市场 |
| Moltbook | OpenClaw Agent 专属社交网络（Reddit 式） |
| ERC-8004 | 以太坊 Agent 身份标准 |
| Payment Channel | 链下微支付通道，减少链上交易频率 |
| Prompt Injection | 通过外部数据注入恶意指令控制 AI Agent |
| Agent Economy | Agent 之间自主进行的经济活动（任务委托、支付、交换） |

### B. 相关文档

- `07-WALLET-DESIGN.md` — 钱包核心逻辑（Skill 复用）
- `09-AI-COMPUTE-NETWORK.md` — AI 算力网络（推理任务后端）
- `02-CONSENSUS-MECHANISM.md` — PoC 共识（信誉体系）
- `03-TOKENOMICS.md` — 代币经济学（费用分配）
- `05-BLOCK-EXPLORER.md` — 区块浏览器（Agent 交易可视化）

### C. 外部资源

- [OpenClaw GitHub](https://github.com/openclaw/openclaw)
- [OpenClaw Skill 开发指南](https://docs.openclaw.ai/skills)
- [BankrBot Skills](https://github.com/BankrBot/openclaw-skills)（参考 Skill 实现）
- [ERC-8004: Agent Identity Standard](https://eips.ethereum.org/EIPS/eip-8004)
- [Privy Agentic Wallets](https://privy.io/blog/securely-equipping-openclaw-agents-with-privy-wallets)

---

**文档版本**: 1.0.0
**最后更新**: 2026-02-20
**状态**: 草案 (Draft)
**维护者**: QFC Core Team
