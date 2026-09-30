# 🌐 Размещение на настоящем веб-сайте

Пошаговое руководство по размещению Консульт CRM на реальном хостинге.

---

## 📋 Что вам нужно

1. **Сервер** (VPS/Dedicated)
2. **Доменное имя** (например: crm.vasha-kompaniya.ru)
3. **Доступ по SSH**
4. **Минимум 1GB RAM, 1 CPU, 10GB диск**

---

## 🎯 Варианты хостинга

### Вариант 1: VPS хостинг (рекомендуется) 💰 от 300₽/мес

**Провайдеры в России:**
- **Timeweb** - https://timeweb.com/ru/ (от 300₽/мес)
- **Selectel** - https://selectel.ru/ (от 400₽/мес)  
- **VDSina** - https://vdsina.ru/ (от 200₽/мес)
- **Reg.ru** - https://www.reg.ru/vps/ (от 350₽/мес)

**Что выбрать:**
- OS: Ubuntu 22.04 LTS
- RAM: минимум 1GB
- CPU: 1 ядро
- SSD: 10GB+

### Вариант 2: PaaS платформы (проще, дороже) 💰 от 500₽/мес

- **Heroku** - heroku.com (есть бесплатный план)
- **Railway.app** - railway.app (бесплатно для старта)
- **Render** - render.com (бесплатно для старта)
- **PythonAnywhere** - pythonanywhere.com (бесплатно для начала)

### Вариант 3: Shared хостинг ⚠️ Не рекомендуется

Обычный shared хостинг не подойдёт, нужна поддержка Python и возможность запуска процессов.

---

## 🚀 БЫСТРЫЙ СТАРТ: Railway.app (бесплатно)

Самый простой способ для начала:

### Шаг 1: Регистрация
1. Зайдите на https://railway.app/
2. Войдите через GitHub

### Шаг 2: Загрузка проекта на GitHub
```bash
cd consultant-crm

# Инициализация Git (если ещё не сделано)
git init
git add .
git commit -m "Initial commit"

# Создайте репозиторий на GitHub и загрузите:
git remote add origin https://github.com/ваш-username/consultant-crm.git
git push -u origin main
```

### Шаг 3: Деплой на Railway
1. В Railway: New Project → Deploy from GitHub repo
2. Выберите репозиторий consultant-crm
3. Railway автоматически обнаружит Python и задеплоит backend
4. Добавьте переменные окружения:
   - `PORT=8000`
   - `DATABASE_URL=postgresql://...` (Railway предоставит бесплатную PostgreSQL)

### Шаг 4: Frontend
Для frontend используйте **Vercel** или **Netlify** (бесплатно):
1. Зайдите на https://vercel.com/
2. Import Git Repository
3. Укажите папку `frontend`
4. Деплой!

---

## 🔧 ПОЛНАЯ УСТАНОВКА: VPS (Linux)

### Шаг 1: Подключение к серверу

```bash
ssh root@ваш-ip-адрес
# Или через PuTTY на Windows
```

### Шаг 2: Обновление системы

```bash
apt update && apt upgrade -y
apt install -y python3 python3-pip python3-venv nginx git postgresql postgresql-contrib
```

### Шаг 3: Создание пользователя

```bash
adduser consultant
usermod -aG sudo consultant
su - consultant
```

### Шаг 4: Загрузка проекта

```bash
cd /home/consultant
git clone https://github.com/ваш-username/consultant-crm.git
cd consultant-crm
```

### Шаг 5: Настройка Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

### Шаг 6: Настройка PostgreSQL

```bash
sudo -u postgres psql

# В psql:
CREATE DATABASE consultant_crm;
CREATE USER consultant_user WITH PASSWORD 'НадёжныйПароль123!';
GRANT ALL PRIVILEGES ON DATABASE consultant_crm TO consultant_user;
\q
```

Обновите `backend/app/database.py`:
```python
SQLALCHEMY_DATABASE_URL = "postgresql://consultant_user:НадёжныйПароль123!@localhost/consultant_crm"
```

### Шаг 7: Создание systemd сервиса

```bash
sudo nano /etc/systemd/system/consultant-backend.service
```

Вставьте:
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
    app.main:app

Restart=always

[Install]
WantedBy=multi-user.target
```

Сохраните (Ctrl+X, Y, Enter)

```bash
sudo systemctl daemon-reload
sudo systemctl enable consultant-backend
sudo systemctl start consultant-backend
sudo systemctl status consultant-backend
```

### Шаг 8: Настройка Nginx

```bash
sudo nano /etc/nginx/sites-available/consultant-crm
```

Вставьте:
```nginx
server {
    listen 80;
    server_name ваш-домен.ru www.ваш-домен.ru;

    # Frontend
    root /home/consultant/consultant-crm/frontend;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # API
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Статика
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/consultant-crm /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Шаг 9: Обновление Frontend API URL

Отредактируйте все JS файлы в `frontend/js/`:

```javascript
// Было:
const API_URL = 'http://localhost:8000/api';

// Стало:
const API_URL = '/api';  // Относительный путь через Nginx
```

### Шаг 10: Настройка SSL (HTTPS)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d ваш-домен.ru -d www.ваш-домен.ru
```

Следуйте инструкциям Certbot.

### Шаг 11: Настройка firewall

```bash
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

### Шаг 12: Проверка

Откройте в браузере:
```
https://ваш-домен.ru
```

---

## 📝 Настройка доменного имени

### Если домен у вас уже есть:

1. Зайдите в панель управления доменом
2. Найдите раздел "DNS настройки" или "DNS записи"
3. Добавьте A-запись:
   - **Тип:** A
   - **Имя:** @ (или пусто)
   - **Значение:** IP-адрес вашего сервера
   - **TTL:** 3600

4. Добавьте ещё одну A-запись для www:
   - **Тип:** A
   - **Имя:** www
   - **Значение:** IP-адрес вашего сервера
   - **TTL:** 3600

5. Подождите 15-60 минут (пока DNS обновится)

### Если домена нет:

Купите домен на:
- **Reg.ru** - от 99₽/год (.ru)
- **Timeweb** - от 149₽/год
- **Namecheap** - от $8/год

---

## 🔄 Автоматическое обновление

Создайте скрипт обновления:

```bash
nano /home/consultant/update.sh
```

```bash
#!/bin/bash
cd /home/consultant/consultant-crm
git pull origin main
cd backend
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart consultant-backend
sudo systemctl restart nginx
echo "Обновление завершено!"
```

```bash
chmod +x /home/consultant/update.sh
```

Для обновления:
```bash
./update.sh
```

---

## 💾 Резервное копирование

```bash
nano /home/consultant/backup.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/home/consultant/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Бэкап БД
pg_dump -U consultant_user consultant_crm > $BACKUP_DIR/db_$DATE.sql

# Удаление старых бэкапов (>30 дней)
find $BACKUP_DIR -type f -mtime +30 -delete
```

```bash
chmod +x /home/consultant/backup.sh
crontab -e
```

Добавьте:
```
0 3 * * * /home/consultant/backup.sh
```

---

## 📊 Мониторинг

Просмотр логов:
```bash
# Backend
sudo journalctl -u consultant-backend -f

# Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

---

## 💰 Примерные затраты

### Минимальная конфигурация:
- **VPS:** 300₽/мес
- **Домен .ru:** 200₽/год
- **SSL:** бесплатно (Let's Encrypt)
- **Итого:** ~320₽/мес

### Рекомендуемая конфигурация:
- **VPS (2GB RAM):** 500₽/мес
- **Домен .ru:** 200₽/год
- **Резервное копирование:** 100₽/мес
- **Итого:** ~620₽/мес

---

## ✅ Чеклист развёртывания

- [ ] VPS сервер арендован
- [ ] Домен куплен и настроен
- [ ] SSH доступ работает
- [ ] PostgreSQL установлена и настроена
- [ ] Backend запущен как systemd сервис
- [ ] Nginx настроен
- [ ] SSL сертификат установлен
- [ ] Firewall настроен
- [ ] Резервное копирование настроено
- [ ] Сайт открывается по домену

---

## 🆘 Нужна помощь?

Если что-то не получается:
1. Проверьте логи (см. раздел Мониторинг)
2. Смотрите DEPLOYMENT.md для деталей
3. Создайте issue в репозитории

---

**Удачи с запуском! 🚀**
