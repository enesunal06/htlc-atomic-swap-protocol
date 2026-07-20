from hashlib import sha256
from atomic_swap.htlc import HTLC
from atomic_swap.chain import SimulatedChain


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


