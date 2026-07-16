from dataclasses import dataclass
from enum import Enum
from hashlib import sha256


class HTLCState(str, Enum):
    LOCKED = "Locked"
    REDEEEMED = "Redeemed"
    REFUNDED = "Refunded"


@dataclass
class HTLC:
    owner: str
    recipient: str
    amount: int
    hash_value: bytes
    deadline: int
    state: HTLCState = HTLCState.LOCKED
    revealed_preimage: bytes | None = None

    def redeem(
        self,
        caller: str,
        preimage: bytes,
        current_time: int,
    ) -> None:
        if self.state is not HTLCState.LOCKED:
            raise ValueError("HTLC is no longer locked.")
        if caller != self.recipient:
            raise PermissionError("Only the recipient can redeem this HTLC.")
        if current_time >= self.deadline:
            raise ValueError("The HTLC deadline has passed.")
        if sha256(preimage).digest() != self.hash_value:
            raise ValueError("The supplied preimage is invalid.")

        self.state = HTLCState.REDEEEMED
        self.revealed_preimage = preimage
    def refund(
            self,
            caller: str,
            current_time: int,

    ) -> None:
         if self.state is not HTLCState.LOCKED:
             raise ValueError("HTLC is no longer locked.")
         if caller != self.owner:
             raise PermissionError("Only the owner can refund this HTLC.")
         if current_time < self.deadline:
             raise ValueError("Refund is not available before the deadline.")

         self.state = HTLCState.REFUNDED
         
