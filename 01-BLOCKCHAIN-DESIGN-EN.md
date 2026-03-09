# QFC Blockchain Core Design

## Overview

This document describes the technical design of the QFC blockchain core engine (`qfc-core`), including data structures, network layer, state management, storage, and RPC API.

## Technology Stack

| Component | Technology | Description |
|-----------|-----------|-------------|
| Language | Rust | High performance, memory safety |
| Network | libp2p | Modular P2P networking library |
| State Storage | RocksDB | High-performance KV store |
| Serialization | borsh / SSZ | Efficient binary serialization |
| Cryptography | ed25519 | Signature algorithm |
| Hashing | Blake3 | High-speed hash function |

## Data Structures

### Block

```rust
/// Block header
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct BlockHeader {
    /// Block version number
    pub version: u32,

    /// Block height
    pub number: u64,

    /// Parent block hash
    pub parent_hash: Hash,

    /// State root (Merkle Patricia Trie)
    pub state_root: Hash,

    /// Transactions root (Merkle Tree)
    pub transactions_root: Hash,

    /// Receipts root (Merkle Tree)
    pub receipts_root: Hash,

    /// Block producer address
    pub producer: Address,

    /// Producer contribution score
    pub contribution_score: u64,

    /// VRF proof
    pub vrf_proof: VrfProof,

    /// Timestamp (milliseconds)
    pub timestamp: u64,

    /// Gas limit
    pub gas_limit: u64,

    /// Gas used
    pub gas_used: u64,

    /// Extra data (max 32 bytes)
    pub extra_data: Vec<u8>,
}

/// Full block
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Block {
    pub header: BlockHeader,
    pub transactions: Vec<Transaction>,
    pub votes: Vec<Vote>,
    pub signature: Signature,
}

impl Block {
    /// Calculate block hash
    pub fn hash(&self) -> Hash {
        blake3::hash(&self.header.to_bytes())
    }

    /// Verify block signature
    pub fn verify_signature(&self) -> bool {
        let msg = self.hash();
        verify_signature(&self.header.producer, &msg, &self.signature)
    }
}
```

### Transaction

```rust
/// Transaction type
#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum TransactionType {
    /// Regular transfer
    Transfer,
    /// Contract creation
    ContractCreate,
    /// Contract call
    ContractCall,
    /// Staking
    Stake,
    /// Unstaking
    Unstake,
    /// Validator registration
    ValidatorRegister,
    /// Validator exit
    ValidatorExit,
}

/// Transaction
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Transaction {
    /// Transaction type
    pub tx_type: TransactionType,

    /// Chain ID (replay attack prevention)
    pub chain_id: u64,

    /// Sender nonce
    pub nonce: u64,

    /// Recipient address (None for contract creation)
    pub to: Option<Address>,

    /// Transfer amount (unit: wei)
    pub value: U256,

    /// Call data
    pub data: Vec<u8>,

    /// Gas limit
    pub gas_limit: u64,

    /// Gas price (unit: wei)
    pub gas_price: U256,

    /// Signature
    pub signature: Signature,
}

impl Transaction {
    /// Calculate transaction hash
    pub fn hash(&self) -> Hash {
        blake3::hash(&self.to_bytes_without_signature())
    }

    /// Recover sender address
    pub fn recover_sender(&self) -> Result<Address, Error> {
        let msg = self.hash();
        recover_address(&msg, &self.signature)
    }

    /// Verify transaction
    pub fn verify(&self) -> Result<(), Error> {
        // 1. Verify signature
        let sender = self.recover_sender()?;

        // 2. Verify chain_id
        if self.chain_id != CHAIN_ID {
            return Err(Error::InvalidChainId);
        }

        // 3. Verify gas
        if self.gas_limit < MINIMUM_GAS {
            return Err(Error::GasTooLow);
        }

        Ok(())
    }
}
```

### Account

```rust
/// Account type
#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum AccountType {
    /// Externally owned account (user)
    EOA,
    /// Contract account
    Contract,
    /// Validator account
    Validator,
}

/// Account state
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Account {
    /// Account type
    pub account_type: AccountType,

    /// Balance
    pub balance: U256,

    /// Nonce (replay attack prevention)
    pub nonce: u64,

    /// Code hash (contract account)
    pub code_hash: Option<Hash>,

    /// Storage root (contract account)
    pub storage_root: Option<Hash>,

    /// Staked amount (validator)
    pub stake: Option<U256>,

    /// Contribution score (validator)
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

### Receipt

```rust
/// Transaction receipt
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Receipt {
    /// Transaction hash
    pub tx_hash: Hash,

    /// Transaction index (position in block)
    pub tx_index: u32,

    /// Execution status
    pub status: ReceiptStatus,

    /// Cumulative gas used
    pub cumulative_gas_used: u64,

    /// Logs
    pub logs: Vec<Log>,

    /// Log Bloom filter
    pub logs_bloom: Bloom,

    /// Contract address (if contract creation)
    pub contract_address: Option<Address>,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum ReceiptStatus {
    Success,
    Failure(String),
    OutOfGas,
    Reverted,
}

/// Event log
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Log {
    pub address: Address,
    pub topics: Vec<Hash>,
    pub data: Vec<u8>,
}
```

## Network Layer (P2P)

### Architecture

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

### Node Configuration

```rust
/// P2P network configuration
#[derive(Clone, Debug)]
pub struct NetworkConfig {
    /// Listen addresses
    pub listen_addresses: Vec<Multiaddr>,

    /// Bootstrap nodes
    pub bootnodes: Vec<Multiaddr>,

    /// Maximum inbound connections
    pub max_inbound_peers: u32,

    /// Maximum outbound connections
    pub max_outbound_peers: u32,

    /// Node private key
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

### GossipSub Topics

```rust
/// Network message topics
pub enum Topic {
    /// New block broadcast
    NewBlocks,
    /// New transaction broadcast
    NewTransactions,
    /// Consensus votes
    ConsensusVotes,
    /// Validator messages
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

### Block Synchronization

```rust
/// Block sync request
#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum SyncRequest {
    /// Get block headers
    GetHeaders {
        start_number: u64,
        count: u32,
    },

    /// Get full blocks
    GetBlocks {
        hashes: Vec<Hash>,
    },

    /// Get state
    GetState {
        root: Hash,
        paths: Vec<Vec<u8>>,
    },
}

/// Sync state machine
pub struct SyncManager {
    /// Current sync mode
    mode: SyncMode,

    /// Local highest block
    local_head: u64,

    /// Network highest block
    network_head: u64,

    /// Pending block sync queue
    pending_blocks: VecDeque<Hash>,
}

#[derive(Clone, Debug)]
pub enum SyncMode {
    /// Full sync (from genesis block)
    Full,
    /// Fast sync (download state only)
    Fast,
    /// Light sync (verify block headers only)
    Light,
    /// Sync completed
    Synced,
}
```

## State Management

### Merkle Patricia Trie

```rust
/// State trie node types
#[derive(Clone, Debug)]
pub enum TrieNode {
    /// Empty node
    Empty,

    /// Leaf node
    Leaf {
        key: NibbleSlice,
        value: Vec<u8>,
    },

    /// Extension node
    Extension {
        key: NibbleSlice,
        child: Hash,
    },

    /// Branch node
    Branch {
        children: [Option<Hash>; 16],
        value: Option<Vec<u8>>,
    },
}

/// State database
pub struct StateDB {
    /// Underlying storage
    db: Arc<RocksDB>,

    /// State cache
    cache: LruCache<Hash, TrieNode>,

    /// Current state root
    root: Hash,
}

impl StateDB {
    /// Get account
    pub fn get_account(&self, address: &Address) -> Option<Account> {
        let key = keccak256(address);
        self.get(&key).map(|bytes| Account::from_bytes(&bytes))
    }

    /// Update account
    pub fn set_account(&mut self, address: &Address, account: &Account) {
        let key = keccak256(address);
        self.set(&key, &account.to_bytes());
    }

    /// Get contract storage
    pub fn get_storage(&self, address: &Address, slot: &U256) -> U256 {
        let account = self.get_account(address)?;
        let storage_root = account.storage_root?;

        let storage_trie = self.open_trie(storage_root);
        let key = keccak256(&slot.to_bytes());

        storage_trie.get(&key)
            .map(|bytes| U256::from_bytes(&bytes))
            .unwrap_or(U256::zero())
    }

    /// Commit state changes, return new state root
    pub fn commit(&mut self) -> Hash {
        self.root = self.trie.commit();
        self.root
    }
}
```

### State Transition

```rust
/// State transition engine
pub struct StateTransition {
    state: StateDB,
    receipts: Vec<Receipt>,
    logs: Vec<Log>,
    gas_used: u64,
}

impl StateTransition {
    /// Execute transaction
    pub fn apply_transaction(
        &mut self,
        tx: &Transaction,
    ) -> Result<Receipt, Error> {
        // 1. Verify transaction
        tx.verify()?;

        // 2. Check sender balance
        let sender = tx.recover_sender()?;
        let sender_account = self.state.get_account(&sender)
            .ok_or(Error::AccountNotFound)?;

        let total_cost = tx.value + tx.gas_limit * tx.gas_price;
        if sender_account.balance < total_cost {
            return Err(Error::InsufficientBalance);
        }

        // 3. Check nonce
        if sender_account.nonce != tx.nonce {
            return Err(Error::InvalidNonce);
        }

        // 4. Deduct gas prepayment
        self.state.sub_balance(&sender, tx.gas_limit * tx.gas_price);
        self.state.increment_nonce(&sender);

        // 5. Execute transaction
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

        // 6. Refund excess gas
        let gas_refund = (tx.gas_limit - result.gas_used) * tx.gas_price;
        self.state.add_balance(&sender, gas_refund);

        // 7. Generate receipt
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

    /// Execute transfer
    fn execute_transfer(&mut self, tx: &Transaction) -> ExecutionResult {
        let to = tx.to.ok_or(Error::MissingRecipient)?;
        let sender = tx.recover_sender()?;

        // Transfer
        self.state.sub_balance(&sender, tx.value);
        self.state.add_balance(&to, tx.value);

        ExecutionResult {
            status: ReceiptStatus::Success,
            gas_used: 21000,  // Base transfer gas
            logs: vec![],
            contract_address: None,
        }
    }
}
```

## Storage Layer

### RocksDB Schema

```rust
/// Database column families
pub enum ColumnFamily {
    /// Block headers
    BlockHeaders,
    /// Block bodies
    BlockBodies,
    /// Transactions
    Transactions,
    /// Receipts
    Receipts,
    /// State (Merkle Patricia Trie nodes)
    State,
    /// Contract code
    Code,
    /// Index (transaction hash -> block number)
    TxIndex,
    /// Metadata
    Metadata,
}

/// Storage keys
pub enum StorageKey {
    /// Block header: height -> BlockHeader
    BlockHeader(u64),
    /// Block hash index: hash -> height
    BlockHashIndex(Hash),
    /// Block body: height -> BlockBody
    BlockBody(u64),
    /// Transaction: hash -> Transaction
    Transaction(Hash),
    /// Receipt: hash -> Receipt
    Receipt(Hash),
    /// State node: hash -> TrieNode
    StateNode(Hash),
    /// Contract code: hash -> bytes
    Code(Hash),
    /// Latest block height
    LatestBlockNumber,
    /// Latest state root
    LatestStateRoot,
}

/// Storage interface
pub trait Storage {
    /// Write block
    fn write_block(&self, block: &Block) -> Result<(), Error>;

    /// Read block header
    fn get_block_header(&self, number: u64) -> Option<BlockHeader>;

    /// Get block by hash
    fn get_block_by_hash(&self, hash: &Hash) -> Option<Block>;

    /// Read transaction
    fn get_transaction(&self, hash: &Hash) -> Option<Transaction>;

    /// Read receipt
    fn get_receipt(&self, hash: &Hash) -> Option<Receipt>;

    /// Batch write
    fn write_batch(&self, batch: WriteBatch) -> Result<(), Error>;
}
```

### Storage Optimization

```rust
/// Storage configuration
#[derive(Clone, Debug)]
pub struct StorageConfig {
    /// Data directory
    pub data_dir: PathBuf,

    /// Block Cache size (MB)
    pub block_cache_size: usize,

    /// Write Buffer size (MB)
    pub write_buffer_size: usize,

    /// Maximum open files
    pub max_open_files: i32,

    /// Enable compression
    pub enable_compression: bool,

    /// State pruning depth (retain state for the most recent N blocks)
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
            state_pruning_depth: Some(1000),  // Retain the most recent 1000 blocks
        }
    }
}
```

## Transaction Pool (Mempool)

```rust
/// Transaction pool
pub struct Mempool {
    /// Pending transactions (sorted by gas price)
    pending: BTreeMap<U256, Vec<Transaction>>,

    /// Grouped by sender (for nonce checking)
    by_sender: HashMap<Address, Vec<Transaction>>,

    /// Transaction hash index
    by_hash: HashMap<Hash, Transaction>,

    /// Configuration
    config: MempoolConfig,
}

#[derive(Clone, Debug)]
pub struct MempoolConfig {
    /// Maximum transaction count
    pub max_size: usize,

    /// Maximum pending transactions per account
    pub max_per_account: usize,

    /// Minimum gas price
    pub min_gas_price: U256,

    /// Transaction expiration time (seconds)
    pub tx_lifetime: u64,
}

impl Mempool {
    /// Add transaction
    pub fn add_transaction(&mut self, tx: Transaction) -> Result<(), Error> {
        // 1. Verify transaction
        tx.verify()?;

        // 2. Check gas price
        if tx.gas_price < self.config.min_gas_price {
            return Err(Error::GasPriceTooLow);
        }

        // 3. Check if already exists
        let hash = tx.hash();
        if self.by_hash.contains_key(&hash) {
            return Err(Error::AlreadyKnown);
        }

        // 4. Check per-account transaction limit
        let sender = tx.recover_sender()?;
        let sender_txs = self.by_sender.entry(sender).or_default();
        if sender_txs.len() >= self.config.max_per_account {
            return Err(Error::AccountPoolFull);
        }

        // 5. Add to pool
        self.pending
            .entry(tx.gas_price)
            .or_default()
            .push(tx.clone());

        sender_txs.push(tx.clone());
        self.by_hash.insert(hash, tx);

        // 6. Evict lowest gas price transactions if size limit exceeded
        self.evict_if_needed();

        Ok(())
    }

    /// Select transactions for block inclusion
    pub fn select_transactions(
        &self,
        max_gas: u64,
        max_count: usize,
    ) -> Vec<Transaction> {
        let mut selected = Vec::new();
        let mut gas_used = 0u64;

        // Select by gas price from highest to lowest
        for (_, txs) in self.pending.iter().rev() {
            for tx in txs {
                if selected.len() >= max_count {
                    break;
                }

                if gas_used + tx.gas_limit > max_gas {
                    continue;
                }

                // Verify nonce is sequential
                let sender = tx.recover_sender().unwrap();
                if self.is_valid_nonce(&sender, tx.nonce) {
                    selected.push(tx.clone());
                    gas_used += tx.gas_limit;
                }
            }
        }

        selected
    }

    /// Remove included transactions
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

### JSON-RPC 2.0 Interface

```rust
/// RPC server
pub struct RpcServer {
    /// Blockchain state
    chain: Arc<Chain>,

    /// Transaction pool
    mempool: Arc<RwLock<Mempool>>,

    /// Network
    network: Arc<Network>,
}

/// RPC methods
impl RpcServer {
    // ========== Account Methods ==========

    /// Get account balance
    /// eth_getBalance(address, block_number) -> U256
    pub async fn get_balance(
        &self,
        address: Address,
        block: BlockNumber,
    ) -> Result<U256, RpcError> {
        let state = self.chain.state_at(block)?;
        Ok(state.get_balance(&address))
    }

    /// Get account nonce
    /// eth_getTransactionCount(address, block_number) -> u64
    pub async fn get_transaction_count(
        &self,
        address: Address,
        block: BlockNumber,
    ) -> Result<u64, RpcError> {
        let state = self.chain.state_at(block)?;
        Ok(state.get_nonce(&address))
    }

    /// Get contract code
    /// eth_getCode(address, block_number) -> bytes
    pub async fn get_code(
        &self,
        address: Address,
        block: BlockNumber,
    ) -> Result<Vec<u8>, RpcError> {
        let state = self.chain.state_at(block)?;
        Ok(state.get_code(&address))
    }

    // ========== Block Methods ==========

    /// Get current block number
    /// eth_blockNumber() -> u64
    pub async fn block_number(&self) -> Result<u64, RpcError> {
        Ok(self.chain.latest_block_number())
    }

    /// Get block
    /// eth_getBlockByNumber(block_number, full_tx) -> Block
    pub async fn get_block_by_number(
        &self,
        number: BlockNumber,
        full_tx: bool,
    ) -> Result<Option<RpcBlock>, RpcError> {
        let block = self.chain.get_block(number)?;
        Ok(block.map(|b| RpcBlock::from_block(b, full_tx)))
    }

    /// Get block by hash
    /// eth_getBlockByHash(hash, full_tx) -> Block
    pub async fn get_block_by_hash(
        &self,
        hash: Hash,
        full_tx: bool,
    ) -> Result<Option<RpcBlock>, RpcError> {
        let block = self.chain.get_block_by_hash(&hash)?;
        Ok(block.map(|b| RpcBlock::from_block(b, full_tx)))
    }

    // ========== Transaction Methods ==========

    /// Send raw transaction
    /// eth_sendRawTransaction(signed_tx) -> hash
    pub async fn send_raw_transaction(
        &self,
        raw_tx: Vec<u8>,
    ) -> Result<Hash, RpcError> {
        let tx = Transaction::from_bytes(&raw_tx)?;
        tx.verify()?;

        let hash = tx.hash();
        self.mempool.write().await.add_transaction(tx)?;

        // Broadcast to network
        self.network.broadcast_transaction(&tx).await;

        Ok(hash)
    }

    /// Get transaction
    /// eth_getTransactionByHash(hash) -> Transaction
    pub async fn get_transaction_by_hash(
        &self,
        hash: Hash,
    ) -> Result<Option<RpcTransaction>, RpcError> {
        // Check mempool first
        if let Some(tx) = self.mempool.read().await.get(&hash) {
            return Ok(Some(RpcTransaction::from_pending(tx)));
        }

        // Then check confirmed transactions
        if let Some(tx) = self.chain.get_transaction(&hash)? {
            return Ok(Some(RpcTransaction::from_confirmed(tx)));
        }

        Ok(None)
    }

    /// Get transaction receipt
    /// eth_getTransactionReceipt(hash) -> Receipt
    pub async fn get_transaction_receipt(
        &self,
        hash: Hash,
    ) -> Result<Option<RpcReceipt>, RpcError> {
        let receipt = self.chain.get_receipt(&hash)?;
        Ok(receipt.map(RpcReceipt::from))
    }

    /// Estimate gas
    /// eth_estimateGas(tx) -> u64
    pub async fn estimate_gas(
        &self,
        tx: CallRequest,
    ) -> Result<u64, RpcError> {
        let state = self.chain.latest_state();
        let gas = self.estimate_gas_internal(&tx, &state)?;
        Ok(gas)
    }

    /// Call contract (no state changes)
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

    // ========== Chain Info ==========

    /// Get chain ID
    /// eth_chainId() -> u64
    pub async fn chain_id(&self) -> Result<u64, RpcError> {
        Ok(CHAIN_ID)
    }

    /// Get gas price
    /// eth_gasPrice() -> U256
    pub async fn gas_price(&self) -> Result<U256, RpcError> {
        // Return median gas price from recent blocks
        let recent_blocks = self.chain.get_recent_blocks(20)?;
        let prices: Vec<U256> = recent_blocks
            .iter()
            .flat_map(|b| b.transactions.iter().map(|tx| tx.gas_price))
            .collect();

        Ok(median(&prices))
    }

    // ========== QFC-Specific ==========

    /// Get validator list
    /// qfc_getValidators() -> Vec<Validator>
    pub async fn get_validators(&self) -> Result<Vec<RpcValidator>, RpcError> {
        let validators = self.chain.get_active_validators()?;
        Ok(validators.into_iter().map(RpcValidator::from).collect())
    }

    /// Get contribution score
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

### WebSocket Subscriptions

```rust
/// WebSocket subscriptions
pub enum Subscription {
    /// New block headers
    NewHeads,
    /// New pending transactions
    NewPendingTransactions,
    /// Log filter
    Logs(LogFilter),
    /// Sync status
    SyncStatus,
}

/// Log filter
#[derive(Clone, Debug)]
pub struct LogFilter {
    /// Start block
    pub from_block: Option<BlockNumber>,
    /// End block
    pub to_block: Option<BlockNumber>,
    /// Contract addresses
    pub address: Option<Vec<Address>>,
    /// Topic filter
    pub topics: Vec<Option<Vec<Hash>>>,
}
```

## Node Startup Flow

```rust
/// Node main entry
pub async fn run_node(config: NodeConfig) -> Result<(), Error> {
    // 1. Initialize logging
    init_logging(&config.log_config);

    // 2. Open database
    let db = Storage::open(&config.storage)?;

    // 3. Initialize state
    let state = StateDB::new(db.clone());

    // 4. Initialize chain
    let chain = Chain::new(db.clone(), state)?;

    // 5. Initialize transaction pool
    let mempool = Arc::new(RwLock::new(Mempool::new(config.mempool)));

    // 6. Initialize P2P network
    let network = Network::new(config.network).await?;

    // 7. Start synchronization
    let sync_manager = SyncManager::new(chain.clone(), network.clone());
    tokio::spawn(sync_manager.run());

    // 8. Initialize consensus (if validator)
    if let Some(validator_key) = config.validator_key {
        let consensus = Consensus::new(
            chain.clone(),
            mempool.clone(),
            network.clone(),
            validator_key,
        );
        tokio::spawn(consensus.run());
    }

    // 9. Start RPC server
    let rpc = RpcServer::new(chain.clone(), mempool.clone(), network.clone());
    rpc.start(&config.rpc).await?;

    // 10. Wait for shutdown signal
    shutdown_signal().await;

    Ok(())
}

/// Node configuration
#[derive(Clone, Debug)]
pub struct NodeConfig {
    /// Data directory
    pub data_dir: PathBuf,

    /// Storage configuration
    pub storage: StorageConfig,

    /// Network configuration
    pub network: NetworkConfig,

    /// Transaction pool configuration
    pub mempool: MempoolConfig,

    /// RPC configuration
    pub rpc: RpcConfig,

    /// Validator private key (optional, validator nodes only)
    pub validator_key: Option<Keypair>,

    /// Log configuration
    pub log_config: LogConfig,
}
```

## Configuration File Example

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
# Required for validator nodes only
enabled = false
# key_file = "./validator.key"

[log]
level = "info"
format = "json"
```

## Module Dependency Graph

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

## Testing Strategy

### Unit Tests

```bash
# Run all unit tests
cargo test

# Run tests for a specific module
cargo test --package qfc-consensus
cargo test --package qfc-state
```

### Integration Tests

```bash
# Start local testnet (3 nodes)
./scripts/start-local-testnet.sh

# Run integration tests
cargo test --test integration
```

### Performance Benchmarks

```bash
# Run benchmarks
cargo bench

# Transaction throughput test
cargo bench --bench throughput
```

## Milestones

### Phase 1: Basic Framework (Month 1)
- [x] Data structure definitions
- [ ] Storage layer implementation
- [ ] Basic state management
- [ ] Simple P2P network

### Phase 2: Core Features (Month 2)
- [ ] Transaction execution
- [ ] Block production
- [ ] Basic consensus (simplified PoC)
- [ ] Block synchronization

### Phase 3: Refinement (Month 3)
- [ ] Full RPC API implementation
- [ ] Transaction pool optimization
- [ ] Complete PoC consensus
- [ ] 3-node testnet operation

---

**Last Updated**: 2026-02-01
**Version**: 1.0.0
**Maintainer**: QFC Core Team
