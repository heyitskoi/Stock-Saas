import os
import smtplib
from email.message import EmailMessage
from typing import Callable

import httpx
from sqlalchemy.orm import Session

from models import Item, Notification


def _send_email(message: str) -> None:
    smtp_server = os.getenv("SMTP_SERVER")
    recipient = os.getenv("ALERT_EMAIL_TO")
    sender = os.getenv("ALERT_EMAIL_FROM", "noreply@example.com")
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
    webhook = os.getenv("SLACK_WEBHOOK_URL")
    if webhook:
        httpx.post(webhook, json={"text": message})


def record_notification(db: Session, item: Item, message: str, channel: str) -> None:
    entry = Notification(item_id=item.id, message=message, channel=channel)
    db.add(entry)


def check_thresholds(
    db: Session,
    email_func: Callable[[str], None] | None = _send_email,
    slack_func: Callable[[str], None] | None = _send_slack,
) -> None:
    low_items = (
        db.query(Item).filter(Item.threshold > 0, Item.available < Item.threshold).all()
    )
    for item in low_items:
        text = f"Item '{item.name}' is below threshold: {item.available} < {item.threshold}"
        if email_func:
            email_func(text)
            record_notification(db, item, text, "email")
        if slack_func:
            slack_func(text)
            record_notification(db, item, text, "slack")
    if low_items:
        db.commit()
