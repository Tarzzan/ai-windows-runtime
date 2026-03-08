async function loadData() {
  if (window.__DASHBOARD_DATA__) return window.__DASHBOARD_DATA__;
  const res = await fetch('data/dashboard-data.json');
  if (!res.ok) throw new Error('Impossible de charger dashboard-data.json');
  return res.json();
}

function frStatus(value) {
  const map = {
    pass: 'ok',
    go: 'go',
    ready: 'pret',
    compliant: 'conforme',
    warn: 'alerte',
    limited: 'limite',
    missing: 'manquant',
    fail: 'echec',
    blocked: 'bloque',
    closed: 'ferme',
    hold: 'attente',
    in_progress: 'en cours',
    completed: 'terminee',
    planned: 'planifiee',
  };
  const key = String(value || '').toLowerCase();
  return map[key] || String(value || 'inconnu');
}

function badge(value) {
  const raw = String(value || '').toLowerCase();
  const label = frStatus(value);
  if (['pass', 'go', 'ready', 'compliant', 'open', 'advance', 'stable'].includes(raw)) {
    return `<span class="badge good">${label}</span>`;
  }
  if (['warn', 'limited', 'missing', 'watch', 'guarded', 'stage', 'moderate'].includes(raw)) {
    return `<span class="badge warn">${label}</span>`;
  }
  return `<span class="badge bad">${label}</span>`;
}

function renderKPIs(data) {
  const p = data.progress;
  const s = data.status;
  const q = data.quality.validation;
  const el = document.getElementById('kpis');
  const items = [
    ['Avancement', `${p.progress_percent}%`],
    ['Phase actuelle', `P${p.current_phase}`],
    ['Capacites', p.capabilities_count],
    ['Validations', `${q.valid}/${q.total}`],
    ['Policy', s.policy_status],
    ['Confiance', s.execution_confidence_band],
    ['Temperature', `${s.temperature} (${s.temperature_index})`],
    ['Intervention', s.intervention_mode],
    ['P0 risques', data.risks?.summary?.p0_entries || 0],
    ['Gate scope', s.scope_transition_gate],
    ['Readiness', `${s.transition_readiness_band} (${s.transition_readiness_score})`],
    ['Admission', s.scope_admission_gate],
    ['Reentree', `${s.scope_reentry_readiness_band} (${s.scope_reentry_readiness_score})`],
    ['Reprise intake', s.intake_resumption_policy],
    ['Deblocage', s.scope_unlock_gate],
  ];
  el.innerHTML = items
    .map(
      ([label, value]) =>
        `<div class="kpi"><div class="label">${label}</div><div class="value">${value}</div></div>`,
    )
    .join('');
}

function renderMeta(data) {
  const m = data.meta || {};
  const c = m.latest_commit || {};
  const date = m.generated_at ? new Date(m.generated_at).toLocaleString('fr-FR') : '-';
  document.getElementById('meta').innerHTML =
    `Branche <b>${m.branch || '-'}</b> | Commit <b>${c.short || '-'}</b> | ${c.subject || ''} | Genere: ${date}`;
}

function renderTimeline(data, search = '', phaseFilter = 'all') {
  const items = (data.timeline || []).filter((p) => {
    if (phaseFilter !== 'all' && p.status !== phaseFilter) return false;
    const blob = `${p.phase} ${p.title} ${p.slug} ${p.file}`.toLowerCase();
    return blob.includes(search.toLowerCase());
  });
  document.getElementById('timeline').innerHTML = items
    .map(
      (p) => `
    <article class="phase ${p.status}">
      <div class="title">Phase ${p.phase} - ${p.title}</div>
      <div>Statut: ${badge(p.status)}</div>
      <div class="file">${p.file}</div>
    </article>`,
    )
    .join('');
}

function renderLists(data) {
  const inProgress = document.getElementById('inProgress');
  inProgress.innerHTML =
    (data.in_progress || []).map((i) => `<li>Phase ${i.phase}: ${i.title}</li>`).join('') ||
    '<li>Aucune entree</li>';

  const remaining = document.getElementById('remaining');
  remaining.innerHTML =
    (data.remaining_backlog || [])
      .slice(0, 15)
      .map((x) => `<li>${x}</li>`)
      .join('') || '<li>Aucune entree</li>';

  const actions = document.getElementById('actions');
  actions.classList.add('actions-priority');
  actions.innerHTML =
    (data.next_actions || [])
      .map((x, idx) => {
        const prio = idx < 3 ? 'priority-high' : idx < 8 ? 'priority-mid' : 'priority-low';
        return `<li class="${prio}"><b>P${idx + 1}</b> - ${x}</li>`;
      })
      .join('') || '<li>Aucune action detectee</li>';

  const commits = document.getElementById('commits');
  commits.innerHTML =
    (data.commits || [])
      .slice(0, 10)
      .map((c) => `<li><b>${c.short}</b> ${c.subject}</li>`)
      .join('') || '<li>Aucun commit</li>';
}

function renderQuality(data) {
  const s = data.status;
  const v = data.quality?.validation || {};
  document.getElementById('quality').innerHTML = `
    <p>Decision release: ${badge(s.release_decision)} | Lancement: ${badge(s.launch_readiness)} | Policy: ${badge(s.policy_status)} (${badge(s.policy_compliance)})</p>
    <p>Confiance: ${badge(s.execution_confidence_band)} | Temperature: ${badge(s.temperature)} | Controle: ${badge(s.control_mode)} | Intervention: ${badge(s.intervention_mode)}</p>
    <p>Transition scope: ${badge(s.scope_transition_gate)} | Readiness transition: ${badge(s.transition_readiness_band)} (${s.transition_readiness_score}) | Politique intake: ${badge(s.intake_transition_policy)} | Admission scope: ${badge(s.scope_admission_gate)} | Reentree scope: ${badge(s.scope_reentry_readiness_band)} (${s.scope_reentry_readiness_score}) | Politique reprise: ${badge(s.intake_resumption_policy)} | Gate deblocage: ${badge(s.scope_unlock_gate)}</p>
    <p>Taux de validation: <b>${v.valid_rate || 0}%</b> | Rapports invalides: <b>${v.invalid || 0}</b></p>`;
}

function renderRisks(data, search = '') {
  const rs = data.risks?.summary || {};
  document.getElementById('riskSummary').innerHTML =
    `P0: <b>${rs.p0_entries || 0}</b> | P1: <b>${rs.p1_entries || 0}</b> | P2: <b>${rs.p2_entries || 0}</b> | Policy: ${badge(rs.release_policy_status || 'missing')}`;

  const rows = (data.risks?.entries || []).filter((r) => {
    const blob = `${r.id} ${r.priority} ${r.kind} ${r.detail}`.toLowerCase();
    return blob.includes(search.toLowerCase());
  });
  document.querySelector('#riskTable tbody').innerHTML = rows
    .map((r) => `<tr><td>${r.id}</td><td>${badge(r.priority)}</td><td>${r.kind}</td><td>${r.detail}</td></tr>`)
    .join('');
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
