import pytest

from stock.core.errors import AlreadyExists, NotFound
from stock.core.use_cases.products import create_product, get_product, list_products


def test_create_product_assigns_id(repos):
    product = create_product(repos.products, "SKU-1", "Widget", min_quantity=3, quantity=10)
    assert product.id is not None
    assert get_product(repos.products, product.id).name == "Widget"


def test_sku_must_be_unique(repos):
    create_product(repos.products, "SKU-1", "Widget", min_quantity=3)
    with pytest.raises(AlreadyExists):
        create_product(repos.products, "SKU-1", "Other", min_quantity=1)


def test_get_unknown_product_raises(repos):
    with pytest.raises(NotFound):
        get_product(repos.products, 99)


def test_list_products(repos):
    create_product(repos.products, "A", "A", min_quantity=0)
    create_product(repos.products, "B", "B", min_quantity=0)
    assert [p.sku for p in list_products(repos.products)] == ["A", "B"]
