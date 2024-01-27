from sqlalchemy import select

from core.database.models import User, async_session
from core.keyboards.inline import *


async def update_last_message_id(bot, new_message_id, telegram_id):
    # Получаем пользователя из базы данных

    async with async_session() as session:
        user = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = user.scalar_one_or_none()

        if user:
            # Если у пользователя уже есть последнее сообщение, удаляем его
            if user.last_message_id:
                try:
                    await bot.delete_message(user.telegram_id, user.last_message_id)
                except Exception as e:
                    print(f"Ошибка при удалении сообщения: {e}")

            # Обновляем last_message_id пользователя
            user.last_message_id = new_message_id

            # Сохраняем изменения в базе данных
            await session.commit()
