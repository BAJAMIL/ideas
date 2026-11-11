import marketplace_registry as mr


def test_registry_exposes_collect_all_signals():
    assert callable(getattr(mr.MarketplaceRegistry, "collect_all_signals", None))


def test_collect_all_signals_renders_all_platforms_without_network(monkeypatch):
    reg = object.__new__(mr.MarketplaceRegistry)
    monkeypatch.setattr(reg, "run_health_check", lambda: {
        "Haraj": {"status": "ONLINE", "items_count": 3, "sample": "RTX 3060"},
        "Aqar": {"status": "ERROR", "error": "403"},
    })
    out = reg.collect_all_signals()
    assert "Haraj" in out
    assert "Aqar" in out
    assert "UNAVAILABLE" in out


def test_collect_all_signals_never_raises(monkeypatch):
    reg = object.__new__(mr.MarketplaceRegistry)

    def boom():
        raise RuntimeError("all sources down")

    monkeypatch.setattr(reg, "run_health_check", boom)
    assert isinstance(reg.collect_all_signals(), str)
