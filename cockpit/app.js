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
    const emptyState = document.getElementById("empty-state");
    emptyState.hidden = false;
    if (location.protocol === "file:") {
      document.getElementById("empty-state-title").textContent =
        "This page needs a static server";
      document.getElementById("empty-state-hint").textContent =
        "Run `python3 -m http.server` in this folder and open http://localhost:8000 — double-clicking the file hides the data.";
    }
  }
}

load();
