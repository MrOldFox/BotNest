from aiogram.filters.callback_data import CallbackData

from core.projects.shops.handlers.sql import Database

db = Database()

shop_info = [
    [['Каталог товаров', 'get_categories'], ['Поиск товаров', 'search']],
    [['Корзина', 'view_cart'], ['История заказов', 'search']],
    [['Назад', 'business_examples']]
]


shop_back = [
    [['Оплатить заказ', {'pay': 'True'}]],
    [['Назад', 'view_cart']]
]

buy = [
    [['Заказать бот', 'order']],
    [['Назад', 'shop_main']]
]


async def get_categories_menu(page: int = 0, items_per_page: int = 6):
    categories = await db.get_all_categories()  # Получение списка категорий

    # Сортировка списка категорий от А до Я по имени
    sorted_categories = sorted(categories, key=lambda category: category.name)

    # Вычисление начального и конечного индекса для текущей страницы
    start = page * items_per_page
    end = start + items_per_page

    # Срез отсортированного списка категорий для текущей страницы
    page_categories = sorted_categories[start:end]

    category_menu = []
    temp_list = []

    for category in page_categories:
        # Добавляем пары категорий во временный список
        temp_list.append([category.name, f"brand_{category.name_slug}"])

        # Когда во временном списке накапливается два элемента, добавляем его в основной список и очищаем временный
        if len(temp_list) == 2:
            category_menu.append(temp_list)
            temp_list = []

    # Если после цикла во временном списке остались элементы, добавляем их в основной список
    if temp_list:
        category_menu.append(temp_list)

    # Добавляем кнопки управления страницами, если это необходимо
    if len(sorted_categories) > items_per_page:
        navigation_buttons = []
        if page > 0:
            navigation_buttons.append(['⬅️ Назад', f'page_{page - 1}'])
        if end < len(sorted_categories):
            navigation_buttons.append(['Вперед ➡️', f'page_{page + 1}'])
        category_menu.extend([navigation_buttons])

    category_menu.append([['В меню', 'shop_main']])

    return category_menu


async def get_products_by_brand_menu(brand_slug: str, page: int = 0, items_per_page: int = 8):
    brand_id = await db.get_brand_id_by_slug(brand_slug)
    products = await db.get_products_by_brand(brand_id, page, items_per_page)

    product_menu = []
    temp_list = []

    for product in products:
        # Проверяем, сколько раз встречается продукт с таким именем в базе данных
        product_count = await db.get_product_count_by_name(product.name)

            # Если имя продукта встречается более одного раза, используем формат с color_

        callback_data = f"color_{product.name}_{brand_slug}"

        temp_list.append([product.name, callback_data])

        if len(temp_list) >= 2:
            product_menu.append(temp_list)
            temp_list = []

    if temp_list:
        product_menu.append(temp_list)

    # Добавляем кнопки управления страницами, если это необходимо
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
        # Формируем пары [название продукта, callback_data для продукта]
        temp_list.append([product.color, f"product_{product.product_id}_{product.name}"])

        if len(temp_list) == 2:
            product_menu.append(temp_list)
            temp_list = []

    if temp_list:
        product_menu.append(temp_list)

    product_menu.append([['Вернуться к моделям', f'brand_{brand_slug}']])
    product_menu.append([['В главное меню', 'shop_main']])

    return product_menu
