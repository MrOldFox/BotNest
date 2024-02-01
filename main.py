import json
import asyncio
import logging

from aiogram import Bot, Dispatcher, Router

from config_reader import config
from core.database.models import async_main

from core.handlers import bot_messages, user_commands
from core.callbacks import pagination, navigation, order
from core.projects.AI.callbacks import ai_assistant, ai_navigation
from core.projects.games.lostorder.callbacks import rolldice
from core.projects.games.lostorder.handlers import gamenavigation
from core.projects.info.business_info.callbacks import info_navigation

from core.webhook.server import *

async def main():
    await async_main()
    bot = Bot(config.bot_token.get_secret_value(), parse_mode="HTML")
    dp = Dispatcher()

    # Создание роутера
    router = Router()

    logging.basicConfig(level=logging.INFO)

    # Добавление middleware к роутеру
    # dp.message.outer_middleware(AutoDeleteMiddleware())
    # dp.callback_query.outer_middleware(AutoDeleteMiddleware())

    dp.include_routers(
        user_commands.router,
        pagination.router,
        navigation.router,
        bot_messages.router,
        order.router,
        gamenavigation.router,
        rolldice.router,
        ai_assistant.router,
        ai_navigation.router,
        info_navigation.router,
    )

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
