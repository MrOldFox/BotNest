from sqlalchemy import func, delete
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, selectinload, joinedload

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
            query = select(Brand.name_slug).join(Product).where(Product.name == product_name)
            result = await session.execute(query)
            brand_slug = result.scalar()
            return brand_slug


    async def get_products_by_color(self, product_name: str):
        async with async_session() as session:
            query = select(Product).where(Product.name == product_name).order_by(Product.name)
            all_products = await session.execute(query)
            all_products = all_products.scalars().all()

            return all_products

    async def get_brand_photo_url_by_slug(self, brand_slug: str):
        async with async_session() as session:
            query = select(Brand.photo_url).where(Brand.name_slug == brand_slug)
            result = await session.execute(query)
            photo_url = result.scalar_one_or_none()
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
            query = select(Product).where(Product.brand_id == brand_id).order_by(Product.name)
            all_products = await session.execute(query)
            all_products = all_products.scalars().all()

            unique_products = []
            seen_names = set()
            for product in all_products:
                if product.name not in seen_names:
                    unique_products.append(product)
                    seen_names.add(product.name)

            start_index = page * items_per_page
            end_index = start_index + items_per_page
            paginated_products = unique_products[start_index:end_index]

            return paginated_products

    async def get_total_products_by_brand(self, brand_id: int):
        async with async_session() as session:
            query = select(func.count()).select_from(Product).where(Product.brand_id == brand_id)
            result = await session.execute(query)

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
            query = select(func.count()).select_from(Product).where(Product.name == product_name)
            result = await session.execute(query)

            return result.scalar_one()

    async def get_all_categories(self):
        async with async_session() as session:
            result = await session.execute(select(Brand))
            return result.scalars().all()

    async def get_cart_items(self, user_id: int):
        async with async_session() as session:
            result = await session.execute(
                select(
                    Cart,
                    Product.name,
                    Product.stock_quantity,
                    Product.price,
                    Product.color
                ).join(Product).where(Cart.user_id == user_id)
                .order_by(Product.name)
            )
            items = result.all()
            cart_items = []
            for item in items:
                cart_item, product_name, stock_quantity, price, color = item  # Добавляем color в распаковку кортежа
                cart_items.append((cart_item, product_name, stock_quantity, price, color))  # Добавляем цвет в кортеж
            return cart_items

    from sqlalchemy.orm import joinedload

    async def get_checkout_items(self, user_id: int):
        async with async_session() as session:
            result = await session.execute(
                select(
                    Cart,
                    Product.name,
                    Product.stock_quantity,
                    Product.price,
                    Product.color
                ).join(Product).where(Cart.user_id == user_id)
                .order_by(Product.name)
            )
            items = result.all()
            return [(cart_item, product_name, stock_quantity, price, color) for
                    cart_item, product_name, stock_quantity, price, color in items]

    async def update_cart_item_quantity(self, cart_id: int, new_quantity: int):
        async with async_session() as session:
            cart_item = await session.get(Cart, cart_id)
            if cart_item:
                cart_item.quantity = new_quantity
                await session.commit()
                return True
            else:
                return False


    async def remove_item_from_cart(self, cart_id: int):
        async with async_session() as session:  # Предполагается, что async_session уже определен в вашем проекте
            cart_item = await session.get(Cart, cart_id)
            if cart_item:
                await session.delete(cart_item)
                await session.commit()
                return True
            else:
                return False


    async def add_item_to_cart(self, user_id: int, product_id: int, requested_quantity: int):
        async with async_session() as session:
            product_info = await session.execute(select(Product.stock_quantity).where(Product.product_id == product_id))
            product_stock_quantity = product_info.scalar_one_or_none()

            if product_stock_quantity is None:
                return "Продукт не найден."

            if product_stock_quantity < requested_quantity:
                return "Недостаточно товара на складе."

            existing_item = await session.execute(
                select(Cart).where(Cart.user_id == user_id, Cart.product_id == product_id))
            existing_item = existing_item.scalar_one_or_none()

            if existing_item:
                if existing_item.quantity + requested_quantity > product_stock_quantity:
                    return "Невозможно добавить указанное количество. Недостаточно товара на складе."
                existing_item.quantity += requested_quantity
            else:
                new_item = Cart(user_id=user_id, product_id=product_id, quantity=requested_quantity)
                session.add(new_item)

            await session.commit()
            return "Товар добавлен в корзину."

    async def clear_user_cart(self, user_id: int):
        async with async_session() as session:
            await session.execute(delete(Cart).where(Cart.user_id == user_id))
            await session.commit()

    async def add_purchase_history(self, user_id: int, total_amount: float, cart_items: list):
        async with async_session() as session:
            new_purchase = PurchaseHistory(
                user_id=user_id,
                total_amount=total_amount,
                purchase_date=datetime.datetime.now(),
                # или используйте func.now(), если хотите, чтобы время устанавливалось базой данных
                delivery_status=False,  # Исходное состояние доставки, предположим, что оно False
                delivery_address="Укажите адрес доставки"  # Это значение следует получить откуда-то ещё
            )
            session.add(new_purchase)
            await session.commit()
            await session.refresh(new_purchase)
            return new_purchase.purchase_id

    async def get_user_purchases(self, user_id: int):
        async with async_session() as session:
            result = await session.execute(
                select(PurchaseHistory)
                .where(PurchaseHistory.user_id == user_id)
                .order_by(PurchaseHistory.purchase_date.desc())
            )
            return result.scalars().all()

    async def get_order_details(self, purchase_id: int):
        async with async_session() as session:
            purchase_info = await session.execute(
                select(PurchaseHistory)
                .where(PurchaseHistory.purchase_id == purchase_id)
            )
            purchase_info = purchase_info.scalars().first()

            if not purchase_info:
                return None  # Если покупка с таким ID не найдена

            details_result = await session.execute(
                select(PurchaseDetail, Product.name)
                .join(Product, Product.product_id == PurchaseDetail.product_id)
                .where(PurchaseDetail.purchase_id == purchase_id)
            )
            purchase_details = details_result.all()

            products_details = [
                {
                    "name": detail[1],
                    "quantity": detail[0].quantity,
                    "price_at_purchase": detail[0].price_at_purchase
                }
                for detail in purchase_details
            ]

            return {
                "purchase_id": purchase_id,
                "user_id": purchase_info.user_id,
                "total_amount": purchase_info.total_amount,
                "purchase_date": purchase_info.purchase_date,
                "delivery_status": purchase_info.delivery_status,
                "delivery_address": purchase_info.delivery_address,
                "products": products_details
            }

    async def add_purchase_detail(self, purchase_id: int, product_id: int, quantity: int, price_at_purchase: float):
        async with async_session() as session:
            new_detail = PurchaseDetail(
                purchase_id=purchase_id,
                product_id=product_id,
                quantity=quantity,
                price_at_purchase=price_at_purchase
            )
            session.add(new_detail)
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
