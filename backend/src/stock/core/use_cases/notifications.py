"""BPMN 'Rupture notifiee': tell the responsible people about a stock shortage."""

from stock.core.entities.customer_order import CustomerOrder
from stock.core.entities.notification import Notification
from stock.core.entities.product import Product
from stock.core.errors import NotFound
from stock.core.ports import NotificationRepository
from stock.core.roles import Role


def notify_out_of_stock(
    notifications: NotificationRepository, product: Product, order: CustomerOrder
) -> list[Notification]:
    message = (
        f"Out of stock: order #{order.id} from {order.customer_name} for {order.quantity} "
        f"x {product.sku} ({product.name}) was rejected, only {product.available} available. "
        f"The missing quantity was added to a purchase request."
    )
    return [
        notifications.add(Notification(recipient=role, message=message, product_id=product.id))
        for role in Role
    ]


def list_notifications(
    notifications: NotificationRepository, recipient: Role
) -> list[Notification]:
    return notifications.list_for(recipient)


def mark_notification_read(
    notifications: NotificationRepository, notification_id: int, recipient: Role
) -> Notification:
    notification = notifications.get(notification_id)
    # Someone else's notification is treated as missing.
    if notification is None or notification.recipient != recipient:
        raise NotFound(f"Notification {notification_id} not found")
    notification.mark_read()
    notifications.save(notification)
    return notification
