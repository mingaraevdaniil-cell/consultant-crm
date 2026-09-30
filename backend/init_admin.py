"""
Скрипт для создания администратора через переменные окружения
"""
import os
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models
from app.auth import get_password_hash

def init_admin():
    """Создание администратора если его нет"""
    # Создание таблиц
    models.Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Проверка существования пользователя
        existing = db.query(models.User).filter(
            models.User.username == "admin"
        ).first()
        
        if existing:
            print("✅ Администратор уже существует")
            return
        
        # Создание администратора
        admin = models.User(
            username="admin",
            full_name="Администратор",
            hashed_password=get_password_hash("admin123"),
            is_active=True
        )
        
        db.add(admin)
        db.commit()
        
        print("✅ Администратор создан!")
        print("   Логин: admin")
        print("   Пароль: admin123")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_admin()
