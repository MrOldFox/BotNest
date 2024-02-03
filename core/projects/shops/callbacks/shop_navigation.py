import json

import aiohttp
import requests
from aiogram import types
from aiogram.fsm.state import StatesGroup, State

import logging

from core.callbacks.navigation import *
from core.database.models import OrderRequest, UserRole
from core.handlers.user_commands import *
from core.keyboards.reply import *
from core.projects.info.business_info.keyboards.builders import *
from core.projects.shops.handlers.sql import Database
from core.projects.shops.keyboards.builders import *
from aiogram.filters.callback_data import CallbackData


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


@router.callback_query(F.data == 'get_categories')
async def get_categories(query: CallbackQuery, bot: Bot):  # Создание экземпляра класса для работы с БД
    category_menu = await get_categories_menu()

    text = (
        "<b>Выберите категорию товара:</b>"
    )

    image_path = 'https://botnest.ru/wp-content/uploads/2024/01/logot.png'

    await query_message_photo(query, bot, text, image_path, category_menu)


@router.callback_query(F.data.startswith("page_"))
async def paginate_categories(query: CallbackQuery, bot: Bot):
    # Извлекаем номер страницы из callback_data
    print(query.data)
    page = int(query.data.split('_')[1])

    # Получаем обновленное меню категорий и кнопки пагинации
    category_menu = await get_categories_menu(page=page)

    # Обновляем сообщение с новым списком категорий и кнопками пагинации
    text = "<b>Выберите категорию товара:</b>"
    image_path = 'https://botnest.ru/wp-content/uploads/2024/01/logot.png'

    await query_message_photo(query, bot, text, image_path, category_menu)
    await query.answer()


dp = Database()

# @router.callback_query(F.data.startswith("brand_"))
# async def show_products_by_brand(query: CallbackQuery, bot: Bot):
#     data_parts = query.data.split('_')
#     if len(data_parts) == 3:
#         # Если callback_data содержит три части, значит это формат "brand_{brand_slug}_{page}"
#         _, brand_slug, str_page = data_parts
#         page = int(str_page)
#     elif len(data_parts) == 2:
#         # Если callback_data содержит две части, значит это формат "brand_{brand_slug}", и используется первая страница
#         _, brand_slug = data_parts
#         page = 0
#     else:
#         # Неожиданный формат callback_data
#         await query.answer("Произошла ошибка, попробуйте ещё раз.", show_alert=True)
#         return
#
#     # Далее логика обработки не меняется
#     products = await db.get_products_by_brand(brand_slug, page)
#
#     if not products:
#         await query.answer("Больше продуктов нет.", show_alert=True)
#         return
#
#     product = products[0]  # Показываем один продукт за раз
#     text = f"<b>{product.name}</b>\nЦена: {product.price} руб.\nЦвет: {product.color}\nРазмер экрана: {product.screen_size}\nПамять: {product.storage} ГБ\nОЗУ: {product.ram} ГБ\nБатарея: {product.battery_capacity} мАч\nОС: {product.operating_system}\nКамера: {product.camera_resolution}\n\nОписание: {product.description}\nВ наличии: {product.stock_quantity} шт."
#
#     # Создание клавиатуры для пагинации
#     keyboard = InlineKeyboardMarkup(inline_keyboard=[
#         [InlineKeyboardButton(text="⬅️ Назад",
#                               callback_data=f"brand_{brand_slug}_{page - 1}" if page > 0 else f"brand_{brand_slug}_{page}"),
#          InlineKeyboardButton(text="Вперед ➡️", callback_data=f"brand_{brand_slug}_{page + 1}")],
#         [InlineKeyboardButton(text="Вернуться к брендам", callback_data="get_categories")]
#     ])
#
#
#     sent_message = await bot.send_photo(chat_id=query.from_user.id, photo=product.photo_url, caption=text, reply_markup=keyboard)
#     await update_last_message_id(bot, sent_message.message_id, query.from_user.id)
#     await query.answer()