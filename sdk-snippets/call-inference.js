/*
 * QFC Inference — minimal JavaScript example
 * Submit a public inference task, wait for completion, fetch result.
 *
 * Requires: node 18+ (native fetch), `npm install ethers`
 * Run:      node call-inference.js
 *
 * For full example with signatures + result verification see qfc-sdk-js.
 */

import { ethers } from "ethers";

const RPC = "https://rpc.testnet.qfc.network";

async function rpc(method, params) {
  const r = await fetch(RPC, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ jsonrpc: "2.0", method, params, id: 1 }),
  });
  const { result, error } = await r.json();
  if (error) throw new Error(`${method}: ${error.message}${error.data ? " — " + error.data : ""}`);
  return result;
}

async function main() {
  // 1. Generate / load a wallet (in production, load from secure storage)
  const wallet = ethers.Wallet.createRandom();
  console.log("Submitter:", wallet.address);

  // 2. Estimate fee for the task
  const fee = await rpc("qfc_estimateInferenceFee", [{
    modelId: "qfc-embed-small:v1.0",
    taskType: "TextEmbedding",
    inputSize: 512,
    maxTokens: 100,
  }]);
  console.log(`Estimated fee: ${ethers.formatEther(fee.baseFee)} QFC (~${fee.estimatedTimeMs}ms)`);

  // 3. Prepare + sign the task. The signature binds (submitter, modelId, inputData, maxFee).
  const inputText = "Hello QFC, prove you can compute this embedding.";
  const inputDataHex = "0x" + Buffer.from(inputText, "utf8").toString("hex");
  const maxFeeHex = "0x" + (2n * BigInt(fee.baseFee)).toString(16); // 2× the estimate for safety
  const payload = ethers.solidityPacked(
    ["address", "string", "bytes", "uint256"],
    [wallet.address, "qfc-embed-small:v1.0", inputDataHex, maxFeeHex]
  );
  const signature = await wallet.signMessage(ethers.getBytes(payload));

  // 4. Submit the task
  const taskId = await rpc("qfc_submitPublicTask", [{
    taskType: "TextEmbedding",
    modelId: "qfc-embed-small:v1.0",
    inputData: inputDataHex,
    maxFee: maxFeeHex,
    submitter: wallet.address,
    signature,
  }]);
  console.log("Submitted task:", taskId);

  // 5. Poll for completion (usually < 1s on testnet)
  for (let attempt = 0; attempt < 60; attempt++) {
    const status = await rpc("qfc_getPublicTaskStatus", [taskId]);
    if (status.status === "Completed") {
      console.log(`\nCompleted in ${status.executionTimeMs}ms by miner ${status.minerAddress}`);
      console.log("Result (base64):", status.result);
      console.log("Verifiable: proof on-chain at block", status.blockHeight);
      return;
    }
    if (status.status === "Failed" || status.status === "Expired") {
      throw new Error(`Task ${status.status}: ${status.failureReason ?? "unknown"}`);
    }
    await new Promise((r) => setTimeout(r, 500));
  }
  throw new Error("Timeout waiting for inference result");
}

main().catch((err) => {
  console.error("Error:", err.message);
  process.exit(1);
});
