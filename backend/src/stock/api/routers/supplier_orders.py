from fastapi import APIRouter, status

from stock.api.deps import PurchasingManager, ReposDep, StockManager
from stock.api.schemas import RejectDeliveryIn, SupplierOrderIn, SupplierOrderOut
from stock.core.use_cases import entry
from stock.core.use_cases import replenishment as uc

router = APIRouter(prefix="/supplier-orders", tags=["replenishment", "entry"])


@router.get("", response_model=list[SupplierOrderOut])
def list_orders(repos: ReposDep):
    return repos.supplier_orders.list()


@router.post(
    "",
    response_model=SupplierOrderOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[PurchasingManager],
)
def issue_order(body: SupplierOrderIn, repos: ReposDep):
    return uc.issue_supplier_order(
        repos.purchase_requests, repos.supplier_orders, body.purchase_request_id, body.supplier_name
    )


# Manual tracking of the external supplier.
@router.post("/{order_id}/ship", response_model=SupplierOrderOut, dependencies=[PurchasingManager])
def mark_shipped(order_id: int, repos: ReposDep):
    return uc.mark_supplier_order_shipped(repos.supplier_orders, order_id)


@router.post(
    "/{order_id}/receive", response_model=SupplierOrderOut, dependencies=[PurchasingManager]
)
def mark_received(order_id: int, repos: ReposDep):
    return uc.mark_supplier_order_received(repos.supplier_orders, order_id)


# Conformity check of the delivery (stock manager).
@router.post("/{order_id}/accept", response_model=SupplierOrderOut, dependencies=[StockManager])
def accept_delivery(order_id: int, repos: ReposDep):
    return entry.accept_delivery(repos.products, repos.supplier_orders, order_id)


@router.post("/{order_id}/reject", response_model=SupplierOrderOut, dependencies=[StockManager])
def reject_delivery(order_id: int, body: RejectDeliveryIn, repos: ReposDep):
    return entry.reject_delivery(repos.supplier_orders, order_id, body.report)
