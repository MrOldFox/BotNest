from aiogram.filters.callback_data import CallbackData

from core.projects.shops.handlers.sql import Database

db = Database()

shop_info = [
    [['Каталог товаров', 'get_categories'], ['Поиск товаров', 'get_categories']],
    [['Корзина', 'get_stock_prices'], ['История заказов', 'get_crypto_rates']],
    [['Акции', 'get_stock_prices'], ['Настройки', 'get_crypto_rates']],
    [['Назад', 'business_examples']]
]


shop_back = [
    [['Назад', 'get_categories']]
]


async def get_categories_menu(page: int = 0, items_per_page: int = 6):
    categories = await db.get_all_categories()  # Получение списка категорий

    # Вычисление начального и конечного индекса для текущей страницы
    start = page * items_per_page
    end = start + items_per_page

    # Срез списка категорий для текущей страницы
    page_categories = categories[start:end]

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
    if len(categories) > items_per_page:
        navigation_buttons = []
        if page > 0:
            navigation_buttons.append(['⬅️ Назад', f'page_{page - 1}'])
        if end < len(categories):
            navigation_buttons.append(['Вперед ➡️', f'page_{page + 1}'])
        category_menu.extend([navigation_buttons])

    category_menu.append([['В меню', 'shop_main']])

    return category_menu


async def get_products_by_brand_menu(brand_slug: str, page: int = 0, items_per_page: int = 8):
    # Предположим, что у вас есть функция для получения ID бренда по его slug
    brand_id = await db.get_brand_id_by_slug(brand_slug)
    products = await db.get_products_by_brand(brand_id, page, items_per_page)

    product_menu = []
    temp_list = []

    for product in products:
        # Формируем пары [название продукта, callback_data для продукта]
        temp_list.append([product.name, f"product_{product.product_id}"])

        if len(temp_list) == 2:
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

    return product_menu
