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
from datetime import datetime


router = Router()



async def get_currency_rates():
    url = 'https://www.cbr-xml-daily.ru/daily_json.js'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json(content_type=None)
            return data['Valute']

def timeit():
    now = datetime.now()
    date_time = now.strftime("%d.%m.%Y %H:%M")
    return date_time


def extract_specific_rates(valute_data):
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
            last_price = data['marketdata']['data'][0][12]
            return last_price



@router.callback_query(F.data == 'business_info')
async def fin_trigger(query: CallbackQuery, bot: Bot):

    text = (
        f"<b>💹 Чат-бот котировок</b> \n\n"
        f"Данный бот предназначен для мгновенного получения актуальной "
        f"информации о котировках акций, обменных курсах валют и стоимости криптовалют.\n\n"
        f"Используя данные боты, вы сможете в любой момент получить "
        f"свежую информацию о финансовых индикаторах, что позволит вам оперативно реагировать "
        f"на изменения на рынке и принимать взвешенные инвестиционные решения."
    )
    image_path = 'https://botnest.ru/wp-content/uploads/2024/botnest/images/bot_money.webp'

    await query_message_photo(query, bot, text, image_path, rate_info)


@router.callback_query(F.data == 'get_rates')
async def get_rates(query: CallbackQuery, bot: Bot):
    time = timeit()

    rates = await get_currency_rates()
    specific_rates = extract_specific_rates(rates)
    response_text = f'<b>Курсы валют на {time}</b>:\n\n'
    response_text += f"Доллар США (USD): {specific_rates['USD']} руб.\n"
    response_text += f"Евро (EUR): {specific_rates['EUR']} руб.\n"
    response_text += f"Китайский юань (CNY): {specific_rates['CNY']} руб.\n"
    response_text += f"Японские йены (JPY): {specific_rates['JPY']} руб.\n"

    image_path = 'https://botnest.ru/wp-content/uploads/2024/botnest/images/bot_money.webp'

    await query_message_photo(query, bot, response_text, image_path, back)


@router.callback_query(F.data == 'get_crypto_rates')
async def get_crypto_rates(query: CallbackQuery, bot: Bot):
    time = timeit()

    rates = await crypto_rates()
    response_text = f'<b>Курсы криптовалют на {time}</b>:\n\n'
    response_text += f"Биткоин (BTC): ${rates['bitcoin']['usd']}\n"
    response_text += f"Ethereum (ETH): ${rates['ethereum']['usd']}\n"
    response_text += f"Рипл (XRP): ${rates['ripple']['usd']}\n"
    response_text += f"Litecoin (LTC): ${rates['litecoin']['usd']}\n"

    image_path = 'https://botnest.ru/wp-content/uploads/2024/botnest/images/bot_money.webp'

    await query_message_photo(query, bot, response_text, image_path, back)


@router.callback_query(F.data == 'get_stock_prices')
async def get_stock_prices(query: CallbackQuery, bot: Bot):
    time = timeit()

    stocks = {
        "Газпром": "GAZP",
        "Сбербанк": "SBER",
        "Ростелеком": "RTKM",
        "Роснефть": "ROSN"
    }
    response_text = f'<b>Котировки акций на {time}</b>:\n\n'
    for name, ticker in stocks.items():
        price = await get_stock_price(ticker)
        response_text += f"{name}: {price} RUB\n"

    image_path = 'https://botnest.ru/wp-content/uploads/2024/botnest/images/bot_money.webp'

    await query_message_photo(query, bot, response_text, image_path, back)
