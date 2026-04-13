/*
 * QFC Inference Demo Relay
 * ------------------------
 * Lets an anonymous browser visitor try QFC inference without needing a wallet
 * or testnet QFC. The relay holds a pre-funded key and signs + submits on the
 * visitor's behalf. Rate-limited per IP.
 *
 * Required env:
 *   QFC_RELAY_PRIVATE_KEY    64-char hex (no 0x prefix OK, but 0x... also OK)
 *
 * Optional env:
 *   QFC_RPC_URL              default https://rpc.testnet.qfc.network
 *   QFC_RELAY_PORT           default 3290
 *   QFC_RELAY_MODEL          default qfc-embed-small:v1.0
 *   QFC_RELAY_RATE_LIMIT     requests per IP per hour, default 10
 *   QFC_RELAY_MAX_INPUT_LEN  default 512 chars
 */

import express from "express";
import rateLimit from "express-rate-limit";
import { ethers } from "ethers";

const RPC_URL = process.env.QFC_RPC_URL || "https://rpc.testnet.qfc.network";
const PORT = Number(process.env.QFC_RELAY_PORT || "3290");
const MODEL = process.env.QFC_RELAY_MODEL || "qfc-embed-small:v1.0";
const RATE_LIMIT = Number(process.env.QFC_RELAY_RATE_LIMIT || "10");
const MAX_INPUT_LEN = Number(process.env.QFC_RELAY_MAX_INPUT_LEN || "512");
const PRIVATE_KEY = process.env.QFC_RELAY_PRIVATE_KEY;

if (!PRIVATE_KEY) {
  console.error("QFC_RELAY_PRIVATE_KEY is required");
  process.exit(1);
}

const provider = new ethers.JsonRpcProvider(RPC_URL);
const wallet = new ethers.Wallet(
  PRIVATE_KEY.startsWith("0x") ? PRIVATE_KEY : "0x" + PRIVATE_KEY,
  provider
);

console.log("Relay wallet:", wallet.address);
provider.getBalance(wallet.address).then((bal) => {
  console.log("Relay balance:", ethers.formatEther(bal), "QFC");
  if (bal < ethers.parseEther("1")) {
    console.warn("WARN: relay balance below 1 QFC — fund via faucet before running out");
  }
});

async function rpc(method, params) {
  const r = await fetch(RPC_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ jsonrpc: "2.0", method, params, id: 1 }),
  });
  const { result, error } = await r.json();
  if (error) throw new Error(`${method}: ${error.message}${error.data ? " — " + error.data : ""}`);
  return result;
}

const app = express();
// Behind Traefik / reverse proxy — trust first hop so express-rate-limit can see the real client IP.
app.set("trust proxy", 1);
app.use(express.json({ limit: "32kb" }));

// Rate limit — per IP, sliding window
app.use("/api/", rateLimit({
  windowMs: 60 * 60 * 1000,
  limit: RATE_LIMIT,
  standardHeaders: "draft-7",
  legacyHeaders: false,
  message: { error: `Too many requests — limit is ${RATE_LIMIT}/hour per IP.` },
}));

// Static frontend — defaults to sibling public/ when run from relay/ locally,
// override with QFC_DEMO_STATIC_DIR in containers (Dockerfile sets it to ./public).
app.use(express.static(process.env.QFC_DEMO_STATIC_DIR || "../public"));

// Relay endpoint
app.post("/api/inference", async (req, res) => {
  try {
    const text = String(req.body?.text ?? "").slice(0, MAX_INPUT_LEN);
    if (!text.trim()) return res.status(400).json({ error: "Empty input" });

    // Fee estimate
    const fee = await rpc("qfc_estimateInferenceFee", [{
      modelId: MODEL,
      taskType: "TextEmbedding",
      inputSize: Buffer.byteLength(text, "utf8"),
      maxTokens: 100,
    }]);

    const inputDataHex = "0x" + Buffer.from(text, "utf8").toString("hex");
    const maxFeeWei = 2n * BigInt(fee.baseFee);
    const maxFeeHex = "0x" + maxFeeWei.toString(16);

    const payload = ethers.solidityPacked(
      ["address", "string", "bytes", "uint256"],
      [wallet.address, MODEL, inputDataHex, maxFeeHex]
    );
    const signature = await wallet.signMessage(ethers.getBytes(payload));

    const taskId = await rpc("qfc_submitPublicTask", [{
      taskType: "TextEmbedding",
      modelId: MODEL,
      inputData: inputDataHex,
      maxFee: maxFeeHex,
      submitter: wallet.address,
      signature,
    }]);

    // Poll for up to 10 s
    const started = Date.now();
    while (Date.now() - started < 10_000) {
      const status = await rpc("qfc_getPublicTaskStatus", [taskId]);
      if (status.status === "Completed") {
        return res.json({
          taskId,
          minerAddress: status.minerAddress,
          blockHeight: status.blockHeight,
          executionTimeMs: status.executionTimeMs,
          result: status.result,
          explorerUrl: `https://explorer.testnet.qfc.network/task/${taskId}`,
        });
      }
      if (status.status === "Failed" || status.status === "Expired") {
        return res.status(500).json({ error: `Task ${status.status}`, taskId });
      }
      await new Promise((r) => setTimeout(r, 300));
    }
    res.status(504).json({ error: "Timeout waiting for inference" });
  } catch (err) {
    console.error("Relay error:", err);
    res.status(500).json({ error: err?.message ?? "Unknown error" });
  }
});

app.get("/api/health", async (_req, res) => {
  const bal = await provider.getBalance(wallet.address).catch(() => null);
  res.json({
    ok: true,
    wallet: wallet.address,
    balanceQfc: bal ? ethers.formatEther(bal) : null,
    rpc: RPC_URL,
    model: MODEL,
  });
});

app.listen(PORT, () => {
  console.log(`Relay listening on :${PORT}`);
});
