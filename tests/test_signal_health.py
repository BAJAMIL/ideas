from signal_health import is_available, health_block, render_signals, INTEGRITY_RULES


def test_is_available_false_for_error_marker():
    assert is_available("Error fetching Mostaql projects: timeout") is False


def test_is_available_false_for_empty_string():
    assert is_available("   ") is False


def test_is_available_true_for_real_section():
    assert is_available("### Mostaql Paid Demands:\n- [PAID_DEMAND] build a store") is True


def test_health_block_marks_unavailable_sources():
    block = health_block({"Reddit": "Error fetching Reddit: 403", "Trends": "### Trending:\n- x"})
    assert "Reddit: UNAVAILABLE" in block
    assert "Trends: OK" in block


def test_render_signals_handles_empty_sample():
    out = render_signals({"Aqar": {"status": "ONLINE", "items_count": 0, "sample": None}})
    assert "n/a" in out
    assert "Aqar" in out


def test_render_signals_marks_error_platform_unavailable():
    out = render_signals({"Haraj": {"status": "ERROR", "error": "timeout"}})
    assert "UNAVAILABLE" in out
    assert "timeout" in out


def test_integrity_rules_forbid_invented_numbers():
    assert "UNAVAILABLE" in INTEGRITY_RULES
    assert "LITERALLY" in INTEGRITY_RULES


def test_is_available_false_when_all_marketplaces_fail():
    """The registry's total-failure fallback must not be mistaken for data."""
    section = (
        "### Unified Saudi marketplace signals (12 platforms)\n"
        "- [UNAVAILABLE] all platforms: boom"
    )
    assert is_available(section) is False
