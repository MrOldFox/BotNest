from datetime import datetime
import asyncio
from sqlalchemy.future import select

from core.database.models import *



class Database:
    def __init__(self):
        self.session = async_session()
# Добавление поддержки асинхронных сессий с БД
    async def add_request(self, telegram_id, text, hashtag):
        async with async_session() as session:
            new_request = Request(
                telegram_id=telegram_id,
                text=text,
                hashtag=hashtag,
                status=RequestStatus.accepted
            )
            session.add(new_request)
            await session.commit()
            return new_request.id