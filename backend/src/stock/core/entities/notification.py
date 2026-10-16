from dataclasses import dataclass, field
from datetime import UTC, datetime

from stock.core.roles import Role


@dataclass
class Notification:
    recipient: Role
    message: str
    product_id: int | None = None
    read: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    id: int | None = None

    def mark_read(self) -> None:
        self.read = True
