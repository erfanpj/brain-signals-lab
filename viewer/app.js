const MANIFEST_URL = "data-manifest.json";

const state = {
  evaluation: null,
  eegnet: null,
  folds: null,
  inventory: null,
  manifest: null,
};

const CHART_PLOT_H = 180;

function pct(x, digits = 1) {
  return `${(x * 100).toFixed(digits)}%`;
}

/** Accuracy difference or SD expressed as percentage points (not relative % change). */
function ppPoints(rate, digits = 1) {
  return `${(rate * 100).toFixed(digits)} pp`;
}

function accuracyBarHeight(acc) {
  const clamped = Math.max(0, Math.min(1, acc));
  return Math.max(2, clamped * CHART_PLOT_H);
}

function subjectLabel(id) {
  return `S${String(id).padStart(3, "0")}`;
}

function scrollRegionAttrs(label) {
  return `class="table-scroll" tabindex="0" role="region" aria-label="${label}"`;
}

function bandLabel(selected) {
  if (!selected?.band_hz) return "—";
  const [lo, hi] = selected.band_hz;
  return `${lo}–${hi} Hz, ${selected.csp_components} CSP`;
}

async function loadJson(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Failed to load ${url}: ${res.status}`);
  return res.json();
}

function setPanel(name) {
  document.querySelectorAll("nav button").forEach((btn) => {
    const on = btn.dataset.panel === name;
    if (on) {
      btn.setAttribute("aria-current", "page");
    } else {
      btn.removeAttribute("aria-current");
    }
  });
  document.querySelectorAll(".panel").forEach((panel) => {
    const id = panel.id.replace("panel-", "");
    const active = id === name;
    panel.classList.toggle("active", active);
    panel.hidden = !active;
  });
}

function renderProtocolStats() {
  const el = document.getElementById("protocol-stats");
  const ev = state.evaluation;
  el.innerHTML = `
    <div class="stat"><div class="label">Outer folds</div><div class="value">5</div><div class="source">splits/FROZEN_participant_folds.json</div></div>
    <div class="stat"><div class="label">Participants</div><div class="value">50</div><div class="source">config/subset.json</div></div>
    <div class="stat"><div class="label">Epoch window</div><div class="value">${ev.window_s[0]}–${ev.window_s[1]} s</div><div class="source">reports/evaluation.json</div></div>
    <div class="stat"><div class="label">Permutation tests</div><div class="value">${ev.n_permutations}× / fold</div><div class="source">reports/evaluation.json</div></div>
  `;

  const rows = Object.entries(state.folds.folds)
    .map(([k, ids]) => {
      const testIds = ids.map(subjectLabel).join(", ");
      return `<tr><td>${k}</td><td>${testIds}</td><td>${ids.length} held out</td></tr>`;
    })
    .join("");
  document.getElementById("fold-table-wrap").innerHTML = `
    <div ${scrollRegionAttrs("Frozen outer fold assignments; scroll horizontally on narrow screens")}><table>
      <thead><tr><th>Fold</th><th>Test participants</th><th>Note</th></tr></thead>
      <tbody>${rows}</tbody>
    </table></div>
  `;
}

function renderEvalSummary() {
  const ev = state.evaluation;
  const nn = state.eegnet;
  document.getElementById("eval-summary").innerHTML = `
    <div class="stat"><div class="label">CSP+LDA mean ± SD</div><div class="value">${pct(ev.csp_lda_fold_mean)} ± ${ppPoints(ev.csp_lda_fold_sd)}</div><div class="source">evaluation.json → csp_lda_fold_mean/sd</div></div>
    <div class="stat"><div class="label">Chance dummy</div><div class="value">${pct(ev.chance_dummy_fold_mean)} ± ${ppPoints(ev.chance_dummy_fold_sd)}</div><div class="source">evaluation.json</div></div>
    <div class="stat"><div class="label">EEGNet-R mean ± SD</div><div class="value">${pct(nn.eegnet_r_fold_mean)} ± ${ppPoints(nn.eegnet_r_fold_sd)}</div><div class="source">eegnet_reduced.json</div></div>
    <div class="stat"><div class="label">Participant median</div><div class="value">${pct(ev.participant_acc.median)}</div><div class="source">evaluation.json → participant_acc.median</div></div>
  `;

  const chart = document.getElementById("fold-chart");
  const foldEntries = Object.entries(ev.folds);
  const ariaParts = [];
  const groups = foldEntries
    .map(([foldId, f]) => {
      const nnFold = nn.folds[foldId];
      const chH = accuracyBarHeight(f.chance_dummy_acc);
      const cspH = accuracyBarHeight(f.csp_lda_acc);
      const nnH = accuracyBarHeight(nnFold.eegnet_r_acc);
      ariaParts.push(
        `Fold ${foldId}: Dummy ${pct(f.chance_dummy_acc)}, CSP+LDA ${pct(f.csp_lda_acc)}, EEGNet-R ${pct(nnFold.eegnet_r_acc)}`,
      );
      return `
        <div class="bar-group-plot">
          <div class="bars">
            <div class="bar chance" style="height:${chH}px" title="Dummy ${pct(f.chance_dummy_acc)}"><span class="bar-value">${pct(f.chance_dummy_acc)}</span></div>
            <div class="bar csp" style="height:${cspH}px" title="CSP+LDA ${pct(f.csp_lda_acc)}"><span class="bar-value">${pct(f.csp_lda_acc)}</span></div>
            <div class="bar nn" style="height:${nnH}px" title="EEGNet-R ${pct(nnFold.eegnet_r_acc)}"><span class="bar-value">${pct(nnFold.eegnet_r_acc)}</span></div>
          </div>
          <div class="bar-caption">Fold ${foldId}</div>
        </div>`;
    })
    .join("");
  const yAxis = [100, 50, 0]
    .map((tick) => {
      const cls = tick === 0 ? "y-tick tick-zero" : "y-tick";
      const top = tick === 100 ? "0%" : tick === 50 ? "50%" : "100%";
      return `<div class="${cls}" style="top:${top}"><span>${tick}%</span></div>`;
    })
    .join("");
  chart.innerHTML = `
    <div class="fold-chart-block">
      <div class="chart-legend" aria-hidden="true">
        <span class="legend-item"><span class="swatch chance"></span> Dummy</span>
        <span class="legend-item"><span class="swatch csp"></span> CSP+LDA</span>
        <span class="legend-item"><span class="swatch nn"></span> EEGNet-R</span>
      </div>
      <p class="chart-scale-note">Bar heights use a 0–100% accuracy scale (50% is mid-height on the axis).</p>
      <div class="chart-plot-row">
        <div class="y-axis" aria-hidden="true">${yAxis}</div>
        <div class="bar-plot-area">
          <div class="bar-chart-plot" tabindex="0" role="region" aria-label="Per-fold accuracy bars; scroll horizontally on narrow screens">
            <div class="bar-chart" role="img" aria-label="${ariaParts.join(". ")}">${groups}</div>
          </div>
        </div>
      </div>
    </div>`;

  const nnRows = Object.entries(ev.folds)
    .map(([foldId, f]) => {
      const nnF = nn.folds[foldId];
      return `<tr>
        <td>${foldId}</td>
        <td>${bandLabel(f.selected)}</td>
        <td>${pct(f.csp_lda_acc)}</td>
        <td>${pct(nnF.eegnet_r_acc)}</td>
        <td>${pct(f.chance_dummy_acc)}</td>
        <td>${ppPoints(nnF.diff_vs_csp_lda, 1)}</td>
      </tr>`;
    })
    .join("");
  document.getElementById("nn-table-wrap").innerHTML = `
    <div ${scrollRegionAttrs("CSP+LDA vs EEGNet-R per fold; scroll horizontally on narrow screens")}><table>
      <thead><tr><th>Fold</th><th>CSP config (train only)</th><th>CSP+LDA</th><th>EEGNet-R</th><th>Dummy</th><th>NN − CSP</th></tr></thead>
      <tbody>${nnRows}</tbody>
    </table></div>
  `;
}

function renderParticipants() {
  const tbody = () => {
    const filterBelow = document.getElementById("filter-below").checked;
    const sort = document.getElementById("sort-participants").value;
    let entries = Object.entries(state.evaluation.participants).map(([id, p]) => ({
      id: Number(id),
      ...p,
    }));
    if (filterBelow) entries = entries.filter((p) => p.accuracy < 0.5);
    entries.sort((a, b) => {
      if (sort === "acc-asc") return a.accuracy - b.accuracy;
      if (sort === "acc-desc") return b.accuracy - a.accuracy;
      return a.id - b.id;
    });
    return entries
      .map((p) => {
        const below = p.accuracy < 0.5;
        const pval = p["p_binom_vs_0.5"];
        return `<tr class="${below ? "below-chance" : ""}">
          <td>${subjectLabel(p.id)}</td>
          <td>${p.fold}</td>
          <td>${p.n}</td>
          <td>${p.correct}</td>
          <td>${pct(p.accuracy)}</td>
          <td>${pct(p.ci95[0], 1)} <span class="ci-note">(one-sided 95% LB)</span></td>
          <td>${pval < 0.001 ? pval.toExponential(2) : pval.toFixed(3)}</td>
          <td>${p.above_chance_holm ? "yes" : "no"}</td>
        </tr>`;
      })
      .join("");
  };

  const wrap = document.getElementById("participant-table-wrap");
  const draw = () => {
    wrap.innerHTML = `
      <div ${scrollRegionAttrs("Participant accuracies; scroll horizontally on narrow screens")}><table>
        <thead><tr><th>Participant</th><th>Fold</th><th>Trials</th><th>Correct</th><th>Accuracy</th><th>One-sided 95% lower bound</th><th>p (one-sided vs 0.5)</th><th>Holm (50 tests)</th></tr></thead>
        <tbody>${tbody()}</tbody>
      </table></div>`;
  };
  draw();
  document.getElementById("filter-below").addEventListener("change", draw);
  document.getElementById("sort-participants").addEventListener("change", draw);
}

function renderSignal() {
  const inv = state.inventory;
  const man = state.manifest.signal_viewer;
  document.getElementById("signal-notice").textContent = man.reason;
  document.getElementById("signal-stats").innerHTML = `
    <div class="stat"><div class="label">Sampling rate</div><div class="value">${inv.sfreq_values[0]} Hz</div><div class="source">data_inventory.json</div></div>
    <div class="stat"><div class="label">Channels</div><div class="value">${inv.channel_names.length}</div><div class="source">data_inventory.json</div></div>
    <div class="stat"><div class="label">Recordings</div><div class="value">${inv.n_recordings}</div><div class="source">data_inventory.json</div></div>
    <div class="stat"><div class="label">Licence</div><div class="value">ODC-By 1.0</div><div class="source">PhysioNet / DATA.md</div></div>
  `;
  document.getElementById("channel-grid").innerHTML = inv.channel_names
    .map((c) => `<span>${c}</span>`)
    .join("");
}

async function init() {
  document.querySelectorAll("nav button").forEach((btn) => {
    btn.addEventListener("click", () => setPanel(btn.dataset.panel));
  });

  try {
    state.manifest = await loadJson(MANIFEST_URL);
    const base = "..";
    const paths = state.manifest.artifacts;
    state.evaluation = await loadJson(`${base}/${paths.evaluation}`);
    state.eegnet = await loadJson(`${base}/${paths.eegnet_reduced}`);
    state.folds = await loadJson(`${base}/${paths.frozen_folds}`);
    state.inventory = await loadJson(`${base}/${paths.data_inventory}`);
    document.getElementById("load-status").textContent =
      "Loaded saved reports. No models were trained in this session.";
    renderProtocolStats();
    renderEvalSummary();
    renderParticipants();
    renderSignal();
  } catch (err) {
    document.getElementById("load-status").textContent = `Could not load reports: ${err.message}. Serve the repository root (not viewer/ alone) with a local HTTP server.`;
    console.error(err);
  }
}

init();
