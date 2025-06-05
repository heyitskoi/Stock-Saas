from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import User
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
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    new_user = User(
        username=payload.username,
        hashed_password=get_password_hash(payload.password),
        role=payload.role,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/users/", response_model=list[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    user: User = Depends(admin_only),
):
    return db.query(User).all()
