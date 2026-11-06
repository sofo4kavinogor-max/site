function getCookie(name) {
    const v = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return v ? v.pop() : '';
}

function toggleTheme() {
    const current = document.documentElement.getAttribute('data-bs-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-bs-theme', next);
    localStorage.setItem('theme', next);
}

function saveFilters() {
    const status = document.getElementById('filterStatus')?.value || '';
    const project = document.getElementById('filterProject')?.value || '';
    sessionStorage.setItem('filterStatus', status);
    sessionStorage.setItem('filterProject', project);
}

function restoreFilters() {
    const status = sessionStorage.getItem('filterStatus') || '';
    const project = sessionStorage.getItem('filterProject') || '';
    const sEl = document.getElementById('filterStatus');
    const pEl = document.getElementById('filterProject');
    if (sEl) sEl.value = status;
    if (pEl) pEl.value = project;
    applyFilters();
}

function applyFilters() {
    const status = document.getElementById('filterStatus')?.value || '';
    const project = document.getElementById('filterProject')?.value || '';
    document.querySelectorAll('#taskTable tr[data-status]').forEach(row => {
        const ok1 = !status || row.dataset.status === status;
        const ok2 = !project || row.dataset.project === project;
        row.style.display = (ok1 && ok2) ? '' : 'none';
    });
}

async function updateStatus(taskId, status) {
    await fetch(`/api/task/${taskId}/status/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({ status }),
    });
    const row = document.querySelector(`#task-${taskId}`);
    if (row) row.dataset.status = status;
}

async function deleteTask(taskId) {
    if (!confirm('Удалить задачу?')) return;
    await fetch(`/api/task/${taskId}/delete/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': getCookie('csrftoken') },
    });
    document.getElementById(`task-${taskId}`)?.remove();
}

async function createTask(title, projectId) {
    const resp = await fetch('/api/task/create/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({ title, project: projectId }),
    });
    return resp.json();
}

document.addEventListener('DOMContentLoaded', () => {
    const theme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-bs-theme', theme);

    restoreFilters();

    document.getElementById('filterStatus')?.addEventListener('change', () => {
        saveFilters(); applyFilters();
    });
    document.getElementById('filterProject')?.addEventListener('change', () => {
        saveFilters(); applyFilters();
    });
    document.getElementById('searchInput')?.addEventListener('input', (e) => {
        const q = e.target.value.toLowerCase();
        document.querySelectorAll('#taskTable tr[data-status]').forEach(row => {
            row.style.display = row.textContent.toLowerCase().includes(q) ? '' : 'none';
        });
    });
});

async function submitCreateTask() {
    const title = document.getElementById('newTaskTitle').value;
    const projectId = document.getElementById('newTaskProject').value;
    if (!title) return;

    const data = await createTask(title, projectId);

    const modalEl = document.getElementById('createTaskModal');
    modalEl.classList.remove('show'); // убираем класс
    modalEl.style.display = 'none';   // скрываем
    modalEl.setAttribute('aria-hidden', 'true');
    
    const backdrop = document.querySelector('.modal-backdrop');
    if (backdrop) backdrop.remove();

    document.getElementById('newTaskTitle').value = '';

    const tbody = document.getElementById('taskTable');
    const tr = document.createElement('tr');
    tr.id = `task-${data.id}`;
    tr.dataset.status = 'todo';
    tr.dataset.project = projectId;
    tr.innerHTML = `
        <td>${data.title}</td>
        <td>${data.project}</td>
        <td>
            <select class="form-select form-select-sm" onchange="updateStatus(${data.id}, this.value)">
                <option value="todo" selected>К выполнению</option>
                <option value="in_progress">В работе</option>
                <option value="done">Выполнено</option>
            </select>
        </td>
        <td>Средний</td>
        <td><button class="btn btn-sm btn-danger" onclick="deleteTask(${data.id})">Удалить</button></td>
    `;
    tbody.prepend(tr);
}