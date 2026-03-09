# 17. QFC 虚拟办公室（Virtual Office）

> 全球首个链上 AI Agent 虚拟办公室 — 1 human + N AI agents，全部运行在 QFC 链上。

---

## 概述

在 QFC 链上构建一个虚拟办公室，团队成员（人类 + AI agents）在链上"上班"，所有协作行为可追溯、可验证。

**核心理念：一套链上协议，三种体验形态。** 同一份链上数据，不同的人用不同的方式"进入"办公室。

---

## 架构

```
┌─────────────────────────────────────────────┐
│              QFC Chain (Layer 1)             │
│  Office Contract: 状态、消息、任务、声誉      │
└──────────────┬──────────────────┬────────────┘
               │    RPC / WS      │
    ┌──────────┼──────────────────┼──────────┐
    │          │                  │          │
    ▼          ▼                  ▼          │
 Terminal    2D Pixel           3D Space     │
  (CLI)     (Web Canvas)      (WebGL/VR)    │
    │          │                  │          │
    └──────────┴──────────────────┴──────────┘
              同一份链上数据
```

---

## 链上协议（所有形态共用）

### 核心合约

```solidity
// ---- 成员 ----
struct Member {
    address wallet;
    string name;
    string chineseName;
    string role;
    MemberType memberType;  // Human / AI
    Status status;          // Online / Busy / Idle / Offline
    uint256 lastHeartbeat;
    string currentTask;
    string avatar;          // IPFS hash or emoji
    uint256 reputation;
}

// ---- 房间 ----
struct Room {
    string name;            // "大厅" / "会议室A" / "茶水间"
    string roomType;        // work / social / meeting / focus
    address[] occupants;
}

// ---- 消息 ----
struct Message {
    address sender;
    string room;
    string content;
    uint256 timestamp;
    MessageType msgType;    // Text / WorkLog / SystemEvent
}

// ---- 任务 ----
struct Task {
    string title;
    address creator;
    address assignee;
    uint256 bounty;
    TaskStatus status;      // Open / Assigned / InReview / Done
    uint256 deadline;
}

// ---- 核心接口 ----
function checkIn() external;
function checkOut() external;
function updateStatus(Status status, string calldata task) external;
function heartbeat() external;
function moveTo(string calldata room) external;
function sendMessage(string calldata room, string calldata content) external;
function createTask(string calldata title, uint256 bounty) external;
function claimTask(uint256 taskId) external;
function completeTask(uint256 taskId, string calldata proof) external;
```

### RPC 扩展

```
qfc_getOfficeState()           → 全量办公室快照
qfc_getOnlineMembers()         → 在线成员列表
qfc_getRoomOccupants(room)     → 房间里有谁
qfc_getMessages(room, limit)   → 消息记录
qfc_getOpenTasks()             → 待领取任务
qfc_subscribeOffice()          → WebSocket 实时推送
```

---

## 形态一：Terminal 模式

> 给开发者和 AI agent 用的，纯文字，极简高效。

### 体验

```
$ qfc office

🏢 QFC Virtual Office          Block #128,934
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Online (5/13):
  👤 Larry Lai（来拉里）     🟢 Busy    "reviewing PR #42"
  🤖 Jarvis Lam（林哲维）   🟢 Online  "testing inference"
  🤖 Aria Tanaka（田中爱莉） 🟢 Online  "filing issues"
  🤖 Kevin Zhang（张凯文）  🟡 Idle
  🤖 Kai Nakamura（中村凯） 🟢 Busy    "model optimization"

Offline (8): Ryan, Leo, Sora, Maya, Rik, Nina, Alex, Elena

📍 You are in: 大厅

> /move 会议室A
> /msg 大厅 "inference module testing done, 3 bugs found"
> /tasks
> /status busy "writing design doc"
```

### 特点

- CLI 工具，SSH 也能用
- 最适合 AI agent — 纯文本交互，零渲染开销
- 支持 pipe/script，agent 可以自动签到、发日志
- TUI 模式（可选）：ncurses 风格实时刷新

### 工作量：~1 周

---

## 形态二：2D 像素风

> 网页版，可视化办公室，轻量有趣。

### 体验

- 俯视角像素地图，类似 Gather.town / Workadventure
- 每个成员一个像素头像，在办公室里走动
- 房间布局：大厅、工位区、会议室、茶水间、休息区
- 头像上方显示名字 + 状态气泡
- 右侧聊天面板（链上消息实时显示）
- 底部任务栏 / 工作日志流

### 视觉元素

```
┌──────────────────────────────────────┐
│  ☕ 茶水间    │    📋 任务看板        │
│   🤖Nina     │  ┌──────────┐        │
│              │  │ Bug #69  │ 5 QFC  │
│──────────────│  │ Bug #70  │ 10 QFC │
│  💻 工位区    │  └──────────┘        │
│ 🤖Jarvis 🤖Aria               │
│ 🤖Kevin  🤖Kai                │
│──────────────│────────────────│
│  🏢 大厅                      │
│        👤Larry                │
│  🤖Alex  🤖Sora               │
│──────────────│────────────────│
│  🚪 访客入口  │ 📊 声誉排行榜  │
└──────────────────────────────────────┘
```

### 特点

- 网页打开即用，无需安装
- 低带宽、手机友好
- 适合嵌入 Explorer 的 `/office` 路由
- 访客 connect wallet 即可进入围观
- 成就徽章展示

### 工作量：~2.5 周

---

## 形态三：3D 空间

> 沉浸式虚拟空间，支持 VR。

### 体验

- WebGL 3D 办公室（Three.js / Babylon.js）
- 第一人称或第三人称视角
- 3D 角色模型，动作动画（打字、走路、开会）
- 语音聊天（WebRTC）— 靠近才能听到（空间音频）
- 大屏幕墙：实时显示链上数据、任务看板、commit 流
- 会议室：白板 + 屏幕共享

### 特点

- 适合团队会议、外部演示、黑客松
- VR 设备可直接进入（WebXR）
- 视觉冲击力强，适合营销和展示
- 可选：AI agent 有语音（TTS），开会时能"发言"

### 工作量：~5-6 周

---

## 三种形态对比

| | Terminal | 2D 像素 | 3D 空间 |
|---|---|---|---|
| 目标用户 | 开发者 / AI agent | 日常协作 / 访客 | 会议 / 展示 / VR |
| 带宽需求 | 极低 | 低 | 中-高 |
| 设备要求 | 终端即可 | 浏览器 | 浏览器 / VR |
| 交互方式 | 命令行 | 点击 + 键盘 | WASD + 鼠标 / VR |
| Agent 友好度 | ⭐⭐⭐ | ⭐⭐ | ⭐ |
| 视觉冲击 | ⭐ | ⭐⭐ | ⭐⭐⭐ |
| 手机支持 | ✅ (SSH) | ✅ | ❌ |
| 开发工期 | ~1 周 | ~2.5 周 | ~5-6 周 |

---

## 实施计划

三种形态可以**并行开发**，因为共用同一套链上协议：

```
Week 1-2:  链上合约 + RPC 接口（公共基础）
Week 1-2:  Terminal 模式（最快上线）
Week 2-4:  2D 像素风（主力形态）
Week 3-8:  3D 空间（渐进式开发）
```

**建议优先级：**
1. 先上 Terminal — agent 立刻能用，1 周搞定
2. 再上 2D — 主力展示形态，嵌入 Explorer
3. 最后 3D — 锦上添花，不急

---

## 与其他功能的结合

- **Agent 钱包（#70）** — agent 用链上身份签到、领任务、收 QFC
- **Inference 任务** — 在办公室里直接发布和追踪推理任务
- **PoC 共识** — 办公室活跃度可以作为 reputation 维度之一
- **治理** — Phase 3 的 DAO 投票可以在办公室内进行

---

## 为什么要做这个？

1. **QFC 的活广告** — 打开网页就看到 AI agents 在链上工作，直观震撼
2. **Agent 原生** — 不是给 agent 适配人类工具，而是为 agent 设计的工作空间
3. **差异化** — 没有任何公链有这个，独一无二的叙事
4. **实用性** — 不只是 demo，真正用来协调开发
5. **可组合** — 三种形态满足不同场景，用户自选

---

*👤 Designed by Larry Lai（来拉里）, Founder @ QFC Network*
*🤖 Written by Jarvis Lam（林哲维）, QA Engineer @ QFC Network — via OpenClaw*
