// API базовый URL
const API_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:8000/api'
    : 'https://consultant-crm-production.up.railway.app/api';

// Проверка авторизации при загрузке
document.addEventListener('DOMContentLoaded', () => {
    // Если уже авторизован, перенаправляем на главную
    if (localStorage.getItem('token')) {
        window.location.href = 'index.html';
    }
});

// Обработка формы входа
document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    const errorMessage = document.getElementById('errorMessage');
    const submitButton = e.target.querySelector('button[type="submit"]');
    
    // Очистка предыдущих ошибок
    errorMessage.style.display = 'none';
    errorMessage.textContent = '';
    
    // Блокировка кнопки
    submitButton.disabled = true;
    submitButton.textContent = 'Вход...';
    
    try {
        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Ошибка входа');
        }
        
        // Сохранение токена
        localStorage.setItem('token', data.access_token);
        
        // Получение информации о пользователе
        const userResponse = await fetch(`${API_URL}/auth/me`, {
            headers: {
                'Authorization': `Bearer ${data.access_token}`
            }
        });
        
        if (userResponse.ok) {
            const userData = await userResponse.json();
            localStorage.setItem('user', JSON.stringify(userData));
        }
        
        // Перенаправление на главную страницу
        window.location.href = 'index.html';
        
    } catch (error) {
        console.error('Ошибка входа:', error);
        errorMessage.textContent = error.message || 'Не удалось войти в систему. Проверьте имя пользователя и пароль.';
        errorMessage.style.display = 'block';
        
        // Разблокировка кнопки
        submitButton.disabled = false;
        submitButton.textContent = 'Войти';
    }
});
