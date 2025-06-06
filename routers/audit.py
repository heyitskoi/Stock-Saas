from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from auth import require_role, ensure_tenant
from database import get_db
from inventory_core import get_recent_logs
from models import User
from schemas import AuditLogResponse

router = APIRouter(prefix="/audit", tags=["audit"])
admin_or_manager = require_role(["admin", "manager"])


@router.get("/logs", response_model=list[AuditLogResponse])
def recent_logs(
    tenant_id: int,
    limit: int = 10,
    db: Session = Depends(get_db),
    user: User = Depends(admin_or_manager),
):
    ensure_tenant(user, tenant_id)
    logs = get_recent_logs(db, limit, tenant_id)
    return logs
