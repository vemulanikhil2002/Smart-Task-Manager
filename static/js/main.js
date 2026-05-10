
let allTasks = [];


function getCsrf() {
  return (document.cookie.split(';').find(c => c.trim().startsWith('csrftoken=')) || '').split('=')[1] || '';
}

function showToast(msg, duration = 3000) {
  const t = document.getElementById('toast');
  if (!t) return;
  t.textContent = msg;
  t.classList.remove('hidden');
  setTimeout(() => t.classList.add('hidden'), duration);
}


async function loadTasks() {
  try {
    const res  = await fetch('/api/tasks/');
    const data = await res.json();
    if (data.success) { allTasks = data.tasks; renderTasks(allTasks); }
  } catch (e) { console.error('Load tasks failed', e); }
}


function renderTasks(tasks) {
  const el = document.getElementById('taskList');
  if (!el) return;
  if (!tasks.length) {
    el.innerHTML = '<div class="empty-state">🎉 No tasks found. Add one above!</div>';
    return;
  }
  el.innerHTML = tasks.map(t => `
    <div class="task-item ${t.status === 'completed' ? 'completed-item' : ''}" id="task-${t.id}">
      <div class="task-content">
        <div class="task-title">${escapeHtml(t.title)}</div>
        ${t.description ? `<div class="task-desc">${escapeHtml(t.description)}</div>` : ''}
        <div class="task-meta">
          <span class="badge badge-${t.priority}">${priorityIcon(t.priority)} ${t.priority}</span>
          <span class="badge badge-${t.status}">${statusIcon(t.status)} ${t.status.replace('_', ' ')}</span>
          <span class="task-date">🕐 ${t.created_at}</span>
        </div>
      </div>
      <div class="task-actions">
        <button class="btn btn-secondary btn-sm" onclick="openEdit(${t.id})">✏️</button>
        <button class="btn btn-danger btn-sm"    onclick="deleteTask(${t.id})">🗑️</button>
      </div>
    </div>`).join('');
}

function filterTasks() {
  const status   = document.getElementById('filterStatus').value;
  const priority = document.getElementById('filterPriority').value;
  let f = allTasks;
  if (status   !== 'all') f = f.filter(t => t.status   === status);
  if (priority !== 'all') f = f.filter(t => t.priority === priority);
  renderTasks(f);
}


async function addTask() {
  const title       = document.getElementById('taskTitle').value.trim();
  const description = document.getElementById('taskDescription').value.trim();
  const priority    = document.getElementById('taskPriority').value;
  const status      = document.getElementById('taskStatus').value;

  if (!title) { showToast('⚠️ Title is required!'); return; }

  try {
    const res  = await fetch('/api/tasks/add/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrf() },
      body: JSON.stringify({ title, description, priority, status }),
    });
    const data = await res.json();
    if (data.success) {
      document.getElementById('taskTitle').value       = '';
      document.getElementById('taskDescription').value = '';
      showToast('✅ Task added!');
      loadTasks(); loadAnalytics();
    } else { showToast('❌ ' + data.error); }
  } catch (e) { showToast('❌ Failed to add task.'); }
}


async function deleteTask(id) {
  if (!confirm('Delete this task?')) return;
  try {
    const res  = await fetch(`/api/tasks/${id}/delete/`, {
      method: 'DELETE',
      headers: { 'X-CSRFToken': getCsrf() },
    });
    const data = await res.json();
    if (data.success) { showToast('🗑️ Task deleted.'); loadTasks(); loadAnalytics(); }
  } catch (e) { showToast('❌ Failed to delete task.'); }
}

// ── Edit modal ───────────────────────────────────────────────
function openEdit(id) {
  const task = allTasks.find(t => t.id === id);
  if (!task) return;
  document.getElementById('editTaskId').value      = task.id;
  document.getElementById('editTitle').value        = task.title;
  document.getElementById('editDescription').value  = task.description || '';
  document.getElementById('editPriority').value     = task.priority;
  document.getElementById('editStatus').value       = task.status;
  document.getElementById('editModal').classList.remove('hidden');
}

function closeModal() {
  document.getElementById('editModal').classList.add('hidden');
}

async function saveEdit() {
  const id          = document.getElementById('editTaskId').value;
  const title       = document.getElementById('editTitle').value.trim();
  const description = document.getElementById('editDescription').value.trim();
  const priority    = document.getElementById('editPriority').value;
  const status      = document.getElementById('editStatus').value;

  if (!title) { showToast('⚠️ Title is required!'); return; }

  try {
    const res  = await fetch(`/api/tasks/${id}/update/`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrf() },
      body: JSON.stringify({ title, description, priority, status }),
    });
    const data = await res.json();
    if (data.success) { closeModal(); showToast('✅ Task updated!'); loadTasks(); loadAnalytics(); }
    else { showToast('❌ ' + data.error); }
  } catch (e) { showToast('❌ Failed to update task.'); }
}

// Close modal on overlay click
document.addEventListener('DOMContentLoaded', () => {
  const overlay = document.getElementById('editModal');
  if (overlay) overlay.addEventListener('click', e => { if (e.target === overlay) closeModal(); });
});

// ── Analytics ────────────────────────────────────────────────
async function loadAnalytics() {
  try {
    const res  = await fetch('/api/analytics/');
    const data = await res.json();
    if (!data.success) return;

    document.getElementById('totalTasks').textContent      = data.total;
    document.getElementById('completedTasks').textContent  = data.completed;
    document.getElementById('pendingTasks').textContent    = data.pending;
    document.getElementById('inProgressTasks').textContent = data.in_progress;
    document.getElementById('completionPct').textContent   = data.completion_pct + '%';

    const total = data.total || 1;
    const pb    = document.getElementById('priorityBars');
    if (!pb) return;
    pb.innerHTML = ['high', 'medium', 'low'].map(p => {
      const count = data.priority_counts[p] || 0;
      const pct   = Math.round((count / total) * 100);
      return `<div class="priority-row">
        <span class="priority-label">${priorityIcon(p)} ${p}</span>
        <div class="priority-bar-bg"><div class="priority-bar-fill bar-${p}" style="width:${pct}%"></div></div>
        <span class="priority-count">${count}</span>
      </div>`;
    }).join('');
  } catch (e) { console.error('Analytics error', e); }
}

// ── Helpers ──────────────────────────────────────────────────
function priorityIcon(p) { return {high:'🔴',medium:'🟡',low:'🟢'}[p] || ''; }
function statusIcon(s)   { return {pending:'⏳',in_progress:'🔄',completed:'✅'}[s] || ''; }
function escapeHtml(str) {
  return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
