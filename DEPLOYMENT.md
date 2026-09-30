# 🚀 Развёртывание на Production

Руководство по развёртыванию Консульт CRM на production сервере.

## 📋 Предварительные требования

### Серверные требования
- **OS:** Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- **RAM:** Минимум 1GB, рекомендуется 2GB+
- **CPU:** 1+ core
- **Storage:** Минимум 10GB
- **Python:** 3.8+
- **Доступ:** SSH, root или sudo

### Доменное имя (опционально)
- Зарегистрированный домен
- DNS настроен на IP сервера

## 🔧 Подготовка сервера

### 1. Обновление системы

```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# CentOS/RHEL
sudo yum update -y
```

### 2. Установка зависимостей

```bash
# Ubuntu/Debian
sudo apt install -y python3 python3-pip python3-venv nginx git

# CentOS/RHEL
sudo yum install -y python3 python3-pip nginx git
```

### 3. Создание пользователя приложения

```bash
sudo useradd -m -s /bin/bash consultant
sudo su - consultant
```

## 📥 Установка приложения

### 1. Клонирование репозитория

```bash
cd /home/consultant
git clone <repository-url> consultant-crm
cd consultant-crm
```

### 2. Настройка Backend

```bash
cd backend

# Создание виртуального окружения
python3 -m venv venv

# Активация
source venv/bin/activate

# Установка зависимостей
pip install --upgrade pip
pip install -r requirements.txt

# Дополнительные production зависимости
pip install gunicorn
```

### 3. Настройка базы данных

#### Вариант A: SQLite (для небольших нагрузок)
```bash
# База создастся автоматически
python -c "from app.database import engine; from app.models import Base; Base.metadata.create_all(bind=engine)"
```

#### Вариант B: PostgreSQL (рекомендуется для production)

**Установка PostgreSQL:**
```bash
sudo apt install postgresql postgresql-contrib
```

**Создание базы и пользователя:**
```bash
sudo -u postgres psql

CREATE DATABASE consultant_crm;
CREATE USER consultant_user WITH PASSWORD 'strong_password_here';
GRANT ALL PRIVILEGES ON DATABASE consultant_crm TO consultant_user;
\q
```

**Обновление database.py:**
```python
# backend/app/database.py
SQLALCHEMY_DATABASE_URL = "postgresql://consultant_user:strong_password_here@localhost/consultant_crm"
```

**Установка драйвера:**
```bash
pip install psycopg2-binary
```

### 4. Наполнение тестовыми данными (опционально)

```bash
python seed_data.py
```

## 🔐 Настройка безопасности

### 1. Переменные окружения

Создайте файл `.env`:
```bash
nano /home/consultant/consultant-crm/backend/.env
```

Содержимое:
```env
DATABASE_URL=postgresql://consultant_user:password@localhost/consultant_crm
SECRET_KEY=your-super-secret-key-here
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
```

### 2. Обновление CORS

В `backend/app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-domain.com",
        "https://www.your-domain.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3. Настройка firewall

```bash
# UFW (Ubuntu)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw enable

# firewalld (CentOS)
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --reload
```

## 🌐 Настройка веб-сервера

### 1. Создание systemd сервиса для Backend

```bash
sudo nano /etc/systemd/system/consultant-backend.service
```

Содержимое:
```ini
[Unit]
Description=Consultant CRM Backend
After=network.target

[Service]
Type=notify
User=consultant
Group=consultant
WorkingDirectory=/home/consultant/consultant-crm/backend
Environment="PATH=/home/consultant/consultant-crm/backend/venv/bin"
ExecStart=/home/consultant/consultant-crm/backend/venv/bin/gunicorn \
    -w 4 \
    -k uvicorn.workers.UvicornWorker \
    --bind 127.0.0.1:8000 \
    --access-logfile /var/log/consultant/access.log \
    --error-logfile /var/log/consultant/error.log \
    app.main:app

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 2. Создание директории для логов

```bash
sudo mkdir -p /var/log/consultant
sudo chown consultant:consultant /var/log/consultant
```

### 3. Запуск Backend сервиса

```bash
sudo systemctl daemon-reload
sudo systemctl enable consultant-backend
sudo systemctl start consultant-backend
sudo systemctl status consultant-backend
```

### 4. Настройка Nginx

```bash
sudo nano /etc/nginx/sites-available/consultant-crm
```

Содержимое:
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # Frontend
    root /home/consultant/consultant-crm/frontend;
    index index.html;

    # Логирование
    access_log /var/log/nginx/consultant-access.log;
    error_log /var/log/nginx/consultant-error.log;

    # Frontend статика
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API прокси
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Кэширование статики
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### 5. Активация конфигурации

```bash
# Создание символической ссылки
sudo ln -s /etc/nginx/sites-available/consultant-crm /etc/nginx/sites-enabled/

# Проверка конфигурации
sudo nginx -t

# Перезапуск Nginx
sudo systemctl restart nginx
```

## 🔒 Настройка SSL (HTTPS)

### Использование Let's Encrypt (бесплатно)

```bash
# Установка Certbot
sudo apt install certbot python3-certbot-nginx

# Получение сертификата
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Автоматическое обновление
sudo certbot renew --dry-run
```

Nginx конфигурация обновится автоматически.

## 📊 Мониторинг

### 1. Просмотр логов

```bash
# Backend логи
sudo journalctl -u consultant-backend -f

# Nginx логи
sudo tail -f /var/log/nginx/consultant-access.log
sudo tail -f /var/log/nginx/consultant-error.log
```

### 2. Проверка статуса

```bash
# Backend
sudo systemctl status consultant-backend

# Nginx
sudo systemctl status nginx

# База данных (PostgreSQL)
sudo systemctl status postgresql
```

## 🔄 Обновление приложения

```bash
# Переход в директорию
cd /home/consultant/consultant-crm

# Получение изменений
git pull origin main

# Backend обновление
cd backend
source venv/bin/activate
pip install -r requirements.txt

# Перезапуск сервиса
sudo systemctl restart consultant-backend

# Перезапуск Nginx (если изменился frontend)
sudo systemctl restart nginx
```

## 💾 Резервное копирование

### Скрипт автоматического бэкапа

```bash
sudo nano /home/consultant/backup.sh
```

Содержимое:
```bash
#!/bin/bash

# Директория для бэкапов
BACKUP_DIR="/home/consultant/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Создание директории
mkdir -p $BACKUP_DIR

# SQLite бэкап
if [ -f "/home/consultant/consultant-crm/backend/consultant_crm.db" ]; then
    cp /home/consultant/consultant-crm/backend/consultant_crm.db \
       $BACKUP_DIR/db_backup_$DATE.db
fi

# PostgreSQL бэкап
# pg_dump -U consultant_user consultant_crm > $BACKUP_DIR/db_backup_$DATE.sql

# Удаление старых бэкапов (старше 30 дней)
find $BACKUP_DIR -type f -mtime +30 -delete

echo "Backup completed: $DATE"
```

### Настройка cron

```bash
chmod +x /home/consultant/backup.sh
crontab -e
```

Добавить:
```cron
# Ежедневный бэкап в 3:00 ночи
0 3 * * * /home/consultant/backup.sh
```

## 📈 Оптимизация производительности

### 1. Gunicorn workers

Рекомендуется: `(2 × CPU cores) + 1`

Для 2 CPU: `-w 5`

### 2. Nginx кэширование

Добавить в конфигурацию:
```nginx
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m max_size=100m inactive=60m;

location /api/ {
    proxy_cache api_cache;
    proxy_cache_valid 200 5m;
    # остальная конфигурация
}
```

### 3. Database connection pooling

В `database.py`:
```python
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True
)
```

## 🐛 Решение проблем

### Backend не запускается
```bash
# Проверить логи
sudo journalctl -u consultant-backend -n 50

# Проверить права
ls -la /home/consultant/consultant-crm/backend

# Проверить виртуальное окружение
/home/consultant/consultant-crm/backend/venv/bin/python --version
```

### 502 Bad Gateway
```bash
# Проверить, что Backend запущен
sudo systemctl status consultant-backend

# Проверить логи Nginx
sudo tail -f /var/log/nginx/error.log
```

### Проблемы с БД
```bash
# PostgreSQL статус
sudo systemctl status postgresql

# Проверить подключение
psql -U consultant_user -d consultant_crm -h localhost
```

## 📞 Поддержка

При проблемах проверьте:
1. Логи Backend (`journalctl -u consultant-backend`)
2. Логи Nginx (`/var/log/nginx/`)
3. Статус сервисов (`systemctl status`)
4. Firewall правила (`ufw status` / `firewall-cmd --list-all`)

## ✅ Чеклист развёртывания

- [ ] Сервер подготовлен и обновлён
- [ ] Все зависимости установлены
- [ ] Приложение склонировано
- [ ] База данных настроена
- [ ] Переменные окружения заданы
- [ ] Backend сервис создан и запущен
- [ ] Nginx настроен и работает
- [ ] SSL сертификат установлен
- [ ] Firewall настроен
- [ ] Бэкапы настроены
- [ ] Мониторинг работает
- [ ] Приложение доступно по домену

---

**Версия:** 1.0.0  
**Для production окружения**
