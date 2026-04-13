# Gap A — Miner Onboarding Path Review

> Date: 2026-04-14
> Scope: `qfc-network/qfc-miner` repo + `start-miner.sh` script + release assets

## TL;DR

The infrastructure is more complete than I initially thought (binaries built, one-click scripts, README), **but there are two real bugs an external miner would hit today**:

1. **Release-repo mismatch** — `start-miner.sh` downloads from `qfc-network/qfc-core` (v2.3.1, 5 platforms) but the miner repo is `qfc-network/qfc-miner` (v2.3.2, 9 platforms). CUDA / OpenCL / Windows / ARM64-CUDA users will hit "No pre-built binary" and fall back to source build (which requires Rust + CUDA toolkit — a showstopper for most).
2. **Version drift** — chain runs v2.2.3 (via `qfc_nodeInfo`), binaries are v2.3.1/v2.3.2. Minor version mismatch should be fine but hasn't been verified end-to-end.

Both are real onboarding failures waiting to happen.

## Evidence

```
$ curl -s -X POST https://rpc.testnet.qfc.network \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","method":"qfc_nodeInfo","params":[],"id":1}'
{"jsonrpc":"2.0","result":{"version":"2.2.3","chainId":"0x2328",...}}
```

```
qfc-core v2.3.1 (latest):       5 assets
  qfc-linux-arm64
  qfc-linux-x86_64
  qfc-linux-x86_64-rocm
  qfc-macos-arm64
  qfc-macos-intel

qfc-miner v2.3.2 (latest):      9 platforms
  qfc-linux-arm64
  qfc-linux-arm64-cuda        ← not in qfc-core
  qfc-linux-x86_64
  qfc-linux-x86_64-cuda       ← not in qfc-core
  qfc-linux-x86_64-opencl     ← not in qfc-core
  qfc-macos-arm64
  qfc-macos-intel
  qfc-windows-x86_64          ← not in qfc-core
  (no rocm variant)
```

`start-miner.sh` auto-detects `linux-x86_64-cuda` when `nvidia-smi` is present. It then hits `qfc-network/qfc-core` (per `GITHUB_REPO` constant), can't find the asset, logs "No pre-built binary found for linux-x86_64-cuda. Falling back to build from source" — **silently changing to a 15-minute Rust build that requires toolchain installation**. A first-time user will not know that "fallback" just happened.

## Platform matrix — what fails today

| Platform detected | qfc-core v2.3.1 | qfc-miner v2.3.2 | Result with current script |
|---|---|---|---|
| macos-arm64 (M-series) | ✓ | ✓ | works |
| macos-intel (2017 Intel MBP, OP's test rig) | ✓ | ✓ | works |
| linux-x86_64 (VPS, no GPU) | ✓ | ✓ | works |
| linux-x86_64-cuda (NVIDIA home rig) | ✗ | ✓ | **silent fallback to source build** |
| linux-x86_64-opencl (AMD home rig) | ✗ | ✓ | **silent fallback to source build** |
| linux-x86_64-rocm (AMD prosumer) | ✓ | ✗ | works |
| linux-arm64 (Raspberry Pi 4/5) | ✓ | ✓ | works |
| linux-arm64-cuda (DGX Spark) | ✗ | ✓ | **silent fallback to source build** |
| windows-x86_64 | ✗ (no .zip) | ✓ | **script doesn't detect Windows at all** |

Windows users use `install.ps1` instead, which I haven't audited yet. The README implies this works but it needs the same end-to-end test.

## Recommended fix (minimal)

Two clean options:

- **Option A**: Point binary downloads at `qfc-network/qfc-miner`, keep source-clone path at `qfc-network/qfc-core`. Requires adding a `BINARIES_REPO` variable. Fast, safe.
- **Option B**: Have the `qfc-core` release pipeline also publish to `qfc-miner` so either works. Longer-term cleaner but a CI change.

Going with A today — a surgical script fix. Option B can be scheduled separately.

## Still untested (not my job here, but must be done before external traffic)

- [ ] End-to-end clean install on a fresh Ubuntu VPS (no dev tools, no env leakage). Record every friction point. **This is Gap A's real validation.** The user said they have a 2017 Intel MBP on Ubuntu — that's the right rig.
- [ ] v2.3.2 binary actually executes on chain v2.2.3 (protocol compat)
- [ ] `qfc_requestFaucet` via the script still gives test QFC (the 3 wallets we just funded had partial failure — parallel requests silently drop)
- [ ] Windows `install.ps1` goes all the way through on a plain Windows 11 box
- [ ] First-day UX: miner starts → explorer shows address earning → user can see "I'm making N QFC/hour" somewhere visible

## Quick wins that unlock the rest

1. Fix the script (this commit)
2. Add `/miner/[address]` page in explorer (next task)
3. Update the README to remove the release-source confusion (say clearly: "binaries come from qfc-miner releases")
