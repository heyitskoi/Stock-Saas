from typing import Dict, Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from models import Item, AuditLog
from datetime import datetime


def _log_action(
    db: Session, user_id: Optional[int], item: Item, action: str, quantity: int
):
    log = AuditLog(
        user_id=user_id,
        item_id=item.id,
        action=action,
        quantity=quantity,
        timestamp=datetime.utcnow(),
    )
    db.add(log)

def add_item(
    db: Session,
    name: str,
    qty: int,
    threshold: int,
    tenant_id: int,
    min_par: int = 0,
    department_id: Optional[int] = None,
    category_id: Optional[int] = None,
    stock_code: Optional[str] = None,
    status: Optional[str] = None,
    user_id: Optional[int] = None,
) -> Item:
    if qty <= 0:
        raise ValueError("Quantity must be positive")
    if threshold < 0:
        raise ValueError("Threshold cannot be negative")
    item = db.query(Item).filter(Item.name == name, Item.tenant_id == tenant_id).first()
    if not item:
        item = Item(
            name=name,
            tenant_id=tenant_id,
            available=0,
            in_use=0,
            threshold=threshold,
            min_par=min_par,
            department_id=department_id,
            category_id=category_id,
            stock_code=stock_code,
            status=status,
        )
        db.add(item)

    item.available += qty
    if threshold is not None:
        item.threshold = threshold
    if min_par is not None:
        item.min_par = min_par
    if department_id is not None:
        item.department_id = department_id
    if category_id is not None:
        item.category_id = category_id
    if stock_code is not None:
        item.stock_code = stock_code
    if status is not None:
        item.status = status

    db.flush()
    _log_action(db, user_id, item, "add", qty)
    db.commit()
    db.refresh(item)
    return item


def issue_item(
    db: Session,
    name: str,
    qty: int,
    tenant_id: int,
    user_id: Optional[int] = None,
) -> Item:
    if qty <= 0:
        raise ValueError("Quantity must be positive")
    item = db.query(Item).filter(Item.name == name, Item.tenant_id == tenant_id).first()
    if not item or item.available < qty:
        raise ValueError("Not enough stock to issue")

    item.available -= qty
    item.in_use += qty

    _log_action(db, user_id, item, "issue", qty)
    db.commit()
    db.refresh(item)
    return item


def return_item(
    db: Session,
    name: str,
    qty: int,
    tenant_id: int,
    user_id: Optional[int] = None,
) -> Item:
    if qty <= 0:
        raise ValueError("Quantity must be positive")
    item = db.query(Item).filter(Item.name == name, Item.tenant_id == tenant_id).first()
    if not item or item.in_use < qty:
        raise ValueError("Invalid return quantity")

    item.in_use -= qty
    item.available += qty

    _log_action(db, user_id, item, "return", qty)
    db.commit()
    db.refresh(item)
    return item


def get_status(
    db: Session, tenant_id: int, name: Optional[str] = None
) -> Dict[str, dict]:
    items: Dict[str, dict] = {}
    base_query = db.query(Item).filter(Item.tenant_id == tenant_id)

    if name:
        item = base_query.filter(Item.name == name).first()
        if item:
            items[item.name] = {
                "available": item.available,
                "in_use": item.in_use,
                "threshold": item.threshold,
                "min_par": item.min_par,
                "department_id": item.department_id,
                "category_id": item.category_id,
                "stock_code": item.stock_code,
                "status": item.status,
            }
    else:
        for item in base_query.all():
            items[item.name] = {
                "available": item.available,
                "in_use": item.in_use,
                "threshold": item.threshold,
                "min_par": item.min_par,
                "department_id": item.department_id,
                "category_id": item.category_id,
                "stock_code": item.stock_code,
                "status": item.status,
            }

    return items


def get_recent_logs(
    db: Session, limit: int = 10, tenant_id: Optional[int] = None
) -> List[AuditLog]:
    query = db.query(AuditLog)
    if tenant_id is not None:
        query = query.join(Item).filter(Item.tenant_id == tenant_id)

    return query.order_by(AuditLog.timestamp.desc()).limit(limit).all()


def get_item_history(
    db: Session, name: str, tenant_id: int, limit: int = 100
) -> List[AuditLog]:
    """Return audit log entries for a specific item."""
    item = db.query(Item).filter(Item.name == name, Item.tenant_id == tenant_id).first()
    if not item:
        return []
    return (
        db.query(AuditLog)
        .filter(AuditLog.item_id == item.id)
        .order_by(AuditLog.timestamp.desc())
        .limit(limit)
        .all()
    )


def update_item(
    db: Session,
    name: str,
    tenant_id: int,
    new_name: Optional[str] = None,
    threshold: Optional[int] = None,
    min_par: Optional[int] = None,
    department_id: Optional[int] = None,
    category_id: Optional[int] = None,
    stock_code: Optional[str] = None,
    status: Optional[str] = None,
    user_id: Optional[int] = None,
) -> Item:
    """Update an item's name and/or threshold."""
    item = db.query(Item).filter(Item.name == name, Item.tenant_id == tenant_id).first()
    if not item:
        raise ValueError("Item not found")

    if new_name:
        item.name = new_name
    if threshold is not None:
        if threshold < 0:
            raise ValueError("Threshold cannot be negative")
        item.threshold = threshold
    if min_par is not None:
        if min_par < 0:
            raise ValueError("min_par cannot be negative")
        item.min_par = min_par
    if department_id is not None:
        item.department_id = department_id
    if category_id is not None:
        item.category_id = category_id
    if stock_code is not None:
        item.stock_code = stock_code
    if status is not None:
        item.status = status
    if min_par is not None:
        if min_par < 0:
            raise ValueError("min_par cannot be negative")
        item.min_par = min_par
    if department_id is not None:
        item.department_id = department_id
    if category_id is not None:
        item.category_id = category_id
    if stock_code is not None:
        item.stock_code = stock_code
    if status is not None:
        item.status = status
    if min_par is not None:
        if min_par < 0:
            raise ValueError("min_par cannot be negative")
        item.min_par = min_par
    if department_id is not None:
        item.department_id = department_id
    if category_id is not None:
        item.category_id = category_id
    if stock_code is not None:
        item.stock_code = stock_code
    if status is not None:
        item.status = status
    if min_par is not None:
        if min_par < 0:
            raise ValueError("min_par cannot be negative")
        item.min_par = min_par
    if department_id is not None:
        item.department_id = department_id
    if category_id is not None:
        item.category_id = category_id
    if stock_code is not None:
        item.stock_code = stock_code
    if status is not None:
        item.status = status
    if min_par is not None:
        if min_par < 0:
            raise ValueError("min_par cannot be negative")
        item.min_par = min_par
    if department_id is not None:
        item.department_id = department_id
    if category_id is not None:
        item.category_id = category_id
    if stock_code is not None:
        item.stock_code = stock_code
    if status is not None:
        item.status = status

    _log_action(db, user_id, item, "update", 0)
    db.commit()
    db.refresh(item)
    return item


def delete_item(
    db: Session,
    name: str,
    tenant_id: int,
    user_id: Optional[int] = None,
) -> None:
    """Remove an item from the inventory."""
    item = db.query(Item).filter(Item.name == name, Item.tenant_id == tenant_id).first()
    if not item:
        raise ValueError("Item not found")

    _log_action(db, user_id, item, "delete", 0)
    db.delete(item)
    db.commit()


def transfer_item(
    db: Session,
    name: str,
    qty: int,
    from_tenant_id: int,
    to_tenant_id: int,
    user_id: Optional[int] = None,
) -> Tuple[Item, Item]:
    """Move stock between tenants and log the transfer."""
    if qty <= 0:
        raise ValueError("Quantity must be positive")

    from_item = (
        db.query(Item)
        .filter(Item.name == name, Item.tenant_id == from_tenant_id)
        .first()
    )
    if not from_item or from_item.available < qty:
        raise ValueError("Not enough stock to transfer")

    to_item = (
        db.query(Item).filter(Item.name == name, Item.tenant_id == to_tenant_id).first()
    )
    if not to_item:
        to_item = Item(
            name=name,
            tenant_id=to_tenant_id,
            available=0,
            in_use=0,
            threshold=from_item.threshold,
        )
        db.add(to_item)

    from_item.available -= qty
    to_item.available += qty

    _log_action(db, user_id, from_item, "transfer", qty)
    _log_action(db, user_id, to_item, "transfer", qty)

    db.commit()
    db.refresh(from_item)
    db.refresh(to_item)
    return from_item, to_item


async def async_add_item(
    db: AsyncSession,
    name: str,
    qty: int,
    threshold: int,
    tenant_id: int,
    min_par: int = 0,
    department_id: Optional[int] = None,
    category_id: Optional[int] = None,
    stock_code: Optional[str] = None,
    status: Optional[str] = None,
    user_id: Optional[int] = None,
) -> Item:
    """Async wrapper around :func:`add_item`."""
    return await db.run_sync(
        lambda sync_db: add_item(
            sync_db,
            name,
            qty,
            threshold,
            tenant_id,
            min_par,
            department_id,
            category_id,
            stock_code,
            status,
            user_id,
        )
    )


async def async_issue_item(
    db: AsyncSession,
    name: str,
    qty: int,
    tenant_id: int,
    user_id: Optional[int] = None,
) -> Item:
    """Async wrapper around :func:`issue_item`."""
    return await db.run_sync(
        lambda sync_db: issue_item(sync_db, name, qty, tenant_id, user_id)
    )


async def async_return_item(
    db: AsyncSession,
    name: str,
    qty: int,
    tenant_id: int,
    user_id: Optional[int] = None,
) -> Item:
    """Async wrapper around :func:`return_item`."""
    return await db.run_sync(
        lambda sync_db: return_item(sync_db, name, qty, tenant_id, user_id)
    )


async def async_get_status(
    db: AsyncSession, tenant_id: int, name: Optional[str] = None
) -> Dict[str, dict]:
    """Async wrapper around :func:`get_status`."""
    return await db.run_sync(lambda sync_db: get_status(sync_db, tenant_id, name))


async def async_get_recent_logs(
    db: AsyncSession, limit: int = 10, tenant_id: Optional[int] = None
) -> List[AuditLog]:
    """Async wrapper around :func:`get_recent_logs`."""
    return await db.run_sync(
        lambda sync_db: get_recent_logs(sync_db, limit=limit, tenant_id=tenant_id)
    )


async def async_get_item_history(
    db: AsyncSession, name: str, tenant_id: int, limit: int = 100
) -> List[AuditLog]:
    """Async wrapper around :func:`get_item_history`."""
    return await db.run_sync(
        lambda sync_db: get_item_history(sync_db, name, tenant_id, limit)
    )


async def async_update_item(
    db: AsyncSession,
    name: str,
    tenant_id: int,
    new_name: Optional[str] = None,
    threshold: Optional[int] = None,
    min_par: Optional[int] = None,
    department_id: Optional[int] = None,
    category_id: Optional[int] = None,
    stock_code: Optional[str] = None,
    status: Optional[str] = None,
    user_id: Optional[int] = None,
) -> Item:
    """Async wrapper around :func:`update_item`."""
    return await db.run_sync(
        lambda sync_db: update_item(
            sync_db,
            name,
            tenant_id,
            new_name,
            threshold,
            min_par,
            department_id,
            category_id,
            stock_code,
            status,
            user_id,
        )
    )


async def async_delete_item(
    db: AsyncSession,
    name: str,
    tenant_id: int,
    user_id: Optional[int] = None,
) -> None:
    """Async wrapper around :func:`delete_item`."""
    await db.run_sync(
        lambda sync_db: delete_item(sync_db, name, tenant_id, user_id)
    )


async def async_transfer_item(
    db: AsyncSession,
    name: str,
    qty: int,
    from_tenant_id: int,
    to_tenant_id: int,
    user_id: Optional[int] = None,
) -> Tuple[Item, Item]:
    """Async wrapper around :func:`transfer_item`."""
    return await db.run_sync(
        lambda sync_db: transfer_item(
            sync_db,
            name,
            qty,
            from_tenant_id,
            to_tenant_id,
            user_id,
        )
    )
