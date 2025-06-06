import os
import asyncio

from fastapi import FastAPI, HTTPException, Depends, WebSocket
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.websockets import WebSocketDisconnect
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from database import Base, engine, get_db, SessionLocal, DATABASE_URL
from database_async import get_async_db
from inventory_core import (
    add_item,
    issue_item,
    return_item,
    get_status,
    get_recent_logs,
    update_item,
    delete_item,
    async_add_item,
    async_issue_item,
    async_return_item,
    async_get_status,
    async_get_recent_logs,
    async_update_item,
    async_delete_item,
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
from websocket_manager import InventoryWSManager
from rate_limiter import RateLimiter


app = FastAPI(
    title="Stock SaaS API",
    description=(
        "Multi-tenant inventory management API. Include `tenant_id` in all"
        " requests to scope data. Long running operations such as CSV exports"
        " run as background tasks. Environment variables configure the database,"
        " initial admin credentials and notification settings."
    ),
)

ws_manager = InventoryWSManager()

# Configure CORS
frontend_origin = os.getenv("NEXT_PUBLIC_API_URL")
origins = [frontend_origin] if frontend_origin else []
if DATABASE_URL.startswith("sqlite"):
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting middleware for sensitive endpoints
rate_limiter = RateLimiter(limit=5, window=60, routes=["/token", "/users"])
app.state.rate_limiter = rate_limiter
app.add_middleware(BaseHTTPMiddleware, dispatch=rate_limiter)

# Initialize DB and Routers
Base.metadata.create_all(bind=engine)
app.include_router(users_router)
app.include_router(analytics_router)


@app.websocket("/ws/inventory/{tenant_id}")
async def inventory_ws(websocket: WebSocket, tenant_id: int):
    await ws_manager.connect(websocket, tenant_id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, tenant_id)


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


# Role guards
admin_or_manager = require_role(["admin", "manager"])
any_user = require_role(["admin", "manager", "user"])


@app.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_db),
):
    """Authenticate a user and return a JWT access token."""
    return await login_for_access_token(form_data, db)


@app.post("/items/add", response_model=ItemResponse, summary="Add items to inventory")
async def api_add_item(
    payload: ItemCreate,
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(admin_or_manager),
):
    item = await async_add_item(
        db,
        payload.name,
        payload.quantity,
        payload.threshold,
        payload.tenant_id,
        user_id=user.id,
    )
    asyncio.create_task(
        ws_manager.broadcast(
            payload.tenant_id,
            {
                "event": "update",
                "item": item.name,
                "available": item.available,
                "in_use": item.in_use,
                "threshold": item.threshold,
            },
        )
    )
    return item


@app.post("/items/issue", response_model=ItemResponse, summary="Issue items to a user")
async def api_issue_item(
    payload: ItemCreate,
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(admin_or_manager),
):
    try:
        item = await async_issue_item(
            db,
            payload.name,
            payload.quantity,
            tenant_id=payload.tenant_id,
            user_id=user.id,
        )
        asyncio.create_task(
            ws_manager.broadcast(
                payload.tenant_id,
                {
                    "event": "update",
                    "item": item.name,
                    "available": item.available,
                    "in_use": item.in_use,
                    "threshold": item.threshold,
                },
            )
        )
        return item
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/items/return", response_model=ItemResponse, summary="Return issued items")
async def api_return_item(
    payload: ItemCreate,
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(admin_or_manager),
):
    try:
        item = await async_return_item(
            db,
            payload.name,
            payload.quantity,
            tenant_id=payload.tenant_id,
            user_id=user.id,
        )
        asyncio.create_task(
            ws_manager.broadcast(
                payload.tenant_id,
                {
                    "event": "update",
                    "item": item.name,
                    "available": item.available,
                    "in_use": item.in_use,
                    "threshold": item.threshold,
                },
            )
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
async def api_update_item(
    payload: ItemUpdate,
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(admin_or_manager),
):
    try:
        item = await async_update_item(
            db,
            payload.name,
            tenant_id=payload.tenant_id,
            new_name=payload.new_name,
            threshold=payload.threshold,
            user_id=user.id,
        )
        asyncio.create_task(
            ws_manager.broadcast(
                payload.tenant_id,
                {
                    "event": "update",
                    "item": item.name,
                    "available": item.available,
                    "in_use": item.in_use,
                    "threshold": item.threshold,
                },
            )
        )
        return item
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.delete("/items/delete", summary="Delete an item")
async def api_delete_item(
    payload: ItemDelete,
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(admin_or_manager),
):
    try:
        await async_delete_item(
            db,
            payload.name,
            tenant_id=payload.tenant_id,
            user_id=user.id,
        )
        asyncio.create_task(
            ws_manager.broadcast(
                payload.tenant_id,
                {
                    "event": "delete",
                    "item": payload.name,
                },
            )
        )
        return {"detail": "Item deleted"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
