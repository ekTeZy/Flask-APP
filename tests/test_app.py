import pytest
from datetime import time
from app import create_app, db
from app.models import User, Admin, Seller, Category, Product
from flask_login import current_user

# Настройка тестового приложения
@pytest.fixture(scope='module')
def app():
    app = create_app(config_name='app.config.Config')  # Пример конфигурации для тестов
    yield app

# Настройка тестового клиента
@pytest.fixture(scope='module')
def client(app):
    return app.test_client()

# Настройка базы данных для тестов
@pytest.fixture(scope='function')
def init_db():
    # Создаем приложение для тестов
    app = create_app(config_name='app.config.Config')
    with app.app_context():
        # Очищаем все таблицы
        db.drop_all()
        db.create_all()

        # Добавляем тестовые данные с уникальными значениями
        user = User(name="test_user", email="testuser@example.com", password="password", phone="1234567890")
        admin = Admin(name="test_admin", email="testadmin@example.com", password="adminpass", phone="1234567890")
        seller = Seller(name="test_seller", email="testseller@example.com", password="sellerpass", phone="1234567890", status="active")
        
        db.session.add(user)
        db.session.add(admin)
        db.session.add(seller)
        db.session.commit()
        
        yield db  # Предоставляем базу данных для тестов
        
        db.session.remove()  # Ensure that session is removed
        db.drop_all()  # После тестов удаляем все таблицы


# Тест авторизации пользователя
def test_user_login(init_db):
    with init_db.app_context():
        user_email = f"user{time.time()}@example.com"
        user = User(name="test_user", email=user_email, password="password", phone="1234567890")
        
        db.session.add(user)
        db.session.commit()

        # Пробуем войти с новым пользователем
        response = client.post('/auth/login', data={'email': user_email, 'password': 'password'})
        assert response.status_code == 200
        assert "Добро пожаловать" in response.data



def test_user_registration(init_db):
    with init_db.app_context():
        # Генерация уникального email для каждого теста
        user_email = f"test{time.time()}@example.com"
        user = User(name="test_user", email=user_email, password="password", phone="1234567890")
        
        db.session.add(user)
        db.session.commit()
        
        # Проверяем, что пользователь добавлен
        added_user = User.query.filter_by(email=user_email).first()
        assert added_user is not None
        assert added_user.email == user_email


def test_create_category(init_db):
    with init_db.app_context():
        category_name = f"Test Category {time.time()}"
        response = client.post('/seller/categories', data={'category_name': category_name})
        
        # Проверяем, что категория была успешно создана
        category = Category.query.filter_by(category_name=category_name).first()
        assert category is not None
        assert category.category_name == category_name




