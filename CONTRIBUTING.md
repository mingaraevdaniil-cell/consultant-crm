# 🤝 Руководство по внесению изменений

Спасибо за интерес к развитию проекта Консульт CRM!

## 📋 Структура проекта

```
consultant-crm/
├── backend/          # Backend на FastAPI
│   └── app/          # Приложение
├── frontend/         # Frontend на HTML/CSS/JS
│   ├── css/          # Стили
│   └── js/           # JavaScript логика
└── docs/             # Документация
```

## 🛠 Настройка окружения разработки

### 1. Клонирование репозитория
```bash
git clone <repository-url>
cd consultant-crm
```

### 2. Backend настройка
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Запуск в режиме разработки
```bash
# Backend с hot-reload
uvicorn app.main:app --reload

# Frontend
cd frontend
python -m http.server 3000
```

## 📝 Стандарты кодирования

### Python (Backend)
- Следуйте [PEP 8](https://pep8.org/)
- Используйте type hints
- Документируйте функции docstrings
- Максимальная длина строки: 100 символов

**Пример:**
```python
def get_client(db: Session, client_id: int) -> Optional[Client]:
    """
    Получить клиента по ID
    
    Args:
        db: Сессия базы данных
        client_id: Уникальный идентификатор клиента
        
    Returns:
        Объект клиента или None
    """
    return db.query(Client).filter(Client.id == client_id).first()
```

### JavaScript (Frontend)
- Используйте camelCase для переменных и функций
- Добавляйте комментарии для сложной логики
- Используйте async/await для асинхронных операций

**Пример:**
```javascript
/**
 * Загрузка списка клиентов с сервера
 * @param {number} page - Номер страницы
 * @param {string} search - Поисковый запрос
 */
async function loadClients(page = 0, search = '') {
    // Реализация
}
```

### CSS
- Используйте CSS переменные для цветов
- Именование классов: kebab-case
- Группируйте связанные стили

## 🔄 Процесс внесения изменений

### 1. Создайте ветку
```bash
git checkout -b feature/your-feature-name
# или
git checkout -b fix/bug-description
```

### 2. Внесите изменения
- Делайте атомарные коммиты
- Пишите понятные сообщения коммитов

```bash
git add .
git commit -m "feat: добавлена экспорт клиентов в Excel"
```

### 3. Тестирование
```bash
# Backend тесты
pytest

# Ручное тестирование API
python backend/test_api.py

# Проверка типов
mypy backend/app
```

### 4. Создайте Pull Request
- Опишите изменения
- Приложите скриншоты (для UI изменений)
- Укажите связанные issues

## 🐛 Отчёты об ошибках

При создании issue включите:
- Описание проблемы
- Шаги для воспроизведения
- Ожидаемое поведение
- Фактическое поведение
- Версия Python/браузера
- Скриншоты (если применимо)

## ✨ Предложения функций

Опишите:
- Какую проблему решает функция
- Предлагаемое решение
- Альтернативные варианты
- Примеры использования

## 📚 Документация

При добавлении функционала обновите:
- README.md - основная документация
- Комментарии в коде
- API документацию (автоматическая в FastAPI)

## 🎯 Приоритетные области для улучшений

- [ ] Экспорт данных (Excel, PDF)
- [ ] Расширенная аналитика
- [ ] Email уведомления
- [ ] Авторизация и роли пользователей
- [ ] Мобильная адаптация
- [ ] Unit и интеграционные тесты
- [ ] CI/CD pipeline

## 📞 Контакты

При вопросах создавайте issue в репозитории.

---

Спасибо за ваш вклад! 🙏
