# Client Kit + Cockpit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Status:** executed 2026-08-20 — 6/6 tasks done, full suite green (24 tests), 8 local commits, nothing pushed.

**Goal:** Deliver the Marketing 4.0 pack to a client team that operates it themselves (COESA pilot), plus a thin read-only cockpit page that shows what the pack produced — without building any DB, auth, or billing infrastructure.

**Architecture:** Two tracks with one contract. Track A (motor): the 5 engine skills + onboarding wizard stay the product; a one-command installer (`install.sh`) packages them into a client workspace, and the README names the runtime (Claude Code) in its first lines. Track B (cockpit): a static HTML page reads a `status.json` exported from the workspace artifacts and renders the four funnel stages — read-only, never writes to the motor; if the cockpit is down, the motor runs unchanged. Contract: `status.json` schema v1.

**Tech Stack:** Bash (installer), Python 3 stdlib only (export + validator), static HTML/CSS/JS (cockpit, no build step), pytest (tests).

## Global Constraints

- Static-only phase 1: no DB, no auth, no billing, no new Vercel project, no analytics. The cockpit ships as static files next to the client deliverable.
- Never push. Local commits per task are fine; push only when the user explicitly orders it.
- Execution environment: this repo has no feature-branch convention — tasks commit directly on `main`. The finishing menu (merge/PR) does not apply; the only integration decision is push-or-keep-local.
- Every task commit adds ONLY its own files by explicit path — never `git add -A` (this repo holds 31 uncommitted sweep files from another task).
- Repo files (docs, plans, cockpit copy) are English. Chat with the user is PT-BR.
- Zero personal/hardcoded branding: no brand names, no personal URLs. Owner is overridable (`MARKETING40_OWNER` env).
- Python tools use stdlib only; pytest is the only test dependency.
- TDD: every code task writes the failing test first, then implements.
- Never invent artifact data: the exporter reads real files only; absent files produce empty stages.

## File Structure

```
marketing-4.0-superpack/
├── install.sh                          # client kit installer (Task 4)
├── cockpit/
│   ├── index.html                      # four stage cards + empty state (Task 3)
│   ├── app.js                          # fetch status.json → render (Task 3)
│   └── styles.css                      # static styling (Task 3)
├── tools/export-status/
│   ├── status.schema.md                # human-readable contract v1 (Task 1)
│   ├── validate_status.py              # schema validator (Task 1)
│   ├── export_status.py                # workspace artifacts → status.json (Task 2)
│   └── tests/
│       ├── conftest.py                 # sys.path for parent-dir imports (Task 1)
│       ├── test_validate_status.py     # Task 1
│       ├── fixtures/{full,empty,malformed}/  # Task 2
│       └── test_export_status.py       # Task 2
│       └── test_cockpit_smoke.py       # Task 3
├── tests/
│   ├── test_install_dry_run.py         # Task 4
│   └── test_readme_gate.py             # Task 5
├── docs/pilots/coesa-2026-08.md        # pilot metrics sheet (Task 6)
├── README.md                           # modified: runtime line-1 + How to run (Task 5)
└── .gitignore                          # modified: artifacts/, status.json, caches (Task 1)
```

---

### Task 1: status.json contract + validator

**Files:**
- Create: `tools/export-status/status.schema.md`
- Create: `tools/export-status/validate_status.py`
- Create: `tools/export-status/tests/conftest.py`
- Create: `tools/export-status/tests/test_validate_status.py`
- Modify: `.gitignore`

**Interfaces:**
- Produces: `validate_status.validate(data: dict) -> list[str]` — returns a list of error strings; empty list means valid. `validate_status.main(path: str) -> None` — exits 1 with INVALID lines on stderr, prints VALID on success.
- Consumes: nothing (first task). Later tasks depend on the contract it defines.

- [ ] **Step 1: Write the failing test**

```python
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
```

Create `tools/export-status/tests/conftest.py` so pytest can import the parent modules:

```python
# tools/export-status/tests/conftest.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pip install --user pytest -q && python3 -m pytest tools/export-status/tests/test_validate_status.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'validate_status'`

- [ ] **Step 3: Write the contract doc**

```markdown
<!-- tools/export-status/status.schema.md -->
# status.json — Schema v1

The single read contract between the Marketing 4.0 skills (motor) and the
cockpit (display). The cockpit only reads this file; it never writes back.

| Field | Type | Rule |
|---|---|---|
| schemaVersion | int | must be 1 |
| client.slug | string | non-empty, lowercase slug |
| client.name | string | display name |
| generatedAt | string | ISO 8601 UTC (`...Z`) |
| stages.atrair / converter / nutrir / medir | object | all four required |
| stages.<s>.deliverables | array | items mirrored from the stage's artifact file |
| stages.<s>.count | int | must equal len(deliverables) |
| stages.atrair.firstPublishedAt | string \| null | ISO 8601 UTC or null |
| stages.converter.firstPublishedAt | string \| null | ISO 8601 UTC or null |
| stages.nutrir.firstSentAt | string \| null | ISO 8601 UTC or null |

Timestamps must be ISO 8601 UTC. Artifact files: `artifacts/atrair/posts.json`,
`artifacts/converter/blueprints.json`, `artifacts/nutrir/emails.json`,
`artifacts/medir/campaigns.json` — each shaped `{"items": [...]}`.

## Example

{
  "schemaVersion": 1,
  "client": {"slug": "coesa", "name": "COESA"},
  "generatedAt": "2026-08-20T10:00:00Z",
  "stages": {
    "atrair": {"deliverables": [], "count": 0, "firstPublishedAt": null},
    "converter": {"deliverables": [], "count": 0, "firstPublishedAt": null},
    "nutrir": {"deliverables": [], "count": 0, "firstSentAt": null},
    "medir": {"deliverables": [], "count": 0}
  }
}
```

- [ ] **Step 4: Write the minimal implementation**

```python
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
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python3 -m pytest tools/export-status/tests/test_validate_status.py -q`
Expected: 6 passed

- [ ] **Step 6: Extend .gitignore**

Append to `.gitignore`:

```
# Marketing 4.0 kit artifacts
marketing40/
artifacts/
status.json
.pytest_cache/
__pycache__/
```

- [ ] **Step 7: Install the pre-push test hook**

```bash
cat > .git/hooks/pre-push << 'EOF'
#!/bin/sh
echo "[pre-push] Running Marketing 4.0 regression tests..."
python3 -m pytest -q
if [ $? -ne 0 ]; then
  echo "[pre-push] BLOCKED: tests failed. Push cancelled."
  exit 1
fi
EOF
chmod +x .git/hooks/pre-push
```

- [ ] **Step 8: Commit**

```bash
git add tools/export-status/status.schema.md tools/export-status/validate_status.py tools/export-status/tests/conftest.py tools/export-status/tests/test_validate_status.py .gitignore
git commit -m "feat: status.json schema v1 contract + validator (TDD)"
```

---

### Task 2: workspace → status.json exporter

**Files:**
- Create: `tools/export-status/export_status.py`
- Create: `tools/export-status/tests/fixtures/full/artifacts/atrair/posts.json`
- Create: `tools/export-status/tests/fixtures/full/artifacts/converter/blueprints.json`
- Create: `tools/export-status/tests/fixtures/full/artifacts/nutrir/emails.json`
- Create: `tools/export-status/tests/fixtures/full/artifacts/medir/campaigns.json`
- Create: `tools/export-status/tests/fixtures/empty/.gitkeep`
- Create: `tools/export-status/tests/fixtures/malformed/artifacts/nutrir/emails.json`
- Create: `tools/export-status/tests/test_export_status.py`

**Interfaces:**
- Consumes: the artifact file layout defined in `status.schema.md` (Task 1).
- Produces: `export_status.export_status(workspace_dir: str, client_slug: str, client_name: str, now: str | None = None) -> dict` — returns the status.json dict (valid per Task 1's `validate`). Tasks 3 and 6 consume its output shape.

- [ ] **Step 1: Write the failing test**

```python
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
```

Create the fixture files exactly as follows:

`tools/export-status/tests/fixtures/full/artifacts/atrair/posts.json`:
```json
{
  "items": [
    {"type": "blog-post", "title": "Energy market outlook — August", "publishedAt": "2026-08-01T09:00:00Z"},
    {"type": "blog-post", "title": "Solar savings: the real numbers", "publishedAt": "2026-08-05T09:00:00Z"}
  ]
}
```

`tools/export-status/tests/fixtures/full/artifacts/converter/blueprints.json`:
```json
{
  "items": [
    {"type": "landing-page", "slug": "relatorio-energia-agosto", "publishedAt": "2026-08-07T14:00:00Z"}
  ]
}
```

`tools/export-status/tests/fixtures/full/artifacts/nutrir/emails.json`:
```json
{
  "items": [
    {"type": "email", "subject": "Your report is ready", "sentAt": "2026-08-03T08:00:00Z", "recipients": 41},
    {"type": "email", "subject": "One week left", "sentAt": "2026-08-08T08:00:00Z", "recipients": 41},
    {"type": "email", "subject": "Last call", "sentAt": "2026-08-10T08:00:00Z", "recipients": 41}
  ]
}
```

`tools/export-status/tests/fixtures/full/artifacts/medir/campaigns.json`:
```json
{
  "items": [
    {"type": "campaign", "slug": "relatorio-energia-agosto", "clicks": 12, "leads": 3}
  ]
}
```

`tools/export-status/tests/fixtures/empty/.gitkeep` (empty file — the empty workspace has no `artifacts/` dir at all).

`tools/export-status/tests/fixtures/malformed/artifacts/nutrir/emails.json`:
```json
{"no_items": true}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tools/export-status/tests/test_export_status.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'export_status'`

- [ ] **Step 3: Write the minimal implementation**

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tools/export-status/tests/test_export_status.py -q`
Expected: 4 passed

- [ ] **Step 5: Commit**

```bash
git add tools/export-status/export_status.py tools/export-status/tests/fixtures tools/export-status/tests/test_export_status.py
git commit -m "feat: workspace -> status.json exporter (TDD)"
```

---

### Task 3: static cockpit page

**Files:**
- Create: `cockpit/index.html`
- Create: `cockpit/app.js`
- Create: `cockpit/styles.css`
- Create: `tools/export-status/tests/test_cockpit_smoke.py`

**Interfaces:**
- Consumes: `status.json` shape defined in Task 1, produced by Task 2. The page fetches `status.json` from its own directory (`fetch("status.json", { cache: "no-store" })`).
- Produces: a deployable static folder (`cockpit/` + a `status.json` beside it). Task 6 references its stage structure.

- [ ] **Step 1: Write the failing test**

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tools/export-status/tests/test_cockpit_smoke.py -q`
Expected: FAIL with `FileNotFoundError: .../cockpit/index.html`

- [ ] **Step 3: Write the page**

`cockpit/index.html`:
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Marketing 4.0 — Campaign Cockpit</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <header class="cockpit-header">
    <h1>Marketing 4.0</h1>
    <p class="cockpit-client" id="client-name">—</p>
    <p class="cockpit-updated" id="updated-at">—</p>
  </header>

  <main class="stages">
    <section class="stage" id="stage-atrair">
      <h2>Atrair</h2>
      <p class="stage-count" id="count-atrair">0</p>
      <ul class="stage-list" id="list-atrair"></ul>
    </section>
    <section class="stage" id="stage-converter">
      <h2>Converter</h2>
      <p class="stage-count" id="count-converter">0</p>
      <ul class="stage-list" id="list-converter"></ul>
    </section>
    <section class="stage" id="stage-nutrir">
      <h2>Nutrir</h2>
      <p class="stage-count" id="count-nutrir">0</p>
      <ul class="stage-list" id="list-nutrir"></ul>
    </section>
    <section class="stage" id="stage-medir">
      <h2>Medir</h2>
      <p class="stage-count" id="count-medir">0</p>
      <ul class="stage-list" id="list-medir"></ul>
    </section>
  </main>

  <div class="empty-state" id="empty-state" hidden>
    <h2>Pilot has no campaigns yet</h2>
    <p>Run the pack once and re-export <code>status.json</code> — the stages above fill in automatically.</p>
  </div>

  <script src="app.js"></script>
</body>
</html>
```

`cockpit/app.js`:
```javascript
// Renders status.json into the four stage cards. Read-only: never writes to the motor.
const TITLES = {
  "blog-post": (it) => it.title || "Untitled post",
  "landing-page": (it) => it.slug || "Untitled LP",
  "email": (it) => it.subject || "Untitled email",
  "campaign": (it) => it.slug || "Untitled campaign",
};

function renderStage(stageName, stage) {
  const count = document.getElementById(`count-${stageName}`);
  const list = document.getElementById(`list-${stageName}`);
  count.textContent = String(stage.count);
  list.replaceChildren();
  for (const item of stage.deliverables.slice(0, 20)) {
    const li = document.createElement("li");
    li.textContent = (TITLES[item.type] || (() => "Item"))(item);
    list.appendChild(li);
  }
}

function render(data) {
  document.getElementById("client-name").textContent = data.client.name;
  document.getElementById("updated-at").textContent = `Updated ${data.generatedAt}`;
  const stages = data.stages;
  const total = Object.values(stages).reduce((sum, s) => sum + s.count, 0);
  for (const name of ["atrair", "converter", "nutrir", "medir"]) {
    renderStage(name, stages[name]);
  }
  document.getElementById("empty-state").hidden = total > 0;
}

async function load() {
  try {
    const res = await fetch("status.json", { cache: "no-store" });
    if (!res.ok) throw new Error(`status.json HTTP ${res.status}`);
    render(await res.json());
  } catch (err) {
    console.error("Cockpit: could not load status.json — showing empty state.", err);
    document.getElementById("empty-state").hidden = false;
  }
}

load();
```

`cockpit/styles.css`:
```css
:root {
  --ink: #1a1524;
  --muted: #6b6478;
  --accent: #7b2fbe;
  --line: #e5e0ee;
}
body {
  margin: 0;
  font-family: Inter, system-ui, sans-serif;
  color: var(--ink);
  background: #faf9fc;
}
.cockpit-header { padding: 2rem 1.5rem 1rem; border-bottom: 1px solid var(--line); }
.cockpit-header h1 { margin: 0; font-size: 1.4rem; }
.cockpit-client { margin: 0.25rem 0 0; font-weight: 600; }
.cockpit-updated { margin: 0; color: var(--muted); font-size: 0.85rem; }
.stages {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
  padding: 1.5rem;
}
.stage { border: 1px solid var(--line); border-radius: 12px; padding: 1rem; background: #fff; }
.stage h2 { margin: 0 0 0.5rem; font-size: 1rem; }
.stage-count { margin: 0 0 0.5rem; font-size: 1.6rem; font-weight: 700; color: var(--accent); }
.stage-list { margin: 0; padding-left: 1.1rem; color: var(--muted); font-size: 0.85rem; }
.empty-state {
  margin: 1.5rem;
  padding: 1.5rem;
  border: 1px dashed var(--line);
  border-radius: 12px;
  text-align: center;
  color: var(--muted);
}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tools/export-status/tests/test_cockpit_smoke.py -q`
Expected: 4 passed

- [ ] **Step 5: Manual browser check (empty and full)**

Empty state:
```bash
rm -rf /tmp/cockpit-demo && mkdir -p /tmp/cockpit-demo
cp cockpit/index.html cockpit/app.js cockpit/styles.css /tmp/cockpit-demo/
python3 tools/export-status/export_status.py /tmp/cockpit-demo coesa COESA
cd /tmp/cockpit-demo && python3 -m http.server 8000
```
Open `http://localhost:8000` — expect: header "—" / "—", four stages with 0, empty-state visible.

Full state (then refresh the page):
```bash
cp -R tools/export-status/tests/fixtures/full/artifacts /tmp/cockpit-demo/
python3 tools/export-status/export_status.py /tmp/cockpit-demo coesa COESA
```
Refresh — expect: client "COESA", counts 2/1/3/1, lists filled, empty-state hidden.

Agentic fallback (no browser available): verify with curl instead —
`curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/index.html`
must return 200 for index.html, app.js, styles.css, and status.json; and
`curl -s http://localhost:8000/status.json` must show the same counts.
If the port is busy, pick another (e.g. 8231) and adjust the URLs.

- [ ] **Step 6: Commit**

```bash
git add cockpit/index.html cockpit/app.js cockpit/styles.css tools/export-status/tests/test_cockpit_smoke.py
git commit -m "feat: static cockpit page reading status.json (TDD)"
```

- [ ] **Step 7: file:// guard (TDD)**

Delivered as a plain folder, the page will be double-clicked — and under
`file://` the `fetch("status.json")` fails silently, showing "no campaigns"
even when data exists. Write the failing test:

```python
def test_cockpit_guides_file_protocol_users():
    js = (REPO_ROOT / "cockpit" / "app.js").read_text(encoding="utf-8")
    assert 'location.protocol === "file:"' in js
```

Run: `python3 -m pytest tools/export-status/tests/test_cockpit_smoke.py -q`
Expected: 1 failed (the guard does not exist yet).

Then implement: give the empty-state heading/paragraph ids in `index.html`
(`id="empty-state-title"`, `id="empty-state-hint"`) and extend the `catch`
block in `app.js`:

```javascript
  } catch (err) {
    console.error("Cockpit: could not load status.json — showing empty state.", err);
    const emptyState = document.getElementById("empty-state");
    emptyState.hidden = false;
    if (location.protocol === "file:") {
      document.getElementById("empty-state-title").textContent =
        "This page needs a static server";
      document.getElementById("empty-state-hint").textContent =
        "Run `python3 -m http.server` in this folder and open http://localhost:8000 — double-clicking the file hides the data.";
    }
  }
```

Run: `python3 -m pytest -q`
Expected: full suite green.

```bash
git add cockpit/index.html cockpit/app.js tools/export-status/tests/test_cockpit_smoke.py
git commit -m "fix: cockpit guides file:// users to a static server (TDD regression)"
```

---

### Task 4: client kit installer

**Files:**
- Create: `install.sh`
- Create: `tests/test_install_dry_run.py`

**Interfaces:**
- Consumes: nothing from earlier code tasks. The wizard skill lives at `<repo>/.claude/skills/marketing40-onboarding/` (already in this repo).
- Produces: `install.sh --dry-run` (prints planned actions, exits 0) and `install.sh` (real install into the caller's workspace). Task 6's onboarding steps invoke it.

- [ ] **Step 1: Write the failing test**

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_install_dry_run.py -q`
Expected: FAIL with returncode != 0 (`bash: install.sh: No such file or directory`)

- [ ] **Step 3: Write the installer**

```bash
#!/usr/bin/env bash
# Marketing 4.0 client kit installer.
# Runs inside the client's workspace. Installs the 5 engine skills and the
# onboarding wizard into .claude/skills/, and appends a CLAUDE.md pointer.
# Owner is overridable: MARKETING40_OWNER=myorg bash install.sh
set -euo pipefail

OWNER="${MARKETING40_OWNER:-luisroquette}"
REPOS=(
  "${OWNER}/My_LP_Makes_Neil_Proud:my-lp-makes-neil-proud"
  "${OWNER}/My_UTMs_Make_Me_Proud:my-utms-make-me-proud"
  "${OWNER}/My_MailMKT_makes_Neil_Proud:my-mailmkt-makes-neil-proud"
  "${OWNER}/My_Blog_Makes_Neil_Proud:my-blog-makes-neil-proud"
  "AgriciDaniel/claude-seo:claude-seo"
)
DEST="marketing40"
SKILLS_DIR=".claude/skills"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WIZARD_SRC="${SCRIPT_DIR}/.claude/skills/marketing40-onboarding"

if ! command -v git >/dev/null 2>&1; then
  echo "install.sh: git is required (https://git-scm.com)" >&2
  exit 1
fi

if [[ "${1:-}" == "--dry-run" ]]; then
  echo "would create ${DEST}/"
  for entry in "${REPOS[@]}"; do
    repo="${entry%%:*}"; name="${entry##*:}"
    echo "would clone https://github.com/${repo}.git -> ${DEST}/${name}"
    echo "would copy skills from ${DEST}/${name} -> ${SKILLS_DIR}/${name}"
  done
  echo "would copy wizard ${WIZARD_SRC} -> ${SKILLS_DIR}/marketing40-onboarding"
  echo "would append CLAUDE.md pointer at repo root"
  exit 0
fi

mkdir -p "${DEST}" "${SKILLS_DIR}"
for entry in "${REPOS[@]}"; do
  repo="${entry%%:*}"; name="${entry##*:}"
  if [[ ! -d "${DEST}/${name}" ]]; then
    git clone --depth 1 "https://github.com/${repo}.git" "${DEST}/${name}"
  else
    echo "already present: ${DEST}/${name} (skipping clone)"
  fi
  mkdir -p "${SKILLS_DIR}/${name}"
  for entry_path in SKILL.md references scripts assets templates; do
    if [[ -e "${DEST}/${name}/${entry_path}" ]]; then
      cp -R "${DEST}/${name}/${entry_path}" "${SKILLS_DIR}/${name}/"
    fi
  done
done

if [[ -d "${WIZARD_SRC}" ]]; then
  cp -R "${WIZARD_SRC}" "${SKILLS_DIR}/marketing40-onboarding"
else
  echo "warning: wizard skill not found at ${WIZARD_SRC} — the pack will run without /marketing40-onboarding" >&2
fi

cat >> CLAUDE.md <<'EOF'

# Marketing 4.0
This workspace runs the Marketing 4.0 pack inside Claude Code.
Start with `/marketing40-onboarding`.
EOF

echo "Done. Open Claude Code in this workspace and run /marketing40-onboarding"
```

Make it executable: `chmod +x install.sh`

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_install_dry_run.py -q`
Expected: 3 passed

- [ ] **Step 5: Manual dry-run check**

Run: `bash install.sh --dry-run`
Expected: 5 "would clone" lines (4 owner repos + claude-seo), wizard line, CLAUDE.md line, no network activity.

- [ ] **Step 6: Commit**

```bash
git add install.sh tests/test_install_dry_run.py
git commit -m "feat: one-command client kit installer (TDD)"
```

- [ ] **Step 7: Idempotency hardening (TDD)**

Re-runs are the happy path of an installer — a second run must not duplicate
the CLAUDE.md pointer or nest the wizard folder. Write the failing test:

```python
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
```

Run: `python3 -m pytest tests/test_install_idempotent.py -q`
Expected: FAIL on both (the Step 3 script appends twice and nests the wizard).

Apply the two fixes to `install.sh`:

```bash
# 1. Wizard copy: clear the destination first so cp never nests
rm -rf "${SKILLS_DIR}/marketing40-onboarding"
cp -R "${WIZARD_SRC}" "${SKILLS_DIR}/marketing40-onboarding"

# 2. CLAUDE.md pointer: append only when the marker is absent
if ! grep -q "This workspace runs the Marketing 4.0 pack" CLAUDE.md 2>/dev/null; then
  cat >> CLAUDE.md <<'EOF'

# Marketing 4.0
This workspace runs the Marketing 4.0 pack inside Claude Code.
Start with `/marketing40-onboarding`.
EOF
fi
```

Run: `python3 -m pytest tests/test_install_idempotent.py -q && python3 -m pytest -q`
Expected: 2 passed, then the full suite green.

```bash
git add install.sh tests/test_install_idempotent.py
git commit -m "fix: installer re-runs are idempotent (TDD regression)"
```

---

### Task 5: README porta de entrada (runtime on line 1)

**Files:**
- Modify: `README.md`
- Create: `tests/test_readme_gate.py`

**Interfaces:**
- Consumes: nothing from code tasks.
- Produces: the gate every client lands on — line-1 runtime statement + `## How to run` section pointing at `/marketing40-onboarding`.

- [ ] **Step 1: Write the failing test**

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_readme_gate.py -q`
Expected: at least one FAIL (today the README has no "## How to run" section and no "/marketing40-onboarding" mention)

- [ ] **Step 3: Edit README.md — insert the runtime callout after the subtitle**

The README has no `# ` H1 — the title is `<h1 align="center">MARKETING 4.0</h1>`
followed by a centered subtitle paragraph. Insert this callout between the
subtitle's closing `</p>` and the badges `<p align="center">` block (this
keeps "Claude Code" inside the gate test's first-20-lines window):

```markdown
> **Marketing 4.0 runs inside Claude Code.** One command installs it, one command starts it: `bash install.sh`, then `/marketing40-onboarding`.
```

- [ ] **Step 4: Edit README.md — insert the "## How to run" section before the first existing `## ` section**

```markdown
## How to run

Marketing 4.0 is a set of agent skills that run **inside Claude Code** — not a
standalone program, not a server, and not something you upload to a chat bot.

1. Install [Claude Code](https://claude.com/claude-code) and sign in (one per operator).
2. Clone this repository and run `bash install.sh` inside the client workspace.
3. Open Claude Code in that workspace and run `/marketing40-onboarding`.

The wizard walks the team through credentials, gates, and the first campaign.
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_readme_gate.py -q`
Expected: 4 passed

- [ ] **Step 6: Commit**

```bash
git add README.md tests/test_readme_gate.py
git commit -m "docs: README names the runtime on line 1 + How to run (TDD)"
```

---

### Task 6: COESA pilot playbook

**Files:**
- Create: `docs/pilots/coesa-2026-08.md`

**Interfaces:**
- Consumes: `status.json` timestamps (metric M1) and stage counts (metric M3) from Task 2; `install.sh` from Task 4.
- Produces: the metric definitions and weekly tracking sheet the pilot runs on. Verification is a review checklist, not a code test.

- [ ] **Step 1: Write the playbook**

```markdown
# COESA Pilot — August 2026

## Setup checklist

- [ ] `bash install.sh` ran inside the COESA workspace (5 engines + wizard present in `.claude/skills/`)
- [ ] Each operator has Claude Code installed and signed in
- [ ] `/marketing40-onboarding` completed at least once (all gates green)
- [ ] `cockpit/` copied into a folder the COESA team can open, with a fresh `status.json` beside it — served over HTTP (e.g. `python3 -m http.server`), never opened via `file://` (the cockpit itself warns about this; same flow as Task 3's manual check)

## Metrics

1. **Time to first campaign** — days from onboarding completion to the first
   campaign published by the COESA team alone. Measured from `status.json`
   timestamps (`stages.converter.firstPublishedAt` or `stages.atrair.firstPublishedAt`).
2. **Support tickets** — number of times the COESA team asks for help
   (you count). Target: 2 or fewer per week after week 1.
3. **Unassisted deliverables** — `stages.*.count` values in `status.json`
   for work the COESA team produced without you in the room.

## Weekly check

| Week | M1 days-to-first | M2 tickets | M3 atrair/converter/nutrir/medir | Notes |
|---|---|---|---|---|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |

## Decision gate (after week 4)

- M1 <= 7 days AND M2 <= 2/week AND M3 growing → the pack runs itself; consider phase 2 (cockpit hosting, more clients).
- M1 > 7 days or M2 > 2/week → fix the onboarding/docs bottleneck before any software expansion. Record the bottleneck here:
  - [ ] (bottleneck notes)
```

- [ ] **Step 2: Review checklist (this IS the verification)**

1. Do the three metrics map 1:1 to the design's pilot metrics (time to first campaign, tickets, unassisted deliverables)? Yes/no.
2. Can M1 and M3 be read from `status.json` as produced by Task 2? M1: `stages.converter.firstPublishedAt` exists only if the client publishes an LP; a blog-first client has it on `stages.atrair.firstPublishedAt` — both covered. M3: `count` fields — covered.
3. Is anything hardcoded to a specific brand or person? The file names COESA (the pilot client — intended), nothing else.

- [ ] **Step 3: Commit**

```bash
git add docs/pilots/coesa-2026-08.md
git commit -m "docs: COESA pilot playbook with metrics and decision gate"
```

---

## Iteration log

- Round 0 (2026-08-20): initial draft (writing-plans skill).
- Round 1 (2026-08-20): 1 improvement applied — Task 6 setup checklist gained the cockpit delivery step (`cockpit/` + `status.json` handed to the COESA team), which the design required but the plan never operationalized.
- Round 2 (2026-08-20, found during execution): fixed cockpit smoke test path bug — `parents[2]` pointed at `tools/`, not the repo root; the test file sits 3 levels deep, so it must be `parents[3]`.
- Round 3 (2026-08-20, found during execution): Task 5 anchor corrected — the README has no `# ` H1 (title is `<h1 align="center">`); the callout anchors on the subtitle paragraph instead, keeping "Claude Code" inside the first 20 lines.
- Round 4 (2026-08-20): 2 improvements applied — (1) Task 3 manual check gained an agentic curl fallback (the plan assumed a browser; execution had none available); (2) Global Constraints gained the execution-environment note (commits land directly on `main`; the finishing menu's merge/PR options do not apply).
- Round 5 (2026-08-20): 3 improvements applied — (1) Task 4 gained Step 7: idempotency hardening with TDD regression tests (re-runs duplicated the CLAUDE.md pointer and nested the wizard folder — both reproduced red, fixed, committed); (2) Task 3 curl fallback gained a port-collision note; (3) header gained the execution status line.
- Round 6 (2026-08-20): CLEAN — no substantial improvements found. Plan is fully executed and reconciled: code blocks match the committed files, counts (23 tests / 7 commits) match reality, anchors and paths verified.
- Round 7 (2026-08-20): 1 improvement applied — Task 3 gained Step 7: file:// guard with TDD regression test (double-clicking the delivered page failed `fetch` silently and showed "no campaigns" with data present; the cockpit now tells file:// users to run a static server). Task 6 checklist tightened to "served over HTTP, never file://". Status line updated to 24 tests / 8 commits.
- Round 8 (2026-08-20): CLEAN — no substantial improvements. Step 7 internally consistent; counts verified (24 tests / 8 commits); remaining candidates (date-only acceptance in the validator, stale-file merge on installer re-runs, missing ToC entry) are cosmetic, not substantial.
- Round 9 (2026-08-20): CLEAN — second consecutive pass with no substantial improvements. Loop closed.
