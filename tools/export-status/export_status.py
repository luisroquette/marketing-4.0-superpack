#!/usr/bin/env python3
# tools/export-status/export_status.py
"""Exports Marketing 4.0 workspace artifacts into status.json (schema v1).

Reads the artifact files defined in status.schema.md. Absent files mean an
empty stage — the exporter never invents data.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

STAGE_FILES = {
    "atrair": ("posts.json", "publishedAt"),
    "converter": ("blueprints.json", "publishedAt"),
    "nutrir": ("emails.json", "sentAt"),
    "medir": ("campaigns.json", None),
}


def _load_items(artifact_path):
    if not artifact_path.exists():
        return []
    data = json.loads(artifact_path.read_text(encoding="utf-8"))
    items = data.get("items")
    if not isinstance(items, list):
        raise ValueError(f"{artifact_path} must contain an 'items' list")
    return items


def export_status(workspace_dir, client_slug, client_name, now=None):
    """Build the status.json dict. `now` is an ISO 8601 UTC string override for tests."""
    if now is None:
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    workspace = Path(workspace_dir)
    stages = {}
    for name, (file_name, time_key) in STAGE_FILES.items():
        items = _load_items(workspace / "artifacts" / name / file_name)
        stage = {"deliverables": items, "count": len(items)}
        if time_key:
            times = [it.get(time_key) for it in items if isinstance(it, dict) and it.get(time_key)]
            key = "firstSentAt" if name == "nutrir" else "firstPublishedAt"
            stage[key] = min(times) if times else None
        stages[name] = stage
    return {
        "schemaVersion": 1,
        "client": {"slug": client_slug, "name": client_name},
        "generatedAt": now,
        "stages": stages,
    }


def main(argv):
    if len(argv) != 4:
        print(f"usage: {argv[0]} <workspace_dir> <client_slug> <client_name>", file=sys.stderr)
        sys.exit(2)
    workspace, slug, name = argv[1], argv[2], argv[3]
    status = export_status(workspace, slug, name)
    out = Path(workspace) / "status.json"
    out.write_text(json.dumps(status, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"status.json written: {out}")


if __name__ == "__main__":
    main(sys.argv)
