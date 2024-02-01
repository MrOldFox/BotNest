import json

import aiohttp
import requests
from aiogram.fsm.state import StatesGroup, State

import logging

from core.callbacks.navigation import *
from core.database.models import OrderRequest, UserRole
from core.handlers.user_commands import *
from core.keyboards.reply import *
from core.projects.info.business_info.keyboards.builders import *

router = Router()



async def get_currency_rates():
    url = 'https://www.cbr-xml-daily.ru/daily_json.js'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            # Игнорирование Content-Type и чтение ответа как JSON
            data = await response.json(content_type=None)
            return data['Valute']


def extract_specific_rates(valute_data):
    # Извлечение курсов для определенных валют
    usd_rate = valute_data['USD']['Value']
    eur_rate = valute_data['EUR']['Value']
    cny_rate = valute_data['CNY']['Value']
    jpy_rate = valute_data['JPY']['Value']
    return {
        'USD': usd_rate,
        'EUR': eur_rate,
        'CNY': cny_rate,
        'JPY': jpy_rate
    }
async def crypto_rates():
    url = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,ripple,litecoin&vs_currencies=usd'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json(content_type=None)
            return data



async def get_stock_price(ticker):
    url = f'http://iss.moex.com/iss/engines/stock/markets/shares/boards/tqbr/securities/{ticker}.json'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json(content_type=None)
            last_price = data['marketdata']['data'][0][12]  # Индекс может варьироваться
            return last_price



@router.callback_query(F.data == 'business_info')
async def fin_trigger(query: CallbackQuery, bot: Bot):
    text = (
        "<b>Бот котировок</b> \n\n"
        "Данный бот получает данные Центра Банка о текущих курсах валют"
        " и передает пользователям в удобной форме."
    )
    image_path = 'https://botnest.ru/wp-content/uploads/2024/01/logot.png'

    await query_message_photo(query, bot, text, image_path, rate_info)


@router.callback_query(F.data == 'get_rates')
async def get_rates(query: CallbackQuery, bot: Bot):
    rates = await get_currency_rates()
    specific_rates = extract_specific_rates(rates)
    response_text = 'Курсы валют на сегодня:\n\n'
    response_text += f"Доллар США (USD): {specific_rates['USD']} руб.\n"
    response_text += f"Евро (EUR): {specific_rates['EUR']} руб.\n"
    response_text += f"Китайский юань (CNY): {specific_rates['CNY']} руб.\n"
    response_text += f"Японские йены (JPY): {specific_rates['JPY']} руб.\n"

    await query_message(query, bot, response_text, back)


@router.callback_query(F.data == 'get_crypto_rates')
async def get_crypto_rates(query: CallbackQuery, bot: Bot):
    rates = await crypto_rates()
    response_text = 'Курсы криптовалют:\n\n'
    response_text += f"Биткоин (BTC): ${rates['bitcoin']['usd']}\n"
    response_text += f"Ethereum (ETH): ${rates['ethereum']['usd']}\n"
    response_text += f"Рипл (XRP): ${rates['ripple']['usd']}\n"
    response_text += f"Litecoin (LTC): ${rates['litecoin']['usd']}\n"

    await query_message(query, bot, response_text, back)


@router.callback_query(F.data == 'get_stock_prices')
async def get_stock_prices(query: CallbackQuery, bot: Bot):
    stocks = {
        "Газпром": "GAZP",
        "Сбербанк": "SBER",
        "Ростелеком": "RTKM",
        "Роснефть": "ROSN"
    }
    response_text = 'Котировки акций на сегодня:\n\n'
    for name, ticker in stocks.items():
        price = await get_stock_price(ticker)
        response_text += f"{name}: {price} RUB\n"

    await query_message(query, bot, response_text, back)