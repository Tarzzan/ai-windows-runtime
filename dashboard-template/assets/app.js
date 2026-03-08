async function loadData() {
  if (window.__DASHBOARD_DATA__) return window.__DASHBOARD_DATA__;
  const res = await fetch('data/dashboard-data.json');
  if (!res.ok) throw new Error('Impossible de charger dashboard-data.json');
  return res.json();
}

function badge(value) {
  const v = String(value || '').toLowerCase();
  if (['pass', 'go', 'ready', 'compliant'].includes(v)) return `<span class="badge good">${value}</span>`;
  if (['warn', 'limited', 'missing'].includes(v)) return `<span class="badge warn">${value}</span>`;
  return `<span class="badge bad">${value}</span>`;
}

function renderKPIs(data) {
  const p = data.progress;
  const s = data.status;
  const q = data.quality.validation;
  const el = document.getElementById('kpis');
  const items = [
    ['Avancement', `${p.progress_percent}%`],
    ['Phase Actuelle', `P${p.current_phase}`],
    ['Capabilities', p.capabilities_count],
    ['Validation', `${q.valid}/${q.total}`],
    ['Policy', s.policy_status],
    ['Confidence', s.execution_confidence_band],
    ['Momentum', `${s.momentum_posture} (${s.momentum_index})`],
    ['Pressure', `${s.pressure_level} (${s.pressure_index})`],
    ['Temperature', `${s.temperature} (${s.temperature_index})`],
    ['Control', s.control_mode],
    ['Efficiency', `${s.efficiency_band} (${s.efficiency_score})`],
    ['Intervention', s.intervention_mode],
    ['Friction', `${s.friction_band} (${s.friction_score})`],
    ['Cadence', s.cadence],
    ['Focus', s.focus_items],
    ['Owners', s.owners_in_scope],
  ];
  el.innerHTML = items.map(([label, value]) => `<div class="kpi"><div class="label">${label}</div><div class="value">${value}</div></div>`).join('');
}

function renderMeta(data) {
  const m = data.meta;
  const c = m.latest_commit || {};
  document.getElementById('meta').innerHTML = `Branch <b>${m.branch || '-'}</b> | Commit <b>${c.short || '-'}</b> | ${c.subject || ''} | Généré: ${m.generated_at}`;
}

function renderTimeline(data, search = '', phaseFilter = 'all') {
  const items = data.timeline.filter((p) => {
    if (phaseFilter !== 'all' && p.status !== phaseFilter) return false;
    const blob = `${p.phase} ${p.title} ${p.slug} ${p.file}`.toLowerCase();
    return blob.includes(search.toLowerCase());
  });
  document.getElementById('timeline').innerHTML = items.map((p) => `
    <article class="phase ${p.status}">
      <div class="title">Phase ${p.phase} - ${p.title}</div>
      <div>Statut: ${badge(p.status)}</div>
      <div class="file">${p.file}</div>
    </article>`).join('');
}

function renderLists(data) {
  const inProgress = document.getElementById('inProgress');
  inProgress.innerHTML = data.in_progress.map((i) => `<li>Phase ${i.phase}: ${i.title}</li>`).join('') || '<li>Aucune entrée</li>';

  const remaining = document.getElementById('remaining');
  remaining.innerHTML = data.remaining_backlog.slice(0, 15).map((x) => `<li>${x}</li>`).join('') || '<li>Aucune entrée</li>';

  const actions = document.getElementById('actions');
  actions.innerHTML = data.next_actions.map((x) => `<li>${x}</li>`).join('') || '<li>Aucune action détectée</li>';

  const commits = document.getElementById('commits');
  commits.innerHTML = data.commits.slice(0, 10).map((c) => `<li><b>${c.short}</b> ${c.subject}</li>`).join('') || '<li>Aucun commit</li>';
}

function renderQuality(data) {
  const q = data.quality;
  const v = q.validation;
  document.getElementById('quality').innerHTML = `
    <p>Quality Gate: ${badge(data.status.quality_gate)} | Release Decision: ${badge(data.status.release_decision)} | Launch: ${badge(data.status.launch_readiness)}</p>
    <p>Policy Compliance: ${badge(data.status.policy_compliance)} | Confidence: ${badge(data.status.execution_confidence_band)} | Mode: ${badge(data.status.execution_mode)} | Momentum: ${badge(data.status.momentum_posture)} (${data.status.momentum_index}) | Pressure: ${badge(data.status.pressure_level)} (${data.status.pressure_index}) | Temperature: ${badge(data.status.temperature)} (${data.status.temperature_index}) | Control: ${badge(data.status.control_mode)} | Efficiency: ${badge(data.status.efficiency_band)} (${data.status.efficiency_score}) | Intervention: ${badge(data.status.intervention_mode)} | Friction: ${badge(data.status.friction_band)} (${data.status.friction_score}) | Cadence: ${badge(data.status.cadence)} | Focus: <b>${data.status.focus_items}</b> | Owners: <b>${data.status.owners_in_scope}</b> | Validation rate: <b>${v.valid_rate}%</b></p>
    <p>Invalid reports: ${v.invalid}</p>`;
}

function renderRisks(data, search = '') {
  const rs = data.risks.summary || {};
  document.getElementById('riskSummary').innerHTML = `P0: <b>${rs.p0_entries || 0}</b> | P1: <b>${rs.p1_entries || 0}</b> | P2: <b>${rs.p2_entries || 0}</b> | Policy: ${badge(rs.release_policy_status || 'missing')}`;

  const rows = (data.risks.entries || []).filter((r) => {
    const blob = `${r.id} ${r.priority} ${r.kind} ${r.detail}`.toLowerCase();
    return blob.includes(search.toLowerCase());
  });
  document.querySelector('#riskTable tbody').innerHTML = rows.map((r) => `<tr><td>${r.id}</td><td>${badge(r.priority)}</td><td>${r.kind}</td><td>${r.detail}</td></tr>`).join('');
}

function bindFilters(data) {
  const s = document.getElementById('search');
  const p = document.getElementById('phaseFilter');
  const render = () => {
    renderTimeline(data, s.value, p.value);
    renderRisks(data, s.value);
  };
  s.addEventListener('input', render);
  p.addEventListener('change', render);
}

(async function main() {
  try {
    const data = await loadData();
    renderMeta(data);
    renderKPIs(data);
    renderTimeline(data);
    renderLists(data);
    renderQuality(data);
    renderRisks(data);
    bindFilters(data);
  } catch (e) {
    document.body.innerHTML = `<pre>Erreur dashboard: ${String(e)}</pre>`;
  }
})();
