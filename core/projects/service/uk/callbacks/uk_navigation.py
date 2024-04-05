from datetime import datetime
import asyncio

from aiogram import Router, F, Bot
from aiogram.enums import ChatType
from aiogram.types import Message, CallbackQuery

from core.callbacks.navigation import query_message_photo
from core.projects.service.uk.database.requests import Database
from core.projects.service.uk.filters.uk_filter import ChatTypeFilter
from core.projects.service.uk.keyboards.builders import uk_menu

router = Router()

db = Database()

ALLOWED_HASHTAGS = {
    '#авария': 'Авария устранена',
    '#жалоба': 'Жалоба рассмотрена и устранена',
    '#ремонт': 'Ремонт выполнен',
    '#предложение': 'Предложение принято к рассмотрению',
    '#уборка': 'Замечания по уборке устранены'
}


@router.callback_query(F.data == 'uk_main')
async def card_main(query: CallbackQuery, bot: Bot):
    text = (
        f"<b>🏢 УК/ТСЖ бот</b>\n\n"
        f"Представляем телеграм-бота для управления заявками в чат-группах УК и ТСЖ. Этот инструмент превращает "
        f"обычные чаты в мощные платформы для управления обращениями жителей. С его помощью можно легко подавать "
        f"и отслеживать заявки прямо в процессе общения, используя специальные хэштеги. Наш демонстрационный "
        f"проект показывает, как эффективно обрабатывать сообщения о авариях, ремонте, уборке и других обращениях,"
        f"делая процесс удобным и оперативным.\n\n"
        f"Посмотреть демонстрационную группу и узнать больше о возможностях таких ботов можно "
        f"перейдя по ссылке в сообщении.\n\n"
        f"Вдохновитесь примером и создайте собственный бот для вашего сообщества, реализуя любые идеи и задачи, "
        f"ограничиваясь только вашей фантазией."
    )
    image_path = 'https://botnest.ru/wp-content/uploads/2024/botnest/images/uk_logo.webp'

    await query_message_photo(query, bot, text, image_path, uk_menu)



@router.message(ChatTypeFilter(chat_type=["group", "supergroup"]))
async def handle_group_message(message: Message):
    if message.text.startswith("#"):
        hashtag, *description = message.text.split(maxsplit=1)
        if hashtag not in ALLOWED_HASHTAGS.keys():
            type_message = (
                "К сожалению, данного типа обращения не существует. "
                "Вот список доступных типов обращений:\n\n"
                "#авария - для срочных сообщений о происшествиях и авариях.\n"
                "#жалоба - для выражения недовольства качеством услуг.\n"
                "#ремонт - для заявок на проведение ремонтных работ.\n"
                "#предложение - для предложений по улучшению работы УК.\n"
                "#уборка - для замечаний и предложений по уборке."
            )
            error_message = await message.answer(type_message)

            await asyncio.sleep(30)
            await message.delete()
            await error_message.delete()
            return
        if not description:
            no_message = await message.answer("К сожалению, ваше обращение не содержит описания.")
            await asyncio.sleep(10)
            await message.delete()
            await no_message.delete()
            return

        description = " ".join(description)
        request_id = await db.add_request(message.from_user.id, description, hashtag[1:])

        # Ответ на сообщение с хэштегом
        response_msg = await message.answer(
            f"<b>Создана заявка №{request_id}</b>\n"
            f"<b>Типовая причина:</b> {hashtag[1:]}\n"
            f"<b>Описание:</b> {description}\n\n"
            f"Для уточнения статуса по заявке вы можете обратиться по телефону 85008008080"
        )

        # Имитация обработки заявки
        await asyncio.sleep(5)

        # Ответ после обработки заявки
        closing_response = ALLOWED_HASHTAGS[hashtag]
        closing_response_msg = await message.answer(
            f"<b>Заявка №{request_id} закрыта</b>\n"
            f"<b>Типовая причина:</b> {hashtag[1:]}\n"
            f"<b>Описание заявки:</b> {description}\n\n"
            f"<b>Ответ по заявке:</b> {closing_response}, время устранения {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}. "
            f"Спасибо за обращение в УК BotNest.\n\nЗаказать бота в телеграм: https://t.me/BotNestRu_bot"
        )

        # Удаление сообщений после задержки
        await asyncio.sleep(20)
        await message.delete()
        await response_msg.delete()
        await closing_response_msg.delete()
    else:
        welcome_message = (
            "чтобы протестировать возможности бота - используйте любой доступный хэштег:\n\n"
            "#авария - для срочных сообщений о происшествиях и авариях.\n"
            "#жалоба - для выражения недовольства качеством услуг.\n"
            "#ремонт - для заявок на проведение ремонтных работ.\n"
            "#предложение - для предложений по улучшению работы УК.\n"
            "#уборка - для замечаний и предложений по уборке.\n\n"
            f"Заказать бота в телеграм: https://t.me/BotNestRu_bot"

        )
        new_message = await message.answer(welcome_message)

        await asyncio.sleep(20)
        await message.delete()
        await new_message.delete()