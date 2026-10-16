"""Create or update a user.

Usage: python -m stock.seed <username> <password> <STOCK_MANAGER|PURCHASING_MANAGER>
"""

import sys

from sqlalchemy import select

from stock.core.roles import Role
from stock.infrastructure.db import SessionLocal
from stock.infrastructure.models import UserRow
from stock.infrastructure.security import hash_password


def upsert_user(username: str, password: str, role: Role) -> None:
    with SessionLocal() as session, session.begin():
        user = session.scalars(select(UserRow).where(UserRow.username == username)).first()
        if user is None:
            user = UserRow(username=username)
            session.add(user)
        user.password_hash = hash_password(password)
        user.role = role


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    username, password, role = sys.argv[1:]
    upsert_user(username, password, Role(role))
    print(f"User '{username}' saved with role {role}")
