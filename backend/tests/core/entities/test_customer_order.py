import pytest

from stock.core.entities.customer_order import CustomerOrder, CustomerOrderStatus
from stock.core.errors import InvalidQuantity, InvalidTransition


def make():
    return CustomerOrder(product_id=1, quantity=2, customer_name="ACME")


def test_new_order_is_received_and_dated():
    order = make()
    assert order.status == CustomerOrderStatus.RECEIVED
    assert order.created_at.tzinfo is not None


def test_quantity_must_be_positive():
    with pytest.raises(InvalidQuantity):
        CustomerOrder(product_id=1, quantity=0, customer_name="ACME")


def test_happy_path_received_to_shipped():
    order = make()
    order.mark_reserved()
    order.mark_prepared()
    order.mark_shipped()
    assert order.status == CustomerOrderStatus.SHIPPED


def test_received_can_be_rejected():
    order = make()
    order.mark_rejected()
    assert order.status == CustomerOrderStatus.REJECTED


def test_cannot_prepare_before_reservation():
    with pytest.raises(InvalidTransition):
        make().mark_prepared()


def test_cannot_ship_before_preparation():
    order = make()
    order.mark_reserved()
    with pytest.raises(InvalidTransition):
        order.mark_shipped()


def test_rejected_order_cannot_be_reserved():
    order = make()
    order.mark_rejected()
    with pytest.raises(InvalidTransition):
        order.mark_reserved()
