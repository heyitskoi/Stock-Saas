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
import uuid

router = APIRouter(prefix="/analytics")

admin_or_manager = require_role(["admin", "manager"])

# In-memory export task results {task_id: csv_data or None while pending}
export_tasks: dict[str, str | None] = {}


def _build_csv(db: Session, limit: int, tenant_id: int) -> str:
    """Generate CSV data for recent audit logs."""
    logs = get_recent_logs(db, limit, tenant_id)
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(
        ["id", "user_id", "item_id", "action", "quantity", "timestamp"]
    )
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


@router.post("/audit/export", summary="Start async audit log CSV export")
def start_audit_export(
    background_tasks: BackgroundTasks,
    tenant_id: int,
    limit: int = 100,
    user: User = Depends(admin_or_manager),
):
    """
    Begin generating a CSV of the most recent audit logs for a given tenant.
    Returns a task_id that can be used to retrieve the CSV once it's ready.
    """
    task_id = str(uuid.uuid4())
    export_tasks[task_id] = None
    background_tasks.add_task(_generate_csv, limit, tenant_id, task_id)
    return {"task_id": task_id}


@router.get(
    "/audit/export",
    response_class=Response,
    summary="Download audit log CSV synchronously",
)
def export_audit_csv(
    tenant_id: int,
    limit: int = 100,
    db: Session = Depends(get_db),
    user: User = Depends(admin_or_manager),
):
    """Generate and return a CSV of recent audit logs."""
    csv_data = _build_csv(db, limit, tenant_id)
    return Response(content=csv_data, media_type="text/csv")


@router.get(
    "/audit/export/{task_id}",
    response_class=Response,
    summary="Download generated audit log CSV",
)
def get_exported_csv(
    task_id: str,
    user: User = Depends(admin_or_manager),
):
    """
    Retrieve the generated CSV for a previously started export task.
    If the CSV is still being generated, returns HTTP 202.
    """
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
    db: Session = Depends(get_db),
    user: User = Depends(admin_or_manager),
):
    """
    Return usage statistics (issued vs. returned) for a single item, grouped by day,
    over the past `days` days.
    """
    since = datetime.utcnow() - timedelta(days=days)
    logs = (
        db.query(AuditLog)
        .join(Item, AuditLog.item_id == Item.id)
        .filter(Item.name == item_name, AuditLog.timestamp >= since)
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

    return [
        {"date": date, "issued": v["issued"], "returned": v["returned"]}
        for date, v in sorted(data.items())
    ]


@router.get("/usage", summary="Aggregate issued/returned usage across all items")
def overall_usage(
    days: int = 30,
    db: Session = Depends(get_db),
    user: User = Depends(admin_or_manager),
):
    """
    Return overall issued vs. returned counts, grouped by day,
    across all items over the past `days` days.
    """
    since = datetime.utcnow() - timedelta(days=days)
    logs = (
        db.query(AuditLog)
        .filter(AuditLog.timestamp >= since)
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

    return [
        {"date": date, "issued": v["issued"], "returned": v["returned"]}
        for date, v in sorted(data.items())
    ]
