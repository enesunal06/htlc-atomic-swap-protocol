from dataclasses import dataclass
from atomic_swap.chain import SimulatedChain
from atomic_swap.errors import UnsafeTimeoutOrder, SecretNotRevealed
from atomic_swap.htlc import HTLC
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
    alice_amount: int
    bob_amount: int

    def __post_init__(self) -> None:
        if self.alice_deadline <= self.bob_deadline:
            raise UnsafeTimeoutOrder(
                "Alice's deadline must be greater than Bob's deadline"
            )

    def initiate(self) -> None:
        alice_contract = HTLC(
            owner=self.alice,
            recipient=self.bob,
            amount=self.alice_amount,
            hash_value=self.hash_value,
            deadline=self.alice_deadline,
        )
        self.chain_a.deploy_htlc(
            contract_id=self.alice_contract_id,
            htlc=alice_contract,
        )

    def participate(self) -> None:
        bob_contract = HTLC(
            owner=self.bob,
            recipient=self.alice,
            amount=self.bob_amount,
            hash_value=self.hash_value,
            deadline=self.bob_deadline,
        )
        self.chain_b.deploy_htlc(
            contract_id=self.bob_contract_id,
            htlc=bob_contract,
        )

    def alice_redeem(self, secret: bytes) -> None:
        self.chain_b.redeem_htlc(
            contract_id=self.bob_contract_id,
            caller=self.alice,
            preimage=secret,
        )

    def bob_redeem(self) -> None:
        bob_contract = self.chain_b.contracts[self.bob_contract_id]
        revealed_secret = bob_contract.revealed_preimage

        if revealed_secret is None:
          raise SecretNotRevealed(
            "The secret has not been revealed on Chain B."
        )

        self.chain_a.redeem_htlc(
          contract_id=self.alice_contract_id,
          caller=self.bob,
          preimage=revealed_secret,
    )
