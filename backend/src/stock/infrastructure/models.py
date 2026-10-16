"""Database tables. Kept separate from the core entities on purpose."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class ProductRow(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    sku: Mapped[str] = mapped_column(String(64), unique=True)
    name: Mapped[str] = mapped_column(String(200))
    quantity: Mapped[int]
    reserved: Mapped[int]
    min_quantity: Mapped[int]


class CustomerOrderRow(Base):
    __tablename__ = "customer_orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int]
    customer_name: Mapped[str] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class PurchaseRequestRow(Base):
    __tablename__ = "purchase_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int]
    created_by_system: Mapped[bool]
    status: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class SupplierOrderRow(Base):
    __tablename__ = "supplier_orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    purchase_request_id: Mapped[int] = mapped_column(ForeignKey("purchase_requests.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int]
    supplier_name: Mapped[str] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(20))
    non_conformity_report: Mapped[str | None]
    accounting_validation_pending: Mapped[bool]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    shipped_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    received_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class NotificationRow(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    recipient: Mapped[str] = mapped_column(String(30), index=True)
    message: Mapped[str]
    product_id: Mapped[int | None] = mapped_column(ForeignKey("products.id"))
    read: Mapped[bool]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class UserRow(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True)
    password_hash: Mapped[str] = mapped_column(String(200))
    role: Mapped[str] = mapped_column(String(30))
