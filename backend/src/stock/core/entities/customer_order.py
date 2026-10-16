from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum

from stock.core.entities.product import ensure_positive
from stock.core.errors import InvalidTransition


class CustomerOrderStatus(StrEnum):
    RECEIVED = "RECEIVED"
    RESERVED = "RESERVED"
    PREPARED = "PREPARED"
    SHIPPED = "SHIPPED"
    REJECTED = "REJECTED"  # automatically, when the stock is insufficient


@dataclass
class CustomerOrder:
    product_id: int
    quantity: int
    customer_name: str
    status: CustomerOrderStatus = CustomerOrderStatus.RECEIVED
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    id: int | None = None

    def __post_init__(self) -> None:
        ensure_positive(self.quantity)

    def _move(self, expected: CustomerOrderStatus, new: CustomerOrderStatus) -> None:
        if self.status != expected:
            raise InvalidTransition(f"Cannot go from {self.status} to {new}")
        self.status = new

    def mark_reserved(self) -> None:
        self._move(CustomerOrderStatus.RECEIVED, CustomerOrderStatus.RESERVED)

    def mark_rejected(self) -> None:
        self._move(CustomerOrderStatus.RECEIVED, CustomerOrderStatus.REJECTED)

    def mark_prepared(self) -> None:
        self._move(CustomerOrderStatus.RESERVED, CustomerOrderStatus.PREPARED)

    def mark_shipped(self) -> None:
        self._move(CustomerOrderStatus.PREPARED, CustomerOrderStatus.SHIPPED)
