from hashlib import sha256
from hmac import digest
from atomic_swap.htlc import HTLC
from atomic_swap.chain import SimulatedChain
import pytest

def test_chain_starts_with_empty_state() -> None:
    chain = SimulatedChain(name="ChainA")
    assert chain.name == "ChainA"
    assert chain.current_time == 0
    assert chain.contracts == {}


def test_chains_have_independent_contract_storage() -> None:
    chain_a = SimulatedChain(name="ChainA")
    chain_b = SimulatedChain(name="ChainB")
    htlc = HTLC(
        owner="Alice",
        recipient="Bob",
        amount=100,
        hash_value=sha256(b"atomic swap secret").digest(),
        deadline=50,
    )
    chain_a.deploy_htlc(
        contract_id="example",
        htlc=htlc,
    )
    assert "example" in chain_a.contracts
    assert "example" not in chain_b.contracts
    assert chain_a.contracts is not chain_b.contracts

def test_deploy_htlc_stores_contract() -> None:
    chain = SimulatedChain(name="ChainA")

    contract = HTLC(
        owner="Alice",
        recipient="Bob",
        amount=100,
        hash_value=sha256(b"atomic swap secret").digest(),
        deadline=50,
    )

    chain.deploy_htlc(
        contract_id="alice-lock",
        htlc=contract,
    )

    assert chain.contracts["alice-lock"] is contract

def test_duplicate_contract_id_is_rejected() -> None:
    chain = SimulatedChain(name="ChainA")
    first_contract = HTLC(
        owner="Alice",
        recipient="Bob",
        amount=100,
        hash_value=sha256(b"first secret").digest(),
        deadline=50,
    )
    second_contract = HTLC(
        owner="Carol",
        recipient="Dave",
        amount=200,
        hash_value=sha256(b"second secret").digest(),
        deadline=60
    )
    chain.deploy_htlc(
        contract_id="swap-1",
        htlc=first_contract,
    )
    with pytest.raises(ValueError):
      chain.deploy_htlc(
        contract_id="swap-1",
        htlc=second_contract,
        )
    assert chain.contracts["swap-1"] is first_contract

def test_advance_time_increases_chain_time() -> None:
    chain = SimulatedChain(name="ChainA")
    chain.advance_time(10)
    assert chain.current_time == 10
    chain.advance_time(5)
    assert chain.current_time == 15


def test_time_cannot_move_backwards() -> None:
    chain = SimulatedChain(name="ChainA")
    chain.advance_time(10)
    with pytest.raises(ValueError):
        chain.advance_time(-1)
    assert chain.current_time == 10
    

