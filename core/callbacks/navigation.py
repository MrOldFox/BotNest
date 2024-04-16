import asyncio
import json
from datetime import datetime

from aiogram.fsm.state import StatesGroup, State

import logging

from core.database.models import OrderRequest, UserRole, ServiceRequestStatus
from core.database.requests import Database
from core.handlers.user_commands import *
from core.keyboards.reply import *
from core.projects.business.shops.keyboards.builders import buy
from core.projects.business.subscribe_bot.keyboards.builders import sub_key_after_buy

router = Router()

from core.keyboards.builders import *
from core.utils.faq import detect_intent_texts

db = Database()

class FAQ(StatesGroup):
    waiting_for_question = State()


@router.message(or_f(Command('order'), F.text.lower == "Заказ", F.text.lower == "заказать"))
@router.callback_query(F.data == 'order')
async def order(message: Union[Message, CallbackQuery], bot: Bot):
    text = (
        f"<b>📱 Заказ разработки бота</b> \n\n"
        f"Для начала сотрудничества предлагаем заполнить краткую анкету. "
        f"Это поможет нам лучше понять ваши потребности и подготовить предложение, максимально соответствующее вашим "
        f"ожиданиям.\n\n"
        f"После отправки анкеты мы свяжемся с вами для обсуждения деталей проекта "
        f"и определения следующих шагов. Либо вы можете <a href='https://t.me/ryzkov_dv'>написать нам в телеграм</a> и напрямую обсудить детали проекта.\n\n"
        f"Нажмите <b>'Заполнить анкету'</b>, чтобы перейти к анкете, или <b>'Отмена'</b>, "
        f"если вы хотите вернуться в предыдущее меню.")

    image_path = 'https://botnest.ru/wp-content/uploads/2024/botnest/images/order.png'

    chat_id = message.message.chat.id if isinstance(message, CallbackQuery) else message.chat.id

    # Отправка изображения с подписью и инлайн-клавиатурой
    sent_message = await bot.send_photo(
        chat_id,
        photo=image_path,  # Или просто строка с URL изображения
        caption=text,
        reply_markup=order_keyboard,
        parse_mode='HTML'
    )

    # Вызов функции update_last_message_id
    await update_last_message_id(bot, sent_message.message_id, chat_id)



@router.message(F.successful_payment)
async def handle_successful_payment(message: Message, bot: Bot):
    payload = message.successful_payment.invoice_payload
    if payload.startswith("sub"):
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


@router.message(F.web_app_data)
async def web_order(message: Message, bot: Bot, state: FSMContext):
    res = json.loads(message.web_app_data.data)
    sent_message = await message.answer(
        f"Спасибо {res['name']}, мы свяжемся с вами в ближайшее время! 🤗\n\n"
        "<i>Возвращаемся в главное меню...</i>"
    )
    await update_last_message_id(bot, sent_message.message_id, message.from_user.id)
    await asyncio.sleep(5)
    await start(message, bot, state)

    # Создание сессии и обработка данных
    async with async_session() as session:
        # Получение пользователя по Telegram ID
        result = await session.execute(select(User).where(User.telegram_id == message.from_user.id))
        user = result.scalar()

        if user:
            # Создание новой заявки
            order_request = OrderRequest(
                user_id=user.id,
                phone=res["phone"],
                email=res["email"],
                description=res["description"],
                contact_via_telegram=res["contactViaTelegram"],
                request_date=datetime.utcnow(),  # Текущее время и дата
                details=None,  # Пример заполнения, может быть изменено
                responsible_id=None,  # Ответственное лицо, может быть задано позже
                status=ServiceRequestStatus.pending  # Начальный статус заявки
            )
            session.add(order_request)
            await session.commit()

            # Подготовка сообщения для администраторов и модераторов
            contact_request = "Да" if res["contactViaTelegram"] else "Нет"
            admin_message = (
                f"Новая заявка от {res['name']}:\n"
                f"Телефон: {res['phone']}\n"
                f"Email: {res['email']}\n"
                f"Описание: {res['description']}\n"
                f"Связь через Telegram: {contact_request}\n"
                f"Дата запроса: {order_request.request_date.strftime('%Y-%m-%d %H:%M')}"
            )

            # Функция notify_admins_and_mods должна быть реализована для уведомления администраторов
            await notify_admins_and_mods(bot, session, admin_message)
        else:
            await message.answer("Нажмите /start для регистрации.")


async def notify_admins_and_mods(bot, session, message, include_moderators=True):
    roles_to_notify = [UserRole.admin]
    if include_moderators:
        roles_to_notify.append(UserRole.moderator)

    # Получение списка администраторов и, при необходимости, модераторах
    admins_and_mods = await session.execute(select(User).where(User.role.in_(roles_to_notify)))
    admins_and_mods = admins_and_mods.scalars().all()

    # Отправка сообщений администраторам и модераторам
    for admin_or_mod in admins_and_mods:
        try:
            await bot.send_message(admin_or_mod.telegram_id, message, parse_mode='HTML')
        except Exception as e:
            print(f"Не удалось отправить сообщение пользователю {admin_or_mod.telegram_id}: {e}")





@router.callback_query(F.data == 'bot_examples')
async def bot_examples(query: CallbackQuery, bot: Bot):

    text = (
        f"<b>🤖 Примеры чат-ботов</b>\n\n"
        f"В BotNest мы разрабатываем чат-боты, ориентированные на различные потребности и цели наших клиентов. "
        f"Исследуя наши примеры, вы сможете лучше понять, какой тип бота подойдет именно вам.\n\n"
        f"<b>Выбирайте, исследуйте и вдохновляйтесь</b> – вместе мы сможем создать идеального "
        f"цифрового помощника для вашего бизнеса или личных нужд!"
    )
    image_path = 'https://botnest.ru/wp-content/uploads/2024/botnest/images/examples.png'

    await query_message_photo(query, bot, text, image_path, examples_type)



@router.callback_query(F.data == 'info_examples')
async def info_examples(query: CallbackQuery, bot: Bot):
    text = (
        f"<b>📢 Примеры информационных ботов</b>\n\n"
        f"В разделе Информационные боты вы найдете примеры чат-ботов Telegram, предназначенных для оперативного "
        f"предоставления актуальной информации и данных.\n\n"
        f"Эти боты станут незаменимыми помощниками в получении свежих новостей, "
        f"котировок акций, курсов валют и многого другого прямо в Telegram."
    )
    image_path = 'https://botnest.ru/wp-content/uploads/2024/botnest/images/info.png?v=2'

    await query_message_photo(query, bot, text, image_path, info_type)



@router.callback_query(F.data == 'ai_examples')
async def ai_examples(query: CallbackQuery, bot: Bot):
    text = (
        f"<b>🤖 Примеры ai чат-ботов</b>\n\n"
        f"Вдохновитесь возможностями искусственного интеллекта с нашими ИИ чат-ботами! Мы поможем вам создать "
        f"разработке на заказ умных помощников, которые могут трансформировать взаимодействие с вашими клиентами, "
        f"улучшить аналитику и оптимизировать рабочие процессы.\n\n"
        f"Выберите будущее уже сегодня – исследуйте наши примеры чат-ботов на искусственном интеллекте и "
        f"найдите идеальное решение, которое поможет вам достичь новых высот в вашем деле."

    )
    image_path = 'https://botnest.ru/wp-content/uploads/2024/botnest/images/AI.png'

    await query_message_photo(query, bot, text, image_path, ai_type)


@router.callback_query(F.data == 'game_examples')
async def game_examples(query: CallbackQuery, bot: Bot):
    text = (
        f"<b>🎮 Примеры игровых чат-ботов</b>\n\n"
        f"В данном разделе вы найдете увлекательные примеры игровых чат-ботов для Telegram, "
        f"которые могут стать отличным дополнением к вашему бизнесу или просто развлечением для сообщества.\n\n"
        f"От ролевых игр с выборами, где каждое ваше решение влияет на ход сюжета,"
        f" до сетевых игр, где вы можете соревноваться с друзьями "
        f"или случайными соперниками в режиме реального времени — "
        f"наши решения позволят вам воплотить любую игровую концепцию. "
    )
    image_path = 'https://botnest.ru/wp-content/uploads/2024/botnest/images/gaming.png'

    await query_message_photo(query, bot, text, image_path, games_type)


@router.callback_query(F.data == 'business_examples')
async def business_examples(query: CallbackQuery, bot: Bot):
    text = (
        f"<b>🏢 Примеры чат-ботов для бизнеса</b>\n\n"
        f"В поисках идей для своего бизнеса? Ознакомьтесь с нашими примерами чат-ботов, "
        f"разработанных специально для улучшения взаимодействия с клиентами и автоматизации "
        f"процессов продажи услуг и товаров.\n\n"
        f"Чат-боты для бизнеса могут стать вашими надежными помощниками в обслуживании клиентов, "
        f"увеличении продаж и оптимизации рабочих процессов."
    )
    image_path = 'https://botnest.ru/wp-content/uploads/2024/botnest/images/busines.png?v=2'

    await query_message_photo(query, bot, text, image_path, business_type)


@router.callback_query(F.data == 'service_examples')
async def service_examples(query: CallbackQuery, bot: Bot):
    text = (
        f"<b>🛠 Примеры сервисных ботов</b>\n\n"
        f"В разделе универсальные чат-боты Telegram, созданные для упрощения повседневных "
        f"задач и автоматизации рутинных процедур.\n\nЭти боты предлагают практические инструменты для различных "
        f"сценариев использования, помогая сэкономить ваше время и усилить продуктивность."
    )
    image_path = 'https://botnest.ru/wp-content/uploads/2024/botnest/images/service.png?v=2'

    await query_message_photo(query, bot, text, image_path, service_type)


@router.callback_query(F.data == 'fin_trigger')
async def fin_trigger(query: CallbackQuery, bot: Bot):
    text = (
        "<b>Сетевая игра - Final Trigger</b> \n\n"
        "Испытай свою удачу в напряженной игре русской рулетки с уникальным игровым ботом - Final Trigger! Сразитесь с "
        "соперником, у кого из вас больше смелости и удачи.\n\n"
        "Ваша задача - выжить в серии раундов, где смертельная угроза скрыта в каждом выстреле. Используйте стратегию и"
        " интуицию, чтобы выбирать между риском для себя или атакой противника. Каждый раунд - новый набор патронов, "
        "каждый ход - важное решение. Победитель - тот, кто останется в живых.\n\n"
        "<i>Даная игра хорошо демонстрирует возможности создания сетевых игр в Telegram: "
        "в ней есть система рейтинга, система внутриигровой валюты и игрового магазина.</i>\n\n"
    )

    # Путь к изображению или URL
    image_path = 'https://botnest.ru/wp-content/uploads/2024/game/finaltrigger/Final_Trigger.png'

    # Отправка изображения с подписью и инлайн-клавиатурой
    sent_message = await query.bot.send_photo(
        query.message.chat.id,
        photo=image_path,  # Или просто строка с URL изображения
        caption=text,
        reply_markup=inline_builder(final_trigger)
    )

    # Вызов функции update_last_message
    await update_last_message_id(bot, sent_message.message_id, query.from_user.id)


@router.callback_query(F.data == 'contacts')
async def contacts(query: CallbackQuery, bot: Bot):
    site = "botnest.ru"
    email = "info@botnest.ru"

    text = (
        f"<b>🤝 Наши контакты</b> \n\n"
        f"Мы всегда рады общению и готовы ответить на любые ваши вопросы. Вы можете связаться с нами следующими способами:\n\n"
        f"<b>На нашем сайте:</b> {site} – здесь вы найдете много полезной информации, а также форму обратной связи.\n"
        f"<b>По электронной почте:</b> {email} – пишите нам, и мы обязательно ответим.\n\n"
        f"Независимо от того, есть у вас вопросы по работе существующего бота, или вы хотите обсудить создание нового проекта, мы всегда к вашим услугам."
    )
    image_path = 'https://botnest.ru/wp-content/uploads/2024/botnest/images/contacts.png'

    await query_message_photo(query, bot, text, image_path, contact_menu)


@router.callback_query(F.data == 'faq')
async def enter_faq(query: CallbackQuery, state: FSMContext, bot: Bot):
    await state.set_state(FAQ.waiting_for_question)

    text = (
        f"<b>💬 Часто задаваемые вопросы (FAQ)</b> \n\n"
        f"Здесь вы можете задать любые вопросы, касающиеся работы нашей компании, и получить на них быстрый ответ. "
        f"Этот раздел работает автоматически, без участия оператора, что позволяет вам получить необходимую информацию максимально оперативно.\n\n"
        f"Напишите свой вопрос и когда получите все необходимые ответы - нажмите 'Отмена', чтобы выйти из режима <b>FAQ</b>."
    )
    image_path = 'https://botnest.ru/wp-content/uploads/2024/botnest/images/faq.png'

    await query_message_photo(query, bot, text, image_path, cancel_faq)


@router.message(FAQ.waiting_for_question, F.text)
async def process_question(message: Message, bot: Bot, state: FSMContext):
    if message.text.lower() == "отмена":
        await state.clear()  # Очищаем состояние (выходим из FAQ)
        await message.answer("Вы вышли из режима FAQ.", reply_markup=ReplyKeyboardRemove())
        await start(message, bot, state)
        return  # Завершаем

    # Обрабатываем вопрос в Dialogflow
    response_text = detect_intent_texts(message.text)
    if not response_text:
        # Если ответ пустой или None
        response_text = "Извините, у меня пока нет ответа на этот вопрос, но в будущем я его найду 😉"

    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    sent_message = await message.answer(response_text, reply_markup=inline_builder(cancel_faq))
    await update_last_message_id(bot, sent_message.message_id, message.from_user.id)


async def query_message_photo(query: CallbackQuery, bot: Bot, text: str, image_path: str, inline_builder_key,
                              is_inline=True):
    if is_inline:
        # Если клавиатура инлайн, обрабатываем её через builder или передаём напрямую
        reply_markup = inline_builder(inline_builder_key)
    else:
        # Если клавиатура обычная, то предполагаем, что она уже создана и передана напрямую
        reply_markup = inline_builder_key

    sent_message = await query.bot.send_photo(
        query.message.chat.id,
        photo=image_path,
        caption=text,
        reply_markup=reply_markup
    )
    await update_last_message_id(bot, sent_message.message_id, query.from_user.id)
    await query.answer()


async def query_message_video(query: CallbackQuery, bot: Bot, text: str, video_path: str, inline_builder_key,
                              is_inline=True):
    if is_inline:
        # Если клавиатура инлайн, обрабатываем её через builder или передаём напрямую
        reply_markup = inline_builder(inline_builder_key)
    else:
        # Если клавиатура обычная, то предполагаем, что она уже создана и передана напрямую
        reply_markup = inline_builder_key

    sent_message = await query.bot.send_video(
        query.message.chat.id,
        video=video_path,
        caption=text,
        reply_markup=reply_markup
    )
    await update_last_message_id(bot, sent_message.message_id, query.from_user.id)
    await query.answer()


async def query_message_animation(query: CallbackQuery, bot: Bot, text: str, image_path: str, inline_builder_key):
    sent_message = await query.bot.send_animation(
        query.message.chat.id,
        animation=image_path,
        caption=text,
        reply_markup=inline_builder(inline_builder_key)
    )
    await update_last_message_id(bot, sent_message.message_id, query.from_user.id)
    await query.answer()



async def query_message(query: CallbackQuery, bot: Bot, text: str, inline_builder_key, is_inline=True):

    if is_inline:
        # Если клавиатура инлайн, обрабатываем её через builder или передаём напрямую
        reply_markup = inline_builder(inline_builder_key)
    else:
        # Если клавиатура обычная, то предполагаем, что она уже создана и передана напрямую
        reply_markup = inline_builder_key

    sent_message = await query.message.answer(text, reply_markup=reply_markup)

    await update_last_message_id(bot, sent_message.message_id, query.from_user.id)
    await query.answer()
