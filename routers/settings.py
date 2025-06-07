from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth import require_role, ensure_tenant
from database import get_db
from models import Setting, User
from schemas import SettingsUpdate

router = APIRouter()

admin_only = require_role(["admin"])


@router.get("/settings", response_model=dict[str, str])
def read_settings(
    tenant_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(admin_only),
):
    ensure_tenant(user, tenant_id)
    settings = db.query(Setting).filter(Setting.tenant_id == tenant_id).all()
    return {s.key: s.value for s in settings}


@router.put("/settings", response_model=dict[str, str])
def update_settings(
    payload: SettingsUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(admin_only),
):
    ensure_tenant(user, payload.tenant_id)
    for key, value in payload.settings.items():
        setting = (
            db.query(Setting)
            .filter(Setting.tenant_id == payload.tenant_id, Setting.key == key)
            .first()
        )
        if setting:
            setting.value = value
        else:
            setting = Setting(tenant_id=payload.tenant_id, key=key, value=value)
            db.add(setting)
    db.commit()
    settings = db.query(Setting).filter(Setting.tenant_id == payload.tenant_id).all()
    return {s.key: s.value for s in settings}

