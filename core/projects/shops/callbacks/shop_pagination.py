from contextlib import suppress

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from core.keyboards import fabrics
from core.data.subloader import get_json

router = Router()


# @dp.callback_query_handler(lambda c: c.data and c.data.startswith(('prev_', 'next_')))
# async def pagination_handler(call: types.CallbackQuery):
#     action, current_page = call.data.split('_')
#     current_page = int(current_page)
#     page = current_page - 1 if action == "prev" else current_page + 1
#
#     # Здесь должна быть ваша логика получения списка категорий и общего количества страниц
#     categories, total_pages = await get_categories(page=page)
#
#     text = "\n".join([f"{category['name']}" for category in categories])  # Пример форматирования списка категорий
#
#     with suppress(TelegramBadRequest):
#         await call.message.edit_text(
#             text,
#             reply_markup=get_categories_keyboard(page, total_pages)
#         )
#     await call.answer()

