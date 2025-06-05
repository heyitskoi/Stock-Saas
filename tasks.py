import os
from celery import Celery
from database import SessionLocal
from notifications import check_thresholds

broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
celery_app = Celery("stock_saas", broker=broker_url)

celery_app.conf.beat_schedule = {
    "check-stock-levels": {
        "task": "tasks.check_stock_levels",
        "schedule": int(os.getenv("STOCK_CHECK_INTERVAL", 3600)),
    }
}

@celery_app.task
def check_stock_levels():
    db = SessionLocal()
    try:
        check_thresholds(db)
    finally:
        db.close()
