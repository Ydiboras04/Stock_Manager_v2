from collections.abc import Iterator
from dataclasses import dataclass
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from stock.core.roles import Role
from stock.infrastructure.db import SessionLocal
from stock.infrastructure.repositories import (
    SqlCustomerOrderRepository,
    SqlNotificationRepository,
    SqlProductRepository,
    SqlPurchaseRequestRepository,
    SqlSupplierOrderRepository,
)
from stock.infrastructure.security import decode_token


def get_session() -> Iterator[Session]:
    """One transaction per request: commit on success, rollback on any error."""
    with SessionLocal() as session, session.begin():
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


@dataclass
class Repos:
    products: SqlProductRepository
    customer_orders: SqlCustomerOrderRepository
    purchase_requests: SqlPurchaseRequestRepository
    supplier_orders: SqlSupplierOrderRepository
    notifications: SqlNotificationRepository


def get_repos(session: SessionDep) -> Repos:
    return Repos(
        SqlProductRepository(session),
        SqlCustomerOrderRepository(session),
        SqlPurchaseRequestRepository(session),
        SqlSupplierOrderRepository(session),
        SqlNotificationRepository(session),
    )


ReposDep = Annotated[Repos, Depends(get_repos)]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


@dataclass
class CurrentUser:
    username: str
    role: Role


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> CurrentUser:
    try:
        payload = decode_token(token)
        return CurrentUser(username=payload["sub"], role=Role(payload["role"]))
    except (jwt.InvalidTokenError, KeyError, ValueError) as error:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token") from error


CurrentUserDep = Annotated[CurrentUser, Depends(get_current_user)]


def require_role(role: Role):
    def check(user: CurrentUserDep) -> CurrentUser:
        if user.role != role:
            raise HTTPException(status.HTTP_403_FORBIDDEN, f"Requires role {role}")
        return user

    return Depends(check)


StockManager = require_role(Role.STOCK_MANAGER)
PurchasingManager = require_role(Role.PURCHASING_MANAGER)
