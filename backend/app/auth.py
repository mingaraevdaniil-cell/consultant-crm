"""
Модуль аутентификации и авторизации
"""
from datetime import datetime, timedelta
from typing import Optional
import hashlib
import secrets
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from . import models
from .database import get_db

# Конфигурация
SECRET_KEY = "your-secret-key-change-this-in-production-2024"  # В production используйте переменную окружения
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 часов

# Схема безопасности
security = HTTPBearer()


def hash_password(password: str) -> str:
    """Хеширование пароля с солью (SHA-256)"""
    # Генерируем соль
    salt = secrets.token_hex(16)
    # Хешируем пароль с солью
    pwd_hash = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
    # Возвращаем соль + хеш
    return f"{salt}${pwd_hash}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля"""
    try:
        # Разделяем соль и хеш
        salt, pwd_hash = hashed_password.split('$')
        # Хешируем введенный пароль с той же солью
        new_hash = hashlib.sha256((plain_password + salt).encode('utf-8')).hexdigest()
        # Сравниваем хеши
        return new_hash == pwd_hash
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """Хеширование пароля (алиас для совместимости)"""
    return hash_password(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Создание JWT токена"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def authenticate_user(db: Session, username: str, password: str):
    """Аутентификация пользователя"""
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    if not user.is_active:
        return False
    return user


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Получение текущего пользователя из токена"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None or not user.is_active:
        raise credentials_exception
    
    return user
