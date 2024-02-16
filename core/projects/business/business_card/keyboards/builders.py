from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

card_main_menu = [
    [['О нас', 'card_info'], ['Услуги', 'card_services']],
    [['Новости', 'card_news'], ['Контакты', 'card_contacts']],
    [['Заказать звонок', 'card_callback']],
    [['Назад', 'business_examples']]
]

card_about_us = [
    [['Наши юристы', 'start_lawyer']],
    [['Назад', 'card_main']]
]

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def generate_lawyers_keyboard(current_id: int, total_lawyers: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    buttons = []

    # Кнопка "Назад"
    if current_id > 1:
        buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"lawyer_{current_id - 1}"))

    # Кнопка "Вперед"
    if current_id < total_lawyers:
        buttons.append(InlineKeyboardButton(text="Вперед ➡️", callback_data=f"lawyer_{current_id + 1}"))

    keyboard.inline_keyboard.append(buttons)
    keyboard.inline_keyboard.append([
        types.InlineKeyboardButton(text="Назад", callback_data="card_info")
    ])
    return keyboard
