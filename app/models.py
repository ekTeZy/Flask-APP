from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from flask_login import UserMixin
from app.db import db

# user model
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True, unique=True)
    name = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    phone = Column(String(15), nullable=True)
    address = Column(String(255), nullable=True)
    role = db.Column(db.String(15), nullable=False, default='user')  
    auth_status = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    orders = relationship('Order', back_populates='buyer', cascade='all, delete-orphan')
    wishlist = relationship('Wishlist', back_populates='user', cascade='all, delete-orphan')

    def get_id(self):
        return f"user:{self.user_id}"

# product model
class Product(db.Model):
    __tablename__ = 'product'
    product_id = Column(Integer, primary_key=True)
    product_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    stock_quantity = Column(Integer, nullable=False)
    image_url = Column(String(255), nullable=True)

    seller_id = Column(Integer, ForeignKey('sellers.seller_id'), nullable=False)

    images = relationship('ProductImage', back_populates='product')
    seller = relationship('Seller', back_populates='products')
    order_products = relationship('OrderProduct', back_populates='product')
    category_products = relationship('CategoryProduct', back_populates='product')  # Связь с CategoryProduct
    wishlist_items = relationship('Wishlist', back_populates='product')


# category model
class Category(db.Model):
    __tablename__ = 'categories'
    category_id = Column(Integer, primary_key=True, unique=True)
    category_name = Column(String(255), unique=True, nullable=False)

    category_products = relationship('CategoryProduct', back_populates='category')  


# link category <-> product
class CategoryProduct(db.Model):
    __tablename__ = 'category_product'
    id = db.Column(db.Integer, primary_key=True, unique=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.category_id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'), nullable=False)

    category = relationship('Category', back_populates='category_products')  
    product = relationship('Product', back_populates='category_products')   



# ProductImage model
class ProductImage(db.Model):
    __tablename__ = 'product_image'
    image_id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('product.product_id'), nullable=False)
    image_url = Column(String(255), nullable=False)

    product = relationship('Product', back_populates='images')





# wishlist model
class Wishlist(db.Model):
    __tablename__ = 'wishlist'
    wishlist_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    product_id = Column(Integer, ForeignKey('product.product_id'), nullable=False)
    created_at = Column(DateTime, default=db.func.current_timestamp())
    total_price = Column(Numeric(10, 2), default=0.00)
    total_quantity = Column(Integer, default=0)

    user = relationship('User', back_populates='wishlist')
    product = relationship('Product', back_populates='wishlist_items')

# seller model
class Seller(db.Model, UserMixin):
    __tablename__ = 'sellers'
    seller_id = Column(Integer, primary_key=True, unique=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    status = Column(String(20), nullable=False, default='inactive')
    phone = Column(String(50), nullable=False)
    admin_id = Column(Integer, ForeignKey('admins.admin_id'))
    is_active = db.Column(Boolean, default=True)
    auth_status = Column(Boolean, default=False)

    products = relationship('Product', back_populates='seller')
    orders = relationship('Order', back_populates='seller')

    def get_id(self):
        return f"seller:{self.seller_id}"

# admin model
class Admin(db.Model, UserMixin):
    __tablename__ = 'admins'
    admin_id = Column(Integer, primary_key=True, unique=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)
    status = Column(String(15), nullable=False, default='inactive')
    is_active = db.Column(Boolean, default=True)
    auth_status = Column(Boolean, default=False)
    def get_id(self):
        return f"admin:{self.admin_id}"

# order model
class Order(db.Model):
    __tablename__ = 'orders'
    order_id = Column(Integer, primary_key=True)
    buyer_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    created_at = Column(DateTime, default=db.func.current_timestamp())
    order_status = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False)
    seller_id = Column(Integer, ForeignKey('sellers.seller_id'))
    total_price = Column(Numeric(10, 2), nullable=False)

    buyer = relationship('User', back_populates='orders')
    seller = relationship('Seller', back_populates='orders')
    order_products = relationship('OrderProduct', back_populates='order', cascade="all, delete-orphan")

# link order <-> product
class OrderProduct(db.Model):
    __tablename__ = 'order_products'
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('product.product_id'), nullable=False)
    order_id = Column(Integer, ForeignKey('orders.order_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)  # Новое поле для хранения количества товаров


    order = relationship('Order', back_populates='order_products')
    product = relationship('Product', back_populates='order_products')
