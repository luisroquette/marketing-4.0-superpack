#!/usr/bin/env python3
"""Validate references/sockets.json against its own schema, its twin sockets.md,
and (optionally) the generated knowledge graph.

Exit 0 when everything holds; exit 1 with a plain list of failures otherwise.

Usage:
  python3 scripts/validate-sockets.py
  python3 scripts/validate-sockets.py --graph /path/to/graph.json
"""
import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILL_REF = REPO / ".claude/skills/marketing40-onboarding/references"

VALID_TIERS = {"must", "should", "optional", "revenue-unlock"}
REQUIRED_FIELDS = ["id", "name", "tier", "required", "contract",
                   "reference_plug", "alternative_plugs", "locked_without"]


def validate_schema(data):
    errors = []
    if "meta" not in data:
        errors.append("meta block missing")
    if "unlock_chain" not in data:
        errors.append("unlock_chain missing")
    if "sockets" not in data or not isinstance(data["sockets"], list):
        errors.append("sockets missing or not a list")
        return errors

    sockets = data["sockets"]
    ids = [s.get("id") for s in sockets]
    if sorted(ids) != list(range(1, len(sockets) + 1)):
        errors.append(f"socket ids must be 1..{len(sockets)} unique, got {ids}")
    for s in sockets:
        sid = s.get("id")
        for field in REQUIRED_FIELDS:
            if field not in s:
                errors.append(f"socket {sid}: field '{field}' missing")
                continue
            v = s[field]
            if field == "required" and not (isinstance(v, bool) or (isinstance(v, str) and v.strip())):
                errors.append(f"socket {sid}: 'required' must be boolean or non-empty string, got {v!r}")
            elif field not in ("id", "required", "reference_plug") and isinstance(v, str) and not v.strip():
                errors.append(f"socket {sid}: field '{field}' is empty")
        if s.get("tier") not in VALID_TIERS:
            errors.append(f"socket {sid}: tier '{s.get('tier')}' not in {sorted(VALID_TIERS)}")
        if "alternative_plugs" in s and not isinstance(s["alternative_plugs"], list):
            errors.append(f"socket {sid}: alternative_plugs must be a list")

    known = set(ids)
    for step in data.get("unlock_chain", []):
        for ref in step.get("socket_ids", []):
            if ref not in known:
                errors.append(f"unlock_chain references unknown socket id {ref}")
    return errors


def validate_md_consistency(data):
    errors = []
    md_path = SKILL_REF / "sockets.md"
    if not md_path.exists():
        errors.append(f"sockets.md not found at {md_path}")
        return errors
    md = md_path.read_text()
    rows = [r for r in re.findall(r"^\| (\d) \| (.+) \|$", md, re.M)
            if not r[1].startswith("Socket")]
    md_ids = [int(r[0]) for r in rows]
    json_sockets = {s["id"]: s for s in data["sockets"]}
    if sorted(md_ids) != sorted(json_sockets):
        errors.append(f"socket ids differ: md={sorted(md_ids)} json={sorted(json_sockets)}")
    for num, cells in rows:
        parts = [c.strip() for c in cells.split("|")]
        if len(parts) != 6:
            errors.append(f"socket {num}: md row must have 6 columns, got {len(parts)}")
            continue
        name, _, _, _, _, locked = parts
        if num not in json_sockets:
            continue
        if name != json_sockets[num]["name"]:
            errors.append(f"socket {num}: name mismatch md='{name}' json='{json_sockets[num]['name']}'")
        if locked != json_sockets[num]["locked_without"]:
            errors.append(f"socket {num}: locked_without mismatch md='{locked}' json='{json_sockets[num]['locked_without']}'")
    return errors


def validate_graph_tags(data, graph_path):
    graph = json.loads(Path(graph_path).read_text())
    nodes = graph.get("nodes", graph if isinstance(graph, list) else [])
    labels = {n.get("label", "") for n in nodes}
    missing = []
    for s in data["sockets"]:
        prefix = f"Socket {s['id']} —"
        if not any(l.startswith(prefix) for l in labels):
            missing.append(s["id"])
    if missing:
        return [f"graph {graph_path} is missing socket nodes: {missing}"]
    return []


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--graph", help="path to graphify graph.json to cross-check socket nodes")
    args = parser.parse_args()

    json_path = SKILL_REF / "sockets.json"
    try:
        data = json.loads(json_path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAIL: cannot read {json_path}: {exc}")
        sys.exit(1)

    errors = validate_schema(data) + validate_md_consistency(data)
    if args.graph:
        errors += validate_graph_tags(data, args.graph)

    if errors:
        print("FAIL:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    print("SOCKETS VALID")
    if args.graph:
        print(f"  graph tags: {len(data['sockets'])}/9 socket nodes present in {args.graph}")


if __name__ == "__main__":
    main()
