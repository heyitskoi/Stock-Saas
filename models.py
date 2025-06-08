from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship

from database import Base


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    users = relationship("User", back_populates="tenant")
    items = relationship("Item", back_populates="tenant")


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    icon = Column(String, nullable=True)

    items = relationship("Item", back_populates="department")
    categories = relationship("Category", back_populates="department")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"))
    icon = Column(String, nullable=True)

    department = relationship("Department", back_populates="categories")
    items = relationship("Item", back_populates="category")


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"))
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    available = Column(Integer, default=0)
    in_use = Column(Integer, default=0)
    threshold = Column(Integer, default=0)
    min_par = Column(Integer, default=0)
    stock_code = Column(String, nullable=True)
    status = Column(String, nullable=True)

    tenant = relationship("Tenant", back_populates="items")
    department = relationship("Department", back_populates="items")
    category = relationship("Category", back_populates="items")

    __table_args__ = (UniqueConstraint("name", "tenant_id", name="uix_name_tenant"),)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="user")
    tenant_id = Column(Integer, ForeignKey("tenants.id"))
    # "email", "slack" or "none"
    notification_preference = Column(String, default="email")

    tenant = relationship("Tenant", back_populates="users")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    item_id = Column(Integer, ForeignKey("items.id"))
    action = Column(String)
    quantity = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    item = relationship("Item")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"))
    message = Column(String)
    channel = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

    item = relationship("Item")


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    token = Column(String, unique=True, index=True)
    expires_at = Column(DateTime)

    user = relationship("User")
