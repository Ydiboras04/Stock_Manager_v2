from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from stock.api.deps import CurrentUserDep, SessionDep
from stock.api.schemas import Token, UserOut
from stock.infrastructure.models import UserRow
from stock.infrastructure.security import create_token, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep):
    user = session.scalars(select(UserRow).where(UserRow.username == form.username)).first()
    if user is None or not verify_password(form.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Wrong username or password")
    return Token(access_token=create_token(user.username, user.role), role=user.role)


@router.get("/me", response_model=UserOut)
def me(user: CurrentUserDep):
    return UserOut(username=user.username, role=user.role)
