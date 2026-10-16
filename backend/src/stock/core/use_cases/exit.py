"""BPMN 'Processus de Sortie'."""

from stock.core.entities.customer_order import CustomerOrder
from stock.core.errors import NotFound
from stock.core.ports import (
    CustomerOrderRepository,
    NotificationRepository,
    ProductRepository,
    PurchaseRequestRepository,
)
from stock.core.use_cases.notifications import notify_out_of_stock
from stock.core.use_cases.products import get_product
from stock.core.use_cases.replenishment import check_replenishment


def place_customer_order(
    products: ProductRepository,
    orders: CustomerOrderRepository,
    requests: PurchaseRequestRepository,
    notifications: NotificationRepository,
    product_id: int,
    quantity: int,
    customer_name: str,
) -> CustomerOrder:
    """Receive the order and check availability.

    Enough stock: reserve it. Otherwise the order is rejected automatically, the
    responsible people are notified and the missing quantity goes to a purchase request.
    """
    product = get_product(products, product_id)
    order = CustomerOrder(product_id=product_id, quantity=quantity, customer_name=customer_name)

    shortfall = max(quantity - product.available, 0)
    if shortfall == 0:
        product.reserve(quantity)
        order.mark_reserved()
        products.save(product)
    else:
        order.mark_rejected()

    orders.add(order)
    if shortfall:
        notify_out_of_stock(notifications, product, order)
    check_replenishment(product, requests, shortfall)
    return order


def get_customer_order(orders: CustomerOrderRepository, order_id: int) -> CustomerOrder:
    order = orders.get(order_id)
    if order is None:
        raise NotFound(f"Customer order {order_id} not found")
    return order


def prepare_order(orders: CustomerOrderRepository, order_id: int) -> CustomerOrder:
    order = get_customer_order(orders, order_id)
    order.mark_prepared()
    orders.save(order)
    return order


def ship_order(
    products: ProductRepository,
    orders: CustomerOrderRepository,
    requests: PurchaseRequestRepository,
    order_id: int,
) -> CustomerOrder:
    """Update the stock level, mark the order shipped, then check the Qmin threshold."""
    order = get_customer_order(orders, order_id)
    order.mark_shipped()
    product = get_product(products, order.product_id)
    product.ship(order.quantity)
    products.save(product)
    orders.save(order)
    check_replenishment(product, requests)
    return order
