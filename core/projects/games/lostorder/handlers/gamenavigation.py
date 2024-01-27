
import asyncio

from aiogram import Router, F, Bot
from aiogram.filters import or_f, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message

from core.handlers.callback import *
from core.projects.games.lostorder.callbacks.gamefunctions import choose_path
from core.projects.games.lostorder.callbacks.rolldice import *
from core.projects.games.lostorder.keyboards.builder import *


# Определение состояний
class GameStates(StatesGroup):
    DiceRoll = State()
    Introduction = State()
    ChoosingPath = State()
    Forest = State()
    ForestBattle = State()
    ExploringRiver = State()
    Encounter = State()
    Village = State()

class CombatStates(StatesGroup):
    RollingForAttack = State()  # Бросок кубика для атаки
    RollingForDefense = State()  # Бросок кубика для защиты
    EnemyAttack = State()  # Бросок кубика для атаки врага

router = Router()



# Начало игры
@router.callback_query(F.data == 'lost_order')
async def start_game(query: CallbackQuery, state: FSMContext, bot: Bot):
    await state.set_state(GameStates.Introduction)
    text = (
        "<b>Легенда Потерянного Ордена</b> \n\n"
        "Ты - отважный рыцарь, последний защитник своего обесчещенного ордена.\n\n"
        "После долгих лет борьбы и скитаний ты отправляешься в путешествие, чтобы открыть "
        "для себя древние тайны и восстановить честь ордена."
        "Твой путь начинается у края известного мира, на перекрестке древних дорог...\n\n"
        "<i>Данная игра создана для демонстрации возможностей при создании игровых ботов.\n\n"
        "Механики:\nПри броске кубиков успешным результатом считается все цифры больше 3</i>"
    )

    # Путь к изображению или URL
    image_path = 'https://botnest.ru/wp-content/uploads/2024/game/lostorder/gamelogo.jpg'

    # Отправка изображения с подписью и инлайн-клавиатурой
    sent_message = await query.bot.send_photo(
        query.message.chat.id,
        photo=image_path,  # Или просто строка с URL изображения
        caption=text,
        reply_markup=inline_builder(StartGame)
    )

    # Вызов функции update_last_message
    await update_last_message_id(bot, sent_message.message_id, query.from_user.id)


# 1 сцена
@router.callback_query(F.data == 'start_game')
async def start_game(query: CallbackQuery, state: FSMContext, bot: Bot):
    await state.set_state(GameStates.Introduction)
    text = (
        "Ты стоишь на древнем распутье, где судьбы разделяются.\n"
        "С одной стороны, путь уводит в густой, таинственный лес, где между деревьями играют тени,"
        "и сквозь листву едва пробивается свет. Эти темные заросли хранят древние секреты и неизведанные опасности.\n\n"
        "С другой стороны, тихая река манит своим спокойствием, сверкая под солнечными лучами.\n"
        "Вдоль её берегов вьются извилистые тропы, и ты можешь слышать далекий шум водопада.\n"
        "Но даже здесь, в этом мирном месте, могут таиться свои тайны.\n\n"
        "Какой путь ты выберешь, рыцарь? Через таинственный лес или вдоль спокойной реки?"
    )

    # Путь к изображению или URL
    image_path = 'https://botnest.ru/wp-content/uploads/2024/game/lostorder/path.jpg'

    # Отправка изображения с подписью и инлайн-клавиатурой
    sent_message = await query.bot.send_photo(
        query.message.chat.id,
        photo=image_path,  # Или просто строка с URL изображения
        caption=text,
        reply_markup=inline_builder(ChoosingPath)
    )

    # Вызов функции update_last_message
    await update_last_message_id(bot, sent_message.message_id, query.from_user.id)


# Сцена при выборе леса
@router.callback_query(F.data == 'forest')
async def start_game(query: CallbackQuery, state: FSMContext, bot: Bot):
    await state.set_state(GameStates.Forest)
    text = (
        "Проходя через лес, ты чувствуешь, что не один, ты слышишь звук раздвигаемых ветвей "
        "и замечаешь как что-то высится над деревьями...\n\n"
        "<i>Брось кубик, чтобы узнать, удастся ли тебе вовремя определить что это.</i>"
    )

    # Путь к изображению или URL
    image_path = 'https://botnest.ru/wp-content/uploads/2024/game/lostorder/foresttreat.jpg'

    # Отправка изображения с подписью и инлайн-клавиатурой
    sent_message = await query.bot.send_photo(
        query.message.chat.id,
        photo=image_path,  # Или просто строка с URL изображения
        caption=text,
        reply_markup=inline_builder(RollDice)
    )
    await query.answer()
    # Вызов функции update_last_message
    await update_last_message_id(bot, sent_message.message_id, query.from_user.id)


@router.callback_query(GameStates.Forest, F.data == 'dice')
async def order(query: CallbackQuery, state: FSMContext, bot: Bot):
    dice_message = await query.message.answer_dice()

    dice_value = dice_message.dice.value
    success = await check_dice_result(dice_value)

    image_path1 = 'https://botnest.ru/wp-content/uploads/2024/game/lostorder/sneak.jpg'
    image_path2 = 'https://botnest.ru/wp-content/uploads/2024/game/lostorder/atack.jpg'

    if success:
        text = f"Результат: {dice_value}, Успех!\n\nВнимательно осматриваясь, ты " \
               "замечаешь <b>Теневого Рыскателя</b> и осторожно обходишь его."

        sent_message = await choose_path(text, image_path1, query, ToVillage)
    else:
        text = f"Результат: {dice_value}, Недача...\n\nТени леса внезапно сгущаются, и из их глубины, " \
               "там, где свет солнца не проникает, возникает существо, как будто" \
               " сотканное из самой тьмы. Оно стоит неподвижно, лишь глаза его горят " \
               "холодным огнем в полумраке. <b>Теневой Рыскатель</b>.\n\n" \
               "Начинается битва. <i>Брось кубик для атаки <b>Теневого Рыскателя</b></i>."

        sent_message = await choose_path(text, image_path2, query, RollDice)
        await state.set_state(GameStates.ForestBattle)

    await query.answer()
    await update_last_message_id(bot, sent_message.message_id, query.from_user.id)


@router.callback_query(GameStates.ForestBattle, F.data == 'dice')
async def start_combat(query: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    message = await query.message.answer_dice()
    dice_value = message.dice.value
    success = await check_dice_result(dice_value)

    image_path1 = 'https://botnest.ru/wp-content/uploads/2024/game/lostorder/success_atack.jpg'
    image_path2 = 'https://botnest.ru/wp-content/uploads/2024/game/lostorder/atack.jpg'

    if success:
        text = f"Результат: {dice_value}, Успех\n\nТвой меч находит свою цель! Теневой Рыскатель ранен и скрывается " \
               f"в ближайшей тени деревьев."

        sent_message = await choose_path(text, image_path1, query, ToVillage)
        await state.set_state(GameStates.Village)
    else:
        await state.set_state(CombatStates.EnemyAttack)
        text = f"Результат: {dice_value}, Недача...\n\nТвой удар прошел мимо! Теневой Рыскатель уклоняется.\n\n" \
               f"<i>Теневой Рыскатель готовится к контратаке!</i>"

        sent_message = await choose_path(text, image_path2, query, EnemyAttack)
        await state.set_state(CombatStates.EnemyAttack)

    await update_last_message_id(bot, sent_message.message_id, query.from_user.id)


@router.callback_query(CombatStates.EnemyAttack, F.data == 'defense')
async def player_attack(query: CallbackQuery, state: FSMContext, bot: Bot):
    await state.set_state(CombatStates.RollingForDefense)
    enemy_attack_value = randint(1, 5)
    await state.update_data(enemy_attack_value=enemy_attack_value)
    text = (
        f"Внезапно тени вокруг оживают, и Теневой Рыскатель, словно поток темной энергии, "
        f"молниеносно мчится к тебе. Его длинные, изящные конечности вытягиваются вперед, "
        f"стремясь нанести удар.\n\n В последнюю долю секунды, когда его пальцы, острые как бритвы, "
        f"уже почти касаются твоей брони, ты понимаешь, что если не уклониться ты "
        f"получаешь <b>{enemy_attack_value}</b> очка урона."
        f"\n\n<i>Бросьте кубик больше чем на <b>{enemy_attack_value}</b>, чтобы попробовать уклониться.</i>"
    )

    # Путь к изображению или URL
    image_path = 'https://botnest.ru/wp-content/uploads/2024/game/lostorder/atack.jpg'

    # Отправка изображения с подписью и инлайн-клавиатурой
    sent_message = await choose_path(text, image_path, query, RollDice)

    await query.answer()
    await update_last_message_id(bot, sent_message.message_id, query.from_user.id)


@router.callback_query(CombatStates.RollingForDefense, F.data == 'dice')
async def defense(query: CallbackQuery, state: FSMContext, bot: Bot):
    message = await query.message.answer_dice()
    await asyncio.sleep(4)
    data = await state.get_data()
    enemy_attack_value = data.get('enemy_attack_value')
    dice_value = message.dice.value

    image_path1 = 'https://botnest.ru/wp-content/uploads/2024/game/lostorder/success_atack.jpg'
    image_path2 = 'https://botnest.ru/wp-content/uploads/2024/game/lostorder/lost.jpg'

    if dice_value > enemy_attack_value:
        text = f"Результат: {dice_value}, Успех\n\nТы успешно защищаешься от атаки врага! И пока Теневой Рыскатель " \
               f"пытается понять что произошло - вам удается спрятаться за ближайшим деревом."

        sent_message = await choose_path(text, image_path1, query, ToVillage)
    else:
        text = f"Результат: {dice_value}, Недача...\n\nТеневой Рыскатель пробивает твою защиту и наносит урон!\n" \
               f"К сожалению вы сильно ранены и не можете продолжать путешествие. " \
               f"Ваш единственный шанс это сбежать и восстановить свои силы\n\n" \
               f"К сожалению это конец вашей истории о далеких приключениях..."

        sent_message = await choose_path(text, image_path2, query, Quit)
        await state.set_state(CombatStates.RollingForDefense)

    await query.answer()
    await update_last_message_id(bot, sent_message.message_id, query.from_user.id)


# Сцена при выборе леса
@router.callback_query(F.data == 'river')
async def exploring_river(query: CallbackQuery, state: FSMContext, bot: Bot):
    await state.set_state(GameStates.Encounter)
    text = (
        "Ты выбираешь путь вдоль реки. На поверхности еле виднеется "
        "небольшая рябь и всю ее площадь покрывает слабый туман, "
        "мягкое журчание воды успокаивает твоё сердце. Ты следуешь по берегу, "
        "наслаждаясь спокойствием и красотой окружающей природы. \n\nНо твоё чутьё подсказывает, "
        "что эта идиллия может быть обманчива. Впереди ты видишь кого-то, кто внимательно изучает реку."
    )

    image_path = 'https://botnest.ru/wp-content/uploads/2024/game/lostorder/scene3%28river%29.jpg?_t=170439394'

    sent_message = await choose_path(text, image_path, query, RiverEncounter)

    await query.answer()
    await update_last_message_id(bot, sent_message.message_id, query.from_user.id)


# Сцена при выборе леса
@router.callback_query(GameStates.Encounter, F.data == 'start_encounter')
async def exploring_river(query: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    await state.set_state(GameStates.DiceRoll)
    text = (
        "Ты подходишь к рыбаку и замечаешь его измученный вид. Он кажется встревоженным и истощенным, "
        "как будто провел несколько последних дней, борясь с невидимым врагом. На твой вопрос о деревне, "
        "он вздрагивает и мимолетно скользит взглядом по окрестностям, словно опасаясь, что его могут услышать.\n\n "
        "«Я... я не знаю, что это было», — произносит он шепотом, "
        "перед тем как быстро добавить: \n«Оно пришло ночью... и после... все изменилось. "
        "Или оно было там всегда..."
        "Лучше вам туда не идти».\n\nОн отворачивается, пытаясь скрыть своё беспокойство, но ты видишь, "
        "что этот человек пережил что-то ужасное."
    )

    # Путь к изображению или URL
    image_path = 'https://botnest.ru/wp-content/uploads/2024/game/lostorder/scene3%28encounter%29.jpg?_t=1704393223'

    sent_message = await choose_path(text, image_path, query, ToVillage)

    await query.answer()
    await update_last_message_id(bot, sent_message.message_id, query.from_user.id)


@router.callback_query(F.data == 'village')
async def exploring_river(query: CallbackQuery, state: FSMContext, bot: Bot):
    await state.set_state(GameStates.DiceRoll)
    text = (
        "Ты продвигаешь дальше, пока не обнаруживаешь заброшенную деревню.\n\n"
        "Пустые дома с распахнутыми дверьми и "
        "окнами кажутся призрачными, и в воздухе витает ощущение недавней суеты. На земле видны следы, "
        "свидетельствующие о том, что люди покинули деревню в спешке.\n\n"
        "<i>Вы можете создать будущее этой истории для своего бота или получить игру в своем жанре и своем формате\n"
        "Вы можете заказать своего бота по ссылке ниже или связаться с нами напрямую</i>"
    )

    # Путь к изображению или URL
    image_path = 'https://botnest.ru/wp-content/uploads/2024/game/lostorder/village.jpg?_t=1704394409'

    sent_message = await choose_path(text, image_path, query, VillagePath)

    await query.answer()
    await update_last_message_id(bot, sent_message.message_id, query.from_user.id)