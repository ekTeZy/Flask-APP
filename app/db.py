"""
ЭТО ТОЛЬКО УДОБСТВА РАБОТЫ С ЛОКАЛЬНОЙ БД
"""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text  

db = SQLAlchemy()

# функция для очистки базы пользователей
def clear_users():
    try:
        db.session.execute(text('TRUNCATE TABLE users RESTART IDENTITY CASCADE'))
        db.session.commit()
        print("Пользователи очищены.")
    except Exception as e:
        print(f"Ошибка при очистке: {e}")

# функция для очистки таблицы корзин
def clear_wishlist():
    try:
        db.session.execute(text('TRUNCATE TABLE wishlist RESTART IDENTITY CASCADE'))
        db.session.commit()
        print("Корзина очщена.")
    except Exception as e:
        print(f"Ошибка при очистке корзины: {e}")

# функция для очистки таблицы с заказами 
def clear_orders():
    try:
        db.session.execute(text('TRUNCATE TABLE orders RESTART IDENTITY CASCADE'))
        db.session.commit()
        print("Заказы очищены.")
    except Exception as e:
        print(f"Ошибка при очистке заказов: {e}")
# функция для очистки связующей таблицы заказов и продуктов 
def clear_order_products():
    try:
        db.session.execute(text('TRUNCATE TABLE order_products RESTART IDENTITY CASCADE'))
        db.session.commit()
        print("Продукты заказов очищены.")
    except Exception as e:
        print(f"Ошибка при очистке продуктов заказов: {e}")