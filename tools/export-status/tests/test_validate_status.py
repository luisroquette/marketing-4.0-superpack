# tools/export-status/tests/test_validate_status.py
"""Tests for the status.json contract validator."""

from validate_status import validate


def _status(**overrides):
    base = {
        "schemaVersion": 1,
        "client": {"slug": "coesa", "name": "COESA"},
        "generatedAt": "2026-08-20T10:00:00Z",
        "stages": {
            "atrair": {"deliverables": [], "count": 0, "firstPublishedAt": None},
            "converter": {"deliverables": [], "count": 0, "firstPublishedAt": None},
            "nutrir": {"deliverables": [], "count": 0, "firstSentAt": None},
            "medir": {"deliverables": [], "count": 0},
        },
    }
    base.update(overrides)
    return base


def test_empty_status_is_valid():
    assert validate(_status()) == []


def test_full_status_is_valid():
    full = _status()
    full["stages"]["atrair"] = {
        "deliverables": [
            {"type": "blog-post", "title": "Energy outlook", "publishedAt": "2026-08-01T09:00:00Z"}
        ],
        "count": 1,
        "firstPublishedAt": "2026-08-01T09:00:00Z",
    }
    assert validate(full) == []


def test_count_mismatch_is_invalid():
    s = _status()
    s["stages"]["atrair"] = {"deliverables": [], "count": 3, "firstPublishedAt": None}
    assert any("count" in e for e in validate(s))


def test_missing_stage_is_invalid():
    s = _status()
    del s["stages"]["medir"]
    assert any("missing stage: medir" in e for e in validate(s))


def test_bad_timestamp_is_invalid():
    s = _status()
    s["generatedAt"] = "ontem"
    assert any("generatedAt" in e for e in validate(s))


def test_non_object_is_invalid():
    assert validate([]) != []
