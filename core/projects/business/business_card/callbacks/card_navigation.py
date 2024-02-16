from core.callbacks.navigation import query_message_photo, query_message_video
from core.handlers.user_commands import *
from core.projects.business.business_card.database.requests import Database
from core.projects.business.business_card.keyboards.builders import *

router = Router()

db = Database()

@router.callback_query(F.data == 'card_main')
async def card_main(query: CallbackQuery, bot: Bot):
    text = (
        f"<b>🔍 Юридическая фирма LawNest</b>\n\n"
        f"Наш чат-бот для юридической фирмы предназначен для демонстрации возможностей автоматизации "
        f"юридических услуг через Telegram.\n\nКлиенты могут легко получать информацию о предоставляемых услугах, "
        f"консультироваться по юридическим вопросам, записываться на прием к специалистам, "
        f"а также следить за последними новостями и обновлениями фирмы."
    )
    image_path = 'https://botnest.ru/wp-content/uploads/2024/botnest/images/Lawnest.png?_t=1708012853'

    await query_message_photo(query, bot, text, image_path, card_main_menu)


@router.callback_query(F.data == 'card_info')
async def card_main(query: CallbackQuery, bot: Bot):
    text = (
        f"<b>🔍 О фирме LawNest</b>\n\n"
        f"LawNest Solutions - инновационная юридическая фирма, предлагающая широкий спектр юридических услуг с помощью "
        f"передовых технологий.\n\nНаша миссия - обеспечить доступную и высококачественную юридическую помощь, "
        f"используя автоматизированные решения для повышения эффективности и доступности юридической поддержки."
    )
    video_path = 'https://botnest.ru/wp-content/uploads/2024/botnest/video/video_law_nest.mp4'

    await query_message_video(query, bot, text, video_path, card_about_us)


@router.callback_query(F.data == 'start_lawyer')
async def start_lawyer(query: CallbackQuery, bot: Bot):
    first_lawyer = await db.get_first_lawyer()  # Получаем первого юриста
    total_lawyers = await db.get_total_lawyers()  # Получаем общее количество юристов в базе данных

    # Используем ID первого юриста при создании клавиатуры
    keyboard = generate_lawyers_keyboard(first_lawyer.lawyer_id, total_lawyers)

    text = f"<b>Имя:</b> {first_lawyer.name}\n\n<b>Специализация:</b> {first_lawyer.specialisation}\n\n<b>Описание:</b> {first_lawyer.description}"

    # if first_lawyer.photo_url:
    #     await query.message.answer_photo(
    #         photo=first_lawyer.photo_url,
    #         caption=text,
    #         reply_markup=keyboard
    #     )
    # else:
    #     await query.message.answer(
    #         text=text,
    #         reply_markup=keyboard
    #     )
    # await query.answer()

    await query_message_photo(query, bot, text, first_lawyer.photo_url, keyboard, False)


@router.callback_query(F.data.startswith("lawyer_"))
async def navigate_lawyers(query: CallbackQuery, bot: Bot):
    lawyer_id = int(query.data.split("_")[1])  # Извлекаем ID юриста из callback data
    lawyer = await db.get_lawyer_by_id(lawyer_id)
    total_lawyers = await db.get_total_lawyers()

    # Используем ID первого юриста при создании клавиатуры
    keyboard = generate_lawyers_keyboard(lawyer.lawyer_id, total_lawyers)

    text = f"<b>Имя:</b> {lawyer.name}\n\n<b>Специализация:</b> {lawyer.specialisation}\n\n<b>Описание:</b> {lawyer.description}"

    await query_message_photo(query, bot, text, lawyer.photo_url, keyboard, False)