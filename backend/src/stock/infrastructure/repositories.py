"""PostgreSQL implementations of the core ports (stock.core.ports)."""

from dataclasses import asdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from stock.core.entities.customer_order import CustomerOrder, CustomerOrderStatus
from stock.core.entities.notification import Notification
from stock.core.entities.product import Product
from stock.core.entities.purchase_request import PurchaseRequest, PurchaseRequestStatus
from stock.core.entities.supplier_order import SupplierOrder, SupplierOrderStatus
from stock.core.roles import Role
from stock.infrastructure.models import (
    CustomerOrderRow,
    NotificationRow,
    ProductRow,
    PurchaseRequestRow,
    SupplierOrderRow,
)


class SqlRepository:
    """Maps a core dataclass to a table row with the same column names."""

    row_class: type
    entity_class: type
    enums: dict[str, type] = {}  # column name -> enum to rebuild

    def __init__(self, session: Session) -> None:
        self.session = session

    def _to_entity(self, row):
        if row is None:
            return None
        data = {c.name: getattr(row, c.name) for c in row.__table__.columns}
        for column, enum in self.enums.items():
            data[column] = enum(data[column])
        return self.entity_class(**data)

    def get(self, entity_id: int):
        # Lock the row until the end of the transaction to avoid concurrent updates.
        row = self.session.get(self.row_class, entity_id, with_for_update=True)
        return self._to_entity(row)

    def list(self):
        rows = self.session.scalars(select(self.row_class).order_by(self.row_class.id))
        return [self._to_entity(row) for row in rows]

    def add(self, entity):
        data = asdict(entity)
        data.pop("id")
        row = self.row_class(**data)
        self.session.add(row)
        self.session.flush()
        entity.id = row.id
        return entity

    def save(self, entity) -> None:
        self.session.merge(self.row_class(**asdict(entity)))
        self.session.flush()


class SqlProductRepository(SqlRepository):
    row_class = ProductRow
    entity_class = Product

    def get_by_sku(self, sku: str) -> Product | None:
        row = self.session.scalars(select(ProductRow).where(ProductRow.sku == sku)).first()
        return self._to_entity(row)


class SqlCustomerOrderRepository(SqlRepository):
    row_class = CustomerOrderRow
    entity_class = CustomerOrder
    enums = {"status": CustomerOrderStatus}


class SqlPurchaseRequestRepository(SqlRepository):
    row_class = PurchaseRequestRow
    entity_class = PurchaseRequest
    enums = {"status": PurchaseRequestStatus}

    def has_open_for_product(self, product_id: int) -> bool:
        open_statuses = [PurchaseRequestStatus.PENDING, PurchaseRequestStatus.VALIDATED]
        query = select(PurchaseRequestRow.id).where(
            PurchaseRequestRow.product_id == product_id,
            PurchaseRequestRow.status.in_(open_statuses),
        )
        return self.session.scalars(query).first() is not None

    def get_pending_for_product(self, product_id: int) -> PurchaseRequest | None:
        query = select(PurchaseRequestRow).where(
            PurchaseRequestRow.product_id == product_id,
            PurchaseRequestRow.status == PurchaseRequestStatus.PENDING,
        )
        return self._to_entity(self.session.scalars(query.with_for_update()).first())


class SqlSupplierOrderRepository(SqlRepository):
    row_class = SupplierOrderRow
    entity_class = SupplierOrder
    enums = {"status": SupplierOrderStatus}


class SqlNotificationRepository(SqlRepository):
    row_class = NotificationRow
    entity_class = Notification
    enums = {"recipient": Role}

    def list_for(self, recipient: Role) -> list[Notification]:
        query = (
            select(NotificationRow)
            .where(NotificationRow.recipient == recipient)
            .order_by(NotificationRow.id.desc())
        )
        return [self._to_entity(row) for row in self.session.scalars(query)]
