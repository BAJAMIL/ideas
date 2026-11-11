import importlib
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
KEY_LITERAL = re.compile(r"haraj_server_\d+")


def test_haraj_key_literal_defined_only_in_config():
    offenders = []
    for path in REPO.rglob("*.py"):
        parts = set(path.parts)
        if parts & {"tests", "docs", ".venv", "__pycache__"}:
            continue
        if path.name == "config.py":
            continue
        if KEY_LITERAL.search(path.read_text(encoding="utf-8", errors="ignore")):
            offenders.append(str(path.relative_to(REPO)))
    assert offenders == [], f"haraj key literal still duplicated in: {offenders}"


def test_haraj_key_reads_from_environment(monkeypatch):
    import config

    monkeypatch.setenv("HARAJ_SERVER_KEY", "rotated_value")
    try:
        assert importlib.reload(config).HARAJ_SERVER_KEY == "rotated_value"
    finally:
        monkeypatch.delenv("HARAJ_SERVER_KEY", raising=False)
        importlib.reload(config)


def test_env_example_lists_all_required_secrets():
    text = (REPO / ".env.example").read_text(encoding="utf-8")
    for key in ("OPENROUTER_API_KEY", "GEMINI_API_KEY", "HARAJ_SERVER_KEY"):
        assert key in text
