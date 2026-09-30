// API базовый URL - автоматически определяется
const API_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:8000/api'  // Для локальной разработки
    : 'https://consultant-crm-production.up.railway.app/api';  // Railway backend

let allClients = [];

// Загрузка данных при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    loadClients();
    loadRequests();
});

// Загрузка списка клиентов для селекта
async function loadClients() {
    try {
        const response = await fetch(`${API_URL}/clients?limit=1000`);
        if (!response.ok) throw new Error('Ошибка загрузки клиентов');
        
        allClients = await response.json();
        populateClientSelect();
        
    } catch (error) {
        console.error('Ошибка:', error);
    }
}

// Заполнение списка клиентов в селекте
function populateClientSelect() {
    const select = document.getElementById('clientSelect');
    select.innerHTML = '<option value="">Выберите клиента...</option>';
    
    allClients.forEach(client => {
        const option = document.createElement('option');
        option.value = client.id;
        option.textContent = `${client.full_name} (${client.phone})`;
        select.appendChild(option);
    });
}

// Загрузка списка заявок
async function loadRequests() {
    try {
        const statusFilter = document.getElementById('statusFilter').value;
        
        const params = new URLSearchParams({
            limit: 100
        });
        
        if (statusFilter) {
            params.append('status', statusFilter);
        }
        
        const response = await fetch(`${API_URL}/requests?${params}`);
        if (!response.ok) throw new Error('Ошибка загрузки заявок');
        
        const requests = await response.json();
        renderRequests(requests);
        
    } catch (error) {
        console.error('Ошибка:', error);
        showError('Не удалось загрузить список заявок');
    }
}

// Отображение заявок в таблице
function renderRequests(requests) {
    const tbody = document.getElementById('requestsTable');
    
    if (requests.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">Заявки не найдены</td></tr>';
        return;
    }
    
    tbody.innerHTML = requests.map(req => {
        const client = allClients.find(c => c.id === req.client_id);
        const clientName = client ? client.full_name : `ID: ${req.client_id}`;
        
        return `
            <tr>
                <td>${req.id}</td>
                <td>${clientName}</td>
                <td>${req.service_type}</td>
                <td>
                    <select class="form-select form-select-sm" onchange="updateRequestStatus(${req.id}, this.value)">
                        <option value="Новая" ${req.status === 'Новая' ? 'selected' : ''}>Новая</option>
                        <option value="В работе" ${req.status === 'В работе' ? 'selected' : ''}>В работе</option>
                        <option value="Завершена" ${req.status === 'Завершена' ? 'selected' : ''}>Завершена</option>
                        <option value="Отменена" ${req.status === 'Отменена' ? 'selected' : ''}>Отменена</option>
                    </select>
                </td>
                <td>${formatCurrency(req.price)}</td>
                <td>${formatDate(req.created_at)}</td>
                <td>
                    <button class="btn btn-sm btn-warning" onclick="editRequest(${req.id})" title="Редактировать">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="deleteRequest(${req.id})" title="Удалить">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

// Открыть модальное окно для создания заявки
function openRequestModal() {
    document.getElementById('requestModalTitle').textContent = 'Создать заявку';
    document.getElementById('requestForm').reset();
    document.getElementById('requestId').value = '';
    document.getElementById('status').value = 'Новая';
    document.getElementById('price').value = '0';
}

// Редактировать заявку
async function editRequest(requestId) {
    try {
        const response = await fetch(`${API_URL}/requests/${requestId}`);
        if (!response.ok) throw new Error('Ошибка загрузки данных заявки');
        
        const request = await response.json();
        
        document.getElementById('requestModalTitle').textContent = 'Редактировать заявку';
        document.getElementById('requestId').value = request.id;
        document.getElementById('clientSelect').value = request.client_id;
        document.getElementById('serviceType').value = request.service_type;
        document.getElementById('status').value = request.status;
        document.getElementById('price').value = request.price;
        document.getElementById('description').value = request.description || '';
        
        // Отключить выбор клиента при редактировании
        document.getElementById('clientSelect').disabled = true;
        
        new bootstrap.Modal(document.getElementById('requestModal')).show();
        
    } catch (error) {
        console.error('Ошибка:', error);
        showError('Не удалось загрузить данные заявки');
    }
}

// Сохранить заявку
async function saveRequest() {
    const requestId = document.getElementById('requestId').value;
    const requestData = {
        client_id: parseInt(document.getElementById('clientSelect').value),
        service_type: document.getElementById('serviceType').value,
        status: document.getElementById('status').value,
        price: parseFloat(document.getElementById('price').value) || 0,
        description: document.getElementById('description').value.trim() || null
    };
    
    // Валидация
    if (!requestData.client_id || !requestData.service_type) {
        showError('Клиент и тип услуги обязательны для заполнения');
        return;
    }
    
    try {
        let url, method;
        
        if (requestId) {
            // Обновление (используем PATCH для частичного обновления)
            url = `${API_URL}/requests/${requestId}`;
            method = 'PATCH';
            // Для обновления не отправляем client_id
            delete requestData.client_id;
        } else {
            // Создание
            url = `${API_URL}/requests`;
            method = 'POST';
        }
        
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestData)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Ошибка сохранения заявки');
        }
        
        // Включить обратно выбор клиента
        document.getElementById('clientSelect').disabled = false;
        
        bootstrap.Modal.getInstance(document.getElementById('requestModal')).hide();
        loadRequests();
        showSuccess(requestId ? 'Заявка обновлена' : 'Заявка создана');
        
    } catch (error) {
        console.error('Ошибка:', error);
        showError(error.message);
    }
}

// Быстрое обновление статуса заявки
async function updateRequestStatus(requestId, newStatus) {
    try {
        const response = await fetch(`${API_URL}/requests/${requestId}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: newStatus })
        });
        
        if (!response.ok) throw new Error('Ошибка обновления статуса');
        
        showSuccess('Статус обновлён');
        
    } catch (error) {
        console.error('Ошибка:', error);
        showError('Не удалось обновить статус');
        loadRequests(); // Перезагрузить для отката изменений
    }
}

// Удалить заявку
async function deleteRequest(requestId) {
    if (!confirm('Вы уверены, что хотите удалить эту заявку?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/requests/${requestId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) throw new Error('Ошибка удаления заявки');
        
        loadRequests();
        showSuccess('Заявка удалена');
        
    } catch (error) {
        console.error('Ошибка:', error);
        showError('Не удалось удалить заявку');
    }
}

// Вспомогательные функции
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

// Сброс disabled при закрытии модального окна
document.getElementById('requestModal').addEventListener('hidden.bs.modal', function () {
    document.getElementById('clientSelect').disabled = false;
});
