from fastapi import APIRouter, status

from stock.api.deps import PurchasingManager, ReposDep
from stock.api.schemas import PurchaseRequestIn, PurchaseRequestOut
from stock.core.use_cases import replenishment as uc

router = APIRouter(prefix="/purchase-requests", tags=["replenishment"])


@router.get("", response_model=list[PurchaseRequestOut])
def list_requests(repos: ReposDep):
    return repos.purchase_requests.list()


@router.post(
    "",
    response_model=PurchaseRequestOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[PurchasingManager],
)
def create_request(body: PurchaseRequestIn, repos: ReposDep):
    return uc.create_purchase_request(
        repos.products, repos.purchase_requests, body.product_id, body.quantity
    )


@router.post(
    "/{request_id}/validate", response_model=PurchaseRequestOut, dependencies=[PurchasingManager]
)
def validate_request(request_id: int, repos: ReposDep):
    return uc.validate_purchase_request(repos.purchase_requests, request_id)


@router.post(
    "/{request_id}/reject", response_model=PurchaseRequestOut, dependencies=[PurchasingManager]
)
def reject_request(request_id: int, repos: ReposDep):
    return uc.reject_purchase_request(repos.purchase_requests, request_id)
