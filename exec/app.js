/* app.js — BLN24 Executive Dashboard logic */

// ── Helpers ──────────────────────────────────────────────────────────────────
function fmtCurrency(v) {
  if (v >= 1e6)  return '$' + (v / 1e6).toFixed(2) + 'M';
  if (v >= 1e3)  return '$' + (v / 1e3).toFixed(0) + 'K';
  return '$' + v.toLocaleString();
}
function fmtPct(v) { return v.toFixed(1) + '%'; }

// Color helpers
function marginColor(v) { return v < 15 ? '#dc2626' : v < 18 ? '#b45309' : '#16a34a'; }
function burnColor(v)   { return v > 90  ? '#dc2626' : v > 80  ? '#b45309' : '#64748b'; }
function utilColor(v)   { return v < 60  ? '#dc2626' : v < 75  ? '#f59e0b' : '#0072CE'; }

function valClass(v, warnLow, dangerLow) {
  if (dangerLow !== undefined && v < dangerLow) return 'val-red';
  if (warnLow   !== undefined && v < warnLow)   return 'val-yellow';
  return 'val-green';
}

// ── Tab switching ─────────────────────────────────────────────────────────────
function showTab(name, el) {
  document.querySelectorAll('.tab-page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.getElementById('tab-' + name).classList.add('active');
  if (el) el.classList.add('active');
  // Close sidebar on mobile
  document.getElementById('sidebar').classList.remove('open');
}

function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('open');
}

// ── Render KPI cards ──────────────────────────────────────────────────────────
function renderKpis(containerId, cards) {
  const el = document.getElementById(containerId);
  if (!el) return;
  el.innerHTML = cards.map(c => `
    <div class="kpi-card ${c.variant || ''}">
      <div class="kpi-label">${c.label}</div>
      <div class="kpi-value">${c.value}</div>
      ${c.sub ? `<div class="kpi-sub">${c.sub}</div>` : ''}
    </div>`).join('');
}

// ── Exec Summary ──────────────────────────────────────────────────────────────
function renderExec(d) {
  const k = d.kpis;

  renderKpis('execKpis', [
    { label: 'Revenue MTD',     value: fmtCurrency(k.revenue_mtd),    sub: 'April 2026' },
    { label: 'Gross Margin',    value: fmtPct(k.margin_mtd),          sub: fmtCurrency(k.revenue_mtd - k.cost_mtd) + ' profit' },
    { label: 'Utilization',     value: fmtPct(k.utilization_pct),     sub: 'Target: 80%+',
      variant: k.utilization_pct < 75 ? 'warn' : k.utilization_pct >= 80 ? 'good' : '' },
    { label: 'Headcount',       value: k.headcount,                    sub: k.billable_headcount + ' billable' },
    { label: 'Not Billing',     value: k.not_billing_count,            sub: 'Billable staff, 0 hrs',
      variant: k.not_billing_count > 3 ? 'danger' : k.not_billing_count > 0 ? 'warn' : 'good' },
    { label: 'At-Risk Projects',value: k.at_risk_projects,             sub: 'Low margin or high burn',
      variant: k.at_risk_projects > 0 ? 'danger' : 'good' },
  ]);

  // Health table
  const tbody = document.getElementById('healthBody');
  tbody.innerHTML = d.health.map(h => {
    const dot   = h.status === 'green' ? '🟢' : h.status === 'yellow' ? '🟡' : '🔴';
    const flags = [];
    if (h.margin_pct  < 15)  flags.push('Low margin (' + fmtPct(h.margin_pct) + ')');
    if (h.burn_pct    > 90)  flags.push('High burn (' + fmtPct(h.burn_pct) + ')');
    if (h.utilization_pct < 65) flags.push('Low util (' + fmtPct(h.utilization_pct) + ')');
    const flagHtml = flags.map(f => `<span class="flag-tag">${f}</span>`).join('');
    const badge = `<span class="badge badge-${h.status}">${dot} ${h.status_label}</span>`;
    const rowCls = h.status === 'red' ? 'row-red' : h.status === 'yellow' ? 'row-yellow' : '';

    return `<tr class="${rowCls}">
      <td><strong>${h.client}</strong><br><small style="color:#94a3b8">${h.project_name.split('—').slice(1).join('—').trim() || h.project_name}</small></td>
      <td class="r">${fmtCurrency(h.revenue)}</td>
      <td class="r ${valClass(h.margin_pct, 18, 15)}">${fmtPct(h.margin_pct)}</td>
      <td class="r ${h.burn_pct > 90 ? 'val-red' : h.burn_pct > 80 ? 'val-yellow' : ''}">${fmtPct(h.burn_pct)}</td>
      <td class="r ${valClass(h.utilization_pct, 75, 60)}">${fmtPct(h.utilization_pct)}</td>
      <td class="r">${h.headcount}</td>
      <td>${badge} ${flagHtml}</td>
    </tr>`;
  }).join('');

  // Not billing
  const nbEl = document.getElementById('notBillingList');
  if (d.not_billing.length) {
    nbEl.innerHTML = d.not_billing.map(u =>
      `<li>👤 ${u.name} <span class="pill">${u.labor_cat}</span></li>`).join('');
  } else {
    nbEl.innerHTML = '<li>✅ All billable employees have logged hours</li>';
  }

  // Missing timesheets
  const mtEl = document.getElementById('missingTsList');
  if (d.missing_ts.length) {
    mtEl.innerHTML = d.missing_ts.map(u =>
      `<li>📄 ${u.name} <span class="pill">${u.project}</span></li>`).join('');
  } else {
    mtEl.innerHTML = '<li>✅ No missing timesheets</li>';
  }
}

// ── Financial Health ──────────────────────────────────────────────────────────
function renderFinancial(d) {
  const k = d.kpis;
  renderKpis('finKpis', [
    { label: 'Revenue MTD',    value: fmtCurrency(k.revenue_mtd),           sub: 'April 2026' },
    { label: 'Cost MTD',       value: fmtCurrency(k.cost_mtd),              sub: 'Direct project costs' },
    { label: 'Gross Profit',   value: fmtCurrency(k.revenue_mtd - k.cost_mtd), sub: fmtPct(k.margin_mtd) + ' margin', variant: 'good' },
  ]);

  const fin = d.financials_apr;
  const labels  = fin.map(f => f.client);
  const colors  = fin.map(f => f.color);

  // Revenue vs Cost
  new Chart(document.getElementById('revCostChart'), {
    type: 'bar',
    data: {
      labels,
      datasets: [
        { label: 'Revenue', data: fin.map(f => f.revenue), backgroundColor: '#0072CE', borderRadius: 4 },
        { label: 'Cost',    data: fin.map(f => f.cost),    backgroundColor: '#cbd5e1', borderRadius: 4 },
      ]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { position: 'top' } },
      scales: { y: { ticks: { callback: v => '$' + (v/1000).toFixed(0) + 'K' } } }
    }
  });

  // Margin horizontal bar
  new Chart(document.getElementById('marginChart'), {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Margin %',
        data: fin.map(f => f.margin_pct),
        backgroundColor: fin.map(f => marginColor(f.margin_pct)),
        borderRadius: 4,
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      indexAxis: 'y',
      plugins: { legend: { display: false } },
      scales: {
        x: { min: 0, max: 30, ticks: { callback: v => v + '%' } }
      }
    }
  });

  // YTD trend
  const months = Object.keys(d.ytd);
  new Chart(document.getElementById('ytdChart'), {
    type: 'line',
    data: {
      labels: months,
      datasets: [
        { label: 'Revenue', data: months.map(m => d.ytd[m].revenue), borderColor: '#0072CE', backgroundColor: 'rgba(0,114,206,0.08)', fill: true, tension: 0.35, pointRadius: 5 },
        { label: 'Cost',    data: months.map(m => d.ytd[m].cost),    borderColor: '#dc2626', backgroundColor: 'rgba(220,38,38,0.04)',  fill: true, tension: 0.35, pointRadius: 5 },
      ]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { position: 'top' } },
      scales: { y: { ticks: { callback: v => '$' + (v/1000).toFixed(0) + 'K' } } }
    }
  });

  // Fin table
  const tbody = document.getElementById('finBody');
  tbody.innerHTML = fin.map(f => `
    <tr>
      <td><strong>${f.client}</strong></td>
      <td class="r">${fmtCurrency(f.revenue)}</td>
      <td class="r">${fmtCurrency(f.cost)}</td>
      <td class="r">${fmtCurrency(f.revenue - f.cost)}</td>
      <td class="r ${valClass(f.margin_pct, 18, 15)}">${fmtPct(f.margin_pct)}</td>
      <td class="r ${f.burn_pct > 90 ? 'val-red' : f.burn_pct > 80 ? 'val-yellow' : ''}">${fmtPct(f.burn_pct)}</td>
    </tr>`).join('');
}

// ── Utilization ───────────────────────────────────────────────────────────────
function renderUtilization(d) {
  const k = d.kpis;
  renderKpis('utilKpis', [
    { label: 'Utilization Rate', value: fmtPct(k.utilization_pct), sub: 'Billable / total hours',
      variant: k.utilization_pct < 75 ? 'warn' : 'good' },
    { label: 'Billable Staff',   value: k.billable_headcount,       sub: 'of ' + k.headcount + ' total' },
    { label: 'Not Billing',      value: k.not_billing_count,        sub: '0 hrs this period',
      variant: k.not_billing_count > 0 ? 'warn' : 'good' },
  ]);

  // Gauge
  const utilPct = k.utilization_pct;
  document.getElementById('gaugeVal').textContent = fmtPct(utilPct);
  new Chart(document.getElementById('gaugeChart'), {
    type: 'doughnut',
    data: {
      datasets: [{
        data: [utilPct, 100 - utilPct],
        backgroundColor: [utilColor(utilPct), '#f1f5f9'],
        borderWidth: 0,
        circumference: 180,
        rotation: 270,
      }]
    },
    options: {
      responsive: false,
      cutout: '72%',
      plugins: { legend: { display: false }, tooltip: { enabled: false } }
    }
  });

  // Trend
  const t = d.util_trend;
  new Chart(document.getElementById('utilTrendChart'), {
    type: 'line',
    data: {
      labels: t.labels,
      datasets: [
        {
          label: 'Utilization %',
          data: t.values,
          borderColor: '#0072CE', backgroundColor: 'rgba(0,114,206,0.08)',
          fill: true, tension: 0.4, pointRadius: 5, pointBackgroundColor: '#0072CE',
        },
        {
          label: 'Target (80%)',
          data: Array(t.labels.length).fill(80),
          borderColor: '#dc2626', borderDash: [5, 5],
          pointRadius: 0, fill: false,
        }
      ]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { position: 'top' } },
      scales: { y: { min: 60, max: 100, ticks: { callback: v => v + '%' } } }
    }
  });

  // Employee bars
  const eu = d.util_employees;
  new Chart(document.getElementById('utilEmpChart'), {
    type: 'bar',
    data: {
      labels: eu.map(u => u.name),
      datasets: [{
        label: 'Utilization %',
        data: eu.map(u => u.pct),
        backgroundColor: eu.map(u => utilColor(u.pct)),
        borderRadius: 3,
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      indexAxis: 'y',
      plugins: { legend: { display: false } },
      scales: {
        x: { min: 0, max: 100, ticks: { callback: v => v + '%' }, grid: { color: '#f1f5f9' } },
        y: { ticks: { font: { size: 11 } } }
      }
    }
  });

  // Low util list
  const lowEl = document.getElementById('lowUtilList');
  const low = d.utilization.filter(u => u.utilization_pct > 0 && u.utilization_pct < 60)
    .sort((a,b) => a.utilization_pct - b.utilization_pct);
  lowEl.innerHTML = low.length
    ? low.map(u => `<li>👤 ${u.employee_name} <span class="pill val-red">${fmtPct(u.utilization_pct)}</span></li>`).join('')
    : '<li>✅ No employees below 60%</li>';

  // Missing TS
  const mt2 = document.getElementById('missingTsList2');
  mt2.innerHTML = d.missing_ts.length
    ? d.missing_ts.map(u => `<li>📄 ${u.name} <span class="pill">${u.project}</span></li>`).join('')
    : '<li>✅ No missing timesheets</li>';
}

// ── CPO Report ────────────────────────────────────────────────────────────────
function renderCPO(d) {
  const c = d.cpo;

  // Signal strip
  const sigEl = document.getElementById('cpoSignals');
  if (sigEl) {
    const icons = { red: '🔴', yellow: '🟡', green: '🟢' };
    sigEl.innerHTML = c.signals.map(function(s) {
      return '<div class="cpo-signal cpo-signal-' + s.level + '">' + (icons[s.level] || '') + ' ' + s.text + '</div>';
    }).join('');
  }

  // KPIs
  const k = c.kpis;
  const gapPct = ((k.bd_gap / k.bd_goal) * 100).toFixed(0);
  renderKpis('cpoKpis', [
    { label: 'Portfolio TCV',     value: fmtCurrency(k.portfolio_tcv),        sub: k.active_programs + ' active programs' },
    { label: 'BD Pipeline (Wtd)', value: fmtCurrency(k.bd_pipeline_weighted), sub: 'of $' + (k.bd_goal/1e6).toFixed(0) + 'M goal', variant: 'warn' },
    { label: 'BD Gap to Goal',    value: fmtCurrency(k.bd_gap),               sub: gapPct + '% shortfall', variant: 'danger' },
    { label: 'Active Vehicles',   value: k.active_vehicles,                    sub: 'GWACs, BPAs, IDIQs' },
    { label: 'Open Risks',        value: k.open_risks,                         sub: '1 red / 5 yellow', variant: k.open_risks > 0 ? 'warn' : 'good' },
    { label: 'Confirm Required',  value: k.contracts_needing_confirm,          sub: 'Contracts w/ lapsed dates', variant: k.contracts_needing_confirm > 0 ? 'danger' : 'good' },
  ]);

  // Portfolio table
  const pbody = document.getElementById('cpoPortfolioBody');
  if (pbody) {
    const healthDots = { green: '🟢', yellow: '🟡', red: '🔴' };
    pbody.innerHTML = c.portfolio.map(function(p) {
      const dot = healthDots[p.health] || '';
      const tcvStr = p.tcv >= 1e9 ? '$' + (p.tcv/1e9).toFixed(1) + 'B' : fmtCurrency(p.tcv);
      const rowCls = p.health === 'red' ? 'row-red' : p.health === 'yellow' ? 'row-yellow' : '';
      const endsColor = p.ends.indexOf('*') >= 0 ? 'var(--red)' : 'inherit';
      const marginStr = p.margin_pct !== null ? fmtPct(p.margin_pct) : '<span style="color:var(--gray-400)">N/A</span>';
      return '<tr class="' + rowCls + '">'
        + '<td style="color:var(--gray-400);font-weight:700">' + p.rank + '</td>'
        + '<td><strong>' + p.program + '</strong><br><small style="color:var(--gray-400)">' + p.note + '</small></td>'
        + '<td>' + p.agency + '</td>'
        + '<td class="r">' + tcvStr + '</td>'
        + '<td class="r">' + marginStr + '</td>'
        + '<td>' + dot + '</td>'
        + '<td><span style="font-size:11px;color:' + endsColor + '">' + p.ends + '</span></td>'
        + '</tr>';
    }).join('');
  }

  // Risk table
  const rbody = document.getElementById('cpoRiskBody');
  if (rbody) {
    const sevDots = { red: '🔴', yellow: '🟡', green: '🟢' };
    rbody.innerHTML = c.risks.map(function(r) {
      const dot = sevDots[r.severity] || '';
      const rowCls = r.severity === 'red' ? 'row-red' : r.severity === 'yellow' ? 'row-yellow' : '';
      return '<tr class="' + rowCls + '">'
        + '<td><strong>' + r.risk + '</strong></td>'
        + '<td><small>' + r.program + '</small></td>'
        + '<td>' + dot + '</td>'
        + '<td><small>' + r.action + '</small></td>'
        + '</tr>';
    }).join('');
  }

  // Pipeline meta bar
  const pmeta = document.getElementById('cpoPipelineMeta');
  if (pmeta) {
    pmeta.innerHTML = '<span class="cpo-meta-pill">Weighted: <strong>' + fmtCurrency(k.bd_pipeline_weighted) + '</strong></span>'
      + '&nbsp;<span class="cpo-meta-pill warn">Gap to $120M: <strong>' + fmtCurrency(k.bd_gap) + '</strong></span>'
      + '&nbsp;<span class="cpo-meta-pill muted">All opps at Identification — no captures assigned yet</span>';
  }

  // Pipeline table
  const pipeBody = document.getElementById('cpoPipelineBody');
  if (pipeBody) {
    pipeBody.innerHTML = c.pipeline.map(function(p) {
      const priClass = p.priority === 'High' ? 'badge-green' : p.priority === 'Medium' ? 'badge-yellow' : 'badge-gray';
      const revStr = p.bln24_rev > 0 ? fmtCurrency(p.bln24_rev) : '<span style="color:var(--gray-400)">TBD</span>';
      return '<tr>'
        + '<td><span class="badge ' + priClass + '">' + p.priority + '</span></td>'
        + '<td><strong>' + p.opp + '</strong></td>'
        + '<td>' + p.agency + '</td>'
        + '<td class="r">' + revStr + '</td>'
        + '<td style="font-weight:600;color:var(--navy-mid)">' + p.rfp + '</td>'
        + '<td>' + p.stage + '</td>'
        + '<td><small>' + p.vehicle + '</small></td>'
        + '</tr>';
    }).join('');
  }

  // Vehicles list
  const vEl = document.getElementById('cpoVehicleList');
  if (vEl) {
    vEl.innerHTML = c.vehicles.map(function(v) {
      return '<li>📋 <strong>' + v.name + '</strong> — ' + v.agency
        + ' <span class="pill">' + v.entity + '</span>'
        + ' <span style="color:var(--gray-400);font-size:11px">' + v.ends + '</span></li>';
    }).join('');
  }

  // CEO Action items
  const aEl = document.getElementById('cpoActionList');
  if (aEl) {
    const urgIcons = { red: '🔴', yellow: '🟡', green: '✅' };
    aEl.innerHTML = c.ceo_actions.map(function(a) {
      return '<li>' + (urgIcons[a.urgency] || '') + ' ' + a.action + '</li>';
    }).join('');
  }
}

// ── Bootstrap ─────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  // Timestamp
  const ts = document.getElementById('generatedTime');
  if (ts) ts.textContent = 'Updated ' + new Date().toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'});

  const d = BLN24_DATA;

  renderExec(d);
  renderFinancial(d);
  renderUtilization(d);
  renderCPO(d);
});
