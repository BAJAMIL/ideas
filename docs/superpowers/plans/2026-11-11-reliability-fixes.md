# Reliability & Integrity Fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix the five verified code-level defects from the 2026-11-11 project audit, each pinned by a failing test.

**Architecture:** Pure helpers go in two small new modules (`signal_health.py`, `config.py`) so they can be unit-tested without network or credentials. Real behaviour changes are thin adapters in existing files. A `tests/` package with `pytest.ini` replaces the misleading root-level `test_*.py` recon scripts as the test suite, without deleting them.

**Tech Stack:** Python 3.12 (verified at `C:\Users\badrf\AppData\Local\Programs\Python\Python312\python.exe`), pytest 9.1.0, httpx, python-dotenv, beautifulsoup4.

**Spec:** `DATA_EXPANSION_STUDY.md` (audit context) and the verified defect list in the 2026-11-11 project rating.

## Global Constraints

- No network calls in tests. Ever. All I/O is stubbed.
- Do NOT delete or rename the ~23 existing root-level `test_*.py` recon scripts — they are user work.
- Do NOT commit, push, or open a PR unless explicitly asked.
- Do NOT add a LICENSE (a legal choice for the owner to make) — report it as remaining.
- `HARAJ_SERVER_KEY` env var is the single rotation point; the shipped default is a public client-side key, not a private secret.
- Do not change report output format for the daily cron beyond adding explicit UNAVAILABLE markers.
- Preserve `run_health_check()` exactly as-is; `collect_all_signals()` is an adapter over it.

## Review Focus

1. **All 12 platforms raise** → `collect_all_signals()` must still return a string, never raise. Test: `test_collect_all_signals_never_raises`.
2. **A source returns an empty string or an "Error ..." marker** → it must be labelled UNAVAILABLE, not silently dropped. Test: `test_health_block_marks_unavailable_sources`.
3. **`run_health_check()` returns a platform with `items_count: 0` and `sample: None`** → rendered as a signal with `n/a`, not a crash. Test: `test_render_signals_handles_empty_sample`.
4. **A `*_client.py` gains a new third-party import** → CI must fail. Test: `test_requirements_declare_all_third_party_imports`.
5. **The prompt is built with thin data** → it must still contain the anti-fabrication guardrail. Test: `test_build_prompt_contains_integrity_guardrail`.

---

### Task 1: Pure signal-integrity helpers

**Files:**
- Create: `signal_health.py`
- Test: `tests/test_signal_health.py`

**Interfaces:**
- Produces: `is_available(section: str) -> bool`, `health_block(sections: dict[str, str]) -> str`, `render_signals(report: dict[str, Any]) -> str`, `INTEGRITY_RULES: str` (module constant).

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_signal_health.py
from signal_health import is_available, health_block, render_signals, INTEGRITY_RULES

def test_is_available_false_for_error_marker():
    assert is_available("Error fetching Mostaql projects: timeout") is False

def test_is_available_true_for_real_section():
    assert is_available("### Mostaql Paid Demands:\n- [PAID_DEMAND] build a store") is True

def test_health_block_marks_unavailable_sources():
    block = health_block({"Reddit": "Error fetching Reddit: 403", "Trends": "### Trending:\n- x"})
    assert "Reddit: UNAVAILABLE" in block
    assert "Trends: OK" in block

def test_render_signals_handles_empty_sample():
    out = render_signals({"Aqar": {"status": "ONLINE", "items_count": 0, "sample": None}})
    assert "n/a" in out and "Aqar" in out

def test_render_signals_marks_error_platform_unavailable():
    out = render_signals({"Haraj": {"status": "ERROR", "error": "timeout"}})
    assert "UNAVAILABLE" in out and "timeout" in out

def test_integrity_rules_forbid_invented_numbers():
    assert "UNAVAILABLE" in INTEGRITY_RULES and "LITERALLY" in INTEGRITY_RULES
```

- [ ] **Step 2: Run test to verify it fails**

Run: `& $PY -m pytest tests/test_signal_health.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'signal_health'`

- [ ] **Step 3: Implement `signal_health.py`**

Four pure units. `is_available` returns `False` for empty/whitespace or when the first 200 chars (lowercased) contain any of: `error`, `returned status code`, `no active signals`, `no projects extracted`, `no unmet requests`, `no news items`, `no autocomplete suggestions`, `no trending items`, `no items found`, `fetch error`. `health_block` emits one `- <name>: OK|UNAVAILABLE (no data returned)` line per entry under the heading `### Source availability (authoritative - do NOT infer from failed sources)`. `render_signals` emits `### Unified Saudi marketplace signals` then one line per platform: ONLINE → `- [MARKET_SIGNAL] {name}: {items_count} items; live sample: {sample or 'n/a'}`, else → `- [UNAVAILABLE] {name}: {error or status}`. `INTEGRITY_RULES` is the guardrail text forbidding reconstruction of failed sources, requiring literal citation of numbers/terms, forbidding invented foreign-language terms, and requiring "insufficient data" when thin.

- [ ] **Step 4: Run test to verify it passes**

Run: `& $PY -m pytest tests/test_signal_health.py -q`
Expected: 6 passed

- [ ] **Step 5: Commit** *(deferred — user has not asked for commits)*

---

### Task 2: Restore the 12-platform pipeline (`collect_all_signals`)

**Files:**
- Modify: `marketplace_registry.py` (add method + import)
- Modify: `agent.py:508-515` (label sections, prepend health block)
- Test: `tests/test_registry.py`, `tests/test_agent.py`

**Interfaces:**
- Consumes: `render_signals` from Task 1; existing `MarketplaceRegistry.run_health_check() -> dict`.
- Produces: `MarketplaceRegistry.collect_all_signals() -> str`; `build_prompt(market_data: str, today_str: str) -> str` in `agent.py`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_registry.py
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
    assert "Haraj" in out and "Aqar" in out and "UNAVAILABLE" in out

def test_collect_all_signals_never_raises(monkeypatch):
    reg = object.__new__(mr.MarketplaceRegistry)
    def boom(): raise RuntimeError("all sources down")
    monkeypatch.setattr(reg, "run_health_check", boom)
    assert isinstance(reg.collect_all_signals(), str)
```

```python
# tests/test_agent.py
import agent

def test_build_prompt_contains_integrity_guardrail():
    p = agent.build_prompt("### Fake:\n- x", "2026-11-11")
    assert "UNAVAILABLE" in p and "LITERALLY" in p

def test_build_prompt_includes_market_data_and_date():
    p = agent.build_prompt("SENTINEL_DATA", "2026-11-11")
    assert "SENTINEL_DATA" in p and "2026-11-11" in p
```

- [ ] **Step 2: Run to verify both fail**

Run: `& $PY -m pytest tests/test_registry.py tests/test_agent.py -q`
Expected: FAIL — `collect_all_signals` absent, `build_prompt` absent. (Installing `beautifulsoup4` locally first is required so imports resolve; see Global Constraints note below.)

- [ ] **Step 3: Implement**

`marketplace_registry.py`: `from signal_health import render_signals`; add method:
```python
def collect_all_signals(self) -> str:
    try:
        return render_signals(self.run_health_check())
    except Exception as exc:
        return f"### Unified Saudi marketplace signals\n- [UNAVAILABLE] all platforms: {exc}"
```
`agent.py`: replace `signals = []` with `sections: dict[str, str] = {}`; give each append a stable key (e.g. `sections["Reddit / r/saudiarabia"] = ...`); at the end return `"\n\n".join([health_block(sections), *sections.values()])`. Extract the existing `prompt = f"""..."""` into `def build_prompt(market_data: str, today_str: str) -> str:` returning the same text plus `INTEGRITY_RULES`. Do not alter the report-writing steps.

- [ ] **Step 4: Run to verify they pass**

Run: `& $PY -m pytest tests/test_registry.py tests/test_agent.py -q`
Expected: 5 passed

- [ ] **Step 5: Commit** *(deferred)*

---

### Task 3: Dependency declaration + real test suite wiring

**Files:**
- Modify: `requirements.txt`
- Create: `pytest.ini`, `tests/__init__.py`, `tests/test_dependencies.py`
- Modify: `.github/workflows/daily-ideas.yml` (add CI test gate; fix misleading cron comment)
- Test: `tests/test_dependencies.py`

**Interfaces:**
- Produces: `pytest.ini` with `testpaths = tests`; `requirements.txt` declaring `beautifulsoup4>=4.12.0`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_dependencies.py
def test_requirements_declare_all_third_party_imports():
    # ast-walk *_client.py, agent.py, marketplace_registry.py; map bs4->beautifulsoup4,
    # dotenv->python-dotenv, httpx->httpx, google->google-antigravity; skip stdlib +
    # local modules; assert declared set covers imported set.
    ...
    assert missing == set(), f"undeclared third-party imports: {missing}"

def test_pytest_only_collects_tests_package(capsys):
    # pytest.ini must pin testpaths = tests
    ...
```

- [ ] **Step 2: Run to verify it fails**

Run: `& $PY -m pytest tests/test_dependencies.py -q`
Expected: FAIL with `undeclared third-party imports: {'beautifulsoup4'}`

- [ ] **Step 3: Implement**

Add `beautifulsoup4>=4.12.0` to `requirements.txt`. Create `pytest.ini`:
```ini
[pytest]
testpaths = tests
python_files = test_*.py
addopts = -q
```
Add CI step to `daily-ideas.yml` before the agent run:
```yaml
      - name: Verify (import smoke + unit tests)
        if: github.event_name != 'push'
        run: |
          python -c "import agent"
          python -m pytest
```
Fix the cron comment to state the single configured schedule `30 1 * * *` = 01:30 UTC = 04:30 AST (the current comment claims two crons and 09:30 AST).

- [ ] **Step 4: Run to verify it passes**

Run: `& $PY -m pytest tests/test_dependencies.py -q`
Expected: 2 passed

- [ ] **Step 5: Commit** *(deferred)*

---

### Task 4: Credential centralisation + `.env.example`

**Files:**
- Create: `config.py`, `.env.example`
- Modify: `haraj_client.py` + the 19 root recon scripts that contain the literal
- Test: `tests/test_secrets.py`

**Interfaces:**
- Produces: `config.HARAJ_SERVER_KEY` (`os.environ.get("HARAJ_SERVER_KEY", <default>)`).

- [ ] **Step 1: Write the failing test**

```python
# tests/test_secrets.py
def test_haraj_key_defined_only_in_config():
    # walk repo *.py, find files containing the literal key; assert <= 1 and it is config.py
    ...

def test_haraj_key_reads_from_environment(monkeypatch):
    import importlib, config
    monkeypatch.setenv("HARAJ_SERVER_KEY", "rotated_value")
    assert importlib.reload(config).HARAJ_SERVER_KEY == "rotated_value"
```

- [ ] **Step 2: Run to verify it fails**

Run: `& $PY -m pytest tests/test_secrets.py -q`
Expected: FAIL — literal present in 20 files

- [ ] **Step 3: Implement**

Create `config.py` with the single default and env override, plus a comment stating it is a public client-side key and that rotation is via `HARAJ_SERVER_KEY`. Replace the literal in the 19 recon scripts and `haraj_client.py` with `HARAJ_SERVER_KEY`, inserting `from config import HARAJ_SERVER_KEY` before each file's first import statement. Create `.env.example` with `OPENROUTER_API_KEY=`, `GEMINI_API_KEY=`, `HARAJ_SERVER_KEY=`.

- [ ] **Step 4: Run to verify it passes**

Run: `& $PY -m pytest tests/test_secrets.py -q`
Expected: 2 passed

- [ ] **Step 5: Commit** *(deferred)*

---

### Task 5: Documentation drift

**Files:**
- Modify: `README.md`

- [ ] **Step 1:** Correct line 3 + line 10: OpenRouter free models are the primary engine, Google Antigravity SDK is the fallback; note both.
- [ ] **Step 2:** Correct line 9: the configured cron is `30 1 * * *` = 01:30 UTC / 04:30 AST (not 05:00 UTC / 08:00 AST).
- [ ] **Step 3:** Rewrite Setup: `OPENROUTER_API_KEY` is the primary secret; `GEMINI_API_KEY` activates the Antigravity fallback; add `HARAJ_SERVER_KEY` note.
- [ ] **Step 4:** Add a "Development / Verification" section: `pip install -r requirements.txt`, `python -m pytest`, `python -c "import agent"`; state that root `test_*.py` are recon scripts, not tests.
- [ ] **Step 5:** Verify README contains no `05:00 UTC`, no `08:00 AM Riyadh`, and mentions `OPENROUTER_API_KEY`.

---

### Final Verification (verification-before-completion)

- [ ] `& $PY -m pytest` — full suite, 0 failures
- [ ] `& $PY -c "import agent; print('OK')"` — import smoke
- [ ] `& $PY -m pytest --collect-only -q` — confirms only `tests/` collected (no root recon scripts fire network calls)
- [ ] `git diff --check`
- [ ] `git status --short`
- [ ] Re-read every defect from the audit and state, per defect, whether it is fixed or remains (LICENSE, key rotation, product-level items remain).

> **Global note:** `beautifulsoup4` must be installed into the local Python 3.12 env (environment setup, not production code) before Step 2 of Task 2, so that `import agent` resolves and tests fail for the intended reason rather than `ModuleNotFoundError`.
