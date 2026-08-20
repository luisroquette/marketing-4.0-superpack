# tests/test_install_dry_run.py
"""Tests for the client kit installer's dry-run contract."""
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
INSTALL = REPO_ROOT / "install.sh"

EXPECTED_REPOS = (
    "My_LP_Makes_Neil_Proud",
    "My_UTMs_Make_Me_Proud",
    "My_MailMKT_makes_Neil_Proud",
    "My_Blog_Makes_Neil_Proud",
    "claude-seo",
)


def run_dry_run():
    return subprocess.run(
        ["bash", str(INSTALL), "--dry-run"], capture_output=True, text=True, timeout=30
    )


def test_dry_run_lists_all_five_repos():
    result = run_dry_run()
    assert result.returncode == 0, result.stderr
    for repo in EXPECTED_REPOS:
        assert repo in result.stdout


def test_dry_run_targets_skills_dir_and_wizard():
    result = run_dry_run()
    assert ".claude/skills" in result.stdout
    assert "marketing40" in result.stdout
    assert ".claude/skills/marketing40-onboarding" in result.stdout


def test_dry_run_never_clones():
    result = run_dry_run()
    assert "would clone" in result.stdout
    assert "git clone" not in result.stdout
