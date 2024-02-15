# from sqlalchemy import Column, Integer, Text, String, DECIMAL, ForeignKey, TIMESTAMP, Boolean
# from sqlalchemy.orm import relationship
#
# from core.database.models import Base, engine
#
#
# class Brand(Base):
#     __tablename__ = 'brands'
#     brand_id = Column(Integer, primary_key=True)  # Уникальный идентификатор бренда
#     name = Column(String(255), nullable=False)  # Название бренда
#     description = Column(Text)  # Описание бренда
#     name_slug = Column(Text, nullable=False)  # Слаг проекта
#     photo_url = Column(String(255))  # URL фотографии товара
#     # Обратная связь с продуктами
#     products = relationship("Product", back_populates="brand")
#
#
# class Product(Base):
#     __tablename__ = 'products'
#     product_id = Column(Integer, primary_key=True)  # Уникальный идентификатор товара
#     brand_id = Column(Integer, ForeignKey('brands.brand_id'), nullable=False)  # Ссылка на бренд
#     name = Column(String(255), nullable=False)  # Название модели телефона
#     price = Column(DECIMAL(10, 2), nullable=False)  # Цена товара
#     photo_url = Column(String(255))  # URL фотографии товара
#     color = Column(String(50))  # Цвет корпуса
#     screen_size = Column(String(255))  # Размер экрана в дюймах
#     storage = Column(String(255))  # Встроенная память в ГБ
#     ram = Column(String(255))  # Оперативная память в ГБ
#     battery_capacity = Column(Integer)  # Ёмкость батареи в мАч
#     operating_system = Column(String(50))  # Операционная система
#     camera_resolution = Column(String(50))  # Разрешение камеры
#     description = Column(Text)  # Описание товара
#     stock_quantity = Column(Integer)  # Количество товара на складе
#
#     # Установка связи между товаром и брендом
#     brand = relationship("Brand", back_populates="products")
#
#
# class Cart(Base):
#     __tablename__ = 'cart'
#     cart_id = Column(Integer, primary_key=True)  # Уникальный идентификатор записи в корзине
#     user_id = Column(Integer, nullable=False)  # Идентификатор пользователя (предполагается внешняя связь)
#     product_id = Column(Integer, ForeignKey('products.product_id'), nullable=False)  # Ссылка на товар
#     quantity = Column(Integer, nullable=False)  # Количество товара в корзине
#     # Установка связи с товаром
#     product = relationship("Product")
#
#
# class PurchaseHistory(Base):
#     __tablename__ = 'purchase_history'
#     purchase_id = Column(Integer, primary_key=True)  # Уникальный идентификатор покупки
#     user_id = Column(Integer, nullable=False)  # Идентификатор пользователя
#     total_amount = Column(DECIMAL(10, 2), nullable=False)  # Общая сумма покупки
#     purchase_date = Column(TIMESTAMP, nullable=False, default='CURRENT_TIMESTAMP')  # Дата и время покупки
#     delivery_status = Column(Boolean, nullable=False)  # Статус доставки
#     delivery_address = Column(Text)  # Адрес доставки
#
#
# class PurchaseDetail(Base):
#     __tablename__ = 'purchase_details'
#     purchase_detail_id = Column(Integer, primary_key=True)  # Уникальный идентификатор детали покупки
#     purchase_id = Column(Integer, ForeignKey('purchase_history.purchase_id'), nullable=False)  # Ссылка на покупку
#     product_id = Column(Integer, ForeignKey('products.product_id'), nullable=False)  # Ссылка на товар
#     quantity = Column(Integer, nullable=False)  # Количество купленного товара
#     price_at_purchase = Column(DECIMAL(10, 2), nullable=False)  # Цена товара на момент покупки
#     # Установка связей
#     purchase = relationship("PurchaseHistory")
#     product = relationship("Product")
#
#
# class Discount(Base):
#     __tablename__ = 'discounts'
#     discount_id = Column(Integer, primary_key=True)  # Уникальный идентификатор скидки
#     product_id = Column(Integer, ForeignKey('products.product_id'))  # Ссылка на товар
#     percentage = Column(DECIMAL(5, 2), nullable=False)  # Процент скидки
#     start_date = Column(TIMESTAMP, nullable=False)  # Дата начала действия скидки
#     end_date = Column(TIMESTAMP, nullable=False)  # Дата окончания действия скидки
#     # Установка связи с товаром
#     product = relationship("Product")
#
#
