import asyncio
import logging
from aiogram import Bot, Dispatcher, types, Router, F

import openai

from aiogram.types import Message
from aiogram.enums import ParseMode

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from core.projects.AI.keyboards.builder import inline_builder, order

# Логирование
logging.basicConfig(level=logging.INFO)

router = Router()

openai.api_key = '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'

messages = []


def create_chatgpt_prompt(user_input):
    system_messages = [{
        "role": "system",
        "content": (
            "Ты - бот-администратор салона красоты Beauty. Твоя задача - помогать клиентам с информацией об услугах "
            "отвечать на вопросы, помогать с регистрацией на запись и предоставлять рекомендации. "
            "Ты обладаешь доступом ко всей необходимой информации об услугах салона Beauty услуг."
            "Если у тебя спрашивают про запись на услуги или про запись в салон, требуется в обязательном (ВАЖНО!) порядке вывести следущее сообщение: запись на услугу"
        )
    }, {
        "role": "user",
        "content": (
            "Как записаться на услуги?"
        )
    }, {
        "role": "assistant",
        "content": (
            "Для записи на услуги в нашем салоне Beauty, тебе необходимо связаться с нашим администратором по телефону или через нашу онлайн-форму записи на сайте."
        )
    }, {
        "role": "system",
        "content": (
            "Отвечай кратко, при этом близко к заданым данным."
            "Отвечай только на вопросы связн не с салоном и его услугами, не отвечай на другие вопрсооы которые никак не относятся к работе салона. услугам и все связаного с ними"
        )
    }, {
        "role": "system",
        "content": (
            "Связаться можно с нами несколькми способами: звонок по номеру +79997775533, либо через данного бота."
            " Услуги которые оказывает салон: маникюр, педикюр, наращивание ресниц оформление бровей, срижка волос, макияж, укладка волос."
        )
    }, {
        "role": "system",
        "content": (
            "Салон регулярно проводит специальные акции и предложения. Например, скидки на определенные услуги "
            "или бонусы для постоянных клиентов. Следите за обновлениями, чтобы не пропустить выгодные предложения!"
        )
    }, {
        "role": "system",
        "content": (
            "В нашем салоне работают высококвалифицированные специалисты. Каждый мастер имеет свою специализацию, "
            "будь то стилист по волосам, мастер маникюра или визажист. Вы можете узнать подробнее о каждом мастере, "
            "их опыте и портфолио."
        )
    }, {
        "role": "system",
        "content": (
            "Чтобы ваш визит в салон был максимально комфортным и эффективным, рекомендуем соблюдать некоторые "
            "простые правила подготовки. Например, перед процедурами по уходу за лицом желательно не наносить макияж."
        )
    }, {"role": "user", "content": user_input}]

    # Добавление сообщения пользователя

    return system_messages


# @router.message(.waiting_for_question, F.text)
# async def start_chat_gpt(message: types.Message):
#     try:
#         user_input = message.text
#         prompt = create_chatgpt_prompt(user_input)
#
#         # Установка ограничений для размера ответа и температуры
#         temperature = 0.4  # Пример для умеренной творческой свободы
#
#         chat = openai.chat.completions.create(
#             model='gpt-3.5-turbo',
#             messages=prompt,
#             temperature=temperature
#         )
#
#         answer = chat.choices[0].message.content
#
#         # Проверка ответа и вызов callback-функции
#         if "Для записи на услуги" in answer:
#             await message.answer("Хотите записаться на услугу?", reply_markup=inline_builder(order))
#         else:
#             await message.answer(answer)
#
#     except Exception as e:
#         logging.error(e)