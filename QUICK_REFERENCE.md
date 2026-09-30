# 📋 Быстрая шпаргалка

## 🚀 Локальный запуск

### Windows (автоматически):
```bash
start.bat
```

### Linux/Mac (автоматически):
```bash
chmod +x start.sh
./start.sh
```

### Вручную:

**Окно 1 - Backend:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # Linux/Mac
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Окно 2 - Frontend:**
```bash
cd frontend
python -m http.server 3000
```

**Открыть:**
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

---

## 🗄️ База данных

### SQLite (по умолчанию)
Создаётся автоматически в `backend/consultant_crm.db`

### PostgreSQL
```bash
# 1. Установить PostgreSQL
# 2. Создать БД:
sudo -u postgres psql
CREATE DATABASE consultant_crm;
CREATE USER consultant_user WITH PASSWORD 'пароль';
GRANT ALL PRIVILEGES ON DATABASE consultant_crm TO consultant_user;
\q

# 3. Установить драйвер:
pip install psycopg2-binary

# 4. Обновить backend/app/database.py:
SQLALCHEMY_DATABASE_URL = "postgresql://consultant_user:пароль@localhost/consultant_crm"
```

### Тестовые данные
```bash
cd backend
source venv/bin/activate
python seed_data.py
```

---

## 🌐 Размещение на сайте

### Самый простой способ (бесплатно):

1. **Railway.app для Backend:**
   - Зарегистрируйтесь на https://railway.app/
   - Deploy from GitHub
   - Railway автоматически запустит backend

2. **Vercel для Frontend:**
   - Зарегистрируйтесь на https://vercel.com/
   - Import Git Repository
   - Укажите папку `frontend`

### VPS сервер (полный контроль):

**Провайдеры в России:**
- Timeweb: от 300₽/мес
- Selectel: от 400₽/мес
- VDSina: от 200₽/мес

**Минимальные требования:**
- Ubuntu 22.04
- 1GB RAM
- 1 CPU
- 10GB диск

**Пошаговая инструкция:**
Смотрите `HOSTING_GUIDE.md`

---

## 🔧 Полезные команды

### Backend
```bash
# Запуск
uvicorn app.main:app --reload

# Создание таблиц вручную
python -c "from app.database import engine; from app.models import Base; Base.metadata.create_all(bind=engine)"

# Тесты
python test_api.py

# Наполнение данными
python seed_data.py
```

### Frontend
```bash
# Запуск
python -m http.server 3000

# Или через Node.js
npx http-server -p 3000
```

### База данных
```bash
# Подключиться к PostgreSQL
psql -U consultant_user -d consultant_crm

# Список таблиц
\dt

# Просмотр данных
SELECT * FROM clients;
SELECT * FROM requests;

# Выход
\q
```

### Git
```bash
# Инициализация
git init
git add .
git commit -m "Initial commit"

# Загрузка на GitHub
git remote add origin https://github.com/username/repo.git
git push -u origin main

# Обновление
git pull origin main
```

---

## 📄 Документация

- **START_HERE.md** - 🎯 начните здесь!
- **QUICKSTART.md** - быстрый запуск
- **README.md** - полное описание
- **INTERFACE.md** - руководство по интерфейсу
- **SETUP_DATABASE.md** - подключение БД
- **HOSTING_GUIDE.md** - размещение на сайте
- **DEPLOYMENT.md** - production развёртывание
- **ARCHITECTURE.md** - архитектура
- **CONTRIBUTING.md** - для разработчиков

---

## 🐛 Решение проблем

### Backend не запускается
```bash
# Проверить Python
python --version  # нужен 3.8+

# Проверить зависимости
pip list

# Переустановить
pip install -r requirements.txt
```

### Frontend показывает ошибки CORS
- Убедитесь, что backend запущен на порту 8000
- Откройте frontend через HTTP-сервер (не file://)

### Порт занят
```bash
# Windows - найти процесс на порту 8000
netstat -ano | findstr :8000

# Убить процесс
taskkill /PID номер_процесса /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

### База данных не создаётся
- Проверьте права на папку backend/
- Убедитесь, что backend запускается без ошибок

---

## 📞 API Endpoints

### Клиенты
```
GET    /api/clients          - список
GET    /api/clients/count    - количество
GET    /api/clients/{id}     - получить
POST   /api/clients          - создать
PUT    /api/clients/{id}     - обновить
DELETE /api/clients/{id}     - удалить
```

### Заявки
```
GET    /api/requests         - список
GET    /api/requests/{id}    - получить
POST   /api/requests         - создать
PATCH  /api/requests/{id}    - обновить
DELETE /api/requests/{id}    - удалить
```

### Статистика
```
GET    /api/dashboard        - дашборд
```

**Тестирование API:** http://localhost:8000/docs

---

## 💡 Первые шаги после запуска

1. Откройте http://localhost:3000
2. Перейдите в "Клиенты"
3. Нажмите "Добавить клиента"
4. Заполните форму (минимум ФИО и телефон)
5. Перейдите в "Заявки"
6. Создайте заявку для клиента
7. Вернитесь на Дашборд - увидите статистику!

---

## 🎯 Структура проекта

```
consultant-crm/
├── backend/          Backend на Python/FastAPI
│   └── app/          Код приложения
├── frontend/         Frontend на HTML/CSS/JS
│   ├── css/          Стили
│   └── js/           JavaScript
└── *.md              Документация
```

---

**Версия:** 1.0.0  
**Для быстрого доступа сохраните этот файл!**
