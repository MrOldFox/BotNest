import asyncio
import logging
from datetime import datetime

from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from sqlalchemy import update

from config_reader import config
from core.database.models import async_main, async_session, User

from core.handlers import bot_messages, user_commands
from core.callbacks import pagination, navigation, order
from core.projects.ai.callbacks import ai_assistant, ai_navigation
from core.projects.business.business_card.callbacks import card_navigation
from core.projects.business.subscribe_bot.callbacks import sub_navigation
from core.projects.games.lostorder.callbacks import rolldice
from core.projects.games.lostorder.handlers import gamenavigation
from core.projects.info.business_info.callbacks import info_navigation
from core.projects.service.uk.callbacks import uk_navigation
from core.projects.service.voice2text.callbacks import v2t_navigation
from core.projects.business.shops.callbacks import shop_navigation
from core.utils.commands import set_commands


async def main():
    await async_main()
    bot = Bot(config.bot_token.get_secret_value(), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # Установка команд бота
    await set_commands(bot)

    logging.basicConfig(level=logging.INFO)

    dp.include_routers(
        user_commands.router,
        pagination.router,
        navigation.router,
        bot_messages.router,
        order.router,
        gamenavigation.router,
        rolldice.router,
        ai_assistant.router,
        uk_navigation.router,
        ai_navigation.router,
        info_navigation.router,
        shop_navigation.router,
        v2t_navigation.router,
        sub_navigation.router,
        card_navigation.router
    )

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
