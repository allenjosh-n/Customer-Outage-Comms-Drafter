// ─── Auth helpers (shared pattern) ───────────────────────────────────────────
function getToken()    { return localStorage.getItem('oc_token') || ''; }
function getUsername() { return localStorage.getItem('oc_username') || ''; }
function getRole()     { return localStorage.getItem('oc_role') || 'viewer'; }
function getMyUserId() {
  try { return JSON.parse(atob(getToken().split('.')[1])).sub; } catch { return null; }
}
function authHeaders() {
  return { 'Content-Type': 'application/json', 'Authorization': `Bearer ${getToken()}` };
}
function logout() {
  ['oc_token','oc_username','oc_role'].forEach(k => localStorage.removeItem(k));
  window.location.href = '/auth/login-page';
}
function showToast(msg) {
  const t = document.getElementById('toast');
  if (!t) return;
  t.textContent = msg;
  t.classList.add('toast--visible');
  setTimeout(() => t.classList.remove('toast--visible'), 2200);
}
function escHtml(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

// ─── Init header ──────────────────────────────────────────────────────────────
function initHeader() {
  const token = getToken();
  if (!token) { window.location.href = '/auth/login-page'; return; }
  const avatar = document.getElementById('userAvatar');
  const name   = document.getElementById('userName');
  const u      = getUsername();
  if (avatar) avatar.textContent = u.charAt(0).toUpperCase();
  if (name)   name.textContent   = u;

  // Viewers can't access workspace
  if (getRole() === 'viewer') {
    window.location.href = '/';
  }
}

// ══════════════════════════════════════════════════════════════════════════════
// WORKSPACE LIST PAGE
// ══════════════════════════════════════════════════════════════════════════════

async function loadWorkspaces() {
  const grid = document.getElementById('wsList');
  if (!grid) return;
  try {
    const res  = await fetch('/workspace', { headers: authHeaders() });
    if (res.status === 401) { logout(); return; }
    const data = await res.json();
    renderWorkspaceList(data.workspaces || []);
  } catch (e) {
    if (grid) grid.innerHTML = `<p class="placeholder-text" style="grid-column:1/-1;padding:var(--space-8);text-align:center;color:var(--red)">Error loading workspaces</p>`;
  }
}

function renderWorkspaceList(workspaces) {
  const grid = document.getElementById('wsList');
  if (!grid) return;

  if (!workspaces.length) {
    grid.innerHTML = `
      <div class="ws-empty" style="grid-column:1/-1">
        <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="color:var(--text-muted)"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
        <p style="color:var(--text-muted);font-style:italic;margin-top:var(--space-3)">No incidents yet. Create the first one.</p>
      </div>`;
    return;
  }

  const sevColors = { Low: 'var(--green)', Medium: 'var(--amber)', High: 'var(--red)' };
  const sevDims   = { Low: 'var(--green-dim)', Medium: 'var(--amber-dim)', High: 'var(--red-dim)' };
  const sevBorder = { Low: 'rgba(34,197,94,0.25)', Medium: 'rgba(245,158,11,0.25)', High: 'rgba(239,68,68,0.25)' };

  grid.innerHTML = workspaces.map(ws => {
    const date = new Date(ws.created_at).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' });
    const sCol = sevColors[ws.severity] || 'var(--text-muted)';
    const sDim = sevDims[ws.severity]   || 'transparent';
    const sBdr = sevBorder[ws.severity] || 'transparent';
    const statusCls = ws.status === 'active' ? 'ws-status-badge--active' : 'ws-status-badge--closed';
    return `
      <div class="ws-card" onclick="window.location.href='/workspace-page/${ws.id}'">
        <div class="ws-card-header">
          <span class="card-badge" style="background:${sDim};border-color:${sBdr};color:${sCol}">${escHtml(ws.severity)}</span>
          <span class="ws-status-badge ${statusCls}">${ws.status === 'active' ? '● Active' : '○ Closed'}</span>
        </div>
        <h3 class="ws-card-title">${escHtml(ws.title)}</h3>
        <div class="ws-card-meta">
          <span>by ${escHtml(ws.created_by)}</span>
          <span>${ws.member_count} member${ws.member_count !== 1 ? 's' : ''}</span>
        </div>
        <div class="ws-card-date">${date}</div>
      </div>`;
  }).join('');
}

// ─── New workspace modal ──────────────────────────────────────────────────────
function openNewModal() {
  document.getElementById('modalOverlay').classList.add('active');
  document.getElementById('newWsModal').classList.add('active');
  document.getElementById('wsTitle').focus();
}
function closeNewModal() {
  document.getElementById('modalOverlay').classList.remove('active');
  document.getElementById('newWsModal').classList.remove('active');
  document.getElementById('modalError').style.display = 'none';
}

async function createWorkspace() {
  const title    = document.getElementById('wsTitle').value.trim();
  const severity = document.getElementById('wsSeverity').value;
  const errBox   = document.getElementById('modalError');
  const btn      = document.querySelector('#newWsModal .generate-btn');

  if (!title) { errBox.textContent = 'Title is required'; errBox.style.display = 'block'; return; }

  btn.disabled = true;
  btn.classList.add('btn--loading');
  errBox.style.display = 'none';

  try {
    const res  = await fetch('/workspace', {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify({ title, severity }),
    });
    const data = await res.json();
    if (!res.ok) { errBox.textContent = data.error || 'Failed'; errBox.style.display = 'block'; return; }
    closeNewModal();
    document.getElementById('wsTitle').value = '';
    window.location.href = `/workspace-page/${data.workspace.id}`;
  } catch (e) {
    errBox.textContent = 'Network error'; errBox.style.display = 'block';
  } finally {
    btn.disabled = false;
    btn.classList.remove('btn--loading');
  }
}


// ══════════════════════════════════════════════════════════════════════════════
// WORKSPACE DETAIL PAGE
// ══════════════════════════════════════════════════════════════════════════════

let _wsData = null;

async function loadWorkspaceDetail() {
  if (typeof WORKSPACE_ID === 'undefined') return;
  try {
    const res  = await fetch(`/workspace/${WORKSPACE_ID}`, { headers: authHeaders() });
    if (res.status === 401) { logout(); return; }
    const data = await res.json();
    _wsData = data.workspace;
    renderDetail(_wsData);
  } catch (e) {
    showToast('Error loading workspace');
  }
}

function renderDetail(ws) {
  if (!ws) return;
  const myId   = getMyUserId();
  const myRole = getRole();
  const isMem  = ws.members.some(m => m.user_id === myId);
  const canAct = myRole === 'owner' || isMem;

  // Title bar
  const sevColors = { Low: 'var(--green)', Medium: 'var(--amber)', High: 'var(--red)' };
  const sevDims   = { Low: 'var(--green-dim)', Medium: 'var(--amber-dim)', High: 'var(--red-dim)' };
  const sevBorder = { Low: 'rgba(34,197,94,0.25)', Medium: 'rgba(245,158,11,0.25)', High: 'rgba(239,68,68,0.25)' };
  const sCol = sevColors[ws.severity] || 'var(--text-muted)';
  const sDim = sevDims[ws.severity]   || 'transparent';
  const sBdr = sevBorder[ws.severity] || 'transparent';

  const titleRow = document.getElementById('wsTitleRow');
  if (titleRow) titleRow.innerHTML = `
    <h1 class="ws-detail-title">${escHtml(ws.title)}</h1>
    <span class="card-badge" style="background:${sDim};border-color:${sBdr};color:${sCol}">${escHtml(ws.severity)}</span>
  `;

  // Severity pulse
  const pulse = document.getElementById('wsSeverityPulse');
  if (pulse) {
    pulse.className = 'brand-pulse ' + (ws.severity === 'High' ? 'pulse--high' : ws.severity === 'Medium' ? 'pulse--medium' : 'pulse--low');
  }

  // Status badge
  const statusBadge = document.getElementById('wsStatusBadge');
  if (statusBadge) {
    statusBadge.className = `ws-status-badge ${ws.status === 'active' ? 'ws-status-badge--active' : 'ws-status-badge--closed'}`;
    statusBadge.textContent = ws.status === 'active' ? '● Active' : '○ Closed';
  }

  // Close button
  const closeBtn = document.getElementById('wsCloseBtn');
  if (closeBtn && ws.status === 'active' && canAct) closeBtn.style.display = 'inline-flex';

  // Members
  renderMembers(ws.members, ws, myId, myRole);

  // Add member button
  const addBtn = document.getElementById('addMemberBtn');
  if (addBtn && canAct && ws.status === 'active') addBtn.style.display = 'inline-flex';

  // Populate add member select
  const sel = document.getElementById('addMemberSelect');
  if (sel && ws.addable_users) {
    sel.innerHTML = '<option value="">Select a team member…</option>' +
      ws.addable_users.map(u => `<option value="${u.id}" data-username="${escHtml(u.username)}">${escHtml(u.username)} (${escHtml(u.role)})</option>`).join('');
  }

  // Update form — hide if not member, not owner, or workspace closed
  const formCard = document.getElementById('updateFormCard');
  if (formCard && (!canAct || ws.status === 'closed')) formCard.style.display = 'none';

  // Render updates
  renderUpdates(ws.updates || []);
}

function renderMembers(members, ws, myId, myRole) {
  const list = document.getElementById('membersList');
  if (!list) return;
  if (!members.length) {
    list.innerHTML = '<p class="placeholder-text" style="font-size:var(--text-xs)">No members yet.</p>';
    return;
  }
  list.innerHTML = members.map(m => {
    const removeBtn = myRole === 'owner' && m.user_id !== myId
      ? `<button class="ws-remove-member-btn" onclick="removeMember(${m.user_id})" title="Remove">✕</button>`
      : '';
    const isMe = m.user_id === myId ? ' <span style="color:var(--text-muted);font-size:var(--text-2xs)">(you)</span>' : '';
    return `
      <div class="ws-member-row">
        <div class="user-avatar" style="flex-shrink:0;width:26px;height:26px;font-size:var(--text-xs)">${m.username.charAt(0).toUpperCase()}</div>
        <span class="ws-member-name">${escHtml(m.username)}${isMe}</span>
        ${removeBtn}
      </div>`;
  }).join('');
}

function renderUpdates(updates) {
  const list = document.getElementById('updatesList');
  if (!list) return;
  if (!updates.length) {
    list.innerHTML = '<p class="placeholder-text" style="padding:var(--space-6);text-align:center">No updates yet. Add the first timeline entry.</p>';
    return;
  }
  const phaseColors = { initial: 'var(--red)', progress: 'var(--amber)', resolved: 'var(--green)' };
  const phaseLabels = { initial: 'Initial Alert', progress: 'In Progress', resolved: 'Resolved' };

  list.innerHTML = updates.map(u => {
    const date  = new Date(u.created_at).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' });
    const pCol  = phaseColors[u.phase] || 'var(--teal)';
    const pLbl  = phaseLabels[u.phase] || u.phase;
    const hasMsg = u.customer_message && u.customer_message.trim();
    const hasSumm = u.summary_entry && u.summary_entry.trim();
    const uid   = `upd-${u.id}`;
    return `
      <div class="ws-update-block ws-update--${u.phase}">
        <div class="ws-update-meta">
          <span class="log-phase-badge log-badge--${u.phase}" style="color:${pCol}">${pLbl}</span>
          <span class="ws-update-author">by ${escHtml(u.created_by)}</span>
          <span class="log-timestamp">${date}</span>
        </div>
        <div class="log-timeline-ref" style="margin:var(--space-2) 0">${escHtml(u.timeline)}</div>
        ${hasMsg ? `
        <div class="ws-collapsible">
          <button class="ws-collapse-btn" onclick="toggleCollapse('msg-${uid}')">
            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="6 9 12 15 18 9"/></svg>
            Customer Message
          </button>
          <div id="msg-${uid}" class="ws-collapse-content">
            <p class="ws-customer-msg">${escHtml(u.customer_message)}</p>
            <button class="copy-btn" style="margin-top:var(--space-2)" data-copy="${escHtml(u.customer_message).replace(/"/g,'&quot;')}" onclick="copyUpdateMsg(this)">Copy</button>
          </div>
        </div>` : ''}
        ${hasSumm ? `
        <div class="ws-collapsible">
          <button class="ws-collapse-btn" onclick="toggleCollapse('summ-${uid}')">
            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="6 9 12 15 18 9"/></svg>
            Internal Summary
          </button>
          <div id="summ-${uid}" class="ws-collapse-content">
            <div class="log-entry-text">${escHtml(u.summary_entry).replace(/•/g,'<span class="log-bullet">•</span>').replace(/\n/g,'<br>')}</div>
          </div>
        </div>` : ''}
      </div>`;
  }).join('');
}

function toggleCollapse(id) {
  const el = document.getElementById(id);
  if (!el) return;
  el.classList.toggle('open');
}

function copyUpdateMsg(btn) {
  const text = btn.getAttribute('data-copy') || '';
  navigator.clipboard.writeText(text).then(() => showToast('Copied'));
}

// ─── Add member ───────────────────────────────────────────────────────────────
function openAddMember()  { document.getElementById('addMemberPanel').style.display = 'block'; }
function closeAddMember() { document.getElementById('addMemberPanel').style.display = 'none'; }

async function addMember() {
  const sel = document.getElementById('addMemberSelect');
  const userId   = sel.value;
  const username = sel.selectedOptions[0]?.dataset.username || '';
  if (!userId) { showToast('Select a team member first'); return; }

  try {
    const res = await fetch(`/workspace/${WORKSPACE_ID}/members`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify({ user_id: parseInt(userId), username }),
    });
    const data = await res.json();
    if (!res.ok) { showToast(data.error || 'Failed'); return; }
    showToast(`${username} added`);
    closeAddMember();
    loadWorkspaceDetail();
  } catch { showToast('Error adding member'); }
}

async function removeMember(userId) {
  if (!confirm('Remove this member from the workspace?')) return;
  try {
    const res = await fetch(`/workspace/${WORKSPACE_ID}/members/${userId}`, {
      method: 'DELETE', headers: authHeaders(),
    });
    if (!res.ok) { showToast('Failed to remove member'); return; }
    showToast('Member removed');
    loadWorkspaceDetail();
  } catch { showToast('Error removing member'); }
}

// ─── Generate update ──────────────────────────────────────────────────────────
async function generateUpdate() {
  const timeline = document.getElementById('updateTimeline').value.trim();
  const severity = document.getElementById('updateSeverity').value;
  const tone     = document.getElementById('updateTone').value;
  const btn      = document.getElementById('generateUpdateBtn');

  if (!timeline) { showToast('Enter a timeline update first'); return; }

  btn.disabled = true;
  btn.classList.add('btn--loading');

  try {
    const res  = await fetch(`/workspace/${WORKSPACE_ID}/updates`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify({ timeline, severity, tone }),
    });
    if (res.status === 401) { logout(); return; }
    const data = await res.json();
    if (!res.ok) { showToast(data.error || 'Failed to generate'); return; }

    document.getElementById('updateTimeline').value = '';
    showToast('Update generated');
    // Append new update to the list without full reload
    if (_wsData) {
      _wsData.updates = [...(_wsData.updates || []), data.update];
      renderUpdates(_wsData.updates);
    } else {
      loadWorkspaceDetail();
    }
  } catch (e) {
    showToast('Error generating update');
  } finally {
    btn.disabled = false;
    btn.classList.remove('btn--loading');
  }
}

// ─── Close workspace ──────────────────────────────────────────────────────────
async function closeWorkspace() {
  if (!confirm('Close this incident workspace? It will become read-only.')) return;
  try {
    const res = await fetch(`/workspace/${WORKSPACE_ID}/status`, {
      method: 'PATCH',
      headers: authHeaders(),
      body: JSON.stringify({ status: 'closed' }),
    });
    if (!res.ok) { showToast('Failed to close workspace'); return; }
    showToast('Incident closed');
    loadWorkspaceDetail();
  } catch { showToast('Error closing workspace'); }
}

// ─── Init ─────────────────────────────────────────────────────────────────────
initHeader();

if (typeof WORKSPACE_ID !== 'undefined') {
  loadWorkspaceDetail();
} else {
  loadWorkspaces();
}
