from fastapi import APIRouter, status

from stock.api.deps import ReposDep, StockManager
from stock.api.schemas import CustomerOrderIn, CustomerOrderOut
from stock.core.use_cases import exit as uc

router = APIRouter(prefix="/customer-orders", tags=["exit"])


@router.get("", response_model=list[CustomerOrderOut])
def list_orders(repos: ReposDep):
    return repos.customer_orders.list()


@router.post(
    "",
    response_model=CustomerOrderOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[StockManager],
)
def place_order(body: CustomerOrderIn, repos: ReposDep):
    return uc.place_customer_order(
        repos.products,
        repos.customer_orders,
        repos.purchase_requests,
        repos.notifications,
        **body.model_dump(),
    )


@router.post("/{order_id}/prepare", response_model=CustomerOrderOut, dependencies=[StockManager])
def prepare_order(order_id: int, repos: ReposDep):
    return uc.prepare_order(repos.customer_orders, order_id)


@router.post("/{order_id}/ship", response_model=CustomerOrderOut, dependencies=[StockManager])
def ship_order(order_id: int, repos: ReposDep):
    return uc.ship_order(repos.products, repos.customer_orders, repos.purchase_requests, order_id)
