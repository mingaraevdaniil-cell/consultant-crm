# 🚂 Развёртывание на Railway.app

## Пошаговая инструкция для размещения Консульт CRM на Railway.app

---

## ✅ Что уже подготовлено

- Файлы конфигурации Railway созданы
- Requirements.txt обновлён
- CORS настроен для production
- .gitignore настроен

---

## Шаг 1: Загрузите проект на GitHub

### 1.1 Откройте PowerShell в папке проекта

Нажмите `Win + R`, введите `powershell` и нажмите Enter.

Перейдите в папку проекта:
```powershell
cd C:\Users\User\source\repos\prop
```

### 1.2 Инициализируйте Git репозиторий

```powershell
git init
git add .
git commit -m "Initial commit - Consultant CRM"
```

### 1.3 Создайте репозиторий на GitHub

1. Откройте https://github.com/ и войдите в аккаунт
2. Нажмите зелёную кнопку **"New"** (или плюс → New repository)
3. Заполните:
   - **Repository name:** consultant-crm
   - **Description:** CRM система для ООО Консульт
   - **Visibility:** Public или Private (ваш выбор)
   - НЕ создавайте README, .gitignore или license (у нас уже есть)
4. Нажмите **"Create repository"**

### 1.4 Загрузите код на GitHub

GitHub покажет команды. Выполните их в PowerShell:

```powershell
git remote add origin https://github.com/ваш-username/consultant-crm.git
git branch -M main
git push -u origin main
```

Если попросит логин/пароль:
- **Username:** ваш GitHub username
- **Password:** создайте Personal Access Token на https://github.com/settings/tokens

---

## Шаг 2: Развёртывание Backend на Railway

### 2.1 Зарегистрируйтесь на Railway

1. Откройте https://railway.app/
2. Нажмите **"Login"** → **"Login with GitHub"**
3. Разрешите доступ

### 2.2 Создайте новый проект

1. В Railway нажмите **"New Project"**
2. Выберите **"Deploy from GitHub repo"**
3. Если попросит доступ к GitHub - разрешите
4. Выберите репозиторий **consultant-crm**

### 2.3 Railway автоматически обнаружит Python

Railway увидит `requirements.txt` и `Procfile` и начнёт деплой.

### 2.4 Добавьте PostgreSQL базу данных

1. В проекте Railway нажмите **"+ New"** → **"Database"** → **"PostgreSQL"**
2. Railway автоматически создаст БД и добавит переменную `DATABASE_URL`

### 2.5 Настройте переменные окружения

1. Кликните на сервис backend в Railway
2. Перейдите в **"Variables"**
3. Нажмите **"Raw Editor"** и добавьте:

```env
PORT=8000
PYTHONUNBUFFERED=1
```

**ВАЖНО:** Переменная `DATABASE_URL` уже добавлена автоматически PostgreSQL!

### 2.6 Обновите код для использования Railway DATABASE_URL

Откройте файл `backend/app/database.py` и замените на:

```python
"""
Конфигурация базы данных SQLite/PostgreSQL
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL подключения - берём из переменной окружения или используем SQLite
DATABASE_URL = os.getenv("DATABASE_URL")

# Railway использует postgres://, но SQLAlchemy требует postgresql://
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Если нет DATABASE_URL, используем SQLite для локальной разработки
SQLALCHEMY_DATABASE_URL = DATABASE_URL or "sqlite:///./consultant_crm.db"

# Создание движка БД
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )
else:
    # PostgreSQL
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Создание фабрики сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()

# Зависимость для получения сессии БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

Сохраните и загрузите изменения:

```powershell
git add .
git commit -m "Update database config for Railway"
git push
```

Railway автоматически пересоберёт и задеплоит!

### 2.7 Получите URL вашего Backend

1. В Railway кликните на сервис backend
2. Перейдите в **"Settings"**
3. Найдите **"Networking"** → **"Public Networking"**
4. Нажмите **"Generate Domain"**
5. Railway создаст URL типа: `consultant-crm-production.up.railway.app`

**Сохраните этот URL!** Он понадобится для Frontend.

### 2.8 Проверьте работу Backend

Откройте в браузере:
```
https://ваш-домен.up.railway.app/docs
```

Должна открыться документация API Swagger!

---

## Шаг 3: Развёртывание Frontend на Vercel/Netlify

### Вариант А: Vercel (рекомендуется)

#### 3.1 Зарегистрируйтесь

1. Откройте https://vercel.com/
2. Нажмите **"Sign Up"** → **"Continue with GitHub"**

#### 3.2 Импортируйте проект

1. Нажмите **"Add New"** → **"Project"**
2. Выберите репозиторий **consultant-crm**
3. В настройках укажите:
   - **Framework Preset:** Other
   - **Root Directory:** `frontend`
   - **Build Command:** (оставьте пустым)
   - **Output Directory:** `./` (точка и слэш)

#### 3.3 Добавьте переменную окружения

1. Перейдите в **"Environment Variables"**
2. Добавьте:
   - **Name:** `RAILWAY_BACKEND_URL`
   - **Value:** `https://ваш-домен.up.railway.app`

Но вообще она не нужна, т.к. мы обновим JS файлы.

#### 3.4 Обновите Frontend для работы с Railway Backend

Откройте файлы в `frontend/js/` и обновите:

**dashboard.js, clients.js, requests.js:**

```javascript
// API базовый URL - для production используем Railway
const API_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:8000/api'  
    : 'https://ваш-railway-домен.up.railway.app/api';  // ЗАМЕНИТЕ НА ВАШ RAILWAY URL!
```

Сохраните и загрузите:
```powershell
git add .
git commit -m "Update API URL for Railway"
git push
```

Vercel автоматически пересоберёт!

#### 3.5 Получите URL Frontend

Vercel создаст URL типа: `consultant-crm.vercel.app`

### Вариант Б: Netlify

1. Откройте https://www.netlify.com/
2. **Sign Up** → **GitHub**
3. **Add new site** → **Import from Git**
4. Выберите репозиторий
5. В настройках:
   - **Base directory:** `frontend`
   - **Build command:** (пусто)
   - **Publish directory:** `frontend`
6. Deploy!

---

## Шаг 4: Обновите CORS на Backend

### 4.1 Добавьте URL Frontend в переменные Railway

1. В Railway откройте проект backend
2. Перейдите в **"Variables"**
3. Добавьте:

```env
ALLOWED_ORIGINS=https://ваш-frontend.vercel.app,https://www.ваш-frontend.vercel.app
```

Railway перезапустит backend автоматически.

---

## Шаг 5: Проверка работы

### 5.1 Откройте Frontend

```
https://ваш-frontend.vercel.app
```

### 5.2 Что проверить:

✅ Дашборд загружается  
✅ Можно создать клиента  
✅ Можно создать заявку  
✅ Статистика обновляется  

---

## 🎉 Готово! Ваш сайт онлайн!

**Frontend:** https://ваш-frontend.vercel.app  
**Backend API:** https://ваш-backend.up.railway.app  
**API Docs:** https://ваш-backend.up.railway.app/docs

---

## 💾 Наполнение базы тестовыми данными

Railway не даёт прямого SSH доступа, но можно запустить через API:

1. Откройте https://ваш-backend.up.railway.app/docs
2. Используйте API endpoints для создания клиентов и заявок

Или создайте endpoint для seed:

Добавьте в `backend/app/main.py`:

```python
@app.post("/api/seed")
def seed_database(db: Session = Depends(get_db)):
    """Наполнить БД тестовыми данными"""
    from . import crud
    
    # Создать тестовых клиентов
    clients_data = [
        {"full_name": "Иванов Иван Иванович", "phone": "+7 495 123-45-67", "email": "ivanov@test.ru"},
        {"full_name": "Петрова Мария Сергеевна", "phone": "+7 495 234-56-78", "email": "petrova@test.ru"},
    ]
    
    for data in clients_data:
        crud.create_client(db, schemas.ClientCreate(**data))
    
    return {"message": "База наполнена тестовыми данными"}
```

Затем откройте `/api/seed` в браузере.

---

## 🔧 Обновление проекта

Когда вносите изменения:

```powershell
git add .
git commit -m "Описание изменений"
git push
```

Railway и Vercel автоматически задеплоят обновления!

---

## 💰 Стоимость

**Railway:**
- Бесплатно: $5 кредитов/месяц (~500 часов работы)
- После: $0.000231/GB-час

**Vercel:**
- Бесплатно навсегда для личных проектов

**Итого:** Можно использовать **БЕСПЛАТНО**!

---

## 🆘 Решение проблем

### Backend не запускается на Railway
- Проверьте логи: Railway → Backend → Deployments → View Logs
- Убедитесь, что `Procfile` и `requirements.txt` в корне проекта

### Frontend не подключается к Backend
- Проверьте URL в JS файлах
- Проверьте CORS настройки в Railway Variables

### База данных пустая
- Используйте /api/seed endpoint или создайте данные через интерфейс

---

## 📞 Дополнительная помощь

- **Railway Docs:** https://docs.railway.app/
- **Vercel Docs:** https://vercel.com/docs

---

**Удачи с деплоем! 🚀**
