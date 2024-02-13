from typing import Union, List

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
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
                elif 'web_app' in data:
                    button = InlineKeyboardButton(text=text, web_app=WebAppInfo(url=data['web_app']))
                elif 'pay' in data:
                    button = InlineKeyboardButton(text=text, pay=data['pay'])
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
    [['Примеры ботов', 'bot_examples'], ['Контакты', 'contacts']]
]

order_menu = [
    [['Сделать заказ', {'web_app': 'https://botnest.ru/wp-content/uploads/2024/botnest/order.html'}]],
    [['Назад', 'main_menu']]
]

cancel_faq = [
    [['Отмена', 'main_menu']]
]

contact_menu = [
    [['Написать в телеграм', {'url': 'https://t.me/ryzkov_dv'}]],
    [['Перейти на сайт', {'url': 'https://botnest.ru'}]],
    [['Назад', 'main_menu']]
]

cancel_order = [
    [['Отмена', 'cancel_order']]
]

examples_type = [
    [['ИИ боты', 'ai_examples'], ['Информационные', 'info_examples']],
    [['Игровые', 'game_examples'], ['Для бизнеса', 'business_examples']],
    [['Инструменты', 'service_examples']],
    [['Назад', 'main_menu']]
]

service_type = [
    [['Из текста в голос', 'text2voice']],
    [['Назад', 'bot_examples']]
]

info_type = [
    [['Валюты и Акции', 'business_info']],
    [['Назад', 'bot_examples']]
]

business_type = [
    [['Магазин телефонов', 'shop_main']],
    [['Назад', 'bot_examples']]
]

ai_type = [
    [['ИИ-ассистент', 'ai_helper'], ['ChatGPT', 'ai_gpt']],
    [['Назад', 'bot_examples']]
]

games_type = [
    [['Одиночная игра - Lost Order', 'lost_order']],
    [['Сетевая игра - Final Trigger', 'fin_trigger']],
    [['Назад', 'bot_examples']]
]

final_trigger = [
    [['Начать игру', {'url': 'https://t.me/FinalTriggerBot'}]],
    [['Назад', 'game_examples']]
]