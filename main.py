import os

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import Base, engine, get_db, SessionLocal, DATABASE_URL
from inventory_core import (
    add_item,
    issue_item,
    return_item,
    get_status,
    get_recent_logs,
    update_item,
    delete_item,
)
from auth import login_for_access_token, require_role, get_password_hash
from models import User, Tenant
from schemas import (
    ItemCreate,
    ItemResponse,
    AuditLogResponse,
    ItemUpdate,
    ItemDelete,
)
from routers.users import router as users_router
from routers.analytics import router as analytics_router

app = FastAPI(title="Stock SaaS API")

# configure CORS so the frontend can access the API
frontend_origin = os.getenv("NEXT_PUBLIC_API_URL")
origins = [frontend_origin] if frontend_origin else []
if DATABASE_URL.startswith("sqlite"):
    # allow everything during local development and tests
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)
app.include_router(users_router)
app.include_router(analytics_router)


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
    tenant = db.query(Tenant).filter(Tenant.name == "default").first()
    if not tenant:
        tenant = Tenant(name="default")
        db.add(tenant)
        db.commit()
        db.refresh(tenant)

    if not db.query(User).filter(User.username == username).first():
        admin = User(
            username=username,
            hashed_password=get_password_hash(password),
            role="admin",
            tenant_id=tenant.id,
            notification_preference="email",
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
    payload: ItemCreate,
    db: Session = Depends(get_db),
    user: User = Depends(admin_or_manager),
):
    item = add_item(
        db,
        payload.name,
        payload.quantity,
        payload.threshold,
        payload.tenant_id,
        user_id=user.id,
    )
    return item


@app.post("/items/issue", response_model=ItemResponse, summary="Issue items to a user")
def api_issue_item(
    payload: ItemCreate,
    db: Session = Depends(get_db),
    user: User = Depends(admin_or_manager),
):
    """Issue quantity of an item from the inventory."""
    try:
        item = issue_item(
            db,
            payload.name,
            payload.quantity,
            tenant_id=payload.tenant_id,
            user_id=user.id,
        )
        return item
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/items/return", response_model=ItemResponse, summary="Return issued items")
def api_return_item(
    payload: ItemCreate,
    db: Session = Depends(get_db),
    user: User = Depends(admin_or_manager),
):
    """Return quantity of an item to the inventory."""
    try:
        item = return_item(
            db,
            payload.name,
            payload.quantity,
            tenant_id=payload.tenant_id,
            user_id=user.id,
        )
        return item
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/items/status")
def api_get_status(
    tenant_id: int,
    name: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(any_user),
):
    data = get_status(db, tenant_id=tenant_id, name=name)
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
    tenant_id: int,
    limit: int = 10,
    db: Session = Depends(get_db),
    user: User = Depends(admin_or_manager),
):
    return get_recent_logs(db, limit, tenant_id)


@app.put("/items/update", response_model=ItemResponse, summary="Update an item")
def api_update_item(
    payload: ItemUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(admin_or_manager),
):
    try:
        item = update_item(
            db,
            payload.name,
            tenant_id=payload.tenant_id,
            new_name=payload.new_name,
            threshold=payload.threshold,
            user_id=user.id,
        )
        return item
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.delete("/items/delete", summary="Delete an item")
def api_delete_item(
    payload: ItemDelete,
    db: Session = Depends(get_db),
    user: User = Depends(admin_or_manager),
):
    try:
        delete_item(
            db,
            payload.name,
            tenant_id=payload.tenant_id,
            user_id=user.id,
        )
        return {"detail": "Item deleted"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
