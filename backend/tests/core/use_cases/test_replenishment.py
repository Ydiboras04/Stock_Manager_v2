import pytest

from stock.core.entities.purchase_request import PurchaseRequestStatus
from stock.core.entities.supplier_order import SupplierOrderStatus
from stock.core.errors import InvalidTransition, NotFound
from stock.core.use_cases import replenishment as uc
from stock.core.use_cases.products import create_product


@pytest.fixture
def product(repos):
    return create_product(repos.products, "SKU-1", "Widget", min_quantity=3, quantity=2)


def test_check_creates_request_when_below_threshold(repos, product):
    request = uc.check_replenishment(product, repos.purchase_requests)
    assert request.status == PurchaseRequestStatus.PENDING
    assert request.quantity == 4  # back to 2 * Qmin
    assert request.created_by_system


def test_check_does_nothing_above_threshold(repos):
    product = create_product(repos.products, "SKU-2", "Bolt", min_quantity=3, quantity=10)
    assert uc.check_replenishment(product, repos.purchase_requests) is None


def test_check_adds_shortfall(repos):
    product = create_product(repos.products, "SKU-2", "Bolt", min_quantity=3, quantity=10)
    request = uc.check_replenishment(product, repos.purchase_requests, shortfall=40)
    assert request.quantity == 40


def test_check_does_not_duplicate_open_request(repos, product):
    uc.check_replenishment(product, repos.purchase_requests)
    assert uc.check_replenishment(product, repos.purchase_requests) is None
    assert len(repos.purchase_requests.list()) == 1


def test_shortfall_increases_pending_request(repos, product):
    first = uc.check_replenishment(product, repos.purchase_requests)
    again = uc.check_replenishment(product, repos.purchase_requests, shortfall=10)
    assert again.id == first.id
    assert repos.purchase_requests.get(first.id).quantity == 4 + 10


def test_shortfall_creates_new_request_when_open_one_is_validated(repos, product):
    first = uc.check_replenishment(product, repos.purchase_requests)
    uc.validate_purchase_request(repos.purchase_requests, first.id)

    second = uc.check_replenishment(product, repos.purchase_requests, shortfall=10)

    assert second.id != first.id
    assert second.quantity == 10  # Qmin already covered by the validated request
    assert repos.purchase_requests.get(first.id).quantity == 4


def test_manual_request_requires_existing_product(repos):
    with pytest.raises(NotFound):
        uc.create_purchase_request(repos.products, repos.purchase_requests, 99, 5)


def test_validate_and_reject(repos, product):
    first = uc.create_purchase_request(repos.products, repos.purchase_requests, product.id, 5)
    second = uc.create_purchase_request(repos.products, repos.purchase_requests, product.id, 5)
    assert not first.created_by_system

    uc.validate_purchase_request(repos.purchase_requests, first.id)
    uc.reject_purchase_request(repos.purchase_requests, second.id)

    assert repos.purchase_requests.get(first.id).status == PurchaseRequestStatus.VALIDATED
    assert repos.purchase_requests.get(second.id).status == PurchaseRequestStatus.REJECTED


def test_issue_supplier_order_from_validated_request(repos, product):
    request = uc.create_purchase_request(repos.products, repos.purchase_requests, product.id, 5)
    uc.validate_purchase_request(repos.purchase_requests, request.id)

    order = uc.issue_supplier_order(
        repos.purchase_requests, repos.supplier_orders, request.id, "Supplier"
    )

    assert order.status == SupplierOrderStatus.ORDERED
    assert (order.product_id, order.quantity) == (product.id, 5)
    assert repos.purchase_requests.get(request.id).status == PurchaseRequestStatus.ORDERED


def test_cannot_issue_order_from_pending_request(repos, product):
    request = uc.create_purchase_request(repos.products, repos.purchase_requests, product.id, 5)
    with pytest.raises(InvalidTransition):
        uc.issue_supplier_order(repos.purchase_requests, repos.supplier_orders, request.id, "S")
    assert repos.supplier_orders.list() == []


def test_manual_supplier_status_updates(repos, product):
    request = uc.create_purchase_request(repos.products, repos.purchase_requests, product.id, 5)
    uc.validate_purchase_request(repos.purchase_requests, request.id)
    order = uc.issue_supplier_order(repos.purchase_requests, repos.supplier_orders, request.id, "S")

    uc.mark_supplier_order_shipped(repos.supplier_orders, order.id)
    received = uc.mark_supplier_order_received(repos.supplier_orders, order.id)

    assert received.status == SupplierOrderStatus.RECEIVED
    assert repos.supplier_orders.get(order.id).status == SupplierOrderStatus.RECEIVED


def test_unknown_ids_raise(repos):
    with pytest.raises(NotFound):
        uc.validate_purchase_request(repos.purchase_requests, 99)
    with pytest.raises(NotFound):
        uc.mark_supplier_order_shipped(repos.supplier_orders, 99)
