from datetime import datetime
from pydantic import BaseModel, conint

try:
    from pydantic import ConfigDict
except Exception:
    ConfigDict = None  # type: ignore


class ItemBase(BaseModel):
    name: str
    available: int
    in_use: int
    threshold: int
    min_par: int
    department_id: int | None = None
    category_id: int | None = None
    stock_code: str | None = None
    status: str | None = None


class ItemCreate(BaseModel):
    name: str
    quantity: conint(gt=0)
    threshold: conint(ge=0) = 0
    tenant_id: int
    min_par: conint(ge=0) = 0
    department_id: int | None = None
    category_id: int | None = None
    stock_code: str | None = None
    status: str | None = None


class ItemUpdate(BaseModel):
    name: str
    tenant_id: int
    new_name: str | None = None
    threshold: conint(ge=0) | None = None
    min_par: conint(ge=0) | None = None
    department_id: int | None = None
    category_id: int | None = None
    stock_code: str | None = None
    status: str | None = None


class ItemDelete(BaseModel):
    name: str
    tenant_id: int


class ItemResponse(ItemBase):
    id: int
    tenant_id: int

    if ConfigDict:
        model_config = ConfigDict(from_attributes=True)


class TransferRequest(BaseModel):
    name: str
    quantity: conint(gt=0)
    from_tenant_id: int
    to_tenant_id: int


class TransferResponse(BaseModel):
    from_item: ItemResponse
    to_item: ItemResponse


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

    if ConfigDict:
        model_config = ConfigDict(from_attributes=True)


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

    if ConfigDict:
        model_config = ConfigDict(from_attributes=True)


class TenantBase(BaseModel):
    name: str


class TenantCreate(TenantBase):
    pass


class TenantResponse(TenantBase):
    id: int

    if ConfigDict:
        model_config = ConfigDict(from_attributes=True)


class DepartmentBase(BaseModel):
    name: str
    icon: str | None = None


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentResponse(DepartmentBase):
    id: int

    if ConfigDict:
        model_config = ConfigDict(from_attributes=True)


class CategoryBase(BaseModel):
    name: str
    department_id: int
    icon: str | None = None


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: int

    if ConfigDict:
        model_config = ConfigDict(from_attributes=True)


class CategoryUpdate(BaseModel):


    """Schema for updating a category."""

    name: str | None = None
    department_id: int | None = None
    icon: str | None = None


class PasswordResetRequest(BaseModel):
    username: str


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str


class RegisterRequest(BaseModel):
    email: str
    password: str
    tenant_id: int | None = None
    is_admin: bool = False


class RegisterResponse(BaseModel):
    user: UserResponse
