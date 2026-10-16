from fastapi import APIRouter, status

from stock.api.deps import ReposDep, StockManager
from stock.api.schemas import ProductIn, ProductOut
from stock.core.use_cases import products as uc

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=list[ProductOut])
def list_products(repos: ReposDep):
    return uc.list_products(repos.products)


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, repos: ReposDep):
    return uc.get_product(repos.products, product_id)


@router.post(
    "", response_model=ProductOut, status_code=status.HTTP_201_CREATED, dependencies=[StockManager]
)
def create_product(body: ProductIn, repos: ReposDep):
    return uc.create_product(repos.products, **body.model_dump())
