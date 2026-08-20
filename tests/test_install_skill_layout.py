# tests/test_install_skill_layout.py
"""REGRESSÃO (piloto COESA 2026-08-20): o installer perdia engines cujo
SKILL.md vive em skills/<name>/ (claude-seo) e falhava em silêncio quando o
repo não tem SKILL.md nenhum (my-blog-makes-neil-proud)."""
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
    """Workspace com os 5 repos já clonados (sem rede), layouts reais."""
    for name in ENGINES:
        (tmp_path / "marketing40" / name).mkdir(parents=True)
    # 3 engines clássicos: SKILL.md na raiz
    for name in ENGINES[:3]:
        (tmp_path / "marketing40" / name / "SKILL.md").write_text(
            "# stub\n", encoding="utf-8"
        )
    # claude-seo: skills aninhadas em skills/<name>/, sem SKILL.md na raiz
    seo = tmp_path / "marketing40" / "claude-seo" / "skills" / "seo-plan"
    seo.mkdir(parents=True)
    (seo / "SKILL.md").write_text("# seo-plan\n", encoding="utf-8")
    # my-blog: sem SKILL.md em lugar nenhum
    return tmp_path


def _run(tmp_path):
    return subprocess.run(
        ["bash", str(INSTALL)], cwd=tmp_path, capture_output=True, text=True, timeout=60
    )


def test_nested_skill_dirs_are_installed(tmp_path):
    ws = _workspace(tmp_path)
    result = _run(ws)
    assert result.returncode == 0, result.stderr
    assert (ws / ".claude" / "skills" / "seo-plan" / "SKILL.md").exists()


def test_engine_without_skill_file_warns_instead_of_silent_skip(tmp_path):
    ws = _workspace(tmp_path)
    result = _run(ws)
    assert result.returncode == 0, result.stderr
    assert "no SKILL.md" in result.stderr
    assert "my-blog-makes-neil-proud" in result.stderr


def test_bundle_layout_keeps_wizard_when_source_is_destination(tmp_path):
    """REGRESSÃO (bundle 2026-08-20): no bundle de download, install.sh e o
    wizard vivem na MESMA árvore — o rm -rf do wizard apagava a fonte e o
    cp morria. A skill deve continuar intacta e o install terminar 0."""
    import shutil

    ws = _workspace(tmp_path)
    wizard = ws / ".claude" / "skills" / "marketing40-onboarding"
    wizard.mkdir(parents=True)
    (wizard / "SKILL.md").write_text("# wizard\n", encoding="utf-8")
    shutil.copy2(INSTALL, ws / "install.sh")
    result = subprocess.run(
        ["bash", "install.sh"], cwd=ws, capture_output=True, text=True, timeout=60
    )
    assert result.returncode == 0, result.stderr
    assert (wizard / "SKILL.md").exists()
