# QFC 项目现状与下一步规划

> 最后更新: 2026-04-07

---

## 1. 项目现状

### 1.1 基础设施

| 组件 | 状态 | 说明 |
|------|------|------|
| 测试网出块 | ✅ 正常 | 区块高度 140,000+，持续出块中 |
| 4-VPS 集群 | ✅ 稳定 | VPS-A (App)、B (Node)、C (DB)、D (Observability) |
| Terraform | ✅ 已同步 | State 存储在 S3，代码与 AWS 实际状态一致 |
| 监控告警 | ✅ 运行中 | Prometheus + Grafana + AlertManager + Telegram Bot |
| CI/CD | ✅ 自动化 | GitHub Actions → GHCR → 自动更新 image tag |
| 磁盘使用 | ✅ 健康 | VPS-A: 13% (58GB)、VPS-D: 9% (116GB) |

### 1.2 链与矿工

| 组件 | 状态 | 说明 |
|------|------|------|
| 节点 (3) | ✅ healthy | geth 兼容，EVM 100% 兼容 |
| 矿工 (2) | ✅ 运行中 | AI inference 任务持续提交，proof accepted |
| Chain ID | 9000 | 测试网 |
| 出块时间 | ~19s | |
| 推理模型 | qfc-embed-small, qfc-embed-medium | candle ML 后端 |

### 1.3 线上服务

| 服务 | URL | 状态 |
|------|-----|------|
| 区块浏览器 | explorer.testnet.qfc.network | ✅ 200 |
| 浏览器 API | api.explorer.testnet.qfc.network | ✅ 200 |
| DEX | dex.testnet.qfc.network | ✅ 200 |
| DeFi 仪表盘 | defi.testnet.qfc.network | ✅ 200 |
| NFT 市场 | nft.testnet.qfc.network | ✅ 200 |
| 跨链桥 | bridge.testnet.qfc.network | ✅ 200 |
| 水龙头 | faucet.testnet.qfc.network | ✅ 200 |
| 游戏中心 | games.testnet.qfc.network | ✅ 200 |
| Agent Hub | agenthub.testnet.qfc.network | ✅ 200 |

### 1.4 客户端工具

| 工具 | 状态 | 说明 |
|------|------|------|
| 浏览器钱包 | ✅ 功能完整 | Swap、NFT、Inference Submit、Speed Up/Cancel Tx |
| JS SDK | ✅ 已完成 | ethers.js 封装 |
| Python SDK | ✅ 已完成 | web3.py 封装 |
| CLI 工具 | ✅ 已完成 | Node.js + commander |
| 移动钱包 | ✅ 已完成 | React Native + Expo |

### 1.5 智能合约（已部署到测试网）

| 合约 | 说明 |
|------|------|
| DEX (Factory + Router + WQFC) | Uniswap V2 风格 AMM |
| NFT (CollectionFactory + Marketplace + AuctionHouse) | NFT 创建、交易、拍卖 |
| Bridge (LockRelease + MintBurn) | QFC ↔ ETH/BSC 跨链桥 |
| qUSD Stablecoin | CDP 模式铸造 |
| DeFi (Lending Pool, Staking, Liquid Staking, Vaults, Launchpad) | 全套 DeFi 协议 |

### 1.6 存在的问题

| 问题 | 严重程度 | 说明 |
|------|----------|------|
| DeFi/NFT/DEX 前端使用 mock data | 🟡 中 | 页面在线但没有真实合约交互 |
| AgentHub 只有空壳 | 🟡 中 | 有设计文档，无实际功能 |
| 钱包未上架 Chrome Web Store | 🟢 低 | 功能已完整 |
| 合约未经审计 | 🟡 中 | 测试网可以先不审，主网前必须做 |
| 只有自己的节点在出块 | 🟡 中 | 无外部验证者 |

---

## 2. 下一步规划

### Phase 1：产品可用（当前 → 4 周）

**目标：** 让用户能在测试网上完成真实的 DeFi 和 NFT 操作

#### 1.1 前端接合约（优先级最高）

当前 defi、nft-marketplace、dex 的前端全部使用 mock data。需要替换为真实合约调用。

| 项目 | 当前状态 | 工作量 |
|------|----------|--------|
| DEX (qfc-dex) | 合约已部署，前端有 hooks 但地址为零 | 小 — 填入合约地址，测试交互 |
| NFT Marketplace (qfc-nft-marketplace) | 合约已部署，前端有 ABI 但地址为零 | 中 — 需要接 indexer |
| DeFi Dashboard (qfc-defi) | 合约已部署，前端全 mock | 大 — 每个功能页都要接 |

优先级：DEX → NFT → DeFi

#### 1.2 浏览器钱包上架

- 打包 Chrome 扩展提交 Chrome Web Store 审核
- 准备 Store 页面素材（截图、描述）
- 审核周期约 1-2 周

#### 1.3 水龙头改进

- 当前每次 10 QFC，足够测试但 UX 可以优化
- 加 Captcha 防滥用

### Phase 2：AgentHub MVP（4 → 8 周）

**目标：** 跑通 AI Agent 注册 → 任务分配 → 执行 → 收据 最小闭环

AgentHub 是 QFC 的差异化核心。QFC 不只是"又一条 EVM 链"，而是"AI inference chain"。AgentHub 让这个定位落地。

#### 2.1 核心功能

```
Agent 注册（ERC-721 NFT）
      ↓
GitHub Issue 触发 Webhook
      ↓
任务分配给 Agent
      ↓
Agent 执行（调用 QFC inference API）
      ↓
执行收据写回 GitHub + 链上
```

#### 2.2 组件

| 组件 | 说明 | 仓库 |
|------|------|------|
| Agent Registry | ERC-721 合约，链上身份 | qfc-contracts |
| Webhook Bridge | GitHub → AgentHub 事件转发 | qfc-agenthub |
| Task Router | 按能力匹配 Agent | qfc-agenthub |
| Receipt Store | 执行记录，链上锚定 | qfc-agenthub |
| AgentHub UI | 注册、监控、管理界面 | qfc-agenthub |

### Phase 3：主网准备（8 → 16 周）

**目标：** 具备主网上线条件

#### 3.1 安全

- [ ] 核心合约安全审计（至少 DEX、Bridge、qUSD）
- [ ] 渗透测试（RPC 节点、Explorer API）
- [ ] Bug Bounty 计划

#### 3.2 去中心化

- [ ] 开放验证者申请
- [ ] 至少 10 个外部验证者节点
- [ ] 验证者经济模型最终确定（staking、slash 机制）

#### 3.3 文档与开发者体验

- [ ] 开发者文档完善（qfc-docs）
- [ ] 合约部署教程
- [ ] SDK 使用示例
- [ ] API 文档（Explorer API、RPC extensions）

#### 3.4 主网配置

- [ ] Chain ID 9001
- [ ] Genesis 配置定稿
- [ ] 初始代币分配执行
- [ ] 多区域节点部署（至少 3 个地理区域）

### Phase 4：生态扩展（主网后）

- **跨链 AI Oracle** — 其他链通过 QFC 调用 AI 推理（见 25-CROSS-CHAIN-AI-ORACLE）
- **模型市场** — 开发者上传自定义模型到 QFC 网络
- **Agent 代币工厂** — Agent 发行自己的代币（见 36-AGENT-TOKEN-FACTORY）
- **CEX 上线** — 交易所合作

---

## 3. 技术债

| 项目 | 问题 | 优先级 |
|------|------|--------|
| Dockerfile | 多个 Next.js 项目缺少 `COPY public`，已陆续修复 | ✅ 已解决 |
| VPS-A .env 漂移 | docker-compose.yaml 的 image tag 在 .env 里手动管理 | 低 |
| VPS-D Loki | 只保留 error/warn 日志，7 天留存 | ✅ 已优化 |
| Terraform state | 已迁移到 S3 backend，不会再丢失 | ✅ 已解决 |
| Node.js 20 deprecation | GitHub Actions 警告 Node 20 将于 2026-09 移除 | 低 — 6 月前升级 actions 版本 |

---

## 4. 关键指标（测试网）

| 指标 | 当前值 | 目标 |
|------|--------|------|
| 区块高度 | 140,000+ | 持续增长 |
| 活跃验证者 | 3（自有） | 10+（含外部） |
| 部署合约数 | 15+ | 50+ |
| 日活地址 | ~1（开发团队） | 100+（公测后） |
| 推理任务/天 | ~8,600（10s/task × 2 miners） | 按需扩展 |
| 服务在线率 | 99%+（近 7 天） | 99.9% |
