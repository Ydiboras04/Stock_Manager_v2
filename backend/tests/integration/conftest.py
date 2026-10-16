"""API tests against a real PostgreSQL database (TEST_DATABASE_URL)."""

import os
from pathlib import Path

import pytest

os.environ["DATABASE_URL"] = os.getenv(
    "TEST_DATABASE_URL", "postgresql+psycopg://stock:stock@localhost:5432/stock_test"
)

from alembic import command  # noqa: E402
from alembic.config import Config  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import text  # noqa: E402

from stock.api.main import app  # noqa: E402
from stock.core.roles import Role  # noqa: E402
from stock.infrastructure.db import engine  # noqa: E402
from stock.seed import upsert_user  # noqa: E402

BACKEND_DIR = Path(__file__).parents[2]


@pytest.fixture(scope="session", autouse=True)
def migrated_database():
    config = Config(BACKEND_DIR / "alembic.ini")
    config.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    command.upgrade(config, "head")


@pytest.fixture(autouse=True)
def clean_tables():
    with engine.begin() as connection:
        connection.execute(
            text(
                "TRUNCATE notifications, supplier_orders, purchase_requests, customer_orders, "
                "products, users RESTART IDENTITY CASCADE"
            )
        )
    upsert_user("stock", "stock-pass", Role.STOCK_MANAGER)
    upsert_user("buyer", "buyer-pass", Role.PURCHASING_MANAGER)


def login(client: TestClient, username: str, password: str) -> TestClient:
    response = client.post("/auth/login", data={"username": username, "password": password})
    assert response.status_code == 200, response.text
    client.headers["Authorization"] = f"Bearer {response.json()['access_token']}"
    return client


@pytest.fixture
def stock_manager():
    return login(TestClient(app), "stock", "stock-pass")


@pytest.fixture
def buyer():
    return login(TestClient(app), "buyer", "buyer-pass")
