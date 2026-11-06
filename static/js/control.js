const API = '/api';

function getCookie(name) {
    const v = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return v ? v.pop() : '';
}

function showAlert(type, message) {
    const box = document.getElementById('ctrlAlert');
    box.innerHTML = `<div class="alert alert-${type} alert-dismissible" role="alert">
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    </div>`;
    setTimeout(() => box.innerHTML = '', 5000);
}

function showModal(id = 'ctrlModal') {
    const modalEl = document.getElementById(id);
    modalEl.classList.add('show');
    modalEl.style.display = 'block';
    modalEl.removeAttribute('aria-hidden');
    document.body.classList.add('modal-open');
    if (!document.querySelector('.modal-backdrop')) {
        const backdrop = document.createElement('div');
        backdrop.className = 'modal-backdrop fade show';
        document.body.appendChild(backdrop);
    }
}

function hideModal(id = 'ctrlModal') {
    const modalEl = document.getElementById(id);
    modalEl.classList.remove('show');
    modalEl.style.display = 'none';
    modalEl.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('modal-open');
    const backdrop = document.querySelector('.modal-backdrop');
    if (backdrop) backdrop.remove();
}

function hideHistoryModal() {
    hideModal('historyModal');
}

async function loadProjects() {
    try {
        const resp = await fetch(`${API}/projects/`);
        if (resp.status === 403) {
            showAlert('warning', 'Вы не авторизованы. Войдите в админку: /admin/');
            return;
        }
        if (!resp.ok) throw new Error('Не удалось загрузить проекты');
        const data = await resp.json();
        
        const filterSel = document.getElementById('ctrlProject');
        const modalSel = document.getElementById('ctrlProjectSelect');
        
        filterSel.innerHTML = '<option value="">Все проекты</option>';
        modalSel.innerHTML = '';
        
        data.forEach(p => {
            filterSel.innerHTML += `<option value="${p.id}">${p.name}</option>`;
            modalSel.innerHTML += `<option value="${p.id}">${p.name}</option>`;
        });
    } catch (e) {
        showAlert('danger', 'Ошибка загрузки проектов: ' + e.message);
    }
}

async function loadTasks() {
    const search = document.getElementById('ctrlSearch').value;
    const status = document.getElementById('ctrlStatus').value;
    const project = document.getElementById('ctrlProject').value;

    const params = new URLSearchParams();
    if (search) params.append('search', search);
    if (status) params.append('status', status);
    if (project) params.append('project', project);
    params.append('ordering', '-created_at');

    try {
        const resp = await fetch(`${API}/tasks/?${params}`);
        if (resp.status === 403) {
            showAlert('warning', 'Вы не авторизованы. Войдите в админку: /admin/');
            document.getElementById('ctrlTable').innerHTML = 
                '<tr><td colspan="7" class="text-secondary">Требуется авторизация</td></tr>';
            return;
        }
        if (!resp.ok) throw new Error('Ошибка загрузки задач');
        const data = await resp.json();
        renderTable(data);
    } catch (e) {
        showAlert('danger', 'Не удалось загрузить задачи: ' + e.message);
    }
}

function renderTable(tasks) {
    const tbody = document.getElementById('ctrlTable');
    tbody.innerHTML = '';
    
    if (tasks.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-secondary">Задач не найдено</td></tr>';
        return;
    }
    
    const statusMap = {
        'todo': 'К выполнению',
        'in_progress': 'В работе',
        'done': 'Выполнено',
    };
    
    tasks.forEach(t => {
        let actionButtons = '';
        if (t.status === 'todo') {
            actionButtons += `<button class="btn btn-sm btn-info" onclick="changeStatus(${t.id}, 'in_progress')">В работу</button> `;
        } else if (t.status === 'in_progress') {
            actionButtons += `<button class="btn btn-sm btn-success" onclick="changeStatus(${t.id}, 'done')">Завершить</button> `;
        } else if (t.status === 'done') {
            actionButtons += `<button class="btn btn-sm btn-secondary" onclick="changeStatus(${t.id}, 'todo')">Переоткрыть</button> `;
        }
        actionButtons += `<button class="btn btn-sm btn-warning" onclick="editTask(${t.id})">Ред.</button> `;
        actionButtons += `<button class="btn btn-sm btn-secondary" onclick="showHistory(${t.id})">История</button> `;
        actionButtons += `<button class="btn btn-sm btn-danger" onclick="deleteTask(${t.id}, '${t.title.replace(/'/g, "\\'")}')">Удал.</button>`;

        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${t.id}</td>
            <td>${t.title}</td>
            <td>${t.project_name}</td>
            <td>${statusMap[t.status] || t.status}</td>
            <td>${t.priority_display}</td>
            <td>${t.due_date || '—'}</td>
            <td>${actionButtons}</td>
        `;
        tbody.appendChild(tr);
    });
}

function openCreateModal() {
    document.getElementById('ctrlId').value = '';
    document.getElementById('ctrlTitle').value = '';
    document.getElementById('ctrlPrioritySelect').value = 'medium';
    document.getElementById('ctrlDueDate').value = '';
    document.getElementById('ctrlModalTitle').textContent = 'Новая задача';
    document.getElementById('ctrlTitleError').textContent = '';
    document.getElementById('ctrlTitle').classList.remove('is-invalid');
    showModal();
}

async function editTask(id) {
    try {
        const resp = await fetch(`${API}/tasks/${id}/`);
        if (!resp.ok) throw new Error('Задача не найдена');
        const t = await resp.json();
        
        document.getElementById('ctrlId').value = t.id;
        document.getElementById('ctrlTitle').value = t.title;
        document.getElementById('ctrlPrioritySelect').value = t.priority || 'medium';
        document.getElementById('ctrlDueDate').value = t.due_date || '';
        document.getElementById('ctrlProjectSelect').value = t.project;
        document.getElementById('ctrlStatusSelect').value = t.status;
        document.getElementById('ctrlModalTitle').textContent = 'Редактирование задачи';
        document.getElementById('ctrlTitleError').textContent = '';
        document.getElementById('ctrlTitle').classList.remove('is-invalid');
        
        showModal();
    } catch (e) {
        showAlert('danger', 'Ошибка: ' + e.message);
    }
}

async function saveTask() {
    const id = document.getElementById('ctrlId').value;
    const title = document.getElementById('ctrlTitle').value;
    const project = document.getElementById('ctrlProjectSelect').value;
    const status = document.getElementById('ctrlStatusSelect').value;
    const priority = document.getElementById('ctrlPrioritySelect').value;
    const due_date = document.getElementById('ctrlDueDate').value || null;

    if (!title || title.trim().length < 3) {
        document.getElementById('ctrlTitleError').textContent = 'Название должно быть не короче 3 символов';
        document.getElementById('ctrlTitle').classList.add('is-invalid');
        return;
    }

    const payload = { title, project, status, priority, due_date };
    const url = id ? `${API}/tasks/${id}/` : `${API}/tasks/`;
    const method = id ? 'PATCH' : 'POST';

    try {
        const resp = await fetch(url, {
            method,
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify(payload),
        });

        if (resp.status === 403) {
            showAlert('warning', 'Вы не авторизованы. Войдите в админку: /admin/');
            return;
        }

        if (!resp.ok) {
            const err = await resp.json();
            if (err.title) {
                document.getElementById('ctrlTitleError').textContent = err.title.join(' ');
                document.getElementById('ctrlTitle').classList.add('is-invalid');
            } else {
                showAlert('danger', 'Ошибка сервера: ' + JSON.stringify(err));
            }
            return;
        }

        hideModal();
        showAlert('success', id ? 'Задача обновлена' : 'Задача создана');
        loadTasks();
    } catch (e) {
        showAlert('danger', 'Ошибка сети: ' + e.message);
    }
}

async function changeStatus(id, newStatus) {
    try {
        const resp = await fetch(`${API}/tasks/${id}/change_status/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({ new_status: newStatus }),
        });
        const data = await resp.json();
        if (!resp.ok) {
            showAlert('danger', (data.error && data.error[0]) || data.error || 'Ошибка смены статуса');
            return;
        }
        showAlert('success', 'Статус изменён');
        loadTasks();
    } catch (e) {
        showAlert('danger', 'Ошибка сети: ' + e.message);
    }
}

async function showHistory(id) {
    try {
        const resp = await fetch(`${API}/tasks/${id}/history/`);
        if (!resp.ok) throw new Error('Не удалось загрузить историю');
        const events = await resp.json();
        const body = document.getElementById('historyBody');
        if (events.length === 0) {
            body.innerHTML = '<p class="text-secondary">Событий пока нет</p>';
        } else {
            body.innerHTML = events.map(e => `
                <div class="mb-2 p-2 border-bottom">
                    <strong>${e.event_type}</strong>:
                    ${e.old_status ? `${e.old_status} → ` : ''}${e.new_status || ''}
                    <br>
                    <span class="text-secondary small">${e.user_name || '—'} • ${new Date(e.created_at).toLocaleString()}</span>
                </div>
            `).join('');
        }
        showModal('historyModal');
    } catch (e) {
        showAlert('danger', 'Ошибка истории: ' + e.message);
    }
}

async function deleteTask(id, title) {
    if (!confirm(`Удалить задачу «${title}»?`)) return;
    try {
        const resp = await fetch(`${API}/tasks/${id}/`, {
            method: 'DELETE',
            headers: { 'X-CSRFToken': getCookie('csrftoken') },
        });
        if (resp.status === 403) {
            showAlert('danger', 'Нельзя удалить чужую задачу');
            return;
        }
        if (!resp.ok) throw new Error('Ошибка удаления');
        showAlert('success', `Задача «${title}» удалена`);
        loadTasks();
    } catch (e) {
        showAlert('danger', 'Не удалось удалить: ' + e.message);
    }
}

document.addEventListener('DOMContentLoaded', async () => {
    await loadProjects();
    await loadTasks();

    document.getElementById('ctrlSearch').addEventListener('input', debounce(loadTasks, 400));
    document.getElementById('ctrlStatus').addEventListener('change', loadTasks);
    document.getElementById('ctrlProject').addEventListener('change', loadTasks);

    // Закрытие модалок по кнопкам "Отмена" и крестику
    document.querySelectorAll('[data-bs-dismiss="modal"]').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const modal = btn.closest('.modal');
            if (modal) hideModal(modal.id);
        });
    });
});

function debounce(fn, delay) {
    let timer;
    return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => fn(...args), delay);
    };
}