import agent


def test_build_prompt_contains_integrity_guardrail():
    prompt = agent.build_prompt("### Fake section:\n- x", "2026-11-11")
    assert "UNAVAILABLE" in prompt
    assert "LITERALLY" in prompt


def test_build_prompt_includes_market_data_and_date():
    prompt = agent.build_prompt("SENTINEL_DATA", "2026-11-11")
    assert "SENTINEL_DATA" in prompt
    assert "2026-11-11" in prompt


def test_collect_market_intelligence_prepends_health_block_without_network(monkeypatch):
    import asyncio

    monkeypatch.setattr(agent, "search_saudi_reddit", lambda *a, **k: "### Reddit:\n- x")
    monkeypatch.setattr(agent, "fetch_mostaql_projects", lambda *a, **k: "No projects extracted.")
    monkeypatch.setattr(agent, "fetch_khamsat_unmet_requests", lambda *a, **k: "### Khamsat:\n- y")
    monkeypatch.setattr(agent, "fetch_saudi_google_news", lambda *a, **k: "### News:\n- z")
    monkeypatch.setattr(agent, "search_saudi_google_autocomplete", lambda *a, **k: "### Auto:\n- q")
    monkeypatch.setattr(agent, "fetch_saudi_google_trends", lambda: "### Trending:\n- t")
    monkeypatch.setattr(agent, "search_global_launches_for_saudi_localization", lambda *a, **k: "### HN:\n- h")
    monkeypatch.setattr(agent, "fetch_haraj_consumer_signals", lambda *a, **k: "### Haraj:\n- j")

    class FakeRegistry:
        def collect_all_signals(self):
            return "### Marketplaces:\n- m"

    monkeypatch.setattr(agent, "MarketplaceRegistry", FakeRegistry)

    out = asyncio.run(agent.collect_market_intelligence())
    assert "Source availability" in out
    assert "UNAVAILABLE" in out
