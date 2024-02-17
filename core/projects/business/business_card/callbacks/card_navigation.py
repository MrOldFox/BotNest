from core.callbacks.navigation import query_message_photo, query_message_video, query_message
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


@router.callback_query(F.data == 'card_services')
async def card_services(query: CallbackQuery, bot: Bot):
    text = (
        f"<b>🖋 Наши услуги</b>\n\n"
        f"Наша юридическая фирма предоставляет следующие услуги:\n\n"
        f"🔹 Корпоративное право и M&A\n"
        f"🔹 Недвижимость и земельное право\n"
        f"🔹 Интеллектуальная собственность"
    )

    image_path = 'https://botnest.ru/wp-content/uploads/2024/botnest/lawnest/photo/services.png'

    await query_message_photo(query, bot, text, image_path, card_service)


@router.callback_query(F.data == 'card_service_m2a')
async def card_service_m2a(query: CallbackQuery, bot: Bot):
    text = (
        f"<b>🖋 Услуга корпоративное право и M&A</b>\n\n"
        f"<b>Что мы предлагаем?</b>\n\n"
        f"🔹 Консультации и сопровождение сделок слияния и поглощения\n"
        f"🔹 Стратегическое планирование корпоративного управления\n"
        f"🔹 Правовое решение корпоративных споров и конфликтов\n\n"
        f"<b>Для кого эта услуга?</b>\n\n"
        f"Идеально для компаний, ищущих расширение через M&A, и желающих укрепить свои корпоративные структуры."
    )

    image_path = 'https://botnest.ru/wp-content/uploads/2024/botnest/lawnest/photo/service_ma.png'

    await query_message_photo(query, bot, text, image_path, card_services_back)

@router.callback_query(F.data == 'card_service_estate')
async def card_service_estate(query: CallbackQuery, bot: Bot):
    text = (
        f"<b>🖋 Услуга недвижимость и земельное право</b>\n\n"
        f"<b>Что мы предлагаем?</b>\n\n"
        f"🔹 Юридическое сопровождение сделок с недвижимостью\n"
        f"🔹 Помощь в регистрации прав собственности и земельных участков\n"
        f"🔹 Решение споров по земельным вопросам и правам на недвижимость\n\n"
        f"<b>Для кого эта услуга?</b>\n\n"
        f"Идеально для застройщиков, владельцев недвижимости, инвесторов и арендаторов, "
        f"стремящихся защитить свои права и инвестиции в сфере недвижимости."
    )

    image_path = 'https://botnest.ru/wp-content/uploads/2024/botnest/lawnest/photo/service_estate.png'

    await query_message_photo(query, bot, text, image_path, card_services_back)


@router.callback_query(F.data == 'card_service_property')
async def card_service_property(query: CallbackQuery, bot: Bot):
    text = (
        f"<b>🖋 Услуга интеллектуальная собственность</b>\n\n"
        f"<b>Что мы предлагаем?</b>\n\n"
        f"🔹 Регистрация и защита интеллектуальной собственности (патенты, торговые марки, авторские права)\n"
        f"🔹 Помощь в решении споров по интеллектуальной собственности\n"
        f"🔹 Консультации по лицензированию и коммерциализации интеллектуальной собственности\n\n"
        f"<b>Для кого эта услуга?</b>\n\n"
        f"Идеально для изобретателей, авторов, владельцев брендов и компаний, "
        f"желающих эффективно управлять и защищать свои интеллектуальные активы."
    )

    image_path = 'https://botnest.ru/wp-content/uploads/2024/botnest/lawnest/photo/service_property.png'

    await query_message_photo(query, bot, text, image_path, card_services)


@router.callback_query(F.data == 'card_contacts')
async def card_contacts(query: CallbackQuery, bot: Bot):
    text = (
        f"<b>🌐 Контактная информация</b>\n\n"
        f"В LawNest мы всегда рады помочь вам с любыми юридическими вопросами. Наша команда экспертов доступна"
        f" для консультаций, предоставления информации о наших услугах и обсуждения вашего уникального случая.\n\n"
        f"Свяжитесь с нами, чтобы воспользоваться высококачественной юридической поддержкой.\n\n"
        f"📞 Телефон: +7 (800) 800 80 80\n"
        f"✉️ Email: info@botnest.ru\n"
        f"🌍 Веб-сайт: botnest.ru"
    )

    image_path = 'https://botnest.ru/wp-content/uploads/2024/botnest/lawnest/photo/card_contacts.png'

    await query_message_photo(query, bot, text, image_path, card_contact)

@router.callback_query(F.data == 'start_lawyer')
async def start_lawyer(query: CallbackQuery, bot: Bot):
    first_lawyer = await db.get_first_lawyer()  # Получаем первого юриста
    total_lawyers = await db.get_total_lawyers()  # Получаем общее количество юристов в базе данных

    # Используем ID первого юриста при создании клавиатуры
    keyboard = generate_lawyers_keyboard(first_lawyer.lawyer_id, total_lawyers)

    text = f"<b>Имя:</b> {first_lawyer.name}\n\n<b>Специализация:</b> {first_lawyer.specialisation}\n\n<b>Описание:</b> {first_lawyer.description}"

    if first_lawyer.photo_url:
        await query_message_photo(query, bot, text, first_lawyer.photo_url, keyboard, False)
    else:
        await query_message(query, bot, text, keyboard)


@router.callback_query(F.data.startswith("lawyer_"))
async def navigate_lawyers(query: CallbackQuery, bot: Bot):
    lawyer_id = int(query.data.split("_")[1])  # Извлекаем ID юриста из callback data
    lawyer = await db.get_lawyer_by_id(lawyer_id)
    total_lawyers = await db.get_total_lawyers()

    # Используем ID первого юриста при создании клавиатуры
    keyboard = generate_lawyers_keyboard(lawyer.lawyer_id, total_lawyers)

    text = f"<b>Имя:</b> {lawyer.name}\n\n<b>Специализация:</b> {lawyer.specialisation}\n\n<b>Описание:</b> {lawyer.description}"

    if lawyer.photo_url:
        await query_message_photo(query, bot, text, lawyer.photo_url, keyboard, False)
    else:
        await query_message(query, bot, text, keyboard)