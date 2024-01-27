import openai
import requests
from aiogram import Bot, Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
import logging

from core.database.models import *
from core.handlers.callback import *
from core.handlers.user_commands import start
from core.keyboards.reply import cancel
from core.projects.AI.callbacks.ai_assistant import create_chatgpt_prompt
from core.projects.AI.keyboards.builder import inline_builder, quit_ai, order

router = Router()


class AI_ASS(StatesGroup):
    waiting_for_ai_ass = State()


@router.callback_query(F.data == 'ai_ass')
async def ai_ass(query: CallbackQuery, state: FSMContext, bot: Bot):
    await state.set_state(AI_ASS.waiting_for_ai_ass)

    sent_message = await query.message.answer("Вы в режиме AI ассистента. Задайте свой вопрос или нажмите 'Отмена' для выхода.",
                                              reply_markup=inline_builder(quit_ai))

    await update_last_message_id(bot, sent_message.message_id, query.from_user.id)


@router.message(AI_ASS.waiting_for_ai_ass, F.text)
async def process_ai_question(message: Message, bot: Bot, state: FSMContext):
    try:
        user_input = message.text
        prompt = create_chatgpt_prompt(user_input)

        # Установка ограничений для размера ответа и температуры
        temperature = 0.4  # Пример для умеренной творческой свободы

        chat = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=prompt,
            temperature=temperature
        )

        answer = chat.choices[0].message.content

        # Проверка ответа и вызов callback-функции
        if "Для записи на услуги" in answer:
            sent_message = await message.answer("Хотите записаться на услугу?", reply_markup=inline_builder(order))
            await update_last_message_id(bot, sent_message.message_id, message.from_user.id)
        else:
            sent_message = await message.answer(answer)
            await update_last_message_id(bot, sent_message.message_id, message.from_user.id)
    except Exception as e:
        logging.error(e)


    # # Сначала проверяем, является ли сообщение командой "Отмена"
    # if message.text.lower() == "отмена":
    #     await state.clear()  # Очищаем состояние (выходим из FAQ)
    #     await start(message, bot, state)
    #     return  # Завершаем обработчик

