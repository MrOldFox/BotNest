import json

import aiohttp
import requests
from aiogram.fsm.state import StatesGroup, State

import logging

from core.callbacks.navigation import *
from core.database.models import OrderRequest, UserRole
from core.handlers.user_commands import *
from core.keyboards.reply import *
from core.projects.info.business_info.keyboards.builders import *
from core.projects.shops.keyboards.builders import *

router = Router()


@router.callback_query(F.data == 'shop_main')
async def fin_trigger(query: CallbackQuery, bot: Bot):
    text = (
        "<b>Магазин товаров</b> \n\n"
        "Данный бот показывает пример реализации бота магазина одежды с полным рабочим функционалом:"
        " карточки товаров, категории, корзина, покупка и доставка товара."
    )
    image_path = 'https://botnest.ru/wp-content/uploads/2024/01/logot.png'

    await query_message_photo(query, bot, text, image_path, shop_info)