"""Single-page HTML UI for shots list/rename; uses ``/shots`` and ``/shots/rename`` (presenter-backed)."""

from __future__ import annotations

import json

from framework_and_drivers.tracking_presets import (
    BACKEND_OPTIONS,
    FAKE_PROJECT_PRESETS,
    PROJECT_HINTS,
)
from interface_adapters.view_models.color_hint_theme import COLOR_HINT_HEX


def shots_browser_html() -> str:
    boot = {
        "backendOptions": [
            {"label": label, "tracking": tracking, "fakeVendor": fake_vendor}
            for label, tracking, fake_vendor in BACKEND_OPTIONS
        ],
        "projectHints": list(PROJECT_HINTS),
        "fakeProjectPresets": {
            f"{tracking}|{fake_vendor}": pids
            for (tracking, fake_vendor), pids in FAKE_PROJECT_PRESETS.items()
        },
        "colorHintHex": {hint.value: hex_ for hint, hex_ in COLOR_HINT_HEX.items()},
    }
    boot_json = json.dumps(boot, separators=(",", ":")).replace("</", "<\\/")
    return _PAGE_TEMPLATE.replace("__BOOT_JSON__", boot_json)


_PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Shots — Clean Architecture demo</title>
<style>
  :root {
    --bg: #f3f4f6;
    --panel: #fff;
    --border: #d1d5db;
    --muted: #4b5563;
    --err: #b91c1c;
    --ok: #15803d;
  }
  html, body { height: 100%; }
  body { font-family: system-ui, sans-serif; margin: 0; padding: 16px; background: var(--bg); color: #111827; box-sizing: border-box; }
  body * { box-sizing: inherit; }
  h1 { font-size: 1.15rem; margin: 0 0 12px; font-weight: 600; }
  .panel { background: var(--panel); border: 1px solid var(--border); border-radius: 8px; padding: 14px 16px; max-width: 960px; display: flex; flex-direction: column; gap: 0; min-height: 0; }
  .row { display: flex; flex-wrap: wrap; gap: 10px 16px; align-items: flex-end; margin-bottom: 12px; }
  label { display: flex; flex-direction: column; gap: 4px; font-size: 12px; color: var(--muted); }
  select, input[type="text"] { min-width: 200px; padding: 6px 8px; border: 1px solid var(--border); border-radius: 6px; font-size: 14px; }
  #projectId { min-width: 220px; }
  button { padding: 8px 14px; border-radius: 6px; border: 1px solid var(--border); background: #e5e7eb; cursor: pointer; font-size: 14px; }
  button.primary { background: #2563eb; color: #fff; border-color: #1d4ed8; }
  button.primary:hover { background: #1d4ed8; }
  #projectHint { font-size: 11px; color: var(--muted); margin: 0 0 10px; line-height: 1.35; }
  th, td { border: 1px solid var(--border); padding: 8px 10px; text-align: left; }
  th { background: #e5e7eb; font-weight: 600; }
  tbody tr { cursor: pointer; }
  tbody tr:nth-child(even) { background: #f9fafb; }
  tbody tr.selected { background: #dbeafe; outline: 2px solid #2563eb; outline-offset: -2px; }
  .status-pill { font-weight: 500; }
  .status-pill.strong { font-weight: 700; }
  #statusMsg { margin-top: 10px; font-size: 13px; min-height: 1.2em; white-space: pre-wrap; flex-shrink: 0; }
  #statusMsg.err { color: var(--err); }
  #statusMsg.ok { color: var(--ok); }
  /* Match Qt: bounded shot list with its own scrollbar; rename stays below without scrolling the page. */
  .table-scroll {
    margin-top: 8px;
    max-height: min(42vh, 360px);
    overflow: auto;
    border: 1px solid var(--border);
    border-radius: 6px;
    flex-shrink: 0;
  }
  .table-scroll table { margin-top: 0; width: 100%; border-collapse: collapse; font-size: 13px; }
  .table-scroll thead th {
    position: sticky;
    top: 0;
    z-index: 1;
    background: #e5e7eb;
    box-shadow: 0 1px 0 var(--border);
  }
  .shots-footer { flex-shrink: 0; margin-top: 12px; padding-top: 4px; border-top: 1px solid var(--border); }
  #selectedInfo { font-size: 12px; color: var(--muted); margin: 0 0 8px; line-height: 1.35; }
  .rename-row { display: flex; flex-wrap: wrap; gap: 10px; align-items: flex-end; margin-top: 0; }
  .rename-row label { min-width: 140px; }
</style>
</head>
<body>
<div class="panel">
  <h1>Shots — Clean Architecture demo</h1>
  <p id="projectHint"></p>
  <div class="row">
    <label>Source
      <select id="source"></select>
    </label>
    <label>Project id
      <input type="text" id="projectId" list="presetList" autocomplete="off"/>
      <datalist id="presetList"></datalist>
    </label>
    <button type="button" class="primary" id="loadBtn">Load shots</button>
  </div>
  <div id="statusMsg"></div>
  <div class="table-scroll" aria-label="Shots list">
    <table>
      <thead><tr><th>Name</th><th>Sequence</th><th>Status</th></tr></thead>
      <tbody id="shotBody"></tbody>
    </table>
  </div>
  <div class="shots-footer">
    <p id="selectedInfo">Load shots, then select a row.</p>
    <div class="rename-row">
      <label>New name
        <input type="text" id="newName" placeholder="e.g. SEQ02_99 (sequence from selected shot)"/>
      </label>
      <label>First segment override (optional)
        <input type="text" id="projectCode" placeholder="Enter to override sequence as first segment"/>
      </label>
      <button type="button" class="primary" id="renameBtn" disabled>Rename selected shot</button>
    </div>
  </div>
</div>
<script type="application/json" id="boot-json">__BOOT_JSON__</script>
<script>
(function () {
  const boot = JSON.parse(document.getElementById("boot-json").textContent);
  const source = document.getElementById("source");
  const projectHint = document.getElementById("projectHint");
  const projectId = document.getElementById("projectId");
  const presetList = document.getElementById("presetList");
  const shotBody = document.getElementById("shotBody");
  const statusMsg = document.getElementById("statusMsg");
  const selectedInfo = document.getElementById("selectedInfo");
  const newName = document.getElementById("newName");
  const projectCode = document.getElementById("projectCode");
  const renameBtn = document.getElementById("renameBtn");
  const loadBtn = document.getElementById("loadBtn");
  const colors = boot.colorHintHex;

  let rows = [];
  let selectedIndex = -1;

  function setStatus(text, kind) {
    statusMsg.textContent = text || "";
    statusMsg.className = kind === "err" ? "err" : kind === "ok" ? "ok" : "";
  }

  function currentBackend() {
    const i = source.selectedIndex;
    return boot.backendOptions[i] || boot.backendOptions[0];
  }

  function presetKey(b) {
    return b.tracking + "|" + (b.fakeVendor || "");
  }

  function refreshPresets() {
    const b = currentBackend();
    projectHint.textContent = boot.projectHints[source.selectedIndex] || "";
    const presets = boot.fakeProjectPresets[presetKey(b)] || [];
    presetList.innerHTML = "";
    presets.forEach(function (pid) {
      const o = document.createElement("option");
      o.value = pid;
      presetList.appendChild(o);
    });
    if (presets.length) {
      projectId.value = presets[0];
    } else {
      projectId.value = "";
    }
    projectId.placeholder = projectHint.textContent || "Project id";
  }

  boot.backendOptions.forEach(function (opt, idx) {
    const o = document.createElement("option");
    o.value = String(idx);
    o.textContent = opt.label;
    source.appendChild(o);
  });
  source.selectedIndex = 0;
  source.addEventListener("change", refreshPresets);
  refreshPresets();

  function queryParams() {
    const b = currentBackend();
    const params = new URLSearchParams();
    params.set("project_id", projectId.value.trim());
    params.set("tracking", b.tracking);
    if (b.fakeVendor) params.set("fake_vendor", b.fakeVendor);
    return params;
  }

  function renameQuery() {
    const b = currentBackend();
    const params = new URLSearchParams();
    params.set("tracking", b.tracking);
    if (b.fakeVendor) params.set("fake_vendor", b.fakeVendor);
    return params.toString();
  }

  function renderTable(data) {
    rows = data.rows || [];
    selectedIndex = -1;
    shotBody.textContent = "";
    rows.forEach(function (r, idx) {
      const tr = document.createElement("tr");
      tr.dataset.index = String(idx);
      const tdName = document.createElement("td");
      tdName.textContent = r.name;
      const tdSeq = document.createElement("td");
      tdSeq.textContent = r.sequence != null ? r.sequence : "";
      const tdStat = document.createElement("td");
      const span = document.createElement("span");
      span.className = "status-pill" + (r.font_emphasis === "strong" ? " strong" : "");
      span.textContent = r.status_label;
      const hex = colors[r.color_hint] || colors.neutral || "#111827";
      span.style.color = hex;
      tdStat.appendChild(span);
      tr.appendChild(tdName);
      tr.appendChild(tdSeq);
      tr.appendChild(tdStat);
      tr.addEventListener("click", function () {
        selectedIndex = idx;
        Array.prototype.forEach.call(shotBody.querySelectorAll("tr"), function (x) {
          x.classList.remove("selected");
        });
        tr.classList.add("selected");
        const sid = r.shot_id;
        selectedInfo.textContent = "Selected: " + r.name + "  (id: " + sid + ")";
        renameBtn.disabled = false;
      });
      shotBody.appendChild(tr);
    });
    if (!rows.length) {
      selectedInfo.textContent = "No rows.";
      renameBtn.disabled = true;
    } else {
      selectedInfo.textContent = "Select a row in the table.";
      renameBtn.disabled = true;
    }
  }

  loadBtn.addEventListener("click", function () {
    const pid = projectId.value.trim();
    if (!pid) {
      setStatus("Enter a project id.", "err");
      return;
    }
    setStatus("Loading…", "");
    const q = queryParams();
    fetch("/shots?" + q.toString(), { headers: { Accept: "application/json" } })
      .then(function (res) {
        return res.json().then(function (body) {
          return { res: res, body: body };
        });
      })
      .then(function (_ref) {
        const res = _ref.res;
        const body = _ref.body;
        if (!res.ok) {
          setStatus(body.error || res.statusText, "err");
          shotBody.textContent = "";
          rows = [];
          selectedIndex = -1;
          renameBtn.disabled = true;
          return;
        }
        setStatus("Loaded " + (body.rows && body.rows.length) + " shot(s).", "ok");
        renderTable(body);
      })
      .catch(function (e) {
        setStatus(String(e), "err");
      });
  });

  renameBtn.addEventListener("click", function () {
    if (selectedIndex < 0 || !rows[selectedIndex]) {
      setStatus("Select a shot in the table first.", "err");
      return;
    }
    const nm = newName.value.trim();
    if (!nm) {
      setStatus("Enter a new name (e.g. SEQ02_01).", "err");
      return;
    }
    const r = rows[selectedIndex];
    const pid = projectId.value.trim();
    const pc = projectCode.value.trim();
    const payload = {
      project_id: pid,
      shot_id: r.shot_id,
      new_name: nm,
      project_code: pc || null
    };
    setStatus("Renaming…", "");
    fetch("/shots/rename?" + renameQuery(), {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify(payload)
    })
      .then(function (res) {
        return res.json().then(function (body) {
          return { res: res, body: body };
        });
      })
      .then(function (_ref2) {
        const res = _ref2.res;
        const body = _ref2.body;
        if (!res.ok) {
          setStatus(body.error || res.statusText, "err");
          return;
        }
        setStatus(body.message || "OK", "ok");
        loadBtn.click();
      })
      .catch(function (e) {
        setStatus(String(e), "err");
      });
  });
})();
</script>
</body>
</html>
"""
