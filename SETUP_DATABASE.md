# 🗄️ Подключение базы данных

## SQLite (по умолчанию) ✅

База данных создаётся **автоматически** при первом запуске backend.

Файл базы: `backend/consultant_crm.db`

**Ничего делать не нужно!** Просто запустите приложение.

---

## PostgreSQL (для production) 🚀

### Шаг 1: Установка PostgreSQL

**Windows:**
1. Скачайте с https://www.postgresql.org/download/windows/
2. Установите PostgreSQL (версия 14 или выше)
3. Запомните пароль для пользователя `postgres`

**Linux:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

**Mac:**
```bash
brew install postgresql
brew services start postgresql
```

### Шаг 2: Создание базы данных

Откройте командную строку PostgreSQL:

**Windows:**
- Найдите "SQL Shell (psql)" в меню Пуск
- Или: `psql -U postgres`

**Linux/Mac:**
```bash
sudo -u postgres psql
```

Выполните команды:
```sql
-- Создание базы данных
CREATE DATABASE consultant_crm;

-- Создание пользователя
CREATE USER consultant_user WITH PASSWORD 'ваш_надёжный_пароль';

-- Выдача прав
GRANT ALL PRIVILEGES ON DATABASE consultant_crm TO consultant_user;

-- Выход
\q
```

### Шаг 3: Установка драйвера Python

```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install psycopg2-binary
```

### Шаг 4: Обновление конфигурации

Отредактируйте `backend/app/database.py`:

```python
# Закомментируйте SQLite:
# SQLALCHEMY_DATABASE_URL = "sqlite:///./consultant_crm.db"

# Добавьте PostgreSQL:
SQLALCHEMY_DATABASE_URL = "postgresql://consultant_user:ваш_надёжный_пароль@localhost/consultant_crm"

# Обновите engine:
engine = create_engine(SQLALCHEMY_DATABASE_URL)
# Удалите: connect_args={"check_same_thread": False}
```

### Шаг 5: Создание таблиц

Таблицы создадутся автоматически при первом запуске backend.

Или вручную:
```bash
cd backend
python -c "from app.database import engine; from app.models import Base; Base.metadata.create_all(bind=engine)"
```

### Шаг 6: Проверка подключения

```bash
# Проверка подключения
psql -U consultant_user -d consultant_crm -h localhost

# В psql:
\dt  # Список таблиц (должны быть clients и requests)
\q   # Выход
```

---

## 🌱 Наполнение тестовыми данными

После настройки базы:

```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python seed_data.py
```

Это создаст 5 клиентов и ~15 заявок для тестирования.

---

## 🔧 Строка подключения

### Формат для разных БД:

**SQLite:**
```python
sqlite:///./consultant_crm.db
```

**PostgreSQL (локально):**
```python
postgresql://username:password@localhost/database_name
```

**PostgreSQL (удалённо):**
```python
postgresql://username:password@host:5432/database_name
```

**MySQL:**
```python
mysql+pymysql://username:password@localhost/database_name
```

---

## 🔐 Безопасность

**Не храните пароли в коде!**

Создайте файл `backend/.env`:
```env
DATABASE_URL=postgresql://consultant_user:password@localhost/consultant_crm
```

Обновите `database.py`:
```python
import os
from dotenv import load_dotenv

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./consultant_crm.db")
```

Установите python-dotenv:
```bash
pip install python-dotenv
```

---

## ✅ Проверка работы

1. Запустите backend: `uvicorn app.main:app --reload`
2. Откройте: http://localhost:8000/docs
3. Попробуйте создать клиента через API
4. Проверьте в БД:
   ```sql
   SELECT * FROM clients;
   ```

---

## 🐛 Решение проблем

### Ошибка подключения к PostgreSQL
```bash
# Проверьте, запущен ли PostgreSQL
# Windows:
services.msc  # Найдите PostgreSQL

# Linux/Mac:
sudo systemctl status postgresql
```

### Ошибка "password authentication failed"
- Проверьте пароль в строке подключения
- Проверьте, что пользователь создан: `\du` в psql

### Ошибка "database does not exist"
```sql
CREATE DATABASE consultant_crm;
```

### Ошибка "psycopg2 not found"
```bash
pip install psycopg2-binary
```
