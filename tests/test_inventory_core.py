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
    transfer_item,
    get_item_history,
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
    item = add_item(
        session,
        "widget",
        5,
        threshold=2,
        min_par=3,
        department_id=1,
        category_id=2,
        stock_code="ABC",
        status="active",
        tenant_id=tenant_id,
    )
    assert item.min_par == 3
    assert item.department_id == 1
    assert item.category_id == 2
    assert item.stock_code == "ABC"
    assert item.status == "active"
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
        session,
        "phone",
        tenant_id=tenant_id,
        new_name="smartphone",
        threshold=5,
        min_par=4,
        department_id=2,
        category_id=3,
        stock_code="XYZ",
        status="inactive",
    )
    assert item.name == "smartphone"
    assert item.threshold == 5
    assert item.min_par == 4
    assert item.department_id == 2
    assert item.category_id == 3
    assert item.stock_code == "XYZ"
    assert item.status == "inactive"

    delete_item(session, "smartphone", tenant_id=tenant_id)
    status = get_status(session, tenant_id=tenant_id, name="smartphone")
    assert status == {}


def test_transfer_between_tenants(db):
    session, tenant_id = db
    dest = Tenant(name="dest")
    session.add(dest)
    session.commit()
    add_item(session, "widget", 5, threshold=0, tenant_id=tenant_id)
    from_item, to_item = transfer_item(
        session, "widget", 2, from_tenant_id=tenant_id, to_tenant_id=dest.id
    )
    assert from_item.available == 3
    assert to_item.available == 2
    history = get_item_history(session, "widget", tenant_id)
    assert history[0].action == "transfer"


def test_update_item_validation_and_log(db):
    session, tenant_id = db
    add_item(session, "widget", 1, threshold=1, tenant_id=tenant_id)

    with pytest.raises(ValueError):
        update_item(session, "widget", tenant_id=tenant_id, min_par=-1)

    item = update_item(
        session,
        "widget",
        tenant_id=tenant_id,
        min_par=2,
        status="active",
    )

    assert item.min_par == 2
    assert item.status == "active"

    history = get_item_history(session, "widget", tenant_id)
    updates = [log.action for log in history].count("update")
    assert updates == 1
