from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

card_main_menu = [
    [['О нас', 'card_info'], ['Услуги', 'card_services']],
    [['Новости', 'card_news'], ['Контакты', 'card_contacts']],
    [['Заказать звонок', {'web_app': 'https://botnest.ru/wp-content/uploads/2024/botnest/lawnest/lawnest.html'}]],
    [['Назад', 'business_examples']]
]

card_about_us = [
    [['Наши юристы', 'start_lawyer']],
    [['Назад', 'card_main']]
]

card_service = [
    [['Корпоративное право', 'card_service_m2a']],
    [['Недвижимость и земельное право', 'card_service_estate']],
    [['Интеллектуальная собственность', 'card_service_property']],
    [['Назад', 'card_main']]
]

card_services = [
    [['Назад', 'card_services']]
]

card_contact = [
    [['Заказать звонок', {'web_app': 'https://botnest.ru/wp-content/uploads/2024/botnest/lawnest/lawnest.html'}]],
    [['Назад', 'card_main']]
]


card_contact_menu = [
    [['Перейти на сайт', {'url': 'https://botnest.ru'}]],
    [['Получить контакт', 'card_tel']],
    [['Назад', 'main_menu']]
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
