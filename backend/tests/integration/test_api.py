from fastapi.testclient import TestClient

from stock.api.main import app


def create_product(client, quantity=10, min_quantity=3):
    body = {"sku": "SKU-1", "name": "Widget", "quantity": quantity, "min_quantity": min_quantity}
    response = client.post("/products", json=body)
    assert response.status_code == 201, response.text
    return response.json()


def test_requires_authentication():
    assert TestClient(app).get("/products").status_code == 401


def test_wrong_password_is_rejected():
    response = TestClient(app).post("/auth/login", data={"username": "stock", "password": "x"})
    assert response.status_code == 401


def test_roles_are_enforced(buyer):
    body = {"sku": "SKU-1", "name": "Widget", "min_quantity": 3}
    assert buyer.post("/products", json=body).status_code == 403


def test_duplicate_sku_returns_409(stock_manager):
    create_product(stock_manager)
    body = {"sku": "SKU-1", "name": "Other", "min_quantity": 0}
    assert stock_manager.post("/products", json=body).status_code == 409


def test_exit_process_triggers_replenishment(stock_manager, buyer):
    product = create_product(stock_manager)

    order = stock_manager.post(
        "/customer-orders", json={"product_id": product["id"], "quantity": 8, "customer_name": "A"}
    ).json()
    assert order["status"] == "RESERVED"
    stock_manager.post(f"/customer-orders/{order['id']}/prepare").raise_for_status()
    shipped = stock_manager.post(f"/customer-orders/{order['id']}/ship").json()
    assert shipped["status"] == "SHIPPED"

    stored = stock_manager.get(f"/products/{product['id']}").json()
    assert (stored["quantity"], stored["available"]) == (2, 2)
    [request] = buyer.get("/purchase-requests").json()
    assert request["created_by_system"] and request["status"] == "PENDING"


def test_out_of_stock_order_is_rejected_and_notified(stock_manager, buyer):
    product = create_product(stock_manager)
    order = stock_manager.post(
        "/customer-orders", json={"product_id": product["id"], "quantity": 50, "customer_name": "A"}
    ).json()
    assert order["status"] == "REJECTED"
    assert order["created_at"]

    [request] = buyer.get("/purchase-requests").json()
    assert request["quantity"] == 40 and request["created_at"]

    [mine] = stock_manager.get("/notifications").json()
    [theirs] = buyer.get("/notifications").json()
    assert f"order #{order['id']}" in mine["message"]
    assert mine["id"] != theirs["id"]

    assert buyer.post(f"/notifications/{mine['id']}/read").status_code == 404
    assert stock_manager.post(f"/notifications/{mine['id']}/read").json()["read"] is True
    assert buyer.get("/notifications").json()[0]["read"] is False


def test_invalid_transition_returns_409_and_rolls_back(stock_manager):
    product = create_product(stock_manager)
    order = stock_manager.post(
        "/customer-orders", json={"product_id": product["id"], "quantity": 2, "customer_name": "A"}
    ).json()
    assert stock_manager.post(f"/customer-orders/{order['id']}/ship").status_code == 409
    assert stock_manager.get(f"/products/{product['id']}").json()["quantity"] == 10


def test_replenishment_and_entry_process(stock_manager, buyer):
    product = create_product(stock_manager, quantity=0)
    request = buyer.post(
        "/purchase-requests", json={"product_id": product["id"], "quantity": 5}
    ).json()
    buyer.post(f"/purchase-requests/{request['id']}/validate").raise_for_status()

    order = buyer.post(
        "/supplier-orders", json={"purchase_request_id": request["id"], "supplier_name": "S"}
    ).json()
    assert order["created_at"] and order["shipped_at"] is None
    shipped = buyer.post(f"/supplier-orders/{order['id']}/ship").json()
    assert shipped["shipped_at"] and shipped["received_at"] is None
    received = buyer.post(f"/supplier-orders/{order['id']}/receive").json()
    assert received["received_at"] >= received["shipped_at"]

    assert buyer.post(f"/supplier-orders/{order['id']}/accept").status_code == 403
    accepted = stock_manager.post(f"/supplier-orders/{order['id']}/accept").json()
    assert accepted["status"] == "ACCEPTED"
    assert accepted["accounting_validation_pending"] is True
    assert stock_manager.get(f"/products/{product['id']}").json()["quantity"] == 5


def test_rejected_delivery_keeps_stock(stock_manager, buyer):
    product = create_product(stock_manager, quantity=0)
    request = buyer.post(
        "/purchase-requests", json={"product_id": product["id"], "quantity": 5}
    ).json()
    buyer.post(f"/purchase-requests/{request['id']}/validate")
    order = buyer.post(
        "/supplier-orders", json={"purchase_request_id": request["id"], "supplier_name": "S"}
    ).json()
    buyer.post(f"/supplier-orders/{order['id']}/ship")
    buyer.post(f"/supplier-orders/{order['id']}/receive")

    rejected = stock_manager.post(
        f"/supplier-orders/{order['id']}/reject", json={"report": "Damaged"}
    ).json()
    assert rejected["status"] == "REJECTED"
    assert rejected["non_conformity_report"] == "Damaged"
    assert stock_manager.get(f"/products/{product['id']}").json()["quantity"] == 0
