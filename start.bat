@echo off
REM Скрипт быстрого запуска Консульт CRM для Windows

echo ============================================
echo   🏢 Запуск Консульт CRM
echo ============================================
echo.

REM Проверка Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python не найден. Установите Python 3.8+ и попробуйте снова.
    pause
    exit /b 1
)

echo ✅ Python найден

REM Переход в папку backend
cd backend

REM Проверка виртуального окружения
if not exist "venv" (
    echo 📦 Создание виртуального окружения...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo 📥 Установка зависимостей...
    pip install -r requirements.txt
) else (
    echo ✅ Виртуальное окружение найдено
    call venv\Scripts\activate.bat
)

REM Запуск Backend
echo.
echo 🚀 Запуск Backend сервера на порту 8000...
start "Консульт CRM Backend" cmd /k "venv\Scripts\activate.bat && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

REM Задержка для запуска Backend
timeout /t 3 /nobreak >nul

REM Переход в папку frontend
cd ..\frontend

REM Запуск Frontend
echo 🌐 Запуск Frontend сервера на порту 3000...
start "Консульт CRM Frontend" cmd /k "python -m http.server 3000"

cd ..

echo.
echo ============================================
echo   ✅ Приложение запущено!
echo ============================================
echo.
echo 📊 Backend API: http://localhost:8000
echo 📖 API Docs: http://localhost:8000/docs
echo 🌐 Frontend: http://localhost:3000
echo.
echo Откроется браузер через 3 секунды...
echo.

timeout /t 3 /nobreak >nul

REM Открытие браузера
start http://localhost:3000

echo Для остановки закройте окна серверов
pause
