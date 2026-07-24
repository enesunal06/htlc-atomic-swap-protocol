class HTLCError(Exception):
    """Base exception for all HTLC-related errors."""
class InvalidPreimage(HTLCError):
    """Raised when the supplied preimage does not match the hashlock."""
class DeadlineExpired(HTLCError):
    """Raised when redeem is attempted after the deadline."""
class RefundNotAvailable(HTLCError):
    """Raised when refund is attempted before the deadline."""
class UnauthorizedCaller(HTLCError):
    """Raised when the caller is not authorized for the operation."""
class ContractAlreadySpent(HTLCError):
    """Raised when a redeemed or refunded HTLC is used again."""

class UnsafeTimeoutOrder(HTLCError):
    """Raised when atomic swap refund readlines are ordered unsafely."""
