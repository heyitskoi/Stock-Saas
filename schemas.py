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


class ItemUpdate(BaseModel):
    name: str
    new_name: str | None = None
    threshold: int | None = None


class ItemDelete(BaseModel):
    name: str


class ItemResponse(ItemBase):
    id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str
    role: str = "user"


class UserResponse(UserBase):
    id: int
    role: str

    class Config:
        orm_mode = True


class AuditLogResponse(BaseModel):
    id: int
    user_id: int
    item_id: int
    action: str
    quantity: int
    timestamp: datetime

    class Config:
        orm_mode = True
