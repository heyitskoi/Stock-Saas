import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base, Item, Notification
from notifications import check_thresholds


def setup_db():
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    return Session()


def test_notification_logs_created():
    db = setup_db()
    item = Item(name="paper", available=0, in_use=0, threshold=1)
    db.add(item)
    db.commit()

    emails = []
    slacks = []

    def fake_email(msg):
        emails.append(msg)

    def fake_slack(msg):
        slacks.append(msg)

    check_thresholds(db, email_func=fake_email, slack_func=fake_slack)

    assert len(emails) == 1
    assert len(slacks) == 1
    logs = db.query(Notification).all()
    assert len(logs) == 2
    assert all(log.item_id == item.id for log in logs)
