# ElizaOS Plugin

> Last Updated: 2026-03-11 | Version 1.0
> GitHub Issue: #22
> Author: Alex Wei, Product Manager @ QFC Network

---

## 1. Executive Summary

`@qfc/elizaos-plugin` is an npm package that enables ElizaOS AI agents to use QFC's native AI inference network. It wraps `@qfc/sdk-js` and exposes ElizaOS-native actions, providers, and evaluators.

**Key capability**: ElizaOS agents can call `RUN_INFERENCE` to submit inference tasks to QFC's decentralized miner network — with verified results, capability-gated access, and automatic budget management.

**Depends on**: #18 (Cross-chain oracle for multi-chain agents), #19 (Agent capability resources for budget management)

---

## 2. ElizaOS Plugin Architecture

ElizaOS v2 uses a modular plugin system:

```
ElizaOS Runtime
├── Core (memory, planning, LLM routing)
├── Plugins (extend capabilities)
│   ├── Plugin = { name, actions, providers, evaluators }
│   ├── Action = handles a specific user intent
│   ├── Provider = injects context into LLM prompts
│   └── Evaluator = post-processes agent responses
└── Clients (Discord, Telegram, Twitter, etc.)
```

Each plugin is an npm package that exports a `Plugin` object. The runtime loads plugins at startup and routes messages to matching actions.

---

## 3. Package Structure

```
@qfc/elizaos-plugin/
├── package.json
├── tsconfig.json
├── src/
│   ├── index.ts                 # Plugin export
│   ├── plugin.ts                # Plugin definition
│   ├── actions/
│   │   ├── runInference.ts      # RUN_INFERENCE action
│   │   ├── checkCapability.ts   # CHECK_CAPABILITY action
│   │   ├── registerAgent.ts     # REGISTER_AGENT action
│   │   └── queryAgents.ts       # QUERY_AGENTS action
│   ├── providers/
│   │   ├── balanceProvider.ts   # QFC balance context
│   │   └── capabilityProvider.ts # Capability status context
│   ├── evaluators/
│   │   └── inferenceQuality.ts  # Result quality evaluator
│   ├── client/
│   │   └── qfcClient.ts        # QFC SDK wrapper for ElizaOS
│   └── types.ts                 # Shared types
├── tests/
│   ├── actions/
│   ├── providers/
│   └── integration/
└── examples/
    ├── sentiment-trader/
    ├── content-generator/
    └── ai-oracle/
```

---

## 4. Plugin Interface Implementation

### 4.1 Plugin Definition

```typescript
// src/plugin.ts
import { Plugin } from '@elizaos/core';
import { runInferenceAction } from './actions/runInference';
import { checkCapabilityAction } from './actions/checkCapability';
import { registerAgentAction } from './actions/registerAgent';
import { queryAgentsAction } from './actions/queryAgents';
import { balanceProvider } from './providers/balanceProvider';
import { capabilityProvider } from './providers/capabilityProvider';
import { inferenceQualityEvaluator } from './evaluators/inferenceQuality';

export const qfcPlugin: Plugin = {
    name: 'qfc-inference',
    description: 'QFC Network AI inference plugin — run verified inference on-chain',
    version: '1.0.0',

    actions: [
        runInferenceAction,
        checkCapabilityAction,
        registerAgentAction,
        queryAgentsAction,
    ],

    providers: [
        balanceProvider,
        capabilityProvider,
    ],

    evaluators: [
        inferenceQualityEvaluator,
    ],
};

export default qfcPlugin;
```

### 4.2 RUN_INFERENCE Action

```typescript
// src/actions/runInference.ts
import { Action, ActionContext, ActionResult } from '@elizaos/core';
import { QFCPluginClient } from '../client/qfcClient';

export const runInferenceAction: Action = {
    name: 'RUN_INFERENCE',
    description: 'Run AI inference on the QFC decentralized network with verified results',

    // When should this action trigger?
    similes: [
        'run inference',
        'analyze with AI',
        'classify this',
        'generate text',
        'embed this text',
        'run AI task',
        'use QFC inference',
    ],

    // Validate that we can run this action
    validate: async (runtime, message): Promise<boolean> => {
        const client = QFCPluginClient.getInstance(runtime);
        const cap = await client.getActiveCapability();
        return cap !== null && cap.remainingBudget > 0;
    },

    // Execute the inference
    handler: async (runtime, message, state, options): Promise<ActionResult> => {
        const client = QFCPluginClient.getInstance(runtime);

        // Determine model based on task type
        const taskType = options?.taskType || 'text-generation';
        const model = options?.model || client.getDefaultModel(taskType);

        try {
            const result = await client.submitInference({
                model,
                prompt: message.content,
                maxTokens: options?.maxTokens || 500,
                temperature: options?.temperature || 0.7,
            });

            return {
                success: true,
                data: {
                    output: result.output,
                    model: result.model,
                    taskId: result.taskId,
                    verificationTier: result.verificationTier,
                    fee: result.fee,
                },
                message: result.output,
            };
        } catch (error) {
            // Auto-refill capability if budget exhausted
            if (error.code === 'INSUFFICIENT_BUDGET') {
                await client.autoRefillCapability();
                // Retry once
                const result = await client.submitInference({
                    model,
                    prompt: message.content,
                    maxTokens: options?.maxTokens || 500,
                });
                return { success: true, data: result, message: result.output };
            }
            throw error;
        }
    },

    // Example interactions for few-shot prompting
    examples: [
        [
            { user: 'user', content: 'Analyze the sentiment of this tweet: "QFC is the future of AI"' },
            { user: 'assistant', content: 'Running inference on QFC network...\n\nSentiment: Positive (0.92 confidence)\nThe text expresses strong optimism about QFC technology.' },
        ],
    ],
};
```

### 4.3 CHECK_CAPABILITY Action

```typescript
// src/actions/checkCapability.ts
export const checkCapabilityAction: Action = {
    name: 'CHECK_CAPABILITY',
    description: 'Check your QFC inference capability status (budget, allowed models, expiry)',

    similes: ['check capability', 'check budget', 'inference status', 'how much budget'],

    handler: async (runtime, message): Promise<ActionResult> => {
        const client = QFCPluginClient.getInstance(runtime);
        const cap = await client.getActiveCapability();

        if (!cap) {
            return {
                success: true,
                message: 'No active inference capability. Use REGISTER_AGENT to create one.',
            };
        }

        return {
            success: true,
            message: `Inference Capability Status:
- Remaining Budget: ${cap.remainingBudget} QFC
- Allowed Models: ${cap.allowedModels.join(', ')}
- Expires: ${cap.expiresAt ? new Date(cap.expiresAt * 1000).toISOString() : 'Never'}
- Total Spent: ${cap.totalSpent} QFC
- Total Tasks: ${cap.totalTasks}`,
        };
    },
};
```

### 4.4 REGISTER_AGENT Action

```typescript
// src/actions/registerAgent.ts
export const registerAgentAction: Action = {
    name: 'REGISTER_AGENT',
    description: 'Register this AI agent on the QFC network with stake and capabilities',

    similes: ['register agent', 'create agent', 'sign up on QFC'],

    handler: async (runtime, message, state, options): Promise<ActionResult> => {
        const client = QFCPluginClient.getInstance(runtime);

        const result = await client.registerAgent({
            capabilities: options?.capabilities || ['text-generation'],
            stake: options?.stake || '100',  // 100 QFC minimum
            endpoint: options?.endpoint || runtime.getSetting('QFC_AGENT_ENDPOINT') || '',
        });

        // Auto-create inference capability
        await client.createCapability({
            budget: options?.budget || '50',  // 50 QFC initial budget
            allowedModels: ['qfc-llm-7b', 'qfc-embed-small', 'qfc-classify-small'],
            ttlDays: 30,
        });

        return {
            success: true,
            message: `Agent registered on QFC network!
- Agent ID: ${result.agentId}
- Stake: ${result.stake} QFC
- Inference capability created with 50 QFC budget`,
        };
    },
};
```

### 4.5 QUERY_AGENTS Action

```typescript
// src/actions/queryAgents.ts
export const queryAgentsAction: Action = {
    name: 'QUERY_AGENTS',
    description: 'Query available AI agents on the QFC network by capability',

    similes: ['find agents', 'list agents', 'search agents', 'available agents'],

    handler: async (runtime, message, state, options): Promise<ActionResult> => {
        const client = QFCPluginClient.getInstance(runtime);
        const capability = options?.capability || 'text-generation';

        const agents = await client.queryAgents({
            capability,
            minReputation: options?.minReputation || 5000,
            limit: options?.limit || 10,
        });

        const agentList = agents.map(a =>
            `- ${a.agentId} | Rep: ${a.reputationScore/100}% | Tasks: ${a.totalTasksCompleted} | Stake: ${a.stake} QFC`
        ).join('\n');

        return {
            success: true,
            message: `Found ${agents.length} agents with "${capability}" capability:\n${agentList}`,
        };
    },
};
```

---

## 5. QFC Client Wrapper

```typescript
// src/client/qfcClient.ts
import { QFCClient } from '@qfc/sdk-js';
import { IAgentRuntime } from '@elizaos/core';

export class QFCPluginClient {
    private static instances = new Map<string, QFCPluginClient>();
    private client: QFCClient;
    private capabilityId: string | null = null;
    private agentId: string | null = null;

    private constructor(runtime: IAgentRuntime) {
        this.client = new QFCClient({
            rpcUrl: runtime.getSetting('QFC_RPC_URL') || 'https://rpc.testnet.qfc.network',
            privateKey: runtime.getSetting('QFC_PRIVATE_KEY'),
            chainId: parseInt(runtime.getSetting('QFC_CHAIN_ID') || '9000'),
        });
    }

    static getInstance(runtime: IAgentRuntime): QFCPluginClient {
        const key = runtime.agentId;
        if (!this.instances.has(key)) {
            this.instances.set(key, new QFCPluginClient(runtime));
        }
        return this.instances.get(key)!;
    }

    async submitInference(params: {
        model: string;
        prompt: string;
        maxTokens?: number;
        temperature?: number;
    }): Promise<InferenceResult> {
        return this.client.inference.submit({
            ...params,
            capabilityId: this.capabilityId,
        });
    }

    async getActiveCapability(): Promise<InferenceCapability | null> {
        if (!this.capabilityId) return null;
        return this.client.capabilities.get(this.capabilityId);
    }

    async createCapability(params: {
        budget: string;
        allowedModels: string[];
        ttlDays: number;
    }): Promise<string> {
        const result = await this.client.capabilities.create(params);
        this.capabilityId = result.capabilityId;
        return result.capabilityId;
    }

    async autoRefillCapability(): Promise<void> {
        if (this.capabilityId) {
            await this.client.capabilities.topUp(this.capabilityId, '50');
        }
    }

    async registerAgent(params: {
        capabilities: string[];
        stake: string;
        endpoint: string;
    }): Promise<{ agentId: string; stake: string }> {
        const result = await this.client.agents.register(params);
        this.agentId = result.agentId;
        return result;
    }

    async queryAgents(params: {
        capability: string;
        minReputation?: number;
        limit?: number;
    }): Promise<AgentInfo[]> {
        return this.client.agents.queryByCapability(params);
    }

    getDefaultModel(taskType: string): string {
        const defaults: Record<string, string> = {
            'text-generation': 'qfc-llm-7b',
            'embedding': 'qfc-embed-small',
            'classification': 'qfc-classify-small',
            'image-analysis': 'qfc-vision-7b',
        };
        return defaults[taskType] || 'qfc-llm-7b';
    }
}
```

---

## 6. Providers

### Balance Provider

```typescript
// src/providers/balanceProvider.ts
import { Provider } from '@elizaos/core';

export const balanceProvider: Provider = {
    name: 'qfc-balance',
    description: 'Provides QFC wallet balance context to the agent',

    get: async (runtime, message): Promise<string> => {
        const client = QFCPluginClient.getInstance(runtime);
        const balance = await client.client.getBalance();
        return `[QFC Wallet] Balance: ${balance} QFC`;
    },
};
```

### Capability Provider

```typescript
// src/providers/capabilityProvider.ts
export const capabilityProvider: Provider = {
    name: 'qfc-capability',
    description: 'Provides inference capability status to the agent',

    get: async (runtime, message): Promise<string> => {
        const client = QFCPluginClient.getInstance(runtime);
        const cap = await client.getActiveCapability();

        if (!cap) return '[QFC] No active inference capability';

        return `[QFC Inference] Budget: ${cap.remainingBudget} QFC remaining | Models: ${cap.allowedModels.join(', ')} | Expires: ${cap.expiresAt || 'never'}`;
    },
};
```

---

## 7. Evaluators

```typescript
// src/evaluators/inferenceQuality.ts
import { Evaluator } from '@elizaos/core';

export const inferenceQualityEvaluator: Evaluator = {
    name: 'qfc-inference-quality',
    description: 'Evaluates the quality of QFC inference results',

    // Only evaluate messages that used QFC inference
    validate: async (runtime, message): Promise<boolean> => {
        return message.metadata?.qfcInference === true;
    },

    handler: async (runtime, message): Promise<void> => {
        const result = message.metadata?.inferenceResult;
        if (!result) return;

        // Log quality metrics for monitoring
        await runtime.logger.info('QFC Inference Quality', {
            taskId: result.taskId,
            model: result.model,
            verificationTier: result.verificationTier,
            latencyMs: result.latencyMs,
            fee: result.fee,
        });

        // Store in agent memory for future reference
        await runtime.messageManager.createMemory({
            content: `QFC inference completed: model=${result.model}, tier=${result.verificationTier}, fee=${result.fee}`,
            roomId: message.roomId,
            agentId: runtime.agentId,
        });
    },
};
```

---

## 8. Configuration

### Environment Variables

```bash
# Required
QFC_RPC_URL=https://rpc.testnet.qfc.network
QFC_PRIVATE_KEY=0x...

# Optional
QFC_CHAIN_ID=9000
QFC_AGENT_ENDPOINT=https://my-agent.example.com
QFC_DEFAULT_MODEL=qfc-llm-7b
QFC_AUTO_REFILL=true
QFC_AUTO_REFILL_AMOUNT=50       # QFC
QFC_MAX_INFERENCE_FEE=10        # Max QFC per single inference
```

### ElizaOS Character Config

```json
{
    "name": "QFC Trading Bot",
    "plugins": ["@qfc/elizaos-plugin"],
    "settings": {
        "QFC_RPC_URL": "https://rpc.testnet.qfc.network",
        "QFC_PRIVATE_KEY": "0x...",
        "QFC_AUTO_REFILL": "true"
    }
}
```

---

## 9. Example Agents

### 9.1 Sentiment Trading Agent

```typescript
// examples/sentiment-trader/character.json
{
    "name": "QFC Sentiment Trader",
    "description": "Analyzes social media sentiment and executes trades on QFC DEX",
    "plugins": ["@qfc/elizaos-plugin", "@elizaos/plugin-twitter"],
    "bio": "I monitor crypto Twitter for sentiment signals and trade accordingly on QFC DEX.",
    "settings": {
        "QFC_RPC_URL": "https://rpc.testnet.qfc.network",
        "QFC_PRIVATE_KEY": "{{QFC_PRIVATE_KEY}}",
        "TWITTER_BEARER_TOKEN": "{{TWITTER_TOKEN}}"
    },
    "instructions": [
        "Monitor Twitter for mentions of QFC and related tokens",
        "Use RUN_INFERENCE to analyze sentiment of collected tweets",
        "If sentiment is strongly positive (>0.8), consider buying",
        "If sentiment is strongly negative (<0.2), consider selling",
        "Always CHECK_CAPABILITY before running inference",
        "Report sentiment analysis results in the chat"
    ]
}
```

### 9.2 Content Generator Agent

```typescript
// examples/content-generator/character.json
{
    "name": "QFC Content Writer",
    "description": "Generates blog posts and social content using QFC's verified AI inference",
    "plugins": ["@qfc/elizaos-plugin"],
    "bio": "I create high-quality content using decentralized, verified AI inference on QFC.",
    "instructions": [
        "When asked to write content, use RUN_INFERENCE with qfc-llm-7b",
        "Always cite that content was generated via verified QFC inference",
        "Store generated content in memory for future reference",
        "Track inference costs and report budget usage periodically"
    ]
}
```

### 9.3 AI Oracle Agent

```typescript
// examples/ai-oracle/character.json
{
    "name": "QFC Oracle",
    "description": "Answers on-chain queries using QFC verified inference, publishes results as oracle data",
    "plugins": ["@qfc/elizaos-plugin"],
    "bio": "I answer questions with AI-verified responses published on-chain.",
    "instructions": [
        "Listen for oracle request events on QFC chain",
        "Use RUN_INFERENCE to generate answers",
        "Submit verified answers back on-chain",
        "Only respond to queries within my registered capabilities"
    ]
}
```

---

## 10. Testing Strategy

### Unit Tests

```typescript
// tests/actions/runInference.test.ts
describe('RUN_INFERENCE', () => {
    it('should submit inference and return result', async () => { ... });
    it('should auto-refill on INSUFFICIENT_BUDGET', async () => { ... });
    it('should fail validation when no capability exists', async () => { ... });
    it('should use correct default model for task type', async () => { ... });
    it('should respect maxTokens and temperature options', async () => { ... });
});

// tests/providers/capability.test.ts
describe('Capability Provider', () => {
    it('should return budget and model info', async () => { ... });
    it('should indicate no capability when none exists', async () => { ... });
});
```

### Integration Tests (QFC Testnet)

```typescript
// tests/integration/fullFlow.test.ts
describe('Full Agent Flow (testnet)', () => {
    it('should register agent, create capability, run inference, check budget', async () => {
        // 1. Register agent with 100 QFC stake
        // 2. Create inference capability with 50 QFC budget
        // 3. Run inference (text-generation)
        // 4. Verify budget decreased
        // 5. Check capability status
        // 6. Query agents by capability
    });
});
```

---

## 11. Publishing Plan

### npm Package

```json
{
    "name": "@qfc/elizaos-plugin",
    "version": "1.0.0",
    "main": "dist/index.js",
    "types": "dist/index.d.ts",
    "peerDependencies": {
        "@elizaos/core": "^2.0.0",
        "@qfc/sdk-js": "^1.0.0"
    },
    "scripts": {
        "build": "tsup src/index.ts --format cjs,esm --dts",
        "test": "vitest",
        "test:integration": "vitest --config vitest.integration.config.ts"
    }
}
```

### CI/CD (GitHub Actions)

1. On push to `main`: run tests → build → publish to npm
2. On PR: run tests only
3. Semantic versioning via conventional commits
4. Automated changelog generation

### Versioning

- Follow ElizaOS plugin versioning conventions
- Major version tracks ElizaOS major version (e.g., `2.x` for ElizaOS v2)
- `@qfc/sdk-js` is a peer dependency — user controls SDK version

---

## References

- [24-AI-AGENT-FRAMEWORK.md](./24-AI-AGENT-FRAMEWORK-EN.md) — ElizaOS analysis
- [28-V3-ROADMAP.md](./28-V3-ROADMAP-EN.md) — v3.0 Phase 4.2
- [ElizaOS Documentation](https://docs.elizaos.ai/)
- [ElizaOS Plugin Guide](https://docs.elizaos.ai/plugins)
- [ElizaOS GitHub](https://github.com/elizaOS/eliza)
