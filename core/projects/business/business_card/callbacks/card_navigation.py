from core.callbacks.navigation import query_message_photo
from core.handlers.user_commands import *
from core.projects.business.business_card.keyboards.builders import *

router = Router()

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
        f"<b>🔍 О фирме фирма LawNest</b>\n\n"
        f"LawNest Solutions - инновационная юридическая фирма, предлагающая широкий спектр юридических услуг с помощью "
        f"передовых технологий. Наша миссия - обеспечить доступную и высококачественную юридическую помощь, "
        f"используя автоматизированные решения для повышения эффективности и доступности юридической поддержки."
    )
    image_path = 'https://botnest.ru/wp-content/uploads/2024/botnest/images/Lawnest.png?_t=1708012853'

    await query_message_photo(query, bot, text, image_path, card_main_menu)