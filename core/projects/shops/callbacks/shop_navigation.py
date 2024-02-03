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

image_main = 'https://botnest.ru/wp-content/uploads/2024/botnest/shop/photo/shop.webp'

router = Router()

@router.callback_query(F.data == 'shop_main')
async def fin_trigger(query: CallbackQuery, bot: Bot):
    text = (
        "<b>Магазин телефонов MobileNest</b> \n\n"
        "Данный бот показывает пример реализации бота магазина мобильных телефонов с полным рабочим функционалом:"
        " карточки товаров, категории, корзина, покупка и доставка товара."
    )
    image_path = image_main

    await query_message_photo(query, bot, text, image_path, shop_info)


@router.callback_query(F.data == 'get_categories')
async def get_categories(query: CallbackQuery, bot: Bot):  # Создание экземпляра класса для работы с БД
    category_menu = await get_categories_menu()

    text = (
        "<b>Выберите категорию товара:</b>"
    )

    image_path = image_main

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
    image_path = image_main

    await query_message_photo(query, bot, text, image_path, category_menu)
    await query.answer()

@router.callback_query(F.data.startswith("brand_"))
async def show_products_by_brand(query: CallbackQuery, bot: Bot):
    data_parts = query.data.split('_')
    if len(data_parts) == 3:
        # Если callback_data содержит три части, значит это формат "brand_{brand_slug}_{page}"
        _, brand_slug, str_page = data_parts
        page = int(str_page)
    elif len(data_parts) == 2:
        # Если callback_data содержит две части, значит это формат "brand_{brand_slug}", и используется первая страница
        _, brand_slug = data_parts
        page = 0
    else:
        # Неожиданный формат callback_data
        await query.answer("Произошла ошибка, попробуйте ещё раз.", show_alert=True)
        return

    products_menu = await get_products_by_brand_menu(brand_slug, page)


    text = f"<b>Продукты бренда:</b>"

    await query_message_photo(query, bot, text, "https://botnest.ru/wp-content/uploads/2024/botnest/shop/photo/apple-logo.jpg", products_menu)
    await query.answer()

def get_product_keyboard(product_id: int, quantity: int, brand_slug: str, telegram_id: int):
    buttons = [
        [
            types.InlineKeyboardButton(text="⬇️", callback_data=f"decrease_{product_id}_{quantity}_{telegram_id}"),
            types.InlineKeyboardButton(text=f"🛒 +{quantity}", callback_data=f"add_{product_id}_{quantity}_{telegram_id}"),
            types.InlineKeyboardButton(text="⬆️", callback_data=f"increase_{product_id}_{quantity}_{telegram_id}")
        ],
        [types.InlineKeyboardButton(text="Назад к бренду", callback_data=f"brand_{brand_slug}_0")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


@router.callback_query(or_f(F.data.startswith("increase_"), F.data.startswith("decrease_")))
async def change_quantity(query: CallbackQuery, bot: Bot):
    action, product_id, quantity, telegram_id = query.data.split('_')
    product_id = int(product_id)
    quantity = int(quantity)
    telegram_id = int(telegram_id)

    # Получаем информацию о продукте из базы данных
    product = await db.get_product_by_id(product_id)
    if not product:
        await query.answer("Продукт не найден.", show_alert=True)
        return

    if action == "increase":
        if quantity < product.stock_quantity:  # Увеличиваем только если меньше доступного количества
            quantity += 1
        else:
            await query.answer("Нельзя добавить больше доступного количества.", show_alert=True)
            return
    elif action == "decrease":
        if quantity > 1:
            quantity -= 1
        else:
            await query.answer("Минимальное количество для добавления - 1 шт.", show_alert=True)
            return


    await update_product_details(query.message, product_id, quantity, telegram_id, bot)
    await query.answer()

async def update_product_details(message: Message, product_id: int, quantity: int, telegram_id, bot: Bot):
    product = await db.get_product_by_id(product_id)
    if not product:
        await message.answer("Продукт не найден.")
        return

    text = f"<b>{product.name}</b>\n\n" \
           f"<b>Цвет:</b> {product.color}\n" \
           f"<b>Размер экрана:</b> {product.screen_size}\n" \
           f"<b>Память:</b> {product.storage}\n" \
           f"<b>ОЗУ:</b> {product.ram}\n" \
           f"<b>Батарея:</b> {product.battery_capacity} мАч\n" \
           f"<b>ОС:</b> {product.operating_system}\n" \
           f"<b>Камера:</b> {product.camera_resolution}\n" \
           f"<b>Описание:</b> {product.description}\n\n" \
           f"<b>Цена:</b> {product.price} руб.\n\n" \
           f"<b>В наличии:</b> {product.stock_quantity} шт."

    sent_message = await message.answer_photo(photo=product.photo_url, caption=text, parse_mode="HTML",
                                              reply_markup=get_product_keyboard(product_id, quantity, product.brand.name_slug, telegram_id))
    await update_last_message_id(bot, sent_message.message_id, telegram_id)

@router.callback_query(F.data.startswith("product_"))
async def show_product_details(query: CallbackQuery, bot: Bot):
    data_parts = query.data.split('_')
    product_id = int(data_parts[1])
    # Устанавливаем количество по умолчанию равным 1, если оно не указано
    quantity = int(data_parts[2]) if len(data_parts) > 2 else 1


    product = await db.get_product_by_id(product_id)

    if not product:
        await query.answer("Продукт не найден.", show_alert=True)
        return

    text = f"<b>{product.name}</b>\n\n" \
           f"<b>Цвет:</b> {product.color}\n" \
           f"<b>Размер экрана:</b> {product.screen_size}\n" \
           f"<b>Память:</b> {product.storage}\n" \
           f"<b>ОЗУ:</b> {product.ram}\n" \
           f"<b>Батарея:</b> {product.battery_capacity} мАч\n" \
           f"<b>ОС:</b> {product.operating_system}\n" \
           f"<b>Камера:</b> {product.camera_resolution}\n" \
           f"<b>Описание:</b> {product.description}\n\n" \
           f"<b>Цена:</b> {product.price} руб.\n\n" \
           f"<b>В наличии:</b> {product.stock_quantity} шт."

    # Отправка сообщения с фото и деталями продукта
    sent_message = await query.message.answer_photo(photo=product.photo_url, caption=text, parse_mode="HTML", reply_markup=get_product_keyboard(product_id, quantity, product.brand.name_slug, query.from_user.id))
    await update_last_message_id(bot, sent_message.message_id, query.from_user.id)
    await query.answer()


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