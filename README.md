# Tezos IP Registry

SmartPy contract for registering intellectual property hashes on Tezos blockchain.

## Features

- Register SHA-256 hashes with metadata (code, description, timestamp, block level)
- Batch registration in a single transaction (gas savings)
- Master hash: hash of all hashes — one transaction proves entire portfolio
- Ownership transfer
- Owner-only access control

## Usage

1. Open [SmartPy IDE](https://smartpy.io/ide)
2. Paste `ip_registry.py`
3. Click Run to verify tests pass
4. Deploy to Ghostnet (testnet) first, then Mainnet
5. Use [Temple Wallet](https://templewallet.com/) to sign transactions

## Contract Interface

| Entrypoint | Description |
|---|---|
| `register(code, sha256, description)` | Register a single IP asset hash |
| `register_batch(entries)` | Register multiple hashes in one tx |
| `set_master_hash(hash)` | Set portfolio-level proof hash |
| `transfer_ownership(new_owner)` | Transfer registry to new address |

## Part of the Coherence Control family

This repository provides the blockchain IP anchoring layer used across the coherence ecosystem.

Core: [coherence-core](https://github.com/coherence-lab/coherence-core)

## License

AGPL-3.0 — see [LICENSE](LICENSE)
