from stock.core.entities.notification import Notification
from stock.core.roles import Role


def test_new_notification_is_unread_and_dated():
    notification = Notification(recipient=Role.STOCK_MANAGER, message="Out of stock")
    assert notification.read is False
    assert notification.created_at.tzinfo is not None


def test_mark_read():
    notification = Notification(recipient=Role.STOCK_MANAGER, message="Out of stock")
    notification.mark_read()
    assert notification.read is True
