import asyncio
import importlib
from pathlib import Path

import agent
import config

REPO = Path(__file__).resolve().parents[1]


def _stub_sources(monkeypatch, news_result="### Google News Saudi Arabia:\n- [MARKET_NEWS] x"):
    """All collection functions are stubbed so no test ever touches the network."""
    monkeypatch.setattr(agent, "search_saudi_reddit", lambda *a, **k: "### Reddit:\n- x")
    monkeypatch.setattr(agent, "fetch_mostaql_projects", lambda *a, **k: "### Mostaql:\n- x")
    monkeypatch.setattr(agent, "fetch_khamsat_unmet_requests", lambda *a, **k: "### Khamsat:\n- x")
    monkeypatch.setattr(agent, "fetch_saudi_google_news", lambda *a, **k: news_result)
    monkeypatch.setattr(agent, "search_saudi_google_autocomplete", lambda *a, **k: "### Auto:\n- x")
    monkeypatch.setattr(agent, "fetch_saudi_google_trends", lambda: "### Trends:\n- x")
    monkeypatch.setattr(agent, "search_global_launches_for_saudi_localization", lambda *a, **k: "### HN:\n- x")
    monkeypatch.setattr(agent, "fetch_haraj_consumer_signals", lambda *a, **k: "### Haraj:\n- x")

    class FakeRegistry:
        def collect_all_signals(self):
            return "### Marketplaces:\n- x"

    monkeypatch.setattr(agent, "MarketplaceRegistry", FakeRegistry)


def test_google_news_flag_defaults_to_off(monkeypatch):
    monkeypatch.delenv("GOOGLE_NEWS_RSS_ENABLED", raising=False)
    try:
        assert importlib.reload(config).GOOGLE_NEWS_RSS_ENABLED is False
    finally:
        importlib.reload(config)


def test_google_news_flag_accepts_truthy_values(monkeypatch):
    try:
        for value in ("1", "true", "YES", "on"):
            monkeypatch.setenv("GOOGLE_NEWS_RSS_ENABLED", value)
            assert importlib.reload(config).GOOGLE_NEWS_RSS_ENABLED is True
        monkeypatch.setenv("GOOGLE_NEWS_RSS_ENABLED", "false")
        assert importlib.reload(config).GOOGLE_NEWS_RSS_ENABLED is False
    finally:
        monkeypatch.delenv("GOOGLE_NEWS_RSS_ENABLED", raising=False)
        importlib.reload(config)


def test_disabled_news_source_omits_section_and_never_fetches(monkeypatch):
    _stub_sources(monkeypatch)
    calls = []
    monkeypatch.setattr(agent, "fetch_saudi_google_news", lambda *a, **k: calls.append(1) or "### News")
    monkeypatch.setattr(config, "GOOGLE_NEWS_RSS_ENABLED", False)

    out = asyncio.run(agent.collect_market_intelligence())

    assert calls == [], "disabled source must not make a network call"
    assert "Google News" not in out, "disabled source must not appear in the health block"


def test_enabled_news_source_includes_section(monkeypatch):
    _stub_sources(monkeypatch, news_result="### Google News Saudi Arabia:\n- [MARKET_NEWS] متجر سلة")
    monkeypatch.setattr(config, "GOOGLE_NEWS_RSS_ENABLED", True)

    out = asyncio.run(agent.collect_market_intelligence())

    assert "Google News Saudi Arabia: OK" in out
    assert "متجر سلة" in out


def test_license_is_mit_with_correct_holder():
    text = (REPO / "LICENSE").read_text(encoding="utf-8")
    assert "MIT License" in text
    assert "Copyright (c) 2026 Badr Bajamil" in text
    assert "Permission is hereby granted, free of charge" in text
    assert "THE SOFTWARE IS PROVIDED" in text


def test_env_example_documents_news_flag():
    text = (REPO / ".env.example").read_text(encoding="utf-8")
    assert "GOOGLE_NEWS_RSS_ENABLED" in text
    assert "non-commercial" in text.lower()


def test_readme_warns_about_news_tos():
    text = (REPO / "README.md").read_text(encoding="utf-8")
    assert "GOOGLE_NEWS_RSS_ENABLED" in text
    assert "non-commercial" in text.lower()
