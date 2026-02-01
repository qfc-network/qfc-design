# QFC Consensus Mechanism - Proof of Contribution (PoC)

## 概述

Proof of Contribution (PoC) 是 QFC 区块链的核心创新，它结合了多种共识机制的优势：
- PoW 的安全性
- PoS 的能源效率
- DPoS 的高性能
- 独创的多维度贡献评估

## 设计理念

### 核心问题
传统共识机制的局限：
- **PoW**: 能源浪费，51%算力攻击
- **PoS**: 富者愈富，中心化倾向
- **DPoS**: 投票操纵，验证者串通

### PoC 解决方案
通过**多维度贡献评分**，防止单一资源控制网络：
- 算力不足？可以提供存储
- 资金不足？可以提供稳定服务
- 综合贡献决定出块权重

## 贡献评分算法

### 评分公式

```rust
fn calculate_contribution_score(node: &ValidatorNode) -> f64 {
    let mut score = 0.0;
    
    // 1. 质押贡献 (30%)
    let stake_ratio = node.stake as f64 / total_stake as f64;
    score += stake_ratio * 0.30;
    
    // 2. 计算贡献 (可选, 20%)
    if node.provides_compute {
        let compute_ratio = node.hashrate as f64 / total_hashrate as f64;
        score += compute_ratio * 0.20;
    }
    
    // 3. 在线时长 (15%)
    let uptime_score = node.uptime_percentage;
    score += uptime_score * 0.15;
    
    // 4. 验证准确率 (15%)
    let accuracy = node.validation_accuracy;
    score += accuracy * 0.15;
    
    // 5. 网络服务质量 (10%)
    let latency_score = 1.0 / (1.0 + node.avg_latency_ms / 100.0);
    let bandwidth_score = node.bandwidth_mbps / 1000.0;
    let service_score = (latency_score * 0.6 + bandwidth_score.min(1.0) * 0.4);
    score += service_score * 0.10;
    
    // 6. 存储贡献 (5%)
    let storage_ratio = node.storage_provided_gb as f64 / total_storage_gb as f64;
    score += storage_ratio * 0.05;
    
    // 7. 历史信誉 (5%)
    let reputation = calculate_reputation(&node.history);
    score += reputation * 0.05;
    
    // 应用网络动态乘数
    score *= get_network_multiplier(&node);
    
    score
}
```

### 权重说明

| 维度 | 权重 | 说明 | 验证方式 |
|------|------|------|---------|
| 质押 | 30% | 质押 QFC 代币数量 | 链上验证 |
| 计算 | 20% | 提供算力（可选） | PoW 工作量证明 |
| 在线时长 | 15% | 节点正常运行时间比例 | 心跳检测 |
| 验证准确率 | 15% | 历史验证投票正确率 | 链上记录 |
| 网络服务 | 10% | 延迟、带宽等网络质量 | P2P 测量 |
| 存储 | 5% | 提供链上数据存储 | 数据挑战 |
| 历史信誉 | 5% | 长期行为记录 | 综合评估 |

### 动态权重调整

网络会根据实时状态调整各维度权重：

```rust
fn get_network_multiplier(node: &ValidatorNode) -> f64 {
    let state = get_network_state();
    
    match state {
        // 网络拥堵：提升计算贡献权重
        NetworkState::Congested => {
            if node.provides_compute {
                1.2  // +20% bonus
            } else {
                1.0
            }
        },
        
        // 存储短缺：提升存储贡献权重
        NetworkState::StorageShortage => {
            if node.storage_provided_gb > 1000 {
                1.15  // +15% bonus
            } else {
                1.0
            }
        },
        
        // 正常状态
        NetworkState::Normal => 1.0,
        
        // 安全威胁：提升信誉权重
        NetworkState::UnderAttack => {
            if node.reputation > 0.9 {
                1.3  // +30% bonus for trusted nodes
            } else {
                0.7  // penalty for low reputation
            }
        }
    }
}
```

## 区块生产流程

### 1. VRF (Verifiable Random Function) 选举

每个 epoch（比如 10 秒）使用 VRF 选出区块生产者：

```rust
struct Epoch {
    number: u64,
    seed: [u8; 32],        // 随机种子
    duration: Duration,     // epoch 时长
}

fn select_block_producer(epoch: &Epoch, validators: &[ValidatorNode]) -> ValidatorNode {
    // 1. 计算所有验证者的贡献分数
    let scores: Vec<(Address, f64)> = validators
        .iter()
        .map(|v| (v.address, calculate_contribution_score(v)))
        .collect();
    
    let total_score: f64 = scores.iter().map(|(_, s)| s).sum();
    
    // 2. 每个验证者生成 VRF 证明
    let mut candidates = Vec::new();
    
    for (address, score) in scores {
        let validator = validators.iter().find(|v| v.address == address).unwrap();
        
        // 使用私钥 + epoch seed 生成 VRF
        let (vrf_output, vrf_proof) = validator.vrf_prove(&epoch.seed);
        
        // VRF 输出转为 0-1 的随机数
        let random_value = bytes_to_f64(&vrf_output);
        
        // 计算选中概率
        let probability = score / total_score;
        
        // 如果 VRF 输出 < 概率阈值，则候选
        if random_value < probability {
            candidates.push((address, vrf_output, vrf_proof));
        }
    }
    
    // 3. 选择 VRF 输出最小的作为生产者
    candidates.sort_by(|a, b| a.1.cmp(&b.1));
    
    validators.iter()
        .find(|v| v.address == candidates[0].0)
        .unwrap()
        .clone()
}
```

### 2. 区块生产

```rust
async fn produce_block(
    producer: &ValidatorNode,
    mempool: &TransactionPool,
) -> Block {
    // 1. 从交易池选择交易
    let transactions = mempool.select_transactions(
        MAX_BLOCK_SIZE,
        MAX_GAS_LIMIT,
    );
    
    // 2. 执行交易，更新状态
    let (receipts, new_state_root) = execute_transactions(
        &transactions,
        &current_state,
    ).await;
    
    // 3. 构建区块
    let block = Block {
        header: BlockHeader {
            number: current_height + 1,
            parent_hash: parent_block.hash(),
            state_root: new_state_root,
            transactions_root: calculate_merkle_root(&transactions),
            receipts_root: calculate_merkle_root(&receipts),
            timestamp: now(),
            producer: producer.address,
            contribution_score: producer.score,
        },
        transactions,
        receipts,
    };
    
    // 4. 签名
    let signature = producer.sign(block.hash());
    block.set_signature(signature);
    
    block
}
```

### 3. 区块验证与投票

```rust
async fn validate_and_vote(
    validator: &ValidatorNode,
    block: &Block,
) -> Vote {
    // 1. 验证区块生产者是否有资格
    let expected_producer = select_block_producer(
        &current_epoch,
        &active_validators,
    );
    
    if block.header.producer != expected_producer.address {
        return Vote::Reject(RejectReason::InvalidProducer);
    }
    
    // 2. 验证 VRF 证明
    if !verify_vrf_proof(&block.vrf_proof, &current_epoch.seed) {
        return Vote::Reject(RejectReason::InvalidVRF);
    }
    
    // 3. 验证交易和状态转换
    let valid = verify_state_transition(
        &parent_state,
        &block.transactions,
        &block.header.state_root,
    );
    
    if !valid {
        return Vote::Reject(RejectReason::InvalidStateTransition);
    }
    
    // 4. 投票
    let vote = Vote {
        block_hash: block.hash(),
        block_height: block.header.number,
        voter: validator.address,
        decision: VoteDecision::Accept,
        timestamp: now(),
    };
    
    // 5. 签名投票
    let signature = validator.sign(vote.hash());
    vote.set_signature(signature);
    
    // 6. 广播投票
    broadcast_vote(vote.clone());
    
    vote
}
```

### 4. 最终确定性

```rust
fn check_finality(block: &Block, votes: &[Vote]) -> bool {
    // 1. 收集该区块的所有投票
    let accept_votes: Vec<&Vote> = votes
        .iter()
        .filter(|v| v.block_hash == block.hash() && v.decision == VoteDecision::Accept)
        .collect();
    
    // 2. 计算投票权重
    let total_vote_weight: f64 = accept_votes
        .iter()
        .map(|v| {
            let validator = get_validator(&v.voter);
            calculate_contribution_score(validator)
        })
        .sum();
    
    let total_network_weight: f64 = active_validators
        .iter()
        .map(|v| calculate_contribution_score(v))
        .sum();
    
    // 3. 超过 2/3 权重即达成最终性
    let finality_threshold = total_network_weight * 2.0 / 3.0;
    
    total_vote_weight >= finality_threshold
}
```

## 激励机制

### 区块奖励分配

```rust
fn distribute_block_reward(block: &Block, votes: &[Vote]) {
    let base_reward = BLOCK_REWARD;  // 比如 10 QFC
    
    // 1. 区块生产者获得 70%
    let producer_reward = base_reward * 0.70;
    transfer(REWARD_POOL, block.header.producer, producer_reward);
    
    // 2. 投票验证者分享 30%
    let voters_reward = base_reward * 0.30;
    let voter_count = votes.len() as f64;
    
    for vote in votes {
        if vote.decision == VoteDecision::Accept {
            let validator = get_validator(&vote.voter);
            let vote_weight = calculate_contribution_score(validator);
            
            // 按贡献分数加权分配
            let reward = voters_reward * (vote_weight / total_vote_weight);
            transfer(REWARD_POOL, vote.voter, reward);
        }
    }
}
```

### 交易费分配

```rust
fn distribute_transaction_fees(block: &Block) {
    let total_fees: u256 = block.transactions
        .iter()
        .map(|tx| tx.gas_used * tx.gas_price)
        .sum();
    
    // 分配策略：
    // - 50% 给区块生产者
    // - 30% 给投票验证者
    // - 20% 销毁（通缩）
    
    let producer_share = total_fees * 50 / 100;
    let voters_share = total_fees * 30 / 100;
    let burn_amount = total_fees * 20 / 100;
    
    transfer(FEE_POOL, block.header.producer, producer_share);
    distribute_to_voters(voters_share, &block.votes);
    burn(burn_amount);
}
```

## 惩罚机制（Slashing）

### 可罚没行为

```rust
enum SlashableOffense {
    DoubleSign,           // 双签（同一高度签署多个区块）
    InvalidBlock,         // 生产无效区块
    Censorship,           // 恶意审查交易
    Offline,              // 长时间离线
    FalseVote,            // 投票给无效区块
}

fn slash_validator(
    validator: Address,
    offense: SlashableOffense,
) -> SlashResult {
    let stake = get_stake(validator);
    
    let (slash_amount, jail_duration) = match offense {
        SlashableOffense::DoubleSign => {
            // 双签：罚没 50% 质押 + 永久禁止
            (stake * 50 / 100, Duration::MAX)
        },
        
        SlashableOffense::InvalidBlock => {
            // 无效区块：罚没 10% + 禁止7天
            (stake * 10 / 100, Duration::from_days(7))
        },
        
        SlashableOffense::Censorship => {
            // 审查交易：罚没 5% + 禁止3天
            (stake * 5 / 100, Duration::from_days(3))
        },
        
        SlashableOffense::Offline => {
            // 离线：罚没 1% + 禁止1天
            (stake * 1 / 100, Duration::from_days(1))
        },
        
        SlashableOffense::FalseVote => {
            // 错误投票：罚没 2% + 禁止1天
            (stake * 2 / 100, Duration::from_days(1))
        },
    };
    
    // 执行罚没
    burn(validator, slash_amount);
    
    // 加入黑名单
    jail(validator, jail_duration);
    
    // 更新信誉分数
    decrease_reputation(validator, offense);
    
    SlashResult {
        validator,
        offense,
        slashed_amount: slash_amount,
        jail_until: now() + jail_duration,
    }
}
```

### 双签检测

```rust
fn detect_double_sign(blocks: &[Block]) -> Vec<(Address, Block, Block)> {
    let mut violations = Vec::new();
    
    // 按高度分组
    let mut blocks_by_height: HashMap<u64, Vec<&Block>> = HashMap::new();
    
    for block in blocks {
        blocks_by_height
            .entry(block.header.number)
            .or_insert(Vec::new())
            .push(block);
    }
    
    // 检查同一高度是否有多个不同区块被同一验证者签名
    for (height, blocks) in blocks_by_height {
        if blocks.len() > 1 {
            // 检查是否有相同生产者的不同区块
            for i in 0..blocks.len() {
                for j in (i+1)..blocks.len() {
                    if blocks[i].header.producer == blocks[j].header.producer
                        && blocks[i].hash() != blocks[j].hash() {
                        
                        violations.push((
                            blocks[i].header.producer,
                            blocks[i].clone(),
                            blocks[j].clone(),
                        ));
                    }
                }
            }
        }
    }
    
    violations
}
```

## 安全分析

### 攻击成本分析

#### 51% 攻击
要控制网络，攻击者需要：

```
总贡献分数 = Σ(各维度贡献 × 权重)

假设攻击者只控制质押（30%权重）：
需要质押 = 总质押量 × 51% / 30% = 总质押量 × 170%

假设攻击者同时控制质押+算力（50%权重）：
需要质押+算力 = 总资源 × 51% / 50% = 总资源 × 102%

结论：多维度要求大幅提升攻击成本
```

#### 长程攻击（Long Range Attack）
防御措施：
- 检查点机制：定期保存不可逆检查点
- 弱主观性：新节点从社交共识获取初始状态
- 历史快照：定期归档历史状态

```rust
fn validate_chain_from_checkpoint(
    checkpoint: &Checkpoint,
    blocks: &[Block],
) -> bool {
    // 1. 验证检查点签名（需要 2/3 验证者签名）
    if !verify_checkpoint_signatures(checkpoint) {
        return false;
    }
    
    // 2. 从检查点后验证区块
    let mut state = checkpoint.state_root;
    
    for block in blocks {
        if block.header.number <= checkpoint.height {
            continue;  // 跳过检查点前的区块
        }
        
        if !verify_block(block, &state) {
            return false;
        }
        
        state = block.header.state_root;
    }
    
    true
}
```

#### Nothing-at-Stake 攻击
防御措施：
- 惩罚机制：双签会被罚没
- VRF 选举：无法预知自己何时出块，无法提前准备多个分叉

### 活性保证（Liveness）

即使部分验证者离线，网络仍能正常运行：

```rust
fn calculate_liveness_threshold() -> f64 {
    // 只要 1/3 贡献权重的验证者在线即可
    total_contribution_score() * 1.0 / 3.0
}

fn is_network_live(online_validators: &[ValidatorNode]) -> bool {
    let online_score: f64 = online_validators
        .iter()
        .map(|v| calculate_contribution_score(v))
        .sum();
    
    online_score >= calculate_liveness_threshold()
}
```

### 安全性保证（Safety）

防止分叉和双花：

```rust
// 最终性：2/3 验证者同意才能最终确认
fn finality_threshold() -> f64 {
    total_contribution_score() * 2.0 / 3.0
}

// 即使 1/3 恶意验证者也无法破坏安全性
// 因为无法达到 2/3 阈值
```

## 与其他共识机制对比

| 特性 | PoW | PoS | DPoS | PoC (QFC) |
|------|-----|-----|------|-----------|
| 能源效率 | ❌ 低 | ✅ 高 | ✅ 高 | ✅ 高 |
| 去中心化 | ✅ 强 | ⚠️ 中等 | ❌ 弱 | ✅ 强 |
| 性能 | ❌ 低 | ⚠️ 中等 | ✅ 高 | ✅ 极高 |
| 安全性 | ✅ 高 | ✅ 高 | ⚠️ 中等 | ✅ 极高 |
| 准入门槛 | 高（设备） | 高（资金） | 中（投票） | 低（多样化） |
| 抗审查 | ✅ 强 | ⚠️ 中等 | ❌ 弱 | ✅ 强 |
| 激励兼容 | ✅ 好 | ⚠️ 富者愈富 | ❌ 易操纵 | ✅ 公平 |

## 参数配置

### 主网参数（建议值）

```toml
[consensus]
# Epoch 配置
epoch_duration = 10  # 秒
blocks_per_epoch = 3  # 每 epoch 3个区块（约3.33秒/块）

# 验证者要求
min_stake = 10000  # 最小质押 10,000 QFC
max_validators = 1000  # 最多1000个活跃验证者

# 投票配置
vote_timeout = 5  # 秒
finality_threshold = 0.67  # 67% 权重确认

# 奖励
block_reward = 10  # QFC
reward_distribution = { producer = 0.70, voters = 0.30 }
fee_distribution = { producer = 0.50, voters = 0.30, burn = 0.20 }

# 惩罚
slash_double_sign = 0.50  # 罚没50%
slash_invalid_block = 0.10
slash_offline = 0.01
jail_duration_double_sign = "forever"
jail_duration_offline = "24h"

# 贡献权重
weights = { stake = 0.30, compute = 0.20, uptime = 0.15, accuracy = 0.15, network = 0.10, storage = 0.05, reputation = 0.05 }
```

### 测试网参数

```toml
[consensus]
epoch_duration = 5  # 更快的迭代
min_stake = 1000  # 降低门槛
block_reward = 100  # 更多测试币
slash_double_sign = 0.10  # 降低惩罚（测试用）
```

## 实施路线图

### Phase 1: 基础 PoS (Month 1-2)
- 简化版 PoC：只考虑质押权重
- VRF 选举机制
- 基础投票和最终性

### Phase 2: 多维度评分 (Month 3-4)
- 添加在线时长、验证准确率
- 实现历史信誉系统
- 测试网验证

### Phase 3: 可选贡献 (Month 5-6)
- 添加计算贡献（PoW 部分）
- 添加存储贡献
- 动态权重调整

### Phase 4: 优化与审计 (Month 7-9)
- 性能优化
- 安全审计
- 经济模型验证
- 主网准备

---

**最后更新**: 2026-02-01
**版本**: 1.0.0
**维护者**: QFC Core Team
