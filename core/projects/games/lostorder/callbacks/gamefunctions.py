import asyncio
import datetime
from random import randint

from aiogram import types, Router, F
from aiogram.filters import or_f, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from core.projects.games.lostorder.keyboards.builder import inline_builder

router = Router()


async def choose_path(text, photo, query, reply_markup):
    sent_message = await query.bot.send_photo(
        query.message.chat.id,
        photo=photo,
        caption=text,
        reply_markup=inline_builder(reply_markup)
    )
    return sent_message
