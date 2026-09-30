// Модуль аутентификации
const Auth = {
    // Проверка авторизации
    isAuthenticated() {
        return !!localStorage.getItem('token');
    },
    
    // Получение токена
    getToken() {
        return localStorage.getItem('token');
    },
    
    // Получение информации о пользователе
    getUser() {
        const userStr = localStorage.getItem('user');
        return userStr ? JSON.parse(userStr) : null;
    },
    
    // Выход из системы
    logout() {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = 'login.html';
    },
    
    // Проверка авторизации и перенаправление
    requireAuth() {
        if (!this.isAuthenticated()) {
            window.location.href = 'login.html';
            return false;
        }
        return true;
    },
    
    // Получение заголовков с токеном
    getAuthHeaders() {
        const token = this.getToken();
        return {
            'Content-Type': 'application/json',
            'Authorization': token ? `Bearer ${token}` : ''
        };
    },
    
    // Fetch с автоматической авторизацией
    async fetchWithAuth(url, options = {}) {
        const token = this.getToken();
        
        if (!token) {
            this.logout();
            throw new Error('Не авторизован');
        }
        
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers,
            'Authorization': `Bearer ${token}`
        };
        
        // Если body - объект, сериализуем в JSON
        let body = options.body;
        if (body && typeof body === 'object' && !(body instanceof FormData)) {
            body = JSON.stringify(body);
        }
        
        const response = await fetch(url, {
            ...options,
            headers,
            body
        });
        
        // Если 401 - токен истек или недействителен
        if (response.status === 401) {
            this.logout();
            throw new Error('Сессия истекла');
        }
        
        return response;
    }
};

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    // Проверяем авторизацию на всех страницах кроме login.html
    if (!window.location.pathname.includes('login.html')) {
        Auth.requireAuth();
        
        // Добавляем информацию о пользователе в шапку
        const user = Auth.getUser();
        if (user) {
            const userInfo = document.getElementById('userInfo');
            if (userInfo) {
                userInfo.innerHTML = `
                    <span class="user-name">${user.full_name}</span>
                    <button onclick="Auth.logout()" class="btn-logout" title="Выход">
                        Выйти
                    </button>
                `;
            }
        }
    }
});
