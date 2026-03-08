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
    ['Overload', s.overloaded_owners],
    ['Throttle', s.throttle_mode],
    ['Corridor', s.priority_corridor],
    ['Queue', `${s.queue_pressure_band} (${s.queue_pressure_score})`],
    ['Bandwidth', `${s.bandwidth_mode} (${s.bandwidth_score})`],
    ['Intake', s.intake_guard],
    ['Capacity', `${s.intake_capacity_mode} (${s.intake_capacity_score})`],
    ['Admission', s.admission_state],
    ['Commitment', s.commitment_mode],
    ['Scope', `${s.scope_budget_mode} (${s.scope_budget_score})`],
    ['Window', s.admission_window],
    ['Guard', s.commitment_guard],
    ['Risk Budget', `${s.risk_budget_mode} (${s.risk_budget_score})`],
    ['Sync', s.delivery_intake_sync],
    ['Reserve', s.execution_reserve],
    ['Buffer', `${s.capacity_buffer_band} (${s.capacity_buffer_score})`],
    ['Queue Policy', s.intake_queue_policy],
    ['Rebalance', s.scope_rebalance],
    ['Flow', `${s.flow_control_mode} (${s.flow_control_score})`],
    ['Release Win', s.intake_release_window],
    ['Stability', s.execution_stability_guard],
    ['Marge Safety', `${s.safety_margin_band} (${s.safety_margin_score})`],
    ['Fenêtre Engage.', s.intake_commitment_window],
    ['Verrou Scope', s.scope_lock_state],
    ['Bande Débit', `${s.throughput_guard_band} (${s.throughput_guard_score})`],
    ['Slots Intake', s.intake_slot_policy],
    ['Gel Scope', s.scope_freeze_guard],
    ['Stress Delivery', `${s.delivery_stress_band} (${s.delivery_stress_score})`],
    ['Fenêtre Pacing', s.intake_pacing_window],
    ['Gate Scope', s.scope_transition_gate],
    ['Readiness Transit.', `${s.transition_readiness_band} (${s.transition_readiness_score})`],
    ['Politique Transit.', s.intake_transition_policy],
    ['Gate Admission', s.scope_admission_gate],
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
    <p>Conformité Policy: ${badge(data.status.policy_compliance)} | Confiance: ${badge(data.status.execution_confidence_band)} | Mode: ${badge(data.status.execution_mode)} | Momentum: ${badge(data.status.momentum_posture)} (${data.status.momentum_index}) | Pression: ${badge(data.status.pressure_level)} (${data.status.pressure_index}) | Température: ${badge(data.status.temperature)} (${data.status.temperature_index}) | Contrôle: ${badge(data.status.control_mode)} | Efficience: ${badge(data.status.efficiency_band)} (${data.status.efficiency_score}) | Intervention: ${badge(data.status.intervention_mode)} | Friction: ${badge(data.status.friction_band)} (${data.status.friction_score}) | Cadence: ${badge(data.status.cadence)} | Focus: <b>${data.status.focus_items}</b> | Owners: <b>${data.status.owners_in_scope}</b> | Surcharge: <b>${data.status.overloaded_owners}</b> | Throttle: ${badge(data.status.throttle_mode)} | Corridor: ${badge(data.status.priority_corridor)} | File: ${badge(data.status.queue_pressure_band)} (${data.status.queue_pressure_score}) | Bande passante: ${badge(data.status.bandwidth_mode)} (${data.status.bandwidth_score}) | Intake: ${badge(data.status.intake_guard)} | Capacité: ${badge(data.status.intake_capacity_mode)} (${data.status.intake_capacity_score}) | Admission: ${badge(data.status.admission_state)} | Engagement: ${badge(data.status.commitment_mode)} | Scope: ${badge(data.status.scope_budget_mode)} (${data.status.scope_budget_score}) | Fenêtre: ${badge(data.status.admission_window)} | Garde: ${badge(data.status.commitment_guard)} | Budget Risque: ${badge(data.status.risk_budget_mode)} (${data.status.risk_budget_score}) | Sync: ${badge(data.status.delivery_intake_sync)} | Réserve: ${badge(data.status.execution_reserve)} | Buffer: ${badge(data.status.capacity_buffer_band)} (${data.status.capacity_buffer_score}) | Politique File: ${badge(data.status.intake_queue_policy)} | Rebalance: ${badge(data.status.scope_rebalance)} | Flux: ${badge(data.status.flow_control_mode)} (${data.status.flow_control_score}) | Fenêtre Release: ${badge(data.status.intake_release_window)} | Garde Stabilité: ${badge(data.status.execution_stability_guard)} | Marge Safety: ${badge(data.status.safety_margin_band)} (${data.status.safety_margin_score}) | Fenêtre Engagement: ${badge(data.status.intake_commitment_window)} | Verrou Scope: ${badge(data.status.scope_lock_state)} | Bande Débit: ${badge(data.status.throughput_guard_band)} (${data.status.throughput_guard_score}) | Slots Intake: ${badge(data.status.intake_slot_policy)} | Gel Scope: ${badge(data.status.scope_freeze_guard)} | Stress Delivery: ${badge(data.status.delivery_stress_band)} (${data.status.delivery_stress_score}) | Fenêtre Pacing: ${badge(data.status.intake_pacing_window)} | Gate Scope: ${badge(data.status.scope_transition_gate)} | Readiness Transition: ${badge(data.status.transition_readiness_band)} (${data.status.transition_readiness_score}) | Politique Transition: ${badge(data.status.intake_transition_policy)} | Gate Admission Scope: ${badge(data.status.scope_admission_gate)} | Taux validation: <b>${v.valid_rate}%</b></p>
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
