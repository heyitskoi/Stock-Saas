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
from pydantic import BaseModel, validator, conint
import uuid

router = APIRouter(prefix="/analytics")

admin_or_manager = require_role(["admin", "manager"])

# In-memory store for export task results
# {task_id: csv_data or None while still generating}
export_tasks: dict[str, str | None] = {}


class UsageParams(BaseModel):
    days: conint(gt=0) = 30
    tenant_id: int | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None

    @validator("days")
    def days_positive(cls, v):
        if v <= 0:
            raise ValueError("days must be positive")
        return v


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
    params: UsageParams = Depends(),
    db: Session = Depends(get_db),
    user: User = Depends(admin_or_manager),
):
    """Return usage stats for a single item."""
    if params.start_date and params.end_date:
        if params.start_date > params.end_date:
            raise HTTPException(
                status_code=400, detail="start_date must be before end_date"
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
    )
    if params.tenant_id is not None:
        query = query.filter(Item.tenant_id == params.tenant_id)

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

    return [
        {"date": date, "issued": v["issued"], "returned": v["returned"]}
        for date, v in sorted(data.items())
    ]


@router.get("/usage", summary="Aggregate issued/returned usage across all items")
def overall_usage(
    params: UsageParams = Depends(),
    db: Session = Depends(get_db),
    user: User = Depends(admin_or_manager),
):
    """Return overall issued vs. returned counts grouped by day."""
    if params.start_date and params.end_date:
        if params.start_date > params.end_date:
            raise HTTPException(
                status_code=400, detail="start_date must be before end_date"
            )
        since = params.start_date
        until = params.end_date
    else:
        since = datetime.utcnow() - timedelta(days=params.days)
        until = datetime.utcnow()

    query = db.query(AuditLog)
    if params.tenant_id is not None:
        query = query.join(Item).filter(Item.tenant_id == params.tenant_id)

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

    return [
        {"date": date, "issued": v["issued"], "returned": v["returned"]}
        for date, v in sorted(data.items())
    ]
