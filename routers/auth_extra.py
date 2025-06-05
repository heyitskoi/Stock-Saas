from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from database import get_db
from auth import get_password_hash, create_password_reset, verify_password_reset
from models import User
from schemas import PasswordResetRequest, PasswordResetConfirm
from notifications import _send_email

router = APIRouter(prefix="/auth")


@router.post("/request-reset")
def request_password_reset(
    payload: PasswordResetRequest, db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    token = create_password_reset(db, user)
    _send_email(f"Password reset token: {token}")
    return {"detail": "reset emailed", "token": token}


@router.post("/reset-password")
def reset_password(payload: PasswordResetConfirm, db: Session = Depends(get_db)):
    user = verify_password_reset(db, payload.token)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid token")
    user.hashed_password = get_password_hash(payload.new_password)
    db.commit()
    return {"detail": "password updated"}
