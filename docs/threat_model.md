# Threat Model

This document explains what this simulation assumes, what kinds of failures it handles, and what it does not try to model.

## Goal

The goal of the protocol is simple:

- Alice and Bob should either complete the swap,
- or both should eventually recover their own funds.

The protocol does not force the swap to finish. One side can stop responding. In that case, funds may stay locked for a while, but the refund paths should prevent a permanent loss.

## Parties

There are two parties:

- Alice starts the swap.
- Bob joins the swap.

Alice locks an asset on Chain A.

Bob locks another asset on Chain B using the same hashlock.

Alice knows the secret preimage. Bob only knows its hash at the beginning.

## What Can Go Wrong?

Either side may:

- stop responding,
- use the wrong preimage,
- try to redeem too late,
- try to refund too early,
- call a method they are not allowed to call,
- try to use an HTLC that was already redeemed or refunded.

The implementation rejects these cases through the HTLC state machine and the swap tests.

## Assumptions

### SHA-256 is secure

The simulation assumes SHA-256 is preimage-resistant.

Bob sees:

```text
hash = SHA256(secret)
```

but should not be able to recover `secret` from the hash before Alice reveals it.

### Both chains keep running

The protocol assumes both chains continue processing transactions.

If one chain stops for too long, a party may miss the redeem or refund window.

### The chains can be observed

Bob must be able to see Alice's redeem transaction on Chain B.

That is how he learns the secret and uses it on Chain A.

In this simulation, the revealed secret is stored in `revealed_preimage`.

### HTLC rules are enforced correctly

The implementation assumes that the HTLC enforces the following rules:

- only the recipient can redeem,
- only the owner can refund,
- the preimage must match the hashlock,
- redeem must happen before the deadline,
- refund must happen at or after the deadline,
- redeemed or refunded contracts cannot be used again.

### Alice's deadline is longer

Alice's deadline must be greater than Bob's deadline:

```text
alice_deadline > bob_deadline
```

This gives Bob time to see the secret on Chain B and use it on Chain A.

Equal or reversed deadlines are rejected.

## Failure Cases

### Bob never joins

Alice creates the first HTLC, but Bob never creates the second one.

Alice waits until her deadline and refunds her funds.

### Alice never reveals the secret

Both HTLCs are created, but Alice never redeems Bob's contract.

Bob refunds after the shorter deadline.

Alice refunds after the longer deadline.

### Alice uses the wrong secret

The hash does not match the stored hashlock.

The redeem call fails and both contracts stay locked.

### Bob tries to redeem too early

Before Alice redeems on Chain B, there is no revealed secret for Bob to use.

The call fails with `SecretNotRevealed`.

### A contract is used twice

Once an HTLC reaches `REDEEMED` or `REFUNDED`, it cannot move to another state.

## What This Does Not Prevent

HTLCs protect funds from being permanently taken by the other side, but they do not stop griefing.

For example, Bob may wait until Alice locks her funds and then disappear. Alice can refund later, but her funds stay locked until the deadline.

The protocol also does not remove:

- transaction fees,
- price changes during the swap,
- confirmation delays,
- fee spikes,
- censorship,
- chain halts,
- chain reorganizations.

## Out of Scope

This project does not model:

- consensus,
- validators or miners,
- block production,
- chain reorganizations,
- mempools,
- front-running,
- real wallets,
- private keys,
- token balances,
- network communication,
- real smart contracts,
- majority attacks.

## Final Note

This is a deterministic Python simulation of the protocol logic.

It is meant to show how HTLC-based atomic swaps work and how the main failure paths are handled. It is not production code and should not be used with real assets.
