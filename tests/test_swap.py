from hashlib import sha256
import pytest
from atomic_swap.chain import SimulatedChain
from atomic_swap.errors import UnsafeTimeoutOrder
from atomic_swap.swap import AtomicSwap

def test_atomic_swap_accepts_safe_timeout_order() -> None:
    swap = AtomicSwap(
        chain_a=SimulatedChain(name="ChainA"),
        chain_b=SimulatedChain(name="ChainB"),
        alice="Alice",
        bob="Bob",
        hash_value=sha256(b"atomic swap secret").digest(),
        alice_contract_id="alice-lcok",
        bob_contract_id="bob-lock",
        alice_deadline=100,
        bob_deadline=50,
        alice_amount=100,
        bob_amount=250,
    )
    assert swap.alice_deadline == 100
    assert swap.bob_deadline == 50


def test_equal_deadlines_are_rejected() -> None:
    with pytest.raises(UnsafeTimeoutOrder):
        AtomicSwap(
            chain_a=SimulatedChain(name="ChainA"),
            chain_b=SimulatedChain(name="ChainB"),
            alice="Alice",
            bob="Bob",
            hash_value=sha256(b"atomic swap secret").digest(),
            alice_contract_id="alice-lock",
            bob_contract_id="bob-lock",
            alice_deadline=50,
            bob_deadline=50,
            alice_amount=100,
            bob_amount=250,
        )


def test_shorter_alice_deadline_is_rejected() -> None:
    with pytest.raises(UnsafeTimeoutOrder):
        AtomicSwap(
            chain_a=SimulatedChain(name="Chain A"),
            chain_b=SimulatedChain(name="Chain B"),
            alice="Alice",
            bob="Bob",
            hash_value=sha256(b"atomic swap secret").digest(),
            alice_contract_id="alice-lock",
            bob_contract_id="bob-lock",
            alice_deadline=40,
            bob_deadline=50,
            alice_amount=100,
            bob_amount=250,
        )
