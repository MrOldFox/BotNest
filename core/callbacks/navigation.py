import requests
from aiogram import Bot, Router, F, types
from aiogram.filters import Command

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, WebAppInfo
import logging


from aiohttp import web

from core.database.models import *
from core.handlers.callback import *
from core.handlers.user_commands import start
from core.keyboards.reply import cancel

router = Router()

from core.keyboards.builders import *
from core.utils.faq import detect_intent_texts


class FAQ(StatesGroup):
    waiting_for_question = State()


@router.callback_query(F.data == 'order')
async def order(query: CallbackQuery, bot: Bot):
    # markup = types.InlineKeyboardMarkup()
    # markup.add(types.InlineKeyboardButton(text='Заполнить заявку', web_app=WebAppInfo(url='https://botnest.ru/wp-content/uploads/2024/botnest/order.html')))
    sent_message = await query.message.answer(
        f'Чтобы заказать бота заполните небольшую анкету и '
        f'мы с вами свяжемся для обсуждения дальнейших шагов',
        reply_markup=inline_builder(order_menu)
    )

    await query.answer()
    await update_last_message_id(bot, sent_message.message_id, query.from_user.id)


@router.callback_query(F.data == 'bot_examples')
async def bot_examples(query: CallbackQuery, bot: Bot):
    sent_message = await query.message.answer(
        f'Вы можете ознакомиться с примером наших ботов'
        f', чтобы лучше определить, какой типа вам больше подойдет',
        reply_markup=inline_builder(examples_type)
    )

    await query.answer()
    await update_last_message_id(bot, sent_message.message_id, query.from_user.id)


@router.callback_query(F.data == 'game_examples')
async def game_examples(query: CallbackQuery, bot: Bot):
    sent_message = await query.message.answer(
        f'Вы можете ознакомиться с примером наших ботов'
        f', чтобы лучше определить, какой типа вам больше подойдет',
        reply_markup=inline_builder(games_type)
    )

    await query.answer()
    await update_last_message_id(bot, sent_message.message_id, query.from_user.id)



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
    tg = "ryzhkov_dv"

    sent_message = await query.message.answer(
        f'Вы можете связаться несколькими способами:\n\n'
        f'💻 {site}\n'
        f'📧 {email}\n',

        reply_markup=inline_builder(contact_menu)
    )

    await query.answer()
    await update_last_message_id(bot, sent_message.message_id, query.from_user.id)


@router.callback_query(F.data == 'faq')
async def enter_faq(query: CallbackQuery, state: FSMContext, bot: Bot):
    await state.set_state(FAQ.waiting_for_question)

    sent_message = await query.message.answer("Вы в режиме FAQ. Задайте свой вопрос или нажмите 'Отмена' для выхода.",
                                              reply_markup=inline_builder(cancel_faq))

    await update_last_message_id(bot, sent_message.message_id, query.from_user.id)


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

    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    sent_message = await message.answer(response_text, reply_markup=inline_builder(cancel_faq))
    await update_last_message_id(bot, sent_message.message_id, message.from_user.id)

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

