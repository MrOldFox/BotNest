import datetime
import asyncpg

from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy import (
    Column, Integer, String, DateTime, func
)

# Строка подключения к базе данных PostgreSQL
DATABASE_URL = "postgresql+asyncpg://postgres:Admin777777@localhost:5432/botnest"

# Создание асинхронного движка
engine = create_async_engine(DATABASE_URL, echo=True)

# Создание асинхронной фабрики сессий
async_session = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    first_visit = Column(DateTime, default=datetime.datetime.utcnow)
    last_visit = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    phone = Column(String)
    email = Column(String)

    last_message_id = Column(BigInteger, nullable=True)

    max_tokens_gpt = Column(Integer, default=5)
    max_tokens_gpt_assistant = Column(Integer, default=5)

class OrderRequest(Base):
    __tablename__ = 'bot_requests'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User")
    phone = Column(String)
    description = Column(String)
    deadline = Column(String)


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)