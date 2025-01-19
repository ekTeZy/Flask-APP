from datetime import timedelta
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default_secret_key') 
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')  
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=True,  
    PERMANENT_SESSION_LIFETIME=timedelta(days=31)

# не помню зачем добавил 
class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # используем базу данных в памяти для тестов
    TESTING = True
    DEBUG = False
