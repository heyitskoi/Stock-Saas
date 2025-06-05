from datetime import datetime
from pydantic import BaseModel


class ItemBase(BaseModel):
    name: str
    available: int
    in_use: int
    threshold: int


class ItemCreate(BaseModel):
    name: str
    quantity: int
    threshold: int = 0
    tenant_id: int


class ItemUpdate(BaseModel):
    name: str
    tenant_id: int
    new_name: str | None = None
    threshold: int | None = None


class ItemDelete(BaseModel):
    name: str
    tenant_id: int


class ItemResponse(ItemBase):
    id: int
    tenant_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    username: str
    notification_preference: str = "email"


class UserCreate(UserBase):
    password: str
    role: str = "user"
    tenant_id: int


class UserResponse(UserBase):
    id: int
    role: str
    tenant_id: int

    class Config:
        orm_mode = True


class UserUpdate(BaseModel):
    id: int
    username: str | None = None
    password: str | None = None
    role: str | None = None
    notification_preference: str | None = None


class UserDelete(BaseModel):
    id: int


class AuditLogResponse(BaseModel):
    id: int
    user_id: int
    item_id: int
    action: str
    quantity: int
    timestamp: datetime

    class Config:
        orm_mode = True


class TenantBase(BaseModel):
    name: str


class TenantCreate(TenantBase):
    pass


class TenantResponse(TenantBase):
    id: int

    class Config:
        orm_mode = True
