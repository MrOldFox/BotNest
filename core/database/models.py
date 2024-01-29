import datetime
import enum

import asyncpg

from sqlalchemy import BigInteger, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship, Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy import (
    Column, Integer, String, DateTime, func
)

from config_reader import config

# Строка подключения к базе данных PostgreSQL
database_url = config.database_url.get_secret_value()

# Создание асинхронного движка
engine = create_async_engine(database_url, echo=True)

# Создание асинхронной фабрики сессий
async_session = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


class Base(AsyncAttrs, DeclarativeBase):
    pass

class UserRole(enum.Enum):
    user = "user"
    moderator = "moderator"
    admin = "admin"


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    first_visit = Column(DateTime, default=datetime.datetime.utcnow)
    last_visit = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    last_message_id = Column(BigInteger, nullable=True)
    role = Column(Enum(UserRole), default=UserRole.user)
    max_tokens_gpt = Column(Integer, default=5)
    max_tokens_gpt_assistant = Column(Integer, default=5)

class OrderRequest(Base):
    __tablename__ = 'order_requests'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User")
    phone = Column(String(20))  # Ограничение до 50 символов
    email = Column(String(50))  # Ограничение до 50 символов
    description = Column(String(1000))  # Ограничение до 1000 символов
    contact_via_telegram = Column(Boolean)


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)