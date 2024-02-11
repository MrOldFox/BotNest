import asyncio
import json

from aiogram.fsm.state import StatesGroup, State

import logging

from core.database.models import OrderRequest, UserRole
from core.handlers.user_commands import *
from core.keyboards.reply import *

router = Router()

from core.keyboards.builders import *
from core.utils.faq import detect_intent_texts


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
        f"После отправки анкеты наш специалист свяжется с вами для обсуждения деталей проекта "
        f"и определения следующих шагов.\n\n"

        f"Нажмите <b>'Заполнить анкету'</b>, чтобы перейти к анкете, или <b>'Отмена'</b>, если вы хотите вернуться в предыдущее меню."
    )
    image_path = 'https://botnest.ru/wp-content/uploads/2024/botnest/images/order.png'

    chat_id = message.message.chat.id if isinstance(message, CallbackQuery) else message.chat.id

    # Отправка изображения с подписью и инлайн-клавиатурой
    sent_message = await bot.send_photo(
        chat_id,
        photo=image_path,  # Или просто строка с URL изображения
        caption=text,
        reply_markup=order_keyboard
    )

    # Вызов функции update_last_message_id
    await update_last_message_id(bot, sent_message.message_id, chat_id)


@router.message(F.web_app_data)
async def web_order(message: Message, bot: Bot, state: FSMContext):
    res = json.loads(message.web_app_data.data)
    sent_message = await message.answer(f'Спасибо {res["name"]}, мы свяжемся с вами в ближайшее время! 🤗\n\n'
                                        f'<i>Возвращаемся в главное меню...</i>')
    await update_last_message_id(bot, sent_message.message_id, message.from_user.id)
    await asyncio.sleep(5)
    await start(message, bot, state)

    # Создайте сессию с вашей базой данных
    async with async_session() as session:
        # Выполнение запроса
        result = await session.execute(select(User).where(User.telegram_id == message.from_user.id))

        # Получение первого результата (если он есть)
        user = result.scalar()
        if user:
            # Пользователь найден, создаем запись в order_requests с user.id
            order_request = OrderRequest(
                user_id=user.id,
                phone=res["phone"],
                email=res["email"],
                description=res["description"],
                contact_via_telegram=res["contactViaTelegram"]
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
                f"Связь через Telegram: {contact_request}"
            )

            await notify_admins_and_mods(bot, session, admin_message)

        else:
            await message.answer(f'Нажмите /start для регистрации')


async def notify_admins_and_mods(bot, session, message, include_moderators=True):
    # Определяем роли, которым нужно отправить сообщение
    roles_to_notify = [UserRole.admin]
    if include_moderators:
        roles_to_notify.append(UserRole.moderator)

    # Получение списка администраторов и, при необходимости, модераторов
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
        f"<b>🤖 Примеры чат-ботов</b>\n\n"
        f"В BotNest мы разрабатываем чат-боты, ориентированные на различные потребности и цели наших клиентов. "
        f"Исследуя наши примеры, вы сможете лучше понять, какой тип бота подойдет именно вам.\n\n"
        f"<b>Выбирайте, исследуйте и вдохновляйтесь</b> – вместе мы сможем создать идеального "
        f"цифрового помощника для вашего бизнеса или личных нужд!"
    )
    image_path = 'https://botnest.ru/wp-content/uploads/2024/botnest/images/info.png?v=2'

    await query_message_photo(query, bot, text, image_path, info_type)



@router.callback_query(F.data == 'ai_examples')
async def ai_examples(query: CallbackQuery, bot: Bot):
    text = (
        f"<b>🤖 Примеры AI чат-ботов</b>\n\n"
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
        f"<b>🤖 Примеры чат-ботов</b>\n\n"
        f"В BotNest мы разрабатываем чат-боты, ориентированные на различные потребности и цели наших клиентов. "
        f"Исследуя наши примеры, вы сможете лучше понять, какой тип бота подойдет именно вам.\n\n"
        f"<b>Выбирайте, исследуйте и вдохновляйтесь</b> – вместе мы сможем создать идеального "
        f"цифрового помощника для вашего бизнеса или личных нужд!"
    )
    image_path = 'https://botnest.ru/wp-content/uploads/2024/botnest/images/gaming.png'

    await query_message_photo(query, bot, text, image_path, games_type)


@router.callback_query(F.data == 'business_examples')
async def business_examples(query: CallbackQuery, bot: Bot):
    text = (
        f"<b>🤖 Примеры чат-ботов</b>\n\n"
        f"В BotNest мы разрабатываем чат-боты, ориентированные на различные потребности и цели наших клиентов. "
        f"Исследуя наши примеры, вы сможете лучше понять, какой тип бота подойдет именно вам.\n\n"
        f"<b>Выбирайте, исследуйте и вдохновляйтесь</b> – вместе мы сможем создать идеального "
        f"цифрового помощника для вашего бизнеса или личных нужд!"
    )
    image_path = 'https://botnest.ru/wp-content/uploads/2024/botnest/images/busines.png?v=2'

    await query_message_photo(query, bot, text, image_path, business_type)


@router.callback_query(F.data == 'service_examples')
async def service_examples(query: CallbackQuery, bot: Bot):
    text = (
        f"<b>🤖 Примеры чат-ботов</b>\n\n"
        f"В BotNest мы разрабатываем чат-боты, ориентированные на различные потребности и цели наших клиентов. "
        f"Исследуя наши примеры, вы сможете лучше понять, какой тип бота подойдет именно вам.\n\n"
        f"<b>Выбирайте, исследуйте и вдохновляйтесь</b> – вместе мы сможем создать идеального "
        f"цифрового помощника для вашего бизнеса или личных нужд!"
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
        "<i>Данная игра создана для будущей реализации в рамках расширения проектов BotNest\n\n"
        "Даная игра хорошо демонстрирует возможности создания сетевых игр в Telegram: "
        "в ней есть система рейтинга, система внутриигровой валюты и игрового магазина.\n\n"
        "Вы можете заказать разработку сетевой игры по своим требованиям и желаниям.</i>"
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
    # Сначала проверяем, является ли сообщение командой "Отмена"
    if message.text.lower() == "отмена":
        await state.clear()  # Очищаем состояние (выходим из FAQ)
        await message.answer("Вы вышли из режима FAQ.", reply_markup=ReplyKeyboardRemove())
        await start(message, bot, state)
        return  # Завершаем обработчик

    # Обрабатываем вопрос в Dialogflow, если это не команда "Отмена"
    response_text = detect_intent_texts(message.text)
    if not response_text:
        # Если ответ пустой или None, отправляем сообщение-заглушку
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


async def query_message_animation(query: CallbackQuery, bot: Bot, text: str, image_path: str, inline_builder_key):
    sent_message = await query.bot.send_animation(
        query.message.chat.id,
        animation=image_path,
        caption=text,
        reply_markup=inline_builder(inline_builder_key)
    )
    await update_last_message_id(bot, sent_message.message_id, query.from_user.id)
    await query.answer()


async def query_message(query: CallbackQuery, bot: Bot, text: str, inline_builder_key):
    sent_message = await query.message.answer(text, reply_markup=inline_builder(inline_builder_key))

    await update_last_message_id(bot, sent_message.message_id, query.from_user.id)
    await query.answer()
