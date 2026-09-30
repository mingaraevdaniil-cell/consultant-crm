#!/bin/bash

# Скрипт быстрого запуска Консульт CRM

echo "🏢 Запуск Консульт CRM..."

# Проверка установки Python
if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null
then
    echo "❌ Python не найден. Установите Python 3.8+ и попробуйте снова."
    exit 1
fi

# Определение команды python
if command -v python3 &> /dev/null
then
    PYTHON_CMD=python3
else
    PYTHON_CMD=python
fi

echo "✅ Используется: $PYTHON_CMD"

# Проверка и установка зависимостей
if [ ! -d "backend/venv" ]; then
    echo "📦 Создание виртуального окружения..."
    cd backend
    $PYTHON_CMD -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
else
    echo "✅ Виртуальное окружение найдено"
    cd backend
    source venv/bin/activate
    cd ..
fi

# Запуск Backend в фоновом режиме
echo "🚀 Запуск Backend сервера на порту 8000..."
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Ожидание запуска Backend
sleep 3

# Запуск Frontend
echo "🌐 Запуск Frontend сервера на порту 3000..."
cd frontend
$PYTHON_CMD -m http.server 3000 &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Приложение запущено!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Backend API: http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs"
echo "🌐 Frontend: http://localhost:3000"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Для остановки нажмите Ctrl+C"

# Функция для остановки серверов
cleanup() {
    echo ""
    echo "🛑 Остановка серверов..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Серверы остановлены"
    exit 0
}

# Перехват сигнала для корректной остановки
trap cleanup SIGINT SIGTERM

# Ожидание
wait
