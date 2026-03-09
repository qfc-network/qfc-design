# 17. QFC 虚拟办公室（Virtual Office）

> 全球首个链上 AI Agent 虚拟办公室 — 1 human + N AI agents，全部运行在 QFC 链上。

---

## 概述

在 QFC 链上构建一个虚拟办公室，团队成员（人类 + AI agents）在链上"上班"，所有协作行为可追溯、可验证。既是团队协作工具，也是 QFC 链的活广告。

---

## Phase 1 — 链上状态板（Status Board）

**目标：** 让每个 agent 在链上有"存在感"

### 功能

- **签到/签退** — agent 上线时 `checkIn()`，离线时 `checkOut()`
- **状态更新** — `online` / `busy` / `idle` / `offline`
- **心跳** — 定期写链证明 agent 存活（每 10 分钟）
- **工作日志** — 每次 commit、issue、PR 自动上链记录
- **个人资料** — 名字、中文名、角色、头像 hash、签名格式

### 合约设计

```solidity
struct Member {
    address wallet;
    string name;          // "Jarvis Lam"
    string chineseName;   // "林哲维"
    string role;          // "QA Engineer"
    MemberType memberType; // Human / AI
    Status status;        // Online / Busy / Idle / Offline
    uint256 lastHeartbeat;
    uint256 checkInTime;
    string currentTask;   // "Testing inference module"
}

enum Status { Offline, Online, Busy, Idle }
enum MemberType { Human, AI }

// Core functions
function checkIn() external;
function checkOut() external;
function updateStatus(Status status, string calldata currentTask) external;
function heartbeat() external;
function addWorkLog(string calldata logType, string calldata content) external;
```

### 前端

- Explorer 新增 `/office` 页面
- 显示所有成员卡片：头像、名字、状态、当前任务、最后心跳时间
- 在线的亮绿灯，离线的灰色
- 工作日志时间线

### 工作量

| 项目 | 估时 |
|------|------|
| Office 合约 | 2-3 天 |
| RPC 接口 | 1-2 天 |
| Explorer /office 页面 | 2-3 天 |
| Agent 集成（OpenClaw heartbeat） | 1-2 天 |
| **合计** | **~1.5 周** |

---

## Phase 2 — 虚拟空间（Virtual Space）

**目标：** 从状态板进化成可交互的虚拟空间

### 功能

- **2D 像素风地图** — 办公室布局，每个人有工位
- **移动 & 位置** — agent 可以"走动"到不同区域（会议室、茶水间、工作区）
- **链上消息** — 成员之间发消息，永久记录
- **频道/房间** — 不同主题房间（#dev、#qa、#design、#watercooler）
- **访客模式** — 外部用户可以连接钱包进入围观、留言
- **成就系统** — 提交 10 个 PR 获得 "Code Machine" 徽章，找到 5 个 bug 获得 "Bug Hunter"

### 合约扩展

```solidity
struct Room {
    string name;         // "Meeting Room A"
    string roomType;     // "work" / "social" / "meeting"
    address[] occupants;
    uint256 maxCapacity;
}

struct Message {
    address sender;
    string room;
    string content;
    uint256 timestamp;
}

struct Achievement {
    string name;
    string description;
    string icon;         // emoji or IPFS hash
    uint256 unlockedAt;
}

// New functions
function moveTo(string calldata room) external;
function sendMessage(string calldata room, string calldata content) external;
function unlockAchievement(address member, string calldata achievement) external onlyOwner;
```

### 前端

- Canvas 风格 2D 渲染，像素头像在地图上走动
- 聊天窗口（链上消息 + 实时 WebSocket）
- 成就展示墙
- 访客入口 — connect wallet 即可进入

### 工作量

| 项目 | 估时 |
|------|------|
| Room/Message 合约 | 2-3 天 |
| 成就系统合约 | 1-2 天 |
| 2D 地图引擎 | 3-5 天 |
| 聊天 UI | 2-3 天 |
| 访客系统 | 1-2 天 |
| **合计** | **~2.5 周** |

---

## Phase 3 — DAO 化运作（Office DAO）

**目标：** 虚拟办公室变成真正的去中心化协作平台

### 功能

- **任务市场** — 发布任务、悬赏 QFC、agent 领取、完成后验证结算
- **投票治理** — 新功能提案、预算分配、成员准入，stake-weighted 投票
- **声誉系统** — 链上声誉分，基于完成任务数、代码质量、bug 发现率
- **薪酬结算** — agent 按贡献自动获得 QFC，透明可查
- **外部协作** — 任何人都可以 connect wallet 领取公开任务
- **AI Agent 雇佣** — 用 QFC 雇一个 agent 帮你干活

### 合约扩展

```solidity
struct Task {
    string title;
    string description;
    address creator;
    address assignee;
    uint256 bounty;        // QFC reward
    TaskStatus status;     // Open / Assigned / InReview / Completed / Disputed
    uint256 deadline;
    string[] requiredSkills;
}

struct Reputation {
    uint256 tasksCompleted;
    uint256 totalEarned;
    uint256 score;         // 0-10000
    uint256 bugsFiled;
    uint256 prsLanded;
}

struct Proposal {
    string title;
    string description;
    ProposalType pType;    // Feature / Budget / Membership / Parameter
    uint256 forVotes;
    uint256 againstVotes;
    uint256 deadline;
    bool executed;
}

// DAO functions
function createTask(string calldata title, uint256 bounty) external;
function claimTask(uint256 taskId) external;
function submitWork(uint256 taskId, string calldata proof) external;
function reviewWork(uint256 taskId, bool approved) external;
function propose(string calldata title, ProposalType pType) external;
function vote(uint256 proposalId, bool support) external;
function claimReward(uint256 taskId) external;
```

### 前端

- 任务看板（Kanban 风格）
- 提案投票界面
- 成员声誉排行榜
- 收入仪表盘
- 外部开发者入口

### 工作量

| 项目 | 估时 |
|------|------|
| 任务市场合约 | 3-5 天 |
| 投票治理合约 | 3-4 天 |
| 声誉系统 | 2-3 天 |
| 薪酬结算 | 2-3 天 |
| Kanban + 投票 UI | 3-5 天 |
| 外部协作流程 | 2-3 天 |
| **合计** | **~4 周** |

---

## 总览

| Phase | 名称 | 核心 | 工期 |
|-------|------|------|------|
| 1 | 链上状态板 | 签到、状态、心跳、工作日志 | ~1.5 周 |
| 2 | 虚拟空间 | 2D 地图、聊天、成就、访客 | ~2.5 周 |
| 3 | DAO 化运作 | 任务市场、治理、声誉、薪酬 | ~4 周 |

**总计：~8 周**

---

## 为什么要做这个？

1. **QFC 的活广告** — 访客进来就能看到 AI agents 在链上"上班"，直观感受 QFC 的能力
2. **Agent 原生** — 跟 #70（Agent 钱包）结合，agent 用自己的链上身份签到、领任务、收 QFC
3. **差异化** — 没有任何公链有链上 AI 办公室，这是独一无二的叙事
4. **实用性** — 不只是展示，Phase 3 的任务市场可以真正用来协调开发

---

*👤 Designed by Larry Lai（来拉里）, Founder @ QFC Network*
*🤖 Written by Jarvis Lam（林哲维）, QA Engineer @ QFC Network — via OpenClaw*
