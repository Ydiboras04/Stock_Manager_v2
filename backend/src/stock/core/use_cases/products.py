from stock.core.entities.product import Product
from stock.core.errors import AlreadyExists, NotFound
from stock.core.ports import ProductRepository


def create_product(
    products: ProductRepository, sku: str, name: str, min_quantity: int, quantity: int = 0
) -> Product:
    if products.get_by_sku(sku) is not None:
        raise AlreadyExists(f"Product '{sku}' already exists")
    return products.add(Product(sku=sku, name=name, min_quantity=min_quantity, quantity=quantity))


def get_product(products: ProductRepository, product_id: int) -> Product:
    product = products.get(product_id)
    if product is None:
        raise NotFound(f"Product {product_id} not found")
    return product


def list_products(products: ProductRepository) -> list[Product]:
    return products.list()
