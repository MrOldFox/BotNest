from sqlalchemy import select

from core.database.models import async_session


# async def get_users():
#     async with async_session() as session:
#         users = await session.execute(select(Us))
#         return users