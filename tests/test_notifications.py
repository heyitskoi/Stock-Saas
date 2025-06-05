import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base, Item, Notification, User
from notifications import check_thresholds


def setup_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    return Session()


def test_notification_logs_created():
    db = setup_db()
    item = Item(name="paper", available=0, in_use=0, threshold=1)
    db.add(item)
    db.commit()

    db.add_all([
        User(username="e1@example.com", hashed_password="x", tenant_id=1, notification_preference="email"),
        User(username="s1@example.com", hashed_password="x", tenant_id=1, notification_preference="slack"),
    ])
    db.commit()

    emails: list[str] = []
    slacks: list[str] = []

    def fake_email(msg, to=None):
        emails.append(to or "")

    def fake_slack(msg):
        slacks.append(msg)

    check_thresholds(db, email_func=fake_email, slack_func=fake_slack)

    assert len(emails) == 1
    assert len(slacks) == 1
    logs = db.query(Notification).all()
    assert len(logs) == 2
    assert all(log.item_id == item.id for log in logs)
