import types

from aiogram import Router, Bot, F, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import Command, CommandObject, CommandStart, state

from core.keyboards.builders import *
from core.keyboards.inline import *


async def update_last_message(bot, state: FSMContext, chat_id, new_message_id):
    data = await state.get_data()
    last_message_id = data.get("last_message_id")
    if last_message_id:
        try:
            await bot.delete_message(chat_id, last_message_id)
            print(f"Удалено сообщение: last_message_id: {last_message_id}, chat_id: {chat_id}")
        except Exception as e:
            print(f"Ошибка при удалении сообщения: {e}, last_message_id: {last_message_id}, chat_id: {chat_id}")

    await state.update_data(last_message_id=new_message_id)
    print(f"last_message_id обновлено: {new_message_id}")



# async def email_handler(call: CallbackQuery, bot: Bot):
#     if call.data == 'send_email':
#         await call.answer()
#         await call.message.answer("Наш email: info@botnest.ru")
#         # await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)



# async def tg_contact(call: callback_query, bot: Bot):
#     if call.data == 'tg_contact':
#         user_id = 123456789  # Замените на реальный Telegram ID пользователя
#         await call.message.answer("Нажмите на кнопку ниже, чтобы написать пользователю:")
#         await call.answer()
#
#         # await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)


# async def tel_handler(call: callback_query, bot: Bot):
#     if call.data == 'send_tel':
#         await call.answer()
#         phone_number = "+79044951833"  # Пример телефонного номера
#         first_name = "Дмитрий"  # Имя, которое будет отображаться
#         await bot.send_contact(chat_id=call.from_user.id, phone_number=phone_number, first_name=first_name, reply_markup=contact_back_menu)