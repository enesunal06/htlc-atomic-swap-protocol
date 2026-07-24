from dataclasses import dataclass
from atomic_swap.chain import SimulatedChain
from atomic_swap.errors import UnsafeTimeoutOrder

@dataclass
class AtomicSwap:
    chain_a: SimulatedChain
    chain_b: SimulatedChain
    alice: str
    bob: str
    hash_value: bytes
    alice_contract_id: str
    bob_contract_id: str
    alice_deadline: int
    bob_deadline: int

    def __post_init__(self) -> None:
        if self.alice_deadline <= self.bob_deadline:
            raise UnsafeTimeoutOrder(
                "Alice's deadline must be greater than Bob's deadline"
            )

