import os

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from stock.api.deps import get_current_user
from stock.api.routers import (
    auth,
    customer_orders,
    notifications,
    products,
    purchase_requests,
    supplier_orders,
)
from stock.core.errors import AlreadyExists, DomainError, InvalidTransition, NotFound

app = FastAPI(title="Stock Management")

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)

ERROR_STATUS = {NotFound: 404, AlreadyExists: 409, InvalidTransition: 409}


@app.exception_handler(DomainError)
def domain_error_handler(request: Request, error: DomainError) -> JSONResponse:
    status = ERROR_STATUS.get(type(error), 400)
    return JSONResponse(status_code=status, content={"detail": str(error)})


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}


app.include_router(auth.router)
for module in (products, customer_orders, purchase_requests, supplier_orders, notifications):
    app.include_router(module.router, dependencies=[Depends(get_current_user)])
