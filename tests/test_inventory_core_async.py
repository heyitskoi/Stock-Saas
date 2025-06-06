import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from models import Base, Tenant
from inventory_core import (
    async_add_item,
    async_issue_item,
    async_return_item,
    async_get_status,
    async_update_item,
    async_delete_item,
)


@pytest_asyncio.fixture
async def adb():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
    async with AsyncSessionLocal() as session:
        tenant = Tenant(name="test")
        session.add(tenant)
        await session.commit()
        await session.refresh(tenant)
        yield session, tenant.id


@pytest.mark.asyncio
async def test_async_add_issue_return(adb):
    session, tenant_id = adb
    item = await async_add_item(session, "widget", 5, threshold=2, tenant_id=tenant_id)
    assert item.available == 5
    item = await async_issue_item(session, "widget", 3, tenant_id=tenant_id)
    assert item.available == 2
    item = await async_return_item(session, "widget", 1, tenant_id=tenant_id)
    status = await async_get_status(session, tenant_id=tenant_id, name="widget")
    assert status["widget"]["available"] == 3


@pytest.mark.asyncio
async def test_async_update_and_delete(adb):
    session, tenant_id = adb
    await async_add_item(session, "phone", 2, threshold=1, tenant_id=tenant_id)
    item = await async_update_item(
        session, "phone", tenant_id, new_name="smartphone", threshold=5
    )
    assert item.name == "smartphone"
    assert item.threshold == 5
    await async_delete_item(session, "smartphone", tenant_id)
    status = await async_get_status(session, tenant_id, name="smartphone")
    assert status == {}
