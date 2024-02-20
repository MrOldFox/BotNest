from core.projects.business.shops.handlers.sql import Database

db = Database()

shop_info = [
    [['Каталог товаров', 'get_categories'], ['Поиск товаров', 'search']],
    [['Корзина', 'view_cart'], ['История заказов', 'order_history']],
    [['Назад', 'business_examples']]
]


shop_back = [
    [['Оплатить заказ', {'pay': 'True'}]],
    [['Назад', 'view_cart']]
]

history_back = [
    [['Назад', 'order_history']]
]

buy = [
    [['Заказать бот', 'order']],
    [['Назад', 'shop_main']]
]


async def get_categories_menu(page: int = 0, items_per_page: int = 6):
    categories = await db.get_all_categories()

    sorted_categories = sorted(categories, key=lambda category: category.name)

    start = page * items_per_page
    end = start + items_per_page

    page_categories = sorted_categories[start:end]

    category_menu = []
    temp_list = []

    for category in page_categories:
        temp_list.append([category.name, f"brand_{category.name_slug}"])

        if len(temp_list) == 2:
            category_menu.append(temp_list)
            temp_list = []

    if temp_list:
        category_menu.append(temp_list)

    if len(sorted_categories) > items_per_page:
        navigation_buttons = []
        if page > 0:
            navigation_buttons.append(['⬅️ Назад', f'page_{page - 1}'])
        if end < len(sorted_categories):
            navigation_buttons.append(['Вперед ➡️', f'page_{page + 1}'])
        category_menu.extend([navigation_buttons])

    category_menu.append([['В главное меню', 'shop_main']])

    return category_menu


async def get_products_by_brand_menu(brand_slug: str, page: int = 0, items_per_page: int = 8):
    brand_id = await db.get_brand_id_by_slug(brand_slug)
    products = await db.get_products_by_brand(brand_id, page, items_per_page)

    product_menu = []
    temp_list = []

    for product in products:
        product_count = await db.get_product_count_by_name(product.name)

        callback_data = f"color_{product.name}_{brand_slug}"

        temp_list.append([product.name, callback_data])

        if len(temp_list) >= 2:
            product_menu.append(temp_list)
            temp_list = []

    if temp_list:
        product_menu.append(temp_list)

    total_products = await db.get_total_products_by_brand(brand_id)
    navigation_buttons = []
    if page > 0:
        navigation_buttons.append(['⬅️ Назад', f'brand_{brand_slug}_{page - 1}'])
    if (page + 1) * items_per_page < total_products:
        navigation_buttons.append(['Вперед ➡️', f'brand_{brand_slug}_{page + 1}'])
    if navigation_buttons:
        product_menu.append(navigation_buttons)

    product_menu.append([['Вернуться к брендам', 'get_categories']])
    product_menu.append([['В главное меню', 'shop_main']])

    return product_menu


async def get_products_by_color(product_name: str, brand_slug: str):
    # product_id = await db.get_brand_id_by_slug(product_id)
    products = await db.get_products_by_color(product_name)
    brand_slug = await db.get_brand_slug_by_product_name(product_name)

    product_menu = []
    temp_list = []

    for product in products:
        temp_list.append([product.color, f"product_{product.product_id}_{product.name}"])

        if len(temp_list) == 2:
            product_menu.append(temp_list)
            temp_list = []

    if temp_list:
        product_menu.append(temp_list)

    product_menu.append([['Вернуться к моделям', f'brand_{brand_slug}']])
    product_menu.append([['В главное меню', 'shop_main']])

    return product_menu


async def generate_purchase_keyboard(user_id: int, page: int = 0, items_per_page: int = 10):
    # Получаем список покупок пользователя с учетом пагинации
    user_purchases = await db.get_user_purchases(user_id)
    total_purchases = len(user_purchases)

    # Определяем начало и конец среза для текущей страницы
    start = page * items_per_page
    end = start + items_per_page
    user_purchases = user_purchases[start:end]

    button_layout = []
    temp_list = [] 

    for purchase in user_purchases:
        button_text = f"Покупка №{purchase.purchase_id}"
        callback_data = f"order_{purchase.purchase_id}"
        temp_list.append([button_text, callback_data]) 

        if len(temp_list) == 2: 
            button_layout.append(temp_list)
            temp_list = []

    if temp_list: 
        button_layout.append(temp_list)

    navigation_buttons = []
    if page > 0:
        navigation_buttons.append(['⬅️ Назад', f'purchases_page_{page - 1}'])
    if end < total_purchases:
        navigation_buttons.append(['Вперед ➡️', f'purchases_page_{page + 1}'])
    if navigation_buttons:
        button_layout.append(navigation_buttons)

    button_layout.append([['В главное меню', 'shop_main']])

    return button_layout


