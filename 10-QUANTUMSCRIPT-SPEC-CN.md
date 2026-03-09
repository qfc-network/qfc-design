# QuantumScript 语言规范

> 版本: 0.1.0 (草案)
> 最后更新: 2026-02-02

## 1. 概述

QuantumScript 是一种为 QFC 区块链原生虚拟机 (QVM) 设计的领域特定语言。它优先考虑安全性、性能和开发者体验，同时支持 QFC 生态系统独有的特性。

### 1.1 设计目标

| 目标 | 描述 |
|------|------|
| **安全优先** | 内存安全、类型安全、无未定义行为 |
| **高性能** | 编译为优化的 QVM 字节码，支持并行执行 |
| **形式化验证** | 内置合约验证支持 |
| **开发者友好** | 简洁的语法、有用的错误信息、熟悉的编程模式 |
| **区块链原生** | 一等公民级别的加密、状态和资产支持 |
| **EVM 互操作** | 与 Solidity 合约的无缝双向调用 |

### 1.2 设计影响来源

- **Rust**: 所有权模型、类型系统、错误处理
- **TypeScript**: 语法熟悉度、类型注解
- **Move**: 面向资源编程、线性类型
- **Solidity**: 合约结构、修饰器模式

---

## 2. 词法结构

### 2.1 关键字

```
// 声明
contract    interface   struct      enum        type
fn          let         const       mut         pub
import      from        as          mod

// 控制流
if          else        match       for         while
loop        break       continue    return      yield

// 类型
bool        u8          u16         u32         u64         u128        u256
i8          i16         i32         i64         i128        i256
f32         f64
string      bytes       address     hash

// 区块链
state       event       error       modifier    require
emit        revert      assert      self        caller
msg         block       tx

// 资源与安全
resource    move        copy        drop        store
pure        view        payable     parallel

// 验证
invariant   ensures     requires    spec
```

### 2.2 运算符

```
// 算术运算
+   -   *   /   %   **

// 比较运算
==  !=  <   >   <=  >=

// 逻辑运算
&&  ||  !

// 位运算
&   |   ^   ~   <<  >>

// 赋值运算
=   +=  -=  *=  /=  %=

// 其他
.   ::  ->  =>  ?   ??  ..  ...
```

### 2.3 注释

```typescript
// 单行注释

/*
 * 多行注释
 */

/// 文档注释（用于函数、合约）
/// 支持 markdown

//! 模块级文档注释
```

---

## 3. 类型系统

### 3.1 基本类型

```typescript
// 无符号整数
u8      // 0 到 255
u16     // 0 到 65,535
u32     // 0 到 4,294,967,295
u64     // 0 到 18,446,744,073,709,551,615
u128    // 0 到 2^128 - 1
u256    // 0 到 2^256 - 1（金额的默认类型）

// 有符号整数
i8, i16, i32, i64, i128, i256

// 浮点数（仅用于链下计算）
f32, f64

// 布尔类型
bool    // true 或 false

// 区块链类型
address     // 20 字节账户地址
hash        // 32 字节哈希值（Blake3）
bytes       // 动态字节数组
string      // UTF-8 字符串
```

### 3.2 复合类型

```typescript
// 数组（固定大小）
let arr: [u256; 10] = [0; 10];

// 向量（动态大小）
let vec: Vec<u256> = Vec::new();

// 元组
let tuple: (u256, address, bool) = (100, addr, true);

// 映射（仅用于状态）
state balances: Map<address, u256>;

// 可选类型
let maybe: Option<u256> = Some(42);

// 结果类型
let result: Result<u256, Error> = Ok(42);
```

### 3.3 自定义类型

```typescript
// 结构体
struct Token {
    name: string,
    symbol: string,
    decimals: u8,
    total_supply: u256,
}

// 枚举
enum OrderStatus {
    Pending,
    Filled { amount: u256 },
    Cancelled { reason: string },
}

// 类型别名
type Amount = u256;
type TokenId = u256;
```

### 3.4 资源类型

资源是线性类型，不能被复制或隐式丢弃——必须显式移动或消耗。

```typescript
// 定义资源
resource Coin {
    amount: u256,
}

// 资源必须移动，不能复制
fn transfer(coin: Coin, to: address) {
    // coin 在此处被移动，原始绑定失效
    deposit(to, move coin);
}

// 需要显式丢弃
fn burn(coin: Coin) {
    drop coin;  // 显式销毁
    emit Burned { amount: coin.amount };
}
```

---

## 4. 合约结构

### 4.1 基本合约

```typescript
/// 一个简单的代币合约
contract Token {
    // 状态变量（持久化存储）
    state owner: address;
    state name: string;
    state symbol: string;
    state decimals: u8;
    state total_supply: u256;
    state balances: Map<address, u256>;
    state allowances: Map<address, Map<address, u256>>;

    // 事件
    event Transfer {
        from: address,
        to: address,
        amount: u256,
    }

    event Approval {
        owner: address,
        spender: address,
        amount: u256,
    }

    // 错误
    error InsufficientBalance { available: u256, required: u256 }
    error Unauthorized { caller: address }
    error ZeroAddress;

    // 构造函数
    pub fn init(name: string, symbol: string, initial_supply: u256) {
        self.owner = caller;
        self.name = name;
        self.symbol = symbol;
        self.decimals = 18;
        self.total_supply = initial_supply;
        self.balances[caller] = initial_supply;

        emit Transfer { from: address(0), to: caller, amount: initial_supply };
    }

    // 视图函数（不修改状态）
    pub view fn balance_of(account: address) -> u256 {
        self.balances[account]
    }

    // 状态修改函数
    pub fn transfer(to: address, amount: u256) -> bool {
        require(to != address(0), ZeroAddress);
        require(self.balances[caller] >= amount, InsufficientBalance {
            available: self.balances[caller],
            required: amount,
        });

        self.balances[caller] -= amount;
        self.balances[to] += amount;

        emit Transfer { from: caller, to, amount };
        true
    }
}
```

### 4.2 修饰器

```typescript
contract Ownable {
    state owner: address;

    error NotOwner { caller: address, owner: address }

    // 定义修饰器
    modifier only_owner {
        require(caller == self.owner, NotOwner {
            caller: caller,
            owner: self.owner
        });
        _; // 被修饰函数体的占位符
    }

    // 使用修饰器
    #[only_owner]
    pub fn set_owner(new_owner: address) {
        self.owner = new_owner;
    }
}
```

### 4.3 接口

```typescript
interface IERC20 {
    fn total_supply() -> u256;
    fn balance_of(account: address) -> u256;
    fn transfer(to: address, amount: u256) -> bool;
    fn allowance(owner: address, spender: address) -> u256;
    fn approve(spender: address, amount: u256) -> bool;
    fn transfer_from(from: address, to: address, amount: u256) -> bool;

    event Transfer { from: address, to: address, amount: u256 }
    event Approval { owner: address, spender: address, amount: u256 }
}

contract MyToken impl IERC20 {
    // 必须实现所有接口函数
}
```

### 4.4 合约继承

```typescript
contract Base {
    state value: u256;

    pub virtual fn get_value() -> u256 {
        self.value
    }
}

contract Derived extends Base {
    pub override fn get_value() -> u256 {
        self.value * 2
    }
}
```

---

## 5. 函数

### 5.1 函数类型

```typescript
// 纯函数：不读写状态，确定性
pure fn add(a: u256, b: u256) -> u256 {
    a + b
}

// 视图函数：只读状态，不写入
view fn get_balance(addr: address) -> u256 {
    self.balances[addr]
}

// 默认函数：可读写状态
fn transfer(to: address, amount: u256) {
    self.balances[caller] -= amount;
    self.balances[to] += amount;
}

// 可支付函数：可接收原生代币
payable fn deposit() {
    self.balances[caller] += msg.value;
}

// 并行函数：可安全并行执行
parallel fn compute_hash(data: bytes) -> hash {
    blake3(data)
}
```

### 5.2 错误处理

```typescript
// 使用 Result 类型
fn safe_divide(a: u256, b: u256) -> Result<u256, Error> {
    if b == 0 {
        Err(Error::DivisionByZero)
    } else {
        Ok(a / b)
    }
}

// 使用 require（失败时回滚）
fn withdraw(amount: u256) {
    require(self.balances[caller] >= amount, InsufficientBalance {
        available: self.balances[caller],
        required: amount,
    });

    self.balances[caller] -= amount;
    // 转移原生代币
    caller.transfer(amount);
}

// 使用 assert（用于不变量检查）
fn internal_transfer(from: address, to: address, amount: u256) {
    let from_balance = self.balances[from];
    let to_balance = self.balances[to];

    self.balances[from] -= amount;
    self.balances[to] += amount;

    // 不变量：总余额不变
    assert(self.balances[from] + self.balances[to] == from_balance + to_balance);
}
```

### 5.3 闭包与高阶函数

```typescript
fn filter_positive(numbers: Vec<i256>) -> Vec<i256> {
    numbers.filter(|n| n > 0)
}

fn map_double(numbers: Vec<u256>) -> Vec<u256> {
    numbers.map(|n| n * 2)
}

fn reduce_sum(numbers: Vec<u256>) -> u256 {
    numbers.reduce(0, |acc, n| acc + n)
}
```

---

## 6. 控制流

### 6.1 条件语句

```typescript
// If-else
if balance > 0 {
    transfer(to, balance);
} else {
    revert InsufficientBalance;
}

// If-let（模式匹配）
if let Some(value) = maybe_value {
    process(value);
}

// Match 表达式
match status {
    OrderStatus::Pending => process_pending(),
    OrderStatus::Filled { amount } => settle(amount),
    OrderStatus::Cancelled { reason } => log_cancellation(reason),
}
```

### 6.2 循环

```typescript
// For 循环（范围）
for i in 0..10 {
    process(i);
}

// For 循环（迭代器）
for (addr, balance) in self.balances.iter() {
    if balance > threshold {
        notify(addr);
    }
}

// While 循环
while condition {
    step();
}

// 带 break 的循环
loop {
    if done {
        break;
    }
    work();
}
```

### 6.3 提前返回

```typescript
fn find_holder(target_balance: u256) -> Option<address> {
    for (addr, balance) in self.balances.iter() {
        if balance >= target_balance {
            return Some(addr);
        }
    }
    None
}
```

---

## 7. 内存模型

### 7.1 存储布局

```typescript
contract StorageExample {
    // 槽位 0：简单值打包存储
    state a: u128;      // 槽位 0，字节 0-15
    state b: u64;       // 槽位 0，字节 16-23
    state c: u64;       // 槽位 0，字节 24-31

    // 槽位 1：地址（20 字节 + 填充）
    state owner: address;

    // 动态：映射存储在 keccak(slot . key)
    state balances: Map<address, u256>;

    // 动态：向量存储在 keccak(slot)，长度存储在 slot
    state holders: Vec<address>;
}
```

### 7.2 内存与存储

```typescript
fn example() {
    // 内存：临时的，开销低
    let local_array: [u256; 10] = [0; 10];

    // 存储：持久化的，开销高
    self.stored_array[0] = 42;

    // 从存储显式复制到内存
    let cached = self.balances[caller];  // 读取一次

    // 多次读取优化
    let balance = cached;  // 使用内存副本
}
```

### 7.3 所有权与借用

```typescript
// 资源的移动语义
fn consume_coin(coin: Coin) {
    // coin 被移动，调用者失去所有权
    self.vault.deposit(coin);
}

// 借用（只读引用）
fn inspect_coin(coin: &Coin) -> u256 {
    coin.amount  // 可以读取但不能修改
}

// 可变借用
fn modify_coin(coin: &mut Coin) {
    coin.amount += 10;  // 可以修改
}
```

---

## 8. 并行执行

### 8.1 并行注解

```typescript
// 标记函数为可安全并行执行
parallel fn compute_merkle_root(leaves: Vec<hash>) -> hash {
    // 无共享可变状态
    // 确定性计算
    merkle_tree(leaves)
}

// 并行映射
fn batch_verify(signatures: Vec<Signature>) -> Vec<bool> {
    signatures.parallel_map(|sig| verify(sig))
}
```

### 8.2 状态访问提示

```typescript
// 声明访问哪些状态槽位
#[reads(balances[from], balances[to])]
#[writes(balances[from], balances[to])]
fn transfer(from: address, to: address, amount: u256) {
    self.balances[from] -= amount;
    self.balances[to] += amount;
}
```

### 8.3 冲突检测

QVM 使用乐观并发控制：

1. 并行执行交易
2. 检测读写冲突
3. 顺序重新执行冲突交易

---

## 9. 形式化验证

### 9.1 规范说明

```typescript
contract VerifiedToken {
    state balances: Map<address, u256>;
    state total_supply: u256;

    // 不变量：所有余额之和等于总供应量
    spec invariant total_supply_correct {
        sum(self.balances.values()) == self.total_supply
    }

    // 函数规范
    #[requires(amount <= self.balances[caller])]
    #[ensures(self.balances[caller] == old(self.balances[caller]) - amount)]
    #[ensures(self.balances[to] == old(self.balances[to]) + amount)]
    pub fn transfer(to: address, amount: u256) {
        self.balances[caller] -= amount;
        self.balances[to] += amount;
    }
}
```

### 9.2 属性测试

```typescript
#[test]
#[property]
fn transfer_preserves_total(
    balances: Map<address, u256>,
    from: address,
    to: address,
    amount: u256,
) {
    assume(balances[from] >= amount);

    let total_before = sum(balances.values());
    transfer(from, to, amount);
    let total_after = sum(self.balances.values());

    assert(total_before == total_after);
}
```

---

## 10. EVM 互操作性

### 10.1 调用 EVM 合约

```typescript
// 导入 EVM 合约接口
import { IERC20 } from "evm:0x1234...";

fn interact_with_evm() {
    let usdc = IERC20(address(0x1234...));

    // 调用 EVM 合约
    let balance = usdc.balance_of(caller);

    // 授权并转账
    usdc.approve(self.address, 1000);
}
```

### 10.2 暴露给 EVM

```typescript
// 生成 EVM 兼容的 ABI
#[evm_compatible]
contract Bridge {
    // 此函数可以从 Solidity 调用
    pub fn deposit(token: address, amount: u256) {
        // ...
    }
}
```

### 10.3 跨虚拟机调用

```typescript
// 从 QuantumScript 调用任意虚拟机
fn cross_vm_example() {
    // 调用 EVM 合约
    let result1 = evm::call(evm_contract, "transfer", [to, amount]);

    // 调用 WASM 合约
    let result2 = wasm::call(wasm_contract, "compute", [data]);
}
```

---

## 11. 标准库

### 11.1 核心模块

```typescript
// 数学运算
mod math {
    fn min<T: Ord>(a: T, b: T) -> T;
    fn max<T: Ord>(a: T, b: T) -> T;
    fn pow(base: u256, exp: u256) -> u256;
    fn sqrt(n: u256) -> u256;
    fn log2(n: u256) -> u256;
}

// 密码学
mod crypto {
    fn blake3(data: bytes) -> hash;
    fn keccak256(data: bytes) -> hash;
    fn ed25519_verify(msg: bytes, sig: Signature, pubkey: PublicKey) -> bool;
    fn dilithium_verify(msg: bytes, sig: bytes, pubkey: bytes) -> bool;  // 后量子
}

// 地址工具
mod address {
    fn is_contract(addr: address) -> bool;
    fn code_hash(addr: address) -> hash;
    fn balance(addr: address) -> u256;
}

// 编码
mod encoding {
    fn abi_encode<T>(value: T) -> bytes;
    fn abi_decode<T>(data: bytes) -> Result<T, Error>;
    fn json_encode<T>(value: T) -> string;
    fn json_decode<T>(data: string) -> Result<T, Error>;
}
```

### 11.2 集合

```typescript
mod collections {
    // 动态数组
    struct Vec<T> {
        fn new() -> Vec<T>;
        fn push(&mut self, item: T);
        fn pop(&mut self) -> Option<T>;
        fn len(&self) -> u256;
        fn get(&self, index: u256) -> Option<&T>;
    }

    // 哈希映射
    struct Map<K, V> {
        fn new() -> Map<K, V>;
        fn insert(&mut self, key: K, value: V);
        fn get(&self, key: &K) -> Option<&V>;
        fn remove(&mut self, key: &K) -> Option<V>;
        fn contains(&self, key: &K) -> bool;
    }

    // 哈希集合
    struct Set<T> {
        fn new() -> Set<T>;
        fn insert(&mut self, item: T) -> bool;
        fn remove(&mut self, item: &T) -> bool;
        fn contains(&self, item: &T) -> bool;
    }
}
```

### 11.3 代币标准

```typescript
mod standards {
    // QRC-20（等同于 ERC-20）
    interface QRC20 {
        fn name() -> string;
        fn symbol() -> string;
        fn decimals() -> u8;
        fn total_supply() -> u256;
        fn balance_of(account: address) -> u256;
        fn transfer(to: address, amount: u256) -> bool;
        fn allowance(owner: address, spender: address) -> u256;
        fn approve(spender: address, amount: u256) -> bool;
        fn transfer_from(from: address, to: address, amount: u256) -> bool;
    }

    // QRC-721（NFT）
    interface QRC721 {
        fn balance_of(owner: address) -> u256;
        fn owner_of(token_id: u256) -> address;
        fn transfer_from(from: address, to: address, token_id: u256);
        fn approve(to: address, token_id: u256);
        fn get_approved(token_id: u256) -> address;
    }
}
```

---

## 12. Gas 模型

### 12.1 Gas 成本

| 操作 | Gas 成本 | 描述 |
|------|----------|------|
| ADD, SUB | 1 | 算术运算 |
| MUL | 2 | 乘法 |
| DIV | 3 | 除法 |
| SLOAD | 100 | 存储读取 |
| SSTORE (新建) | 10000 | 存储写入（新槽位） |
| SSTORE (更新) | 2900 | 存储写入（已有槽位） |
| CALL | 100 + gas | 外部调用 |
| CREATE | 32000 | 合约创建 |
| BLAKE3 | 30 + 6/字 | 哈希计算 |
| VERIFY_SIG | 3000 | 签名验证 |

### 12.2 Gas 优化

```typescript
// 缓存存储读取
fn optimized_transfer(to: address, amount: u256) {
    let sender_balance = self.balances[caller];  // 1 次 SLOAD
    require(sender_balance >= amount);

    self.balances[caller] = sender_balance - amount;  // 1 次 SSTORE
    self.balances[to] += amount;  // 1 次 SLOAD + 1 次 SSTORE
}

// 批量操作
fn batch_transfer(recipients: Vec<(address, u256)>) {
    let mut sender_balance = self.balances[caller];

    for (to, amount) in recipients {
        require(sender_balance >= amount);
        sender_balance -= amount;
        self.balances[to] += amount;
    }

    self.balances[caller] = sender_balance;  // 最后只写入一次
}
```

---

## 13. 工具链

### 13.1 编译器 (qsc)

```bash
# 编译为 QVM 字节码
qsc compile contract.qs -o contract.qvm

# 优化编译
qsc compile contract.qs -O3 -o contract.qvm

# 生成 ABI
qsc abi contract.qs -o contract.abi.json

# 仅类型检查
qsc check contract.qs

# 格式化代码
qsc fmt contract.qs
```

### 13.2 包管理器 (qpm)

```bash
# 初始化项目
qpm init my-project

# 添加依赖
qpm add @qfc/token-standards

# 构建项目
qpm build

# 运行测试
qpm test

# 部署到测试网
qpm deploy --network testnet
```

### 13.3 IDE 支持

- **VSCode 扩展**: 语法高亮、自动补全、错误检查
- **语言服务器 (LSP)**: 实时诊断、跳转到定义
- **调试器**: 逐步执行、状态检查

---

## 14. 示例合约

### 14.1 简单代币

```typescript
//! QRC-20 代币实现

import { QRC20 } from "std:standards";

contract SimpleToken impl QRC20 {
    state name: string;
    state symbol: string;
    state decimals: u8;
    state total_supply: u256;
    state balances: Map<address, u256>;
    state allowances: Map<address, Map<address, u256>>;

    event Transfer { from: address, to: address, amount: u256 }
    event Approval { owner: address, spender: address, amount: u256 }

    error InsufficientBalance { available: u256, required: u256 }
    error InsufficientAllowance { available: u256, required: u256 }

    pub fn init(name: string, symbol: string, initial_supply: u256) {
        self.name = name;
        self.symbol = symbol;
        self.decimals = 18;
        self.total_supply = initial_supply;
        self.balances[caller] = initial_supply;

        emit Transfer { from: address(0), to: caller, amount: initial_supply };
    }

    pub view fn name() -> string { self.name }
    pub view fn symbol() -> string { self.symbol }
    pub view fn decimals() -> u8 { self.decimals }
    pub view fn total_supply() -> u256 { self.total_supply }

    pub view fn balance_of(account: address) -> u256 {
        self.balances[account]
    }

    pub view fn allowance(owner: address, spender: address) -> u256 {
        self.allowances[owner][spender]
    }

    pub fn transfer(to: address, amount: u256) -> bool {
        self._transfer(caller, to, amount);
        true
    }

    pub fn approve(spender: address, amount: u256) -> bool {
        self.allowances[caller][spender] = amount;
        emit Approval { owner: caller, spender, amount };
        true
    }

    pub fn transfer_from(from: address, to: address, amount: u256) -> bool {
        let current_allowance = self.allowances[from][caller];
        require(current_allowance >= amount, InsufficientAllowance {
            available: current_allowance,
            required: amount,
        });

        self.allowances[from][caller] = current_allowance - amount;
        self._transfer(from, to, amount);
        true
    }

    fn _transfer(from: address, to: address, amount: u256) {
        let from_balance = self.balances[from];
        require(from_balance >= amount, InsufficientBalance {
            available: from_balance,
            required: amount,
        });

        self.balances[from] = from_balance - amount;
        self.balances[to] += amount;

        emit Transfer { from, to, amount };
    }
}
```

### 14.2 质押池

```typescript
//! 基于时间加权奖励的质押池

contract StakingPool {
    state staking_token: address;
    state reward_token: address;
    state reward_rate: u256;        // 每秒奖励
    state last_update_time: u256;
    state reward_per_token_stored: u256;
    state total_staked: u256;

    state stakes: Map<address, u256>;
    state user_reward_per_token_paid: Map<address, u256>;
    state rewards: Map<address, u256>;

    event Staked { user: address, amount: u256 }
    event Withdrawn { user: address, amount: u256 }
    event RewardPaid { user: address, reward: u256 }

    error InsufficientStake { available: u256, required: u256 }

    modifier update_reward(account: address) {
        self.reward_per_token_stored = self.reward_per_token();
        self.last_update_time = block.timestamp;

        if account != address(0) {
            self.rewards[account] = self.earned(account);
            self.user_reward_per_token_paid[account] = self.reward_per_token_stored;
        }
        _;
    }

    pub view fn reward_per_token() -> u256 {
        if self.total_staked == 0 {
            return self.reward_per_token_stored;
        }

        self.reward_per_token_stored +
            (block.timestamp - self.last_update_time) * self.reward_rate * 1e18 / self.total_staked
    }

    pub view fn earned(account: address) -> u256 {
        self.stakes[account] *
            (self.reward_per_token() - self.user_reward_per_token_paid[account]) / 1e18 +
            self.rewards[account]
    }

    #[update_reward(caller)]
    pub fn stake(amount: u256) {
        require(amount > 0, "Cannot stake 0");

        self.total_staked += amount;
        self.stakes[caller] += amount;

        // 从调用者转入代币
        QRC20(self.staking_token).transfer_from(caller, self.address, amount);

        emit Staked { user: caller, amount };
    }

    #[update_reward(caller)]
    pub fn withdraw(amount: u256) {
        require(self.stakes[caller] >= amount, InsufficientStake {
            available: self.stakes[caller],
            required: amount,
        });

        self.total_staked -= amount;
        self.stakes[caller] -= amount;

        QRC20(self.staking_token).transfer(caller, amount);

        emit Withdrawn { user: caller, amount };
    }

    #[update_reward(caller)]
    pub fn claim_reward() {
        let reward = self.rewards[caller];
        if reward > 0 {
            self.rewards[caller] = 0;
            QRC20(self.reward_token).transfer(caller, reward);
            emit RewardPaid { user: caller, reward };
        }
    }
}
```

---

## 15. 从 Solidity 迁移

### 15.1 语法对照

| Solidity | QuantumScript |
|----------|---------------|
| `uint256` | `u256` |
| `mapping(address => uint)` | `Map<address, u256>` |
| `function foo() public view` | `pub view fn foo()` |
| `require(cond, "msg")` | `require(cond, Error)` |
| `msg.sender` | `caller` |
| `msg.value` | `msg.value` |
| `block.timestamp` | `block.timestamp` |
| `emit Event(...)` | `emit Event { ... }` |

### 15.2 迁移工具

```bash
# 将 Solidity 转换为 QuantumScript
qsc migrate MyContract.sol -o MyContract.qs

# 手动审查和调整
# QuantumScript 具有更严格的类型安全
```

---

## 16. 未来扩展

### 16.1 计划中的特性

- **Async/Await**: 异步跨合约调用
- **泛型**: 参数化类型和函数
- **宏**: 编译时代码生成
- **Trait**: 类似 Rust 的 trait 系统
- **零知识证明**: 内置 ZK 证明支持

### 16.2 研究方向

- **形式化验证**: 自动化证明生成
- **AI 集成**: 合约内执行机器学习模型
- **抗量子计算**: 后量子签名方案

---

## 附录 A: 语法 (EBNF)

```ebnf
program         = { import_decl | contract_decl | interface_decl }
contract_decl   = "contract" IDENT [ "extends" IDENT ] [ "impl" IDENT { "," IDENT } ] "{" { contract_item } "}"
contract_item   = state_decl | event_decl | error_decl | modifier_decl | function_decl
state_decl      = "state" IDENT ":" type ";"
function_decl   = [ visibility ] [ fn_modifier ] "fn" IDENT "(" params ")" [ "->" type ] block
visibility      = "pub"
fn_modifier     = "view" | "pure" | "payable" | "parallel"
type            = primitive_type | array_type | map_type | custom_type
primitive_type  = "bool" | "u8" | ... | "u256" | "address" | "hash" | "string" | "bytes"
```

---

## 附录 B: 字节码格式

QVM 字节码采用基于栈的架构，类似于 EVM，但扩展了并行执行和资源类型的支持。

```
字节码头部:
  magic:    0x51564D31 ("QVM1")
  version:  u16
  flags:    u16 (parallel_safe, verified, 等)

代码段:
  instructions: [Instruction]

数据段:
  constants: [Constant]

元数据段:
  abi: JSON
  source_map: Optional
```

---

**文档状态**: 草案
**后续步骤**:
1. 实现词法分析器/语法分析器
2. 设计 QVM 指令集
3. 构建类型检查器
4. 开发代码生成器 (LLVM)
