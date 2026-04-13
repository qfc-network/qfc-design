# QFC Inference — Minimal SDK Snippets

Two minimal examples of calling the QFC public inference API from outside the chain — what any external developer needs to answer "can I actually use this from my app?"

| File | Runtime | Notes |
|------|---------|-------|
| [`call-inference.js`](./call-inference.js) | Node 18+ | Uses native `fetch` and `ethers` v6 |
| [`call-inference.py`](./call-inference.py) | Python 3.10+ | Uses `requests` + `eth-account` |

Both do the same 5 steps:

1. Generate (or load) a wallet
2. Estimate the fee via `qfc_estimateInferenceFee`
3. Prepare and sign the task payload
4. Submit via `qfc_submitPublicTask` — returns `taskId`
5. Poll `qfc_getPublicTaskStatus(taskId)` until `Completed`

Average latency on testnet is under a second for embedding tasks (226ms avg per `qfc_getInferenceStats`).

## What makes this different from calling OpenAI?

- Every call has an on-chain receipt. The miner's proof is verifiable — you can prove the model actually ran on the inputs you sent.
- Rate limits are economic, not policy. Pay more fee → jump the queue. No OpenAI-style usage caps or TOS suspensions.
- The model catalog is open (see `qfc_getSupportedModels`) — anyone can propose a new model via governance.

Today only three embedding/classification models are approved. The pitch above only holds once an actual LLM is on the catalog; this is blocker #1 for Gap B.

## How to run

```bash
# JS
npm install ethers
node call-inference.js

# Python
pip install requests eth-account eth-utils
python3 call-inference.py
```

Both print the submitter address, estimated fee, task ID, miner address that executed, and the result (base64). You need some QFC in the submitter wallet to pay the fee — grab from the faucet first:

```bash
curl https://faucet.testnet.qfc.network/api/faucet \
  -H 'Content-Type: application/json' \
  -d '{"address":"0x<your-address>"}'
```

## Known issues

- The signed payload format (`address + modelId + inputData + maxFee`) is what the RPC validation expects. This is currently undocumented outside this file and the Rust source — needs a proper spec page.
- `result` is base64 of raw bytes (256 dims × f32 for embeddings). An SDK wrapper should decode this to numpy/Float32Array.
- No sample script yet for verifying the proof client-side. The `proofBytes` is a signed attestation by the miner; verification requires the miner's pubkey lookup via `qfc_getRegisteredMiners`.
