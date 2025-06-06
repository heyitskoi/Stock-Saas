from typing import Dict, Optional, List, Union
from sqlalchemy.orm import Session
from sqlalchemy import select
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


async def _async_log_action(
    db: AsyncSession, user_id: Optional[int], item: Item, action: str, quantity: int
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
    user_id: Optional[int] = None,
) -> Item:
    item = db.query(Item).filter(Item.name == name, Item.tenant_id == tenant_id).first()
    if not item:
        item = Item(
            name=name,
            tenant_id=tenant_id,
            available=0,
            in_use=0,
            threshold=threshold,
        )
        db.add(item)

    item.available += qty
    if threshold is not None:
        item.threshold = threshold

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
            }
    else:
        for item in base_query.all():
            items[item.name] = {
                "available": item.available,
                "in_use": item.in_use,
                "threshold": item.threshold,
            }

    return items


def get_recent_logs(
    db: Session, limit: int = 10, tenant_id: Optional[int] = None
) -> List[AuditLog]:
    query = db.query(AuditLog)
    if tenant_id is not None:
        query = query.join(Item).filter(Item.tenant_id == tenant_id)

    return query.order_by(AuditLog.timestamp.desc()).limit(limit).all()


def update_item(
    db: Session,
    name: str,
    tenant_id: int,
    new_name: Optional[str] = None,
    threshold: Optional[int] = None,
    user_id: Optional[int] = None,
) -> Item:
    """Update an item's name and/or threshold."""
    item = db.query(Item).filter(Item.name == name, Item.tenant_id == tenant_id).first()
    if not item:
        raise ValueError("Item not found")

    if new_name:
        item.name = new_name
    if threshold is not None:
        item.threshold = threshold

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


async def async_add_item(
    db: AsyncSession,
    name: str,
    qty: int,
    threshold: int,
    tenant_id: int,
    user_id: Optional[int] = None,
) -> Item:
    result = await db.execute(
        select(Item).where(Item.name == name, Item.tenant_id == tenant_id)
    )
    item = result.scalars().first()
    if not item:
        item = Item(
            name=name,
            tenant_id=tenant_id,
            available=0,
            in_use=0,
            threshold=threshold,
        )
        db.add(item)

    item.available += qty
    if threshold is not None:
        item.threshold = threshold

    await db.flush()
    await _async_log_action(db, user_id, item, "add", qty)
    await db.commit()
    await db.refresh(item)
    return item


async def async_issue_item(
    db: AsyncSession,
    name: str,
    qty: int,
    tenant_id: int,
    user_id: Optional[int] = None,
) -> Item:
    result = await db.execute(
        select(Item).where(Item.name == name, Item.tenant_id == tenant_id)
    )
    item = result.scalars().first()
    if not item or item.available < qty:
        raise ValueError("Not enough stock to issue")

    item.available -= qty
    item.in_use += qty

    await _async_log_action(db, user_id, item, "issue", qty)
    await db.commit()
    await db.refresh(item)
    return item


async def async_return_item(
    db: AsyncSession,
    name: str,
    qty: int,
    tenant_id: int,
    user_id: Optional[int] = None,
) -> Item:
    result = await db.execute(
        select(Item).where(Item.name == name, Item.tenant_id == tenant_id)
    )
    item = result.scalars().first()
    if not item or item.in_use < qty:
        raise ValueError("Invalid return quantity")

    item.in_use -= qty
    item.available += qty

    await _async_log_action(db, user_id, item, "return", qty)
    await db.commit()
    await db.refresh(item)
    return item


async def async_get_status(
    db: AsyncSession, tenant_id: int, name: Optional[str] = None
) -> Dict[str, dict]:
    items: Dict[str, dict] = {}
    stmt = select(Item).where(Item.tenant_id == tenant_id)

    if name:
        result = await db.execute(stmt.where(Item.name == name))
        item = result.scalars().first()
        if item:
            items[item.name] = {
                "available": item.available,
                "in_use": item.in_use,
                "threshold": item.threshold,
            }
    else:
        result = await db.execute(stmt)
        for item in result.scalars().all():
            items[item.name] = {
                "available": item.available,
                "in_use": item.in_use,
                "threshold": item.threshold,
            }

    return items


async def async_get_recent_logs(
    db: AsyncSession, limit: int = 10, tenant_id: Optional[int] = None
) -> List[AuditLog]:
    stmt = select(AuditLog)
    if tenant_id is not None:
        stmt = stmt.join(Item).where(Item.tenant_id == tenant_id)

    result = await db.execute(stmt.order_by(AuditLog.timestamp.desc()).limit(limit))
    return result.scalars().all()


async def async_update_item(
    db: AsyncSession,
    name: str,
    tenant_id: int,
    new_name: Optional[str] = None,
    threshold: Optional[int] = None,
    user_id: Optional[int] = None,
) -> Item:
    result = await db.execute(
        select(Item).where(Item.name == name, Item.tenant_id == tenant_id)
    )
    item = result.scalars().first()
    if not item:
        raise ValueError("Item not found")

    if new_name:
        item.name = new_name
    if threshold is not None:
        item.threshold = threshold

    await _async_log_action(db, user_id, item, "update", 0)
    await db.commit()
    await db.refresh(item)
    return item


async def async_delete_item(
    db: AsyncSession,
    name: str,
    tenant_id: int,
    user_id: Optional[int] = None,
) -> None:
    result = await db.execute(
        select(Item).where(Item.name == name, Item.tenant_id == tenant_id)
    )
    item = result.scalars().first()
    if not item:
        raise ValueError("Item not found")

    await _async_log_action(db, user_id, item, "delete", 0)
    await db.delete(item)
    await db.commit()
