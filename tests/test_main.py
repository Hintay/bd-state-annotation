import pytest
import main as m

def test_dispatch_maps_known_tasks():
    assert set(m.TASKS) == {"single", "trend", "verify", "deid"}

def test_dispatch_calls_selected_runner(monkeypatch):
    called = {}
    monkeypatch.setitem(m.TASKS, "single", lambda: called.setdefault("single", True))
    m.dispatch("single")
    assert called["single"] is True

def test_dispatch_rejects_unknown_task():
    with pytest.raises(SystemExit):
        m.dispatch("bogus")
