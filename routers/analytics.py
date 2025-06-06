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
from auth import require_role
import csv
from io import StringIO
from models import User, AuditLog, Item
from datetime import datetime, timedelta
from time import time
import uuid

router = APIRouter(prefix="/analytics")

admin_or_manager = require_role(["admin", "manager"])

# In-memory store for export task results
# {task_id: csv_data or None while still generating}
export_tasks: dict[str, str | None] = {}

# Simple in-memory cache for usage results
# {key: (timestamp, data)}
usage_cache: dict[tuple, tuple[float, list[dict]]] = {}
CACHE_TTL = 300  # seconds

def _get_cached_usage(key: tuple) -> list[dict] | None:
    entry = usage_cache.get(key)
    if entry and time() - entry[0] < CACHE_TTL:
        return entry[1]
    return None


def _build_csv(db: Session, limit: int, tenant_id: int) -> str:
    """Generate CSV data for recent audit logs filtered by tenant."""
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
    """Background task: build CSV data for audit logs filtered by tenant."""
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
    """Synchronously generate and return audit log CSV for a tenant."""
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
    """Begin generating a CSV of the most recent audit logs for a tenant."""
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
    """Retrieve the generated CSV for a previously started export task."""
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
    days: int = 30,
    tenant_id: int | None = None,
    user_id: int | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(admin_or_manager),
):
    """Return usage stats for a single item."""
    if start_date and end_date:
        since = start_date
        until = end_date
    else:
        since = datetime.utcnow() - timedelta(days=days)
        until = datetime.utcnow()

    query = (
        db.query(AuditLog)
        .join(Item, AuditLog.item_id == Item.id)
        .filter(Item.name == item_name)
    )
    if tenant_id is not None:
        query = query.filter(Item.tenant_id == tenant_id)
    if user_id is not None:
        query = query.filter(AuditLog.user_id == user_id)

    cache_key = (
        "item",
        item_name,
        tenant_id,
        user_id,
        since.isoformat(),
        until.isoformat(),
    )
    cached = _get_cached_usage(cache_key)
    if cached is not None:
        return cached

    logs = (
        query.filter(AuditLog.timestamp >= since, AuditLog.timestamp <= until)
        .filter(AuditLog.action.in_(["issue", "return"]))
        .order_by(AuditLog.timestamp)
        .all()
    )

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
    return result


@router.get("/usage", summary="Aggregate issued/returned usage across all items")
def overall_usage(
    days: int = 30,
    tenant_id: int | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    item_name: str | None = None,
    user_id: int | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(admin_or_manager),
):
    """Return overall issued vs. returned counts grouped by day."""
    if start_date and end_date:
        since = start_date
        until = end_date
    else:
        since = datetime.utcnow() - timedelta(days=days)
        until = datetime.utcnow()

    query = db.query(AuditLog)
    if item_name:
        query = query.join(Item).filter(Item.name == item_name)
    if user_id is not None:
        query = query.filter(AuditLog.user_id == user_id)
    if tenant_id is not None:
        if not item_name:
            query = query.join(Item)
        query = query.filter(Item.tenant_id == tenant_id)

    cache_key = (
        "overall",
        tenant_id,
        item_name,
        user_id,
        since.isoformat(),
        until.isoformat(),
    )
    cached = _get_cached_usage(cache_key)
    if cached is not None:
        return cached

    logs = (
        query.filter(AuditLog.timestamp >= since, AuditLog.timestamp <= until)
        .filter(AuditLog.action.in_(["issue", "return"]))
        .order_by(AuditLog.timestamp)
        .all()
    )

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
    return result
