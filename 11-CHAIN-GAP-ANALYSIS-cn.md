# QFC 链差距分析（设计 vs. 实现）

最后更新: 2026-02-02

本文档总结了 QFC 设计文档与 `qfc-core` 代码轻量扫描之间的高层差距分析，旨在为核心链工作的优先级排序提供规划参考。

代码扫描范围（轻量）:
- qfc-core/crates/qfc-consensus
- qfc-core/crates/qfc-node
- qfc-core/crates/qfc-mempool
- qfc-core/crates/qfc-rpc
- qfc-core/crates/qfc-network（浅层）

说明:
- 这不是完整审计。仅用于突出可能的差距和风险。
- 某些项目可能已在其他位置实现；应视为"需要验证"。

---

## 按领域汇总

### 共识 (PoC)
设计意图 (docs/02-CONSENSUS-MECHANISM.md):
- 多维度贡献评分与动态权重
- 基于 VRF 的出块者选择
- 加权投票终局性 (2/3)
- 针对不当行为的罚没机制与明确惩罚

代码中观察到的:
- PoC 评分 + 动态权重已在 `qfc-consensus` 中实现。
- VRF 选择和加权投票/终局性逻辑已存在。
- 罚没逻辑存在于共识引擎的内存中。
- 证据处理存在于 `qfc-node` 同步流程中。

主要差距:
- 罚没和惩罚未明确持久化到链上状态（存储）。
- 用于评分的指标（延迟、存储、计算）缺乏清晰的、可验证的链上证明。

### 节点 / 网络
设计意图 (docs/01-BLOCKCHAIN-DESIGN.md):
- 基于 libp2p 的 P2P 网络（GossipSub/Kademlia/Req-Resp）
- 同步模式: 全量/快速/轻量
- 交易池: nonce、gas 价格排序、过期机制

代码中观察到的:
- P2P 和同步管理器已存在；区块同步为基础实现。
- 交易池排序已存在；nonce 检查标注了 TODO 需关联状态。

主要差距:
- 快速/轻量同步未实现（仅有区块同步）。
- 交易池 nonce 验证未关联状态。
- P2P DoS 防护/节点信誉机制不可见。

### 治理
设计意图:
- 参数治理和提案生命周期

代码中观察到的:
- 未找到治理模块或链上参数更新工作流。

主要差距:
- 提案、投票、执行流水线。
- 链上参数更新和紧急控制机制。

### 安全
设计意图:
- 针对多种违规行为的罚没
- 长程攻击和无利害关系攻击的防御
- 密钥管理和运营安全保障

代码中观察到的:
- 罚没函数已存在但似乎仅在内存中。
- 未发现显式的检查点/弱主观性机制。

主要差距:
- 链上罚没状态转换。
- 检查点和针对长程攻击的重放保护。

### 生态 / RPC
设计意图:
- 兼容以太坊的 JSON-RPC + QFC 扩展
- 用于日志/新区块头/待处理交易的 WebSocket 订阅

代码中观察到的:
- HTTP RPC 已实现；eth + qfc 命名空间已存在。
- 未发现 WebSocket 订阅功能。

主要差距:
- 用于日志/新区块头/待处理交易的 WS 订阅。
- 核心 RPC 中的过滤器 API。

---

## 差距矩阵（高层）

| 领域 | 需求 | 状态 | 证据 | 优先级 |
|------|------|------|------|--------|
| 共识 | PoC 评分 + 动态权重 | 部分完成 | qfc-consensus 评分/NetworkState | P1 |
| 共识 | VRF 选择 & 加权终局性 | 已存在 | qfc-consensus 引擎 | P0 |
| 共识 | 罚没持久化到链上 | 缺失 | 仅内存罚没 | P0 |
| 节点 | 快速/轻量同步 | 缺失 | sync.rs 基础区块同步 | P0 |
| 节点 | 交易池 nonce vs 状态 | 缺失 | mempool 中的 TODO | P0 |
| 网络 | DoS/节点评分 | 缺失 | 扫描中未发现 | P1 |
| 治理 | 提案/投票/执行 | 缺失 | 未找到模块 | P0 |
| 安全 | 长程攻击检查点 | 缺失 | 未发现 | P1 |
| RPC | WS 订阅 | 缺失 | 仅有 HTTP | P1 |
| RPC | eth 过滤器 API | 部分完成 | 核心 RPC 中未找到 | P1 |

---

## 建议的 P0 工作清单

1) 交易池 nonce 验证关联状态
2) 实现快速同步（快照 + 状态裁剪）
3) 罚没作为链上状态转换（余额/监禁持久化）
4) 参数更新的最小治理流程

## 建议的 P1 工作清单

1) WS 订阅（新区块头/日志/待处理交易）
2) 节点信誉 / P2P 速率限制
3) 检查点 / 弱主观性

---

## 参考资料

设计文档:
- qfc-design/01-BLOCKCHAIN-DESIGN.md
- qfc-design/02-CONSENSUS-MECHANISM.md
- qfc-design/03-TOKENOMICS.md

代码扫描路径:
- qfc-core/crates/qfc-consensus
- qfc-core/crates/qfc-node
- qfc-core/crates/qfc-mempool
- qfc-core/crates/qfc-rpc
