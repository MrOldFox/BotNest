
from sqlalchemy.future import select

from core.database.models import *


class Database:
    def __init__(self):
        self.session = async_session()

    async def check_user_tokens(self, telegram_id: int, token_type: str) -> bool:
        async with async_session() as session:
            query = select(User).where(User.telegram_id == telegram_id)
            result = await session.execute(query)
            user = result.scalars().first()
            if user:
                if token_type == 'gpt' and user.max_tokens_gpt > 0:
                    user.max_tokens_gpt -= 1  # Уменьшаем количество доступных токенов
                    await session.commit()
                    return True
                elif token_type == 'gpt_assistant' and user.max_tokens_gpt_assistant > 0:
                    user.max_tokens_gpt_assistant -= 1
                    await session.commit()
                    return True
                elif token_type == 'voice_gen' and user.max_tokens_voice_gen > 0:
                    user.max_tokens_voice_gen -= 1
                    await session.commit()
                    return True
            return False
