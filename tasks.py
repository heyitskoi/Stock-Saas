from celery import Celery
from database import SessionLocal
from notifications import check_thresholds

from config import settings

broker_url = settings.celery_broker_url
celery_app = Celery("stock_saas", broker=broker_url)

celery_app.conf.beat_schedule = {
    "check-stock-levels": {
        "task": "tasks.check_stock_levels",
        "schedule": settings.stock_check_interval,
    }
}


@celery_app.task
def check_stock_levels():
    db = SessionLocal()
    try:
        check_thresholds(db)
    finally:
        db.close()
