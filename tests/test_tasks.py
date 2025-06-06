import os
import tempfile
from importlib import reload

import pytest

# Ensure DATABASE_URL points to a temporary SQLite database before importing tasks
fd, path = tempfile.mkstemp(prefix='tasks', suffix='.db')
os.close(fd)
os.environ['DATABASE_URL'] = f'sqlite:///{path}'
from tasks import check_stock_levels, check_thresholds
import tasks


def test_check_stock_levels_invokes_notifications(monkeypatch):
    called = {}

    def fake_check(db):
        called['ran'] = True
    monkeypatch.setattr(tasks, 'check_thresholds', fake_check)

    check_stock_levels()
    assert called.get('ran')
