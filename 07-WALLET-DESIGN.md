# QFC Wallet Design Specification

## 概述

QFC 钱包是用户进入 QFC 生态的第一道门，必须同时满足：
- **安全性**：密钥永不泄露
- **易用性**：新手也能轻松使用
- **兼容性**：支持多平台、多DApp
- **功能性**：完整的资产管理能力

## 多端覆盖策略

### 优先级划分

**第一优先级（必须有）**：
1. ✅ 浏览器插件钱包 - 开发者和桌面用户
2. ✅ 移动端 App - 主流用户群体
3. ✅ Web 钱包 - 快速体验，无需安装

**第二优先级（生态成熟后）**：
4. ○ 硬件钱包集成 - 大额资产用户
5. ○ 桌面客户端 - 专业用户
6. ○ CLI 钱包 - 开发者工具

**第三优先级（未来探索）**：
7. ○ 智能合约钱包 - Account Abstraction
8. ○ 多签钱包 - 团队/机构
9. ○ MPC 钱包 - 无私钥托管

---

## Phase 1: 浏览器插件钱包

### 为什么先做浏览器插件？

✅ **开发者优先** - DApp 开发需要  
✅ **快速迭代** - Web 技术栈熟悉  
✅ **成本低** - 无需 App Store 审核  
✅ **兼容性好** - 可 fork MetaMask  
✅ **桌面体验好** - 大屏幕操作方便  

### 技术架构

```
┌─────────────────────────────────────────────┐
│         Content Script (网页注入)            │
│  - 注入 window.qfc 对象                      │
│  - 监听 DApp 请求                            │
│  - 事件通信                                  │
└──────────────────┬──────────────────────────┘
                   │ Message Passing
┌──────────────────┴──────────────────────────┐
│         Background Script (后台服务)         │
│  - 密钥管理                                  │
│  - 交易签名                                  │
│  - RPC 请求处理                              │
│  - 状态管理                                  │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────┴──────────────────────────┐
│         Popup UI (弹窗界面)                  │
│  - React + TypeScript                       │
│  - TailwindCSS                              │
│  - Zustand (状态管理)                        │
└─────────────────────────────────────────────┘
```

### 技术栈

- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Styling**: TailwindCSS
- **State Management**: Zustand
- **Crypto**: ethers.js v6
- **Storage**: chrome.storage.local (加密)
- **Manifest**: Chrome Extension Manifest V3

### 目录结构

```
wallet/extension/
├── src/
│   ├── background/              # 后台服务
│   │   ├── index.ts            # Service Worker 入口
│   │   ├── WalletController.ts # 钱包管理
│   │   ├── TransactionController.ts # 交易处理
│   │   ├── NetworkController.ts # 网络管理
│   │   └── StorageController.ts # 存储管理
│   │
│   ├── content/                 # 内容脚本
│   │   └── inject.ts           # 注入到网页
│   │
│   ├── inpage/                  # 页面内脚本
│   │   └── provider.ts         # window.qfc Provider
│   │
│   ├── popup/                   # 弹窗 UI
│   │   ├── App.tsx
│   │   ├── pages/
│   │   │   ├── Home.tsx
│   │   │   ├── Send.tsx
│   │   │   ├── Receive.tsx
│   │   │   ├── Settings.tsx
│   │   │   ├── CreateWallet.tsx
│   │   │   ├── ImportWallet.tsx
│   │   │   └── Unlock.tsx
│   │   │
│   │   └── components/
│   │       ├── WalletCard.tsx
│   │       ├── TransactionItem.tsx
│   │       ├── AssetList.tsx
│   │       └── ConfirmTransaction.tsx
│   │
│   ├── utils/                   # 工具函数
│   │   ├── crypto.ts           # 加密解密
│   │   ├── storage.ts          # 存储封装
│   │   ├── validation.ts       # 验证函数
│   │   └── constants.ts        # 常量定义
│   │
│   └── types/                   # 类型定义
│       ├── wallet.ts
│       ├── transaction.ts
│       └── network.ts
│
├── public/
│   ├── manifest.json            # 扩展清单
│   ├── icons/                   # 图标
│   │   ├── icon16.png
│   │   ├── icon48.png
│   │   └── icon128.png
│   └── popup.html               # 弹窗 HTML
│
├── package.json
├── tsconfig.json
├── vite.config.ts
└── README.md
```

### 核心文件实现

#### 1. manifest.json

```json
{
  "manifest_version": 3,
  "name": "QFC Wallet",
  "version": "1.0.0",
  "description": "Secure wallet for QFC Network",
  "icons": {
    "16": "icons/icon16.png",
    "48": "icons/icon48.png",
    "128": "icons/icon128.png"
  },
  "action": {
    "default_popup": "popup.html",
    "default_icon": "icons/icon48.png",
    "default_title": "QFC Wallet"
  },
  "background": {
    "service_worker": "background.js",
    "type": "module"
  },
  "content_scripts": [
    {
      "matches": ["<all_urls>"],
      "js": ["content.js"],
      "run_at": "document_start",
      "all_frames": true
    }
  ],
  "permissions": [
    "storage",
    "activeTab",
    "notifications",
    "alarms"
  ],
  "host_permissions": [
    "https://*/*",
    "http://*/*"
  ],
  "web_accessible_resources": [
    {
      "resources": ["inpage.js"],
      "matches": ["<all_urls>"]
    }
  ],
  "content_security_policy": {
    "extension_pages": "script-src 'self'; object-src 'self'"
  }
}
```

#### 2. inpage/provider.ts - window.qfc Provider

```typescript
import { ethers } from 'ethers';

/**
 * QFC Provider - 注入到网页的 window.qfc 对象
 * 兼容 EIP-1193 标准
 */
class QFCProvider extends EventTarget {
  public isQFC = true;
  public isMetaMask = true;  // 兼容性标记
  public chainId: string;
  public selectedAddress: string | null = null;
  
  private _requestId = 0;
  private _pendingRequests: Map<number, {
    resolve: (value: any) => void;
    reject: (error: any) => void;
  }> = new Map();
  
  constructor() {
    super();
    this.chainId = '0x2328';  // 9000 (testnet)
    
    // 监听来自 background 的消息
    window.addEventListener('message', this._handleMessage.bind(this));
  }
  
  /**
   * 核心方法：发送 RPC 请求
   * @param args - { method: string, params?: any[] }
   */
  async request(args: { method: string; params?: any[] }): Promise<any> {
    const { method, params = [] } = args;
    
    console.log(`[QFC] Request: ${method}`, params);
    
    // 特殊方法处理
    switch (method) {
      case 'eth_requestAccounts':
        return this._requestAccounts();
      
      case 'eth_accounts':
        return this.selectedAddress ? [this.selectedAddress] : [];
      
      case 'eth_chainId':
        return this.chainId;
      
      case 'eth_sendTransaction':
        return this._sendTransaction(params[0]);
      
      case 'personal_sign':
        return this._personalSign(params[0], params[1]);
      
      case 'eth_signTypedData_v4':
        return this._signTypedData(params[0], params[1]);
      
      // 其他方法转发到 RPC
      default:
        return this._sendToBackground({ method, params });
    }
  }
  
  /**
   * 请求连接钱包
   */
  private async _requestAccounts(): Promise<string[]> {
    const response = await this._sendToBackground({
      method: 'eth_requestAccounts'
    });
    
    if (response.result) {
      this.selectedAddress = response.result[0];
      this._emit('accountsChanged', response.result);
      this._emit('connect', { chainId: this.chainId });
    }
    
    return response.result || [];
  }
  
  /**
   * 发送交易（需要用户确认）
   */
  private async _sendTransaction(tx: any): Promise<string> {
    const response = await this._sendToBackground({
      method: 'eth_sendTransaction',
      params: [tx]
    });
    
    if (response.error) {
      throw new Error(response.error.message);
    }
    
    return response.result;
  }
  
  /**
   * 签名消息
   */
  private async _personalSign(message: string, address: string): Promise<string> {
    const response = await this._sendToBackground({
      method: 'personal_sign',
      params: [message, address]
    });
    
    if (response.error) {
      throw new Error(response.error.message);
    }
    
    return response.result;
  }
  
  /**
   * 签名结构化数据
   */
  private async _signTypedData(address: string, typedData: string): Promise<string> {
    const response = await this._sendToBackground({
      method: 'eth_signTypedData_v4',
      params: [address, typedData]
    });
    
    if (response.error) {
      throw new Error(response.error.message);
    }
    
    return response.result;
  }
  
  /**
   * 发送消息到 background script
   */
  private _sendToBackground(payload: any): Promise<any> {
    return new Promise((resolve, reject) => {
      const id = this._requestId++;
      
      this._pendingRequests.set(id, { resolve, reject });
      
      // 发送请求
      window.postMessage({
        type: 'QFC_REQUEST',
        id,
        payload
      }, '*');
      
      // 超时处理
      setTimeout(() => {
        if (this._pendingRequests.has(id)) {
          this._pendingRequests.delete(id);
          reject(new Error('Request timeout'));
        }
      }, 30000);  // 30秒超时
    });
  }
  
  /**
   * 处理来自 background 的响应
   */
  private _handleMessage(event: MessageEvent) {
    if (event.source !== window) return;
    
    const { type, id, payload } = event.data;
    
    // 响应消息
    if (type === 'QFC_RESPONSE') {
      const pending = this._pendingRequests.get(id);
      if (pending) {
        this._pendingRequests.delete(id);
        
        if (payload.error) {
          pending.reject(payload.error);
        } else {
          pending.resolve(payload);
        }
      }
    }
    
    // 通知消息
    if (type === 'QFC_NOTIFICATION') {
      const { method, params } = payload;
      this._emit(method, params);
    }
  }
  
  /**
   * 触发事件
   */
  private _emit(event: string, data: any) {
    console.log(`[QFC] Event: ${event}`, data);
    this.dispatchEvent(new CustomEvent(event, { detail: data }));
  }
  
  /**
   * 兼容老式 on() 方法
   */
  on(event: string, callback: (data: any) => void) {
    this.addEventListener(event, (e: any) => callback(e.detail));
  }
  
  /**
   * 兼容老式 removeListener() 方法
   */
  removeListener(event: string, callback: (data: any) => void) {
    this.removeEventListener(event, callback as any);
  }
}

// 注入到 window
declare global {
  interface Window {
    qfc: QFCProvider;
    ethereum: QFCProvider;  // 兼容性
  }
}

const provider = new QFCProvider();
window.qfc = provider;
window.ethereum = provider;  // 兼容 MetaMask 的 DApp

// 触发事件通知 DApp 钱包已就绪
window.dispatchEvent(new Event('ethereum#initialized'));

console.log('[QFC] Provider injected');
```

#### 3. background/WalletController.ts - 核心钱包逻辑

```typescript
import { ethers } from 'ethers';
import { encrypt, decrypt } from '../utils/crypto';

export interface Wallet {
  address: string;
  encryptedPrivateKey: string;
  name: string;
  createdAt: number;
}

export class WalletController {
  private wallets: Wallet[] = [];
  private currentWallet: Wallet | null = null;
  private isUnlocked = false;
  private password: string | null = null;
  private provider: ethers.JsonRpcProvider;
  
  // 自动锁定定时器
  private lockTimer: NodeJS.Timeout | null = null;
  private readonly LOCK_TIMEOUT = 30 * 60 * 1000;  // 30分钟
  
  constructor(rpcUrl: string) {
    this.provider = new ethers.JsonRpcProvider(rpcUrl);
    this.loadFromStorage();
  }
  
  /**
   * 从存储加载钱包
   */
  private async loadFromStorage() {
    try {
      const data = await chrome.storage.local.get(['wallets', 'currentAddress']);
      
      if (data.wallets) {
        this.wallets = data.wallets;
      }
      
      if (data.currentAddress && this.wallets.length > 0) {
        this.currentWallet = this.wallets.find(
          w => w.address === data.currentAddress
        ) || this.wallets[0];
      }
    } catch (error) {
      console.error('Failed to load wallets:', error);
    }
  }
  
  /**
   * 保存钱包到存储
   */
  private async saveToStorage() {
    await chrome.storage.local.set({
      wallets: this.wallets,
      currentAddress: this.currentWallet?.address
    });
  }
  
  /**
   * 创建新钱包
   */
  async createWallet(name: string, password: string): Promise<{
    address: string;
    mnemonic: string;
  }> {
    // 生成助记词
    const wallet = ethers.Wallet.createRandom();
    
    // 加密私钥
    const encryptedPrivateKey = encrypt(wallet.privateKey, password);
    
    const newWallet: Wallet = {
      address: wallet.address,
      encryptedPrivateKey,
      name: name || `Account ${this.wallets.length + 1}`,
      createdAt: Date.now()
    };
    
    this.wallets.push(newWallet);
    this.currentWallet = newWallet;
    this.password = password;
    this.isUnlocked = true;
    
    await this.saveToStorage();
    this.startLockTimer();
    
    return {
      address: wallet.address,
      mnemonic: wallet.mnemonic!.phrase
    };
  }
  
  /**
   * 导入钱包
   */
  async importWallet(
    privateKeyOrMnemonic: string,
    name: string,
    password: string
  ): Promise<string> {
    let wallet: ethers.Wallet;
    
    // 判断是私钥还是助记词
    if (privateKeyOrMnemonic.split(' ').length >= 12) {
      // 助记词
      wallet = ethers.Wallet.fromPhrase(privateKeyOrMnemonic);
    } else {
      // 私钥
      wallet = new ethers.Wallet(privateKeyOrMnemonic);
    }
    
    // 检查是否已存在
    if (this.wallets.some(w => w.address === wallet.address)) {
      throw new Error('Wallet already exists');
    }
    
    const encryptedPrivateKey = encrypt(wallet.privateKey, password);
    
    const newWallet: Wallet = {
      address: wallet.address,
      encryptedPrivateKey,
      name: name || `Imported ${this.wallets.length + 1}`,
      createdAt: Date.now()
    };
    
    this.wallets.push(newWallet);
    this.currentWallet = newWallet;
    this.password = password;
    this.isUnlocked = true;
    
    await this.saveToStorage();
    this.startLockTimer();
    
    return wallet.address;
  }
  
  /**
   * 解锁钱包
   */
  async unlock(password: string): Promise<boolean> {
    if (this.wallets.length === 0) {
      throw new Error('No wallet found');
    }
    
    try {
      // 验证密码（尝试解密第一个钱包）
      decrypt(this.wallets[0].encryptedPrivateKey, password);
      
      this.password = password;
      this.isUnlocked = true;
      
      if (!this.currentWallet) {
        this.currentWallet = this.wallets[0];
      }
      
      this.startLockTimer();
      
      return true;
    } catch {
      return false;
    }
  }
  
  /**
   * 锁定钱包
   */
  lock() {
    this.isUnlocked = false;
    this.password = null;
    this.stopLockTimer();
  }
  
  /**
   * 获取当前账户
   */
  getCurrentAccount(): string | null {
    return this.isUnlocked && this.currentWallet 
      ? this.currentWallet.address 
      : null;
  }
  
  /**
   * 切换账户
   */
  async switchAccount(address: string): Promise<void> {
    const wallet = this.wallets.find(w => w.address === address);
    if (!wallet) {
      throw new Error('Wallet not found');
    }
    
    this.currentWallet = wallet;
    await this.saveToStorage();
  }
  
  /**
   * 获取所有账户
   */
  getAllAccounts(): Wallet[] {
    return this.wallets.map(w => ({
      ...w,
      encryptedPrivateKey: ''  // 不暴露私钥
    }));
  }
  
  /**
   * 获取余额
   */
  async getBalance(address?: string): Promise<string> {
    const addr = address || this.currentWallet?.address;
    if (!addr) throw new Error('No address');
    
    const balance = await this.provider.getBalance(addr);
    return ethers.formatEther(balance);
  }
  
  /**
   * 发送交易
   */
  async sendTransaction(tx: ethers.TransactionRequest): Promise<string> {
    if (!this.isUnlocked || !this.currentWallet || !this.password) {
      throw new Error('Wallet is locked');
    }
    
    // 解密私钥
    const privateKey = decrypt(
      this.currentWallet.encryptedPrivateKey,
      this.password
    );
    
    const wallet = new ethers.Wallet(privateKey, this.provider);
    
    // 发送交易
    const txResponse = await wallet.sendTransaction(tx);
    
    // 重置锁定计时器
    this.startLockTimer();
    
    return txResponse.hash;
  }
  
  /**
   * 签名消息
   */
  async signMessage(message: string): Promise<string> {
    if (!this.isUnlocked || !this.currentWallet || !this.password) {
      throw new Error('Wallet is locked');
    }
    
    const privateKey = decrypt(
      this.currentWallet.encryptedPrivateKey,
      this.password
    );
    
    const wallet = new ethers.Wallet(privateKey);
    const signature = await wallet.signMessage(message);
    
    this.startLockTimer();
    
    return signature;
  }
  
  /**
   * 签名结构化数据
   */
  async signTypedData(typedData: any): Promise<string> {
    if (!this.isUnlocked || !this.currentWallet || !this.password) {
      throw new Error('Wallet is locked');
    }
    
    const privateKey = decrypt(
      this.currentWallet.encryptedPrivateKey,
      this.password
    );
    
    const wallet = new ethers.Wallet(privateKey);
    
    const { domain, types, message } = JSON.parse(typedData);
    delete types.EIP712Domain;  // ethers 会自动处理
    
    const signature = await wallet.signTypedData(domain, types, message);
    
    this.startLockTimer();
    
    return signature;
  }
  
  /**
   * 启动自动锁定定时器
   */
  private startLockTimer() {
    this.stopLockTimer();
    
    this.lockTimer = setTimeout(() => {
      this.lock();
      console.log('[QFC] Wallet auto-locked after inactivity');
    }, this.LOCK_TIMEOUT);
  }
  
  /**
   * 停止自动锁定定时器
   */
  private stopLockTimer() {
    if (this.lockTimer) {
      clearTimeout(this.lockTimer);
      this.lockTimer = null;
    }
  }
  
  /**
   * 检查是否解锁
   */
  isWalletUnlocked(): boolean {
    return this.isUnlocked;
  }
}
```

#### 4. utils/crypto.ts - 加密工具

```typescript
import CryptoJS from 'crypto-js';

/**
 * 使用 AES 加密
 */
export function encrypt(text: string, password: string): string {
  return CryptoJS.AES.encrypt(text, password).toString();
}

/**
 * 使用 AES 解密
 */
export function decrypt(ciphertext: string, password: string): string {
  const bytes = CryptoJS.AES.decrypt(ciphertext, password);
  const decrypted = bytes.toString(CryptoJS.enc.Utf8);
  
  if (!decrypted) {
    throw new Error('Decryption failed - wrong password');
  }
  
  return decrypted;
}

/**
 * 生成随机密码
 */
export function generatePassword(length: number = 32): string {
  const charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*';
  let password = '';
  
  const randomValues = new Uint8Array(length);
  crypto.getRandomValues(randomValues);
  
  for (let i = 0; i < length; i++) {
    password += charset[randomValues[i] % charset.length];
  }
  
  return password;
}
```

### UI 组件示例

#### popup/pages/Home.tsx

```typescript
import React, { useState, useEffect } from 'react';
import { Copy, Send, ArrowDownToLine, Settings } from 'lucide-react';

export default function Home() {
  const [address, setAddress] = useState('');
  const [balance, setBalance] = useState('0');
  const [usdValue, setUsdValue] = useState('0');
  
  useEffect(() => {
    loadAccountData();
  }, []);
  
  const loadAccountData = async () => {
    // 从 background 获取数据
    const response = await chrome.runtime.sendMessage({
      method: 'eth_accounts'
    });
    
    if (response.result && response.result.length > 0) {
      const addr = response.result[0];
      setAddress(addr);
      
      // 获取余额
      const balanceResponse = await chrome.runtime.sendMessage({
        method: 'eth_getBalance',
        params: [addr, 'latest']
      });
      
      if (balanceResponse.result) {
        const bal = parseFloat(balanceResponse.result);
        setBalance(bal.toFixed(4));
        setUsdValue((bal * 2.34).toFixed(2));  // 假设 QFC = $2.34
      }
    }
  };
  
  const copyAddress = () => {
    navigator.clipboard.writeText(address);
    // 显示复制成功提示
  };
  
  return (
    <div className="w-[400px] h-[600px] bg-gradient-to-br from-purple-50 to-blue-50 p-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-lg font-bold">QFC Wallet</h1>
        <button className="p-2 hover:bg-white/50 rounded-lg">
          <Settings size={20} />
        </button>
      </div>
      
      {/* Balance Card */}
      <div className="bg-gradient-to-r from-purple-500 to-blue-500 rounded-2xl p-6 text-white mb-4">
        <div className="text-sm opacity-80">Total Balance</div>
        <div className="text-4xl font-bold mt-2">{balance} QFC</div>
        <div className="text-sm opacity-80 mt-1">${usdValue} USD</div>
        
        <div className="flex items-center mt-4 space-x-2">
          <div className="bg-white/20 px-3 py-1.5 rounded-full text-sm">
            {address.slice(0, 6)}...{address.slice(-4)}
          </div>
          <button 
            onClick={copyAddress}
            className="bg-white/20 px-3 py-1.5 rounded-full text-sm hover:bg-white/30"
          >
            <Copy size={14} />
          </button>
        </div>
      </div>
      
      {/* Quick Actions */}
      <div className="grid grid-cols-3 gap-3 mb-4">
        <QuickAction icon={<ArrowDownToLine />} label="Receive" />
        <QuickAction icon={<Send />} label="Send" />
        <QuickAction icon={<>⇄</>} label="Swap" />
      </div>
      
      {/* Assets & Activity */}
      <div className="bg-white rounded-2xl p-4">
        <div className="flex space-x-4 border-b">
          <button className="pb-2 border-b-2 border-blue-500 font-semibold">
            Assets
          </button>
          <button className="pb-2 text-gray-500">
            Activity
          </button>
        </div>
        
        <div className="mt-4 space-y-3">
          <AssetItem 
            name="QFC"
            balance={balance}
            value={usdValue}
          />
        </div>
      </div>
    </div>
  );
}

function QuickAction({ icon, label }: { icon: React.ReactNode; label: string }) {
  return (
    <button className="bg-white rounded-xl p-4 hover:shadow-md transition-shadow">
      <div className="text-blue-500 mb-2 flex justify-center">{icon}</div>
      <div className="text-xs text-gray-600">{label}</div>
    </button>
  );
}

function AssetItem({ name, balance, value }: any) {
  return (
    <div className="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg">
      <div className="flex items-center space-x-3">
        <div className="w-10 h-10 bg-gradient-to-br from-purple-400 to-blue-400 rounded-full" />
        <div>
          <div className="font-semibold">{name}</div>
          <div className="text-sm text-gray-500">${value}</div>
        </div>
      </div>
      <div className="text-right">
        <div className="font-semibold">{balance}</div>
        <div className="text-sm text-gray-500">{name}</div>
      </div>
    </div>
  );
}
```

### 安全要求

#### 密钥管理
- ✅ 私钥加密后存储在 chrome.storage.local
- ✅ 密码永不存储（只在内存中）
- ✅ 30分钟无操作自动锁定
- ✅ 敏感操作需要重新输入密码

#### XSS 防护
- ✅ CSP 策略限制脚本来源
- ✅ 用户输入严格验证
- ✅ 不使用 innerHTML

#### 钓鱼防护
- ✅ 显示 DApp 域名
- ✅ 警告可疑请求
- ✅ 交易确认显示完整信息

### 测试要求

```typescript
// tests/WalletController.test.ts

import { WalletController } from '../src/background/WalletController';

describe('WalletController', () => {
  let controller: WalletController;
  
  beforeEach(() => {
    controller = new WalletController('https://rpc.testnet.qfc.network');
  });
  
  test('should create wallet', async () => {
    const { address, mnemonic } = await controller.createWallet(
      'Test Wallet',
      'password123'
    );
    
    expect(address).toMatch(/^0x[a-fA-F0-9]{40}$/);
    expect(mnemonic.split(' ')).toHaveLength(12);
  });
  
  test('should unlock with correct password', async () => {
    await controller.createWallet('Test', 'password123');
    controller.lock();
    
    const unlocked = await controller.unlock('password123');
    expect(unlocked).toBe(true);
  });
  
  test('should reject wrong password', async () => {
    await controller.createWallet('Test', 'password123');
    controller.lock();
    
    const unlocked = await controller.unlock('wrongpassword');
    expect(unlocked).toBe(false);
  });
  
  // 更多测试...
});
```

### 发布流程

#### 1. 构建
```bash
cd wallet/extension
npm install
npm run build
```

#### 2. 打包
```bash
cd dist
zip -r qfc-wallet-v1.0.0.zip .
```

#### 3. Chrome Web Store
- 访问 https://chrome.google.com/webstore/devconsole
- 创建新项目
- 上传 ZIP
- 填写描述、截图、隐私政策
- 提交审核（1-3天）

#### 4. Firefox Add-ons
- 访问 https://addons.mozilla.org/developers/
- 上传同样的 ZIP
- 提交审核（1-7天）

---

## Phase 2: 移动端钱包

### 技术栈
- React Native + Expo
- TypeScript
- ethers.js
- Biometric Authentication
- WalletConnect

### 关键功能
- 生物识别解锁（指纹/面容ID）
- 二维码扫描
- WalletConnect 支持
- 推送通知
- 本地加密存储

（详细设计省略，与浏览器插件类似但针对移动端优化）

---

## 开发时间线

### Week 1-2: 浏览器插件框架
- ✅ 项目初始化
- ✅ manifest.json 配置
- ✅ Provider 注入
- ✅ 基础 UI

### Week 3-4: 核心功能
- ✅ 钱包创建/导入
- ✅ 交易签名
- ✅ 余额查询
- ✅ 交易历史

### Week 5-6: 完善与测试
- ✅ UI 优化
- ✅ 单元测试
- ✅ 安全审计
- ✅ 文档

### Week 7: 发布
- ✅ Chrome Web Store
- ✅ Firefox Add-ons
- ✅ 用户反馈

---

**最后更新**: 2026-02-01
**版本**: 1.0.0
**维护者**: QFC Core Team
