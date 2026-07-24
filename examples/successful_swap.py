from hashlib import sha256
from atomic_swap.chain import SimulatedChain
from atomic_swap.htlc import HTLCState
from atomic_swap.swap import AtomicSwap

def main () -> None:
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

    alice_contract = swap.chain_a.contracts[swap.alice_contract_id]
    bob_contract = swap.chain_b.contracts[swap.bob_contract_id]

    print("Atomic swap completed")
    print(f"Chain A contract: {alice_contract.state.value}")
    print(f"Chain B contract: {bob_contract.state.value}")
    print("Same secret revealed on both chains:", alice_contract.revealed_preimage == bob_contract.revealed_preimage == secret,)
    assert alice_contract.state is HTLCState.REDEEMED
    assert bob_contract.state is HTLCState.REDEEMED

if __name__ == "__main__":
    main()

