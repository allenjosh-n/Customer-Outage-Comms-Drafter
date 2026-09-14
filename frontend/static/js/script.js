// ─── History drawer ───────────────────────────────────────────────────────────
function openHistoryPanel() {
  document.getElementById('historyOverlay').classList.add('active');
  document.getElementById('historyDrawer').classList.add('active');
  loadHistory();
}

function closeHistoryPanel() {
  document.getElementById('historyOverlay').classList.remove('active');
  document.getElementById('historyDrawer').classList.remove('active');
}

// ─── Load history ─────────────────────────────────────────────────────────────
async function loadHistory() {
  const list = document.getElementById('historyList');
  list.innerHTML = '<p class="placeholder-text" style="padding:var(--space-4)">Loading…</p>';

  try {
    const res  = await fetch('/incidents', { headers: authHeaders() });
    if (res.status === 401) { logout(); return; }
    const data = await res.json();
    if (data.error) {
      list.innerHTML = `<p class="placeholder-text" style="padding:var(--space-4);color:var(--red)">${data.error}</p>`;
      return;
    }
    renderHistory(data.incidents || []);
  } catch (e) {
    list.innerHTML = `<p class="placeholder-text" style="padding:var(--space-4);color:var(--red)">Error: ${e.message}</p>`;
  }
}

function renderHistory(incidents) {
  const list = document.getElementById('historyList');

  if (!incidents.length) {
    list.innerHTML = '<div class="history-empty">No past incidents yet.<br>Complete an incident and start a new one to save it here.</div>';
    return;
  }

  const phaseColors = { initial: 'var(--red)', progress: 'var(--amber)', resolved: 'var(--green)' };
  const phaseLabels = { initial: 'Initial Alert', progress: 'In Progress', resolved: 'Resolved' };

  list.innerHTML = incidents.map((inc, idx) => {
    const date = new Date(inc.created).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' });

    const entriesHtml = (inc.entries || []).map(e => `
      <div class="history-entry history-entry--${e.phase}">
        <div class="history-entry-phase" style="color:${phaseColors[e.phase] || 'var(--teal)'}">
          ${phaseLabels[e.phase] || e.phase}
        </div>
        <div class="history-entry-timeline">${escapeHtml(e.timeline || '')}</div>
        <div class="history-entry-text">${escapeHtml(e.entry || '').replace(/•/g, '<span class="log-bullet">•</span>')}</div>
      </div>
    `).join('');

    return `
      <div class="history-card">
        <div class="history-card-header">
          <span class="card-badge" style="background:rgba(0,201,167,0.1);border-color:rgba(0,201,167,0.25);color:var(--teal)">
            Incident #${incidents.length - idx}
          </span>
          <span class="history-date">${date}</span>
        </div>
        <div class="history-entries">${entriesHtml}</div>
      </div>
    `;
  }).join('');
}

// ─── Save incident to history ─────────────────────────────────────────────────
async function saveCurrentIncident() {
  if (!summaryEntries.length) return;
  const severity = document.getElementById('severity').value;
  try {
    await fetch('/incidents/save', {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify({ severity, entries: summaryEntries }),
    });
  } catch (e) {
    console.warn('Could not save incident to history:', e);
  }
}

// ─── Auth helpers ─────────────────────────────────────────────────────────────
function getToken() {
  return localStorage.getItem('oc_token') || '';
}

function authHeaders() {
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${getToken()}`,
  };
}

function logout() {
  localStorage.removeItem('oc_token');
  localStorage.removeItem('oc_username');
  window.location.href = '/auth/login-page';
}

function initUserInfo() {
  const token    = getToken();
  const username = localStorage.getItem('oc_username') || '';

  if (!token) {
    window.location.href = '/auth/login-page';
    return;
  }

  // Show username and avatar initial in header
  const avatar = document.getElementById('userAvatar');
  const name   = document.getElementById('userName');
  if (avatar) avatar.textContent = username.charAt(0).toUpperCase();
  if (name)   name.textContent   = username;
}

// ─── State ────────────────────────────────────────────────────────────────────
const filledPhases   = new Set();  // tracks which cards have been drafted
const summaryEntries = [];         // { phase, timeline, entry }

// ─── Severity UI ──────────────────────────────────────────────────────────────
function updateSeverity(value) {
  const pulse = document.getElementById('severityPulse');
  const badge = document.getElementById('severityBadge');
  const text  = badge.querySelector('.severity-text');
  pulse.className = 'brand-pulse';
  badge.className = 'severity-badge';
  if (value === 'High') {
    pulse.classList.add('pulse--high');
    badge.classList.add('badge-sev--high');
    text.textContent = 'High Severity';
  } else if (value === 'Medium') {
    pulse.classList.add('pulse--medium');
    badge.classList.add('badge-sev--medium');
    text.textContent = 'Medium Severity';
  } else {
    pulse.classList.add('pulse--low');
    badge.classList.add('badge-sev--low');
    text.textContent = 'Low Severity';
  }
}

// ─── Toast ────────────────────────────────────────────────────────────────────
function showToast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg || 'Done';
  t.classList.add('toast--visible');
  setTimeout(() => t.classList.remove('toast--visible'), 2200);
}

// ─── Header status label ──────────────────────────────────────────────────────
function setStatus(msg, color) {
  const lbl = document.getElementById('statusLabel');
  lbl.textContent = msg;
  lbl.style.color = color || 'var(--teal)';
}

// ─── Copy helpers ─────────────────────────────────────────────────────────────
function copyCard(id) {
  const el = document.getElementById(id);
  if (!el || el.classList.contains('placeholder-text')) return;
  navigator.clipboard.writeText(el.innerText).then(() => showToast('Copied'));
}

function copySummary() {
  const text = buildSummaryText();
  if (!text) return;
  navigator.clipboard.writeText(text).then(() => showToast('Log copied'));
}

// ─── Plain-text report builder ────────────────────────────────────────────────
function buildSummaryText() {
  if (!summaryEntries.length) return '';
  const severity = document.getElementById('severity').value;
  const lines = [
    '==================================',
    '  INCIDENT SUMMARY REPORT',
    '  OutageComms — Auto-generated',
    `  Severity: ${severity}`,
    `  Generated: ${new Date().toLocaleString()}`,
    '==================================',
    '',
  ];
  summaryEntries.forEach(({ phase, timeline, entry }) => {
    lines.push(`── ${phase.toUpperCase()} ──`);
    lines.push(`Timeline: ${timeline}`);
    lines.push(entry);
    lines.push('');
  });
  return lines.join('\n');
}

// ─── Download report ──────────────────────────────────────────────────────────
function downloadSummary() {
  const text = buildSummaryText();
  if (!text) return;
  const blob = new Blob([text], { type: 'text/plain' });
  const url  = URL.createObjectURL(blob);
  const a    = document.createElement('a');
  a.href     = url;
  a.download = `incident-report-${Date.now()}.txt`;
  a.click();
  URL.revokeObjectURL(url);
  showToast('Report downloaded');
}

// ─── Append entry to summary log ──────────────────────────────────────────────
function appendSummaryEntry(phase, timeline, entryText) {
  summaryEntries.push({ phase, timeline, entry: entryText });

  const placeholder = document.getElementById('summaryPlaceholder');
  if (placeholder) placeholder.remove();

  const log   = document.getElementById('summaryLog');
  const block = document.createElement('div');
  block.className = `log-block log-block--${phase}`;

  const labels = { initial: 'Initial Alert', progress: 'In Progress', resolved: 'Resolved' };

  block.innerHTML = `
    <div class="log-phase-header">
      <span class="log-phase-badge log-badge--${phase}">${labels[phase] || phase}</span>
      <span class="log-timestamp">${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
    </div>
    <div class="log-timeline-ref">${escapeHtml(timeline)}</div>
    <div class="log-entry-text">${escapeHtml(entryText).replace(/•/g, '<span class="log-bullet">•</span>')}</div>
  `;
  log.appendChild(block);
  document.getElementById('downloadBtn').disabled = false;
}

function escapeHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\n/g, '<br>');
}

// ─── Phase chip ───────────────────────────────────────────────────────────────
const phaseChipConfig = {
  initial:  { label: 'Initial Alert', cls: 'chip--initial'  },
  progress: { label: 'In Progress',   cls: 'chip--progress' },
  resolved: { label: 'Resolved',      cls: 'chip--resolved' },
};

function showPhaseChip(phase) {
  const row  = document.getElementById('phaseHintRow');
  const chip = document.getElementById('phaseChip');
  const cfg  = phaseChipConfig[phase] || { label: phase, cls: '' };
  chip.textContent = cfg.label;
  chip.className   = `phase-chip ${cfg.cls}`;
  row.style.display = 'flex';
}

// ─── Main generate flow ───────────────────────────────────────────────────────
async function generateDraft() {
  const timeline = document.getElementById('timeline').value.trim();
  if (!timeline) { showToast('Please enter a timeline update'); return; }

  const btn = document.getElementById('generateBtn');
  btn.classList.add('btn--loading');
  btn.disabled = true;
  setStatus('Detecting phase…', 'var(--amber)');

  const severity = document.getElementById('severity').value;
  const tone     = document.getElementById('tone').value;

  try {
    // Step 1 — detect phase
    const detectRes = await fetch('/detect-phase', {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify({ timeline }),
    });

    if (detectRes.status === 401) { logout(); return; }
    const { phase } = await detectRes.json();

    showPhaseChip(phase);
    setStatus('Generating draft…', 'var(--amber)');

    const cardEl = document.getElementById(phase);
    if (cardEl) {
      cardEl.className  = 'card-text card-text--loading';
      cardEl.textContent = '';
    }

    // Step 2 — generate communication
    const genRes = await fetch('/generate', {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify({ timeline, severity, tone, phase }),
    });
    if (genRes.status === 401) { logout(); return; }
    const data = await genRes.json();

    if (cardEl) {
      cardEl.className  = 'card-text card-text--populated';
      cardEl.textContent = data.text || 'No content generated.';

      filledPhases.add(phase);
      const lockEl = document.getElementById(`lock-${phase}`);
      if (lockEl) lockEl.style.display = 'inline-flex';
      document.getElementById(`card-${phase}`).classList.add('card--locked');
    }

    if (data.summary_entry) appendSummaryEntry(phase, timeline, data.summary_entry);

    setStatus('AI Ready', 'var(--teal)');
    document.getElementById('timeline').value = '';
    document.getElementById('timeline').focus();
    showToast(`${phase.charAt(0).toUpperCase() + phase.slice(1)} draft ready`);

  } catch (e) {
    console.error(e);
    setStatus('Error — try again', 'var(--red)');
    showToast('Error generating draft');
  }

  btn.classList.remove('btn--loading');
  btn.disabled = false;
}

// ─── Reset ────────────────────────────────────────────────────────────────────
async function resetAll() {
  // Save current incident to history before clearing
  await saveCurrentIncident();

  const placeholders = {
    initial:  'Waiting for initial alert entry…',
    progress: 'Waiting for in-progress entry…',
    resolved: 'Waiting for resolution entry…',
  };

  Object.keys(placeholders).forEach(phase => {
    const el = document.getElementById(phase);
    el.className   = 'card-text placeholder-text';
    el.textContent = placeholders[phase];
    const lock = document.getElementById(`lock-${phase}`);
    if (lock) lock.style.display = 'none';
    document.getElementById(`card-${phase}`).classList.remove('card--locked');
  });

  filledPhases.clear();
  summaryEntries.length = 0;

  document.getElementById('summaryLog').innerHTML =
    '<p class="placeholder-text" id="summaryPlaceholder">The incident log builds here as you submit each phase update.</p>';

  document.getElementById('downloadBtn').disabled = true;
  document.getElementById('phaseHintRow').style.display = 'none';
  document.getElementById('timeline').value = '';
  setStatus('AI Ready', 'var(--teal)');
  showToast('Incident reset');
}

// ─── Init ─────────────────────────────────────────────────────────────────────
initUserInfo();
updateSeverity('Low');
