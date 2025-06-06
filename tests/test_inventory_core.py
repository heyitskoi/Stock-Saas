import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base, Tenant
from inventory_core import (
    add_item,
    issue_item,
    return_item,
    get_status,
    update_item,
    delete_item,
)


@pytest.fixture
def db():
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    tenant = Tenant(name="test")
    session.add(tenant)
    session.commit()
    try:
        yield session, tenant.id
    finally:
        session.close()


def test_add_issue_return(db):
    session, tenant_id = db
    item = add_item(session, "widget", 5, threshold=2, tenant_id=tenant_id)
    assert item.available == 5
    assert item.in_use == 0

    item = issue_item(session, "widget", 3, tenant_id=tenant_id)
    assert item.available == 2
    assert item.in_use == 3

    item = return_item(session, "widget", 1, tenant_id=tenant_id)
    assert item.available == 3
    assert item.in_use == 2

    status = get_status(session, tenant_id=tenant_id, name="widget")
    assert status["widget"]["available"] == 3


def test_issue_insufficient_stock(db):
    session, tenant_id = db
    add_item(session, "laptop", 1, threshold=0, tenant_id=tenant_id)
    with pytest.raises(ValueError):
        issue_item(session, "laptop", 2, tenant_id=tenant_id)


def test_negative_quantity(db):
    session, tenant_id = db
    with pytest.raises(ValueError):
        add_item(session, "bad", -1, threshold=0, tenant_id=tenant_id)
    add_item(session, "good", 1, threshold=0, tenant_id=tenant_id)
    with pytest.raises(ValueError):
        issue_item(session, "good", -2, tenant_id=tenant_id)
    with pytest.raises(ValueError):
        return_item(session, "good", -1, tenant_id=tenant_id)


def test_update_and_delete(db):
    session, tenant_id = db
    add_item(session, "phone", 2, threshold=1, tenant_id=tenant_id)
    item = update_item(
        session, "phone", tenant_id=tenant_id, new_name="smartphone", threshold=5
    )
    assert item.name == "smartphone"
    assert item.threshold == 5

    delete_item(session, "smartphone", tenant_id=tenant_id)
    status = get_status(session, tenant_id=tenant_id, name="smartphone")
    assert status == {}
