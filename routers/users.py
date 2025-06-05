from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import User, Tenant
from schemas import UserCreate, UserResponse
from auth import require_role, get_password_hash

router = APIRouter()

admin_only = require_role(["admin"])


@router.post("/users/", response_model=UserResponse)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    user: User = Depends(admin_only),
):
    if (
        db.query(User)
        .filter(User.username == payload.username, User.tenant_id == payload.tenant_id)
        .first()
    ):
        raise HTTPException(status_code=400, detail="Username already registered")
    new_user = User(
        username=payload.username,
        hashed_password=get_password_hash(payload.password),
        role=payload.role,
        tenant_id=payload.tenant_id,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/users/", response_model=list[UserResponse])
def list_users(
    tenant_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(admin_only),
):
    return db.query(User).filter(User.tenant_id == tenant_id).all()
