import openai

from aiogram import Bot, Router, F

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
import logging

from core.callbacks.navigation import query_message_photo

from core.database.requests import Database
from core.handlers.callback import *
from core.projects.ai.callbacks.ai_assistant import create_chatgpt_prompt
from core.projects.ai.keyboards.builder import *

router = Router()
db = Database()


class AI_ASS(StatesGroup):
    waiting_for_ai_ass = State()
    waiting_for_gpt_ass = State()


@router.callback_query(F.data == 'ai_helper')
async def ai_helper(query: CallbackQuery, bot: Bot, state: FSMContext):
    if state:
        await state.clear()

    text = (
        f"<b>🤖 ai помощник</b>\n\n"
        f"В разделе представлен инновационный чат-бот на основе технологии ChatGPT, разработанный как помощник "
        f"для обслуживания клиентов. Наш примерный проект Beauty Bot демонстрирует, как такой бот может "
        f"выступать в роли администратора салона красоты, обеспечивая высококачественное и "
        f"персонализированное обслуживание.\n\n"
        f"Если вы хотите адаптировать эту концепцию под свои нужды, "
        f"наша команда готова помочь вам в реализации вашего проекта."
        f"\n\nДля тестирования данной функции доступно всего <b>5 запросов</b>."
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
        f"\n\nДля тестирования данной функции доступно всего <b>5 запросов</b>."
    )
    image_path = 'https://botnest.ru/wp-content/uploads/2024/botnest/images/examples.png'

    await query_message_photo(query, bot, text, image_path, gpt_menu)


@router.callback_query(F.data == 'ai_ass')
async def ai_ass(query: CallbackQuery, state: FSMContext, bot: Bot):
    await state.set_state(AI_ASS.waiting_for_ai_ass)

    sent_message = await query.message.answer(
        "Вы в режиме ai ассистента. Задайте свой вопрос или нажмите 'Отмена' для выхода.",
        reply_markup=inline_builder(quit_ai))

    await update_last_message_id(bot, sent_message.message_id, query.from_user.id)


@router.callback_query(F.data == 'ai_gpt_start')
async def ai_gpt(query: CallbackQuery, state: FSMContext, bot: Bot):
    await state.set_state(AI_ASS.waiting_for_gpt_ass)

    sent_message = await query.message.answer(
        "Вы в режиме чата GPT. Задайте свой вопрос или нажмите 'Отмена' для выхода.",
        reply_markup=inline_builder(quit_gpt))

    await update_last_message_id(bot, sent_message.message_id, query.from_user.id)


@router.message(AI_ASS.waiting_for_ai_ass, F.text)
async def process_ai_question(message: Message, bot: Bot, state: FSMContext):
    # Проверяем наличие токенов перед выполнением запроса
    has_tokens = await db.check_user_tokens(message.from_user.id, "gpt_assistant")
    if not has_tokens:
        await message.answer("К сожалению, у вас закончились токены для использования этой функции.",
                             reply_markup=inline_builder(quit_ai))
        return

    try:
        user_input = message.text
        prompt = create_chatgpt_prompt(user_input)


        temperature = 0.4

        chat = openai.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=prompt,
            temperature=temperature
        )

        answer = chat.choices[0].message.content
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

        # Проверка ответа и вызов
        if "Для записи на услуги" in answer:
            sent_message = await message.answer("Хотите записаться на услугу?", reply_markup=inline_builder(order))
            await update_last_message_id(bot, sent_message.message_id, message.from_user.id)
        else:
            sent_message = await message.answer(answer, reply_markup=inline_builder(quit_ai))
            await update_last_message_id(bot, sent_message.message_id, message.from_user.id)
    except Exception as e:
        logging.error(e)


@router.message(AI_ASS.waiting_for_gpt_ass, F.text)
async def process_ai_question(message: Message, bot: Bot):
    # Проверяем наличие токенов перед выполнением запроса
    has_tokens = await db.check_user_tokens(message.from_user.id, "gpt")
    if not has_tokens:
        await message.answer("К сожалению, у вас закончились токены для использования этой функции.",
                             reply_markup=inline_builder(quit_gpt))
        return

    try:
        user_input = message.text

        # Установка ограничений для размера ответа и температуры
        temperature = 0.4 

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
