from hashlib import sha256
import pytest
from atomic_swap.errors import InvalidPreimage, UnauthorizedCaller, DeadlineExpired
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
