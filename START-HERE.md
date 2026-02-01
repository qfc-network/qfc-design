# QFC Blockchain - 快速开始指南

> **给 Claude Code 的第一条指令**

## 项目简介

嗨 Claude Code！我要开发 **QFC 区块链项目**。

**QFC** 是一个高性能区块链，核心创新包括：
- ✨ **PoC (Proof of Contribution)** 共识机制 - 多维度贡献评分
- 🚀 **多虚拟机架构** - QVM + EVM + WASM + AI-VM
- ⚡ **极致性能** - 目标 TPS 500k+，确认时间 <0.3秒
- 🔐 **量子抗性** - 格基密码学

## 文档结构

所有设计文档都在 `docs/` 目录：

```
docs/
├── 00-PROJECT-OVERVIEW.md          # 📋 项目总览（必读）
├── 01-BLOCKCHAIN-DESIGN.md         # ⛓️ 区块链核心设计
├── 02-CONSENSUS-MECHANISM.md       # 🎯 PoC 共识机制详解
├── 03-SMART-CONTRACT-SYSTEM.md     # 📝 智能合约系统
├── 04-NODE-OPERATION.md            # 🖥️ 节点运行
├── 05-BLOCK-EXPLORER.md            # 🔍 区块浏览器
├── 06-TESTNET-SETUP.md             # 🧪 测试网搭建
├── 07-WALLET-DESIGN.md             # 💼 钱包设计
└── START-HERE.md                   # 👉 本文件
```

## 当前任务：浏览器插件钱包

**为什么先做钱包？**
- 开发者需要它来测试 DApp
- 快速验证区块链 RPC 接口
- 低成本快速迭代
- 桌面用户体验好

**目标交付物：**
- Chrome/Firefox 浏览器插件
- 类似 MetaMask 的体验
- 支持 QFC 测试网

---

## 第一步：阅读设计文档

在开始编码之前，请**务必**阅读以下文档：

### 必读文档
1. **`00-PROJECT-OVERVIEW.md`** - 了解项目全貌
   - 核心创新点
   - 技术栈
   - 项目阶段
   
2. **`07-WALLET-DESIGN.md`** - 钱包完整设计
   - 技术架构
   - 目录结构
   - 核心代码示例
   - 安全要求

### 建议阅读
3. **`02-CONSENSUS-MECHANISM.md`** - 理解 QFC 的独特之处
4. **`06-TESTNET-SETUP.md`** - 了解测试网配置

---

## 第二步：初始化项目

### 项目结构

```bash
qfc-blockchain/
├── wallet/
│   └── extension/              # 👈 我们从这里开始
│       ├── src/
│       │   ├── background/     # 后台服务（密钥管理、交易签名）
│       │   ├── content/        # 内容脚本（注入网页）
│       │   ├── inpage/         # window.qfc Provider
│       │   ├── popup/          # 弹窗 UI
│       │   └── utils/          # 工具函数
│       ├── public/
│       │   ├── manifest.json   # Chrome 扩展配置
│       │   └── icons/
│       ├── package.json
│       ├── tsconfig.json
│       ├── vite.config.ts
│       └── README.md
```

### 技术栈

- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Styling**: TailwindCSS
- **State**: Zustand
- **Crypto**: ethers.js v6
- **Storage**: chrome.storage.local

---

## 第三步：开始实现

### 实施计划

#### Phase 1: 项目框架 (Day 1-2)

**任务：**
```
请帮我初始化浏览器钱包项目：

1. 创建项目结构
   cd wallet/extension
   npm create vite@latest . -- --template react-ts
   
2. 安装依赖
   - ethers@^6.0.0
   - @types/chrome
   - tailwindcss
   - zustand
   - lucide-react (图标)

3. 配置 Vite 用于 Chrome 扩展构建
   - 多入口点（popup, background, content, inpage）
   - 输出格式配置
   - manifest.json 处理

4. 创建基础目录结构
   按照 07-WALLET-DESIGN.md 中的目录结构

5. 创建 manifest.json
   参考设计文档中的配置
```

**验收标准：**
- ✅ `npm run build` 成功
- ✅ 可以在 Chrome 加载扩展（chrome://extensions）
- ✅ 点击图标能弹出空白 popup

#### Phase 2: Provider 注入 (Day 3-4)

**任务：**
```
实现 window.qfc Provider：

参考 07-WALLET-DESIGN.md 的 "inpage/provider.ts" 章节

要求：
1. 实现 EIP-1193 标准接口
2. 支持方法：
   - eth_requestAccounts
   - eth_accounts
   - eth_chainId
   - eth_sendTransaction
   - personal_sign
   - eth_signTypedData_v4

3. 事件支持：
   - accountsChanged
   - chainChanged
   - connect
   - disconnect

4. 与 background 的消息通信

5. 兼容 MetaMask（设置 window.ethereum）
```

**测试：**
创建一个简单的测试页面：
```html
<!DOCTYPE html>
<html>
<body>
  <button onclick="connect()">Connect Wallet</button>
  <script>
    async function connect() {
      const accounts = await window.qfc.request({
        method: 'eth_requestAccounts'
      });
      console.log('Connected:', accounts);
    }
  </script>
</body>
</html>
```

#### Phase 3: Background Service (Day 5-7)

**任务：**
```
实现后台钱包管理：

参考 07-WALLET-DESIGN.md 的 "background/WalletController.ts" 章节

核心功能：
1. 钱包管理
   - createWallet() - 创建新钱包
   - importWallet() - 导入钱包（私钥/助记词）
   - getAllAccounts() - 获取所有账户
   - switchAccount() - 切换账户

2. 认证
   - unlock() - 解锁钱包
   - lock() - 锁定钱包
   - 30分钟自动锁定

3. 交易
   - sendTransaction() - 发送交易
   - signMessage() - 签名消息
   - signTypedData() - 签名结构化数据

4. 查询
   - getBalance() - 获取余额
   - 与 RPC 节点通信

安全要求：
- 私钥加密存储（使用 crypto.ts）
- 密码永不保存
- 敏感操作重置自动锁定计时器
```

#### Phase 4: Popup UI (Day 8-10)

**任务：**
```
实现用户界面：

参考 07-WALLET-DESIGN.md 的 "popup/pages" 章节

页面：
1. CreateWallet.tsx - 创建钱包
   - 生成助记词
   - 设置密码
   - 备份提醒

2. ImportWallet.tsx - 导入钱包
   - 输入助记词/私钥
   - 设置密码

3. Unlock.tsx - 解锁页面
   - 输入密码
   - 错误提示

4. Home.tsx - 主页
   - 显示余额
   - 资产列表
   - 快速操作（发送/接收）
   - 最近交易

5. Send.tsx - 发送页面
   - 输入收款地址
   - 输入金额
   - Gas 设置
   - 确认

6. Settings.tsx - 设置页面
   - 账户管理
   - 网络切换
   - 锁定钱包

设计要求：
- 使用 TailwindCSS
- 响应式（400x600px 弹窗）
- 流畅动画
- 清晰的错误提示
```

#### Phase 5: 测试与优化 (Day 11-12)

**任务：**
```
1. 单元测试
   - WalletController 测试
   - 加密工具测试
   - Provider 测试

2. 集成测试
   - 端到端流程测试
   - 与测试网交互

3. 安全审查
   - XSS 防护检查
   - 密钥管理审查
   - 输入验证

4. 性能优化
   - 减小包体积
   - 优化加载速度

5. 文档
   - README.md
   - 使用教程
   - 开发文档
```

---

## 实施细节

### 如何与我互动

#### ✅ 好的提问方式

```
请实现 wallet/extension/src/background/WalletController.ts

要求：
1. 参考 docs/07-WALLET-DESIGN.md 中的设计
2. 包含完整的类型定义
3. 添加详细注释
4. 包含错误处理
5. 提供单元测试示例

我会逐个功能确认，请先实现 createWallet() 方法。
```

#### ❌ 避免的提问方式

```
帮我做一个钱包
```

### 分步骤实现

**不要一次性要求所有功能！** 建议按照以下顺序：

1. **Day 1**: 项目初始化 + manifest.json
2. **Day 2**: Provider 基础结构
3. **Day 3**: Provider 完整实现
4. **Day 4**: Background 基础框架
5. **Day 5**: WalletController 核心方法
6. **Day 6**: 交易和签名功能
7. **Day 7**: Background 完整测试
8. **Day 8**: Popup 基础 UI
9. **Day 9**: 主要页面（Home, Send）
10. **Day 10**: 创建/导入/解锁流程
11. **Day 11**: 测试和 Bug 修复
12. **Day 12**: 优化和文档

### 验收标准

每完成一个阶段，确保：

- ✅ 代码可以运行
- ✅ 没有 TypeScript 错误
- ✅ 通过基本测试
- ✅ 有清晰的注释

---

## 关键配置文件

### package.json

```json
{
  "name": "qfc-wallet",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "test": "vitest"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "ethers": "^6.9.0",
    "zustand": "^4.4.0",
    "lucide-react": "^0.294.0"
  },
  "devDependencies": {
    "@types/chrome": "^0.0.253",
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@vitejs/plugin-react": "^4.2.0",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32",
    "tailwindcss": "^3.3.6",
    "typescript": "^5.3.0",
    "vite": "^5.0.0",
    "vitest": "^1.0.0"
  }
}
```

### vite.config.ts

```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      input: {
        popup: resolve(__dirname, 'popup.html'),
        background: resolve(__dirname, 'src/background/index.ts'),
        content: resolve(__dirname, 'src/content/inject.ts'),
        inpage: resolve(__dirname, 'src/inpage/provider.ts'),
      },
      output: {
        entryFileNames: '[name].js',
        chunkFileNames: '[name].js',
        assetFileNames: '[name].[ext]',
      },
    },
  },
});
```

### tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "types": ["chrome", "vite/client"]
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

---

## 常见问题

### Q: RPC 节点地址是什么？
**A**: 测试网 RPC: `https://rpc.testnet.qfc.network`  
（注：初期可能还不存在，可以先用本地节点或以太坊测试网做开发）

### Q: Chain ID 是多少？
**A**: 
- 主网: 待定
- 测试网: 9000 (0x2328)

### Q: 如何获得测试币？
**A**: 水龙头地址（待测试网上线）: `https://faucet.testnet.qfc.network`

### Q: 需要实现所有 EIP-1193 方法吗？
**A**: 初期重点实现：
- eth_requestAccounts
- eth_accounts
- eth_chainId
- eth_sendTransaction
- personal_sign
- eth_getBalance
- eth_blockNumber

其他方法可以暂时转发到 RPC 节点。

---

## 开发原则

### 1. 安全第一 🔐
- 密钥管理极其谨慎
- 加密存储
- 输入验证
- XSS 防护

### 2. 代码质量 📝
- TypeScript 严格模式
- 详细注释
- 单元测试
- 错误处理

### 3. 用户体验 ✨
- 清晰的界面
- 有用的错误提示
- 流畅的动画
- 响应式设计

### 4. 迭代开发 🔄
- 先实现核心功能
- 逐步添加特性
- 持续测试
- 及时重构

---

## 资源链接

### 官方文档
- [Chrome Extension Docs](https://developer.chrome.com/docs/extensions/mv3/)
- [EIP-1193](https://eips.ethereum.org/EIPS/eip-1193)
- [ethers.js Docs](https://docs.ethers.org/v6/)

### 参考项目
- [MetaMask](https://github.com/MetaMask/metamask-extension)
- [Rabby](https://github.com/RabbyHub/Rabby)
- [Frame](https://github.com/floating/frame)

---

## 下一步

完成浏览器钱包后，我们将：

1. **搭建测试网** (docs/06-TESTNET-SETUP.md)
2. **开发区块浏览器** (docs/05-BLOCK-EXPLORER.md)
3. **实现核心区块链** (docs/01-BLOCKCHAIN-DESIGN.md)

---

## 立即开始！

### 给 Claude Code 的第一条指令

```
我要开始实现 QFC 浏览器钱包。

请先：
1. 阅读 docs/07-WALLET-DESIGN.md
2. 创建项目基础结构（按照 "目录结构" 章节）
3. 设置 package.json、tsconfig.json、vite.config.ts
4. 创建 manifest.json

完成后，我们将逐步实现核心功能。
```

---

**最后更新**: 2026-02-01  
**版本**: 1.0.0  
**维护者**: QFC Core Team

祝开发顺利！有任何问题随时问我 💪
