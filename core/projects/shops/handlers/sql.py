from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker # Убедитесь, что модели импортированы корректно

from core.database.models import async_session
from core.projects.shops.database.models import *


class Database:
    def __init__(self):
        self.session = async_session()

    async def get_product_by_id(self, product_id: int):
        async with self.session() as session:
            query = select(Product).where(Product.product_id == product_id)
            result = await session.execute(query)
            return result.scalars().first()

    async def get_products_by_category(self, brand_id: int):
        async with self.session() as session:
            query = select(Product).where(Product.brand_id == brand_id)
            result = await session.execute(query)
            return result.scalars().all()

    async def get_all_categories(self):
        async with async_session() as session:
            result = await session.execute(select(Brand))
            # Возвращаем результат запроса
            return result.scalars().all()

    async def get_cart_items(self, user_id: int):
        async with self.session() as session:
            query = select(Cart).where(Cart.user_id == user_id)
            result = await session.execute(query)
            return result.scalars().all()

    async def add_item_to_cart(self, user_id: int, product_id: int, quantity: int):
        async with self.session() as session:
            new_item = Cart(user_id=user_id, product_id=product_id, quantity=quantity)
            session.add(new_item)
            await session.commit()

    async def remove_item_from_cart(self, cart_id: int):
        async with self.session() as session:
            query = select(Cart).where(Cart.cart_id == cart_id)
            result = await session.execute(query)
            item_to_delete = result.scalars().first()
            await session.delete(item_to_delete)
            await session.commit()

    async def clear_cart(self, user_id: int):
        async with self.session() as session:
            query = select(Cart).where(Cart.user_id == user_id)
            result = await session.execute(query)
            items_to_delete = result.scalars().all()
            for item in items_to_delete:
                await session.delete(item)
            await session.commit()

    async def get_products_by_brand(self, brand_slug: str, page: int = 0, items_per_page: int = 1):
        async with async_session() as session:
            brand = await session.execute(select(Brand).where(Brand.name_slug == brand_slug))
            brand = brand.scalars().first()

            if brand is None:
                return []

            query = select(Product).where(Product.brand_id == brand.brand_id).offset(page * items_per_page).limit(items_per_page)
            result = await session.execute(query)
            return result.scalars().all()