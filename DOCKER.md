# 🐳 Запуск через Docker

Этот документ описывает, как запустить Консульт CRM с помощью Docker и Docker Compose.

## Требования

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Быстрый запуск

### 1. Запуск всех сервисов

```bash
docker-compose up -d
```

Эта команда:
- Соберёт Docker образ для Backend
- Запустит Backend на порту 8000
- Запустит Frontend на порту 3000 (через Nginx)
- Создаст сеть между контейнерами

### 2. Проверка статуса

```bash
docker-compose ps
```

### 3. Просмотр логов

```bash
# Все сервисы
docker-compose logs -f

# Только Backend
docker-compose logs -f backend

# Только Frontend
docker-compose logs -f frontend
```

### 4. Остановка

```bash
docker-compose down
```

## Доступ к приложению

После запуска:
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

## Полезные команды

### Пересборка образов
```bash
docker-compose build
```

### Перезапуск сервисов
```bash
docker-compose restart
```

### Удаление контейнеров и volumes
```bash
docker-compose down -v
```

### Выполнение команд внутри контейнера
```bash
# Backend
docker-compose exec backend bash

# Применить миграции
docker-compose exec backend python -m alembic upgrade head

# Наполнить БД тестовыми данными
docker-compose exec backend python seed_data.py
```

## Конфигурация

### Изменение портов

Отредактируйте `docker-compose.yml`:

```yaml
services:
  backend:
    ports:
      - "8080:8000"  # изменить первое число
  
  frontend:
    ports:
      - "3001:80"    # изменить первое число
```

### Использование PostgreSQL вместо SQLite

1. Добавьте PostgreSQL в `docker-compose.yml`:

```yaml
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: consultant_crm
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

2. Обновите `backend/app/database.py`:

```python
SQLALCHEMY_DATABASE_URL = "postgresql://admin:password@db:5432/consultant_crm"
```

3. Добавьте зависимость в `backend/requirements.txt`:
```
psycopg2-binary==2.9.9
```

## Production режим

Для production используйте:

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

Создайте `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  backend:
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
    environment:
      - PYTHONUNBUFFERED=1
      - LOG_LEVEL=warning
    restart: always

  frontend:
    restart: always
```

## Решение проблем

### Порт уже занят
Измените порты в `docker-compose.yml` или остановите процесс, использующий порт.

### База данных не сохраняется
Убедитесь, что volume смонтирован правильно:
```yaml
volumes:
  - ./consultant_crm.db:/app/consultant_crm.db
```

### Ошибки CORS
Проверьте настройки CORS в `backend/app/main.py` - должен быть разрешён origin с Frontend.
