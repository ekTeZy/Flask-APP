from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user
from .models import Admin, Seller

# проверка на админа
def admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        
        if isinstance(current_user, Admin):
            return(func(*args, **kwargs))
        
        if current_user.role == 'admin':
            return func(*args, **kwargs)

        flash('Доступ запрещён.', 'danger')
        return redirect(url_for('auth.login'))
    return decorated_view

# проверка на продавца
def seller_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not isinstance(current_user, Seller):
            flash('Доступ запрещён. Вы должны быть продавцом.', 'danger')
            return redirect(url_for('auth.login'))  # перенаправляем на страницу входа
        return func(*args, **kwargs)
    return decorated_view



