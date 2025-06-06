from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict
from database import get_db
from auth import get_current_user
from models import User
from schemas import (
    ItemCreate,
    ItemUpdate,
    ItemDelete,
    ItemResponse,
    TransferRequest,
    TransferResponse,
)
from inventory_core import (
    add_item,
    issue_item,
    return_item,
    get_status,
    update_item,
    delete_item,
    transfer_item,
    get_item_history,
)

router = APIRouter(prefix="/items", tags=["items"])


@router.post("/add", response_model=ItemResponse)
def api_add_item(payload: ItemCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        item = add_item(
            db,
            name=payload.name,
            qty=payload.quantity,
            threshold=payload.threshold,
            tenant_id=payload.tenant_id,
            min_par=payload.min_par,
            department_id=payload.department_id,
            category_id=payload.category_id,
            stock_code=payload.stock_code,
            status=payload.status,
            user_id=current_user.id,
        )
        return item
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/status")
def api_status(name: str | None = None, tenant_id: int = 1, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    items: Dict[str, dict] = get_status(db, tenant_id=tenant_id, name=name)
    if not items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return items


@router.put("/update", response_model=ItemResponse)
def api_update_item(payload: ItemUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        item = update_item(
            db,
            name=payload.name,
            tenant_id=payload.tenant_id,
            new_name=payload.new_name,
            threshold=payload.threshold,
            min_par=payload.min_par,
            department_id=payload.department_id,
            category_id=payload.category_id,
            stock_code=payload.stock_code,
            status=payload.status,
            user_id=current_user.id,
        )
        return item
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/delete")
def api_delete_item(payload: ItemDelete, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        delete_item(db, name=payload.name, tenant_id=payload.tenant_id, user_id=current_user.id)
        return {"detail": "Item deleted"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/transfer", response_model=TransferResponse)
def api_transfer_item(payload: TransferRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        from_item, to_item = transfer_item(
            db,
            name=payload.name,
            qty=payload.quantity,
            from_tenant_id=payload.from_tenant_id,
            to_tenant_id=payload.to_tenant_id,
            user_id=current_user.id,
        )
        return {"from_item": from_item, "to_item": to_item}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/history")
def api_item_history(name: str, tenant_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    logs = get_item_history(db, name=name, tenant_id=tenant_id)
    return [
        {
            "id": log.id,
            "user_id": log.user_id,
            "item_id": log.item_id,
            "action": log.action,
            "quantity": log.quantity,
            "timestamp": log.timestamp,
        }
        for log in logs
    ]
