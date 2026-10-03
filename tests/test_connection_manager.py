from src.adapters.connection_manager import ConnectionManager

def test_connection_manager_does_not_expose_secret_values(monkeypatch):
    monkeypatch.setenv("CJ_API_KEY", "super-secret")
    summary = ConnectionManager().summary()
    cj = next(item for item in summary if item["adapter"] == "cj_dropshipping")
    assert cj["status"] == "CONFIGURED"
    assert "super-secret" not in str(cj)
    assert cj["credential"] == "CJ_API_KEY"

def test_connection_manager_reports_missing_configuration(monkeypatch):
    monkeypatch.delenv("CJ_API_KEY", raising=False)
    summary = ConnectionManager().summary()
    cj = next(item for item in summary if item["adapter"] == "cj_dropshipping")
    assert cj["status"] == "NOT_CONFIGURED"
