import smtplib
from email.message import EmailMessage
from typing import Callable
import asyncio

from websocket_manager import InventoryWSManager

import httpx
from sqlalchemy.orm import Session

from models import Item, Notification, User
from config import settings


def _send_email(message: str, recipient: str | None = None) -> None:
    smtp_server = settings.smtp_server
    recipient = recipient or settings.alert_email_to
    sender = settings.alert_email_from
    if not (smtp_server and recipient):
        return
    msg = EmailMessage()
    msg["Subject"] = "Low stock alert"
    msg["From"] = sender
    msg["To"] = recipient
    msg.set_content(message)
    with smtplib.SMTP(smtp_server) as server:
        server.send_message(msg)


def _send_slack(message: str) -> None:
    webhook = settings.slack_webhook_url
    if webhook:
        httpx.post(webhook, json={"text": message})


def record_notification(db: Session, item: Item, message: str, channel: str) -> None:
    entry = Notification(item_id=item.id, message=message, channel=channel)
    db.add(entry)


def check_thresholds(
    db: Session,
    email_func: Callable[[str, str | None], None] | None = _send_email,
    slack_func: Callable[[str], None] | None = _send_slack,
    ws_manager: InventoryWSManager | None = None,
) -> None:
    low_items = (
        db.query(Item).filter(Item.threshold > 0, Item.available < Item.threshold).all()
    )
    if not low_items:
        return

    users = db.query(User).all()
    for item in low_items:
        text = (
            f"Item '{item.name}' is below threshold: {item.available} < "
            f"{item.threshold}"
        )
        if users:
            for u in users:
                if u.notification_preference == "email" and email_func:
                    email_func(text, u.username)
                    record_notification(db, item, text, "email")
                elif u.notification_preference == "slack" and slack_func:
                    slack_func(text)
                    record_notification(db, item, text, "slack")
                elif u.notification_preference == "none":
                    pass
        else:
            if email_func:
                email_func(text, None)
                record_notification(db, item, text, "email")
            if slack_func:
                slack_func(text)
                record_notification(db, item, text, "slack")
        if ws_manager:
            payload = {
                "event": "low_stock",
                "item": item.name,
                "available": item.available,
                "threshold": item.threshold,
            }
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(ws_manager.broadcast(item.tenant_id, payload))
            except RuntimeError:
                loop = asyncio.new_event_loop()
                loop.run_until_complete(ws_manager.broadcast(item.tenant_id, payload))
                loop.close()
    db.commit()
