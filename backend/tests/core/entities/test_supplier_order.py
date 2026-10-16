import pytest

from stock.core.entities.supplier_order import SupplierOrder, SupplierOrderStatus
from stock.core.errors import DomainError, InvalidQuantity, InvalidTransition


def make(status=SupplierOrderStatus.ORDERED):
    return SupplierOrder(
        purchase_request_id=1, product_id=1, quantity=5, supplier_name="Supplier", status=status
    )


def test_new_order_is_ordered_and_dated():
    order = make()
    assert order.status == SupplierOrderStatus.ORDERED
    assert order.accounting_validation_pending is False
    assert order.created_at.tzinfo is not None
    assert order.shipped_at is None and order.received_at is None


def test_quantity_must_be_positive():
    with pytest.raises(InvalidQuantity):
        SupplierOrder(purchase_request_id=1, product_id=1, quantity=0, supplier_name="S")


def test_manual_status_updates():
    order = make()
    order.mark_shipped()
    assert order.status == SupplierOrderStatus.SHIPPED
    assert order.shipped_at >= order.created_at
    assert order.received_at is None
    order.mark_received()
    assert order.status == SupplierOrderStatus.RECEIVED
    assert order.received_at >= order.shipped_at


def test_cannot_receive_before_shipped():
    order = make()
    with pytest.raises(InvalidTransition):
        order.mark_received()
    assert order.received_at is None


def test_accept_triggers_accounting_validation():
    order = make(SupplierOrderStatus.RECEIVED)
    order.accept()
    assert order.status == SupplierOrderStatus.ACCEPTED
    assert order.accounting_validation_pending is True


def test_reject_stores_report():
    order = make(SupplierOrderStatus.RECEIVED)
    order.reject("Damaged boxes")
    assert order.status == SupplierOrderStatus.REJECTED
    assert order.non_conformity_report == "Damaged boxes"


def test_reject_requires_report():
    with pytest.raises(DomainError):
        make(SupplierOrderStatus.RECEIVED).reject("  ")


@pytest.mark.parametrize("status", [SupplierOrderStatus.ORDERED, SupplierOrderStatus.SHIPPED])
def test_cannot_check_conformity_before_reception(status):
    with pytest.raises(InvalidTransition):
        make(status).accept()
