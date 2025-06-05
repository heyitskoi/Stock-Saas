import factory
from factory.alchemy import SQLAlchemyModelFactory
from datetime import datetime

from database import SessionLocal
from models import User, Item, AuditLog
from auth import get_password_hash

# Use a dedicated session for factory-created objects
_session = SessionLocal()


class BaseFactory(SQLAlchemyModelFactory):
    class Meta:
        abstract = True
        sqlalchemy_session = _session
        sqlalchemy_session_persistence = "commit"


class UserFactory(BaseFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    role = "user"
    notification_preference = "email"

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        password = kwargs.pop("password", "password")
        kwargs["hashed_password"] = get_password_hash(password)
        return super()._create(model_class, *args, **kwargs)


class ItemFactory(BaseFactory):
    class Meta:
        model = Item

    name = factory.Sequence(lambda n: f"item{n}")
    available = 0
    in_use = 0
    threshold = 0


class AuditLogFactory(BaseFactory):
    class Meta:
        model = AuditLog

    user = factory.SubFactory(UserFactory)
    item = factory.SubFactory(ItemFactory)
    action = "add"
    quantity = 1
    timestamp = factory.LazyFunction(datetime.utcnow)
