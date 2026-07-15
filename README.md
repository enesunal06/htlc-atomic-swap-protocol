# HTLC Atomic Swap Protocol

A Python implementation and simulation of an HTLC-based cross-chain atomic swap protocol.

This project explores how two parties can exchange assets across independent blockchains without relying on a trusted intermediary. The protocol uses hashlocks, timelocks, and asymmetric refund windows to coordinate the swap.

## Project Goal

The goal of this repository is to turn the protocol logic behind HTLC-based atomic swaps into a clear, testable Python implementation.

The project focuses on:

* HTLC state transitions
* Hashlock and preimage verification
* Redeem and refund paths
* Cross-chain secret revelation
* Asymmetric timeout design
* Aborted and invalid swap scenarios
* Protocol assumptions and limitations

This is a protocol simulation, not a production blockchain application. The first version does not connect to real networks, wallets, RPC endpoints, or smart contracts.

## Why This Project?

Atomic swaps solve a basic cross-chain exchange problem.

Suppose Alice owns an asset on Chain A and Bob owns an asset on Chain B. They want to exchange these assets, but neither party wants to send first or trust a centralized intermediary.

An HTLC-based atomic swap links two separate contracts using the same hashlock:

1. Alice chooses a secret and shares its hash with Bob.
2. Alice locks her asset on Chain A.
3. Bob locks his asset on Chain B using the same hash.
4. Alice reveals the secret to redeem Bob's asset.
5. Bob observes the revealed secret and uses it to redeem Alice's asset.
6. If the swap is not completed, both parties recover their assets through refund paths.

The two blockchains do not communicate directly. They are connected logically through the shared secret.

## What Is an HTLC?

HTLC stands for Hash Time-Locked Contract.

An HTLC combines two conditions:

* **Hashlock:** The recipient must reveal a valid preimage whose hash matches the stored hash value.
* **Timelock:** If the recipient does not redeem before the deadline, the original owner can refund the locked asset.

A simplified state transition model is:

```text
LOCKED -> REDEEMED
LOCKED -> REFUNDED
```

A redeemed or refunded HTLC cannot be spent again.

## Planned Structure

```text
htlc-atomic-swap-protocol/
├── src/
│   └── atomic_swap/
│       ├── __init__.py
│       ├── htlc.py
│       ├── chain.py
│       ├── swap.py
│       ├── errors.py
│       └── events.py
│
├── tests/
├── examples/
├── docs/
├── pyproject.toml
└── README.md
```

## Roadmap

### v0.1.0 - HTLC Atomic Swap Simulation

* Implement a single HTLC state machine
* Implement redeem and refund rules
* Simulate two independent chains
* Coordinate two HTLCs into an atomic swap
* Model secret revelation across chains
* Validate safe timeout ordering
* Add successful, aborted, and invalid swap tests
* Document the threat model and protocol assumptions

### v0.2.0 - Schnorr Adaptor Signatures

* Package and reuse the existing elliptic-curve implementation from `crypto-primitives-from-scratch`
* Implement Schnorr signatures
* Implement adaptor pre-signatures
* Implement signature adaptation
* Extract the secret from the completed signature
* Compare HTLC-based and scriptless atomic swaps

### v0.3.0 - Schnorr Identification and ZK Analysis

* Implement the Schnorr identification protocol
* Explain completeness, soundness, and zero knowledge
* Clarify why adaptor signatures are not themselves zero-knowledge proofs
* Compare the role of shared discrete-logarithm mathematics across the protocols

## Current Status

The repository structure and Python development environment have been initialized.

The next step is to implement the single-contract HTLC state machine and its unit tests.

## Development Setup

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the project and development dependencies:

```powershell
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Run the test suite:

```powershell
pytest
```

## Scope

This repository currently does not attempt to model:

* Blockchain consensus
* Mining or validators
* Chain reorganizations
* Mempool behavior
* Transaction fees
* Real token transfers
* Wallet key management
* Production smart-contract security

The initial focus is protocol correctness at the state-machine level.
