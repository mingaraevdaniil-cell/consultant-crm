"""
Скрипт для создания первого пользователя в системе
"""
import sys
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models
from app.auth import get_password_hash

def create_user(username: str, password: str, full_name: str):
    """Создание пользователя"""
    # Создание таблиц если их нет
    models.Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Проверка существования пользователя
        existing_user = db.query(models.User).filter(
            models.User.username == username
        ).first()
        
        if existing_user:
            print(f"❌ Пользователь '{username}' уже существует!")
            return False
        
        # Создание нового пользователя
        hashed_password = get_password_hash(password)
        new_user = models.User(
            username=username,
            full_name=full_name,
            hashed_password=hashed_password,
            is_active=True
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        print(f"✅ Пользователь успешно создан!")
        print(f"   ID: {new_user.id}")
        print(f"   Имя пользователя: {new_user.username}")
        print(f"   Полное имя: {new_user.full_name}")
        print(f"   Дата создания: {new_user.created_at}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка создания пользователя: {e}")
        db.rollback()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("  СОЗДАНИЕ ПОЛЬЗОВАТЕЛЯ ДЛЯ КОНСУЛЬТ CRM")
    print("=" * 60)
    
    # Ввод данных
    username = input("\nИмя пользователя (логин): ").strip()
    if not username:
        print("❌ Имя пользователя не может быть пустым!")
        sys.exit(1)
    
    password = input("Пароль (минимум 6 символов): ").strip()
    if len(password) < 6:
        print("❌ Пароль должен быть не менее 6 символов!")
        sys.exit(1)
    
    full_name = input("Полное имя: ").strip()
    if not full_name:
        print("❌ Полное имя не может быть пустым!")
        sys.exit(1)
    
    print("\n" + "-" * 60)
    print("Создание пользователя...")
    print("-" * 60)
    
    success = create_user(username, password, full_name)
    
    if success:
        print("\n" + "=" * 60)
        print("  Теперь можете войти в систему с этими учётными данными!")
        print("=" * 60)
    else:
        sys.exit(1)
