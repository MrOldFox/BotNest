from sqlalchemy import func
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, selectinload  # Убедитесь, что модели импортированы корректно

from core.database.models import async_session
from core.database.models import *


class Database:
    def __init__(self):
        self.session = async_session()

    async def get_product_by_id(self, product_id: int):
        async with async_session() as session:
            query = select(Product).options(selectinload(Product.brand)).where(Product.product_id == product_id)
            result = await session.execute(query)
            return result.scalars().first()

    async def get_products_by_name(self, product_name: str):
        async with async_session() as session:
            query = select(Product).where(Product.name == product_name)
            result = await session.execute(query)
            return result.fetchall()

    # async def get_products_by_category(self, brand_id: int):
    #     async with self.session() as session:
    #         query = select(Product).where(Product.brand_id == brand_id)
    #         result = await session.execute(query)
    #         return result.scalars().all()

    async def get_brand_id_by_slug(self, brand_slug: str):
        async with async_session() as session:
            query = select(Brand.brand_id).where(Brand.name_slug == brand_slug)
            result = await session.execute(query)
            brand = result.scalar()
            return brand

    async def get_brand_slug_by_product_name(self, product_name: str):
        async with async_session() as session:
            # Создаем запрос для выбора slug бренда на основе имени продукта
            query = select(Brand.name_slug).join(Product).where(Product.name == product_name)
            result = await session.execute(query)
            brand_slug = result.scalar()
            return brand_slug


    async def get_products_by_color(self, product_name: str):
        async with async_session() as session:
            # Получаем все продукты указанного бренда без учета пагинации
            query = select(Product).where(Product.name == product_name).order_by(Product.name)
            all_products = await session.execute(query)
            all_products = all_products.scalars().all()

            return all_products

    async def get_brand_photo_url_by_slug(self, brand_slug: str):
        async with async_session() as session:
            query = select(Brand.photo_url).where(Brand.name_slug == brand_slug)
            result = await session.execute(query)
            photo_url = result.scalar_one_or_none()  # Возвращает URL или None, если такого нет
            return photo_url


    async def get_product_count_by_name(self, product_name: str):
        async with async_session() as session:
            query = select(func.count()).where(Product.name == product_name)
            result = await session.execute(query)
            count = result.scalar_one_or_none()
            return count if count is not None else 0

    async def get_product_name_by_id(self, product_id: str):
        async with async_session() as session:
            query = select(Product.name).where(Product.product_id == product_id)
            result = await session.execute(query)
            product_name = result.scalar()
            return product_name


    async def get_products_by_brand(self, brand_id: int, page: int = 0, items_per_page: int = 8):
        async with async_session() as session:
            # Получаем все продукты указанного бренда без учета пагинации
            query = select(Product).where(Product.brand_id == brand_id).order_by(Product.name)
            all_products = await session.execute(query)
            all_products = all_products.scalars().all()

            # Фильтруем уникальные имена продуктов
            unique_products = []
            seen_names = set()
            for product in all_products:
                if product.name not in seen_names:
                    unique_products.append(product)
                    seen_names.add(product.name)

            # Применяем пагинацию к уникальным продуктам
            start_index = page * items_per_page
            end_index = start_index + items_per_page
            paginated_products = unique_products[start_index:end_index]

            return paginated_products

    async def get_total_products_by_brand(self, brand_id: int):
        async with async_session() as session:
            # Создаем запрос для подсчета количества продуктов определенного бренда
            query = select(func.count()).select_from(Product).where(Product.brand_id == brand_id)
            result = await session.execute(query)

            # Возвращаем количество продуктов бренда
            return result.scalar_one()

    async def get_unique_product_names_count_by_brand(self, brand_id: int):
        async with async_session() as session:
            query = (
                select(func.count(Product.name.distinct()))
                .where(Product.brand_id == brand_id)
            )
            result = await session.execute(query)
            return result.scalar_one()

    async def get_total_products_by_color(self, product_name: str):
        async with async_session() as session:
            # Создаем запрос для подсчета количества продуктов определенного бренда
            query = select(func.count()).select_from(Product).where(Product.name == product_name)
            result = await session.execute(query)

            # Возвращаем количество продуктов бренда
            return result.scalar_one()

    async def get_all_categories(self):
        async with async_session() as session:
            result = await session.execute(select(Brand))
            # Возвращаем результат запроса
            return result.scalars().all()

    async def get_cart_items(self, user_id: int):
        async with async_session() as session:
            result = await session.execute(
                select(
                    Cart,
                    Product.name,
                    Product.stock_quantity,
                    Product.price  # Добавляем выборку цены товара
                ).join(Product).where(Cart.user_id == user_id)
            )
            items = result.all()
            cart_items = []
            for item in items:
                cart_item, product_name, stock_quantity, price = item
                cart_items.append((cart_item, product_name, stock_quantity, price))  # Добавляем цену в кортеж
            return cart_items


    async def update_cart_item_quantity(self, cart_id: int, new_quantity: int):
        async with async_session() as session:  # Предполагается, что async_session уже определен в вашем проекте
            # Находим запись в корзине по cart_id
            cart_item = await session.get(Cart, cart_id)
            if cart_item:
                # Обновляем количество товара
                cart_item.quantity = new_quantity
                # Коммитим изменения
                await session.commit()
                return True
            else:
                return False


    async def remove_item_from_cart(self, cart_id: int):
        async with async_session() as session:  # Предполагается, что async_session уже определен в вашем проекте
            # Находим запись в корзине по cart_id
            cart_item = await session.get(Cart, cart_id)
            if cart_item:
                # Удаляем запись из корзины
                await session.delete(cart_item)
                # Коммитим изменения
                await session.commit()
                return True
            else:
                return False


    async def add_item_to_cart(self, user_id: int, product_id: int, requested_quantity: int):
        async with async_session() as session:
            # Получаем информацию о продукте, включая количество на складе
            product_info = await session.execute(select(Product.stock_quantity).where(Product.product_id == product_id))
            product_stock_quantity = product_info.scalar_one_or_none()

            if product_stock_quantity is None:
                # Если продукт не найден, можно возвратить сообщение об ошибке
                return "Продукт не найден."

            if product_stock_quantity < requested_quantity:
                # Если на складе недостаточно товара
                return "Недостаточно товара на складе."

            # Проверяем, есть ли уже такой продукт в корзине пользователя
            existing_item = await session.execute(
                select(Cart).where(Cart.user_id == user_id, Cart.product_id == product_id))
            existing_item = existing_item.scalar_one_or_none()

            if existing_item:
                # Если элемент найден, проверяем, не превысит ли добавление запрошенного количества наличие на складе
                if existing_item.quantity + requested_quantity > product_stock_quantity:
                    return "Невозможно добавить указанное количество. Недостаточно товара на складе."
                # Обновляем количество в корзине без изменения на складе
                existing_item.quantity += requested_quantity
            else:
                # Создаем новый элемент в корзине
                new_item = Cart(user_id=user_id, product_id=product_id, quantity=requested_quantity)
                session.add(new_item)

            await session.commit()
            return "Товар добавлен в корзину."

    async def clear_cart(self, user_id: int):
        async with self.session() as session:
            query = select(Cart).where(Cart.user_id == user_id)
            result = await session.execute(query)
            items_to_delete = result.scalars().all()
            for item in items_to_delete:
                await session.delete(item)
            await session.commit()

    # async def get_products_by_brand(self, brand_slug: str, page: int = 0, items_per_page: int = 1):
    #     async with async_session() as session:
    #         brand = await session.execute(select(Brand).where(Brand.name_slug == brand_slug))
    #         brand = brand.scalars().first()
    #
    #         if brand is None:
    #             return []
    #
    #         query = select(Product).where(Product.brand_id == brand.brand_id).offset(page * items_per_page).limit(items_per_page)
    #         result = await session.execute(query)
    #         return result.scalars().all()