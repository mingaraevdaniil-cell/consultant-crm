# ⚡ Быстрый запуск

## 🪟 Для Windows

### Автоматический запуск
Дважды кликните на файл `start.bat` — скрипт автоматически:
1. Проверит установку Python
2. Создаст виртуальное окружение
3. Установит зависимости
4. Запустит Backend и Frontend
5. Откроет браузер

### Ручной запуск

**1. Откройте PowerShell/CMD в папке проекта**

**2. Запустите Backend:**
```cmd
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**3. В новом окне запустите Frontend:**
```cmd
cd frontend
python -m http.server 3000
```

**4. Откройте:** http://localhost:3000

---

## 🐧 Для Linux/Mac

### Автоматический запуск
```bash
chmod +x start.sh
./start.sh
```

### Ручной запуск

**1. Откройте терминал**

**2. Запустите Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**3. В новом терминале запустите Frontend:**
```bash
cd frontend
python3 -m http.server 3000
```

**4. Откройте:** http://localhost:3000

---

## 📝 Требования

- **Python 3.8 или выше**
- **pip** (установщик пакетов Python)
- Современный браузер (Chrome, Firefox, Edge, Safari)

### Проверка Python
```bash
python --version
# или
python3 --version
```

Если Python не установлен:
- **Windows:** https://www.python.org/downloads/
- **Linux:** `sudo apt install python3 python3-pip`
- **Mac:** `brew install python3`

---

## 🔥 Первый запуск

После запуска приложения:

1. **Дашборд** открывается автоматически
2. Создайте первого клиента: `Клиенты → Добавить клиента`
3. Создайте заявку: `Заявки → Создать заявку`
4. Наслаждайтесь работой! 🎉

---

## ❓ Проблемы?

### Ошибка "Address already in use"
Порт 8000 или 3000 уже занят. Измените порт:
```bash
# Backend на другом порту
uvicorn app.main:app --reload --port 8080

# Frontend на другом порту
python -m http.server 3001
```

### Ошибка "uvicorn not found"
Активируйте виртуальное окружение:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### CORS ошибки в браузере
Убедитесь, что:
- Backend запущен на порту 8000
- Frontend открыт через HTTP-сервер (не file://)

---

## 📚 Полная документация

Смотрите [README.md](README.md) для детальной информации.
