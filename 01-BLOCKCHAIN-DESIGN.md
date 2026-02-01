# QFC Blockchain Core Design

## 概述

本文档描述 QFC 区块链核心引擎（`qfc-core`）的技术设计，包括数据结构、网络层、状态管理、存储和 RPC API。

## 技术栈

| 组件 | 技术选型 | 说明 |
|------|----------|------|
| 语言 | Rust | 高性能、内存安全 |
| 网络 | libp2p | 模块化 P2P 网络库 |
| 状态存储 | RocksDB | 高性能 KV 存储 |
| 序列化 | borsh / SSZ | 高效二进制序列化 |
| 加密 | ed25519 | 签名算法 |
| 哈希 | Blake3 | 高速哈希函数 |

## 数据结构

### 区块（Block）

```rust
/// 区块头
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct BlockHeader {
    /// 区块版本号
    pub version: u32,

    /// 区块高度
    pub number: u64,

    /// 父区块哈希
    pub parent_hash: Hash,

    /// 状态根（Merkle Patricia Trie）
    pub state_root: Hash,

    /// 交易根（Merkle Tree）
    pub transactions_root: Hash,

    /// 收据根（Merkle Tree）
    pub receipts_root: Hash,

    /// 区块生产者地址
    pub producer: Address,

    /// 生产者贡献分数
    pub contribution_score: u64,

    /// VRF 证明
    pub vrf_proof: VrfProof,

    /// 时间戳（毫秒）
    pub timestamp: u64,

    /// Gas 限制
    pub gas_limit: u64,

    /// 已使用 Gas
    pub gas_used: u64,

    /// 额外数据（最大32字节）
    pub extra_data: Vec<u8>,
}

/// 完整区块
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Block {
    pub header: BlockHeader,
    pub transactions: Vec<Transaction>,
    pub votes: Vec<Vote>,
    pub signature: Signature,
}

impl Block {
    /// 计算区块哈希
    pub fn hash(&self) -> Hash {
        blake3::hash(&self.header.to_bytes())
    }

    /// 验证区块签名
    pub fn verify_signature(&self) -> bool {
        let msg = self.hash();
        verify_signature(&self.header.producer, &msg, &self.signature)
    }
}
```

### 交易（Transaction）

```rust
/// 交易类型
#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum TransactionType {
    /// 普通转账
    Transfer,
    /// 合约创建
    ContractCreate,
    /// 合约调用
    ContractCall,
    /// 质押
    Stake,
    /// 取消质押
    Unstake,
    /// 验证者注册
    ValidatorRegister,
    /// 验证者退出
    ValidatorExit,
}

/// 交易
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Transaction {
    /// 交易类型
    pub tx_type: TransactionType,

    /// 链 ID（防止重放攻击）
    pub chain_id: u64,

    /// 发送者 nonce
    pub nonce: u64,

    /// 接收者地址（合约创建时为 None）
    pub to: Option<Address>,

    /// 转账金额（单位：wei）
    pub value: U256,

    /// 调用数据
    pub data: Vec<u8>,

    /// Gas 限制
    pub gas_limit: u64,

    /// Gas 价格（单位：wei）
    pub gas_price: U256,

    /// 签名
    pub signature: Signature,
}

impl Transaction {
    /// 计算交易哈希
    pub fn hash(&self) -> Hash {
        blake3::hash(&self.to_bytes_without_signature())
    }

    /// 恢复发送者地址
    pub fn recover_sender(&self) -> Result<Address, Error> {
        let msg = self.hash();
        recover_address(&msg, &self.signature)
    }

    /// 验证交易
    pub fn verify(&self) -> Result<(), Error> {
        // 1. 验证签名
        let sender = self.recover_sender()?;

        // 2. 验证 chain_id
        if self.chain_id != CHAIN_ID {
            return Err(Error::InvalidChainId);
        }

        // 3. 验证 gas
        if self.gas_limit < MINIMUM_GAS {
            return Err(Error::GasTooLow);
        }

        Ok(())
    }
}
```

### 账户（Account）

```rust
/// 账户类型
#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum AccountType {
    /// 外部账户（用户）
    EOA,
    /// 合约账户
    Contract,
    /// 验证者账户
    Validator,
}

/// 账户状态
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Account {
    /// 账户类型
    pub account_type: AccountType,

    /// 余额
    pub balance: U256,

    /// Nonce（防止重放攻击）
    pub nonce: u64,

    /// 代码哈希（合约账户）
    pub code_hash: Option<Hash>,

    /// 存储根（合约账户）
    pub storage_root: Option<Hash>,

    /// 质押金额（验证者）
    pub stake: Option<U256>,

    /// 贡献分数（验证者）
    pub contribution_score: Option<u64>,
}

impl Account {
    pub fn new_eoa() -> Self {
        Self {
            account_type: AccountType::EOA,
            balance: U256::zero(),
            nonce: 0,
            code_hash: None,
            storage_root: None,
            stake: None,
            contribution_score: None,
        }
    }
}
```

### 收据（Receipt）

```rust
/// 交易收据
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Receipt {
    /// 交易哈希
    pub tx_hash: Hash,

    /// 交易索引（在区块中的位置）
    pub tx_index: u32,

    /// 执行状态
    pub status: ReceiptStatus,

    /// 累计 Gas 使用量
    pub cumulative_gas_used: u64,

    /// 日志
    pub logs: Vec<Log>,

    /// 日志 Bloom 过滤器
    pub logs_bloom: Bloom,

    /// 合约地址（如果是合约创建）
    pub contract_address: Option<Address>,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum ReceiptStatus {
    Success,
    Failure(String),
    OutOfGas,
    Reverted,
}

/// 事件日志
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Log {
    pub address: Address,
    pub topics: Vec<Hash>,
    pub data: Vec<u8>,
}
```

## 网络层（P2P）

### 架构

```
┌─────────────────────────────────────────────────────────┐
│                    Application Layer                     │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐   │
│  │ Block Sync  │ │ Tx Gossip   │ │ Consensus Msgs  │   │
│  └─────────────┘ └─────────────┘ └─────────────────┘   │
└─────────────────────────┬───────────────────────────────┘
                          │
┌─────────────────────────┴───────────────────────────────┐
│                    libp2p Layer                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐   │
│  │ GossipSub   │ │ Kademlia    │ │ Request/Response│   │
│  │ (pub/sub)   │ │ (DHT)       │ │ (sync)          │   │
│  └─────────────┘ └─────────────┘ └─────────────────┘   │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐   │
│  │ Identify    │ │ Ping        │ │ Noise           │   │
│  │ (handshake) │ │ (health)    │ │ (encryption)    │   │
│  └─────────────┘ └─────────────┘ └─────────────────┘   │
└─────────────────────────┬───────────────────────────────┘
                          │
┌─────────────────────────┴───────────────────────────────┐
│                    Transport Layer                       │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐   │
│  │ TCP         │ │ QUIC        │ │ WebSocket       │   │
│  └─────────────┘ └─────────────┘ └─────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### 节点配置

```rust
/// P2P 网络配置
#[derive(Clone, Debug)]
pub struct NetworkConfig {
    /// 监听地址
    pub listen_addresses: Vec<Multiaddr>,

    /// 引导节点
    pub bootnodes: Vec<Multiaddr>,

    /// 最大入站连接数
    pub max_inbound_peers: u32,

    /// 最大出站连接数
    pub max_outbound_peers: u32,

    /// 节点私钥
    pub node_key: Keypair,
}

impl Default for NetworkConfig {
    fn default() -> Self {
        Self {
            listen_addresses: vec![
                "/ip4/0.0.0.0/tcp/30303".parse().unwrap(),
                "/ip4/0.0.0.0/udp/30303/quic".parse().unwrap(),
            ],
            bootnodes: vec![],
            max_inbound_peers: 50,
            max_outbound_peers: 25,
            node_key: Keypair::generate_ed25519(),
        }
    }
}
```

### GossipSub 主题

```rust
/// 网络消息主题
pub enum Topic {
    /// 新区块广播
    NewBlocks,
    /// 新交易广播
    NewTransactions,
    /// 共识投票
    ConsensusVotes,
    /// 验证者消息
    ValidatorMessages,
}

impl Topic {
    pub fn to_string(&self) -> String {
        match self {
            Topic::NewBlocks => "/qfc/blocks/1".to_string(),
            Topic::NewTransactions => "/qfc/txs/1".to_string(),
            Topic::ConsensusVotes => "/qfc/votes/1".to_string(),
            Topic::ValidatorMessages => "/qfc/validator/1".to_string(),
        }
    }
}
```

### 区块同步

```rust
/// 区块同步请求
#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum SyncRequest {
    /// 获取区块头
    GetHeaders {
        start_number: u64,
        count: u32,
    },

    /// 获取完整区块
    GetBlocks {
        hashes: Vec<Hash>,
    },

    /// 获取状态
    GetState {
        root: Hash,
        paths: Vec<Vec<u8>>,
    },
}

/// 同步状态机
pub struct SyncManager {
    /// 当前同步模式
    mode: SyncMode,

    /// 本地最高区块
    local_head: u64,

    /// 网络最高区块
    network_head: u64,

    /// 待同步区块队列
    pending_blocks: VecDeque<Hash>,
}

#[derive(Clone, Debug)]
pub enum SyncMode {
    /// 完整同步（从创世区块）
    Full,
    /// 快速同步（只下载状态）
    Fast,
    /// 轻同步（只验证区块头）
    Light,
    /// 已同步完成
    Synced,
}
```

## 状态管理

### Merkle Patricia Trie

```rust
/// 状态树节点类型
#[derive(Clone, Debug)]
pub enum TrieNode {
    /// 空节点
    Empty,

    /// 叶子节点
    Leaf {
        key: NibbleSlice,
        value: Vec<u8>,
    },

    /// 扩展节点
    Extension {
        key: NibbleSlice,
        child: Hash,
    },

    /// 分支节点
    Branch {
        children: [Option<Hash>; 16],
        value: Option<Vec<u8>>,
    },
}

/// 状态数据库
pub struct StateDB {
    /// 底层存储
    db: Arc<RocksDB>,

    /// 状态缓存
    cache: LruCache<Hash, TrieNode>,

    /// 当前状态根
    root: Hash,
}

impl StateDB {
    /// 获取账户
    pub fn get_account(&self, address: &Address) -> Option<Account> {
        let key = keccak256(address);
        self.get(&key).map(|bytes| Account::from_bytes(&bytes))
    }

    /// 更新账户
    pub fn set_account(&mut self, address: &Address, account: &Account) {
        let key = keccak256(address);
        self.set(&key, &account.to_bytes());
    }

    /// 获取合约存储
    pub fn get_storage(&self, address: &Address, slot: &U256) -> U256 {
        let account = self.get_account(address)?;
        let storage_root = account.storage_root?;

        let storage_trie = self.open_trie(storage_root);
        let key = keccak256(&slot.to_bytes());

        storage_trie.get(&key)
            .map(|bytes| U256::from_bytes(&bytes))
            .unwrap_or(U256::zero())
    }

    /// 提交状态变更，返回新的状态根
    pub fn commit(&mut self) -> Hash {
        self.root = self.trie.commit();
        self.root
    }
}
```

### 状态转换

```rust
/// 状态转换引擎
pub struct StateTransition {
    state: StateDB,
    receipts: Vec<Receipt>,
    logs: Vec<Log>,
    gas_used: u64,
}

impl StateTransition {
    /// 执行交易
    pub fn apply_transaction(
        &mut self,
        tx: &Transaction,
    ) -> Result<Receipt, Error> {
        // 1. 验证交易
        tx.verify()?;

        // 2. 检查发送者余额
        let sender = tx.recover_sender()?;
        let sender_account = self.state.get_account(&sender)
            .ok_or(Error::AccountNotFound)?;

        let total_cost = tx.value + tx.gas_limit * tx.gas_price;
        if sender_account.balance < total_cost {
            return Err(Error::InsufficientBalance);
        }

        // 3. 检查 nonce
        if sender_account.nonce != tx.nonce {
            return Err(Error::InvalidNonce);
        }

        // 4. 扣除 gas 预付
        self.state.sub_balance(&sender, tx.gas_limit * tx.gas_price);
        self.state.increment_nonce(&sender);

        // 5. 执行交易
        let result = match tx.tx_type {
            TransactionType::Transfer => {
                self.execute_transfer(tx)
            },
            TransactionType::ContractCreate => {
                self.execute_contract_create(tx)
            },
            TransactionType::ContractCall => {
                self.execute_contract_call(tx)
            },
            TransactionType::Stake => {
                self.execute_stake(tx)
            },
            _ => unimplemented!(),
        };

        // 6. 退还多余 gas
        let gas_refund = (tx.gas_limit - result.gas_used) * tx.gas_price;
        self.state.add_balance(&sender, gas_refund);

        // 7. 生成收据
        let receipt = Receipt {
            tx_hash: tx.hash(),
            tx_index: self.receipts.len() as u32,
            status: result.status,
            cumulative_gas_used: self.gas_used + result.gas_used,
            logs: result.logs,
            logs_bloom: create_bloom(&result.logs),
            contract_address: result.contract_address,
        };

        self.gas_used += result.gas_used;
        self.receipts.push(receipt.clone());

        Ok(receipt)
    }

    /// 执行转账
    fn execute_transfer(&mut self, tx: &Transaction) -> ExecutionResult {
        let to = tx.to.ok_or(Error::MissingRecipient)?;
        let sender = tx.recover_sender()?;

        // 转账
        self.state.sub_balance(&sender, tx.value);
        self.state.add_balance(&to, tx.value);

        ExecutionResult {
            status: ReceiptStatus::Success,
            gas_used: 21000,  // 基础转账 gas
            logs: vec![],
            contract_address: None,
        }
    }
}
```

## 存储层

### RocksDB Schema

```rust
/// 数据库列族
pub enum ColumnFamily {
    /// 区块头
    BlockHeaders,
    /// 区块体
    BlockBodies,
    /// 交易
    Transactions,
    /// 收据
    Receipts,
    /// 状态（Merkle Patricia Trie 节点）
    State,
    /// 合约代码
    Code,
    /// 索引（交易哈希 -> 区块号）
    TxIndex,
    /// 元数据
    Metadata,
}

/// 存储键
pub enum StorageKey {
    /// 区块头：height -> BlockHeader
    BlockHeader(u64),
    /// 区块哈希索引：hash -> height
    BlockHashIndex(Hash),
    /// 区块体：height -> BlockBody
    BlockBody(u64),
    /// 交易：hash -> Transaction
    Transaction(Hash),
    /// 收据：hash -> Receipt
    Receipt(Hash),
    /// 状态节点：hash -> TrieNode
    StateNode(Hash),
    /// 合约代码：hash -> bytes
    Code(Hash),
    /// 最新区块高度
    LatestBlockNumber,
    /// 最新状态根
    LatestStateRoot,
}

/// 存储接口
pub trait Storage {
    /// 写入区块
    fn write_block(&self, block: &Block) -> Result<(), Error>;

    /// 读取区块头
    fn get_block_header(&self, number: u64) -> Option<BlockHeader>;

    /// 通过哈希读取区块
    fn get_block_by_hash(&self, hash: &Hash) -> Option<Block>;

    /// 读取交易
    fn get_transaction(&self, hash: &Hash) -> Option<Transaction>;

    /// 读取收据
    fn get_receipt(&self, hash: &Hash) -> Option<Receipt>;

    /// 批量写入
    fn write_batch(&self, batch: WriteBatch) -> Result<(), Error>;
}
```

### 存储优化

```rust
/// 存储配置
#[derive(Clone, Debug)]
pub struct StorageConfig {
    /// 数据目录
    pub data_dir: PathBuf,

    /// Block Cache 大小（MB）
    pub block_cache_size: usize,

    /// Write Buffer 大小（MB）
    pub write_buffer_size: usize,

    /// 最大打开文件数
    pub max_open_files: i32,

    /// 是否启用压缩
    pub enable_compression: bool,

    /// 状态剪枝深度（保留最近多少个区块的状态）
    pub state_pruning_depth: Option<u64>,
}

impl Default for StorageConfig {
    fn default() -> Self {
        Self {
            data_dir: PathBuf::from("./data"),
            block_cache_size: 512,      // 512 MB
            write_buffer_size: 64,      // 64 MB
            max_open_files: 1024,
            enable_compression: true,
            state_pruning_depth: Some(1000),  // 保留最近1000个区块
        }
    }
}
```

## 交易池（Mempool）

```rust
/// 交易池
pub struct Mempool {
    /// 待处理交易（按 gas price 排序）
    pending: BTreeMap<U256, Vec<Transaction>>,

    /// 按发送者分组（用于 nonce 检查）
    by_sender: HashMap<Address, Vec<Transaction>>,

    /// 交易哈希索引
    by_hash: HashMap<Hash, Transaction>,

    /// 配置
    config: MempoolConfig,
}

#[derive(Clone, Debug)]
pub struct MempoolConfig {
    /// 最大交易数
    pub max_size: usize,

    /// 单账户最大待处理交易数
    pub max_per_account: usize,

    /// 最低 gas price
    pub min_gas_price: U256,

    /// 交易过期时间（秒）
    pub tx_lifetime: u64,
}

impl Mempool {
    /// 添加交易
    pub fn add_transaction(&mut self, tx: Transaction) -> Result<(), Error> {
        // 1. 验证交易
        tx.verify()?;

        // 2. 检查 gas price
        if tx.gas_price < self.config.min_gas_price {
            return Err(Error::GasPriceTooLow);
        }

        // 3. 检查是否已存在
        let hash = tx.hash();
        if self.by_hash.contains_key(&hash) {
            return Err(Error::AlreadyKnown);
        }

        // 4. 检查账户交易数限制
        let sender = tx.recover_sender()?;
        let sender_txs = self.by_sender.entry(sender).or_default();
        if sender_txs.len() >= self.config.max_per_account {
            return Err(Error::AccountPoolFull);
        }

        // 5. 添加到池
        self.pending
            .entry(tx.gas_price)
            .or_default()
            .push(tx.clone());

        sender_txs.push(tx.clone());
        self.by_hash.insert(hash, tx);

        // 6. 如果超出大小限制，移除最低 gas price 的交易
        self.evict_if_needed();

        Ok(())
    }

    /// 选择交易打包进区块
    pub fn select_transactions(
        &self,
        max_gas: u64,
        max_count: usize,
    ) -> Vec<Transaction> {
        let mut selected = Vec::new();
        let mut gas_used = 0u64;

        // 按 gas price 从高到低选择
        for (_, txs) in self.pending.iter().rev() {
            for tx in txs {
                if selected.len() >= max_count {
                    break;
                }

                if gas_used + tx.gas_limit > max_gas {
                    continue;
                }

                // 验证 nonce 是否连续
                let sender = tx.recover_sender().unwrap();
                if self.is_valid_nonce(&sender, tx.nonce) {
                    selected.push(tx.clone());
                    gas_used += tx.gas_limit;
                }
            }
        }

        selected
    }

    /// 移除已打包的交易
    pub fn remove_transactions(&mut self, txs: &[Transaction]) {
        for tx in txs {
            let hash = tx.hash();
            self.by_hash.remove(&hash);

            let sender = tx.recover_sender().unwrap();
            if let Some(sender_txs) = self.by_sender.get_mut(&sender) {
                sender_txs.retain(|t| t.hash() != hash);
            }

            if let Some(price_txs) = self.pending.get_mut(&tx.gas_price) {
                price_txs.retain(|t| t.hash() != hash);
            }
        }
    }
}
```

## RPC API

### JSON-RPC 2.0 接口

```rust
/// RPC 服务器
pub struct RpcServer {
    /// 区块链状态
    chain: Arc<Chain>,

    /// 交易池
    mempool: Arc<RwLock<Mempool>>,

    /// 网络
    network: Arc<Network>,
}

/// RPC 方法
impl RpcServer {
    // ========== 账户相关 ==========

    /// 获取账户余额
    /// eth_getBalance(address, block_number) -> U256
    pub async fn get_balance(
        &self,
        address: Address,
        block: BlockNumber,
    ) -> Result<U256, RpcError> {
        let state = self.chain.state_at(block)?;
        Ok(state.get_balance(&address))
    }

    /// 获取账户 nonce
    /// eth_getTransactionCount(address, block_number) -> u64
    pub async fn get_transaction_count(
        &self,
        address: Address,
        block: BlockNumber,
    ) -> Result<u64, RpcError> {
        let state = self.chain.state_at(block)?;
        Ok(state.get_nonce(&address))
    }

    /// 获取合约代码
    /// eth_getCode(address, block_number) -> bytes
    pub async fn get_code(
        &self,
        address: Address,
        block: BlockNumber,
    ) -> Result<Vec<u8>, RpcError> {
        let state = self.chain.state_at(block)?;
        Ok(state.get_code(&address))
    }

    // ========== 区块相关 ==========

    /// 获取当前区块号
    /// eth_blockNumber() -> u64
    pub async fn block_number(&self) -> Result<u64, RpcError> {
        Ok(self.chain.latest_block_number())
    }

    /// 获取区块
    /// eth_getBlockByNumber(block_number, full_tx) -> Block
    pub async fn get_block_by_number(
        &self,
        number: BlockNumber,
        full_tx: bool,
    ) -> Result<Option<RpcBlock>, RpcError> {
        let block = self.chain.get_block(number)?;
        Ok(block.map(|b| RpcBlock::from_block(b, full_tx)))
    }

    /// 通过哈希获取区块
    /// eth_getBlockByHash(hash, full_tx) -> Block
    pub async fn get_block_by_hash(
        &self,
        hash: Hash,
        full_tx: bool,
    ) -> Result<Option<RpcBlock>, RpcError> {
        let block = self.chain.get_block_by_hash(&hash)?;
        Ok(block.map(|b| RpcBlock::from_block(b, full_tx)))
    }

    // ========== 交易相关 ==========

    /// 发送原始交易
    /// eth_sendRawTransaction(signed_tx) -> hash
    pub async fn send_raw_transaction(
        &self,
        raw_tx: Vec<u8>,
    ) -> Result<Hash, RpcError> {
        let tx = Transaction::from_bytes(&raw_tx)?;
        tx.verify()?;

        let hash = tx.hash();
        self.mempool.write().await.add_transaction(tx)?;

        // 广播到网络
        self.network.broadcast_transaction(&tx).await;

        Ok(hash)
    }

    /// 获取交易
    /// eth_getTransactionByHash(hash) -> Transaction
    pub async fn get_transaction_by_hash(
        &self,
        hash: Hash,
    ) -> Result<Option<RpcTransaction>, RpcError> {
        // 先查交易池
        if let Some(tx) = self.mempool.read().await.get(&hash) {
            return Ok(Some(RpcTransaction::from_pending(tx)));
        }

        // 再查已打包
        if let Some(tx) = self.chain.get_transaction(&hash)? {
            return Ok(Some(RpcTransaction::from_confirmed(tx)));
        }

        Ok(None)
    }

    /// 获取交易收据
    /// eth_getTransactionReceipt(hash) -> Receipt
    pub async fn get_transaction_receipt(
        &self,
        hash: Hash,
    ) -> Result<Option<RpcReceipt>, RpcError> {
        let receipt = self.chain.get_receipt(&hash)?;
        Ok(receipt.map(RpcReceipt::from))
    }

    /// 估算 Gas
    /// eth_estimateGas(tx) -> u64
    pub async fn estimate_gas(
        &self,
        tx: CallRequest,
    ) -> Result<u64, RpcError> {
        let state = self.chain.latest_state();
        let gas = self.estimate_gas_internal(&tx, &state)?;
        Ok(gas)
    }

    /// 调用合约（不产生状态变更）
    /// eth_call(tx, block_number) -> bytes
    pub async fn call(
        &self,
        tx: CallRequest,
        block: BlockNumber,
    ) -> Result<Vec<u8>, RpcError> {
        let state = self.chain.state_at(block)?;
        let result = self.execute_call(&tx, &state)?;
        Ok(result)
    }

    // ========== 链信息 ==========

    /// 获取链 ID
    /// eth_chainId() -> u64
    pub async fn chain_id(&self) -> Result<u64, RpcError> {
        Ok(CHAIN_ID)
    }

    /// 获取 Gas 价格
    /// eth_gasPrice() -> U256
    pub async fn gas_price(&self) -> Result<U256, RpcError> {
        // 返回最近区块的中位数 gas price
        let recent_blocks = self.chain.get_recent_blocks(20)?;
        let prices: Vec<U256> = recent_blocks
            .iter()
            .flat_map(|b| b.transactions.iter().map(|tx| tx.gas_price))
            .collect();

        Ok(median(&prices))
    }

    // ========== QFC 特有 ==========

    /// 获取验证者列表
    /// qfc_getValidators() -> Vec<Validator>
    pub async fn get_validators(&self) -> Result<Vec<RpcValidator>, RpcError> {
        let validators = self.chain.get_active_validators()?;
        Ok(validators.into_iter().map(RpcValidator::from).collect())
    }

    /// 获取贡献分数
    /// qfc_getContributionScore(address) -> u64
    pub async fn get_contribution_score(
        &self,
        address: Address,
    ) -> Result<u64, RpcError> {
        let validator = self.chain.get_validator(&address)?
            .ok_or(RpcError::ValidatorNotFound)?;
        Ok(validator.contribution_score)
    }
}
```

### WebSocket 订阅

```rust
/// WebSocket 订阅
pub enum Subscription {
    /// 新区块头
    NewHeads,
    /// 新待处理交易
    NewPendingTransactions,
    /// 日志过滤
    Logs(LogFilter),
    /// 同步状态
    SyncStatus,
}

/// 日志过滤器
#[derive(Clone, Debug)]
pub struct LogFilter {
    /// 起始区块
    pub from_block: Option<BlockNumber>,
    /// 结束区块
    pub to_block: Option<BlockNumber>,
    /// 合约地址
    pub address: Option<Vec<Address>>,
    /// 主题过滤
    pub topics: Vec<Option<Vec<Hash>>>,
}
```

## 节点启动流程

```rust
/// 节点主入口
pub async fn run_node(config: NodeConfig) -> Result<(), Error> {
    // 1. 初始化日志
    init_logging(&config.log_config);

    // 2. 打开数据库
    let db = Storage::open(&config.storage)?;

    // 3. 初始化状态
    let state = StateDB::new(db.clone());

    // 4. 初始化链
    let chain = Chain::new(db.clone(), state)?;

    // 5. 初始化交易池
    let mempool = Arc::new(RwLock::new(Mempool::new(config.mempool)));

    // 6. 初始化 P2P 网络
    let network = Network::new(config.network).await?;

    // 7. 启动同步
    let sync_manager = SyncManager::new(chain.clone(), network.clone());
    tokio::spawn(sync_manager.run());

    // 8. 初始化共识（如果是验证者）
    if let Some(validator_key) = config.validator_key {
        let consensus = Consensus::new(
            chain.clone(),
            mempool.clone(),
            network.clone(),
            validator_key,
        );
        tokio::spawn(consensus.run());
    }

    // 9. 启动 RPC 服务器
    let rpc = RpcServer::new(chain.clone(), mempool.clone(), network.clone());
    rpc.start(&config.rpc).await?;

    // 10. 等待关闭信号
    shutdown_signal().await;

    Ok(())
}

/// 节点配置
#[derive(Clone, Debug)]
pub struct NodeConfig {
    /// 数据目录
    pub data_dir: PathBuf,

    /// 存储配置
    pub storage: StorageConfig,

    /// 网络配置
    pub network: NetworkConfig,

    /// 交易池配置
    pub mempool: MempoolConfig,

    /// RPC 配置
    pub rpc: RpcConfig,

    /// 验证者私钥（可选，仅验证者节点）
    pub validator_key: Option<Keypair>,

    /// 日志配置
    pub log_config: LogConfig,
}
```

## 配置文件示例

```toml
# config.toml

[node]
data_dir = "./data"
chain_id = 9000

[network]
listen = ["/ip4/0.0.0.0/tcp/30303"]
bootnodes = [
    "/ip4/bootnode1.qfc.network/tcp/30303/p2p/12D3...",
    "/ip4/bootnode2.qfc.network/tcp/30303/p2p/12D3...",
]
max_peers = 50

[rpc]
http_enabled = true
http_addr = "0.0.0.0"
http_port = 8545
ws_enabled = true
ws_addr = "0.0.0.0"
ws_port = 8546

[mempool]
max_size = 10000
max_per_account = 64
min_gas_price = 1000000000  # 1 Gwei

[storage]
cache_size = 512  # MB
pruning_depth = 1000

[validator]
# 仅验证者节点需要
enabled = false
# key_file = "./validator.key"

[log]
level = "info"
format = "json"
```

## 模块依赖关系

```
                    ┌──────────────┐
                    │     RPC      │
                    └──────┬───────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Mempool    │  │    Chain     │  │   Network    │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │
       │         ┌───────┴───────┐         │
       │         ▼               ▼         │
       │  ┌──────────────┐ ┌──────────┐    │
       │  │  Consensus   │ │  State   │    │
       │  └──────┬───────┘ └────┬─────┘    │
       │         │              │          │
       └─────────┴──────┬───────┴──────────┘
                        │
                        ▼
                ┌──────────────┐
                │   Storage    │
                └──────────────┘
```

## 测试策略

### 单元测试

```bash
# 运行所有单元测试
cargo test

# 运行特定模块测试
cargo test --package qfc-consensus
cargo test --package qfc-state
```

### 集成测试

```bash
# 启动本地测试网（3节点）
./scripts/start-local-testnet.sh

# 运行集成测试
cargo test --test integration
```

### 性能基准

```bash
# 运行基准测试
cargo bench

# 交易吞吐量测试
cargo bench --bench throughput
```

## 里程碑

### Phase 1: 基础框架（Month 1）
- [x] 数据结构定义
- [ ] 存储层实现
- [ ] 状态管理基础
- [ ] 简单 P2P 网络

### Phase 2: 核心功能（Month 2）
- [ ] 交易执行
- [ ] 区块生产
- [ ] 基础共识（简化 PoC）
- [ ] 区块同步

### Phase 3: 完善（Month 3）
- [ ] RPC API 完整实现
- [ ] 交易池优化
- [ ] 完整 PoC 共识
- [ ] 3 节点测试网运行

---

**最后更新**: 2026-02-01
**版本**: 1.0.0
**维护者**: QFC Core Team
