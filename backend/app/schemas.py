"""
Pydantic схемы для валидации данных
"""
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List


# Схемы для клиентов
class ClientBase(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=255)
    phone: str = Field(..., min_length=1, max_length=50)
    email: Optional[EmailStr] = None
    company_name: Optional[str] = None
    notes: Optional[str] = None


class ClientCreate(ClientBase):
    pass


class ClientUpdate(ClientBase):
    pass


class Client(ClientBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Схемы для заявок
class RequestBase(BaseModel):
    client_id: int
    service_type: str = Field(..., min_length=1, max_length=100)
    status: str = Field(default="Новая", max_length=50)
    price: float = Field(default=0.0, ge=0)
    description: Optional[str] = None


class RequestCreate(RequestBase):
    pass


class RequestUpdate(BaseModel):
    service_type: Optional[str] = None
    status: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)
    description: Optional[str] = None


class Request(RequestBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Расширенная схема клиента с заявками
class ClientWithRequests(Client):
    requests: List[Request] = []


# Схемы для статистики дашборда
class DashboardStats(BaseModel):
    total_clients: int
    active_requests: int
    total_revenue: float
    recent_requests: List[Request]


# Схемы для аутентификации
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    full_name: str = Field(..., min_length=1, max_length=255)


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str
