from aiogram.filters import BaseFilter, Filter
from aiogram.types import Message


class isTrueContact(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        try:
            return message.contact.user_id == message.from_user.id
        except:
            return False
