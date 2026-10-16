from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class Out(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str


class UserOut(BaseModel):
    username: str
    role: str


class ProductIn(BaseModel):
    sku: str = Field(min_length=1)
    name: str = Field(min_length=1)
    min_quantity: int = Field(ge=0)
    quantity: int = Field(default=0, ge=0)


class ProductOut(Out):
    id: int
    sku: str
    name: str
    quantity: int
    reserved: int
    available: int
    min_quantity: int


class CustomerOrderIn(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)
    customer_name: str = Field(min_length=1)


class CustomerOrderOut(Out):
    id: int
    product_id: int
    quantity: int
    customer_name: str
    status: str
    created_at: datetime


class PurchaseRequestIn(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class PurchaseRequestOut(Out):
    id: int
    product_id: int
    quantity: int
    created_by_system: bool
    status: str
    created_at: datetime


class SupplierOrderIn(BaseModel):
    purchase_request_id: int
    supplier_name: str = Field(min_length=1)


class RejectDeliveryIn(BaseModel):
    report: str = Field(min_length=1)


class SupplierOrderOut(Out):
    id: int
    purchase_request_id: int
    product_id: int
    quantity: int
    supplier_name: str
    status: str
    non_conformity_report: str | None
    accounting_validation_pending: bool
    created_at: datetime
    shipped_at: datetime | None
    received_at: datetime | None


class NotificationOut(Out):
    id: int
    message: str
    product_id: int | None
    read: bool
    created_at: datetime
