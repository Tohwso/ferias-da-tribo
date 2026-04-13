/* ===================================================================
   app.js — Férias do Time (vanilla JS, sem frameworks)
   CRUD completo: Teams, People, Vacations
   API prefix: /api/v1
   =================================================================== */

const API = '/api/v1';

// ─── Cache ──────────────────────────────────────────────
let _teamsCache = [];
let _peopleCache = [];
let _deleteCallback = null;

// ─── Init ───────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    setupTabs();
    setupDatePreview();
    setupFilterListeners();
    loadAll();
});

// ─── Tabs ───────────────────────────────────────────────
function setupTabs() {
    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            tab.classList.add('active');
            const section = document.getElementById('tab-' + tab.dataset.tab);
            if (section) section.classList.add('active');
        });
    });
}

// ─── Filter Listeners ───────────────────────────────────
function setupFilterListeners() {
    // Agenda filters
    const agendaTeam = document.getElementById('agenda-filter-team');
    const agendaPast = document.getElementById('agenda-toggle-past');
    if (agendaTeam) agendaTeam.addEventListener('change', loadAgenda);
    if (agendaPast) agendaPast.addEventListener('change', loadAgenda);

    // Vacations tab filters
    const vacTeam = document.getElementById('vac-filter-team');
    const vacPast = document.getElementById('vac-toggle-past');
    if (vacTeam) vacTeam.addEventListener('change', loadVacations);
    if (vacPast) vacPast.addEventListener('change', loadVacations);
}

// ─── Load All ───────────────────────────────────────────
async function loadAll() {
    await loadTeams();
    await loadPeople();
    loadAgenda();
    loadVacations();
}

// ═══════════════════════════════════════════════════════
//  TEAMS — CRUD
// ═══════════════════════════════════════════════════════

async function loadTeams() {
    try {
        const res = await fetch(`${API}/teams`);
        if (!res.ok) throw new Error('Erro ao carregar times');
        _teamsCache = await res.json();
        renderTeamsTable();
        populateTeamSelects();
    } catch (err) {
        showToast(err.message, 'error');
    }
}

function renderTeamsTable() {
    const tbody = document.getElementById('teams-tbody');
    if (!tbody) return;
    if (!_teamsCache.length) {
        tbody.innerHTML = '<tr><td colspan="4" class="empty-cell">Nenhum time cadastrado. Crie o primeiro!</td></tr>';
        return;
    }
    tbody.innerHTML = _teamsCache.map(t => `
        <tr>
            <td class="person-name">${esc(t.name)}</td>
            <td class="notes-text">${esc(t.description || '—')}</td>
            <td class="text-center"><span class="count-badge">${t.person_count}</span></td>
            <td class="text-center">
                <div class="actions-cell">
                    <button class="btn-icon" title="Editar" onclick="editTeam(${t.id})">✏️</button>
                    <button class="btn-icon danger" title="Excluir" onclick="deleteTeam(${t.id}, '${escAttr(t.name)}', ${t.person_count})">🗑️</button>
                </div>
            </td>
        </tr>
    `).join('');
}

function populateTeamSelects() {
    const opts = _teamsCache.map(t => `<option value="${t.id}">${esc(t.name)}</option>`).join('');
    const selects = {
        'agenda-filter-team': '<option value="">Todos os times</option>',
        'vac-filter-team':    '<option value="">Todos</option>',
        'person-team':        '<option value="">Selecione...</option>',
    };
    for (const [id, defaultOpt] of Object.entries(selects)) {
        const el = document.getElementById(id);
        if (el) {
            const prev = el.value;
            el.innerHTML = defaultOpt + opts;
            // Restore previous selection if still valid
            if (prev && el.querySelector(`option[value="${prev}"]`)) {
                el.value = prev;
            }
        }
    }
}

// Open team modal for create or edit
function openTeamModal(team = null) {
    document.getElementById('modal-team-title').textContent = team ? 'Editar Time' : 'Novo Time';
    document.getElementById('team-id').value = team ? team.id : '';
    document.getElementById('team-name').value = team ? team.name : '';
    document.getElementById('team-desc').value = team ? (team.description || '') : '';
    openModal('modal-team');
    document.getElementById('team-name').focus();
}

function editTeam(id) {
    const team = _teamsCache.find(t => t.id === id);
    if (team) openTeamModal(team);
}

async function submitTeam(e) {
    e.preventDefault();
    const id = document.getElementById('team-id').value;
    const payload = {
        name: document.getElementById('team-name').value.trim(),
        description: document.getElementById('team-desc').value.trim() || null,
    };

    try {
        const res = await fetch(`${API}/teams${id ? '/' + id : ''}`, {
            method: id ? 'PUT' : 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || 'Erro ao salvar time');
        }
        showToast(id ? 'Time atualizado!' : 'Time criado!');
        closeModal('modal-team');
        await loadAll();
    } catch (err) {
        showToast(err.message, 'error');
    }
}

function deleteTeam(id, name, count) {
    if (count > 0) {
        showToast(`Não é possível excluir "${name}": possui ${count} pessoa(s) vinculada(s)`, 'error');
        return;
    }
    confirmAction(`Excluir o time "${name}"?`, async () => {
        try {
            const res = await fetch(`${API}/teams/${id}`, { method: 'DELETE' });
            if (res.status === 409) {
                const err = await res.json();
                throw new Error(err.detail);
            }
            if (!res.ok) throw new Error('Erro ao excluir time');
            showToast('Time excluído!');
            await loadAll();
        } catch (err) {
            showToast(err.message, 'error');
        }
    });
}

// ═══════════════════════════════════════════════════════
//  PEOPLE — CRUD
// ═══════════════════════════════════════════════════════

async function loadPeople() {
    try {
        const res = await fetch(`${API}/people`);
        if (!res.ok) throw new Error('Erro ao carregar pessoas');
        _peopleCache = await res.json();
        renderPeopleTable();
        populatePersonSelect();
    } catch (err) {
        showToast(err.message, 'error');
    }
}

function renderPeopleTable() {
    const tbody = document.getElementById('people-tbody');
    if (!tbody) return;
    if (!_peopleCache.length) {
        tbody.innerHTML = '<tr><td colspan="5" class="empty-cell">Nenhuma pessoa cadastrada. Adicione a primeira!</td></tr>';
        return;
    }
    tbody.innerHTML = _peopleCache.map(p => `
        <tr>
            <td class="person-name">${esc(p.name)}</td>
            <td class="email">${esc(p.email)}</td>
            <td><span class="team-tag">${esc(p.team_name)}</span></td>
            <td class="text-center"><span class="count-badge">${p.vacation_count}</span></td>
            <td class="text-center">
                <div class="actions-cell">
                    <button class="btn-icon" title="Editar" onclick="editPerson(${p.id})">✏️</button>
                    <button class="btn-icon danger" title="Excluir" onclick="deletePerson(${p.id}, '${escAttr(p.name)}')">🗑️</button>
                </div>
            </td>
        </tr>
    `).join('');
}

function populatePersonSelect() {
    const el = document.getElementById('vacation-person');
    if (!el) return;
    const prev = el.value;
    el.innerHTML = '<option value="">Selecione...</option>' +
        _peopleCache.map(p => `<option value="${p.id}">${esc(p.name)} — ${esc(p.team_name)}</option>`).join('');
    if (prev && el.querySelector(`option[value="${prev}"]`)) {
        el.value = prev;
    }
}

function openPersonModal(person = null) {
    document.getElementById('modal-person-title').textContent = person ? 'Editar Pessoa' : 'Nova Pessoa';
    document.getElementById('person-id').value = person ? person.id : '';
    document.getElementById('person-name').value = person ? person.name : '';
    document.getElementById('person-email').value = person ? person.email : '';
    document.getElementById('person-team').value = person ? person.team_id : '';
    openModal('modal-person');
    document.getElementById('person-name').focus();
}

function editPerson(id) {
    const person = _peopleCache.find(p => p.id === id);
    if (person) openPersonModal(person);
}

async function submitPerson(e) {
    e.preventDefault();
    const id = document.getElementById('person-id').value;
    const payload = {
        name: document.getElementById('person-name').value.trim(),
        email: document.getElementById('person-email').value.trim(),
        team_id: parseInt(document.getElementById('person-team').value),
    };

    try {
        const res = await fetch(`${API}/people${id ? '/' + id : ''}`, {
            method: id ? 'PUT' : 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || 'Erro ao salvar pessoa');
        }
        showToast(id ? 'Pessoa atualizada!' : 'Pessoa cadastrada!');
        closeModal('modal-person');
        await loadAll();
    } catch (err) {
        showToast(err.message, 'error');
    }
}

function deletePerson(id, name) {
    confirmAction(`Excluir "${name}"? As férias associadas também serão excluídas.`, async () => {
        try {
            const res = await fetch(`${API}/people/${id}`, { method: 'DELETE' });
            if (!res.ok) {
                const err = await res.json().catch(() => ({}));
                throw new Error(err.detail || 'Erro ao excluir pessoa');
            }
            showToast('Pessoa excluída!');
            await loadAll();
        } catch (err) {
            showToast(err.message, 'error');
        }
    });
}

// ═══════════════════════════════════════════════════════
//  AGENDA — Read-only vacation overview
// ═══════════════════════════════════════════════════════

async function loadAgenda() {
    const teamId = document.getElementById('agenda-filter-team')?.value;
    const past = document.getElementById('agenda-toggle-past')?.checked;
    const params = new URLSearchParams();
    if (teamId) params.set('team_id', teamId);
    if (past) params.set('include_past', 'true');

    try {
        const res = await fetch(`${API}/vacations?${params}`);
        if (!res.ok) throw new Error('Erro ao carregar agenda');
        const data = await res.json();
        renderAgenda(data.vacations);
    } catch (err) {
        showToast(err.message, 'error');
    }
}

function renderAgenda(vacations) {
    const tbody = document.getElementById('agenda-tbody');
    if (!tbody) return;
    if (!vacations.length) {
        tbody.innerHTML = '<tr><td colspan="6" class="empty-cell">🏖️ Nenhuma férias encontrada</td></tr>';
        return;
    }
    const today = todayISO();
    tbody.innerHTML = vacations.map(v => {
        const isPast = v.end_date < today;
        const isCurrent = v.start_date <= today && v.end_date >= today;

        let statusHtml;
        if (v.has_overlap) {
            statusHtml = '<span class="overlap-badge">⚠️ Sobreposição</span>';
        } else if (isCurrent) {
            statusHtml = '<span class="status-current">🟢 Em curso</span>';
        } else if (isPast) {
            statusHtml = '<span class="status-past">Passada</span>';
        } else {
            statusHtml = '<span class="status-future">Futura</span>';
        }

        return `<tr class="${v.has_overlap ? 'overlap-row' : ''}">
            <td class="person-name">${esc(v.person_name)}</td>
            <td><span class="team-tag">${esc(v.team_name)}</span></td>
            <td>${formatDate(v.start_date)}</td>
            <td>${formatDate(v.end_date)}</td>
            <td class="text-center"><strong>${v.days}</strong></td>
            <td class="text-center">${statusHtml}</td>
        </tr>`;
    }).join('');
}

// ═══════════════════════════════════════════════════════
//  VACATIONS — CRUD
// ═══════════════════════════════════════════════════════

async function loadVacations() {
    const teamId = document.getElementById('vac-filter-team')?.value;
    const past = document.getElementById('vac-toggle-past')?.checked;
    const params = new URLSearchParams();
    if (teamId) params.set('team_id', teamId);
    if (past) params.set('include_past', 'true');

    try {
        const res = await fetch(`${API}/vacations?${params}`);
        if (!res.ok) throw new Error('Erro ao carregar férias');
        const data = await res.json();
        renderVacationsTable(data.vacations);
    } catch (err) {
        showToast(err.message, 'error');
    }
}

function renderVacationsTable(vacations) {
    const tbody = document.getElementById('vacations-tbody');
    if (!tbody) return;
    if (!vacations.length) {
        tbody.innerHTML = '<tr><td colspan="7" class="empty-cell">Nenhuma férias encontrada</td></tr>';
        return;
    }
    tbody.innerHTML = vacations.map(v => `
        <tr class="${v.has_overlap ? 'overlap-row' : ''}">
            <td class="person-name">${esc(v.person_name)}${v.has_overlap ? ' <span class="overlap-badge">⚠️</span>' : ''}</td>
            <td><span class="team-tag">${esc(v.team_name)}</span></td>
            <td>${formatDate(v.start_date)}</td>
            <td>${formatDate(v.end_date)}</td>
            <td class="text-center"><strong>${v.days}</strong></td>
            <td class="notes-text">${esc(v.notes || '—')}</td>
            <td class="text-center">
                <div class="actions-cell">
                    <button class="btn-icon" title="Editar" onclick="editVacation(${v.id})">✏️</button>
                    <button class="btn-icon danger" title="Excluir" onclick="deleteVacation(${v.id}, '${escAttr(v.person_name)}')">🗑️</button>
                </div>
            </td>
        </tr>
    `).join('');
}

function openVacationModal(vac = null) {
    document.getElementById('modal-vacation-title').textContent = vac ? 'Editar Férias' : 'Novas Férias';
    document.getElementById('vacation-id').value = vac ? vac.id : '';
    document.getElementById('vacation-person').value = vac ? vac.person_id : '';
    document.getElementById('vacation-start').value = vac ? vac.start_date : '';
    document.getElementById('vacation-end').value = vac ? vac.end_date : '';
    document.getElementById('vacation-notes').value = vac ? (vac.notes || '') : '';
    updateDaysPreview();
    openModal('modal-vacation');
}

async function editVacation(id) {
    try {
        const res = await fetch(`${API}/vacations/${id}`);
        if (!res.ok) throw new Error('Erro ao carregar férias');
        const vac = await res.json();
        openVacationModal(vac);
    } catch (err) {
        showToast(err.message, 'error');
    }
}

async function submitVacation(e) {
    e.preventDefault();
    const id = document.getElementById('vacation-id').value;
    const start = document.getElementById('vacation-start').value;
    const end = document.getElementById('vacation-end').value;

    // Client-side validation
    if (start > end) {
        showToast('Data de início deve ser anterior ou igual à data de fim', 'error');
        return;
    }

    // Backend auto-calculates "days" — we only send person_id, start_date, end_date, notes
    const payload = {
        person_id: parseInt(document.getElementById('vacation-person').value),
        start_date: start,
        end_date: end,
        notes: document.getElementById('vacation-notes').value.trim() || null,
    };

    try {
        const res = await fetch(`${API}/vacations${id ? '/' + id : ''}`, {
            method: id ? 'PUT' : 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || 'Erro ao salvar férias');
        }
        showToast(id ? 'Férias atualizada!' : 'Férias cadastrada!');
        closeModal('modal-vacation');
        loadAgenda();
        loadVacations();
    } catch (err) {
        showToast(err.message, 'error');
    }
}

function deleteVacation(id, name) {
    confirmAction(`Excluir as férias de "${name}"?`, async () => {
        try {
            const res = await fetch(`${API}/vacations/${id}`, { method: 'DELETE' });
            if (!res.ok) {
                const err = await res.json().catch(() => ({}));
                throw new Error(err.detail || 'Erro ao excluir férias');
            }
            showToast('Férias excluída!');
            loadAgenda();
            loadVacations();
        } catch (err) {
            showToast(err.message, 'error');
        }
    });
}

// ─── Days Preview (vacation form) ────────────────────────
function setupDatePreview() {
    const startEl = document.getElementById('vacation-start');
    const endEl = document.getElementById('vacation-end');
    if (startEl) startEl.addEventListener('change', updateDaysPreview);
    if (endEl) endEl.addEventListener('change', updateDaysPreview);
}

function updateDaysPreview() {
    const start = document.getElementById('vacation-start').value;
    const end = document.getElementById('vacation-end').value;
    const preview = document.getElementById('days-preview');
    if (!preview) return;
    if (!start || !end) { preview.textContent = ''; return; }
    const days = calcDays(start, end);
    if (days > 0) {
        preview.textContent = `📅 ${days} dia${days !== 1 ? 's' : ''}`;
    } else {
        preview.textContent = '⚠️ Datas inválidas';
    }
}

function calcDays(start, end) {
    if (!start || !end) return 0;
    const s = new Date(start + 'T00:00:00');
    const e = new Date(end + 'T00:00:00');
    const diff = (e - s) / (1000 * 60 * 60 * 24) + 1;
    return Math.max(0, Math.round(diff));
}

// ═══════════════════════════════════════════════════════
//  MODALS & CONFIRM DIALOG
// ═══════════════════════════════════════════════════════

function openModal(id) {
    const el = document.getElementById(id);
    if (el) {
        el.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    }
}

function closeModal(id) {
    const el = document.getElementById(id);
    if (el) {
        el.classList.add('hidden');
        document.body.style.overflow = '';
    }
}

function closeOnBackdrop(e, id) {
    if (e.target === e.currentTarget) closeModal(id);
}

function confirmAction(message, callback) {
    document.getElementById('confirm-message').textContent = message;
    _deleteCallback = callback;
    openModal('modal-confirm');
}

function confirmDelete() {
    closeModal('modal-confirm');
    if (_deleteCallback) {
        _deleteCallback();
        _deleteCallback = null;
    }
}

// Close modals on Escape key
document.addEventListener('keydown', e => {
    if (e.key === 'Escape') {
        const modalIds = ['modal-confirm', 'modal-vacation', 'modal-person', 'modal-team'];
        for (const id of modalIds) {
            const el = document.getElementById(id);
            if (el && !el.classList.contains('hidden')) {
                closeModal(id);
                break; // Close only the topmost modal
            }
        }
    }
});

// ═══════════════════════════════════════════════════════
//  UTILITIES
// ═══════════════════════════════════════════════════════

function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    if (!container) return;
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => {
        if (toast.parentNode) toast.remove();
    }, 3000);
}

/** Escape HTML for rendering inside elements */
function esc(text) {
    if (text == null) return '';
    const d = document.createElement('div');
    d.textContent = String(text);
    return d.innerHTML;
}

/** Escape for use inside HTML attribute values (onclick strings) */
function escAttr(text) {
    if (text == null) return '';
    return String(text)
        .replace(/\\/g, '\\\\')
        .replace(/'/g, "\\'")
        .replace(/"/g, '&quot;');
}

/** Format YYYY-MM-DD → DD/MM/YYYY */
function formatDate(dateStr) {
    if (!dateStr) return '—';
    const [y, m, d] = dateStr.split('-');
    return `${d}/${m}/${y}`;
}

/** Today in YYYY-MM-DD format */
function todayISO() {
    return new Date().toISOString().slice(0, 10);
}
