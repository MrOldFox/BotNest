from sqlalchemy.future import select

from core.database.models import *


class Database:
    def __init__(self):
        self.session = async_session()

    async def get_first_lawyer(self):
        async with async_session() as session:
            result = await session.execute(select(Lawyer).order_by(Lawyer.lawyer_id).limit(1))
            first_lawyer = result.scalars().first()
            return first_lawyer

    async def get_total_lawyers(self):
        async with async_session() as session:
            result = await session.execute(select(func.count()).select_from(Lawyer))
            total_count = result.scalar_one()
            return total_count

    async def get_lawyer_by_id(self, lawyer_id: int):
        async with async_session() as session:
            result = await session.execute(select(Lawyer).where(Lawyer.lawyer_id == lawyer_id))
            lawyer = result.scalars().first()
            return lawyer

    async def get_first_news(self):
        async with async_session() as session:
            result = await session.execute(select(LegalNews).order_by(LegalNews.publication_date.desc()).limit(1))
            first_news = result.scalars().first()
            return first_news

    async def get_total_news(self):
        async with async_session() as session:
            result = await session.execute(select(func.count()).select_from(LegalNews))
            total_count = result.scalar_one()
            return total_count

    async def get_news_by_id(self, news_id: int):
        async with async_session() as session:
            result = await session.execute(select(LegalNews).where(LegalNews.news_id == news_id))
            news = result.scalars().first()
            return news

    async def get_news_with_pagination(self, page_number: int, page_size: int):
        async with async_session() as session:
            offset = (page_number - 1) * page_size
            query = select(LegalNews).order_by(LegalNews.publication_date.desc()).offset(offset).limit(page_size)
            result = await session.execute(query)
            news_list = result.scalars().all()
            return news_list