from fastapi import (
    APIRouter,
    Depends,
    Response,
    BackgroundTasks,
    HTTPException,
)
from inventory_core import get_recent_logs
from database import SessionLocal, get_db
from sqlalchemy.orm import Session
from auth import require_role, ensure_tenant
import csv
from io import StringIO
from models import User, AuditLog, Item
from datetime import datetime, timedelta
from pydantic import BaseModel, validator, conint
from time import time
from cache import get_cached, set_cached
import uuid

router = APIRouter(prefix="/analytics")

admin_or_manager = require_role(["admin", "manager"])

# In-memory store for export task results
export_tasks: dict[str, str | None] = {}

# Simple in-memory cache for usage results as a fallback when Redis is unavailable
usage_cache: dict[tuple, tuple[float, list[dict]]] = {}
CACHE_TTL = 300  # seconds


def _get_cached_usage(key: tuple) -> list[dict] | None:
    cached = get_cached(str(key))
    if cached is not None:
        return cached

    entry = usage_cache.get(key)
    if entry and time() - entry[0] < CACHE_TTL:
        return entry[1]
    return None


class UsageParams(BaseModel):
    days: conint(gt=0) = 30
    tenant_id: int | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    user_id: int | None = None
    item_name: str | None = None

    @validator("days")
    def days_positive(cls, v):
        if v <= 0:
            raise ValueError("days must be positive")
        return v


def _build_csv(db: Session, limit: int, tenant_id: int) -> str:
    logs = get_recent_logs(db, limit, tenant_id)
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "user_id", "item_id", "action", "quantity", "timestamp"])
    for log in logs:
        writer.writerow(
            [
                log.id,
                log.user_id,
                log.item_id,
                log.action,
                log.quantity,
                log.timestamp.isoformat(),
            ]
        )
    return output.getvalue()


def _generate_csv(limit: int, tenant_id: int, task_id: str) -> None:
    db = SessionLocal()
    try:
        export_tasks[task_id] = _build_csv(db, limit, tenant_id)
    finally:
        db.close()


@router.get(
    "/audit/export",
    response_class=Response,
    summary="Export audit log CSV immediately",
)
def export_audit_csv(
    tenant_id: int,
    limit: int = 100,
    db: Session = Depends(get_db),
    user: User = Depends(admin_or_manager),
):
    ensure_tenant(user, tenant_id)
    csv_data = _build_csv(db, limit, tenant_id)
    return Response(content=csv_data, media_type="text/csv")


@router.post(
    "/audit/export",
    summary="Start async audit log CSV export",
)
def start_audit_export(
    background_tasks: BackgroundTasks,
    tenant_id: int,
    limit: int = 100,
    user: User = Depends(admin_or_manager),
):
    ensure_tenant(user, tenant_id)
    task_id = str(uuid.uuid4())
    export_tasks[task_id] = None
    background_tasks.add_task(_generate_csv, limit, tenant_id, task_id)
    return {"task_id": task_id}


@router.get(
    "/audit/export/{task_id}",
    response_class=Response,
    summary="Download generated audit log CSV",
)
def get_exported_csv(
    task_id: str,
    user: User = Depends(admin_or_manager),
):
    if task_id not in export_tasks:
        raise HTTPException(status_code=404, detail="Export not found")
    csv_data = export_tasks[task_id]
    if csv_data is None:
        raise HTTPException(status_code=202, detail="Export in progress")
    return Response(content=csv_data, media_type="text/csv")


@router.get(
    "/usage/{item_name}",
    summary="Aggregate issued/returned quantities for a single item",
)
def item_usage(
    item_name: str,
    params: UsageParams = Depends(),
    db: Session = Depends(get_db),
    user: User = Depends(admin_or_manager),
):
    if params.start_date and params.end_date:
        if params.start_date > params.end_date:
            raise HTTPException(
                status_code=400,
                detail="start_date must be before end_date",
            )
        since = params.start_date
        until = params.end_date
    else:
        since = datetime.utcnow() - timedelta(days=params.days)
        until = datetime.utcnow()

    query = (
        db.query(AuditLog)
        .join(Item, AuditLog.item_id == Item.id)
        .filter(Item.name == item_name)
        .filter(AuditLog.timestamp >= since, AuditLog.timestamp <= until)
        .filter(AuditLog.action.in_(["issue", "return"]))
        .order_by(AuditLog.timestamp)
    )

    if params.tenant_id is not None:
        ensure_tenant(user, params.tenant_id)
        query = query.filter(Item.tenant_id == params.tenant_id)
    if params.user_id is not None:
        query = query.filter(AuditLog.user_id == params.user_id)

    cache_key = (
        "item",
        item_name,
        params.tenant_id,
        params.user_id,
        since.isoformat(),
        until.isoformat(),
    )
    cached = _get_cached_usage(cache_key)
    if cached is not None:
        return cached

    logs = query.all()
    data: dict[str, dict[str, int]] = {}
    for log in logs:
        date_key = log.timestamp.date().isoformat()
        entry = data.setdefault(date_key, {"issued": 0, "returned": 0})
        if log.action == "issue":
            entry["issued"] += log.quantity
        else:
            entry["returned"] += log.quantity

    result = [
        {"date": date, "issued": v["issued"], "returned": v["returned"]}
        for date, v in sorted(data.items())
    ]
    usage_cache[cache_key] = (time(), result)
    set_cached(str(cache_key), result, CACHE_TTL)
    return result


@router.get(
    "/usage",
    summary="Aggregate issued/returned usage across all items",
)
def overall_usage(
    params: UsageParams = Depends(),
    db: Session = Depends(get_db),
    user: User = Depends(admin_or_manager),
):
    if params.start_date and params.end_date:
        if params.start_date > params.end_date:
            raise HTTPException(
                status_code=400,
                detail="start_date must be before end_date",
            )
        since = params.start_date
        until = params.end_date
    else:
        since = datetime.utcnow() - timedelta(days=params.days)
        until = datetime.utcnow()

    query = (
        db.query(AuditLog)
        .filter(
            AuditLog.timestamp >= since,
            AuditLog.timestamp <= until,
            AuditLog.action.in_(["issue", "return"]),
        )
        .order_by(AuditLog.timestamp)
    )

    if params.item_name:
        query = query.join(Item).filter(Item.name == params.item_name)
    elif params.tenant_id is not None:
        ensure_tenant(user, params.tenant_id)
        query = query.join(Item).filter(Item.tenant_id == params.tenant_id)

    if params.user_id is not None:
        query = query.filter(AuditLog.user_id == params.user_id)

    cache_key = (
        "overall",
        params.tenant_id,
        params.item_name,
        params.user_id,
        since.isoformat(),
        until.isoformat(),
    )
    cached = _get_cached_usage(cache_key)
    if cached is not None:
        return cached

    logs = query.all()
    data: dict[str, dict[str, int]] = {}
    for log in logs:
        date_key = log.timestamp.date().isoformat()
        entry = data.setdefault(date_key, {"issued": 0, "returned": 0})
        if log.action == "issue":
            entry["issued"] += log.quantity
        else:
            entry["returned"] += log.quantity

    result = [
        {"date": date, "issued": v["issued"], "returned": v["returned"]}
        for date, v in sorted(data.items())
    ]
    usage_cache[cache_key] = (time(), result)
    set_cached(str(cache_key), result, CACHE_TTL)
    return result
