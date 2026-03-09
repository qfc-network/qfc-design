# 05-BLOCK-EXPLORER.md — QFC 区块浏览器（MVP 设计）

> 目标：先做一个能用的 Explorer（读链、可搜索、可定位问题），再逐步加统计与高级分析。

## 0. 范围与非目标

### MVP 必须有
- 最新区块列表（分页）
- 最新交易列表（分页）
- 区块详情页（含交易列表）
- 交易详情页
- 地址详情页（余额/nonce/交易历史）
- 全局搜索框：支持 `blockHeight` / `blockHash` / `txHash` / `address`
- 基础 API（供前端调用）
- Indexer：把链数据写入 PostgreSQL（最小化可运行）

### MVP 不做（后续）
- 合约/事件索引、ABI 解码
- Token/NFT 资产视图
- 图表（TPS、Gas、活跃地址等）
- ElasticSearch（先用 Postgres + trigram/索引）
- 多链/多网络切换（先做 1 个 network）

---

## 1. 总体架构

### 1.1 组件
- **Frontend**：Next.js (App Router) + React + Tailwind
- **Backend API**：Node.js + Express（也可用 Next.js Route Handlers 一体化；MVP 建议直接一体化，减少组件）
- **Indexer**：Rust（轮询/订阅 RPC，落库）
- **DB**：PostgreSQL（MVP 只用 PG）

### 1.2 数据流
1) Indexer 从 QFC 节点 RPC 拉取新区块/交易
2) 写入 Postgres（blocks/txs/address_stats）
3) 前端通过 API 查询 Postgres

---

## 2. RPC 依赖（假设/约定）

> 具体方法名可按 QFC RPC 实际落地调整；先定义 Explorer 所需的“能力”。

### 必需能力
- `getBlockNumber()` → 最新高度
- `getBlockByNumber(height, includeTxs)`
- `getBlockByHash(hash, includeTxs)`
- `getTransactionByHash(txHash)`
- `getTransactionReceipt(txHash)`（可选，若有状态/日志）
- `getBalance(address, blockTag)`
- `getNonce(address, blockTag)`（或 account nonce）

---

## 3. 数据库（PostgreSQL）

### 3.1 blocks
```sql
CREATE TABLE blocks (
  id BIGSERIAL PRIMARY KEY,
  height BIGINT NOT NULL UNIQUE,
  hash TEXT NOT NULL UNIQUE,
  parent_hash TEXT,
  timestamp TIMESTAMPTZ NOT NULL,
  proposer TEXT,
  tx_count INT NOT NULL DEFAULT 0,
  size_bytes INT,
  raw JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX blocks_timestamp_idx ON blocks (timestamp DESC);
```

### 3.2 transactions
```sql
CREATE TABLE transactions (
  id BIGSERIAL PRIMARY KEY,
  hash TEXT NOT NULL UNIQUE,
  block_height BIGINT NOT NULL,
  block_hash TEXT,
  tx_index INT,
  from_addr TEXT,
  to_addr TEXT,
  value_numeric NUMERIC(78,0),
  fee_numeric NUMERIC(78,0),
  nonce BIGINT,
  status SMALLINT, -- 1 success, 0 fail, null unknown
  timestamp TIMESTAMPTZ NOT NULL,
  raw JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT fk_block_height FOREIGN KEY (block_height) REFERENCES blocks(height)
);

CREATE INDEX txs_block_height_idx ON transactions (block_height DESC);
CREATE INDEX txs_from_idx ON transactions (from_addr);
CREATE INDEX txs_to_idx ON transactions (to_addr);
CREATE INDEX txs_timestamp_idx ON transactions (timestamp DESC);
```

### 3.3 address_stats（MVP：可选，但对地址页性能很有帮助）
```sql
CREATE TABLE address_stats (
  address TEXT PRIMARY KEY,
  last_seen_block BIGINT,
  last_seen_at TIMESTAMPTZ,
  tx_sent BIGINT NOT NULL DEFAULT 0,
  tx_received BIGINT NOT NULL DEFAULT 0,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX address_stats_last_seen_idx ON address_stats (last_seen_at DESC);
```

### 3.4 搜索（MVP）
- `blockHeight`：纯数字 → 直接查 blocks.height
- `hash`：长度/前缀判断（0x? + 64 hex）
- `address`：按地址规则（例如 0x + 40 hex 或 qfc1...）
- 先不做模糊搜索

---

## 4. API 设计（MVP）

> 路径可放在 Next Route Handlers：`/api/...`

- `GET /api/health`
- `GET /api/blocks?limit=20&cursor=<height>`
- `GET /api/blocks/:height`
- `GET /api/blocks/hash/:hash`
- `GET /api/txs?limit=20&cursor=<id|time>`
- `GET /api/txs/:hash`
- `GET /api/address/:address`
- `GET /api/address/:address/txs?limit=20&cursor=<id|time>`
- `GET /api/search?q=...` → 返回 `{type, redirectUrl}`

返回字段原则：
- 列表页返回“轻字段”（hash/height/time/from/to/value/status）
- 详情页返回 raw JSONB + 已解析常用字段

---

## 5. 前端页面（MVP）

### 5.1 首页
- 最新区块（Top N）
- 最新交易（Top N）
- 搜索框（置顶）

### 5.2 Blocks 列表
- 列：height / time / tx_count / proposer / hash(截断)

### 5.3 Block 详情
- 基本信息：height/hash/parent/timestamp/proposer
- 交易列表（分页）

### 5.4 Transactions 列表
- 列：hash / block_height / time / from / to / value / status

### 5.5 Tx 详情
- 基本信息：hash / block_height / index / from / to / value / fee / nonce / status
- raw JSON（折叠展示）

### 5.6 Address 详情
- address
- balance（可实时 RPC 拉，也可后续缓存）
- nonce
- 交易历史（发出/收到混合列表）

---

## 6. Indexer（Rust）MVP 方案

### 6.1 同步策略
- 启动时：
  1) 读 DB 中 `max(blocks.height)` 作为 `startHeight`
  2) 从 `startHeight+1` 追到 `latestHeight`
- 运行中：每 X 秒轮询 `latestHeight`，有新区块就拉取并写入

### 6.2 回滚/分叉（MVP 简化）
- 先假设短期无深分叉（或测试网单分叉）
- 记录 `parent_hash`，如果发现 `blocks[height-1].hash != parent_hash`：
  - 标记异常并停止（打印告警），人工处理
- 后续增强：自动回滚到共同祖先

### 6.3 幂等写入
- blocks/txs 使用 `UNIQUE(hash)` / `UNIQUE(height)`
- Upsert：`INSERT ... ON CONFLICT DO NOTHING/UPDATE`

---

## 7. 目录结构建议（qfc-explorer 仓库）

```
qfc-explorer/
  apps/
    web/              # Next.js
  packages/
    db/               # SQL migrations + db client
    types/            # shared types
  services/
    indexer/          # Rust indexer
  docker-compose.yml
  README.md
```

MVP 更简单也可以：
- 先直接 `qfc-explorer/` 下一个 Next.js + 一个 indexer 文件夹。

---

## 8. 里程碑（建议）

### Milestone 0（半天）
- Next.js 初始化 + 首页空壳
- Postgres 连接与 migration 框架

### Milestone 1（1-2 天）
- Rust indexer：blocks + txs 落库
- blocks/txs 列表 + 详情页跑通

### Milestone 2（1 天）
- address 页 + search 功能
- 部署：docker compose 一键起（web + postgres + indexer）

---

## 9. 需要你确认的两件事（实现前）
1) QFC 地址格式：`0x...` 还是 `qfc1...`？（影响 search/校验/展示）
2) QFC RPC 具体方法名/字段：目前按“能力假设”，实现时需对齐实际 RPC。
