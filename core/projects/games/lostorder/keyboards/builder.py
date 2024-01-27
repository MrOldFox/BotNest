from typing import Union, List

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from core.handlers.callback import *

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


RollDice = [
    [['Бросить кубик', 'dice']]
]

# StartGame = [
#     [['Начать игру', 'start_game']],
#     [['Выйти', 'main_menu']]
# ]

StartGame = [
    [['Начать игру', 'start_game']],
    [['Назад', 'game_examples']]
]

ChoosingPath = [
    [['Через лес', 'forest'], ['Вдоль реки', 'river']]
]

EnemyAttack = [
    [['Защититься', 'defense']]
]

RiverEncounter = [
    [['Подойти к незнакомцу', 'start_encounter']],
    [['Продолжить путь', 'village']]
]

ToVillage = [
    [['Продолжить путь', 'village']]
]

Quit = [
    [['Начать сначала', 'start_game']],
    [['Сдаться...', 'main_menu']]
]

VillagePath = [
    [['Заказать бота', 'make_order']],
    [['Начать сначала', 'start_game'], ['Главное меню', 'main_menu']]
]
