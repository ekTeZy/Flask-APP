from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from .models import db, User, Admin, Seller
from .validators import user_data_validation
from flask_login import login_user, current_user, logout_user
# import logging


# logging.basicConfig(level=logging.DEBUG)

auth_bp = Blueprint('auth', __name__)
# обработка данных пользователя при регистрации
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        phone = request.form.get('phone')
        email = request.form.get('email')
        address = request.form.get('address')

        # проверка существующих пользователей
        existing_user = User.query.filter_by(email=email).first()
        existing_admin = Admin.query.filter_by(email=email).first()
        existing_seller = Seller.query.filter_by(email=email).first()
         
        if existing_seller:
            flash('Этот email уже зарегистрирован в качестве продавца. Пожалуйста войдите в систему', 'danger')
            return redirect(url_for('auth.login'))
        
        if existing_admin:
            flash('Этот email уже зарегистрирован в качестве админа. Пожалуйста войдите в систему', 'danger')
            return redirect(url_for('auth.login'))
        
        if existing_user:
            flash('Этот email уже зарегистрирован.', 'danger')
            return redirect(url_for('auth.register'))

        if password != confirm_password:
            flash('Пароли не совпадают.', 'danger')
            return redirect(url_for('auth.register'))

        if user_data_validation(username=username, phone=phone, password=password):

            hashed_password = generate_password_hash(password, method='scrypt')
            new_user = User(name=username, email=email, address=address, password=hashed_password, phone=phone)

            db.session.add(new_user)
            db.session.commit()
            flash('Регистрация прошла успешно! Пожалуйста, войдите в систему.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(f"Неверно указан телефона, имя пользователя или пароль\nИмя минимум 4 символа, пароль минимум 6 символов")
            return redirect(url_for('auth.register')) 
    
    return render_template('auth/register.html')


# обрабатываем данные для входа пользвателя
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # проверки паролей и статусов  
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)  
            current_user.auth_status = True
            db.session.commit() 
            flash('Вы успешно вошли как пользователь!', 'success')
            return redirect(url_for('lk.lk_login'))

        admin = Admin.query.filter_by(email=email).first()
        if admin and check_password_hash(admin.password, password):
            login_user(admin)  
            current_user.auth_status = True
            db.session.commit()
            flash('Вы успешно вошли как администратор!', 'success')
            return redirect(url_for('admin.admin_dashboard'))

        seller = Seller.query.filter_by(email=email).first()
        if seller and check_password_hash(seller.password, password):
            current_user.auth_status = True
            db.session.commit()
            login_user(seller)  
            flash('Вы успешно вошли как продавец!', 'success')
            return redirect(url_for('seller.manage_products'))

        flash('Неверный email или пароль.', 'danger')
        return redirect(url_for('auth.login'))

    return render_template('auth/login.html')




# обработка логаута 
@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    if current_user.is_authenticated:
        # обновляем статус пользователя в базе данных
        current_user.auth_status = False
        db.session.commit()

    # выход 
    logout_user()
    session.clear()
    flash("Вы успешно вышли из системы.", "info")
    return redirect(url_for('auth.login'))
