from sqlalchemy import Column, Integer, Text, String, DECIMAL, ForeignKey, TIMESTAMP, Boolean
from sqlalchemy.orm import relationship

from core.database.models import Base, engine



class Category(Base):
    __tablename__ = 'categories'
    category_id = Column(Integer, primary_key=True)  # Уникальный идентификатор категории
    name = Column(String(255), nullable=False)  # Название категории
    description = Column(Text)  # Описание категории
    products = relationship("Product", back_populates="category")

class Product(Base):
    __tablename__ = 'products'
    product_id = Column(Integer, primary_key=True)  # Уникальный идентификатор товара
    category_id = Column(Integer, ForeignKey('categories.category_id'), nullable=False)  # Ссылка на категорию
    name = Column(String(255), nullable=False)  # Название товара
    price = Column(DECIMAL(10, 2), nullable=False)  # Цена товара
    photo_url = Column(String(255))  # URL фотографии товара
    color = Column(String(50))  # Цвет товара
    size = Column(String(50))  # Размер товара
    description = Column(Text)  # Описание товара
    stock_quantity = Column(Integer)  # Количество товара на складе
    # Установка связи между товаром и его категорией
    category = relationship("Category", back_populates="products")


class Cart(Base):
    __tablename__ = 'cart'
    cart_id = Column(Integer, primary_key=True)  # Уникальный идентификатор записи в корзине
    user_id = Column(Integer, nullable=False)  # Идентификатор пользователя (предполагается внешняя связь)
    product_id = Column(Integer, ForeignKey('products.product_id'), nullable=False)  # Ссылка на товар
    quantity = Column(Integer, nullable=False)  # Количество товара в корзине
    # Установка связи с товаром
    product = relationship("Product")


class PurchaseHistory(Base):
    __tablename__ = 'purchase_history'
    purchase_id = Column(Integer, primary_key=True)  # Уникальный идентификатор покупки
    user_id = Column(Integer, nullable=False)  # Идентификатор пользователя
    total_amount = Column(DECIMAL(10, 2), nullable=False)  # Общая сумма покупки
    purchase_date = Column(TIMESTAMP, nullable=False, default='CURRENT_TIMESTAMP')  # Дата и время покупки
    delivery_status = Column(Boolean, nullable=False)  # Статус доставки
    delivery_address = Column(Text)  # Адрес доставки


class PurchaseDetail(Base):
    __tablename__ = 'purchase_details'
    purchase_detail_id = Column(Integer, primary_key=True)  # Уникальный идентификатор детали покупки
    purchase_id = Column(Integer, ForeignKey('purchase_history.purchase_id'), nullable=False)  # Ссылка на покупку
    product_id = Column(Integer, ForeignKey('products.product_id'), nullable=False)  # Ссылка на товар
    quantity = Column(Integer, nullable=False)  # Количество купленного товара
    price_at_purchase = Column(DECIMAL(10, 2), nullable=False)  # Цена товара на момент покупки
    # Установка связей
    purchase = relationship("PurchaseHistory")
    product = relationship("Product")


class Discount(Base):
    __tablename__ = 'discounts'
    discount_id = Column(Integer, primary_key=True)  # Уникальный идентификатор скидки
    product_id = Column(Integer, ForeignKey('products.product_id'))  # Ссылка на товар
    percentage = Column(DECIMAL(5, 2), nullable=False)  # Процент скидки
    start_date = Column(TIMESTAMP, nullable=False)  # Дата начала действия скидки
    end_date = Column(TIMESTAMP, nullable=False)  # Дата окончания действия скидки
    # Установка связи с товаром
    product = relationship("Product")


async def async_main_shop():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)