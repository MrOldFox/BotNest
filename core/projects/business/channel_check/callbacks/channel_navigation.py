from core.callbacks.navigation import query_message_photo, query_message_video, query_message
from core.handlers.user_commands import *
from core.projects.business.business_card.database.requests import Database
from core.projects.business.business_card.keyboards.builders import *
from core.projects.business.channel_check.keyboards.builders import sub_channel_main, nosub_channel_main
import asyncio

router = Router()



@router.callback_query(F.data == 'channel_main')
async def channel_main(query: CallbackQuery, bot: Bot):
    telegram_id = query.from_user.id

    is_subscribed = await check_user_subscription(bot, telegram_id, '-1002114150805')


    subscription_active = is_subscribed if is_subscribed else False


    # Текст сообщения в зависимости от статуса подписки
    if subscription_active:
        status_text = "🟢 Ваша подписка активна"
    else:
        status_text = "🔴 У вас нет активной подписки на канал"

    image = 'https://botnest.ru/wp-content/uploads/2024/botnest/images/fitnest.webp'

    text = (
        f"🌟 <b>Добро пожаловать в FitNest!</b>\n\n"
        f"Откройте для себя новый уровень фитнеса с нашими персонализированными программами тренировок и советами по питанию. 🚀\n\n"
        f"Присоединяйтесь к нашему каналу, чтобы получить доступ ко всем функциям бота.\n\n"
        f"{status_text}\n\n"
        f"<i>Этот бот создан для демонстрации возможностей Telegram "
        f"в создании ботов, которые помогут вам увеличить подписчиков в ваших телеграм группах или каналах</i>"
    )

    if subscription_active:
        await query_message_photo(query, bot, text, image, sub_channel_main)
    else:
        await query_message_photo(query, bot, text, image, nosub_channel_main)


@router.callback_query(F.data == 'check_channel')
async def channel_check(query: CallbackQuery, bot: Bot):
    telegram_id = query.from_user.id

    is_subscribed = await check_user_subscription(bot, telegram_id, '-1002114150805')

    subscription_active = is_subscribed if is_subscribed else False


    # Текст сообщения в зависимости от статуса подписки
    if subscription_active:
        await channel_main(query, bot)
    else:
        sent_message = await query.message.answer(
            text="🔴 У вас нет активной подписки на канал"
        )
        await query.answer()
        await asyncio.sleep(3)
        await sent_message.delete()



async def check_user_subscription(bot: Bot, user_id: int, channel_id: str) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
        # Пользователь считается подписанным, если его статус не 'left' и не 'kicked'
        return member.status not in ['left', 'kicked', 'creator']
    except Exception as e:
        print(f"Ошибка при проверке подписки: {e}")
        return False
