from aiogram import types
from aiogram.types import LabeledPrice, PreCheckoutQuery

from core.callbacks.navigation import *
from core.handlers.user_commands import *
from core.projects.business.shops.keyboards.builders import *

image_main = 'https://botnest.ru/wp-content/uploads/2024/botnest/shop/photo/shop.webp'

router = Router()

@router.callback_query(F.data == 'shop_main')
async def shop_main(query: CallbackQuery, bot: Bot):
    text = (
        "<b>📲 Магазин телефонов MobileNest</b> \n\n"
        "Наш чат-бот для магазина телефонов позволяет клиентам легко и быстро находить интересующие их модели телефонов,"
        " получать подробную информацию о продуктах, проверять наличие товара на складе и даже совершать покупки прямо "
        "через Telegram.\n\nАвтоматизация процесса заказа сокращает время на покупку и повышает удовлетворенность клиентов."
    )
    image_path = image_main

    await query_message_photo(query, bot, text, image_path, shop_info)


@router.callback_query(F.data == 'order_history')
async def order_history(query: CallbackQuery, bot: Bot):
    user_id = query.from_user.id  # Получаем ID пользователя из сообщения

    # Проверяем, есть ли у пользователя покупки
    user_purchases = await db.get_user_purchases(user_id)
    if not user_purchases:
        # Если покупок нет, отправляем алерт
        await query.answer("Вы ещё не совершали покупок.", show_alert=True)
        return

    # Если покупки есть, продолжаем генерацию клавиатуры и отправку сообщения
    purchase_keyboard = await generate_purchase_keyboard(user_id)  # Генерируем клавиатуру для покупок пользователя

    text = "Выберите из списка ниже нужную покупку для полной детализации:"
    image_path = image_main

    await query_message_photo(query, bot, text, image_path, purchase_keyboard)


@router.callback_query(F.data == 'get_categories')
async def get_categories(query: CallbackQuery, bot: Bot):  # Создание экземпляра класса для работы с БД
    category_menu = await get_categories_menu()

    text = (
        "<b>Выберите категорию товара:</b>"
    )

    image_path = image_main

    await query_message_photo(query, bot, text, image_path, category_menu)


@router.callback_query(F.data.startswith("page_"))
async def paginate_categories(query: CallbackQuery, bot: Bot):
    # Извлекаем номер страницы из callback_data
    print(query.data)
    page = int(query.data.split('_')[1])

    # Получаем обновленное меню категорий и кнопки пагинации
    category_menu = await get_categories_menu(page=page)

    # Обновляем сообщение с новым списком категорий и кнопками пагинации
    text = "<b>Выберите категорию товара:</b>"
    image_path = image_main

    await query_message_photo(query, bot, text, image_path, category_menu)
    await query.answer()




@router.callback_query(F.data.startswith("brand_"))
async def show_products_by_brand(query: CallbackQuery, bot: Bot):
    data_parts = query.data.split('_')
    if len(data_parts) == 3:
        # Если callback_data содержит три части, значит это формат "brand_{brand_slug}_{page}"
        _, brand_slug, str_page = data_parts
        page = int(str_page)
    elif len(data_parts) == 2:
        # Если callback_data содержит две части, значит это формат "brand_{brand_slug}", и используется первая страница
        _, brand_slug = data_parts
        page = 0
    else:
        # Неожиданный формат callback_data
        await query.answer("Произошла ошибка, попробуйте ещё раз.", show_alert=True)
        return

    # Получаем photo_url для данного brand_slug
    photo_url = await db.get_brand_photo_url_by_slug(brand_slug)
    if not photo_url:
        photo_url = "https://botnest.ru/wp-content/uploads/2024/botnest/shop/photo/shop.webp"


    products_menu = await get_products_by_brand_menu(brand_slug, page)


    text = f"<b>Продукты бренда:</b>"

    await query_message_photo(query, bot, text, photo_url, products_menu)
    await query.answer()


@router.callback_query(F.data.startswith("color_"))
async def show_products_by_color(query: CallbackQuery, bot: Bot):
    data_parts = query.data.split('_')
    if len(data_parts) == 4:
        # Если callback_data содержит три части, значит это формат "brand_{brand_slug}_{page}"
        _, product_name, brand_slug, str_page = data_parts
        page = int(str_page)
    elif len(data_parts) == 3:
        # Если callback_data содержит две части, значит это формат "brand_{brand_slug}", и используется первая страница
        _, product_name, brand_slug = data_parts
        page = 0
    else:
        # Неожиданный формат callback_data
        await query.answer("Произошла ошибка, попробуйте ещё раз.", show_alert=True)
        return

    products_menu = await get_products_by_color(product_name, brand_slug)


    text = f"<b>Выберите цвет продукта:</b>"

    await query_message_photo(query, bot, text, "https://botnest.ru/wp-content/uploads/2024/botnest/shop/photo/apple-logo.jpg", products_menu)
    await query.answer()



@router.callback_query(F.data == "checkout")
async def checkout(query: CallbackQuery, bot: Bot):
    user_id = query.from_user.id

    # Получаем товары из корзины пользователя
    cart_items = await db.get_checkout_items(user_id)
    if not cart_items:
        await query.answer("Ваша корзина пуста.", show_alert=True)
        return

    # Составляем список цен для инвойса
    prices = []
    for cart_item, product_name, stock_quantity, price, color in cart_items:
        label = f"{product_name} ({color}) x {cart_item.quantity}"
        amount = int(price) * 100 * cart_item.quantity  # Преобразование в целое число и умножение на 100
        print(amount)
        prices.append(LabeledPrice(label=label, amount=amount))

    total_amount = sum(price.amount for price in prices)  # Общая сумма в копейках
    print(prices)
    # Проверяем, не превышает ли общая сумма максимально допустимый порог
    max_amount = 25000000  # Максимальная сумма в копейках (250 000 рублей)
    if total_amount > max_amount:
        await query.answer(f"Сумма покупки не может превышать 250 000 рублей. Ваша сумма составляет {total_amount / 100} рублей.", show_alert=True)
        return

    # Добавляем фото первого товара в инвойсе для наглядности (если доступно)
    first_item_photo_url = 'https://botnest.ru/wp-content/uploads/2024/botnest/shop/photo/pay.png?_t=1707660307'

    text = (f'\nДля проведения пробной покупки используйте данные тестовой карты:'\
            f'\n\nНомер карты: 1111 1111 1111 1026,'\
            f'\nДата выпуска: 12/22,'\
            f'\nCVC: 000\n')
    # Отправляем инвойс пользователю
    send_message = await bot.send_invoice(
        chat_id=query.message.chat.id,
        title='Оплата товаров из корзины',
        description=text,
        payload='Test payment',
        provider_token='381764678:TEST:73182',  # Токен платежного провайдера
        currency='rub',
        prices=prices,
        need_name=True,
        need_phone_number=True,
        need_shipping_address=True,
        need_email=True,
        start_parameter='botnest',
        send_email_to_provider=False,
        send_phone_number_to_provider=False,
        provider_data=None,
        photo_url=first_item_photo_url,
        protect_content=False,
        reply_markup=inline_builder(shop_back),
        allow_sending_without_reply=True,
    )

    await update_last_message_id(bot, send_message.message_id, query.from_user.id)
    await query.answer()

@router.pre_checkout_query()
async def pre_checkout_query(pre_checkout_query: PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
    print('ok')

@router.message(F.successful_payment)
async def successful_payment(message: Message, bot: Bot):
    telegram_id = message.from_user.id

    user_id = message.from_user.id

    # Шаг 1: Получаем товары из корзины пользователя
    cart_items = await db.get_checkout_items(user_id)
    if cart_items:
        # Шаг 2: Добавляем запись в PurchaseHistory
        total_amount = message.successful_payment.total_amount / 100  # Telegram возвращает сумму в копейках
        purchase_id = await db.add_purchase_history(user_id, total_amount, cart_items)

        # Шаг 3: Для каждого товара из корзины добавляем запись в PurchaseDetail
        for cart_item, product_name, stock_quantity, price, color in cart_items:
            await db.add_purchase_detail(purchase_id, cart_item.product_id, cart_item.quantity, price)

    await db.clear_user_cart(user_id)

    text = (
        f"<b>💬 Успешно!</b> \n\n"
        f"Вы успешно получили пробную оплату товара, при этом вы потратили {message.successful_payment.total_amount // 100} виртуальных {message.successful_payment.currency}.\n\n"
        f"Если хотите получить такой же бот, то можете подать заявку ниже."
    )
    image_path = 'https://botnest.ru/wp-content/uploads/2024/botnest/shop/photo/pay.png?_t=1707660307'
    sent_message = await bot.send_photo(
        message.chat.id,
        photo=image_path,  # Или просто строка с URL изображения
        caption=text,
        reply_markup=inline_builder(buy)
    )
    await update_last_message_id(bot, sent_message.message_id, telegram_id)


@router.callback_query(F.data.startswith("search"))
async def increase_cart_item_quantity(query: CallbackQuery, bot: Bot):
    await query.answer(
        f"Функция в разработке",
        show_alert=True)

@router.callback_query(F.data == "view_cart")
async def view_cart(query: CallbackQuery, bot: Bot):
    user_id = query.from_user.id  # Получаем ID пользователя
    cart_items = await db.get_cart_items(user_id)  # Предполагается, что эта функция теперь также возвращает цену каждого товара
    if not cart_items:
        await query.answer("Ваша корзина пуста.", show_alert=True)
        return

    text = "В вашей корзине следующие товары:\n\n"
    total_price = 0  # Для подсчета общей стоимости товаров в корзине

    # Используем enumerate для получения индекса каждого элемента
    for index, (cart_item, product_name, stock_quantity, price, color) in enumerate(cart_items, start=1):
        item_total_price = cart_item.quantity * price  # Стоимость данного товара в корзине
        text += f"{index}) {product_name} ({color}) - {cart_item.quantity} шт. ({item_total_price} руб.)\n"
        total_price += item_total_price  # Добавляем стоимость товара к общей стоимости корзины

    text += f"\nОбщая стоимость: {total_price} руб."

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[])

    for index, (cart_item, product_name, stock_quantity, color, _) in enumerate(cart_items, start=1):
        buttons_row = [
            types.InlineKeyboardButton(text="<-", callback_data=f"cart_decrease_{cart_item.cart_id}_{cart_item.quantity}"),
            types.InlineKeyboardButton(text=f"{index}", callback_data="noop"),  # Используем индекс как номер позиции
            types.InlineKeyboardButton(text="->", callback_data=f"cart_increase_{cart_item.cart_id}_{cart_item.quantity}_{stock_quantity}")
        ]
        # Добавляем список кнопок как новую строку в inline_keyboard
        keyboard.inline_keyboard.append(buttons_row)
    # После добавления всех товаров в клавиатуру добавляем кнопку "Купить"
    keyboard.inline_keyboard.append([
        types.InlineKeyboardButton(text="Купить", callback_data="checkout")
    ])

    # Добавляем кнопку "Назад"
    keyboard.inline_keyboard.append([
        types.InlineKeyboardButton(text="Назад", callback_data="shop_main")
    ])

    image_path = 'https://botnest.ru/wp-content/uploads/2024/botnest/shop/photo/pay.png?_t=1707660307'

    send_message = await query.bot.send_photo(query.message.chat.id, photo=image_path, caption=text, reply_markup=keyboard)
    await update_last_message_id(bot, send_message.message_id, query.from_user.id)


@router.callback_query(F.data.startswith("cart_increase_"))
async def increase_cart_item_quantity(query: CallbackQuery, bot: Bot):
    # Предполагаем, что callback_data имеет вид "cart_increase_cart_id_current_quantity_stock_quantity"
    data_parts = query.data.split('_')
    if len(data_parts) != 5:
        await query.answer("Произошла ошибка. Неверный формат данных.", show_alert=True)
        return

    _, cart_id, current_quantity, stock_quantity = data_parts[1], int(data_parts[2]), int(data_parts[3]), int(data_parts[4])

    if current_quantity < stock_quantity:
        # Увеличиваем количество товара в корзине
        await db.update_cart_item_quantity(cart_id, current_quantity + 1)
    else:
        await query.answer("Нельзя добавить больше доступного количества.", show_alert=True)

    await view_cart(query, bot)  # Обновляем содержимое корзины


@router.callback_query(F.data.startswith("cart_decrease_"))
async def decrease_cart_item_quantity(query: CallbackQuery, bot: Bot):
    data_parts = query.data.split('_')
    if len(data_parts) >= 4:
        _, cart_id_str, current_quantity_str = data_parts[1:4]
        try:
            cart_id = int(cart_id_str)
            current_quantity = int(current_quantity_str)

            if current_quantity > 1:
                await db.update_cart_item_quantity(cart_id, current_quantity - 1)
            else:
                await db.remove_item_from_cart(cart_id)
                # Проверяем, остались ли ещё элементы в корзине после удаления
                remaining_items = await db.get_cart_items(query.from_user.id)
                if not remaining_items:
                    # Если элементов не осталось, возвращаем пользователя в меню
                    await query.answer("Ваша корзина теперь пуста. Возвращаем вас в меню.")
                    await shop_main(query, bot)  # Предположим, что у вас есть функция show_main_menu для отображения главного меню
                    return

            await view_cart(query, bot)  # Обновляем содержимое корзины
        except ValueError:
            await query.answer("Произошла ошибка при обработке запроса.", show_alert=True)
    else:
        await query.answer("Произошла ошибка при обработке запроса.", show_alert=True)


@router.callback_query(F.data.startswith("add_"))
async def add_to_cart(query: CallbackQuery, bot: Bot):
    _, product_id, quantity, telegram_id, product_name = query.data.split('_')
    product_id = int(product_id)
    quantity = int(quantity)
    telegram_id = int(telegram_id)

    # Вызываем функцию добавления в корзину и получаем результат
    result_message = await db.add_item_to_cart(telegram_id, product_id, quantity)

    # Отправляем результат пользователю
    await query.answer(result_message, show_alert=True)


def get_product_keyboard(product_id: int, quantity: int, brand_slug: str, telegram_id: int, product_name: str):
    buttons = [
        [
            types.InlineKeyboardButton(text="⬇️", callback_data=f"decrease_{product_id}_{quantity}_{telegram_id}_{product_name}"),
            types.InlineKeyboardButton(text=f"🛒 +{quantity}", callback_data=f"add_{product_id}_{quantity}_{telegram_id}_{product_name}"),
            types.InlineKeyboardButton(text="⬆️", callback_data=f"increase_{product_id}_{quantity}_{telegram_id}_{product_name}")
        ],
            [types.InlineKeyboardButton(text="Корзина", callback_data='view_cart')],
            [types.InlineKeyboardButton(text="Назад", callback_data=f"color_{product_name}_{brand_slug}")]

        ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)

    return keyboard


@router.callback_query(or_f(F.data.startswith("increase_"), F.data.startswith("decrease_")))
async def change_quantity(query: CallbackQuery, bot: Bot):
    action, product_id, quantity, telegram_id, product_name = query.data.split('_')
    product_id = int(product_id)
    quantity = int(quantity)
    telegram_id = int(telegram_id)
    product_name = str(product_name)

    # Получаем информацию о продукте из базы данных
    product = await db.get_product_by_id(product_id)
    if not product:
        await query.answer("Продукт не найден.", show_alert=True)
        return

    if action == "increase":
        if quantity < product.stock_quantity:  # Увеличиваем только если меньше доступного количества
            quantity += 1
        else:
            await query.answer("Нельзя добавить больше доступного количества.", show_alert=True)
            return
    elif action == "decrease":
        if quantity > 1:
            quantity -= 1
        else:
            await query.answer("Минимальное количество для добавления - 1 шт.", show_alert=True)
            return

    await update_product_details(query.message, product_id, quantity, telegram_id, bot, product_name)
    await query.answer()

async def update_product_details(message: Message, product_id: int, quantity: int, telegram_id, bot: Bot, product_name: str):
    product = await db.get_product_by_id(product_id)
    if not product:
        await message.answer("Продукт не найден.")
        return

    text = generate_product_details_text(product)

    sent_message = await message.answer_photo(photo=product.photo_url, caption=text, parse_mode="HTML",
                                              reply_markup=get_product_keyboard(product_id, quantity, product.brand.name_slug, telegram_id, product_name))
    await update_last_message_id(bot, sent_message.message_id, telegram_id)

@router.callback_query(F.data.startswith("product_"))
async def show_product_details(query: CallbackQuery, bot: Bot):
    data_parts = query.data.split('_')
    product_id = int(data_parts[1])
    # Устанавливаем количество по умолчанию равным 1, если оно не указано
    quantity = int(data_parts[2]) if len(data_parts) > 4 else 1
    brand_slug = str(data_parts[2])


    if len(data_parts) > 4:  # Предполагаем, что у вас 5 частей в data_parts
        quantity = int(data_parts[2])
        brand_slug = data_parts[3]
        color = data_parts[4].lower() == "true"
    elif len(data_parts) > 3:  # Предполагаем, что у вас 4 части в data_parts
        brand_slug = data_parts[2]
        color = data_parts[3].lower() == "true"
    else:
        # Если меньше, то используем значения по умолчанию или другую логику
        pass

    product = await db.get_product_by_id(product_id)
    product_name = await db.get_product_name_by_id(product_id)

    if not product:
        await query.answer("Продукт не найден.", show_alert=True)
        return

    text = generate_product_details_text(product)

    # Отправка сообщения с фото и деталями продукта
    sent_message = await query.message.answer_photo(photo=product.photo_url, caption=text, parse_mode="HTML", reply_markup=get_product_keyboard(product_id, quantity, brand_slug, query.from_user.id, product_name))
    await update_last_message_id(bot, sent_message.message_id, query.from_user.id)
    await query.answer()




def generate_product_details_text(product):
    """
    Генерирует текстовое описание продукта для отображения в сообщении.

    :param product: Экземпляр продукта, содержащий его характеристики.
    :return: Строка с описанием продукта.
    """
    # Основная информация о продукте
    details = [
        f"<b>{product.name}</b>\n",
        f"Цена: <b>{product.price} руб.</b>\n",
        f"Цвет: <b>{product.color}</b>\n",
        f"Размер экрана: <b>{product.screen_size}</b>\n",
        f"Память: <b>{product.storage}</b>\n",
        f"ОЗУ: <b>{product.ram}</b>\n",
        f"Батарея: <b>{product.battery_capacity} мАч</b>\n",
        f"Операционная система: <b>{product.operating_system}</b>\n",
        f"Разрешение камеры: <b>{product.camera_resolution}</b>\n"
    ]

    # Дополнительное описание, если оно доступно
    if product.description:
        details.append(f"\nОписание:\n{product.description}\n")

    # Информация о наличии на складе
    stock_info = f"В наличии: <b>{product.stock_quantity} шт.</b>" if product.stock_quantity > 0 else "<b>Нет в наличии</b>"
    details.append(stock_info)

    return ''.join(details)



@router.callback_query(F.data.startswith("order_"))
async def show_order_details(query: CallbackQuery, bot: Bot):
    order_id = int(query.data.split("_")[1])
    order_details = await db.get_order_details(order_id)  # Предполагается, что этот метод возвращает детали заказа в виде словаря

    if not order_details:
        await query.message.answer("Детали заказа не найдены.")
        return

    # Корректно обращаемся к данным через квадратные скобки
    text = f"Покупка №{order_details['purchase_id']}\nДата покупки: {order_details['purchase_date'].strftime('%d.%m.%Y')}\n\nСписок товаров:\n"
    total_amount = 0

    for product_detail in order_details['products']:
        text += f"{product_detail['name']} ({product_detail['quantity']} шт.) - {product_detail['price_at_purchase']} руб\n"
        total_amount += product_detail['price_at_purchase'] * product_detail['quantity']

    text += f"\nОбщая сумма покупки: {order_details['total_amount']} руб"

    image_path = image_main

    await query_message_photo(query, bot, text, image_path, history_back)


@router.callback_query(F.data.startswith("purchases_page_"))
async def handle_pagination(query: CallbackQuery, bot: Bot):
    # Извлекаем номер страницы из callback data
    page = int(query.data.split("_")[-1])

    # Получаем ID пользователя из сообщения
    user_id = query.from_user.id

    # Генерируем новую клавиатуру для указанной страницы
    new_keyboard = await generate_purchase_keyboard(user_id, page=page)

    text = "Выберите из списка ниже нужную покупку для полной детализации:"
    image_path = image_main

    await query_message_photo(query, bot, text, image_path, new_keyboard)