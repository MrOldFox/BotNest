from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    KeyboardButtonPollType
)

cancel = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Отмена"),
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    selective=True
)

spec = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Отправить гео", request_location=True),
            KeyboardButton(text="Отправить контакт", request_contact=True),
            KeyboardButton(text="Создать викторину", request_poll=KeyboardButtonPollType())
        ],
        [
            KeyboardButton(text="НАЗАД")
        ]
    ],
    resize_keyboard=True
)