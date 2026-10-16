"""BPMN 'Processus d'Entree': conformity check of a received supplier delivery."""

from stock.core.entities.supplier_order import SupplierOrder
from stock.core.ports import ProductRepository, SupplierOrderRepository
from stock.core.use_cases.products import get_product
from stock.core.use_cases.replenishment import get_supplier_order


def accept_delivery(
    products: ProductRepository, supplier_orders: SupplierOrderRepository, order_id: int
) -> SupplierOrder:
    """Conform: trigger accounting validation and update the stock."""
    order = get_supplier_order(supplier_orders, order_id)
    order.accept()
    product = get_product(products, order.product_id)
    product.add(order.quantity)
    products.save(product)
    supplier_orders.save(order)
    return order


def reject_delivery(
    supplier_orders: SupplierOrderRepository, order_id: int, report: str
) -> SupplierOrder:
    """Not conform: store the non-conformity report, stock is untouched."""
    order = get_supplier_order(supplier_orders, order_id)
    order.reject(report)
    supplier_orders.save(order)
    return order
