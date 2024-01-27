from typing import Union, List

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def inline_builder(button_layout: List[List[Union[str, List]]]) -> InlineKeyboardMarkup:
    inline_keyboard = []

    for row in button_layout:
        row_buttons = []
        for btn in row:
            text = btn[0]
            data = btn[1]

            # Определяем тип кнопки: URL или callback
            if isinstance(data, dict):
                if 'url' in data:
                    button = InlineKeyboardButton(text=text, url=data['url'])
                elif 'callback_data' in data:
                    button = InlineKeyboardButton(text=text, callback_data=data['callback_data'])
                else:
                    continue  # Пропускаем неизвестные типы
            else:
                # Старый формат для обратной совместимости
                button = InlineKeyboardButton(text=text, callback_data=data)

            row_buttons.append(button)
        inline_keyboard.append(row_buttons)

    markup = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    return markup


main_menu = [
    [['Заказать', 'order'], ['FAQ', 'faq']],
    [['Примеры ботов', 'lost_order'], ['Контакты', 'contacts']]
]

order_menu = [
    [['Сделать заказ', 'make_order']],
    [['Назад', 'main_menu']]
]

contact_menu = [
    [['Написать в телеграм', {'url': 'test.ru'}]],
    [['Назад', 'main_menu']]
]

cancel_order = [
    [['Отмена', 'cancel_order']]
]

share_phone = [
    [['Поделиться контактом', 'share_phone']],
    [['Отмена', 'cancel_order']]
]
