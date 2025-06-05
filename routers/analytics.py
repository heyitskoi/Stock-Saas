from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from inventory_core import get_recent_logs
from database import get_db
from auth import require_role
import csv
from io import StringIO
from models import User

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

