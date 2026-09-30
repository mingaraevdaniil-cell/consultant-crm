"""
Главный файл FastAPI приложения
"""
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional

from . import crud, models, schemas
from .database import engine, get_db

# Создание таблиц в БД
models.Base.metadata.create_all(bind=engine)

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


# === Эндпоинты для дашборда ===

@app.get("/api/dashboard", response_model=schemas.DashboardStats)
def get_dashboard_statistics(db: Session = Depends(get_db)):
    """Получить статистику для дашборда"""
    return crud.get_dashboard_stats(db)


# === Эндпоинты для клиентов ===

@app.get("/api/clients", response_model=List[schemas.Client])
def read_clients(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Получить список клиентов с пагинацией и поиском"""
    clients = crud.get_clients(db, skip=skip, limit=limit, search=search)
    return clients


@app.get("/api/clients/count")
def count_clients(
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Получить общее количество клиентов"""
    count = crud.get_clients_count(db, search=search)
    return {"count": count}


@app.get("/api/clients/{client_id}", response_model=schemas.ClientWithRequests)
def read_client(client_id: int, db: Session = Depends(get_db)):
    """Получить клиента по ID с его заявками"""
    db_client = crud.get_client(db, client_id=client_id)
    if db_client is None:
        raise HTTPException(status_code=404, detail="Клиент не найден")
    return db_client


@app.post("/api/clients", response_model=schemas.Client, status_code=201)
def create_client(client: schemas.ClientCreate, db: Session = Depends(get_db)):
    """Создать нового клиента"""
    return crud.create_client(db=db, client=client)


@app.put("/api/clients/{client_id}", response_model=schemas.Client)
def update_client(
    client_id: int,
    client: schemas.ClientUpdate,
    db: Session = Depends(get_db)
):
    """Обновить данные клиента"""
    db_client = crud.update_client(db, client_id=client_id, client=client)
    if db_client is None:
        raise HTTPException(status_code=404, detail="Клиент не найден")
    return db_client


@app.delete("/api/clients/{client_id}")
def delete_client(client_id: int, db: Session = Depends(get_db)):
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
    db: Session = Depends(get_db)
):
    """Получить список заявок с фильтрацией"""
    requests = crud.get_requests(
        db, skip=skip, limit=limit, client_id=client_id, status=status
    )
    return requests


@app.get("/api/requests/{request_id}", response_model=schemas.Request)
def read_request(request_id: int, db: Session = Depends(get_db)):
    """Получить заявку по ID"""
    db_request = crud.get_request(db, request_id=request_id)
    if db_request is None:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    return db_request


@app.post("/api/requests", response_model=schemas.Request, status_code=201)
def create_request(request: schemas.RequestCreate, db: Session = Depends(get_db)):
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
    db: Session = Depends(get_db)
):
    """Обновить заявку (частичное обновление)"""
    db_request = crud.update_request(db, request_id=request_id, request=request)
    if db_request is None:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    return db_request


@app.delete("/api/requests/{request_id}")
def delete_request(request_id: int, db: Session = Depends(get_db)):
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
