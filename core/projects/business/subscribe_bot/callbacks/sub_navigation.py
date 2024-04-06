from datetime import datetime
import asyncio

from aiogram import Router, F, Bot
from aiogram.client import bot
from aiogram.enums import ChatType
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery

from core.callbacks.navigation import query_message_photo
from core.handlers.callback import update_last_message_id

from core.keyboards.builders import inline_builder
from core.projects.business.subscribe_bot.database.requests import Database
from core.projects.business.subscribe_bot.keyboards.builders import sub_key_main, nosub_key_main, sub_key_buy, \
    sub_key_after_buy

router = Router()

db = Database()


@router.callback_query(F.data == '123')
async def card_main(query: CallbackQuery, bot: Bot):
    text = (
        f"<b>🏢 УК/ТСЖ бот</b>\n\n"
        f"Представляем телеграм-бота для управления заявками в чат-группах УК и ТСЖ. Этот инструмент превращает "
        f"обычные чаты в мощные платформы для управления обращениями жителей. С его помощью можно легко подавать "
        f"и отслеживать заявки прямо в процессе общения, используя специальные хэштеги. Наш демонстрационный "
        f"проект показывает, как эффективно обрабатывать сообщения о авариях, ремонте, уборке и других обращениях,"
        f"делая процесс удобным и оперативным.\n\n"
        f"Посмотреть демонстрационную группу и узнать больше о возможностях таких ботов можно "
        f"перейдя по ссылке в сообщении.\n\n"
        f"Вдохновитесь примером и создайте собственный бот для вашего сообщества, реализуя любые идеи и задачи, "
        f"ограничиваясь только вашей фантазией."
    )
    image_path = 'https://botnest.ru/wp-content/uploads/2024/botnest/images/uk_logo.webp'

    await query_message_photo(query, bot, text, image_path, uk_menu)


@router.callback_query(F.data == 'sub_main')
async def main_menu_handler(query: CallbackQuery, bot: Bot):
    telegram_id = query.from_user.id
    subscription_info = await db.check_user_subscription(telegram_id)
    subscription_active, subscription_expires = subscription_info if subscription_info else (False, None)

    # Текст сообщения в зависимости от статуса подписки
    if subscription_active:
        status_text = "🟢 Ваша подписка активна до " + subscription_expires.strftime('%Y-%m-%d %H:%M')
        menu_buttons = [
            [("Мои уроки", "my_lessons")],
        ]
    else:
        status_text = "🔴 У вас нет активной подписки. Подпишитесь, чтобы получить доступ к урокам."
        menu_buttons = [
            [("Подписаться", "subscribe")],
        ]

    text = (
        f"🌟 <b>Добро пожаловать в NestLearn!</b>\n\n"
        f"Ваш ключ к миру знаний и секретов успешного ведения телеграм-каналов ждет вас! 🚀\n"
        f"Мы предлагаем эксклюзивные уроки и гайды, которые помогут вашему каналу вырасти и зажечь аудиторию.\n\n"
        f"{status_text}\n\n"
    )

    if subscription_active:
        await query_message_photo(query, bot, text,
                                  "https://botnest.ru/wp-content/uploads/2024/botnest/images/NestLearn.webp",
                                  sub_key_main)
    else:
        await query_message_photo(query, bot, text,
                                  "https://botnest.ru/wp-content/uploads/2024/botnest/images/learnnestbot.png",
                                  nosub_key_main)


@router.callback_query(F.data == "subscription")
async def checkout(query: CallbackQuery, bot: Bot):

    # Добавляем фото первого товара в инвойсе для наглядности (если доступно)
    first_item_photo_url = 'https://botnest.ru/wp-content/uploads/2024/botnest/images/learnnestbot.png'

    text = (f'\nДля проведения пробной покупки используйте данные тестовой карты:' \
            f'\n\nНомер карты: 1111 1111 1111 1026,' \
            f'\nДата выпуска: 12/22,' \
            f'\nCVC: 000\n')

    prices = [LabeledPrice(label="Купить подписку", amount=10000)]

    # Отправляем инвойс пользователю
    send_message = await bot.send_invoice(
        chat_id=query.message.chat.id,
        title='Оплата подписки NestLearn',
        description=text,
        payload='sub',
        provider_token='381764678:TEST:73182',
        currency='rub',
        prices=prices,
        need_name=False,
        need_phone_number=False,
        need_shipping_address=False,
        need_email=False,
        start_parameter='sub',
        send_email_to_provider=False,
        send_phone_number_to_provider=False,
        provider_data=None,
        photo_url=first_item_photo_url,
        protect_content=False,
        reply_markup=inline_builder(sub_key_buy),
        allow_sending_without_reply=True,
    )

    await update_last_message_id(bot, send_message.message_id, query.from_user.id)
    await query.answer()


@router.pre_checkout_query()
async def handle_pre_checkout_query(query: PreCheckoutQuery, bot: Bot):
    if query.invoice_payload.startswith("sub"):
        print('OK')
        await bot.answer_pre_checkout_query(query.id, ok=True)
    elif query.invoice_payload.startswith("phone"):
        print('ok')
        await bot.answer_pre_checkout_query(query.id, ok=True)

@router.message(F.successful_payment)
async def handle_successful_payment(message: Message, bot: Bot):
    payload = message.successful_payment.invoice_payload
    if payload.startswith("sub"):
        print('OK2')
        user_id = message.from_user.id
        # Активируем подписку для пользователя через метод класса Database
        await db.activate_subscription(user_id)  # Обновленный вызов функции активации подписки

        # Отправляем пользователю сообщение об успешной активации подписки
        text = "🎉 Ваша подписка успешно активирована! Теперь вы имеете доступ ко всем урокам."
        image_path = 'https://botnest.ru/wp-content/uploads/2024/botnest/shop/photo/pay.png?_t=1707660307'
        sent_message = await bot.send_photo(
            message.chat.id,
            photo=image_path,  # Или просто строка с URL изображения
            caption=text,
            reply_markup=inline_builder(sub_key_after_buy)
        )
        await update_last_message_id(bot, sent_message.message_id, user_id)
    elif payload.startswith("phone"):
        telegram_id = message.from_user.id

        user_id = message.from_user.id

        # Шаг 1: Получаем товары из корзины пользователя
        cart_items = await db.get_checkout_items(user_id)
        if cart_items:
            # Шаг 2: Добавляем запись в PurchaseHistory
            total_amount = message.successful_payment.total_amount / 100  # Telegram возвращает сумму в копейках
            purchase_id = await db.add_purchase_history(user_id, total_amount, cart_items)

            # Шаг 3: Для каждого товара из корзины добавляем запись в PurchaseDetail
            for cart_item, product_name, stock_quantity, price, color in cart_items:
                await db.add_purchase_detail(purchase_id, cart_item.product_id, cart_item.quantity, price)

        await db.clear_user_cart(user_id)

        text = (
            f"<b>💬 Успешно!</b> \n\n"
            f"Вы успешно получили пробную оплату товара, при этом вы потратили {message.successful_payment.total_amount // 100} виртуальных {message.successful_payment.currency}.\n\n"
            f"Если хотите получить такой же бот, то можете подать заявку ниже."
        )
        image_path = 'https://botnest.ru/wp-content/uploads/2024/botnest/shop/photo/pay.png?_t=1707660307'
        sent_message = await bot.send_photo(
            message.chat.id,
            photo=image_path,  # Или просто строка с URL изображения
            caption=text,
            reply_markup=inline_builder(buy)
        )
        await update_last_message_id(bot, sent_message.message_id, telegram_id)
