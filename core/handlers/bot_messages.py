from contextlib import suppress

from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, CallbackQuery
from aiogram.types import callback_query

import core.keyboards
from core.keyboards import reply, inline, builders, fabrics
from core.data.subloader import get_json

router = Router()


@router.callback_query(F.data == "back_send_email")
async def send_email(query: CallbackQuery, bot: Bot):
    await query.answer()
    await query.message.edit_text("Наш email: info@botnest.ru", reply_markup=inline.get_back)

@router.callback_query(F.data == "back_send_email")
async def send_email(query: CallbackQuery, bot: Bot):
    await query.answer()
    await query.message.edit_text("Наш email: info@botnest.ru", reply_markup=inline.get_back)

