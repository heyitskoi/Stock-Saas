from datetime import datetime, timedelta
import secrets
import pyotp

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import User, PasswordResetToken, Tenant
from auth import get_password_hash
from schemas import (
    PasswordResetRequest,
    PasswordResetConfirm,
    RegisterRequest,
    RegisterResponse,
    UserResponse,
)

router = APIRouter(prefix="/auth")


@router.post("/register", response_model=RegisterResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == payload.email).first():
        raise HTTPException(status_code=400, detail="Username already registered")

    if payload.tenant_id is not None:
        tenant = db.query(Tenant).filter(Tenant.id == payload.tenant_id).first()
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")
    else:
        tenant = Tenant(name=payload.email)
        db.add(tenant)
        db.commit()
        db.refresh(tenant)

    role = "admin" if payload.is_admin else "user"
    secret = pyotp.random_base32()
    user = User(
        username=payload.email,
        hashed_password=get_password_hash(payload.password),
        role=role,
        tenant_id=tenant.id,
        totp_secret=secret,
        notification_preference="email",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return RegisterResponse(user=user, totp_secret=secret)


@router.post("/request-reset")
def request_password_reset(
    payload: PasswordResetRequest, db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    token = secrets.token_urlsafe(32)
    expires = datetime.utcnow() + timedelta(hours=1)
    db.add(PasswordResetToken(user_id=user.id, token=token, expires_at=expires))
    db.commit()
    return {"reset_token": token}


@router.post("/reset-password")
def reset_password(payload: PasswordResetConfirm, db: Session = Depends(get_db)):
    entry = (
        db.query(PasswordResetToken)
        .filter(PasswordResetToken.token == payload.token)
        .first()
    )
    if not entry or entry.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    user = db.query(User).filter(User.id == entry.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.hashed_password = get_password_hash(payload.new_password)
    db.delete(entry)
    db.commit()
    return {"detail": "Password updated"}
