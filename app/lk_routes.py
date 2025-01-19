from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for, get_flashed_messages
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import db, User
from .validators import user_data_validation

lk_bp = Blueprint('lk', __name__)

@lk_bp.route('/', methods=['GET', 'POST'])
@login_required
def lk_login():
    print(f"Current user: {current_user}")

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()

        # валидируем новые данные пользователя
        if user_data_validation(username=name, phone=phone):
            if name != current_user.name:
                current_user.name = name
                flash("Имя пользователя изменено на {}.".format(name))
            if email != current_user.email:
                if User.query.filter_by(email=email).first():
                    flash("Этот email уже используется.")
                else:
                    current_user.email = email
                    flash("Электронная почта изменена на {}.".format(email))
            if phone != current_user.phone:
                current_user.phone = phone
                flash("Телефон изменён на {}.".format(phone))
            if address != current_user.address:
                current_user.address = address
                flash("Адрес изменён на {}.".format(address))
            # попытка коммита в базу 
            try:
                db.session.commit()
                flash("Изменения успешно сохранены.")
            except Exception as e:
                db.session.rollback()
                flash("Ошибка сохранения данных.")
                print(e)

            return redirect(url_for('lk.lk_login'))
        
        else:
            flash("Неверные данные")
            return redirect(url_for('lk.lk_login'))


    return render_template('lk/lk.html', user=current_user)


# отдельный маршрут для смены пароля
@lk_bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        # все условия для валидации 
        if not check_password_hash(current_user.password, current_password):
            flash("Неверно указан текущий пароль", "error")
            return redirect(url_for('lk.change_password'))

        if new_password != confirm_password:
            flash("Пароли не совпадают", "error")
            return redirect(url_for('lk.change_password'))

        if not user_data_validation(password=new_password):  
            flash("Пароль не соответствует требованиям безопасности", "error")
            return redirect(url_for('lk.change_password'))
        # смена пароля после валидации
        current_user.password = generate_password_hash(new_password, method='scrypt')
        db.session.commit()

        flash("Пароль успешно сменён", "success")
        return redirect(url_for('lk.lk_login'))

    return render_template('lk/change_password.html', user=current_user)