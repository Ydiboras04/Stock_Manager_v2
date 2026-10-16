import pytest

from stock.core.entities.product import Product
from stock.core.errors import InsufficientStock, InvalidQuantity


def make(quantity=10, reserved=0, min_quantity=3):
    return Product(
        sku="SKU-1", name="Widget", quantity=quantity, reserved=reserved, min_quantity=min_quantity
    )


def test_available_is_quantity_minus_reserved():
    assert make(quantity=10, reserved=4).available == 6


def test_cannot_create_with_negative_values():
    with pytest.raises(InvalidQuantity):
        make(quantity=-1)


def test_cannot_reserve_more_than_quantity_at_creation():
    with pytest.raises(InvalidQuantity):
        make(quantity=2, reserved=3)


def test_add_increases_quantity():
    product = make(quantity=10)
    product.add(5)
    assert product.quantity == 15


@pytest.mark.parametrize("qty", [0, -2])
def test_add_rejects_non_positive_quantity(qty):
    with pytest.raises(InvalidQuantity):
        make().add(qty)


def test_reserve_reduces_available():
    product = make(quantity=10)
    product.reserve(7)
    assert product.reserved == 7
    assert product.available == 3


def test_reserve_more_than_available_fails():
    product = make(quantity=10, reserved=8)
    with pytest.raises(InsufficientStock):
        product.reserve(3)


def test_ship_removes_reserved_units():
    product = make(quantity=10, reserved=6)
    product.ship(6)
    assert product.quantity == 4
    assert product.reserved == 0


def test_ship_more_than_reserved_fails():
    product = make(quantity=10, reserved=2)
    with pytest.raises(InsufficientStock):
        product.ship(3)


@pytest.mark.parametrize(
    ("quantity", "reserved", "expected"),
    [(10, 0, False), (4, 0, False), (3, 0, True), (10, 8, True), (0, 0, True)],
)
def test_needs_replenishment_when_available_reaches_min(quantity, reserved, expected):
    assert make(quantity=quantity, reserved=reserved).needs_replenishment() is expected
