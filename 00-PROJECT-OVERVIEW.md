# QFC Blockchain - Project Overview

## 项目目标
构建一个高性能、低成本、量子抗性的新一代区块链系统

## 核心创新点

### 1. Proof of Contribution (PoC) 共识机制
- **多维度贡献评分系统**
  - 计算贡献 (30% 权重)
  - 质押贡献 (25% 权重)
  - 网络服务质量 (20% 权重)
  - 验证准确率 (15% 权重)
  - 历史信誉 (10% 权重)

- **动态权重调整**
  - 根据网络状态自动调整各维度权重
  - 应对不同场景（拥堵、攻击、正常运行）

- **激励兼容性**
  - 防止单点控制
  - 鼓励多样化贡献
  - 长期稳定性

### 2. 多虚拟机并行架构
- **QVM (Quantum Virtual Machine)** - 原生虚拟机
  - 专为高性能设计
  - 支持并行执行
  - 内置形式化验证
  
- **EVM 兼容层**
  - 100% Solidity 兼容
  - 自动优化
  - 无缝迁移
  
- **WASM VM**
  - 支持 Rust/C++/AssemblyScript
  - 近原生性能
  - 适合复杂计算
  
- **AI-VM**
  - AI 模型作为合约逻辑
  - 链上推理
  - 智能决策

### 3. 分层并行架构
```
执行层 (Execution Layer)    - 100,000+ TPS
    ↓ 异步通信
状态层 (State Layer)         - 即时状态同步
    ↓ Merkle证明
共识层 (Consensus Layer)     - 最终确定性
    ↓ 跨链桥接
存储层 (Storage Layer)       - 分布式永久存储
```

### 4. 动态分片技术
- 自适应分片（根据交易密度）
- 跨分片原子交易
- 分片安全池

## 性能指标

| 指标 | 目标值 | 对比 |
|------|--------|------|
| TPS | 500,000+ | Solana: ~65,000, ETH: ~15 |
| 确认时间 | <0.3秒 | BTC: ~10分钟, ETH: ~12秒 |
| Gas费 | <$0.0001 | ETH: $1-50 |
| 区块时间 | 3秒 | - |
| 最终确定性 | <10秒 | - |

## 技术栈

### 核心区块链
- **语言**: Rust (核心引擎) + Go (工具链)
- **数据库**: 
  - RocksDB (状态存储)
  - PostgreSQL (索引/查询)
  - Redis (缓存)
- **网络**: libp2p
- **共识**: 自研 PoC
- **加密**: 
  - 格基密码学 (量子抗性)
  - EdDSA (签名)
  - Blake3 (哈希)

### 智能合约
- **QVM**: 自研语言 QuantumScript
- **EVM**: Solidity 0.8+ 兼容
- **WASM**: Rust/AssemblyScript 支持

### 基础设施
- **区块浏览器**: 
  - Frontend: Next.js + React + TailwindCSS
  - Backend: Node.js + Express
  - Database: PostgreSQL + ElasticSearch
  - Indexer: Rust

- **钱包**: 
  - 浏览器插件: TypeScript + React + ethers.js
  - 移动端: React Native + Expo
  - Web钱包: Next.js
  
- **测试网**: 
  - 容器化: Docker + Docker Compose
  - 编排: Kubernetes
  - IaC: Terraform
  - 监控: Prometheus + Grafana

## 项目阶段

### Phase 1: 核心开发 (Month 1-3)
**目标**: 实现可运行的区块链原型

- [ ] 基础区块链框架
  - P2P 网络层 (libp2p)
  - 区块/交易数据结构
  - 状态管理 (Merkle Patricia Trie)
  
- [ ] PoC 共识引擎
  - 贡献评分算法
  - 区块生产逻辑
  - 投票机制
  
- [ ] RPC API
  - JSON-RPC 2.0
  - WebSocket 订阅
  - 批量请求支持

- [ ] 基础测试
  - 单元测试
  - 集成测试
  - 性能基准测试

**里程碑**: 3节点本地测试网运行

### Phase 2: 虚拟机开发 (Month 3-5)
**目标**: 实现智能合约执行能力

- [ ] QVM 设计与实现
  - QuantumScript 语言设计
  - 编译器开发
  - 虚拟机执行引擎
  - Gas 计量系统
  
- [ ] EVM 兼容层
  - Solidity 编译器集成
  - EVM 字节码解释器
  - 状态映射
  
- [ ] 跨 VM 调用
  - 统一接口层
  - 类型转换
  - Gas 计算
  
- [ ] 智能合约工具链
  - CLI 工具
  - 测试框架
  - 部署脚本

**里程碑**: 成功运行 Uniswap V2 合约

### Phase 3: 基础设施 (Month 4-6)
**目标**: 用户友好的生态工具

- [ ] 区块浏览器
  - 实时区块/交易展示
  - 地址/合约查询
  - 统计分析
  - API 服务
  
- [ ] 浏览器插件钱包
  - 账户管理
  - 交易签名
  - DApp 连接
  - 多链支持
  
- [ ] 移动端钱包
  - iOS + Android
  - 生物识别
  - WalletConnect
  
- [ ] 开发者工具
  - SDK (JS/Python/Rust)
  - 文档站点
  - 示例 DApp

**里程碑**: 完整的用户体验闭环

### Phase 4: 测试网 (Month 6-9)
**目标**: 大规模测试和社区建设

#### 4.1 内部测试网 (Week 1-2)
- [ ] 3-5个节点（团队控制）
- [ ] 核心功能验证
- [ ] Bug 修复

#### 4.2 公开测试网 (Week 3-12)
- [ ] 开放节点注册
- [ ] 50-100个节点
- [ ] 开发者 onboarding
- [ ] 收集反馈

#### 4.3 激励测试网 (Week 13-24)
- [ ] 1000+节点
- [ ] 空投激励计划
- [ ] 压力测试
- [ ] 安全审计

**里程碑**: 稳定运行3个月，无重大bug

### Phase 5: 主网准备 (Month 10-12)
**目标**: 主网启动

- [ ] 代码审计
  - 内部审计
  - 第三方安全公司审计（2-3家）
  - Bug Bounty 计划
  
- [ ] 主网参数确定
  - 创世区块配置
  - 代币经济学
  - 治理机制
  
- [ ] 社区准备
  - 验证者招募
  - 文档完善
  - 培训材料
  
- [ ] 启动准备
  - 监控系统
  - 应急预案
  - 客服支持

**里程碑**: 主网成功启动

## 代码仓库结构

```
qfc-blockchain/
├── core/                          # 核心区块链（Rust）
│   ├── consensus/                 # PoC 共识引擎
│   ├── network/                   # P2P 网络
│   ├── state/                     # 状态管理
│   ├── storage/                   # 数据存储
│   ├── rpc/                       # RPC 服务器
│   └── mempool/                   # 交易池
│
├── vm/                            # 虚拟机
│   ├── qvm/                       # QVM 实现
│   │   ├── compiler/              # QuantumScript 编译器
│   │   ├── runtime/               # 运行时
│   │   └── std/                   # 标准库
│   ├── evm/                       # EVM 兼容层
│   └── wasm/                      # WASM 支持
│
├── contracts/                     # 智能合约示例
│   ├── examples/                  # 示例合约
│   └── system/                    # 系统合约
│
├── tools/                         # CLI 工具
│   ├── qfc-cli/                   # 主 CLI
│   ├── genesis-tool/              # 创世块工具
│   └── key-manager/               # 密钥管理
│
├── explorer/                      # 区块浏览器
│   ├── frontend/                  # Web 前端
│   ├── backend/                   # API 后端
│   └── indexer/                   # 链上数据索引器
│
├── wallet/                        # 钱包
│   ├── extension/                 # 浏览器插件
│   │   ├── src/
│   │   │   ├── background/
│   │   │   ├── content/
│   │   │   ├── inpage/
│   │   │   └── popup/
│   │   └── public/
│   └── mobile/                    # 移动端 App
│       ├── ios/
│       ├── android/
│       └── src/
│
├── testnet/                       # 测试网配置
│   ├── docker/                    # Docker 配置
│   ├── k8s/                       # Kubernetes 配置
│   └── terraform/                 # Terraform 脚本
│
├── sdk/                           # SDK
│   ├── js/                        # JavaScript SDK
│   ├── python/                    # Python SDK
│   └── rust/                      # Rust SDK
│
└── docs/                          # 文档
    ├── architecture/              # 架构文档
    ├── specs/                     # 技术规范
    ├── tutorials/                 # 教程
    └── api/                       # API 文档
```

## 如何使用本文档与 Claude Code

### 初始化项目
```
我要开始开发 QFC 区块链项目。

请先阅读 docs/00-PROJECT-OVERVIEW.md 了解项目全貌。

我现在要开始 [具体模块]，请阅读相关设计文档：
- 钱包开发: docs/07-WALLET-DESIGN.md
- 共识机制: docs/02-CONSENSUS-MECHANISM.md
- 智能合约: docs/03-SMART-CONTRACT-SYSTEM.md
```

### 实现具体功能
```
根据 docs/07-WALLET-DESIGN.md 中的 "Phase 1: 浏览器插件钱包" 部分，
实现以下功能：

1. [具体需求]
2. [具体需求]

请提供：
- 完整代码实现
- 类型定义
- 错误处理
- 单元测试
```

### 引用具体章节
```
请实现 07-WALLET-DESIGN.md 的 "Provider 注入" 章节中描述的功能。

关键要求：
- 兼容 EIP-1193
- 支持事件监听
- 完整的错误处理
```

## 开发原则

### 1. 安全第一
- 密钥管理极其谨慎
- 交易签名多重验证
- 输入严格校验
- 防止常见攻击（重入、溢出、DOS）

### 2. 性能优先
- 目标 TPS 500k+
- 低延迟（<300ms）
- 资源高效利用
- 可扩展性设计

### 3. 模块化
- 清晰的模块边界
- 最小化依赖
- 独立可测试
- 易于替换

### 4. 文档驱动
- 代码必须有对应文档
- API 完整注释
- 示例代码
- 变更日志

### 5. 测试完备
- 单元测试覆盖率 >80%
- 集成测试
- 性能测试
- 安全测试

## 关键文件索引

- **项目总览**: `docs/00-PROJECT-OVERVIEW.md` (本文件)
- **区块链设计**: `docs/01-BLOCKCHAIN-DESIGN.md`
- **共识机制**: `docs/02-CONSENSUS-MECHANISM.md`
- **智能合约系统**: `docs/03-SMART-CONTRACT-SYSTEM.md`
- **节点运行**: `docs/04-NODE-OPERATION.md`
- **区块浏览器**: `docs/05-BLOCK-EXPLORER.md`
- **测试网搭建**: `docs/06-TESTNET-SETUP.md`
- **钱包设计**: `docs/07-WALLET-DESIGN.md`
- **实施计划**: `docs/08-IMPLEMENTATION-PLAN.md`
- **快速开始**: `docs/START-HERE.md`

## 团队协作

### 角色分工
- **核心开发**: Rust 区块链引擎
- **虚拟机开发**: 智能合约执行
- **前端开发**: 钱包、浏览器
- **DevOps**: 测试网、监控
- **安全审计**: 代码审计、渗透测试
- **文档**: 技术文档、教程

### 开发流程
1. 阅读相关设计文档
2. 创建 feature 分支
3. 实现 + 测试
4. Code Review
5. 合并到 main

### 沟通渠道
- GitHub Issues: Bug 报告、功能请求
- Discord: 实时讨论
- 周会: 进度同步

## 预算估算

### 开发成本（12个月）
- 核心团队（6人）: $1,200,000/年
- 审计费用: $100,000
- 基础设施: $50,000/年
- 总计: ~$1,350,000

### 运营成本（年度）
- 测试网: $20,000
- 主网基础设施: $100,000
- 营销推广: $200,000
- 社区运营: $50,000
- 总计: ~$370,000

## 风险与应对

### 技术风险
- **共识机制未验证**: 长期测试网运行
- **性能未达标**: 持续优化和基准测试
- **安全漏洞**: 多家审计 + Bug Bounty

### 市场风险
- **竞争激烈**: 专注独特价值（PoC + 性能）
- **监管不确定**: 合规设计，法律咨询

### 团队风险
- **人员流失**: 激励机制，代币期权
- **技术债务**: 代码质量优先，持续重构

## 成功标准

### 技术指标
- ✅ TPS >500,000
- ✅ 确认时间 <0.3秒
- ✅ 测试网稳定运行 >3个月
- ✅ 安全审计通过

### 生态指标
- ✅ 活跃开发者 >100
- ✅ 部署智能合约 >1,000
- ✅ 日活地址 >10,000
- ✅ TVL >$10M

### 社区指标
- ✅ Discord成员 >5,000
- ✅ Twitter关注 >20,000
- ✅ GitHub Stars >1,000

---

**最后更新**: 2026-02-01
**版本**: 1.0.0
**维护者**: QFC Core Team
