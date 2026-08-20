# tests/test_install_idempotent.py
"""Regression tests: install.sh re-runs must be idempotent (no duplicate
CLAUDE.md pointer, no nested wizard folder)."""
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
INSTALL = REPO_ROOT / "install.sh"

ENGINES = (
    "my-lp-makes-neil-proud",
    "my-utms-make-me-proud",
    "my-mailmkt-makes-neil-proud",
    "my-blog-makes-neil-proud",
    "claude-seo",
)


def _workspace(tmp_path):
    """A client workspace with all 5 engine repos already cloned (no network)."""
    for name in ENGINES:
        (tmp_path / "marketing40" / name).mkdir(parents=True)
        (tmp_path / "marketing40" / name / "SKILL.md").write_text("# stub\n", encoding="utf-8")
    return tmp_path


def _run(tmp_path):
    return subprocess.run(
        ["bash", str(INSTALL)], cwd=tmp_path, capture_output=True, text=True, timeout=60
    )


def test_second_run_does_not_duplicate_claude_md_pointer(tmp_path):
    ws = _workspace(tmp_path)
    first = _run(ws)
    assert first.returncode == 0, first.stderr
    second = _run(ws)
    assert second.returncode == 0, second.stderr
    text = (ws / "CLAUDE.md").read_text(encoding="utf-8")
    assert text.count("This workspace runs the Marketing 4.0 pack") == 1


def test_second_run_does_not_nest_wizard_folder(tmp_path):
    ws = _workspace(tmp_path)
    assert _run(ws).returncode == 0
    assert _run(ws).returncode == 0
    nested = ws / ".claude" / "skills" / "marketing40-onboarding" / "marketing40-onboarding"
    assert not nested.exists()
