# tools/export-status/tests/test_export_status.py
"""Tests for the workspace -> status.json exporter."""
from pathlib import Path

import pytest

from export_status import export_status

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def test_full_workspace_exports_every_stage():
    status = export_status(FIXTURES / "full", "coesa", "COESA", now="2026-08-20T10:00:00Z")
    assert status["schemaVersion"] == 1
    assert status["client"] == {"slug": "coesa", "name": "COESA"}
    assert status["generatedAt"] == "2026-08-20T10:00:00Z"
    stages = status["stages"]
    assert stages["atrair"]["count"] == 2
    assert stages["atrair"]["firstPublishedAt"] == "2026-08-01T09:00:00Z"
    assert stages["converter"]["count"] == 1
    assert stages["converter"]["firstPublishedAt"] == "2026-08-07T14:00:00Z"
    assert stages["nutrir"]["count"] == 3
    assert stages["nutrir"]["firstSentAt"] == "2026-08-03T08:00:00Z"
    assert stages["medir"]["count"] == 1


def test_empty_workspace_exports_valid_empty_status():
    status = export_status(FIXTURES / "empty", "coesa", "COESA", now="2026-08-20T10:00:00Z")
    for stage in status["stages"].values():
        assert stage["deliverables"] == []
        assert stage["count"] == 0
    assert status["stages"]["atrair"]["firstPublishedAt"] is None


def test_artifact_without_items_key_raises_value_error():
    with pytest.raises(ValueError, match="items"):
        export_status(FIXTURES / "malformed", "coesa", "COESA", now="2026-08-20T10:00:00Z")


def test_exported_status_passes_the_validator():
    from validate_status import validate

    status = export_status(FIXTURES / "full", "coesa", "COESA", now="2026-08-20T10:00:00Z")
    assert validate(status) == []
