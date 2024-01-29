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

    # Отправка изображения с подписью и инлайн-клавиатурой
    sent_message = await bot.send_photo(
        chat_id,
        photo=image_path,  # Или просто строка с URL изображения
        caption='Добро пожаловать в BotNest',
        reply_markup=main_menu_markup
    )

    # Вызов функции update_last_message_id
    await update_last_message_id(bot, sent_message.message_id, telegram_id)

# @router.message(CommandStart())
# @router.callback_query(F.data == 'main_menu')
# async def start(message: Union[Message, CallbackQuery], bot: Bot, state: FSMContext):
#     global last_message_id
#
#     # Определение chat_id
#     chat_id = message.message.chat.id if isinstance(message, CallbackQuery) else message.chat.id
#
#     # Удаление предыдущего сообщения, если оно существует
#     if last_message_id:
#         try:
#             await bot.delete_message(chat_id, last_message_id)
#         except Exception as e:
#             print(f"Ошибка при удалении сообщения: {e}")
#
#     # Очистка состояния
#     await state.clear()
#
#     # Создание и отправка главного меню
#     main_menu_text = 'Добро пожаловать в BotNest'
#     main_menu_markup = inline_builder(main_menu)  # Предполагается, что это функция создает ваше меню
#
#     # Отправка сообщения и обновление last_message_id
#     sent_message = await bot.send_message(chat_id, main_menu_text, reply_markup=main_menu_markup)
#     last_message_id = sent_message.message_id


# @router.message(F.text == "Отмена")
# async def cancel_faq(message: Message, state: FSMContext):
#     await state.clear()
#     await message.answer('Отмена')