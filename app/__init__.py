import os
from flask import Flask, request, redirect
from flask_login import LoginManager
from datetime import timedelta
from urllib.parse import urlparse, urljoin
from .auth_routes import auth_bp
from .wishlist_routes import wishlist_bp
from .catalog_routes import catalog_bp
from .product_routes import product_bp
from .purchase_routes import purchase_bp
from .orders_routes import orders_bp
from .lk_routes import lk_bp
from .admin_routes import admin_bp
from .seller_routes import seller_bp
from app.models import User, Admin, Seller
from app.db import db
from flask_migrate import Migrate
from dotenv import load_dotenv


load_dotenv()

def create_app(config_name='app.config.Config'):
    """Создание Flask-приложения"""
    # Инициализация приложения
    app = Flask(__name__, static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static'))
    app.config.from_object(config_name)  # Загрузка конфигурации

    # Подключение базы данных
    db.init_app(app)
    migrate = Migrate(app, db)

    # Настройка LoginManager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # Маршрут для редиректа при отсутствии авторизации

    @login_manager.user_loader
    def load_user(user_id):
        if ":" not in user_id:
            return None

        user_type, user_id = user_id.split(":")
        user_id = int(user_id)

        if user_type == 'user':
            return User.query.get(user_id)
        elif user_type == 'admin':
            return Admin.query.get(user_id)
        elif user_type == 'seller':
            return Seller.query.get(user_id)

        return None


    # Функция для предотвращения open redirect
    def is_safe_url(target):
        ref_url = urlparse(request.host_url)
        test_url = urlparse(urljoin(request.host_url, target))
        return test_url.scheme in ['http', 'https'] and ref_url.netloc == test_url.netloc

    @app.route('/some-url')
    def some_view():
        next_url = request.args.get('next', '/')
        if not is_safe_url(next_url):
            next_url = '/'
        return redirect(next_url)

    # Регистрация blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(wishlist_bp, url_prefix='/wishlist')
    app.register_blueprint(catalog_bp, url_prefix='/catalog')
    app.register_blueprint(product_bp, url_prefix='/product')
    app.register_blueprint(purchase_bp, url_prefix='/purchase')
    app.register_blueprint(orders_bp, url_prefix='/orders')
    app.register_blueprint(lk_bp, url_prefix='/lk')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(seller_bp, url_prefix='/seller')

    # Дополнительные параметры конфигурации
    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SECURE=True,  # Используйте True только с HTTPS
        PERMANENT_SESSION_LIFETIME=timedelta(days=31)
    )

    return app
