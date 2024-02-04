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

    # Получаем photo_url для данного brand_slug
    photo_url = await db.get_brand_photo_url_by_slug(brand_slug)
    if not photo_url:
        photo_url = "https://botnest.ru/wp-content/uploads/2024/botnest/shop/photo/shop.webp"


    products_menu = await get_products_by_brand_menu(brand_slug, page)


    text = f"<b>Продукты бренда:</b>"

    await query_message_photo(query, bot, text, photo_url, products_menu)
    await query.answer()


@router.callback_query(F.data.startswith("color_"))
async def show_products_by_color(query: CallbackQuery, bot: Bot):
    data_parts = query.data.split('_')
    if len(data_parts) == 4:
        # Если callback_data содержит три части, значит это формат "brand_{brand_slug}_{page}"
        _, product_name, brand_slug, str_page = data_parts
        page = int(str_page)
    elif len(data_parts) == 3:
        # Если callback_data содержит две части, значит это формат "brand_{brand_slug}", и используется первая страница
        _, product_name, brand_slug = data_parts
        page = 0
    else:
        # Неожиданный формат callback_data
        await query.answer("Произошла ошибка, попробуйте ещё раз.", show_alert=True)
        return

    products_menu = await get_products_by_color(product_name, brand_slug)


    text = f"<b>Выберите цвет продукта:</b>"

    await query_message_photo(query, bot, text, "https://botnest.ru/wp-content/uploads/2024/botnest/shop/photo/apple-logo.jpg", products_menu)
    await query.answer()


def get_product_keyboard(product_id: int, quantity: int, brand_slug: str, telegram_id: int, product_name: str, color: bool):
    if color:
        buttons = [
            [
                types.InlineKeyboardButton(text="⬇️", callback_data=f"decrease_{product_id}_{quantity}_{telegram_id}_{product_name}_{color}"),
                types.InlineKeyboardButton(text=f"🛒 +{quantity}", callback_data=f"add_{product_id}_{quantity}_{telegram_id}_{product_name}_{color}"),
                types.InlineKeyboardButton(text="⬆️", callback_data=f"increase_{product_id}_{quantity}_{telegram_id}_{product_name}_{color}")
            ],

                [types.InlineKeyboardButton(text="Назад", callback_data=f"color_{product_name}_{brand_slug}")]

            ]
    else:
        buttons = [
            [
                types.InlineKeyboardButton(text="⬇️", callback_data=f"decrease_{product_id}_{quantity}_{telegram_id}_{product_name}_{color}"),
                types.InlineKeyboardButton(text=f"🛒 +{quantity}",
                                           callback_data=f"add_{product_id}_{quantity}_{telegram_id}_{product_name}_{color}"),
                types.InlineKeyboardButton(text="⬆️", callback_data=f"increase_{product_id}_{quantity}_{telegram_id}_{product_name}_{color}")
            ],

            [types.InlineKeyboardButton(text="Назад", callback_data=f"brand_{brand_slug}")]
            ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)

    return keyboard


@router.callback_query(or_f(F.data.startswith("increase_"), F.data.startswith("decrease_")))
async def change_quantity(query: CallbackQuery, bot: Bot):
    action, product_id, quantity, telegram_id, product_name, color = query.data.split('_')
    product_id = int(product_id)
    quantity = int(quantity)
    telegram_id = int(telegram_id)
    product_name = str(product_name)
    color = bool(color)


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


    await update_product_details(query.message, product_id, quantity, telegram_id, bot, product_name, color)
    await query.answer()

async def update_product_details(message: Message, product_id: int, quantity: int, telegram_id, bot: Bot, product_name: str, color: bool):
    product = await db.get_product_by_id(product_id)
    if not product:
        await message.answer("Продукт не найден.")
        return

    text = generate_product_details_text(product)

    sent_message = await message.answer_photo(photo=product.photo_url, caption=text, parse_mode="HTML",
                                              reply_markup=get_product_keyboard(product_id, quantity, product.brand.name_slug, telegram_id, product_name, color))
    await update_last_message_id(bot, sent_message.message_id, telegram_id)

@router.callback_query(F.data.startswith("product_"))
async def show_product_details(query: CallbackQuery, bot: Bot):
    data_parts = query.data.split('_')
    product_id = int(data_parts[1])
    # Устанавливаем количество по умолчанию равным 1, если оно не указано
    quantity = int(data_parts[2]) if len(data_parts) > 4 else 1
    brand_slug = str(data_parts[2])
    color = False

    if len(data_parts) > 4:  # Предполагаем, что у вас 5 частей в data_parts
        quantity = int(data_parts[2])
        brand_slug = data_parts[3]
        color = data_parts[4].lower() == "true"
    elif len(data_parts) > 3:  # Предполагаем, что у вас 4 части в data_parts
        brand_slug = data_parts[2]
        color = data_parts[3].lower() == "true"
    else:
        # Если меньше, то используем значения по умолчанию или другую логику
        pass

    product = await db.get_product_by_id(product_id)
    product_name = await db.get_product_name_by_id(product_id)

    if not product:
        await query.answer("Продукт не найден.", show_alert=True)
        return

    text = generate_product_details_text(product)

    # Отправка сообщения с фото и деталями продукта
    if color:
        sent_message = await query.message.answer_photo(photo=product.photo_url, caption=text, parse_mode="HTML", reply_markup=get_product_keyboard(product_id, quantity, brand_slug, query.from_user.id, product_name, True))
    else:
        sent_message = await query.message.answer_photo(photo=product.photo_url, caption=text, parse_mode="HTML", reply_markup=get_product_keyboard(product_id, quantity, brand_slug, query.from_user.id, product_name, False))
    await update_last_message_id(bot, sent_message.message_id, query.from_user.id)
    await query.answer()




def generate_product_details_text(product):
    """
    Генерирует текстовое описание продукта для отображения в сообщении.

    :param product: Экземпляр продукта, содержащий его характеристики.
    :return: Строка с описанием продукта.
    """
    # Основная информация о продукте
    details = [
        f"<b>{product.name}</b>\n",
        f"Цена: <b>{product.price} руб.</b>\n",
        f"Цвет: <b>{product.color}</b>\n",
        f"Размер экрана: <b>{product.screen_size}</b>\n",
        f"Память: <b>{product.storage}</b>\n",
        f"ОЗУ: <b>{product.ram}</b>\n",
        f"Батарея: <b>{product.battery_capacity} мАч</b>\n",
        f"Операционная система: <b>{product.operating_system}</b>\n",
        f"Разрешение камеры: <b>{product.camera_resolution}</b>\n"
    ]

    # Дополнительное описание, если оно доступно
    if product.description:
        details.append(f"\nОписание:\n{product.description}\n")

    # Информация о наличии на складе
    stock_info = f"В наличии: <b>{product.stock_quantity} шт.</b>" if product.stock_quantity > 0 else "<b>Нет в наличии</b>"
    details.append(stock_info)

    return ''.join(details)

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