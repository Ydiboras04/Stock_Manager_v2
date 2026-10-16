"""BPMN 'Processus de Reapprovisionnement' + manual tracking of the external supplier."""

from stock.core.entities.product import Product
from stock.core.entities.purchase_request import PurchaseRequest
from stock.core.entities.supplier_order import SupplierOrder
from stock.core.errors import NotFound
from stock.core.ports import (
    ProductRepository,
    PurchaseRequestRepository,
    SupplierOrderRepository,
)
from stock.core.use_cases.products import get_product


def check_replenishment(
    product: Product, requests: PurchaseRequestRepository, shortfall: int = 0
) -> PurchaseRequest | None:
    """Qmin reached or missing quantity -> the system asks to buy more.

    - Qmin reached: order back up to twice the threshold, unless a request is already open.
    - Missing quantity (rejected customer order): always ordered, added to the pending
      request of the product if there is one, otherwise in a new request.
    """
    quantity = shortfall
    if product.needs_replenishment() and not requests.has_open_for_product(product.id):
        quantity += max(2 * product.min_quantity - product.available, 1)
    if quantity == 0:
        return None

    pending = requests.get_pending_for_product(product.id)
    if pending is not None:
        pending.increase(quantity)
        requests.save(pending)
        return pending
    return requests.add(
        PurchaseRequest(product_id=product.id, quantity=quantity, created_by_system=True)
    )


def create_purchase_request(
    products: ProductRepository, requests: PurchaseRequestRepository, product_id: int, quantity: int
) -> PurchaseRequest:
    get_product(products, product_id)
    return requests.add(PurchaseRequest(product_id=product_id, quantity=quantity))


def get_purchase_request(requests: PurchaseRequestRepository, request_id: int) -> PurchaseRequest:
    request = requests.get(request_id)
    if request is None:
        raise NotFound(f"Purchase request {request_id} not found")
    return request


def validate_purchase_request(
    requests: PurchaseRequestRepository, request_id: int
) -> PurchaseRequest:
    request = get_purchase_request(requests, request_id)
    request.validate()
    requests.save(request)
    return request


def reject_purchase_request(
    requests: PurchaseRequestRepository, request_id: int
) -> PurchaseRequest:
    request = get_purchase_request(requests, request_id)
    request.reject()
    requests.save(request)
    return request


def issue_supplier_order(
    requests: PurchaseRequestRepository,
    supplier_orders: SupplierOrderRepository,
    request_id: int,
    supplier_name: str,
) -> SupplierOrder:
    request = get_purchase_request(requests, request_id)
    request.mark_ordered()
    requests.save(request)
    return supplier_orders.add(
        SupplierOrder(
            purchase_request_id=request.id,
            product_id=request.product_id,
            quantity=request.quantity,
            supplier_name=supplier_name,
        )
    )


def get_supplier_order(supplier_orders: SupplierOrderRepository, order_id: int) -> SupplierOrder:
    order = supplier_orders.get(order_id)
    if order is None:
        raise NotFound(f"Supplier order {order_id} not found")
    return order


def mark_supplier_order_shipped(
    supplier_orders: SupplierOrderRepository, order_id: int
) -> SupplierOrder:
    order = get_supplier_order(supplier_orders, order_id)
    order.mark_shipped()
    supplier_orders.save(order)
    return order


def mark_supplier_order_received(
    supplier_orders: SupplierOrderRepository, order_id: int
) -> SupplierOrder:
    order = get_supplier_order(supplier_orders, order_id)
    order.mark_received()
    supplier_orders.save(order)
    return order
