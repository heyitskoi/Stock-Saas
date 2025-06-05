import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base
from inventory_core import add_item, issue_item, return_item, get_status


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_add_issue_return(db):
    item = add_item(db, "widget", 5, threshold=2)
    assert item.available == 5
    assert item.in_use == 0

    item = issue_item(db, "widget", 3)
    assert item.available == 2
    assert item.in_use == 3

    item = return_item(db, "widget", 1)
    assert item.available == 3
    assert item.in_use == 2

    status = get_status(db, "widget")
    assert status["widget"]["available"] == 3


def test_issue_insufficient_stock(db):
    add_item(db, "laptop", 1, threshold=0)
    with pytest.raises(ValueError):
        issue_item(db, "laptop", 2)
