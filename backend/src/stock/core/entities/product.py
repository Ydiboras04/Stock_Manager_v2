from dataclasses import dataclass

from stock.core.errors import InsufficientStock, InvalidQuantity


def ensure_positive(quantity: int) -> None:
    if quantity <= 0:
        raise InvalidQuantity(f"Quantity must be positive, got {quantity}")


@dataclass
class Product:
    sku: str
    name: str
    min_quantity: int = 0
    quantity: int = 0
    reserved: int = 0
    id: int | None = None

    def __post_init__(self) -> None:
        if self.min_quantity < 0 or self.quantity < 0 or self.reserved < 0:
            raise InvalidQuantity("Quantities cannot be negative")
        if self.reserved > self.quantity:
            raise InvalidQuantity("Reserved cannot exceed quantity")

    @property
    def available(self) -> int:
        return self.quantity - self.reserved

    def add(self, quantity: int) -> None:
        ensure_positive(quantity)
        self.quantity += quantity

    def reserve(self, quantity: int) -> None:
        ensure_positive(quantity)
        if quantity > self.available:
            raise InsufficientStock(
                f"Only {self.available} '{self.sku}' available, {quantity} requested"
            )
        self.reserved += quantity

    def ship(self, quantity: int) -> None:
        """Remove previously reserved units from the stock."""
        ensure_positive(quantity)
        if quantity > self.reserved:
            raise InsufficientStock(f"Only {self.reserved} '{self.sku}' reserved")
        self.reserved -= quantity
        self.quantity -= quantity

    def needs_replenishment(self) -> bool:
        return self.available < self.min_quantity
