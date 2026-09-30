"""
Главный файл FastAPI приложения
"""
from datetime import timedelta
from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional

from . import crud, models, schemas, auth
from .database import engine, get_db

# Создание таблиц в БД
models.Base.metadata.create_all(bind=engine)

# Создание администратора по умолчанию при первом запуске
def init_admin():
    """Создание администратора если его нет"""
    from .database import SessionLocal
    db = SessionLocal()
    try:
        existing = db.query(models.User).filter(models.User.username == "admin").first()
        if not existing:
            admin = models.User(
                username="admin",
                full_name="Администратор",
                hashed_password=auth.get_password_hash("admin123"),
                is_active=True
            )
            db.add(admin)
            db.commit()
            print("✅ Администратор создан: admin / admin123")
        else:
            print("✅ Администратор уже существует")
    except Exception as e:
        print(f"⚠️ Ошибка создания администратора: {e}")
        db.rollback()
    finally:
        db.close()

# Инициализация админа при старте
init_admin()

# Инициализация FastAPI приложения
app = FastAPI(
    title="Консульт CRM",
    description="Система учёта клиентов для ООО Консульт",
    version="1.0.0"
)

# CORS для работы с фронтендом
import os

# Определяем разрешённые origins
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "")
if allowed_origins_env:
    ALLOWED_ORIGINS = [origin.strip() for origin in allowed_origins_env.split(",")]
else:
    # Дефолтные origins для разработки и production
    ALLOWED_ORIGINS = [
        "https://consultant-crm-frontend.vercel.app",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# === Эндпоинты аутентификации ===

@app.post("/api/auth/login", response_model=schemas.Token)
def login(login_data: schemas.LoginRequest, db: Session = Depends(get_db)):
    """Вход в систему"""
    user = auth.authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/api/auth/me", response_model=schemas.User)
async def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    """Получить информацию о текущем пользователе"""
    return current_user


@app.post("/api/auth/register", response_model=schemas.User, status_code=201)
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    """Регистрация нового пользователя (для первоначальной настройки)"""
    # Проверка существования пользователя
    existing_user = db.query(models.User).filter(
        models.User.username == user_data.username
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким именем уже существует"
        )
    
    # Создание нового пользователя
    hashed_password = auth.get_password_hash(user_data.password)
    db_user = models.User(
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        is_active=True
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


# === Эндпоинты для дашборда ===

@app.get("/api/dashboard", response_model=schemas.DashboardStats)
def get_dashboard_statistics(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Получить статистику для дашборда"""
    return crud.get_dashboard_stats(db)


# === Эндпоинты для клиентов ===

@app.get("/api/clients", response_model=List[schemas.Client])
def read_clients(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Получить список клиентов с пагинацией и поиском"""
    clients = crud.get_clients(db, skip=skip, limit=limit, search=search)
    return clients


@app.get("/api/clients/count")
def count_clients(
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Получить общее количество клиентов"""
    count = crud.get_clients_count(db, search=search)
    return {"count": count}


@app.get("/api/clients/{client_id}", response_model=schemas.ClientWithRequests)
def read_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Получить клиента по ID с его заявками"""
    db_client = crud.get_client(db, client_id=client_id)
    if db_client is None:
        raise HTTPException(status_code=404, detail="Клиент не найден")
    return db_client


@app.post("/api/clients", response_model=schemas.Client, status_code=201)
def create_client(
    client: schemas.ClientCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Создать нового клиента"""
    return crud.create_client(db=db, client=client)


@app.put("/api/clients/{client_id}", response_model=schemas.Client)
def update_client(
    client_id: int,
    client: schemas.ClientUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Обновить данные клиента"""
    db_client = crud.update_client(db, client_id=client_id, client=client)
    if db_client is None:
        raise HTTPException(status_code=404, detail="Клиент не найден")
    return db_client


@app.delete("/api/clients/{client_id}")
def delete_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Удалить клиента"""
    success = crud.delete_client(db, client_id=client_id)
    if not success:
        raise HTTPException(status_code=404, detail="Клиент не найден")
    return {"message": "Клиент успешно удалён"}


# === Эндпоинты для заявок ===

@app.get("/api/requests", response_model=List[schemas.Request])
def read_requests(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    client_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Получить список заявок с фильтрацией"""
    requests = crud.get_requests(
        db, skip=skip, limit=limit, client_id=client_id, status=status
    )
    return requests


@app.get("/api/requests/{request_id}", response_model=schemas.Request)
def read_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Получить заявку по ID"""
    db_request = crud.get_request(db, request_id=request_id)
    if db_request is None:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    return db_request


@app.post("/api/requests", response_model=schemas.Request, status_code=201)
def create_request(
    request: schemas.RequestCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Создать новую заявку"""
    # Проверка существования клиента
    client = crud.get_client(db, client_id=request.client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Клиент не найден")
    return crud.create_request(db=db, request=request)


@app.patch("/api/requests/{request_id}", response_model=schemas.Request)
def update_request(
    request_id: int,
    request: schemas.RequestUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Обновить заявку (частичное обновление)"""
    db_request = crud.update_request(db, request_id=request_id, request=request)
    if db_request is None:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    return db_request


@app.delete("/api/requests/{request_id}")
def delete_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Удалить заявку"""
    success = crud.delete_request(db, request_id=request_id)
    if not success:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    return {"message": "Заявка успешно удалена"}


# Корневой эндпоинт
@app.get("/")
def root():
    return {
        "message": "Консульт CRM API",
        "version": "1.0.0",
        "docs": "/docs"
    }
