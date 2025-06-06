import os
import tempfile

# Ensure DATABASE_URL points to a temporary SQLite database before importing tasks
fd, path = tempfile.mkstemp(prefix="tasks", suffix=".db")
os.close(fd)
os.environ["DATABASE_URL"] = f"sqlite:///{path}"
import tasks  # noqa: E402


def test_check_stock_levels_invokes_notifications(monkeypatch):
    called = {}

    def fake_check(db):
        called["ran"] = True

    monkeypatch.setattr(tasks, "check_thresholds", fake_check)

    tasks.check_stock_levels()
    assert called.get("ran")
