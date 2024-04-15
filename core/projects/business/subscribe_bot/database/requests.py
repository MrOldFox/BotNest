from datetime import datetime, timedelta
import asyncio

from sqlalchemy import update
from sqlalchemy.future import select

from core.database.models import *



class Database:
    def __init__(self):
        self.session = async_session()
# Добавление поддержки асинхронных сессий с БД
    async def check_subscription(self, telegram_id):
        async with async_session() as session:
            result = await session.execute(
                select(User)
                .where(User.telegram_id == telegram_id)
                .where(User.subscription_active == True)
            )
            user = result.scalar()
            return user is not None

    async def check_user_subscription(self, telegram_id: int):
        async with async_session() as session:
            result = await session.execute(
                select(User.subscription_active)
                .where(User.telegram_id == telegram_id)
            )
            user_subscription = result.scalar_one_or_none()
            return user_subscription

