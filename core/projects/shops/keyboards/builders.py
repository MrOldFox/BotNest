from aiogram.filters.callback_data import CallbackData

from core.projects.shops.handlers.sql import Database

db = Database()

shop_info = [
    [['Каталог товаров', 'get_categories'], ['Поиск товаров', 'get_crypto_rates']],
    [['Корзина', 'get_stock_prices'], ['История заказов', 'get_crypto_rates']],
    [['Акции', 'get_stock_prices'], ['Настройки', 'get_crypto_rates']],
    [['Назад', 'business_examples']]
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

