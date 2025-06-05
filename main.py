import os

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database import Base, engine, get_db, SessionLocal, DATABASE_URL
from inventory_core import add_item, issue_item, return_item, get_status
from auth import login_for_access_token, require_role, get_password_hash
from models import User
from schemas import ItemCreate, ItemResponse

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


@app.post("/items/add", response_model=ItemResponse, summary="Add items to inventory")
def api_add_item(
    item_data: ItemCreate,
    db: Session = Depends(get_db),
    user: User = Depends(admin_or_manager),
):

    item = add_item(db, item_data.name, item_data.quantity, item_data.threshold, user_id=user.id)
    return item



@app.post("/items/issue", response_model=ItemResponse, summary="Issue items to a user")
def api_issue_item(
    item_data: ItemCreate,
    db: Session = Depends(get_db),
    user: User = Depends(admin_or_manager),
):
    try:
        item = issue_item(db, item_data.name, item_data.quantity, user_id=user.id)
        return item
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/items/return", response_model=ItemResponse, summary="Return issued items")
def api_return_item(
    item_data: ItemCreate,
    db: Session = Depends(get_db),
    user: User = Depends(admin_or_manager),
):
    try:
        item = return_item(db, item_data.name, item_data.quantity, user_id=user.id)
        return item
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
