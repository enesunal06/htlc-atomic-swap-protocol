from hashlib import sha256
import pytest
from atomic_swap.chain import SimulatedChain
from atomic_swap.errors import UnsafeTimeoutOrder, SecretNotRevealed, InvalidPreimage, DeadlineExpired
from atomic_swap.swap import AtomicSwap
from atomic_swap.htlc import HTLCState

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

def test_succesful_atomic_swap_redeems_both_contracts() -> None:
    secret = b"atomic swap secret"
    swap = AtomicSwap(
        chain_a=SimulatedChain(name="ChainA"),
        chain_b=SimulatedChain(name="ChainB"),
        alice="Alice",
        bob="Bob",
        alice_amount=100,
        bob_amount=250,
        hash_value=sha256(secret).digest(),
        alice_contract_id="alice-lock",
        bob_contract_id="bob-lock",
        alice_deadline=100,
        bob_deadline=50,
    )
    swap.initiate()
    swap.participate()
    swap.chain_b.advance_time(20)
    swap.alice_redeem(secret)
    swap.chain_a.advance_time(30)
    swap.bob_redeem()
    alice_contract = swap.chain_a.contracts["alice-lock"]
    bob_contract = swap.chain_b.contracts["bob-lock"]
    assert alice_contract.state is HTLCState.REDEEMED
    assert bob_contract.state is HTLCState.REDEEMED
    assert alice_contract.revealed_preimage == secret
    assert bob_contract.revealed_preimage == secret



def test_alice_can_refund_if_bob_never_participates() -> None:
    secret = b"atomic swap secret"
    swap = AtomicSwap(
        chain_a=SimulatedChain(name="ChainA"),
        chain_b=SimulatedChain(name="ChainB"),
        alice="Alice",
        bob="Bob",
        alice_amount=100,
        bob_amount=250,
        hash_value=sha256(secret).digest(),
        alice_contract_id="alice-lock",
        bob_contract_id="bob-lock",
        alice_deadline=100,
        bob_deadline=50,
    )
    swap.initiate()
    swap.chain_a.advance_time(100)
    swap.chain_a.refund_htlc(
        contract_id="alice-lock",
        caller="Alice",
    )
    alice_contract = swap.chain_a.contracts["alice-lock"]
    assert alice_contract.state is HTLCState.REFUNDED
    assert alice_contract.revealed_preimage is None
    assert "bob-lock" not in swap.chain_b.contracts




def test_both_parties_can_refund_if_alice_never_redeems() -> None:
    secret = b"atomic swap secret"

    swap = AtomicSwap(
        chain_a=SimulatedChain(name="Chain A"),
        chain_b=SimulatedChain(name="Chain B"),
        alice="Alice",
        bob="Bob",
        alice_amount=100,
        bob_amount=250,
        hash_value=sha256(secret).digest(),
        alice_contract_id="alice-lock",
        bob_contract_id="bob-lock",
        alice_deadline=100,
        bob_deadline=50,
    )

    swap.initiate()
    swap.participate()

    swap.chain_b.advance_time(50)
    swap.chain_b.refund_htlc(
        contract_id="bob-lock",
        caller="Bob",
    )

    swap.chain_a.advance_time(100)
    swap.chain_a.refund_htlc(
        contract_id="alice-lock",
        caller="Alice",
    )

    alice_contract = swap.chain_a.contracts["alice-lock"]
    bob_contract = swap.chain_b.contracts["bob-lock"]

    assert alice_contract.state is HTLCState.REFUNDED
    assert bob_contract.state is HTLCState.REFUNDED
    assert alice_contract.revealed_preimage is None
    assert bob_contract.revealed_preimage is None


def test_bob_cannot_redeem_befor_secret_is_revealed() -> None:
    secret = b"atomic swap secret"
    swap = AtomicSwap(
        chain_a=SimulatedChain(name="ChainA"),
        chain_b=SimulatedChain(name="ChainB"),
        alice="Alice",
        bob="Bob",
        alice_amount=100,
        bob_amount=250,
        hash_value=sha256(secret).digest(),
        alice_contract_id="alice-lock",
        bob_contract_id="bob-lock",
        alice_deadline=100,
        bob_deadline=50,
    )
    swap.initiate()
    swap.participate()
    with pytest.raises(SecretNotRevealed):
        swap.bob_redeem()
    alice_contract = swap.chain_a.contracts["alice-lock"]
    bob_contract = swap.chain_b.contracts["bob-lock"]

    assert alice_contract.state is HTLCState.LOCKED
    assert bob_contract.state is HTLCState.LOCKED
    assert bob_contract.revealed_preimage is None



def test_alice_cannot_redeem_with_wrong_secret() -> None:
    secret = b"atomic swap secret"

    swap = AtomicSwap(
        chain_a=SimulatedChain(name="Chain A"),
        chain_b=SimulatedChain(name="Chain B"),
        alice="Alice",
        bob="Bob",
        alice_amount=100,
        bob_amount=250,
        hash_value=sha256(secret).digest(),
        alice_contract_id="alice-lock",
        bob_contract_id="bob-lock",
        alice_deadline=100,
        bob_deadline=50,
    )

    swap.initiate()
    swap.participate()

    swap.chain_b.advance_time(20)

    with pytest.raises(InvalidPreimage):
        swap.alice_redeem(b"wrong secret")

    alice_contract = swap.chain_a.contracts["alice-lock"]
    bob_contract = swap.chain_b.contracts["bob-lock"]

    assert alice_contract.state is HTLCState.LOCKED
    assert bob_contract.state is HTLCState.LOCKED
    assert bob_contract.revealed_preimage is None




def test_alice_cannot_redeem_after_bob_deadline() -> None:
    secret = b"atomic swap secret"

    swap = AtomicSwap(
        chain_a=SimulatedChain(name="Chain A"),
        chain_b=SimulatedChain(name="Chain B"),
        alice="Alice",
        bob="Bob",
        alice_amount=100,
        bob_amount=250,
        hash_value=sha256(secret).digest(),
        alice_contract_id="alice-lock",
        bob_contract_id="bob-lock",
        alice_deadline=100,
        bob_deadline=50,
    )

    swap.initiate()
    swap.participate()

    swap.chain_b.advance_time(50)

    with pytest.raises(DeadlineExpired):
        swap.alice_redeem(secret)

    alice_contract = swap.chain_a.contracts["alice-lock"]
    bob_contract = swap.chain_b.contracts["bob-lock"]

    assert alice_contract.state is HTLCState.LOCKED
    assert bob_contract.state is HTLCState.LOCKED
    assert bob_contract.revealed_preimage is None
