// API базовый URL - автоматически определяется
const API_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:8000/api'  // Для локальной разработки
    : 'https://consultant-crm-production.up.railway.app/api';  // Railway backend

// Загрузка статистики при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    loadDashboardStats();
});

// Загрузка статистики для дашборда
async function loadDashboardStats() {
    try {
        const response = await fetch(`${API_URL}/dashboard`);
        if (!response.ok) throw new Error('Ошибка загрузки данных');
        
        const data = await response.json();
        
        // Обновление карточек статистики
        document.getElementById('totalClients').textContent = data.total_clients;
        document.getElementById('activeRequests').textContent = data.active_requests;
        document.getElementById('totalRevenue').textContent = 
            new Intl.NumberFormat('ru-RU', { style: 'currency', currency: 'RUB' }).format(data.total_revenue);
        
        // Загрузка последних заявок
        renderRecentRequests(data.recent_requests);
        
    } catch (error) {
        console.error('Ошибка:', error);
        showError('Не удалось загрузить статистику');
    }
}

// Отображение последних заявок
function renderRecentRequests(requests) {
    const tbody = document.getElementById('recentRequestsTable');
    
    if (requests.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">Нет данных</td></tr>';
        return;
    }
    
    tbody.innerHTML = requests.map(req => `
        <tr>
            <td>${req.id}</td>
            <td>ID клиента: ${req.client_id}</td>
            <td>${req.service_type}</td>
            <td><span class="badge ${getStatusClass(req.status)}">${req.status}</span></td>
            <td>${formatCurrency(req.price)}</td>
            <td>${formatDate(req.created_at)}</td>
        </tr>
    `).join('');
}

// Получение CSS класса для статуса
function getStatusClass(status) {
    const statusMap = {
        'Новая': 'status-new',
        'В работе': 'status-in-progress',
        'Завершена': 'status-completed',
        'Отменена': 'status-cancelled'
    };
    return statusMap[status] || 'bg-secondary';
}

// Форматирование валюты
function formatCurrency(amount) {
    return new Intl.NumberFormat('ru-RU', { 
        style: 'currency', 
        currency: 'RUB',
        minimumFractionDigits: 0
    }).format(amount);
}

// Форматирование даты
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

// Показать ошибку
function showError(message) {
    alert(message);
}
