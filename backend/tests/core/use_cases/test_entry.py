import pytest

from stock.core.entities.supplier_order import SupplierOrder, SupplierOrderStatus
from stock.core.errors import InvalidTransition
from stock.core.use_cases.entry import accept_delivery, reject_delivery
from stock.core.use_cases.products import create_product


@pytest.fixture
def product(repos):
    return create_product(repos.products, "SKU-1", "Widget", min_quantity=3, quantity=2)


def add_order(repos, product, status=SupplierOrderStatus.RECEIVED):
    return repos.supplier_orders.add(
        SupplierOrder(
            purchase_request_id=1,
            product_id=product.id,
            quantity=5,
            supplier_name="Supplier",
            status=status,
        )
    )


def test_accept_updates_stock_and_triggers_accounting(repos, product):
    order = add_order(repos, product)
    accepted = accept_delivery(repos.products, repos.supplier_orders, order.id)

    assert accepted.status == SupplierOrderStatus.ACCEPTED
    assert accepted.accounting_validation_pending
    assert repos.products.get(product.id).quantity == 7
    assert repos.supplier_orders.get(order.id).status == SupplierOrderStatus.ACCEPTED


def test_reject_keeps_stock_and_stores_report(repos, product):
    order = add_order(repos, product)
    rejected = reject_delivery(repos.supplier_orders, order.id, "Wrong items")

    assert rejected.status == SupplierOrderStatus.REJECTED
    assert repos.supplier_orders.get(order.id).non_conformity_report == "Wrong items"
    assert repos.products.get(product.id).quantity == 2


def test_cannot_accept_before_reception(repos, product):
    order = add_order(repos, product, SupplierOrderStatus.SHIPPED)
    with pytest.raises(InvalidTransition):
        accept_delivery(repos.products, repos.supplier_orders, order.id)
    assert repos.products.get(product.id).quantity == 2
