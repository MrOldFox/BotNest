from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    KeyboardButtonPollType, WebAppInfo
)

order_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Заполнить заявку', web_app=WebAppInfo(url='https://botnest.ru/wp-content/uploads/2024/botnest/order.html')),
            KeyboardButton(text='Отмена'),
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

spec = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Заполнить анкету", request_location=True),
        ],
        [
            KeyboardButton(text="НАЗАД")
        ]
    ],
    resize_keyboard=True
)