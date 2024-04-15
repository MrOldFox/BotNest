from sqlalchemy import delete
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

    async def activate_subscription(self, telegram_id: int):
        """
        Активирует подписку пользователя на указанное количество дней.

        Args:
            telegram_id (int): Telegram ID пользователя.
        """
        async with async_session() as session:
            # Получаем пользователя по telegram_id
            result = await session.execute(select(User).where(User.telegram_id == telegram_id))
            user = result.scalar()

            if user:
                # Устанавливаем статус подписки активным и обновляем дату истечения подписки
                user.subscription_active = True
                await session.commit()


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