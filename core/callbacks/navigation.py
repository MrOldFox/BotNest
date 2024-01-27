import requests
from aiogram import Bot, Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
import logging

from core.handlers.callback import update_last_message
from core.handlers.user_commands import start
from core.keyboards.reply import cancel

router = Router()

from core.keyboards.builders import *
from core.utils.faq import detect_intent_texts


class FAQ(StatesGroup):
    waiting_for_question = State()


@router.callback_query(F.data == 'order')
async def order(query: CallbackQuery, state: FSMContext):
    sent_message = await query.message.answer(
        f'Чтобы заказать бота заполните небольшую анкету и '
        f'мы с вами свяжемся для обсуждения дальнейших шагов',
        reply_markup=inline_builder(order_menu)
    )

    await query.answer()
    await update_last_message(query.bot, state, query.message.chat.id, sent_message.message_id)


@router.callback_query(F.data == 'contacts')
async def contacts(query: CallbackQuery, state: FSMContext):

    site = "botnest.ru"
    email = "info@botnest.ru"
    tg = "ryzhkov_dv"

    sent_message = await query.message.answer(
        f'Вы можете связаться несколькими способами:\n\n'
        f'💻 {site}\n'
        f'📧 {email}\n',

        reply_markup=inline_builder(contact_menu)
    )

    await query.answer()
    await update_last_message(query.bot, state, query.message.chat.id, sent_message.message_id)

    # Вызов функции update_last_message с корректным chat_id


@router.callback_query(F.data == 'faq')
async def enter_faq(query: CallbackQuery, state: FSMContext):
    await state.set_state(FAQ.waiting_for_question)

    sent_message = await query.message.answer("Вы в режиме FAQ. Задайте свой вопрос или нажмите 'Отмена' для выхода.", reply_markup=cancel)

    await update_last_message(query.bot, state, query.message.chat.id, sent_message.message_id)


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
        response_text = "Извините, у меня пока нет ответа на этот вопрос."

    await message.answer(response_text)


# @router.message(F.text == 'Отмена', FAQ.waiting_for_question)
# async def cancel_faq(message: Message, state: FSMContext):
#     await state.clear()
#     await message.answer("Вы вышли из режима FAQ.")



# @router.callback_query(F.data == 'info_tel')
# async def info_tel(query: CallbackQuery, bot: Bot):
#     button = InlineKeyboardButton(text="Назад", callback_data="contacts_from_info_tel")
#     keyboard_back = InlineKeyboardMarkup(inline_keyboard=[[button]])
#
#     await query.message.delete()
#     await query.answer()
#     phone_number = "+79044951833"  # Пример телефонного номера
#     first_name = "Дмитрий"  # Имя, которое будет отображаться
#     await bot.send_contact(chat_id=query.from_user.id, phone_number=phone_number, first_name=first_name,
#                            reply_markup=keyboard_back)

