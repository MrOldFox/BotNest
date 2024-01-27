from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from typing import Dict, Any, Callable, Awaitable
from datetime import datetime


def office_hours() -> bool:
    return datetime.now().weekday() in (0, 1, 2, 3, 4, 5) and datetime.now().hour in ([i for i in (range(8, 19))])


class OfficeHoursMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        if office_hours():
            return await handler(event, data)

        await event.answer('Время работы бота: Пн-пт с 8 до 18. Приходите в рабочее время')