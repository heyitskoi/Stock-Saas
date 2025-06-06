from datetime import datetime
from pydantic import BaseModel, conint


class ItemBase(BaseModel):
    name: str
    available: int
    in_use: int
    threshold: int


class ItemCreate(BaseModel):
    name: str
    quantity: conint(gt=0)
    threshold: conint(ge=0) = 0
    tenant_id: int


class ItemUpdate(BaseModel):
    name: str
    tenant_id: int
    new_name: str | None = None
    threshold: conint(ge=0) | None = None


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
    notification_preference: str = "email"  # "email", "slack" or "none"


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


class DepartmentBase(BaseModel):
    name: str
    icon: str | None = None


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentResponse(DepartmentBase):
    id: int

    class Config:
        orm_mode = True


class CategoryBase(BaseModel):
    name: str
    department_id: int
    icon: str | None = None


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: int

    class Config:
        orm_mode = True


class PasswordResetRequest(BaseModel):
    username: str


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str
