# tests/test_readme_gate.py
"""Gate tests: the README must name the runtime and the single start flow."""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_readme_names_claude_code_early():
    lines = (REPO_ROOT / "README.md").read_text(encoding="utf-8").splitlines()
    assert "Claude Code" in "\n".join(lines[:20])


def test_readme_has_how_to_run_section():
    text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    assert "## How to run" in text


def test_readme_points_to_onboarding_wizard():
    text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    assert "/marketing40-onboarding" in text


def test_readme_hardcode_free():
    text = (REPO_ROOT / "README.md").read_text(encoding="utf-8").lower()
    for banned in ("empiricus", "luis roquette", "cf gauss", "rocketlabs", "@luisroquette"):
        assert banned not in text
