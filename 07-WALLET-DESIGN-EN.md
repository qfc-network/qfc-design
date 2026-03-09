# QFC Wallet Design Specification

## Overview

The QFC wallet is the user's first gateway into the QFC ecosystem and must simultaneously satisfy:
- **Security**: Private keys must never be leaked
- **Usability**: Easy to use even for beginners
- **Compatibility**: Multi-platform, multi-DApp support
- **Functionality**: Complete asset management capabilities

## Multi-Platform Coverage Strategy

### Priority Tiers

**First Priority (Must-Have)**:
1. Browser Extension Wallet - For developers and desktop users
2. Mobile App - For mainstream user base
3. Web Wallet - Quick experience, no installation required

**Second Priority (After Ecosystem Maturity)**:
4. Hardware Wallet Integration - For high-value asset holders
5. Desktop Client - For professional users
6. CLI Wallet - Developer tooling

**Third Priority (Future Exploration)**:
7. Smart Contract Wallet - Account Abstraction
8. Multi-Signature Wallet - For teams/institutions
9. MPC Wallet - Keyless custody

---

## Phase 1: Browser Extension Wallet

### Why Build the Browser Extension First?

- **Developer-first** - Required for DApp development
- **Fast iteration** - Familiar web tech stack
- **Low cost** - No App Store review needed
- **Good compatibility** - Can fork MetaMask
- **Great desktop experience** - Large screen convenience

### Technical Architecture

```
┌─────────────────────────────────────────────┐
│         Content Script (Page Injection)      │
│  - Inject window.qfc object                 │
│  - Listen for DApp requests                 │
│  - Event communication                      │
└──────────────────┬──────────────────────────┘
                   │ Message Passing
┌──────────────────┴──────────────────────────┐
│         Background Script (Background Service)│
│  - Key management                           │
│  - Transaction signing                      │
│  - RPC request handling                     │
│  - State management                         │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────┴──────────────────────────┐
│         Popup UI (Popup Interface)           │
│  - React + TypeScript                       │
│  - TailwindCSS                              │
│  - Zustand (State Management)               │
└─────────────────────────────────────────────┘
```

### Tech Stack

- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Styling**: TailwindCSS
- **State Management**: Zustand
- **Crypto**: ethers.js v6
- **Storage**: chrome.storage.local (encrypted)
- **Manifest**: Chrome Extension Manifest V3

### Directory Structure

```
wallet/extension/
├── src/
│   ├── background/              # Background service
│   │   ├── index.ts            # Service Worker entry
│   │   ├── WalletController.ts # Wallet management
│   │   ├── TransactionController.ts # Transaction handling
│   │   ├── NetworkController.ts # Network management
│   │   └── StorageController.ts # Storage management
│   │
│   ├── content/                 # Content scripts
│   │   └── inject.ts           # Injected into web pages
│   │
│   ├── inpage/                  # In-page scripts
│   │   └── provider.ts         # window.qfc Provider
│   │
│   ├── popup/                   # Popup UI
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
│   ├── utils/                   # Utility functions
│   │   ├── crypto.ts           # Encryption/decryption
│   │   ├── storage.ts          # Storage wrapper
│   │   ├── validation.ts       # Validation functions
│   │   └── constants.ts        # Constants definition
│   │
│   └── types/                   # Type definitions
│       ├── wallet.ts
│       ├── transaction.ts
│       └── network.ts
│
├── public/
│   ├── manifest.json            # Extension manifest
│   ├── icons/                   # Icons
│   │   ├── icon16.png
│   │   ├── icon48.png
│   │   └── icon128.png
│   └── popup.html               # Popup HTML
│
├── package.json
├── tsconfig.json
├── vite.config.ts
└── README.md
```

### Core File Implementations

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
 * QFC Provider - window.qfc object injected into web pages
 * Compatible with EIP-1193 standard
 */
class QFCProvider extends EventTarget {
  public isQFC = true;
  public isMetaMask = true;  // Compatibility flag
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

    // Listen for messages from background
    window.addEventListener('message', this._handleMessage.bind(this));
  }

  /**
   * Core method: send RPC request
   * @param args - { method: string, params?: any[] }
   */
  async request(args: { method: string; params?: any[] }): Promise<any> {
    const { method, params = [] } = args;

    console.log(`[QFC] Request: ${method}`, params);

    // Special method handling
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

      // Forward other methods to RPC
      default:
        return this._sendToBackground({ method, params });
    }
  }

  /**
   * Request wallet connection
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
   * Send transaction (requires user confirmation)
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
   * Sign message
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
   * Sign typed data
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
   * Send message to background script
   */
  private _sendToBackground(payload: any): Promise<any> {
    return new Promise((resolve, reject) => {
      const id = this._requestId++;

      this._pendingRequests.set(id, { resolve, reject });

      // Send request
      window.postMessage({
        type: 'QFC_REQUEST',
        id,
        payload
      }, '*');

      // Timeout handling
      setTimeout(() => {
        if (this._pendingRequests.has(id)) {
          this._pendingRequests.delete(id);
          reject(new Error('Request timeout'));
        }
      }, 30000);  // 30-second timeout
    });
  }

  /**
   * Handle response from background
   */
  private _handleMessage(event: MessageEvent) {
    if (event.source !== window) return;

    const { type, id, payload } = event.data;

    // Response message
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

    // Notification message
    if (type === 'QFC_NOTIFICATION') {
      const { method, params } = payload;
      this._emit(method, params);
    }
  }

  /**
   * Emit event
   */
  private _emit(event: string, data: any) {
    console.log(`[QFC] Event: ${event}`, data);
    this.dispatchEvent(new CustomEvent(event, { detail: data }));
  }

  /**
   * Legacy on() method compatibility
   */
  on(event: string, callback: (data: any) => void) {
    this.addEventListener(event, (e: any) => callback(e.detail));
  }

  /**
   * Legacy removeListener() method compatibility
   */
  removeListener(event: string, callback: (data: any) => void) {
    this.removeEventListener(event, callback as any);
  }
}

// Inject into window
declare global {
  interface Window {
    qfc: QFCProvider;
    ethereum: QFCProvider;  // Compatibility
  }
}

const provider = new QFCProvider();
window.qfc = provider;
window.ethereum = provider;  // Compatible with MetaMask DApps

// Dispatch event to notify DApps that wallet is ready
window.dispatchEvent(new Event('ethereum#initialized'));

console.log('[QFC] Provider injected');
```

#### 3. background/WalletController.ts - Core Wallet Logic

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

  // Auto-lock timer
  private lockTimer: NodeJS.Timeout | null = null;
  private readonly LOCK_TIMEOUT = 30 * 60 * 1000;  // 30 minutes

  constructor(rpcUrl: string) {
    this.provider = new ethers.JsonRpcProvider(rpcUrl);
    this.loadFromStorage();
  }

  /**
   * Load wallets from storage
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
   * Save wallets to storage
   */
  private async saveToStorage() {
    await chrome.storage.local.set({
      wallets: this.wallets,
      currentAddress: this.currentWallet?.address
    });
  }

  /**
   * Create a new wallet
   */
  async createWallet(name: string, password: string): Promise<{
    address: string;
    mnemonic: string;
  }> {
    // Generate mnemonic
    const wallet = ethers.Wallet.createRandom();

    // Encrypt private key
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
   * Import a wallet
   */
  async importWallet(
    privateKeyOrMnemonic: string,
    name: string,
    password: string
  ): Promise<string> {
    let wallet: ethers.Wallet;

    // Determine if input is a private key or mnemonic
    if (privateKeyOrMnemonic.split(' ').length >= 12) {
      // Mnemonic
      wallet = ethers.Wallet.fromPhrase(privateKeyOrMnemonic);
    } else {
      // Private key
      wallet = new ethers.Wallet(privateKeyOrMnemonic);
    }

    // Check if already exists
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
   * Unlock the wallet
   */
  async unlock(password: string): Promise<boolean> {
    if (this.wallets.length === 0) {
      throw new Error('No wallet found');
    }

    try {
      // Verify password (attempt to decrypt first wallet)
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
   * Lock the wallet
   */
  lock() {
    this.isUnlocked = false;
    this.password = null;
    this.stopLockTimer();
  }

  /**
   * Get current account
   */
  getCurrentAccount(): string | null {
    return this.isUnlocked && this.currentWallet
      ? this.currentWallet.address
      : null;
  }

  /**
   * Switch account
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
   * Get all accounts
   */
  getAllAccounts(): Wallet[] {
    return this.wallets.map(w => ({
      ...w,
      encryptedPrivateKey: ''  // Do not expose private keys
    }));
  }

  /**
   * Get balance
   */
  async getBalance(address?: string): Promise<string> {
    const addr = address || this.currentWallet?.address;
    if (!addr) throw new Error('No address');

    const balance = await this.provider.getBalance(addr);
    return ethers.formatEther(balance);
  }

  /**
   * Send transaction
   */
  async sendTransaction(tx: ethers.TransactionRequest): Promise<string> {
    if (!this.isUnlocked || !this.currentWallet || !this.password) {
      throw new Error('Wallet is locked');
    }

    // Decrypt private key
    const privateKey = decrypt(
      this.currentWallet.encryptedPrivateKey,
      this.password
    );

    const wallet = new ethers.Wallet(privateKey, this.provider);

    // Send transaction
    const txResponse = await wallet.sendTransaction(tx);

    // Reset lock timer
    this.startLockTimer();

    return txResponse.hash;
  }

  /**
   * Sign message
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
   * Sign typed data
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
    delete types.EIP712Domain;  // ethers handles this automatically

    const signature = await wallet.signTypedData(domain, types, message);

    this.startLockTimer();

    return signature;
  }

  /**
   * Start auto-lock timer
   */
  private startLockTimer() {
    this.stopLockTimer();

    this.lockTimer = setTimeout(() => {
      this.lock();
      console.log('[QFC] Wallet auto-locked after inactivity');
    }, this.LOCK_TIMEOUT);
  }

  /**
   * Stop auto-lock timer
   */
  private stopLockTimer() {
    if (this.lockTimer) {
      clearTimeout(this.lockTimer);
      this.lockTimer = null;
    }
  }

  /**
   * Check if wallet is unlocked
   */
  isWalletUnlocked(): boolean {
    return this.isUnlocked;
  }
}
```

#### 4. utils/crypto.ts - Encryption Utilities

```typescript
import CryptoJS from 'crypto-js';

/**
 * Encrypt using AES
 */
export function encrypt(text: string, password: string): string {
  return CryptoJS.AES.encrypt(text, password).toString();
}

/**
 * Decrypt using AES
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
 * Generate random password
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

### UI Component Example

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
    // Fetch data from background
    const response = await chrome.runtime.sendMessage({
      method: 'eth_accounts'
    });

    if (response.result && response.result.length > 0) {
      const addr = response.result[0];
      setAddress(addr);

      // Get balance
      const balanceResponse = await chrome.runtime.sendMessage({
        method: 'eth_getBalance',
        params: [addr, 'latest']
      });

      if (balanceResponse.result) {
        const bal = parseFloat(balanceResponse.result);
        setBalance(bal.toFixed(4));
        setUsdValue((bal * 2.34).toFixed(2));  // Assuming QFC = $2.34
      }
    }
  };

  const copyAddress = () => {
    navigator.clipboard.writeText(address);
    // Show copy success notification
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

### Security Requirements

#### Key Management
- Private keys encrypted before storage in chrome.storage.local
- Password is never persisted (only held in memory)
- Auto-lock after 30 minutes of inactivity
- Sensitive operations require password re-entry

#### XSS Protection
- CSP policy restricts script sources
- Strict validation of user inputs
- No use of innerHTML

#### Phishing Protection
- DApp domain name displayed
- Suspicious request warnings
- Full information shown on transaction confirmation

### Testing Requirements

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

  // More tests...
});
```

### Release Process

#### 1. Build
```bash
cd wallet/extension
npm install
npm run build
```

#### 2. Package
```bash
cd dist
zip -r qfc-wallet-v1.0.0.zip .
```

#### 3. Chrome Web Store
- Visit https://chrome.google.com/webstore/devconsole
- Create a new project
- Upload ZIP
- Fill in description, screenshots, privacy policy
- Submit for review (1-3 days)

#### 4. Firefox Add-ons
- Visit https://addons.mozilla.org/developers/
- Upload the same ZIP
- Submit for review (1-7 days)

---

## Phase 2: Mobile Wallet

### Tech Stack
- React Native + Expo
- TypeScript
- ethers.js
- Biometric Authentication
- WalletConnect

### Key Features
- Biometric unlock (fingerprint/Face ID)
- QR code scanning
- WalletConnect support
- Push notifications
- Local encrypted storage

(Detailed design omitted; similar to browser extension but optimized for mobile)

---

## Development Timeline

### Week 1-2: Browser Extension Framework
- Project initialization
- manifest.json configuration
- Provider injection
- Basic UI

### Week 3-4: Core Features
- Wallet creation/import
- Transaction signing
- Balance queries
- Transaction history

### Week 5-6: Polish & Testing
- UI optimization
- Unit tests
- Security audit
- Documentation

### Week 7: Release
- Chrome Web Store
- Firefox Add-ons
- User feedback

---

**Last Updated**: 2026-02-01
**Version**: 1.0.0
**Maintainer**: QFC Core Team
