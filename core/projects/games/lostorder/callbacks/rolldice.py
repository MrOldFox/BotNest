import asyncio
import datetime
from random import randint

from aiogram import types, Router, F
from aiogram.filters import or_f, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

router = Router()


async def roll_dice(message: types.Message):
    roll = randint(1, 6)
    success = roll > 3
    await message.answer(f"Вы бросили кубик и выпало {roll}. {'Успех!' if success else 'Неудача...'}")
    return success


# Функция для броска кубика

async def check_dice_result(dice_value):
    happy_number = 3
    await asyncio.sleep(4)
    return dice_value > happy_number

