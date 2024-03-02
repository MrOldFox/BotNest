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

from config_reader import config
from core.callbacks.navigation import query_message_photo, query_message
from core.database.requests import Database
from core.handlers.callback import update_last_message_id
from core.handlers.user_commands import start
from core.keyboards.builders import inline_builder
from core.projects.service.voice2text.keyboards.builders import text_voice, text_quit

router = Router()
db = Database()


class VOICE(StatesGroup):
    waiting_for_text = State()


@router.callback_query(F.data == 'text2voice')
async def text2voice(query: CallbackQuery, bot: Bot, state: FSMContext):
    if state:
        await state.clear()
    text = (
        f"<b>🔊 Преобразование текста в аудио</b>\n\n"
        f"Эта функциональность позволяет вам превратить любой текст в аудиофайл. "
        f"Теперь вы можете слушать статьи, новости, заметки и любые другие тексты, "
        f"когда у вас нет возможности читать.\n\n"
        f"Просто отправьте текст, который вы хотели бы услышать, и система автоматически сгенерирует для вас аудио."
        f"\n\nДля тестирования данной функции доступно всего <b>5 запросов</b>."
    )
    image_path = 'https://botnest.ru/wp-content/uploads/2024/botnest/images/v2t.webp'

    await query_message_photo(query, bot, text, image_path, text_voice)


@router.callback_query(F.data == 'voice')
async def enter_text(query: CallbackQuery, state: FSMContext, bot: Bot):
    await state.set_state(VOICE.waiting_for_text)

    text = (
        f"Напишите текст длинной не более 30 символов, для преобразования в голос или нажмите 'Отмена' для выхода."
    )

    await query_message(query, bot, text, text_quit)

@router.message(VOICE.waiting_for_text, F.text)
async def process_t2v(message: Message, bot: Bot, state: FSMContext):
    has_tokens = await db.check_user_tokens(message.from_user.id, "voice_gen")
    if not has_tokens:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        sent_message = await message.answer("К сожалению, у вас закончились токены для использования этой функции.",
                             reply_markup=inline_builder(text_quit))
        await update_last_message_id(bot, sent_message.message_id, message.from_user.id)
        return

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
    zvukogram_key = config.zvukogram_key.get_secret_value()
    zvukogram_email = config.zvukogram_email.get_secret_value()
    data = {
        'token': zvukogram_key,
        'email': zvukogram_email,
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
