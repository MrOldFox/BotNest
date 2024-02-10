import logging
import os
import random

from aiogram.types import InputFile
from aiogram import Router, Bot, F, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import Command, CommandObject, CommandStart, state, or_f
from sqlalchemy import select

from core.handlers.callback import *
from core.keyboards.builders import *
from core.keyboards.inline import *
from core.database.models import async_session, User


router = Router()


@router.message(or_f(CommandStart(), F.text == "Старт", F.text == "Отмена"))
@router.callback_query(F.data == 'main_menu')
async def start(message: Union[Message, CallbackQuery], bot: Bot, state: FSMContext):
    telegram_id = message.from_user.id
    if state:
        await state.clear()

    if not isinstance(message, CallbackQuery) and message.text == "Отмена":
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

    async with async_session() as session:
        # Проверяем, есть ли уже такой пользователь
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalar()

        if not user:
            # Пользователь не найден, добавляем его в базу данных
            new_user = User(telegram_id=telegram_id)
            session.add(new_user)
            await session.commit()

    chat_id = message.message.chat.id if isinstance(message, CallbackQuery) else message.chat.id

    # Создание инлайн-клавиатуры для главного меню
    main_menu_markup = inline_builder(main_menu)  # Предполагается, что это функция создает ваше меню

    # Путь к изображению или URL
    image_path = 'https://botnest.ru/wp-content/uploads/2024/01/logot.png'  # Замените на путь к вашему изображению

    text = (
        f"<b>🚀 Добро пожаловать в BotNest!</b> \n\n"
        f"Мы создаем телеграм-боты под ключ: реализуем ваши идеи и помогаем автоматизировать бизнес-процессы.\n\n"
        f"▪ <b>Заказать бота</b> – начнем проект вашей мечты!\n\n"
        f"▪ <b>Портфолио</b> – вдохновитесь примерами различных ботов\n\n"
        f"▪ <b>Контакты</b> – свяжитесь с нами для любых вопросов\n\n"
        f"▪ <b>FAQ</b> – ответы на частые вопросы здесь!\n\n"
        f"Выберите раздел и давайте воплотим идею в жизнь вместе!"
    )

    # Отправка изображения с подписью и инлайн-клавиатурой
    sent_message = await bot.send_photo(
        chat_id,
        photo=image_path,  # Или просто строка с URL изображения
        caption=text,
        reply_markup=main_menu_markup
    )

    # Вызов функции update_last_message_id
    await update_last_message_id(bot, sent_message.message_id, telegram_id)
