/* ============================================================
   DevPulse — Dashboard JS
   ============================================================ */

const LANG_COLORS = [
  '#58a6ff', '#bc8cff', '#39d353', '#f0883e', '#f85149',
  '#79c0ff', '#d2a8ff', '#56e36b', '#ffc680', '#ff7b72',
  '#a5d6ff', '#e2c5ff', '#7ee787', '#ffa657', '#ffa198',
];

let langChart = null;
let hourlyChart = null;
let weeklyChart = null;
let pollInterval = null;

document.addEventListener('DOMContentLoaded', () => {
  if (window.DEVPULSE_SYNCING) {
    startPolling();
  } else {
    loadStats();
  }
});

function startPolling() {
  pollInterval = setInterval(async () => {
    const res = await fetch('/api/status');
    const data = await res.json();
    if (data.synced) {
      clearInterval(pollInterval);
      document.getElementById('sync-banner').classList.add('hidden');
      const main = document.getElementById('dashboard-content');
      main.style.opacity = '1';
      main.style.pointerEvents = 'auto';
      loadStats();
    }
  }, 4000);
}

async function loadStats() {
  try {
    const res = await fetch('/api/stats');
    const data = await res.json();
    if (data.syncing) { startPolling(); return; }
    updateStatCards(data);
    renderHeatmap(data.commit_heatmap || {});
    renderLangChart(data.language_stats || {});
    renderHourlyChart(data.hourly_activity || {});
    renderWeeklyChart(data.weekly_activity || {});
    renderTopRepos(data.top_repos || []);
    updatePeakLabels(data);
  } catch (err) {
    console.error('Failed to load stats:', err);
  }
}

function updateStatCards(data) {
  const set = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val ?? '—'; };
  set('stat-commits', data.total_commits?.toLocaleString());
  set('stat-repos', data.total_repos);
  set('stat-stars', data.total_stars?.toLocaleString());
  set('stat-streak', data.longest_streak ? `${data.longest_streak}d` : '—');
  set('stat-lang', data.top_language);
  set('stat-current-streak', data.current_streak ? `${data.current_streak}d` : '—');
}

function updatePeakLabels(data) {
  const hourEl = document.getElementById('peak-hour-label');
  const dayEl = document.getElementById('peak-day-label');
  if (hourEl && data.peak_coding_hour !== undefined) {
    const h = data.peak_coding_hour;
    const ampm = h >= 12 ? 'PM' : 'AM';
    const h12 = h % 12 || 12;
    hourEl.textContent = `Peak activity at ${h12}:00 ${ampm}`;
  }
  if (dayEl && data.peak_coding_day) {
    dayEl.textContent = `Most active on ${data.peak_coding_day}s`;
  }
}

function renderHeatmap(heatmapData) {
  const container = document.getElementById('commit-heatmap');
  const monthsEl = document.getElementById('heatmap-months');
  if (!container) return;
  container.innerHTML = '';
  if (monthsEl) monthsEl.innerHTML = '';

  const today = new Date();
  const start = new Date(today);
  start.setDate(today.getDate() - 364);
  const startDow = start.getDay();
  start.setDate(start.getDate() - startDow);

  const maxVal = Math.max(...Object.values(heatmapData), 1);
  const months = [];
  let colCount = 0;
  let lastMonth = -1;
  const cur = new Date(start);

  while (cur <= today) {
    const col = document.createElement('div');
    col.style.cssText = 'display:grid;grid-template-rows:repeat(7,12px);gap:2px';

    for (let d = 0; d < 7; d++) {
      const cell = document.createElement('div');
      cell.className = 'heatmap-cell';

      if (cur <= today && cur >= new Date(today.getFullYear() - 1, today.getMonth(), today.getDate())) {
        const key = cur.toISOString().split('T')[0];
        const count = heatmapData[key] || 0;
        const level = count === 0 ? 0
          : count <= Math.ceil(maxVal * 0.25) ? 1
          : count <= Math.ceil(maxVal * 0.5) ? 2
          : count <= Math.ceil(maxVal * 0.75) ? 3 : 4;
        cell.classList.add(`level-${level}`);
        cell.title = `${key}: ${count} commit${count !== 1 ? 's' : ''}`;
      } else {
        cell.style.visibility = 'hidden';
      }

      if (cur.getMonth() !== lastMonth && d === 0) {
        months.push({ col: colCount, name: cur.toLocaleString('default', { month: 'short' }) });
        lastMonth = cur.getMonth();
      }

      col.appendChild(cell);
      cur.setDate(cur.getDate() + 1);
    }

    container.appendChild(col);
    colCount++;
  }

  if (monthsEl && months.length) {
    months.forEach(m => {
      const label = document.createElement('div');
      label.className = 'heatmap-month-label';
      label.textContent = m.name;
      label.style.width = `${(1 / colCount) * 100}%`;
      monthsEl.appendChild(label);
    });
  }
}

function renderLangChart(langStats) {
  const canvas = document.getElementById('lang-chart');
  const legendEl = document.getElementById('lang-legend');
  if (!canvas) return;
  const entries = Object.entries(langStats).slice(0, 8);
  if (!entries.length) return;

  const labels = entries.map(([l]) => l);
  const values = entries.map(([, v]) => v);
  const colors = labels.map((_, i) => LANG_COLORS[i % LANG_COLORS.length]);

  if (langChart) langChart.destroy();
  langChart = new Chart(canvas, {
    type: 'doughnut',
    data: { labels, datasets: [{ data: values, backgroundColor: colors, borderWidth: 0, hoverOffset: 4 }] },
    options: {
      cutout: '68%',
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: ctx => ` ${ctx.label}: ${ctx.parsed.toFixed(1)}%` } },
      },
    },
  });

  if (legendEl) {
    legendEl.innerHTML = entries.map(([lang, pct], i) => `
      <div class="lang-legend-item">
        <div class="lang-legend-dot" style="background:${colors[i]}"></div>
        <span class="lang-legend-name">${lang}</span>
        <span class="lang-legend-pct">${pct.toFixed(1)}%</span>
      </div>`).join('');
  }
}

function renderHourlyChart(hourlyData) {
  const canvas = document.getElementById('hourly-chart');
  if (!canvas) return;

  const labels = Array.from({ length: 24 }, (_, i) =>
    i === 0 ? '12am' : i === 12 ? '12pm' : i < 12 ? `${i}am` : `${i - 12}pm`
  );
  const values = labels.map((_, i) => hourlyData[String(i)] || 0);
  const maxVal = Math.max(...values, 1);
  const bgColors = values.map(v => {
    const t = v / maxVal;
    return t > 0.8 ? 'rgba(88,166,255,0.9)' : t > 0.5 ? 'rgba(88,166,255,0.6)' : 'rgba(88,166,255,0.25)';
  });

  if (hourlyChart) hourlyChart.destroy();
  hourlyChart = new Chart(canvas, {
    type: 'bar',
    data: { labels, datasets: [{ data: values, backgroundColor: bgColors, borderRadius: 3, borderSkipped: false }] },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: {
        x: { ticks: { color: '#8b949e', font: { size: 9, family: 'JetBrains Mono' }, maxRotation: 0, autoSkip: true, maxTicksLimit: 12 }, grid: { color: '#21262d' } },
        y: { ticks: { color: '#8b949e', font: { size: 10 } }, grid: { color: '#21262d' }, beginAtZero: true },
      },
    },
  });
}

function renderWeeklyChart(weeklyData) {
  const canvas = document.getElementById('weekly-chart');
  if (!canvas) return;

  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  const values = days.map(d => weeklyData[d] || 0);
  const maxVal = Math.max(...values, 1);
  const bgColors = values.map(v => {
    const t = v / maxVal;
    return t > 0.8 ? 'rgba(57,211,83,0.9)' : t > 0.5 ? 'rgba(57,211,83,0.6)' : 'rgba(57,211,83,0.25)';
  });

  if (weeklyChart) weeklyChart.destroy();
  weeklyChart = new Chart(canvas, {
    type: 'bar',
    data: { labels: days, datasets: [{ data: values, backgroundColor: bgColors, borderRadius: 4, borderSkipped: false }] },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: {
        x: { ticks: { color: '#8b949e', font: { size: 11 } }, grid: { color: '#21262d' } },
        y: { ticks: { color: '#8b949e', font: { size: 10 } }, grid: { color: '#21262d' }, beginAtZero: true },
      },
    },
  });
}

function renderTopRepos(repos) {
  const tbody = document.getElementById('repos-tbody');
  if (!tbody || !repos.length) return;
  const maxCommits = repos[0]?.commits || 1;
  tbody.innerHTML = repos.map((r, i) => {
    const barWidth = Math.round((r.commits / maxCommits) * 120);
    return `<tr>
      <td class="table-rank">${i + 1}</td>
      <td class="table-repo-name">${escapeHtml(r.name)}</td>
      <td class="table-commits">${r.commits.toLocaleString()}</td>
      <td><div class="activity-bar-wrap"><div class="activity-bar" style="width:${barWidth}px"></div></div></td>
    </tr>`;
  }).join('');
}

async function triggerSync() {
  const btn = document.getElementById('sync-btn');
  const btnText = document.getElementById('sync-btn-text');
  if (btn) btn.disabled = true;
  if (btnText) btnText.textContent = '↻ Syncing…';
  try {
    await fetch('/api/sync', { method: 'POST' });
    document.getElementById('sync-banner')?.classList.remove('hidden');
    startPolling();
  } catch (err) {
    console.error('Sync trigger failed:', err);
    if (btn) btn.disabled = false;
    if (btnText) btnText.textContent = '↻ Refresh Data';
  }
}

function escapeHtml(str) {
  return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
