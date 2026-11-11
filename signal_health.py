"""Pure helpers that turn raw source responses into honest, labelled signal text.

Kept dependency-free and network-free so the daily agent's integrity rules can be
unit-tested in isolation. A failed source must be *visible*, never silently
dropped, because the model will otherwise invent plausible data to fill the gap.
"""

from typing import Any, Mapping

# Injected into the report prompt so the model cannot fabricate content for
# sources that returned nothing today.
INTEGRITY_RULES = """\
DATA INTEGRITY RULES (mandatory, override any other instruction):
- The "Source availability" block above is authoritative. Any source marked
  UNAVAILABLE returned NO data today. State plainly that it was unavailable.
  Do NOT reconstruct, estimate, extrapolate, or invent its content.
- Cite numbers, prices, search-volume/traffic figures and verbatim terms ONLY
  when they appear LITERALLY in the sections below. Never attach a numeric
  volume to a term unless that exact number appears next to that term in the
  data. Never invent foreign-language words as "expat influence".
- If the data is too thin to support a claim, write "insufficient data" instead
  of filling the gap. Do not present inference as a live mined signal.
"""

# Failure markers emitted by the collection functions in agent.py. Checked
# against the head of a section only, so a real signal containing e.g. the word
# "error" further down is not misclassified.
_UNAVAILABLE_MARKERS = (
    "error",
    "returned status code",
    "no active signals",
    "no projects extracted",
    "no unmet requests",
    "no news items",
    "no autocomplete suggestions",
    "no trending items",
    "no items found",
    "fetch error",
    "no signals",
    "all platforms:",
)


def is_available(section: str) -> bool:
    """False when a source returned an error/empty marker instead of real data."""
    if not isinstance(section, str) or not section.strip():
        return False
    head = section.strip()[:200].lower()
    return not any(marker in head for marker in _UNAVAILABLE_MARKERS)


def health_block(sections: Mapping[str, str]) -> str:
    """Renders an explicit per-source availability table for the report prompt."""
    lines = [
        "### Source availability (authoritative - do NOT infer from failed sources)"
    ]
    for name, body in sections.items():
        state = "OK" if is_available(body) else "UNAVAILABLE (no data returned)"
        lines.append(f"- {name}: {state}")
    return "\n".join(lines)


def render_signals(report: Mapping[str, Mapping[str, Any]]) -> str:
    """Renders MarketplaceRegistry.run_health_check() output as signal text."""
    lines = ["### Unified Saudi marketplace signals (12 platforms)"]
    for name, stats in report.items():
        if stats.get("status") == "ONLINE":
            sample = stats.get("sample") or "n/a"
            lines.append(
                f"- [MARKET_SIGNAL] {name}: {stats.get('items_count', 0)} items; "
                f"live sample: {sample}"
            )
        else:
            reason = stats.get("error") or stats.get("status") or "unknown"
            lines.append(f"- [UNAVAILABLE] {name}: {reason}")
    return "\n".join(lines)
