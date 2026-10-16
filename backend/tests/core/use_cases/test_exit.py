import pytest

from stock.core.entities.customer_order import CustomerOrderStatus
from stock.core.errors import InvalidTransition, NotFound
from stock.core.roles import Role
from stock.core.use_cases.exit import place_customer_order, prepare_order, ship_order
from stock.core.use_cases.products import create_product


@pytest.fixture
def product(repos):
    return create_product(repos.products, "SKU-1", "Widget", min_quantity=3, quantity=10)


def place(repos, product_id, quantity):
    return place_customer_order(
        repos.products,
        repos.customer_orders,
        repos.purchase_requests,
        repos.notifications,
        product_id,
        quantity,
        "ACME",
    )


def test_enough_stock_reserves(repos, product):
    order = place(repos, product.id, 4)
    assert order.status == CustomerOrderStatus.RESERVED
    assert repos.products.get(product.id).reserved == 4
    assert repos.purchase_requests.list() == []


def test_not_enough_stock_rejects_and_orders_missing_quantity(repos, product):
    order = place(repos, product.id, 50)
    assert order.status == CustomerOrderStatus.REJECTED
    assert repos.customer_orders.get(order.id).status == CustomerOrderStatus.REJECTED
    assert repos.products.get(product.id).reserved == 0
    [request] = repos.purchase_requests.list()
    assert request.created_by_system
    assert request.quantity == 40  # the missing quantity


def test_not_enough_stock_notifies_both_roles(repos, product):
    order = place(repos, product.id, 50)
    for role in Role:
        [notification] = repos.notifications.list_for(role)
        assert f"order #{order.id}" in notification.message


def test_missing_quantity_is_added_to_pending_request(repos, product):
    place(repos, product.id, 8)  # available 2 <= Qmin 3 -> request of 4
    place(repos, product.id, 50)  # 48 missing
    [request] = repos.purchase_requests.list()
    assert request.quantity == 4 + 48


def test_reserved_order_sends_no_notification(repos, product):
    place(repos, product.id, 4)
    assert repos.notifications.list() == []


def test_unknown_product_raises(repos):
    with pytest.raises(NotFound):
        place(repos, 99, 1)


def test_prepare_then_ship_updates_stock(repos, product):
    order = place(repos, product.id, 4)
    prepare_order(repos.customer_orders, order.id)
    shipped = ship_order(repos.products, repos.customer_orders, repos.purchase_requests, order.id)

    assert shipped.status == CustomerOrderStatus.SHIPPED
    stored = repos.products.get(product.id)
    assert (stored.quantity, stored.reserved) == (6, 0)
    assert repos.purchase_requests.list() == []  # 6 > Qmin 3


def test_shipping_below_threshold_creates_purchase_request(repos, product):
    order = place(repos, product.id, 8)
    prepare_order(repos.customer_orders, order.id)
    ship_order(repos.products, repos.customer_orders, repos.purchase_requests, order.id)
    assert len(repos.purchase_requests.list()) == 1


def test_cannot_ship_unprepared_order(repos, product):
    order = place(repos, product.id, 4)
    with pytest.raises(InvalidTransition):
        ship_order(repos.products, repos.customer_orders, repos.purchase_requests, order.id)
    assert repos.products.get(product.id).quantity == 10


def test_prepare_unknown_order_raises(repos):
    with pytest.raises(NotFound):
        prepare_order(repos.customer_orders, 99)
