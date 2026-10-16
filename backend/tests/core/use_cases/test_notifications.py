import pytest

from stock.core.entities.customer_order import CustomerOrder
from stock.core.errors import NotFound
from stock.core.roles import Role
from stock.core.use_cases.notifications import (
    list_notifications,
    mark_notification_read,
    notify_out_of_stock,
)
from stock.core.use_cases.products import create_product


@pytest.fixture
def sent(repos):
    product = create_product(repos.products, "PEN", "Pen", min_quantity=3, quantity=2)
    order = CustomerOrder(product_id=product.id, quantity=10, customer_name="ACME", id=7)
    return notify_out_of_stock(repos.notifications, product, order)


def test_both_roles_are_notified(sent):
    assert {n.recipient for n in sent} == set(Role)
    assert "order #7" in sent[0].message
    assert "PEN" in sent[0].message


def test_each_role_only_sees_its_own(repos, sent):
    [mine] = list_notifications(repos.notifications, Role.STOCK_MANAGER)
    assert mine.recipient == Role.STOCK_MANAGER


def test_mark_read_only_affects_one_role(repos, sent):
    [mine] = list_notifications(repos.notifications, Role.STOCK_MANAGER)
    mark_notification_read(repos.notifications, mine.id, Role.STOCK_MANAGER)

    assert list_notifications(repos.notifications, Role.STOCK_MANAGER)[0].read
    assert not list_notifications(repos.notifications, Role.PURCHASING_MANAGER)[0].read


def test_cannot_mark_someone_elses_notification(repos, sent):
    [theirs] = list_notifications(repos.notifications, Role.PURCHASING_MANAGER)
    with pytest.raises(NotFound):
        mark_notification_read(repos.notifications, theirs.id, Role.STOCK_MANAGER)


def test_unknown_notification(repos):
    with pytest.raises(NotFound):
        mark_notification_read(repos.notifications, 99, Role.STOCK_MANAGER)
