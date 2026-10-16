import pytest

from stock.core.entities.purchase_request import PurchaseRequest, PurchaseRequestStatus
from stock.core.errors import InvalidQuantity, InvalidTransition


def make():
    return PurchaseRequest(product_id=1, quantity=5)


def test_new_request_is_pending_and_open():
    request = make()
    assert request.status == PurchaseRequestStatus.PENDING
    assert request.is_open
    assert request.created_at.tzinfo is not None


def test_quantity_must_be_positive():
    with pytest.raises(InvalidQuantity):
        PurchaseRequest(product_id=1, quantity=0)


def test_validate_then_order():
    request = make()
    request.validate()
    assert request.is_open
    request.mark_ordered()
    assert request.status == PurchaseRequestStatus.ORDERED
    assert not request.is_open


def test_reject_closes_request():
    request = make()
    request.reject()
    assert request.status == PurchaseRequestStatus.REJECTED
    assert not request.is_open


def test_cannot_order_a_pending_request():
    with pytest.raises(InvalidTransition):
        make().mark_ordered()


def test_cannot_reject_a_validated_request():
    request = make()
    request.validate()
    with pytest.raises(InvalidTransition):
        request.reject()


def test_pending_request_can_be_increased():
    request = make()
    request.increase(3)
    assert request.quantity == 8


def test_increase_requires_positive_quantity():
    with pytest.raises(InvalidQuantity):
        make().increase(0)


def test_validated_request_cannot_be_increased():
    request = make()
    request.validate()
    with pytest.raises(InvalidTransition):
        request.increase(3)
