"""In-memory implementations of the core ports, used by use-case tests."""

import copy
from dataclasses import dataclass

import pytest

from stock.core.entities.purchase_request import PurchaseRequest


class InMemoryRepository:
    def __init__(self) -> None:
        self.items: dict[int, object] = {}
        self._next_id = 1

    def get(self, entity_id: int):
        item = self.items.get(entity_id)
        return copy.deepcopy(item)

    def list(self):
        return [copy.deepcopy(item) for item in self.items.values()]

    def add(self, entity):
        entity.id = self._next_id
        self._next_id += 1
        self.items[entity.id] = copy.deepcopy(entity)
        return entity

    def save(self, entity) -> None:
        self.items[entity.id] = copy.deepcopy(entity)


class InMemoryProducts(InMemoryRepository):
    def get_by_sku(self, sku: str):
        return next((p for p in self.list() if p.sku == sku), None)


class InMemoryPurchaseRequests(InMemoryRepository):
    def has_open_for_product(self, product_id: int) -> bool:
        items: list[PurchaseRequest] = self.list()
        return any(r.product_id == product_id and r.is_open for r in items)

    def get_pending_for_product(self, product_id: int):
        items: list[PurchaseRequest] = self.list()
        return next(
            (r for r in items if r.product_id == product_id and r.status == "PENDING"), None
        )


class InMemoryNotifications(InMemoryRepository):
    def list_for(self, recipient):
        return [n for n in self.list() if n.recipient == recipient]


@dataclass
class Repos:
    products: InMemoryProducts
    customer_orders: InMemoryRepository
    purchase_requests: InMemoryPurchaseRequests
    supplier_orders: InMemoryRepository
    notifications: InMemoryNotifications


@pytest.fixture
def repos() -> Repos:
    return Repos(
        InMemoryProducts(),
        InMemoryRepository(),
        InMemoryPurchaseRequests(),
        InMemoryRepository(),
        InMemoryNotifications(),
    )
