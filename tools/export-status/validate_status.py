#!/usr/bin/env python3
# tools/export-status/validate_status.py
"""Validates status.json against the Marketing 4.0 stage contract (schema v1)."""
import json
import sys
from datetime import datetime

STAGES = ("atrair", "converter", "nutrir", "medir")


def _iso_ok(value):
    if value is None:
        return True
    try:
        datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return True
    except (ValueError, AttributeError):
        return False


def validate(data):
    """Return a list of error strings; empty list means valid."""
    errors = []
    if not isinstance(data, dict):
        return ["status.json must be a JSON object"]
    if data.get("schemaVersion") != 1:
        errors.append("schemaVersion must be 1")
    client = data.get("client")
    if not isinstance(client, dict) or not isinstance(client.get("slug"), str) or not client["slug"]:
        errors.append("client.slug must be a non-empty string")
    if not _iso_ok(data.get("generatedAt")):
        errors.append("generatedAt must be an ISO 8601 UTC timestamp")
    stages = data.get("stages")
    if not isinstance(stages, dict):
        errors.append("stages must be an object")
        return errors
    for name in STAGES:
        if name not in stages:
            errors.append(f"missing stage: {name}")
            continue
        stage = stages[name]
        if not isinstance(stage, dict):
            errors.append(f"stages.{name} must be an object")
            continue
        items = stage.get("deliverables", [])
        if not isinstance(items, list):
            errors.append(f"stages.{name}.deliverables must be a list")
            continue
        if stage.get("count") != len(items):
            errors.append(
                f"stages.{name}.count ({stage.get('count')}) != len(deliverables) ({len(items)})"
            )
        if name in ("atrair", "converter") and not _iso_ok(stage.get("firstPublishedAt")):
            errors.append(f"stages.{name}.firstPublishedAt must be ISO 8601 UTC or null")
        if name == "nutrir" and not _iso_ok(stage.get("firstSentAt")):
            errors.append("stages.nutrir.firstSentAt must be ISO 8601 UTC or null")
    return errors


def main(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    errors = validate(data)
    if errors:
        for e in errors:
            print(f"INVALID: {e}", file=sys.stderr)
        sys.exit(1)
    print(f"VALID: {path}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <status.json>", file=sys.stderr)
        sys.exit(2)
    main(sys.argv[1])
