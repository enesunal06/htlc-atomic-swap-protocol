from dataclasses import dataclass, field
from atomic_swap.htlc import HTLC
@dataclass
class SimulatedChain:
    name: str
    current_time: int = 0
    contracts: dict[str, HTLC] = field(default_factory=dict)

    def deploy_htlc(
        self,
        contract_id: str,
        htlc: HTLC,
    ) -> None:
        if contract_id in self.contracts:
            raise ValueError(
                f"Contract ID '{contract_id}' already exists on {self.name}."
            )

        self.contracts[contract_id] = htlc
    def advance_time(self, amount: int) -> None:
        if amount < 0:
            raise ValueError("Time cannot monve backwards.")
        self.current_time += amount

    def redeem_htlc(
            self,
            contract_id: str,
            caller: str,
            preimage: bytes,
    ) -> None:
        contract = self.contracts[contract_id]
        contract.redeem(
            caller=caller,
            preimage=preimage,
            current_time=self.current_time
        )

    def refund_htlc(
            self,
            contract_id: str,
            caller: str,
    ) -> None:
        contract = self.contracts[contract_id]
        contract.refund(
            caller=caller,
            current_time=self.current_time
        )

