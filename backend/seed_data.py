"""
Скрипт для наполнения базы данных тестовыми данными
"""
from app.database import SessionLocal, engine
from app.models import Base, Client, Request
from datetime import datetime, timedelta
import random

# Создание таблиц
Base.metadata.create_all(bind=engine)

# Тестовые данные
clients_data = [
    {
        "full_name": "Иванов Иван Иванович",
        "phone": "+7 (495) 123-45-67",
        "email": "ivanov@example.com",
        "company_name": "ООО Рога и Копыта",
        "notes": "Важный клиент, требует особого внимания"
    },
    {
        "full_name": "Петрова Мария Сергеевна",
        "phone": "+7 (495) 234-56-78",
        "email": "petrova@business.ru",
        "company_name": "ИП Петрова М.С.",
        "notes": "Работаем с 2020 года"
    },
    {
        "full_name": "Сидоров Петр Алексеевич",
        "phone": "+7 (495) 345-67-89",
        "email": "sidorov@mail.ru",
        "company_name": "ЗАО Сидоров и Партнеры",
        "notes": None
    },
    {
        "full_name": "Козлова Анна Дмитриевна",
        "phone": "+7 (495) 456-78-90",
        "email": "kozlova@company.com",
        "company_name": "ООО Успех",
        "notes": "Заинтересована в долгосрочном сотрудничестве"
    },
    {
        "full_name": "Морозов Дмитрий Викторович",
        "phone": "+7 (495) 567-89-01",
        "email": "morozov@enterprise.ru",
        "company_name": "АО Морозов Групп",
        "notes": "VIP клиент"
    }
]

services = [
    "Консультация",
    "Аудит",
    "Сопровождение",
    "Юридические услуги",
    "Бухгалтерские услуги",
    "Налоговое консультирование"
]

statuses = ["Новая", "В работе", "Завершена", "Отменена"]

def seed_database():
    """Наполнение базы данных тестовыми данными"""
    db = SessionLocal()
    
    try:
        # Проверка, есть ли уже данные
        existing_clients = db.query(Client).count()
        if existing_clients > 0:
            print("⚠️  База данных уже содержит данные.")
            response = input("Очистить и создать новые данные? (y/n): ")
            if response.lower() != 'y':
                print("❌ Операция отменена.")
                return
            
            # Очистка таблиц
            db.query(Request).delete()
            db.query(Client).delete()
            db.commit()
            print("🗑️  Старые данные удалены.")
        
        # Создание клиентов
        print("📝 Создание клиентов...")
        created_clients = []
        for client_data in clients_data:
            client = Client(**client_data)
            db.add(client)
            db.commit()
            db.refresh(client)
            created_clients.append(client)
            print(f"   ✅ Создан клиент: {client.full_name}")
        
        # Создание заявок
        print("\n📋 Создание заявок...")
        request_count = 0
        for client in created_clients:
            # Каждому клиенту создаём от 1 до 4 заявок
            num_requests = random.randint(1, 4)
            
            for i in range(num_requests):
                # Случайная дата в последние 60 дней
                days_ago = random.randint(0, 60)
                created_at = datetime.now() - timedelta(days=days_ago)
                
                # Выбор статуса с учётом даты
                if days_ago < 7:
                    status = random.choice(["Новая", "В работе"])
                elif days_ago < 30:
                    status = random.choice(["В работе", "Завершена"])
                else:
                    status = random.choice(["Завершена", "Отменена"])
                
                # Генерация цены
                if status == "Завершена":
                    price = random.randint(10000, 500000)
                elif status == "В работе":
                    price = random.randint(5000, 300000)
                else:
                    price = 0
                
                request = Request(
                    client_id=client.id,
                    service_type=random.choice(services),
                    status=status,
                    price=price,
                    description=f"Описание заявки на {random.choice(services).lower()}. Требуется выполнить полный комплекс работ.",
                    created_at=created_at
                )
                db.add(request)
                request_count += 1
        
        db.commit()
        print(f"   ✅ Создано {request_count} заявок")
        
        # Статистика
        print("\n" + "="*50)
        print("✅ База данных успешно наполнена!")
        print("="*50)
        print(f"👥 Клиентов: {len(created_clients)}")
        print(f"📋 Заявок: {request_count}")
        
        # Статистика по статусам
        for status in statuses:
            count = db.query(Request).filter(Request.status == status).count()
            print(f"   - {status}: {count}")
        
        # Общий доход
        total_revenue = db.query(Request).filter(
            Request.status == "Завершена"
        ).with_entities(db.func.sum(Request.price)).scalar() or 0
        print(f"💰 Общий доход: {total_revenue:,.0f} ₽")
        print("="*50)
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🏢 Консульт CRM - Наполнение базы данных")
    print("="*50)
    seed_database()
