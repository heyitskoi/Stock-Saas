from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base, Item, Notification, User
from notifications import check_thresholds
from websocket_manager import InventoryWSManager


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

    db.add_all(
        [
            User(
                username="e1@example.com",
                hashed_password="x",
                tenant_id=1,
                notification_preference="email",
            ),
            User(
                username="s1@example.com",
                hashed_password="x",
                tenant_id=1,
                notification_preference="slack",
            ),
            User(
                username="n1@example.com",
                hashed_password="x",
                tenant_id=1,
                notification_preference="none",
            ),
        ]
    )
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


def test_no_notifications_when_stock_ok():
    db = setup_db()
    item = Item(name="stapler", available=5, in_use=0, threshold=2)
    db.add(item)
    db.commit()

    emails = []
    slacks = []

    check_thresholds(db, email_func=emails.append, slack_func=slacks.append)

    assert emails == []
    assert slacks == []
    assert db.query(Notification).count() == 0


def test_websocket_broadcast_on_low_stock():
    db = setup_db()
    item = Item(name="ws", available=0, in_use=0, threshold=1, tenant_id=1)
    db.add(item)
    db.commit()

    ws_mgr = InventoryWSManager()
    received = []

    async def fake_broadcast(tid, data):
        received.append((tid, data))

    ws_mgr.broadcast = fake_broadcast

    check_thresholds(db, email_func=None, slack_func=None, ws_manager=ws_mgr)

    assert received
    tid, data = received[0]
    assert tid == 1
    assert data["event"] == "low_stock"
