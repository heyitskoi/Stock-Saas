from fastapi import (
    APIRouter,
    Depends,
    Response,
    BackgroundTasks,
    HTTPException,
)
from inventory_core import get_recent_logs
from database import SessionLocal, get_db
from auth import require_role
import csv
from io import StringIO
from models import User, AuditLog, Item
from datetime import datetime, timedelta
import uuid

router = APIRouter(prefix="/analytics")

admin_or_manager = require_role(["admin", "manager"])

# store results of async exports in memory {task_id: csv_data}
export_tasks: dict[str, str | None] = {}


def _generate_csv(limit: int, task_id: str) -> None:
    """Background task to build the CSV data for audit logs."""
    db = SessionLocal()
    try:
        logs = get_recent_logs(db, limit)
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["id", "user_id", "item_id", "action", "quantity", "timestamp"])
        for log in logs:
            writer.writerow([
                log.id,
                log.user_id,
                log.item_id,
                log.action,
                log.quantity,
                log.timestamp.isoformat(),
            ])
        export_tasks[task_id] = output.getvalue()
    finally:
        db.close()


@router.post("/audit/export", summary="Start async audit log CSV export")
def start_audit_export(
    background_tasks: BackgroundTasks,
    limit: int = 100,
    user: User = Depends(admin_or_manager),
):
    task_id = str(uuid.uuid4())
    export_tasks[task_id] = None
    background_tasks.add_task(_generate_csv, limit, task_id)
    return {"task_id": task_id}


@router.get(
    "/audit/export/{task_id}",
    response_class=Response,
    summary="Download generated audit log CSV",
)
def get_exported_csv(task_id: str, user: User = Depends(admin_or_manager)):
    if task_id not in export_tasks:
        raise HTTPException(status_code=404, detail="Export not found")
    csv_data = export_tasks[task_id]
    if csv_data is None:
        raise HTTPException(status_code=202, detail="Export in progress")
    headers = {"Content-Type": "text/csv"}
    return Response(content=csv_data, media_type="text/csv", headers=headers)


@router.get("/usage/{item_name}", summary="Aggregate issued/returned quantities for an item")
def item_usage(
    item_name: str,
    days: int = 30,
    db: Session = Depends(get_db),
    user: User = Depends(admin_or_manager),
):
    """Return usage statistics for a single item grouped by day."""
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


@router.get("/usage", summary="Aggregate usage across all items")
def overall_usage(
    days: int = 30,
    db: Session = Depends(get_db),
    user: User = Depends(admin_or_manager),
):
    """Return overall issued/returned counts grouped by day."""
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
