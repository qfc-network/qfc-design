# 32. QFC Chain Games Deployment Strategy

**English** | [中文](./32-DEPLOYMENT-STRATEGY-CN.md)

> How to deploy QFC chain games from localhost to the public internet so anyone can play.

---

## Existing Projects

| Project | Port | Frontend | Backend | Status |
|------|------|------|------|------|
| qfc-office | 3210 | Phaser/Three.js | Express+WS | ✅ Done |
| qfc-cards | 3220 | Canvas | Express+WS | ✅ Done |
| qfc-pets | 3230 | DOM/CSS | Express | ✅ Done |

**Common trait: all require a Node.js backend** (state management, WebSocket, API). Pure static hosting won't work.

---

## Option Comparison

### Option A: Railway (Recommended ⭐)
- **Pros**: One-click Node.js deployment, built-in WebSocket support, $5/month free tier
- **Cons**: Limited free tier, sleep mechanism (auto-sleeps after 30min of no traffic)
- **Best for**: Fast launch during the MVP phase
- **Deploy**: `railway up` or connect GitHub for auto-deploy

### Option B: Fly.io
- **Pros**: Global edge deployment, good WebSocket support, 3 free small instances
- **Cons**: Slightly more complex setup, requires a Dockerfile
- **Best for**: Real-time games that need low latency

### Option C: VPS (Self-Hosted)
- **Pros**: Full control, no limits, cheapest long-term
- **Cons**: Requires ops work
- **Best for**: Production operations phase
- **Recommended**: Hetzner (€4.5/month) or DigitalOcean ($5/month)

### Option D: Vercel + Serverless
- **Pros**: Dead-simple frontend deployment, free
- **Cons**: No WebSocket support (requires Pusher/Ably etc.), state needs external storage
- **Best for**: Pure API + static frontend; not suitable for real-time games

### Option E: GitHub Pages + External API
- **Pros**: Free, CDN acceleration
- **Cons**: Static files only; backend must be deployed separately
- **Best for**: Frontend showcase with the backend running elsewhere

---

## Recommended Approach: Unified Gateway + Subpaths

```
games.qfc.network (Nginx/Caddy)
├── /office/  → qfc-office (port 3210)
├── /cards/   → qfc-cards (port 3220)
├── /pets/    → qfc-pets (port 3230)
└── /         → game lobby page
```

### Implementation Steps

#### Step 1: Create a Unified Entry Point (Game Lobby)
```
qfc-games/
├── lobby/          # Game lobby (static page)
│   ├── index.html  # Lists all games, links out
│   └── style.css
├── qfc-office/     # Submodule or standalone directory
├── qfc-cards/
└── qfc-pets/
```

#### Step 2: Dockerize
One Dockerfile per game:
```dockerfile
FROM node:22-slim
WORKDIR /app
COPY package*.json ./
RUN npm ci --production
COPY . .
RUN npm run build
CMD ["npm", "start"]
```

#### Step 3: Docker Compose (Local/VPS)
```yaml
version: "3.8"
services:
  lobby:
    build: ./lobby
    ports: ["3200:3200"]
  office:
    build: ./qfc-office/web
    ports: ["3210:3210"]
    volumes: ["shared-state:/root/.qfc-office"]
  cards:
    build: ./qfc-cards
    ports: ["3220:3220"]
  pets:
    build: ./qfc-pets
    ports: ["3230:3230"]
    volumes: ["pets-state:/root/.qfc-pets"]
  nginx:
    image: nginx:alpine
    ports: ["80:80", "443:443"]
    volumes: ["./nginx.conf:/etc/nginx/conf.d/default.conf"]
    depends_on: [lobby, office, cards, pets]

volumes:
  shared-state:
  pets-state:
```

#### Step 4: Fast Railway Deployment (MVP)
Deploy each project to Railway independently:
```bash
# In each project directory
railway login
railway init
railway up
```

Each gets a `*.railway.app` domain automatically.

---

## Quick Path: Run Locally First, Expose via Cloudflare Tunnel

Fastest way to go live (5 minutes):
```bash
# Install cloudflared
brew install cloudflare/cloudflare/cloudflared

# Start all services
cd qfc-office/web && npm start &
cd qfc-cards && npm start &
cd qfc-pets && npm start &

# Expose to the public internet
cloudflared tunnel --url http://localhost:3210  # office
cloudflared tunnel --url http://localhost:3220  # cards  
cloudflared tunnel --url http://localhost:3230  # pets
```

Each gets a temporary public `*.trycloudflare.com` URL.

---

## End Goal

```
games.qfc.network
├── /          → Game lobby (React/static)
├── /office    → Virtual office (3 modes)
├── /cards     → AI strategy cards
├── /pets      → AI pets
├── /arena     → AI Arena (future)
└── /dungeon   → AI dungeon (future)
```

Everything connects to on-chain data via QFC testnet RPC.

---

## Game Lobby Design

```
┌─────────────────────────────────────────┐
│     🎮 QFC Game Center                  │
│     Play AI-powered games on QFC Chain  │
├─────────────────────────────────────────┤
│                                         │
│  🏢 Virtual Office    🃏 AI Cards       │
│  Work-to-Earn         Strategy TCG      │
│  [Play]               [Play]            │
│                                         │
│  🐾 AI Pets           🏟️ AI Arena       │
│  Raise & Battle       Coming Soon       │
│  [Play]               [Soon]            │
│                                         │
└─────────────────────────────────────────┘
```

---

*👤 Designed by Larry Lai（来拉里）, Founder @ QFC Network*  
*🤖 Written by Jarvis Lam（林哲维）, QA Engineer @ QFC Network — via OpenClaw*
