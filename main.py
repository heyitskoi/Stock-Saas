from config import settings

from fastapi import FastAPI, WebSocket, Form, Depends

from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.websockets import WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import JWTError, jwt

from database import Base, engine, SessionLocal, DATABASE_URL
from database_async import get_async_db
import database_async
from auth import (
    login_for_access_token,
    require_role,
    get_password_hash,
    SECRET_KEY,
    ALGORITHM,
)
from models import User, Tenant
from routers.users import router as users_router
from routers.analytics import router as analytics_router
from routers.auth import router as auth_router
from routers.audit import router as audit_router
from routers.departments import router as departments_router
from routers.categories import router as categories_router
from routers.items import router as items_router
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
origins_raw = settings.cors_allow_origins or settings.next_public_api_url
if origins_raw:
    origins = [o.strip() for o in origins_raw.split(",") if o.strip()]
else:
    origins = []
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
rate_limiter = RateLimiter(
    limit=5,
    window=60,
    routes=["/token", "/users"],
    redis_url=settings.rate_limit_redis_url or "redis://redis:6379/1",
)
app.state.rate_limiter = rate_limiter
app.add_middleware(BaseHTTPMiddleware, dispatch=rate_limiter)

# Initialize DB and Routers
Base.metadata.create_all(bind=engine)
app.include_router(users_router)
app.include_router(analytics_router)
app.include_router(auth_router)
app.include_router(departments_router)
app.include_router(categories_router)
app.include_router(items_router)
app.include_router(audit_router)


@app.websocket("/ws/inventory/{tenant_id}")
async def inventory_ws(websocket: WebSocket, tenant_id: int):
    """Websocket endpoint broadcasting inventory updates scoped to a tenant."""

    token = websocket.query_params.get("token")
    if not token:
        auth_header = websocket.headers.get("Authorization")
        if auth_header and auth_header.lower().startswith("bearer "):
            token = auth_header.split(" ", 1)[1]

    if not token:
        await websocket.close(code=1008)
        return

    async with database_async.AsyncSessionLocal() as session:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            if username is None:
                raise JWTError
        except JWTError:
            await websocket.close(code=1008)
            return

        result = await session.execute(select(User).where(User.username == username))
        user = result.scalars().first()
        if not user or user.tenant_id != tenant_id:
            await websocket.close(code=1008)
            return

    await ws_manager.connect(websocket, tenant_id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, tenant_id)


@app.on_event("startup")
def create_default_admin():
    username = settings.admin_username
    password = settings.admin_password
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
