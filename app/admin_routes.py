from flask import Blueprint, render_template, request, redirect, url_for, flash, get_flashed_messages
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from .models import db, User, Admin, Seller
from .auth_helpers import admin_required
from .validators import user_data_validation
import logging

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_dashboard():
    return render_template('admin/admin_dashboard.html')

# управление пользователями
@admin_bp.route('/manage_users', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_users():
    if request.method == 'POST':
        get_flashed_messages()
        user_id = request.form.get('user_id')
        action = request.form.get('action')

        user = User.query.get(user_id)
        if not user:
            flash("Пользователь не найден.", 'danger')
            return redirect(url_for('admin.manage_users'))

        if action == 'delete' and current_user is user:
            flash("Вы не можете удалить свой аккаунт.", 'danger')
            return redirect(url_for('admin.manage_users'))

        if action == 'delete':
            db.session.delete(user)
            db.session.commit()
            flash("Пользователь успешно удалён.", 'success')
            return redirect(url_for('admin.manage_users'))

        elif action == 'edit':
            name = request.form.get('name')
            email = request.form.get('email')
            phone = request.form.get('phone')
            address = request.form.get('address')
            role = request.form.get('role')  # получение новой роли

            # проверка на ввод уже существующих данных
            if user_data_validation(username=name, email=email, phone=phone):
                duplicate_email = User.query.filter(User.email == email, User.user_id != user.user_id).first()
                duplicate_phone = User.query.filter(User.phone == phone, User.user_id != user.user_id).first()
                duplicate_name = User.query.filter(User.name == name, User.user_id != user.user_id).first()

                if duplicate_email or duplicate_phone or duplicate_name:
                    flash('Пользователь с такими данными уже существует.', 'danger')
                    return redirect(url_for('admin.manage_users'))
                
                # формируем новые данные пользователя
                user.name = name
                user.email = email
                user.phone = phone
                user.address = address
                user.role = role
                db.session.commit()
                flash("Данные пользователя успешно обновлены.", 'success')
                return redirect(url_for('admin.manage_users'))

            else:
                flash(f"Имя {name}, email {email} или телефон {phone} указаны неверно", 'danger')
                return redirect(url_for('admin.manage_users'))

    users = User.query.all()
    return render_template('admin/manage_users.html', users=users)

# управление продавцами
@admin_bp.route('/manage_sellers', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_sellers():
    if request.method == 'POST':
        get_flashed_messages()
        seller_id = request.form.get('seller_id')
        action = request.form.get('action')
        seller = Seller.query.get(seller_id)

        if not seller:
            flash("Продавец не найден.", 'danger')
            return redirect(url_for('admin.manage_sellers'))

        if action == 'delete' and not isinstance(current_user, Admin):
            flash("Удаление продавцов доступно только супер администраторам.", 'danger')
            return redirect(url_for('admin.manage_sellers'))

        elif action == 'delete' and isinstance(current_user, Admin) and Seller.query.count() < 2:
            flash("Нельзя удалить последнего продавца.", 'danger')
            return redirect(url_for('admin.manage_sellers'))

        elif action == 'delete':
            db.session.delete(seller)
            db.session.commit()
            flash("Продавец успешно удалён.",'success')
            return redirect(url_for('admin.manage_sellers'))

        if action == 'edit':
            name = request.form.get('name')
            email = request.form.get('email')
            phone = request.form.get('phone')
            status = request.form.get('status', seller.status)

            if user_data_validation(username=name, phone=phone, email=email):
                duplicate_email = Seller.query.filter(Seller.email == email, Seller.seller_id != seller.seller_id).first()
                duplicate_phone = Seller.query.filter(Seller.phone == phone, Seller.seller_id != seller.seller_id).first()
                duplicate_name = Seller.query.filter(Seller.name == name, Seller.seller_id != seller.seller_id).first()

                if duplicate_email or duplicate_phone or duplicate_name:
                    flash('Продавец с такими данными уже существует.', 'danger')
                    return redirect(url_for('admin.manage_sellers'))

            # формируем новые данные продавца
            seller.name = name
            seller.email = email
            seller.phone = phone
            seller.status = status
            db.session.commit()
            flash("Данные продавца успешно обновлены.", 'success')
    sellers = Seller.query.all()
    return render_template('admin/manage_sellers.html', sellers=sellers)

# создание продавца
@admin_bp.route('/create_seller', methods=['GET', 'POST'])
@login_required
@admin_required
def create_seller():
    get_flashed_messages()
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        phone = request.form.get('phone')
        status = request.form.get('status', 'active')

        if user_data_validation(username=name, phone=phone, password=password):

            if Seller.query.filter_by(email=email).first() or Seller.query.filter_by(name=name).first() or Seller.query.filter_by(phone=phone).first():
                flash('Продавец с такими данными уже существует.', 'danger')

            if password != confirm_password:
                flash('Пароли не совпадают.', 'danger')
                return redirect(url_for('admin.create_seller'))

            hashed_password = generate_password_hash(password, method='scrypt')
            
            # формируем нового продавца
            new_seller = Seller(
                name=name,
                email=email,
                password=hashed_password,
                phone=phone,
                status=status,
                admin_id=current_user.admin_id
            )

            db.session.add(new_seller)
            db.session.commit()
            flash('Продавец успешно создан!', 'success')
            return redirect(url_for('admin.manage_sellers'))

        else:
            flash(f"Имя {name}, email {email} или телефон {phone} указаны неверно", 'danger')
            return redirect(url_for('admin.manage_sellers'))

    return render_template('admin/create_seller.html')

# управление администраторами
@admin_bp.route('/manage_admins', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_admins():

    if not isinstance(current_user, Admin):
        flash("Доступ запрещён. Только супер администраторы могут управлять администраторами.", 'danger')
        return redirect(url_for('admin.admin_dashboard'))

    if request.method == 'POST':
        get_flashed_messages()
        admin_id = request.form.get('admin_id')
        action = request.form.get('action')
        logging.debug(f"Received admin_id: {admin_id}, action: {action}")

        admin = Admin.query.get(admin_id)
        if not admin:
            flash("Администратор не найден.", 'danger')
            logging.debug("Admin not found.")
            return redirect(url_for('admin.manage_admins'))

        if action == 'delete':
            if int(admin_id) == current_user.admin_id:
                flash("Невозможно удалить свой аккаунт.", 'danger')
                logging.debug("Attempted to delete self.")
                return redirect(url_for('admin.manage_admins'))

            else:
                db.session.delete(admin)
                db.session.commit()
                flash("Администратор успешно удалён.", 'success')
                logging.debug("Admin deleted successfully.")
                return redirect(url_for('admin.manage_admins'))

        elif action == 'edit':
            name = request.form.get('name')
            email = request.form.get('email')
            phone = request.form.get('phone')
            status = request.form.get('status', admin.status)

            if user_data_validation(username=name, phone=phone, email=email):
                duplicate_email = Admin.query.filter(Admin.email == email, Admin.admin_id != admin.admin_id).first()
                duplicate_phone = Admin.query.filter(Admin.phone == phone, Admin.admin_id != admin.admin_id).first()
                duplicate_name = Admin.query.filter(Admin.name == name, Admin.admin_id != admin.admin_id).first()

                if duplicate_email or duplicate_phone or duplicate_name:
                    flash('Администратор с такими данными уже существует.', 'danger')
                    return redirect(url_for('admin.manage_admins'))
                
                # формируем новые данные админа
                admin.name = name
                admin.email = email
                admin.phone = phone
                admin.status = status
                db.session.commit()
                flash("Данные администратора успешно обновлены.", 'success')
                return redirect(url_for('admin.manage_admins'))

            else:
                flash(f"Имя {name}, email {email} или телефон {phone} указаны неверно", 'danger')
                return redirect(url_for('admin.manage_admins'))

    admins = Admin.query.all()
    logging.debug(f"Admin list: {admins}")
    return render_template('admin/manage_admins.html', admins=admins)


# создание админа
@admin_bp.route('/create_admin', methods=['GET', 'POST'])
@login_required
@admin_required
def create_admin():
    if request.method == 'POST':
        get_flashed_messages()
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        phone = request.form.get('phone')

        if user_data_validation(username=name, phone=phone, password=password):

            if Admin.query.filter_by(email=email).first() or Admin.query.filter_by(name=name).first() or Admin.query.filter_by(phone=phone).first():
                flash('Администратор с такими данными уже существует.', 'danger')
                return redirect(url_for('admin.create_admin'))

            if password != confirm_password:
                flash('Пароли не совпадают.', 'danger')
                return redirect(url_for('admin.create_admin'))

            hashed_password = generate_password_hash(password, method='scrypt')
            
            # формируем нового админа
            new_admin = Admin(
                name=name,
                email=email,
                password=hashed_password,
                phone=phone
            )

            db.session.add(new_admin)
            db.session.commit()
            flash('Администратор успешно создан!', 'success')
            return redirect(url_for('admin.manage_admins'))

        else:
            flash(f"Имя {name}, email {email} или пароль указаны неверно", 'danger')
            return redirect(url_for('admin.manage_admins'))

    return render_template('admin/create_admin.html')