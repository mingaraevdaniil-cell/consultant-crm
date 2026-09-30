"""
Скрипт для тестирования API
Запустите сервер перед выполнением: uvicorn app.main:app --reload
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_health():
    """Тест доступности API"""
    print("🔍 Проверка доступности API...")
    try:
        response = requests.get("http://localhost:8000/")
        if response.status_code == 200:
            print("✅ API доступен")
            print(f"   Ответ: {response.json()}")
            return True
        else:
            print(f"❌ Ошибка: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Не удалось подключиться к серверу: {e}")
        print("   Убедитесь, что сервер запущен: uvicorn app.main:app --reload")
        return False

def test_create_client():
    """Тест создания клиента"""
    print("\n📝 Тест создания клиента...")
    client_data = {
        "full_name": "Тестовый Клиент Тестович",
        "phone": "+7 (999) 999-99-99",
        "email": "test@test.ru",
        "company_name": "Тестовая Компания",
        "notes": "Это тестовый клиент"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/clients", json=client_data)
        if response.status_code == 201:
            client = response.json()
            print("✅ Клиент создан успешно")
            print(f"   ID: {client['id']}, ФИО: {client['full_name']}")
            return client['id']
        else:
            print(f"❌ Ошибка: {response.status_code}")
            print(f"   {response.text}")
            return None
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

def test_get_clients():
    """Тест получения списка клиентов"""
    print("\n📋 Тест получения списка клиентов...")
    try:
        response = requests.get(f"{BASE_URL}/clients?limit=5")
        if response.status_code == 200:
            clients = response.json()
            print(f"✅ Получено клиентов: {len(clients)}")
            for client in clients:
                print(f"   - {client['full_name']} ({client['phone']})")
            return True
        else:
            print(f"❌ Ошибка: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def test_search_clients():
    """Тест поиска клиентов"""
    print("\n🔍 Тест поиска клиентов...")
    try:
        response = requests.get(f"{BASE_URL}/clients?search=Тестовый")
        if response.status_code == 200:
            clients = response.json()
            print(f"✅ Найдено клиентов: {len(clients)}")
            return True
        else:
            print(f"❌ Ошибка: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def test_create_request(client_id):
    """Тест создания заявки"""
    print(f"\n📋 Тест создания заявки для клиента ID={client_id}...")
    request_data = {
        "client_id": client_id,
        "service_type": "Консультация",
        "status": "Новая",
        "price": 50000,
        "description": "Тестовая заявка на консультацию"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/requests", json=request_data)
        if response.status_code == 201:
            request = response.json()
            print("✅ Заявка создана успешно")
            print(f"   ID: {request['id']}, Услуга: {request['service_type']}")
            return request['id']
        else:
            print(f"❌ Ошибка: {response.status_code}")
            print(f"   {response.text}")
            return None
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

def test_update_request_status(request_id):
    """Тест обновления статуса заявки"""
    print(f"\n🔄 Тест обновления статуса заявки ID={request_id}...")
    try:
        response = requests.patch(
            f"{BASE_URL}/requests/{request_id}",
            json={"status": "В работе"}
        )
        if response.status_code == 200:
            request = response.json()
            print(f"✅ Статус обновлён: {request['status']}")
            return True
        else:
            print(f"❌ Ошибка: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def test_dashboard():
    """Тест получения статистики дашборда"""
    print("\n📊 Тест получения статистики...")
    try:
        response = requests.get(f"{BASE_URL}/dashboard")
        if response.status_code == 200:
            stats = response.json()
            print("✅ Статистика получена:")
            print(f"   👥 Всего клиентов: {stats['total_clients']}")
            print(f"   ⏳ Активных заявок: {stats['active_requests']}")
            print(f"   💰 Общий доход: {stats['total_revenue']:,.0f} ₽")
            return True
        else:
            print(f"❌ Ошибка: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def run_all_tests():
    """Запуск всех тестов"""
    print("="*60)
    print("🏢 Консульт CRM - Тестирование API")
    print("="*60)
    
    # Проверка доступности
    if not test_health():
        return
    
    # Создание клиента
    client_id = test_create_client()
    if not client_id:
        print("\n⚠️  Невозможно продолжить тесты без создания клиента")
        return
    
    # Получение списка клиентов
    test_get_clients()
    
    # Поиск клиентов
    test_search_clients()
    
    # Создание заявки
    request_id = test_create_request(client_id)
    
    # Обновление статуса заявки
    if request_id:
        test_update_request_status(request_id)
    
    # Статистика дашборда
    test_dashboard()
    
    print("\n" + "="*60)
    print("✅ Тестирование завершено!")
    print("="*60)

if __name__ == "__main__":
    run_all_tests()
