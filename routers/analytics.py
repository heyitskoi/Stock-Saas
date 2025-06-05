from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from inventory_core import get_recent_logs
from database import get_db
from auth import require_role
import csv
from io import StringIO
from models import User, AuditLog, Item
from datetime import datetime, timedelta

router = APIRouter(prefix="/analytics")

admin_or_manager = require_role(["admin", "manager"])

@router.get("/audit/export", response_class=Response, summary="Export audit log as CSV")
def export_audit_csv(limit: int = 100, db: Session = Depends(get_db), user: User = Depends(admin_or_manager)):
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
    csv_data = output.getvalue()
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

