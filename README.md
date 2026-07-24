# HTLC Atomic Swap Protocol

A Python implementation and simulation of an HTLC-based cross-chain atomic swap protocol.

This project explores how two parties can exchange assets across independent blockchains without relying on a trusted intermediary. The protocol uses hashlocks, timelocks, and asymmetric refund windows to coordinate the swap.

## Project Goal

The goal of this repository is to turn the protocol logic behind HTLC-based atomic swaps into a clear, testable Python implementation.

The project focuses on:

- HTLC state transitions
- Hashlock and preimage verification
- Redeem and refund paths
- Cross-chain secret revelation
- Asymmetric timeout design
- Aborted and invalid swap scenarios
- Protocol assumptions and limitations

This is a protocol simulation, not a production blockchain application. It does not connect to real networks, wallets, RPC endpoints, or smart contracts.

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

- **Hashlock:** The recipient must reveal a valid preimage whose hash matches the stored hash value.
- **Timelock:** If the recipient does not redeem before the deadline, the original owner can refund the locked asset.

A simplified state transition model is:

```text
LOCKED -> REDEEMED
LOCKED -> REFUNDED
```

A redeemed or refunded HTLC cannot be spent again.

## Protocol Flow

The implementation uses two simulated chains and two HTLCs.

```text
Chain A
Alice locks funds for Bob
Deadline: longer

Chain B
Bob locks funds for Alice
Deadline: shorter
```

The safe timeout condition is:

```text
alice_deadline > bob_deadline
```

The successful flow is:

```text
Alice creates HTLC on Chain A
        |
Bob creates HTLC on Chain B
        |
Alice redeems on Chain B and reveals the secret
        |
Bob reads the revealed secret
        |
Bob redeems on Chain A
```

If the swap stops before completion, each party can use the refund path after the relevant deadline.

## Project Structure

```text
htlc-atomic-swap-protocol/
├── src/
│   └── atomic_swap/
│       ├── __init__.py
│       ├── htlc.py
│       ├── chain.py
│       ├── swap.py
│       └── errors.py
│
├── tests/
│   ├── test_htlc.py
│   ├── test_chain.py
│   └── test_swap.py
│
├── examples/
│   └── successful_swap.py
│
├── docs/
│   └── threat_model.md
│
├── pyproject.toml
└── README.md
```

## Current Implementation

The current version includes:

- A single-contract HTLC state machine
- SHA-256 hashlock verification
- Recipient-only redeem rules
- Owner-only refund rules
- Deadline checks
- Protection against reusing spent contracts
- Independent simulated chain state and time
- Two-chain atomic swap coordination
- Safe timeout-order validation
- Cross-chain secret revelation
- Successful swap flow
- Refund flows for aborted swaps
- Custom protocol errors
- A runnable example
- A documented threat model
- Automated tests for valid and invalid scenarios

## Failure Cases Covered

The test suite covers cases such as:

- invalid preimage
- unauthorized redeem
- unauthorized refund
- redeem at or after the deadline
- refund before the deadline
- redeem after refund
- refund after redeem
- duplicate contract IDs
- negative chain-time movement
- unsafe timeout ordering
- Bob never participating
- Alice never revealing the secret
- Bob trying to redeem before the secret is revealed
- Alice trying to redeem with the wrong secret
- Alice trying to redeem after Bob's deadline

## Running the Example

Install the project first, then run:

```powershell
python examples\successful_swap.py
```

Expected output:

```text
Atomic swap completed
Chain A contract: redeemed
Chain B contract: redeemed
Same secret revealed on both chains: True
```

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

Run the tests with detailed output:

```powershell
pytest -v
```

## Threat Model

The protocol assumptions, failure behavior, security boundaries, and out-of-scope risks are documented in:

```text
docs/threat_model.md
```

The main assumptions are:

- SHA-256 is preimage-resistant.
- Both chains continue processing transactions.
- Bob can observe Alice's redeem transaction.
- HTLC rules are enforced correctly.
- Alice's refund deadline is longer than Bob's.

## Scope

This repository does not attempt to model:

- blockchain consensus
- mining or validators
- chain reorganizations
- mempool behavior
- transaction fees
- real token transfers
- wallet key management
- network communication
- real smart contracts
- production smart-contract security

The current focus is protocol correctness at the state-machine level.

## Roadmap

### v0.1.0 - HTLC Atomic Swap Simulation

- [x] Implement a single HTLC state machine
- [x] Implement redeem and refund rules
- [x] Simulate two independent chains
- [x] Coordinate two HTLCs into an atomic swap
- [x] Model secret revelation across chains
- [x] Validate safe timeout ordering
- [x] Add successful, aborted, and invalid swap tests
- [x] Add a runnable example
- [x] Document the threat model and protocol assumptions

### v0.2.0 - Schnorr Adaptor Signatures

- [ ] Package and reuse the existing elliptic-curve implementation from `crypto-primitives-from-scratch`
- [ ] Implement Schnorr signatures
- [ ] Implement adaptor pre-signatures
- [ ] Implement signature adaptation
- [ ] Extract the secret from the completed signature
- [ ] Compare HTLC-based and scriptless atomic swaps

### v0.3.0 - Schnorr Identification and ZK Analysis

- [ ] Implement the Schnorr identification protocol
- [ ] Explain completeness, soundness, and zero knowledge
- [ ] Clarify why adaptor signatures are not themselves zero-knowledge proofs
- [ ] Compare the role of shared discrete-logarithm mathematics across the protocols

## Disclaimer

This project is for learning, research, and protocol analysis.

It is not production code and should not be used to transfer real assets.
