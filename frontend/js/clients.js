// API базовый URL - автоматически определяется
const API_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:8000/api'  // Для локальной разработки
    : 'https://consultant-crm-production.up.railway.app/api';  // Railway backend

let currentPage = 0;
const pageSize = 10;
let currentSearch = '';

// Загрузка клиентов при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    loadClients();
    
    // Поиск с задержкой
    const searchInput = document.getElementById('searchInput');
    let searchTimeout;
    searchInput.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            currentSearch = e.target.value;
            currentPage = 0;
            loadClients();
        }, 500);
    });
});

// Загрузка списка клиентов
async function loadClients() {
    try {
        const params = new URLSearchParams({
            skip: currentPage * pageSize,
            limit: pageSize
        });
        
        if (currentSearch) {
            params.append('search', currentSearch);
        }
        
        const response = await fetch(`${API_URL}/clients?${params}`);
        if (!response.ok) throw new Error('Ошибка загрузки клиентов');
        
        const clients = await response.json();
        
        // Получение общего количества
        const countResponse = await fetch(`${API_URL}/clients/count?${currentSearch ? 'search=' + currentSearch : ''}`);
        const { count } = await countResponse.json();
        
        renderClients(clients);
        renderPagination(count);
        
    } catch (error) {
        console.error('Ошибка:', error);
        showError('Не удалось загрузить список клиентов');
    }
}

// Отображение клиентов в таблице
function renderClients(clients) {
    const tbody = document.getElementById('clientsTable');
    
    if (clients.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">Клиенты не найдены</td></tr>';
        return;
    }
    
    tbody.innerHTML = clients.map(client => `
        <tr>
            <td>${client.id}</td>
            <td>${client.full_name}</td>
            <td>${client.phone}</td>
            <td>${client.email || '-'}</td>
            <td>${client.company_name || '-'}</td>
            <td>${formatDate(client.created_at)}</td>
            <td>
                <button class="btn btn-sm btn-info" onclick="viewClient(${client.id})" title="Просмотр">
                    <i class="bi bi-eye"></i>
                </button>
                <button class="btn btn-sm btn-warning" onclick="editClient(${client.id})" title="Редактировать">
                    <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-sm btn-danger" onclick="deleteClient(${client.id})" title="Удалить">
                    <i class="bi bi-trash"></i>
                </button>
            </td>
        </tr>
    `).join('');
}

// Пагинация
function renderPagination(totalCount) {
    const totalPages = Math.ceil(totalCount / pageSize);
    const pagination = document.getElementById('pagination');
    
    if (totalPages <= 1) {
        pagination.innerHTML = '';
        return;
    }
    
    let html = '';
    
    // Предыдущая
    html += `<li class="page-item ${currentPage === 0 ? 'disabled' : ''}">
        <a class="page-link" href="#" onclick="changePage(${currentPage - 1}); return false;">Назад</a>
    </li>`;
    
    // Страницы
    for (let i = 0; i < totalPages; i++) {
        if (i === 0 || i === totalPages - 1 || (i >= currentPage - 2 && i <= currentPage + 2)) {
            html += `<li class="page-item ${i === currentPage ? 'active' : ''}">
                <a class="page-link" href="#" onclick="changePage(${i}); return false;">${i + 1}</a>
            </li>`;
        } else if (i === currentPage - 3 || i === currentPage + 3) {
            html += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
        }
    }
    
    // Следующая
    html += `<li class="page-item ${currentPage >= totalPages - 1 ? 'disabled' : ''}">
        <a class="page-link" href="#" onclick="changePage(${currentPage + 1}); return false;">Вперед</a>
    </li>`;
    
    pagination.innerHTML = html;
}

function changePage(page) {
    currentPage = page;
    loadClients();
}

// Открыть модальное окно для добавления клиента
function openClientModal() {
    document.getElementById('clientModalTitle').textContent = 'Добавить клиента';
    document.getElementById('clientForm').reset();
    document.getElementById('clientId').value = '';
}

// Просмотр информации о клиенте
async function viewClient(clientId) {
    try {
        const response = await fetch(`${API_URL}/clients/${clientId}`);
        if (!response.ok) throw new Error('Ошибка загрузки данных клиента');
        
        const client = await response.json();
        
        const content = `
            <div class="row mb-4">
                <div class="col-md-6">
                    <h5><i class="bi bi-person-badge"></i> Основная информация</h5>
                    <table class="table">
                        <tr><th>ФИО:</th><td>${client.full_name}</td></tr>
                        <tr><th>Телефон:</th><td>${client.phone}</td></tr>
                        <tr><th>Email:</th><td>${client.email || '-'}</td></tr>
                        <tr><th>Компания:</th><td>${client.company_name || '-'}</td></tr>
                        <tr><th>Дата создания:</th><td>${formatDate(client.created_at)}</td></tr>
                    </table>
                </div>
                <div class="col-md-6">
                    <h5><i class="bi bi-sticky"></i> Заметки</h5>
                    <p>${client.notes || 'Нет заметок'}</p>
                </div>
            </div>
            <div class="row">
                <div class="col-12">
                    <h5><i class="bi bi-clipboard-data"></i> История заявок</h5>
                    ${renderClientRequests(client.requests)}
                </div>
            </div>
        `;
        
        document.getElementById('clientInfoContent').innerHTML = content;
        new bootstrap.Modal(document.getElementById('clientInfoModal')).show();
        
    } catch (error) {
        console.error('Ошибка:', error);
        showError('Не удалось загрузить данные клиента');
    }
}

// Отображение заявок клиента
function renderClientRequests(requests) {
    if (!requests || requests.length === 0) {
        return '<p class="text-muted">Нет заявок</p>';
    }
    
    return `
        <table class="table table-sm table-hover">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Услуга</th>
                    <th>Статус</th>
                    <th>Стоимость</th>
                    <th>Дата</th>
                </tr>
            </thead>
            <tbody>
                ${requests.map(req => `
                    <tr>
                        <td>${req.id}</td>
                        <td>${req.service_type}</td>
                        <td><span class="badge ${getStatusClass(req.status)}">${req.status}</span></td>
                        <td>${formatCurrency(req.price)}</td>
                        <td>${formatDate(req.created_at)}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

// Редактировать клиента
async function editClient(clientId) {
    try {
        const response = await fetch(`${API_URL}/clients/${clientId}`);
        if (!response.ok) throw new Error('Ошибка загрузки данных клиента');
        
        const client = await response.json();
        
        document.getElementById('clientModalTitle').textContent = 'Редактировать клиента';
        document.getElementById('clientId').value = client.id;
        document.getElementById('fullName').value = client.full_name;
        document.getElementById('phone').value = client.phone;
        document.getElementById('email').value = client.email || '';
        document.getElementById('companyName').value = client.company_name || '';
        document.getElementById('notes').value = client.notes || '';
        
        new bootstrap.Modal(document.getElementById('clientModal')).show();
        
    } catch (error) {
        console.error('Ошибка:', error);
        showError('Не удалось загрузить данные клиента');
    }
}

// Сохранить клиента
async function saveClient() {
    const clientId = document.getElementById('clientId').value;
    const clientData = {
        full_name: document.getElementById('fullName').value.trim(),
        phone: document.getElementById('phone').value.trim(),
        email: document.getElementById('email').value.trim() || null,
        company_name: document.getElementById('companyName').value.trim() || null,
        notes: document.getElementById('notes').value.trim() || null
    };
    
    // Валидация
    if (!clientData.full_name || !clientData.phone) {
        showError('ФИО и телефон обязательны для заполнения');
        return;
    }
    
    try {
        const url = clientId ? `${API_URL}/clients/${clientId}` : `${API_URL}/clients`;
        const method = clientId ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(clientData)
        });
        
        if (!response.ok) throw new Error('Ошибка сохранения клиента');
        
        bootstrap.Modal.getInstance(document.getElementById('clientModal')).hide();
        loadClients();
        showSuccess(clientId ? 'Клиент обновлён' : 'Клиент создан');
        
    } catch (error) {
        console.error('Ошибка:', error);
        showError('Не удалось сохранить клиента');
    }
}

// Удалить клиента
async function deleteClient(clientId) {
    if (!confirm('Вы уверены, что хотите удалить этого клиента? Все связанные заявки также будут удалены.')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/clients/${clientId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) throw new Error('Ошибка удаления клиента');
        
        loadClients();
        showSuccess('Клиент удалён');
        
    } catch (error) {
        console.error('Ошибка:', error);
        showError('Не удалось удалить клиента');
    }
}

// Вспомогательные функции
function getStatusClass(status) {
    const statusMap = {
        'Новая': 'status-new',
        'В работе': 'status-in-progress',
        'Завершена': 'status-completed',
        'Отменена': 'status-cancelled'
    };
    return statusMap[status] || 'bg-secondary';
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('ru-RU', { 
        style: 'currency', 
        currency: 'RUB',
        minimumFractionDigits: 0
    }).format(amount);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('ru-RU', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    }).format(date);
}

function showError(message) {
    alert('Ошибка: ' + message);
}

function showSuccess(message) {
    alert(message);
}
