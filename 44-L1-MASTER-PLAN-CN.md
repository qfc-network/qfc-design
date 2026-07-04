# QFC L1 总体规划（Master Plan）

> 最后更新：2026-07-04
>
> 定位：本文档是 QFC L1 的**唯一顶层规划**，替代 39（现状已过时）并承接 42（三大缺口）的判据框架。42 的时间盒已到期但未被真正测试——整个窗口被共识分叉吃掉了，因此判据在此重置重新计时，纪律不变。

---

## 0. 现状快照（2026-07-04，如实）

**链核心（qfc-core）**
- ❌ **测试网从未达成多节点共识**——3 个 validator 从 block #1 三路分叉。已定位 6 个复合缺陷，修了 5 个（PR #126 leader election 收敛、#128 forward catch-up、#129 wall-clock slot/epoch），**第 6 个未修**：新节点启动时无"追平前禁止出块"门控，fresh boot 直接产自己的 block #1。
- ⚠️ 两次 reset 均失败（每次暴露一个新缺陷）。上次会话结论：停止逐个修-试循环，改为**对整条出块/同步路径做一次合并式审查**，把剩余缺陷一次找全、一起修、做最后一次 reset。
- ✅ SRE T1–T8 全部合并（PR #103–#123）但部署被 reset 阻塞。镜像流水线就绪（staging 分支构建，VPS-B 可拉取）。
- ✅ AI-V3：B-1 + Feature A（A0–A6）核心完成，B-2 spike 完成（交互式 WAN 推理 no-go，batch 受带宽门控）。剩余全部需要节点集成或跨区域真机。

**生态外围**
- ✅ 全家桶在线（explorer/dex/defi/nft/bridge/faucet/games/agenthub/钱包×3/SDK×2/CLI），完成度 60–95% 不等。
- ❌ **外部参与为零**：0 外部矿工、0 外部推理调用者、0 外部验证者。

**42 三大缺口的真实进度**（本次盘点修正：并非"全部未动"）
- **Gap C 大头已做**：`miner-economics/` 有模型 v2（MINER-ECONOMICS.md + model.py，2026-04-14 对活链实测），周度快照 snapshots.jsonl 自 05-10 连跑 8 周。结论：**条件性通过**——emission 按年减半（10 → 0.625 QFC/block，第 4 年到底），当前 75% 通胀 / 25% 费用的结构在零需求增长下也会因 emission 衰减在第 4 年自然到 ~39% 费用占比。两个存活条件：① 矿工要熬过 year 0 稀释（币价 < $0.05 时 RTX 3060 级亏损，低成本设备才保本）；② 需求要在矿工数超 ~500 前出现。外部 review 模板（REVIEW-REQUEST.md）与外联文案（OUTREACH-POSTS.md，$300/45min）已备好但**从未发出**。
- **Gap A 审查已做**：MINER-ONBOARDING-REVIEW.md（04-14）发现 2 个真实 bug 且**均未修**：① `start-miner.sh` 从 `qfc-core` release（v2.3.1，5 平台）下载而非 `qfc-miner` repo（v2.3.2，9 平台）——CUDA/Windows/ARM64 用户直接掉进源码编译；② 链 v2.2.3 与 binary v2.3.x 版本漂移未做端到端验证。
- **Gap B 未动**。

**核心结论**：外围严重超前于核心。链本身不收敛，一切外部化动作（矿工招募、需求验证、主网）都没有意义。规划必须从修链开始。

---

## 1. 战略主线

QFC 的存在理由只有一条闭环：

> **矿工跑 AI 推理换区块奖励（供给）↔ 用户/Agent 付费调用可验证推理（需求）**，跑在一条**能收敛、经济自洽**的链上。

一切工作按"是否推进这条闭环"排序。闭环验证不过，主网不启动；验证通过，主网才有资格进入日程。

```
Phase 0 链能跑 ──→ Phase 1 经济自洽 ──→ Phase 2 外部闭环验证 ──→ Phase 3 主网准备
   (硬前置)          (Gap C)              (Gap A + Gap B)           (PMF 之后才做)
```

---

## Phase 0 — 链能跑（当前 → 收敛验证完成）

**目标**：3 validator 从 fresh genesis 连续收敛 ≥ 7 天，SRE T2–T8 部署，合约全量重部署。

| # | 工作项 | 说明 |
|---|--------|------|
| 0.1 | **合并式共识审查** | 对 producer/sync/consensus/网络全路径做一次对抗式审查（多 agent），目标是把第 6 类之后的所有"多节点运行时才暴露"的缺陷一次找全。重点：sync-before-produce 门控、启动 grace、fork choice、时钟漂移容忍、epoch 边界竞态 |
| 0.2 | **修复全部发现** | 含已知的第 6 缺陷：producer 感知 SyncManager.highest_peer_block，strictly behind 时不出块；bootnode 无 peer 时立即出块建链 |
| 0.3 | **最终 reset（第 3 次，目标是最后一次）** | 新镜像 → 三节点 wipe → fresh genesis → 逐项验证：peering、epoch 一致、block #1/#100/#10k 哈希一致 |
| 0.4 | **7 天收敛 soak** | Grafana 加"多节点头哈希一致性"告警（分叉 = 立即报警，不再靠人工发现）|
| 0.5 | **部署 T2–T8 + 重部署全部合约** | DEX/NFT/Bridge/qUSD/DeFi 合约地址全换 → 同步更新各前端 env、41 号文档、faucet |

**出口门（硬性）**：连续 7 天 3 节点同高度同哈希；矿工 proof 被接受；explorer 数据一致。**不过此门，后续所有 Phase 不启动。**

**工作量**：Claude session 约 5–8 小时（审查 1–2、修复 2–3、reset+部署+验证 2–3）。墙钟约 1.5–2 周，soak 7 天占大头。

---

## Phase 1 — 经济自洽（Gap C 收尾，与 Phase 0 并行）

模型 v2 已存在（见 §0），本 Phase 是**收尾**而非从零建模。纯离线，**立即可启动**。

| # | 工作项 | 说明 |
|---|--------|------|
| 1.1 | **模型刷新** | 用 8 周 snapshots.jsonl 实测数据 + reset 后新链参数刷新 model.py 输出；补 n = [10, 100, 1000] 矿工规模敏感性和 year-0 保本点表 |
| 1.2 | **主网参数草案** | 初始通胀率（emission 减半表已在协议常量里）、奖励分配曲线、质押门槛、slashing 阈值（对照 03-TOKENOMICS 与 12-VALIDATOR-ALLOCATION 修订）|
| 1.3 | **发出外部审查** | REVIEW-REQUEST.md + OUTREACH-POSTS.md 都写好了，卡在"发出"这一步——发帖、约人、付 $300/45min，做 1–2 场 |

**出口门**：刷新后的模型维持"条件性通过"且外部 review 无重大逻辑漏洞。
**放弃门**：若刷新后结论恶化为"币价 > $10 才有人跑"→ 去中心化矿工路线经济不成立，转向纯推理 API 定位（链保留但不推矿工招募）。

**工作量**：Claude session 约 1–2 小时（模型刷新+参数草案）。1.3 发帖约人是**人工事项，时长不在 Claude 控制内**——这是 Gap C 目前唯一真正的卡点。

---

## Phase 2 — 外部闭环验证（Gap A + B，Phase 0/1 双过门后启动）

42 号文档的判据在此**重新计时**：A/B 并行，8 周窗口。

### 2A. Miner Onboarding（供给侧）

| # | 工作项 |
|---|--------|
| 2A.1 | 先修 MINER-ONBOARDING-REVIEW.md 的 2 个已知 bug：`start-miner.sh` 下载源指向 `qfc-miner` repo（而非 qfc-core）；版本漂移端到端验证 |
| 2A.2 | miner 发版对齐 reset 后的链协议（旧 binary 必然失效——genesis 换了），重建 9 平台 binary；然后 clean VPS 按 README 全流程自测，成功判据 = explorer 上看到该地址的推理证明 |
| 2A.3 | landing page（miner.qfc.network）：一屏文案 + `curl \| sh` + 收益估算器（直接引用 Phase 1 模型）|
| 2A.4 | 矿工首日 dashboard：explorer `/miner/[address]` 页（proof 数、累计奖励）|
| 2A.5 | 曝光：Twitter + Show HN + 相关 Discord/TG——**人工事项**（发帖、答疑、社区运营）|

### 2B. Inference Demand（需求侧）

| # | 工作项 |
|---|--------|
| 2B.1 | 公开推理 REST API（api.qfc.network/v1/inference，Traefik + rate limit + API key + requests_per_day 指标）——qfc-inference-router 已有底子 |
| 2B.2 | SDK snippet：JS/Python 各 ≤20 行完成"调用 + 拿结果 + 验证证明" |
| 2B.3 | **差异化 demo**：1 分钟讲清"可验证推理"的一个具体场景（候选：Agent 决策审计、链游 AI 公平性、内容审核可追溯）。这是给陌生人看的第一件东西 |
| 2B.4 | 5 个 use case 访谈提纲 + 找 3 个外部开发者聊——**人工事项** |

### 判据（修正 42 的可测性问题）

- **8 周门**：≥ 3 个外部矿工（不同 IP 段 + 不同注册渠道，排除 sybil）连续 7 天产证明；≥ 1 个外部调用者（非团队 API key 有持续调用）。
- **12 周门**：≥ 10 矿工、≥ 3 调用者、1 个能打动陌生人的 demo → 宣告 PMF 初验，进入 Phase 3。
- **kill 门**：8 周零外部矿工且零 onboarding 询问 → 矿工路线关停，执行 Phase 1 的纯 API 备选定位；8 周零外部调用 → 需求端无 PMF，主网无限期搁置。
- 测量先行：landing 页埋点、API per-key 指标、矿工地址注册渠道标记——**判据用到的每个数字先定义采集方式再开跑**。

**工作量**：Claude session 约 10–14 小时（2A 约 5–6、2B 约 5–8）。墙钟 8–12 周，瓶颈是外部采用信号，不是开发。

---

## Phase 3 — 主网准备（仅当 12 周门通过）

先列清单不展开（到时单独出详细计划）：

1. **安全**：合约审计（外部，数周墙钟+费用）、共识/节点代码审计、bug bounty
2. **AI-V3 节点集成**：Feature A 的 apply_settlement 接真实链状态、P2P 广播、N-of-M 操作员共识、VRF 采样熵（qfc-ai-coordinator 里已全部标记）
3. **B-2 分片推理 build**：门控在"跨区域矿工的真实 RTT/BW 重跑 calculator"——Phase 2 招到多区域矿工后自然解锁
4. **性能**：T1 profiling 发现的 BLAKE3 portable backend、sync-log 写放大；向 500k TPS 目标做基准测试
5. **主网参数定稿**：Phase 1 草案 + 测试网实测数据修订；genesis 仪式、validator 分配（12 号文档）
6. **治理最低集**：升级机制、紧急暂停、governance proposal_id 绑定 model_info（B-1 遗留的主网前必修项）

**工作量**：Claude session 约 15–25 小时；外部审计为墙钟主导——**人工事项（选审计商、付费、排期）**。

---

## 3. 并行与依赖总图

```
now ──────────────────────────────────────────────────────▶
Phase 0 链能跑 ████████░░ (1.5–2 周，soak 占大头)
Phase 1 经济模型 ██████░░ (与 P0 并行；外部 review 排期在你)
Phase 2 A+B          ░░████████████████ (8–12 周，双过门后启动)
Phase 3 主网                          ░░░░░░████ (仅 PMF 后)
冻结区: DeFi 新功能 / NFT·游戏前端 / Bridge 扩链 / UI 打磨 ──全程冻结──
```

**冻结纪律**（承 42）：任何 PR 先问"这在推进当前 Phase 吗？"不是 → 延后。唯一例外：AgentHub 若被选为 2B.3 demo 载体。

---

## 4. 治理节奏

- **周更**：每周日在本文档 §5 追加各 Phase 一段进展（42 的教训：写了制度不执行等于没有——这条本身进周更检查）。
- **门禁决策**：每个出口门/kill 门到期时,单独开 session 做判定并记录在 §5，**不允许沉默滑过**。
- **42 号文档**：补写 T+12 判定（"窗口被共识分叉吞没、判据未被测试、按 44 号重置"），然后归档只读。

---

## 5. 进展日志

*(每周日追加)*

- **2026-07-04**：本文档创建。盘点修正：Gap C 模型 v2 + 8 周快照已存在（条件性通过），Gap A 审查已做（2 bug 未修），Gap B 未动。Phase 0 待启动（第 6 缺陷未修，测试网仍分叉于 7ce54c5）；Phase 1 只剩模型刷新 + 发出外部 review。
