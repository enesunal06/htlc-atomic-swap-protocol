from hashlib import sha256
import pytest
from atomic_swap.errors import InvalidPreimage, UnauthorizedCaller, DeadlineExpired, RefundNotAvailable, ContractAlreadySpent
from atomic_swap.htlc import HTLC, HTLCState

def test_recipient_can_redeem_with_correct_preimage() -> None:
    secret = b"atomic swap secret"
    hash_value = sha256(secret).digest()
    htlc = HTLC(
        owner="Alice",
        recipient="Bob",
        amount=100,
        hash_value=hash_value,
        deadline=50,
    )
    htlc.redeem(
        caller="Bob",
        preimage=secret,
        current_time=20,
    )
    assert htlc.state is HTLCState.REDEEMED
    assert htlc.revealed_preimage == secret

def test_wrong_preimage_is_rejected() -> None:
    secret = b"atomic swap secret"
    hash_value = sha256(secret).digest()

    htlc = HTLC(
        owner="Alice",
        recipient="Bob",
        amount=100,
        hash_value=hash_value,
        deadline=50,
    )
    with pytest.raises(InvalidPreimage):
        htlc.redeem(
            caller="Bob",
            preimage=b"wrong secret",
            current_time=20,

        )
    assert htlc.state is HTLCState.LOCKED
    assert htlc.revealed_preimage is None


def test_non_recipient_cannot_redeem() -> None:
    secret = b"atomic swap secret"
    hash_value = sha256(secret).digest()
    htlc = HTLC(
        owner="Alice",
        recipient="Bob",
        amount=100,
        hash_value=hash_value,
        deadline=50,
    )
    with pytest.raises(UnauthorizedCaller):
        htlc.redeem(
            caller="Alice",
            preimage=secret,
            current_time=20,
        )
    assert htlc.state is HTLCState.LOCKED
    assert htlc.revealed_preimage is None


def test_redeem_at_deadline_is_rejected() -> None:
    secret = b"atomic swap secret"
    hash_value = sha256(secret).digest()
    htlc = HTLC(
        owner="Alice",
        recipient="Bob",
        amount=100,
        hash_value=hash_value,
        deadline=50,
    )
    with pytest.raises(DeadlineExpired):
        htlc.redeem(
            caller="Bob",
            preimage=secret,
            current_time=50,
        )
    assert htlc.state is HTLCState.LOCKED
    assert htlc.revealed_preimage is None



def test_redeem_before_deadline_succeeds() -> None:
    secret = b"atomic swap secret"
    hash_value = sha256(secret).digest()
    htlc = HTLC(
        owner="Alice",
        recipient="Bob",
        amount=100,
        hash_value=hash_value,
        deadline=50,
    )
    htlc.redeem(
        caller="Bob",
        preimage=secret,
        current_time=49,
    )
    assert htlc.state is HTLCState.REDEEMED
    assert htlc.revealed_preimage == secret



def test_owner_can_refund_at_deadline() -> None:
        secret = b"atomic swap secret"
        hash_value = sha256(secret).digest()
        htlc = HTLC(
            owner="Alice",
            recipient="Bob",
            amount=100,
            hash_value=hash_value,
            deadline=50,
        )
        htlc.refund(
        caller="Alice",
        current_time=50,
       )
        assert htlc.state is HTLCState.REFUNDED
        assert htlc.revealed_preimage is None

def test_refund_before_deadline_is_rejected() -> None:
    secret = b"atomic swap secret"
    hash_value = sha256(secret).digest()
    htlc = HTLC(
        owner="Alice",
        recipient="Bob",
        amount=100,
        hash_value=hash_value,
        deadline=50,
    )
    with pytest.raises(RefundNotAvailable):
        htlc.refund(
            caller="Alice",
            current_time=49,
        )
    assert htlc.state is HTLCState.LOCKED
    assert htlc.revealed_preimage is None


def test_non_owner_cannot_refund() -> None:
    secret = b"atomic swap secret"
    hash_value = sha256(secret).digest()

    htlc = HTLC(
        owner="Alice",
        recipient="Bob",
        amount=100,
        hash_value=hash_value,
        deadline=50,
    )

    with pytest.raises(UnauthorizedCaller):
        htlc.refund(
            caller="Bob",
            current_time=50,
        )

    assert htlc.state is HTLCState.LOCKED
    assert htlc.revealed_preimage is None



def test_redeemed_htlc_cannot_be_refunded() -> None:
    secret = b"atomic swap secret"
    hash_value = sha256(secret).digest()

    htlc = HTLC(
        owner="Alice",
        recipient="Bob",
        amount=100,
        hash_value=hash_value,
        deadline=50,
    )

    htlc.redeem(
        caller="Bob",
        preimage=secret,
        current_time=20,
    )

    with pytest.raises(ContractAlreadySpent):
        htlc.refund(
            caller="Alice",
            current_time=50,
        )

    assert htlc.state is HTLCState.REDEEMED
    assert htlc.revealed_preimage == secret


def test_refunded_htlc_cannot_be_redeemed() -> None:
    secret = b"atomic swap secret"
    hash_value = sha256(secret).digest()

    htlc = HTLC(
        owner="Alice",
        recipient="Bob",
        amount=100,
        hash_value=hash_value,
        deadline=50,
    )

    htlc.refund(
        caller="Alice",
        current_time=50,
    )

    with pytest.raises(ContractAlreadySpent):
        htlc.redeem(
            caller="Bob",
            preimage=secret,
            current_time=50,
        )

    assert htlc.state is HTLCState.REFUNDED
    assert htlc.revealed_preimage is None
