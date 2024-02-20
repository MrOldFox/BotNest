import json

import aiofiles
from aiofile import AIOFile
import aiohttp
import asyncio
import os
import time
import logging

from aiogram.types import InputFile, FSInputFile
from aiogram import Bot, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from core.callbacks.navigation import query_message_photo
from core.handlers.callback import update_last_message_id
from core.handlers.user_commands import start
from core.keyboards.builders import inline_builder
from core.projects.service.voice2text.keyboards.builders import text_voice, text_quit

router = Router()
class VOICE(StatesGroup):
    waiting_for_text = State()


@router.callback_query(F.data == 'text2voice')
async def text2voice(query: CallbackQuery, bot: Bot, state: FSMContext):
    if state:
        await state.clear()
    text = (
        f"<b>🎮 Примеры игровых чат-ботов</b>\n\n"
        f"Test"
    )
    image_path = 'https://botnest.ru/wp-content/uploads/2024/botnest/images/gaming.png'

    await query_message_photo(query, bot, text, image_path, text_voice)



@router.callback_query(F.data == 'voice')
async def enter_faq(query: CallbackQuery, state: FSMContext, bot: Bot):
    await state.set_state(VOICE.waiting_for_text)

    text = (
        f"<b>💬 Часто задаваемые вопросы (FAQ)</b> \n\n"
        f"Здесь вы можете задать любые вопросы, касающиеся работы нашей компании, и получить на них быстрый ответ. "
        f"Этот раздел работает автоматически, без участия оператора, что позволяет вам получить необходимую информацию максимально оперативно.\n\n"
        f"Напишите свой вопрос и когда получите все необходимые ответы - нажмите 'Отмена', чтобы выйти из режима <b>FAQ</b>."
    )
    image_path = 'https://botnest.ru/wp-content/uploads/2024/botnest/images/faq.png'

    await query_message_photo(query, bot, text, image_path, text_quit)



@router.message(VOICE.waiting_for_text, F.text)
async def process_question(message: Message, bot: Bot, state: FSMContext):
    if len(message.text) > 30:
        await message.reply("Ошибка: текст превышает максимально допустимую длину.")
        await state.clear()
        return

    audio_file_path = await text_to_speech(message.text)
    if audio_file_path:

        voice_file = FSInputFile(audio_file_path)

        sent_message = await bot.send_voice(chat_id=message.chat.id, voice=voice_file, caption=message.text,
                                            reply_markup=inline_builder(text_quit))

        os.remove(audio_file_path)
    else:
        sent_message = await message.reply("Не удалось преобразовать текст в аудио.", reply_markup=inline_builder(text_quit))

    await state.clear()

    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await update_last_message_id(bot, sent_message.message_id, message.from_user.id)


async def text_to_speech(text):
    url = "https://zvukogram.com/index.php?r=api/text"
    data = {
        'token': '02bb39c53cd8f1a1700cd819207f95c3',
        'email': 'mrolldfox@gmail.com',
        'voice': 'Захар new',
        'text': text,
        'format': 'mp3',
        'speed': 1.1,
        'pitch': 0.8,
        'emotion': 'good',
        'pause_sentence': 300,
        'pause_paragraph': 400,
        'bitrate': 48000,
    }

    headers = {
        'Accept': 'application/json',
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data) as response:
            response_text = await response.text()
            try:
                result = json.loads(response_text)
                if result['status'] == 1:
                    file_url = result['file']
                    # Создаем имя файла на основе id озвучки
                    file_path = f"{result['id']}.mp3"
                    # Скачиваем файл
                    async with session.get(file_url) as file_response:
                        if file_response.status == 200:
                            async with aiofiles.open(file_path, 'wb') as f:
                                await f.write(await file_response.read())
                            return file_path
                        else:
                            print("Ошибка при скачивании файла")
                else:
                    print("Ошибка API:", result.get('error'))
            except json.JSONDecodeError:
                print("Failed to decode JSON, server returned:", response_text)
                return None
