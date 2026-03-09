# QFC Blockchain - Quick Start Guide

> **The first instruction for Claude Code**

## Project Introduction

Hi Claude Code! I'm developing the **QFC blockchain project**.

**QFC** is a high-performance blockchain with core innovations including:
- ✨ **PoC (Proof of Contribution)** consensus mechanism - Multi-dimensional contribution scoring
- 🚀 **Multi-VM architecture** - QVM + EVM + WASM + AI-VM
- ⚡ **Extreme performance** - Target TPS 500k+, confirmation time <0.3s
- 🔐 **Quantum resistance** - Lattice-based cryptography

## Document Structure

All design documents are in the `docs/` directory:

```
docs/
├── 00-PROJECT-OVERVIEW.md          # 📋 Project overview (must read)
├── 01-BLOCKCHAIN-DESIGN.md         # ⛓️ Blockchain core design
├── 02-CONSENSUS-MECHANISM.md       # 🎯 PoC consensus mechanism details
├── 03-SMART-CONTRACT-SYSTEM.md     # 📝 Smart contract system
├── 04-NODE-OPERATION.md            # 🖥️ Node operation
├── 05-BLOCK-EXPLORER.md            # 🔍 Block explorer
├── 06-TESTNET-SETUP.md             # 🧪 Testnet setup
├── 07-WALLET-DESIGN.md             # 💼 Wallet design
└── START-HERE.md                   # 👉 This file
```

## Current Task: Browser Extension Wallet

**Why build the wallet first?**
- Developers need it to test DApps
- Quickly validate blockchain RPC interfaces
- Low cost, fast iteration
- Good desktop user experience

**Target deliverables:**
- Chrome/Firefox browser extension
- MetaMask-like experience
- Support for QFC testnet

---

## Step 1: Read the Design Documents

Before writing any code, please **make sure** to read the following documents:

### Required Reading
1. **`00-PROJECT-OVERVIEW.md`** - Understand the full project picture
   - Core innovations
   - Technology stack
   - Project phases

2. **`07-WALLET-DESIGN.md`** - Complete wallet design
   - Technical architecture
   - Directory structure
   - Core code examples
   - Security requirements

### Recommended Reading
3. **`02-CONSENSUS-MECHANISM.md`** - Understand what makes QFC unique
4. **`06-TESTNET-SETUP.md`** - Learn about testnet configuration

---

## Step 2: Initialize the Project

### Project Structure

```bash
qfc-blockchain/
├── wallet/
│   └── extension/              # 👈 We start here
│       ├── src/
│       │   ├── background/     # Background service (key management, transaction signing)
│       │   ├── content/        # Content script (injected into web pages)
│       │   ├── inpage/         # window.qfc Provider
│       │   ├── popup/          # Popup UI
│       │   └── utils/          # Utility functions
│       ├── public/
│       │   ├── manifest.json   # Chrome extension configuration
│       │   └── icons/
│       ├── package.json
│       ├── tsconfig.json
│       ├── vite.config.ts
│       └── README.md
```

### Technology Stack

- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Styling**: TailwindCSS
- **State**: Zustand
- **Crypto**: ethers.js v6
- **Storage**: chrome.storage.local

---

## Step 3: Start Implementation

### Implementation Plan

#### Phase 1: Project Scaffolding (Day 1-2)

**Task:**
```
Please help me initialize the browser wallet project:

1. Create the project structure
   cd wallet/extension
   npm create vite@latest . -- --template react-ts

2. Install dependencies
   - ethers@^6.0.0
   - @types/chrome
   - tailwindcss
   - zustand
   - lucide-react (icons)

3. Configure Vite for Chrome extension builds
   - Multiple entry points (popup, background, content, inpage)
   - Output format configuration
   - manifest.json handling

4. Create the base directory structure
   Follow the directory structure in 07-WALLET-DESIGN.md

5. Create manifest.json
   Refer to the configuration in the design document
```

**Acceptance criteria:**
- ✅ `npm run build` succeeds
- ✅ Extension can be loaded in Chrome (chrome://extensions)
- ✅ Clicking the icon opens a blank popup

#### Phase 2: Provider Injection (Day 3-4)

**Task:**
```
Implement the window.qfc Provider:

Refer to the "inpage/provider.ts" section in 07-WALLET-DESIGN.md

Requirements:
1. Implement the EIP-1193 standard interface
2. Supported methods:
   - eth_requestAccounts
   - eth_accounts
   - eth_chainId
   - eth_sendTransaction
   - personal_sign
   - eth_signTypedData_v4

3. Event support:
   - accountsChanged
   - chainChanged
   - connect
   - disconnect

4. Message communication with background

5. MetaMask compatibility (set window.ethereum)
```

**Test:**
Create a simple test page:
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

**Task:**
```
Implement the background wallet manager:

Refer to the "background/WalletController.ts" section in 07-WALLET-DESIGN.md

Core features:
1. Wallet management
   - createWallet() - Create a new wallet
   - importWallet() - Import wallet (private key/mnemonic)
   - getAllAccounts() - Get all accounts
   - switchAccount() - Switch account

2. Authentication
   - unlock() - Unlock wallet
   - lock() - Lock wallet
   - 30-minute auto-lock

3. Transactions
   - sendTransaction() - Send transaction
   - signMessage() - Sign message
   - signTypedData() - Sign typed data

4. Queries
   - getBalance() - Get balance
   - Communicate with RPC node

Security requirements:
- Encrypted private key storage (using crypto.ts)
- Password is never saved
- Sensitive operations reset the auto-lock timer
```

#### Phase 4: Popup UI (Day 8-10)

**Task:**
```
Implement the user interface:

Refer to the "popup/pages" section in 07-WALLET-DESIGN.md

Pages:
1. CreateWallet.tsx - Create wallet
   - Generate mnemonic
   - Set password
   - Backup reminder

2. ImportWallet.tsx - Import wallet
   - Enter mnemonic/private key
   - Set password

3. Unlock.tsx - Unlock page
   - Enter password
   - Error messages

4. Home.tsx - Home page
   - Display balance
   - Asset list
   - Quick actions (send/receive)
   - Recent transactions

5. Send.tsx - Send page
   - Enter recipient address
   - Enter amount
   - Gas settings
   - Confirmation

6. Settings.tsx - Settings page
   - Account management
   - Network switching
   - Lock wallet

Design requirements:
- Use TailwindCSS
- Responsive (400x600px popup)
- Smooth animations
- Clear error messages
```

#### Phase 5: Testing & Optimization (Day 11-12)

**Task:**
```
1. Unit tests
   - WalletController tests
   - Encryption utility tests
   - Provider tests

2. Integration tests
   - End-to-end workflow testing
   - Testnet interaction

3. Security review
   - XSS protection check
   - Key management review
   - Input validation

4. Performance optimization
   - Reduce bundle size
   - Optimize loading speed

5. Documentation
   - README.md
   - User guide
   - Developer documentation
```

---

## Implementation Details

### How to Interact with Me

#### ✅ Good Prompting Style

```
Please implement wallet/extension/src/background/WalletController.ts

Requirements:
1. Follow the design in docs/07-WALLET-DESIGN.md
2. Include complete type definitions
3. Add detailed comments
4. Include error handling
5. Provide unit test examples

I will confirm feature by feature, please start with the createWallet() method.
```

#### ❌ Prompting Style to Avoid

```
Build me a wallet
```

### Step-by-Step Implementation

**Don't request all features at once!** Suggested order:

1. **Day 1**: Project initialization + manifest.json
2. **Day 2**: Provider basic structure
3. **Day 3**: Provider full implementation
4. **Day 4**: Background basic framework
5. **Day 5**: WalletController core methods
6. **Day 6**: Transaction and signing features
7. **Day 7**: Background full testing
8. **Day 8**: Popup basic UI
9. **Day 9**: Main pages (Home, Send)
10. **Day 10**: Create/Import/Unlock flow
11. **Day 11**: Testing and bug fixes
12. **Day 12**: Optimization and documentation

### Acceptance Criteria

After completing each phase, ensure:

- ✅ Code runs successfully
- ✅ No TypeScript errors
- ✅ Passes basic tests
- ✅ Has clear comments

---

## Key Configuration Files

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

## FAQ

### Q: What is the RPC node address?
**A**: Testnet RPC: `https://rpc.testnet.qfc.network`
(Note: This may not exist initially. You can use a local node or an Ethereum testnet for development first.)

### Q: What is the Chain ID?
**A**:
- Mainnet: TBD
- Testnet: 9000 (0x2328)

### Q: How do I get test tokens?
**A**: Faucet address (available after testnet launch): `https://faucet.testnet.qfc.network`

### Q: Do I need to implement all EIP-1193 methods?
**A**: Initially focus on implementing:
- eth_requestAccounts
- eth_accounts
- eth_chainId
- eth_sendTransaction
- personal_sign
- eth_getBalance
- eth_blockNumber

Other methods can be forwarded to the RPC node for now.

---

## Development Principles

### 1. Security First 🔐
- Handle key management with extreme care
- Encrypted storage
- Input validation
- XSS protection

### 2. Code Quality 📝
- TypeScript strict mode
- Detailed comments
- Unit tests
- Error handling

### 3. User Experience ✨
- Clear interface
- Helpful error messages
- Smooth animations
- Responsive design

### 4. Iterative Development 🔄
- Implement core features first
- Add features incrementally
- Test continuously
- Refactor promptly

---

## Resource Links

### Official Documentation
- [Chrome Extension Docs](https://developer.chrome.com/docs/extensions/mv3/)
- [EIP-1193](https://eips.ethereum.org/EIPS/eip-1193)
- [ethers.js Docs](https://docs.ethers.org/v6/)

### Reference Projects
- [MetaMask](https://github.com/MetaMask/metamask-extension)
- [Rabby](https://github.com/RabbyHub/Rabby)
- [Frame](https://github.com/floating/frame)

---

## Next Steps

After completing the browser wallet, we will:

1. **Set up the testnet** (docs/06-TESTNET-SETUP.md)
2. **Develop the block explorer** (docs/05-BLOCK-EXPLORER.md)
3. **Implement the core blockchain** (docs/01-BLOCKCHAIN-DESIGN.md)

---

## Get Started Now!

### First Instruction for Claude Code

```
I want to start implementing the QFC browser wallet.

Please first:
1. Read docs/07-WALLET-DESIGN.md
2. Create the base project structure (follow the "Directory Structure" section)
3. Set up package.json, tsconfig.json, vite.config.ts
4. Create manifest.json

Once done, we will implement the core features step by step.
```

---

**Last updated**: 2026-02-01
**Version**: 1.0.0
**Maintainer**: QFC Core Team

Happy coding! Have any questions, feel free to ask 💪
