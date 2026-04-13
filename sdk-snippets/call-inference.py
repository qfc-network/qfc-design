"""
QFC Inference — minimal Python example
Submit a public inference task, wait for completion, fetch result.

Requires: pip install requests eth-account eth-utils
Run:      python3 call-inference.py

For full example with signatures + result verification see qfc-sdk-python.
"""

from __future__ import annotations
import time
import requests
from eth_account import Account
from eth_account.messages import encode_defunct
from eth_utils import keccak

RPC = "https://rpc.testnet.qfc.network"


def rpc(method: str, params: list) -> dict:
    r = requests.post(RPC, json={"jsonrpc": "2.0", "method": method, "params": params, "id": 1}, timeout=10)
    body = r.json()
    if "error" in body:
        raise RuntimeError(f"{method}: {body['error']['message']} — {body['error'].get('data')}")
    return body["result"]


def main() -> None:
    # 1. Generate / load a wallet (in production, load from secure storage)
    acct = Account.create()
    print("Submitter:", acct.address)

    # 2. Estimate fee
    fee = rpc("qfc_estimateInferenceFee", [{
        "modelId": "qfc-embed-small:v1.0",
        "taskType": "TextEmbedding",
        "inputSize": 512,
        "maxTokens": 100,
    }])
    base_fee_wei = int(fee["baseFee"], 16)
    print(f"Estimated fee: {base_fee_wei / 1e18:.6f} QFC (~{fee['estimatedTimeMs']}ms)")

    # 3. Prepare + sign the task
    input_text = "Hello QFC, prove you can compute this embedding."
    input_data_hex = "0x" + input_text.encode("utf-8").hex()
    max_fee_wei = 2 * base_fee_wei  # 2× the estimate for safety
    max_fee_hex = "0x" + format(max_fee_wei, "x")

    # Signed payload binds (submitter, modelId, inputData, maxFee)
    payload = (
        bytes.fromhex(acct.address[2:])
        + "qfc-embed-small:v1.0".encode("utf-8")
        + bytes.fromhex(input_data_hex[2:])
        + max_fee_wei.to_bytes(32, "big")
    )
    msg = encode_defunct(keccak(payload))
    signed = Account.sign_message(msg, private_key=acct.key)
    signature = signed.signature.hex()

    # 4. Submit the task
    task_id = rpc("qfc_submitPublicTask", [{
        "taskType": "TextEmbedding",
        "modelId": "qfc-embed-small:v1.0",
        "inputData": input_data_hex,
        "maxFee": max_fee_hex,
        "submitter": acct.address,
        "signature": "0x" + signature,
    }])
    print("Submitted task:", task_id)

    # 5. Poll for completion (usually < 1s on testnet)
    for _ in range(60):
        status = rpc("qfc_getPublicTaskStatus", [task_id])
        if status["status"] == "Completed":
            print(f"\nCompleted in {status['executionTimeMs']}ms by miner {status['minerAddress']}")
            print("Result (base64):", status.get("result"))
            print("Verifiable: proof on-chain at block", status.get("blockHeight"))
            return
        if status["status"] in ("Failed", "Expired"):
            raise RuntimeError(f"Task {status['status']}: {status.get('failureReason', 'unknown')}")
        time.sleep(0.5)

    raise TimeoutError("Timeout waiting for inference result")


if __name__ == "__main__":
    main()
