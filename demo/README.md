# QFC Inference Demo — public relay + landing page

Gap B's "1-minute pitch" artifact: a stranger visits a URL, types text, clicks Submit, sees

1. A QFC inference result (embedding vector today, LLM text after [`PROPOSAL-LLM-MODEL-CATALOG.md`](../PROPOSAL-LLM-MODEL-CATALOG.md) passes)
2. The on-chain task ID + miner that executed it
3. A link to the explorer proof page

No wallet, no faucet, no MetaMask prompt. The relay wallet pays the tiny fee for them.

## Structure

```
demo/
├── README.md       ← this file
├── relay/          ← Node.js backend that signs + submits tasks
│   ├── server.js
│   ├── package.json
│   └── Dockerfile
└── public/
    └── index.html  ← single-page frontend, zero build step
```

## What the relay does

- Holds a pre-funded QFC wallet (topped up from the faucet once a day by a cron)
- Accepts `POST /api/inference` from the frontend, rate-limited by IP
- Signs and submits the task via `qfc_submitPublicTask`
- Polls `qfc_getPublicTaskStatus` until Completed (usually <1 s)
- Returns result + taskId + minerAddress + block height to the frontend

## Deploying (user action needed)

Code is ready but the relay needs a host. Two paths:

### Path A — VPS-A (same host as the NFT/DEX/explorer stack)

```bash
# On VPS-A:
cd ~/qfc-testnet  # or wherever the 4vps compose lives
# Drop into the existing docker-compose stack:
#   qfc-demo-relay service → reads env vars for funded wallet
# Then point Traefik at demo.testnet.qfc.network
```

The relay image can be built from this directory and published to ghcr via a CI workflow similar to `qfc-testnet-bot`.

### Path B — any cheap VPS + Caddy/nginx

```bash
git clone https://github.com/qfc-network/qfc-design.git
cd qfc-design/demo/relay
npm install
QFC_RELAY_PRIVATE_KEY=<key> QFC_RPC_URL=https://rpc.testnet.qfc.network \
  node server.js
# Then serve demo/public/index.html from any static host
```

## Security notes

- The relay wallet is **demo-funded only** (never more than ~50 QFC at a time). If it gets drained, the demo stops — it does not leak private user data.
- Rate limiting is per-IP (10 requests / hour by default). Tune via `QFC_RELAY_RATE_LIMIT`.
- Input length is capped at 512 characters to prevent abuse.
- The relay's signing key is required (env var `QFC_RELAY_PRIVATE_KEY`). Never commit it.

## Cost per demo call

At current testnet fees (0.1 QFC per inference task) and a generous 1000 calls/day cap, the relay burns ~100 QFC/day. Faucet gives 10 QFC per 24h per address, so the relay wallet needs ~10 addresses in rotation, OR the treasury grants it periodic top-ups. Pick one before launch.

## What this demo proves (and doesn't)

**Proves:**
- The public API works end-to-end from outside the chain
- Verifiable inference exists and a random visitor can see the proof link
- Latency is real (<1 s) — not theoretical

**Doesn't prove:**
- Economic sustainability (the relay is paying, not the user)
- LLM capability (until the proposal above passes)
- Anti-abuse at scale (rate limiting is simple; sophisticated attacker could exhaust budget)

The demo is a foot-in-the-door, not a product. The moment a visitor says "cool, how do I use this in MY app?", you hand them [`../sdk-snippets/`](../sdk-snippets/).
