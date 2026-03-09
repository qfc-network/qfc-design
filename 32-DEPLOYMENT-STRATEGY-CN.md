# 32. QFC 链游部署策略（Deployment Strategy）

> 如何将 QFC 链游从 localhost 部署到公网，让任何人都能玩。

---

## 现有项目

| 项目 | 端口 | 前端 | 后端 | 状态 |
|------|------|------|------|------|
| qfc-office | 3210 | Phaser/Three.js | Express+WS | ✅ 完成 |
| qfc-cards | 3220 | Canvas | Express+WS | ✅ 完成 |
| qfc-pets | 3230 | DOM/CSS | Express | ✅ 完成 |

**共同特点：全部需要 Node.js 后端**（状态管理、WebSocket、API）。不能用纯静态托管。

---

## 方案比较

### 方案 A: Railway (推荐 ⭐)
- **优点**: 一键部署 Node.js，自带 WebSocket 支持，免费额度 $5/月
- **缺点**: 免费额度有限，睡眠机制（30min 无流量自动休眠）
- **适合**: MVP 阶段快速上线
- **部署**: `railway up` 或连接 GitHub 自动部署

### 方案 B: Fly.io
- **优点**: 全球边缘部署，WebSocket 支持好，免费 3 个小实例
- **缺点**: 配置稍复杂，需要 Dockerfile
- **适合**: 需要低延迟的实时游戏

### 方案 C: VPS (自建)
- **优点**: 完全控制，无限制，最便宜长期
- **缺点**: 需要运维
- **适合**: 正式运营阶段
- **推荐**: Hetzner (€4.5/月) 或 DigitalOcean ($5/月)

### 方案 D: Vercel + Serverless
- **优点**: 前端部署极简，免费
- **缺点**: 不支持 WebSocket (需要 Pusher/Ably 等)，状态需要外部存储
- **适合**: 纯 API + 静态前端，不适合实时游戏

### 方案 E: GitHub Pages + 外部 API
- **优点**: 免费，CDN 加速
- **缺点**: 只能托管静态文件，后端需要单独部署
- **适合**: 前端展示，后端另外跑

---

## 推荐方案：统一网关 + 子路径

```
games.qfc.network (Nginx/Caddy)
├── /office/  → qfc-office (port 3210)
├── /cards/   → qfc-cards (port 3220)
├── /pets/    → qfc-pets (port 3230)
└── /         → 游戏大厅页面
```

### 实施步骤

#### Step 1: 创建统一入口（游戏大厅）
```
qfc-games/
├── lobby/          # 游戏大厅（静态页面）
│   ├── index.html  # 列出所有游戏，链接跳转
│   └── style.css
├── qfc-office/     # 子模块或独立目录
├── qfc-cards/
└── qfc-pets/
```

#### Step 2: Docker 化
每个游戏一个 Dockerfile：
```dockerfile
FROM node:22-slim
WORKDIR /app
COPY package*.json ./
RUN npm ci --production
COPY . .
RUN npm run build
CMD ["npm", "start"]
```

#### Step 3: Docker Compose（本地/VPS）
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

#### Step 4: Railway 快速部署（MVP）
每个项目独立部署到 Railway：
```bash
# 在每个项目目录
railway login
railway init
railway up
```

自动获得 `*.railway.app` 域名。

---

## 快速方案：先本地跑，用 Cloudflare Tunnel 暴露

最快上线（5 分钟）：
```bash
# 安装 cloudflared
brew install cloudflare/cloudflare/cloudflared

# 启动所有服务
cd qfc-office/web && npm start &
cd qfc-cards && npm start &
cd qfc-pets && npm start &

# 暴露到公网
cloudflared tunnel --url http://localhost:3210  # office
cloudflared tunnel --url http://localhost:3220  # cards  
cloudflared tunnel --url http://localhost:3230  # pets
```

每个获得一个 `*.trycloudflare.com` 临时公网 URL。

---

## 最终目标

```
games.qfc.network
├── /          → 游戏大厅（React/静态）
├── /office    → 虚拟办公室（3 模式）
├── /cards     → AI 策略卡牌
├── /pets      → AI 宠物
├── /arena     → AI Arena（未来）
└── /dungeon   → AI 地牢（未来）
```

全部通过 QFC 测试网 RPC 连接链上数据。

---

## 游戏大厅设计

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
