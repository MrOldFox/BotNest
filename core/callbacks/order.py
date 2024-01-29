import requests
from aiogram import Bot, Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_session

from core.database.models import async_session, User, OrderRequest
from core.handlers.callback import *
from core.handlers.user_commands import start
from core.keyboards.builders import cancel_order, inline_builder

router = Router()


class Order(StatesGroup):
    awaiting_phone = State()
    awaiting_description = State()
    awaiting_deadline = State()


@router.callback_query(F.data == 'make_order')
async def start_survey(query: CallbackQuery, state: FSMContext):
    sent_message = await query.message.answer("Пожалуйста, поделитесь своим контактом или введите номер телефона:",
                         reply_markup=inline_builder(cancel_order))
    await query.answer()
    # Вызов функции update_last_message
    await update_last_message(query.bot, state, query.message.chat.id, sent_message.message_id)

    await state.set_state(Order.awaiting_phone)


@router.message(Order.awaiting_phone, F.text)
async def process_phone(message: Message, state: FSMContext):
    print('1')
    phone = message.contact.phone_number if message.contact else message.text

    # Переход к следующему вопросу анкеты
    await state.update_data(phone=phone)
    await message.answer("Опишите кратко, что должен делать бот:",
                         reply_markup=inline_builder(cancel_order))
    await state.set_state(Order.awaiting_description)


@router.message(Order.awaiting_description, F.text)
async def process_description(message: Message, state: FSMContext):
    # Получение описания от пользователя
    description = message.text
    await state.update_data(description=description)

    # Переход к следующему вопросу или завершение анкеты
    await message.answer("Какие у вас требования к срокам реализации бота?",
                         reply_markup=inline_builder(cancel_order))
    await state.set_state(Order.awaiting_deadline)


@router.message(Order.awaiting_deadline, F.text)
async def process_deadline(message: Message, state: FSMContext):
    data = await state.get_data()
    new_phone = data.get("phone")
    description = data.get("description")
    deadline = message.text
    telegram_id = message.from_user.id

    async with async_session() as session:
        # Ищем пользователя в базе данных по telegram_id
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalar()

        # Добавление нового номера телефона к существующим
        existing_phones = user.phone.split(',') if user.phone else []
        if new_phone not in existing_phones:
            existing_phones.append(new_phone)
            user.phone = ','.join(existing_phones)

        # Создание нового запроса на заказ бота
        bot_request = OrderRequest(user_id=user.id, phone=new_phone, description=description, deadline=deadline)
        session.add(bot_request)

        # Фиксация изменений в базе данных
        await session.commit()
        await message.answer("Спасибо за заполнение анкеты!")

    await state.clear()


@router.callback_query(F.data == 'cancel_order')
async def cancel_survey(query: CallbackQuery, state: FSMContext):
    await query.message.answer("Анкета отменена.")
    await query.answer()
    await state.clear()
    await start(query, query.bot, state)