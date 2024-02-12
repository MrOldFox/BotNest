import openai
import requests
from aiogram import Bot, Router, F, types
from aiogram.filters import Command
from aiogram.fsm import state
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
import logging

from core.callbacks.navigation import query_message_photo
from core.database.models import *
from core.handlers.callback import *
from core.projects.AI.callbacks.ai_assistant import create_chatgpt_prompt
from core.projects.AI.keyboards.builder import inline_builder, quit_ai, order, ai

router = Router()


class AI_ASS(StatesGroup):
    waiting_for_ai_ass = State()
    waiting_for_gpt_ass = State()


@router.callback_query(F.data == 'ai_helper')
async def ai_helper(query: CallbackQuery, bot: Bot, state: FSMContext):

    if state:
        await state.clear()

    text = (
        f"<b>🤖 AI помощник</b>\n\n"
        f"В разделе  представлен инновационный чат-бот на основе технологии ChatGPT, разработанный как помощник "
        f"для обслуживания клиентов. Наш примерный проект Beauty Bot демонстрирует, как такой бот может "
        f"выступать в роли администратора салона красоты, обеспечивая высококачественное и "
        f"персонализированное обслуживание.\n\n"
        f"Если вы хотите адаптировать эту концепцию под свои нужды, "
        f"наша команда готова помочь вам в реализации вашего проекта."
    )
    image_path = 'https://botnest.ru/wp-content/uploads/2024/botnest/images/examples.png'

    await query_message_photo(query, bot, text, image_path, ai)


@router.callback_query(F.data == 'ai_gpt')
async def ai_gpt(query: CallbackQuery, bot: Bot, state: FSMContext):

    if state:
        await state.clear()

    text = (
        f"<b>🤖 ChatGPT помощник</b>\n\n"
        f"В разделе представлен революционного помощник, воплощение новейших достижений в области искусственного "
        f"интеллекта - чат-бот, интегрированный с ChatGPT.\n\nЭтот бот способен общаться на любые темы, "
        f"предоставляя мгновенные ответы на разнообразные вопросы и запросы."
    )
    image_path = 'https://botnest.ru/wp-content/uploads/2024/botnest/images/examples.png'

    await query_message_photo(query, bot, text, image_path, ai)

@router.callback_query(F.data == 'ai_ass')
async def ai_ass(query: CallbackQuery, state: FSMContext, bot: Bot):
    await state.set_state(AI_ASS.waiting_for_ai_ass)

    sent_message = await query.message.answer("Вы в режиме AI ассистента. Задайте свой вопрос или нажмите 'Отмена' для выхода.",
                                              reply_markup=inline_builder(quit_ai))

    await update_last_message_id(bot, sent_message.message_id, query.from_user.id)


@router.callback_query(F.data == 'ai_gpt')
async def ai_gpt(query: CallbackQuery, state: FSMContext, bot: Bot):
    await state.set_state(AI_ASS.waiting_for_gpt_ass)

    sent_message = await query.message.answer("Вы в режиме чата GPT. Задайте свой вопрос или нажмите 'Отмена' для выхода.",
                                              reply_markup=inline_builder(quit_ai))

    await update_last_message_id(bot, sent_message.message_id, query.from_user.id)


@router.message(AI_ASS.waiting_for_ai_ass, F.text)
async def process_ai_question(message: Message, bot: Bot, state: FSMContext):
    try:
        user_input = message.text
        prompt = create_chatgpt_prompt(user_input)

        # Установка ограничений для размера ответа и температуры
        temperature = 0.4  # Пример для умеренной творческой свободы

        chat = openai.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=prompt,
            temperature=temperature
        )

        answer = chat.choices[0].message.content
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

        # Проверка ответа и вызов callback-функции
        if "Для записи на услуги" in answer:
            sent_message = await message.answer("Хотите записаться на услугу?", reply_markup=inline_builder(order))
            await update_last_message_id(bot, sent_message.message_id, message.from_user.id)
        else:
            sent_message = await message.answer(answer, reply_markup=inline_builder(quit_ai))
            await update_last_message_id(bot, sent_message.message_id, message.from_user.id)
    except Exception as e:
        logging.error(e)


@router.message(AI_ASS.waiting_for_gpt_ass, F.text)
async def process_ai_question(message: Message, bot: Bot, state: FSMContext):
    try:
        user_input = message.text

        # Установка ограничений для размера ответа и температуры
        temperature = 0.4  # Пример для умеренной творческой свободы

        chat = openai.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=user_input,
            temperature=temperature
        )

        answer = chat.choices[0].message.content
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


        sent_message = await message.answer(answer, reply_markup=inline_builder(quit_ai))
        await update_last_message_id(bot, sent_message.message_id, message.from_user.id)
    except Exception as e:
        logging.error(e)
