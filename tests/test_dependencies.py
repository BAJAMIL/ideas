import ast
import configparser
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

# Top-level import name -> distribution name on PyPI.
DIST = {
    "bs4": "beautifulsoup4",
    "dotenv": "python-dotenv",
    "httpx": "httpx",
}

SCANNED = ["agent.py", "marketplace_registry.py"] + [
    p.name for p in sorted(REPO.glob("*_client.py"))
]


def _declared_packages():
    declared = set()
    for line in (REPO / "requirements.txt").read_text(encoding="utf-8").splitlines():
        line = line.split("#")[0].strip()
        if not line or line.startswith("-"):
            continue
        name = re.split(r"[<>=!~\[]", line)[0].strip().lower().replace("_", "-")
        declared.add(name)
    return declared


def _eager_third_party_imports():
    local = {p.stem for p in REPO.glob("*.py")}
    stdlib = set(sys.stdlib_module_names)
    found = set()
    for filename in SCANNED:
        tree = ast.parse((REPO / filename).read_text(encoding="utf-8"))
        # Module-level statements only: lazy imports inside functions are optional
        # and do not break `import agent` in CI.
        for node in tree.body:
            names = []
            if isinstance(node, ast.Import):
                names = [a.name.split(".")[0] for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                names = [node.module.split(".")[0]]
            for mod in names:
                if mod in stdlib or mod in local:
                    continue
                found.add(DIST.get(mod, mod))
    return found


def test_requirements_declare_all_eager_third_party_imports():
    missing = {
        pkg.lower().replace("_", "-")
        for pkg in _eager_third_party_imports()
    } - _declared_packages()
    assert missing == set(), f"undeclared third-party imports: {sorted(missing)}"


def test_pytest_only_collects_tests_package():
    cfg = configparser.ConfigParser()
    cfg.read(REPO / "pytest.ini")
    assert cfg.get("pytest", "testpaths").split() == ["tests"]


def test_tests_package_is_not_gitignored():
    """The root `.gitignore` has `test_*.py`; the real suite must be exempt."""
    import subprocess

    result = subprocess.run(
        ["git", "check-ignore", "-q", "tests/test_agent.py"],
        cwd=REPO,
        capture_output=True,
    )
    assert result.returncode != 0, "tests/test_*.py is gitignored and would never reach CI"
