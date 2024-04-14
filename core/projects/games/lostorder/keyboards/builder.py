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
    [['Бросить кубик', 'dice']],
    [['Выход', 'game_examples']]
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
    [['Через лес', 'forest'], ['Вдоль реки', 'river']],
    [['Выход', 'game_examples']]
]

EnemyAttack = [
    [['Защититься', 'defense']],
    [['Выход', 'game_examples']]
]

RiverEncounter = [
    [['Подойти к незнакомцу', 'start_encounter']],
    [['Продолжить путь', 'start_encounter_fail']],
    [['Выход', 'game_examples']]
]

stranger_choice_success = [
    [['Продолжить путь', 'start_encounter_success']],
    [['Выход', 'game_examples']]
]

stranger_choice_fail = [
    [['Продолжить путь', 'start_encounter_fail']],
    [['Выход', 'game_examples']]
]

WolfEnemyAttack = [
    [['Защититься', 'wolf_defense']],
    [['Выход', 'game_examples']]
]

bad_caravan = [
    [['Продолжить путь', 'skip_shadowstalker']],
    [['Выход', 'game_examples']]
]


safe_caravan = [
    [['Продолжить путь', 'defense_shadowstalker']],
    [['Выход', 'game_examples']]
]

stranger_choice = [
    [['Убедить рассказать больше', 'persuade_to_tell_more']],
    [['Продолжить путь', 'start_encounter_fail']],
    [['Выход', 'game_examples']]
]

WolfEncounter = [
    [['Подойти к незнакомцу', 'start_encounter']],
    [['Продолжить путь', 'start_encounter_fail']],
    [['Выход', 'game_examples']]
]

ToVillage = [
    [['Продолжить путь', 'village']],
    [['Выход', 'game_examples']]
]

Quit = [
    [['Начать сначала', 'start_game']],
    [['Сдаться...', 'main_menu']],
]

VillagePath = [
    [['Заказать бота', 'make_order']],
    [['Начать сначала', 'start_game'], ['Главное меню', 'main_menu']]
]
