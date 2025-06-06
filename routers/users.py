from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import User
from schemas import UserCreate, UserResponse, UserUpdate, UserDelete
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
        notification_preference=payload.notification_preference,
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


@router.put("/users/update", response_model=UserResponse)
def update_user(
    payload: UserUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(admin_only),
):
    user_obj = (
        db.query(User)
        .filter(User.id == payload.id, User.tenant_id == user.tenant_id)
        .first()
    )
    if not user_obj:
        raise HTTPException(status_code=404, detail="User not found")
    if payload.username:
        if (
            db.query(User)
            .filter(User.username == payload.username, User.id != payload.id)
            .first()
        ):
            raise HTTPException(status_code=400, detail="Username already registered")
        user_obj.username = payload.username
    if payload.password:
        user_obj.hashed_password = get_password_hash(payload.password)
    if payload.role:
        user_obj.role = payload.role
    if payload.notification_preference:
        user_obj.notification_preference = payload.notification_preference
    db.commit()
    db.refresh(user_obj)
    return user_obj


@router.delete("/users/delete")
def delete_user(
    payload: UserDelete,
    db: Session = Depends(get_db),
    user: User = Depends(admin_only),
):
    user_obj = (
        db.query(User)
        .filter(User.id == payload.id, User.tenant_id == user.tenant_id)
        .first()
    )
    if not user_obj:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user_obj)
    db.commit()
    return {"detail": "User deleted"}
