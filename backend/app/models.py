"""
Модели базы данных SQLAlchemy
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class Client(Base):
    """Модель клиента"""
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False, index=True)
    phone = Column(String(50), nullable=False)
    email = Column(String(255), index=True)
    company_name = Column(String(255))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Связь с заявками
    requests = relationship("Request", back_populates="client", cascade="all, delete-orphan")


class Request(Base):
    """Модель заявки/услуги"""
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    service_type = Column(String(100), nullable=False)
    status = Column(String(50), default="Новая", nullable=False)
    price = Column(Float, default=0.0)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Связь с клиентом
    client = relationship("Client", back_populates="requests")
