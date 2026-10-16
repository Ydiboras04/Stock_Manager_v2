from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum

from stock.core.entities.product import ensure_positive
from stock.core.errors import DomainError, InvalidTransition


class SupplierOrderStatus(StrEnum):
    ORDERED = "ORDERED"
    SHIPPED = "SHIPPED"
    RECEIVED = "RECEIVED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


@dataclass
class SupplierOrder:
    purchase_request_id: int
    product_id: int
    quantity: int
    supplier_name: str
    status: SupplierOrderStatus = SupplierOrderStatus.ORDERED
    non_conformity_report: str | None = None
    accounting_validation_pending: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    shipped_at: datetime | None = None
    received_at: datetime | None = None
    id: int | None = None

    def __post_init__(self) -> None:
        ensure_positive(self.quantity)

    def _move(self, expected: SupplierOrderStatus, new: SupplierOrderStatus) -> None:
        if self.status != expected:
            raise InvalidTransition(f"Cannot go from {self.status} to {new}")
        self.status = new

    # Updated manually: the supplier is external.
    def mark_shipped(self) -> None:
        self._move(SupplierOrderStatus.ORDERED, SupplierOrderStatus.SHIPPED)
        self.shipped_at = datetime.now(UTC)

    def mark_received(self) -> None:
        self._move(SupplierOrderStatus.SHIPPED, SupplierOrderStatus.RECEIVED)
        self.received_at = datetime.now(UTC)

    # Conformity check of the delivery.
    def accept(self) -> None:
        self._move(SupplierOrderStatus.RECEIVED, SupplierOrderStatus.ACCEPTED)
        self.accounting_validation_pending = True

    def reject(self, report: str) -> None:
        if not report.strip():
            raise DomainError("A non-conformity report is required")
        self._move(SupplierOrderStatus.RECEIVED, SupplierOrderStatus.REJECTED)
        self.non_conformity_report = report
