# 05-BLOCK-EXPLORER.md — QFC Block Explorer (MVP Design)

> Goal: Build a functional Explorer first (read chain data, searchable, able to pinpoint issues), then gradually add statistics and advanced analytics.

## 0. Scope and Non-Goals

### MVP Must-Haves
- Latest block list (paginated)
- Latest transaction list (paginated)
- Block detail page (with transaction list)
- Transaction detail page
- Address detail page (balance/nonce/transaction history)
- Global search bar: supports `blockHeight` / `blockHash` / `txHash` / `address`
- Basic API (for frontend consumption)
- Indexer: write chain data into PostgreSQL (minimum viable)

### MVP Non-Goals (Future Work)
- Contract/event indexing, ABI decoding
- Token/NFT asset views
- Charts (TPS, Gas, active addresses, etc.)
- ElasticSearch (use Postgres + trigram/indexes first)
- Multi-chain/multi-network switching (single network first)

---

## 1. Overall Architecture

### 1.1 Components
- **Frontend**: Next.js (App Router) + React + Tailwind
- **Backend API**: Node.js + Express (alternatively, Next.js Route Handlers for an all-in-one approach; recommended for MVP to reduce component count)
- **Indexer**: Rust (polling/subscribing to RPC, persisting to database)
- **DB**: PostgreSQL (MVP uses PG only)

### 1.2 Data Flow
1) Indexer fetches new blocks/transactions from QFC node RPC
2) Writes to Postgres (blocks/txs/address_stats)
3) Frontend queries Postgres via API

---

## 2. RPC Dependencies (Assumptions/Conventions)

> Specific method names may be adjusted based on the actual QFC RPC implementation; this defines the "capabilities" the Explorer requires.

### Required Capabilities
- `getBlockNumber()` → latest height
- `getBlockByNumber(height, includeTxs)`
- `getBlockByHash(hash, includeTxs)`
- `getTransactionByHash(txHash)`
- `getTransactionReceipt(txHash)` (optional, if status/logs are available)
- `getBalance(address, blockTag)`
- `getNonce(address, blockTag)` (or account nonce)

---

## 3. Database (PostgreSQL)

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

### 3.3 address_stats (MVP: optional, but very helpful for address page performance)
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

### 3.4 Search (MVP)
- `blockHeight`: pure number → query blocks.height directly
- `hash`: determine by length/prefix (0x? + 64 hex)
- `address`: match by address format (e.g., 0x + 40 hex or qfc1...)
- No fuzzy search for now

---

## 4. API Design (MVP)

> Paths can be placed in Next Route Handlers: `/api/...`

- `GET /api/health`
- `GET /api/blocks?limit=20&cursor=<height>`
- `GET /api/blocks/:height`
- `GET /api/blocks/hash/:hash`
- `GET /api/txs?limit=20&cursor=<id|time>`
- `GET /api/txs/:hash`
- `GET /api/address/:address`
- `GET /api/address/:address/txs?limit=20&cursor=<id|time>`
- `GET /api/search?q=...` → returns `{type, redirectUrl}`

Response field principles:
- List pages return "lightweight fields" (hash/height/time/from/to/value/status)
- Detail pages return raw JSONB + commonly parsed fields

---

## 5. Frontend Pages (MVP)

### 5.1 Home Page
- Latest blocks (Top N)
- Latest transactions (Top N)
- Search bar (pinned to top)

### 5.2 Blocks List
- Columns: height / time / tx_count / proposer / hash (truncated)

### 5.3 Block Detail
- Basic info: height/hash/parent/timestamp/proposer
- Transaction list (paginated)

### 5.4 Transactions List
- Columns: hash / block_height / time / from / to / value / status

### 5.5 Transaction Detail
- Basic info: hash / block_height / index / from / to / value / fee / nonce / status
- Raw JSON (collapsible)

### 5.6 Address Detail
- address
- balance (can be fetched in real-time via RPC, or cached later)
- nonce
- Transaction history (mixed list of sent/received)

---

## 6. Indexer (Rust) MVP Approach

### 6.1 Sync Strategy
- On startup:
  1) Read `max(blocks.height)` from DB as `startHeight`
  2) Catch up from `startHeight+1` to `latestHeight`
- During runtime: poll `latestHeight` every X seconds, fetch and persist new blocks when available

### 6.2 Reorgs/Forks (MVP Simplified)
- Assume no deep forks in the short term (or single fork on testnet)
- Record `parent_hash`; if `blocks[height-1].hash != parent_hash` is detected:
  - Flag the anomaly and halt (print warning), handle manually
- Future enhancement: automatic rollback to common ancestor

### 6.3 Idempotent Writes
- blocks/txs use `UNIQUE(hash)` / `UNIQUE(height)`
- Upsert: `INSERT ... ON CONFLICT DO NOTHING/UPDATE`

---

## 7. Suggested Directory Structure (qfc-explorer repository)

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

For a simpler MVP:
- Just have a single `qfc-explorer/` directory with one Next.js folder and one indexer folder.

---

## 8. Milestones (Suggested)

### Milestone 0 (Half Day)
- Next.js initialization + home page shell
- Postgres connection and migration framework

### Milestone 1 (1-2 Days)
- Rust indexer: blocks + txs persisted to database
- Blocks/txs list + detail pages working end-to-end

### Milestone 2 (1 Day)
- Address page + search functionality
- Deployment: docker compose one-click startup (web + postgres + indexer)

---

## 9. Two Items to Confirm Before Implementation
1) QFC address format: `0x...` or `qfc1...`? (Affects search/validation/display)
2) QFC RPC specific method names/fields: currently based on "capability assumptions"; need to align with actual RPC during implementation.
