import os

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database import Base, engine, get_db, SessionLocal, DATABASE_URL
from inventory_core import add_item, issue_item, return_item, get_status, get_recent_logs
from auth import login_for_access_token, require_role, get_password_hash
from models import User
from schemas import ItemCreate, ItemResponse, AuditLogResponse

app = FastAPI(title="Stock SaaS API")

Base.metadata.create_all(bind=engine)


@app.on_event("startup")
def create_default_admin():
    username = os.getenv("ADMIN_USERNAME")
    password = os.getenv("ADMIN_PASSWORD")
    if not (username and password) and DATABASE_URL.startswith("sqlite"):
        username = username or "admin"
        password = password or "admin"

    if not (username and password):
        return

    db = SessionLocal()
    if not db.query(User).filter(User.username == username).first():
        admin = User(
            username=username,
            hashed_password=get_password_hash(password),
            role="admin",
        )
        db.add(admin)
        db.commit()
    db.close()


admin_or_manager = require_role(["admin", "manager"])
any_user = require_role(["admin", "manager", "user"])


@app.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    return await login_for_access_token(form_data, db)



@app.post("/items/add")
=======
@app.post("/items/add", summary="Add items to inventory")

def api_add_item(
    name: str,
    quantity: int,
    threshold: int = 0,
    db: Session = Depends(get_db),
    user: User = Depends(admin_or_manager),
):



@app.post("/items/issue")
def api_issue_item(
    name: str,
    quantity: int,
    db: Session = Depends(get_db),
    user: User = Depends(admin_or_manager),
):
    try:
        item = issue_item(db, name, quantity, user_id=user.id)
        return {
            "message": f"Issued {quantity} {name}(s)",
            "item": {
                "available": item.available,
                "in_use": item.in_use,
                "threshold": item.threshold,
            },
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/items/return")
def api_return_item(
    name: str,
    quantity: int,
    db: Session = Depends(get_db),
    user: User = Depends(admin_or_manager),
):
    try:
        item = return_item(db, name, quantity, user_id=user.id)
        return {
            "message": f"Returned {quantity} {name}(s)",
            "item": {
                "available": item.available,
                "in_use": item.in_use,
                "threshold": item.threshold,
            },
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/items/status")
def api_get_status(
    name: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(any_user),
):
    data = get_status(db, name)
    if not data:
        raise HTTPException(
            status_code=404,
            detail="Item not found" if name else "No items found",
        )
    return data


@app.get(
    "/audit/logs",
    response_model=list[AuditLogResponse],
    summary="Get recent audit log entries",
)
def api_get_audit_logs(
    limit: int = 10,
    db: Session = Depends(get_db),
    user: User = Depends(admin_or_manager),
):
    return get_recent_logs(db, limit)
