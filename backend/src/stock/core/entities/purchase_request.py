from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum

from stock.core.entities.product import ensure_positive
from stock.core.errors import InvalidTransition


class PurchaseRequestStatus(StrEnum):
    PENDING = "PENDING"
    VALIDATED = "VALIDATED"
    REJECTED = "REJECTED"
    ORDERED = "ORDERED"


@dataclass
class PurchaseRequest:
    product_id: int
    quantity: int
    created_by_system: bool = False
    status: PurchaseRequestStatus = PurchaseRequestStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    id: int | None = None

    def __post_init__(self) -> None:
        ensure_positive(self.quantity)

    @property
    def is_open(self) -> bool:
        return self.status in (PurchaseRequestStatus.PENDING, PurchaseRequestStatus.VALIDATED)

    def increase(self, quantity: int) -> None:
        """Only a request that has not been validated yet can still change."""
        ensure_positive(quantity)
        if self.status != PurchaseRequestStatus.PENDING:
            raise InvalidTransition(f"Cannot change a {self.status} request")
        self.quantity += quantity

    def _move(self, expected: PurchaseRequestStatus, new: PurchaseRequestStatus) -> None:
        if self.status != expected:
            raise InvalidTransition(f"Cannot go from {self.status} to {new}")
        self.status = new

    def validate(self) -> None:
        self._move(PurchaseRequestStatus.PENDING, PurchaseRequestStatus.VALIDATED)

    def reject(self) -> None:
        self._move(PurchaseRequestStatus.PENDING, PurchaseRequestStatus.REJECTED)

    def mark_ordered(self) -> None:
        self._move(PurchaseRequestStatus.VALIDATED, PurchaseRequestStatus.ORDERED)
