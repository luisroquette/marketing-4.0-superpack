# tools/export-status/tests/test_cockpit_smoke.py
"""Structural smoke tests for the static cockpit page."""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


def test_cockpit_fetches_status_json():
    html = (REPO_ROOT / "cockpit" / "index.html").read_text(encoding="utf-8")
    assert "status.json" in html


def test_cockpit_has_four_stage_containers():
    html = (REPO_ROOT / "cockpit" / "index.html").read_text(encoding="utf-8")
    for stage in ("atrair", "converter", "nutrir", "medir"):
        assert f'id="stage-{stage}"' in html


def test_cockpit_has_empty_state():
    html = (REPO_ROOT / "cockpit" / "index.html").read_text(encoding="utf-8")
    assert 'id="empty-state"' in html


def test_cockpit_falls_back_to_empty_state_on_load_failure():
    js = (REPO_ROOT / "cockpit" / "app.js").read_text(encoding="utf-8")
    assert "catch" in js
