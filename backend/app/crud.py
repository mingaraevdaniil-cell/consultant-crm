"""
CRUD операции для работы с базой данных
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import List, Optional
from . import models, schemas


# === CRUD для клиентов ===

def get_client(db: Session, client_id: int) -> Optional[models.Client]:
    """Получить клиента по ID"""
    return db.query(models.Client).filter(models.Client.id == client_id).first()


def get_clients(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    search: Optional[str] = None
) -> List[models.Client]:
    """Получить список клиентов с пагинацией и поиском"""
    query = db.query(models.Client)
    
    if search:
        search_filter = or_(
            models.Client.full_name.ilike(f"%{search}%"),
            models.Client.phone.ilike(f"%{search}%"),
            models.Client.email.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    return query.order_by(models.Client.created_at.desc()).offset(skip).limit(limit).all()


def get_clients_count(db: Session, search: Optional[str] = None) -> int:
    """Получить общее количество клиентов"""
    query = db.query(func.count(models.Client.id))
    
    if search:
        search_filter = or_(
            models.Client.full_name.ilike(f"%{search}%"),
            models.Client.phone.ilike(f"%{search}%"),
            models.Client.email.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    return query.scalar()


def create_client(db: Session, client: schemas.ClientCreate) -> models.Client:
    """Создать нового клиента"""
    db_client = models.Client(**client.model_dump())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client


def update_client(
    db: Session, 
    client_id: int, 
    client: schemas.ClientUpdate
) -> Optional[models.Client]:
    """Обновить данные клиента"""
    db_client = get_client(db, client_id)
    if db_client:
        for key, value in client.model_dump().items():
            setattr(db_client, key, value)
        db.commit()
        db.refresh(db_client)
    return db_client


def delete_client(db: Session, client_id: int) -> bool:
    """Удалить клиента"""
    db_client = get_client(db, client_id)
    if db_client:
        db.delete(db_client)
        db.commit()
        return True
    return False


# === CRUD для заявок ===

def get_request(db: Session, request_id: int) -> Optional[models.Request]:
    """Получить заявку по ID"""
    return db.query(models.Request).filter(models.Request.id == request_id).first()


def get_requests(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    client_id: Optional[int] = None,
    status: Optional[str] = None
) -> List[models.Request]:
    """Получить список заявок с фильтрацией"""
    query = db.query(models.Request)
    
    if client_id:
        query = query.filter(models.Request.client_id == client_id)
    
    if status:
        query = query.filter(models.Request.status == status)
    
    return query.order_by(models.Request.created_at.desc()).offset(skip).limit(limit).all()


def create_request(db: Session, request: schemas.RequestCreate) -> models.Request:
    """Создать новую заявку"""
    db_request = models.Request(**request.model_dump())
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    return db_request


def update_request(
    db: Session, 
    request_id: int, 
    request: schemas.RequestUpdate
) -> Optional[models.Request]:
    """Обновить заявку"""
    db_request = get_request(db, request_id)
    if db_request:
        update_data = request.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_request, key, value)
        db.commit()
        db.refresh(db_request)
    return db_request


def delete_request(db: Session, request_id: int) -> bool:
    """Удалить заявку"""
    db_request = get_request(db, request_id)
    if db_request:
        db.delete(db_request)
        db.commit()
        return True
    return False


# === Статистика для дашборда ===

def get_dashboard_stats(db: Session) -> dict:
    """Получить статистику для дашборда"""
    # Всего клиентов
    total_clients = db.query(func.count(models.Client.id)).scalar()
    
    # Активные заявки (в работе)
    active_requests = db.query(func.count(models.Request.id)).filter(
        models.Request.status == "В работе"
    ).scalar()
    
    # Суммарный доход по завершённым услугам
    total_revenue = db.query(func.sum(models.Request.price)).filter(
        models.Request.status == "Завершена"
    ).scalar() or 0.0
    
    # Последние 5 заявок
    recent_requests = db.query(models.Request).order_by(
        models.Request.created_at.desc()
    ).limit(5).all()
    
    return {
        "total_clients": total_clients,
        "active_requests": active_requests,
        "total_revenue": total_revenue,
        "recent_requests": recent_requests
    }
