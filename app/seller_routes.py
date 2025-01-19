from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .models import db, Product, Category, CategoryProduct
from .auth_helpers import seller_required
import logging

seller_bp = Blueprint('seller', __name__)

# Страница управления категориями
@seller_bp.route('/categories', methods=['GET', 'POST'])
@login_required
@seller_required
def manage_categories():
    if request.method == 'POST':
        category_id = request.form.get('category_id')
        action = request.form.get('action')
        logging.debug(f"Received category_id: {category_id}, action: {action}")

        category = Category.query.get(category_id)
        
        
        if action == 'add_category':
            category_name = request.form.get('category_name')

            if Category.query.filter_by(category_name=category_name).first():
                flash("Категория с таким именем уже существует.", 'danger')
                return redirect(url_for('seller.manage_categories'))

            # создание новой категории 
            if category_name:
                new_category = Category(category_name=category_name)
                db.session.add(new_category)
                db.session.commit()
                flash(f"Категория '{category_name}' успешно добавлена.", 'success')
                logging.debug(f"Category '{category_name}' added successfully.")
                return redirect(url_for('seller.manage_categories'))
            else:
                flash("Название категории не может быть пустым.", 'danger')
                return redirect(url_for('seller.manage_categories'))
        
        
        elif action == 'edit':
            category_name = request.form.get('category_name')

            if category_name:
                # проверяем есть ли категория с таким же именем
                duplicate_category = Category.query.filter(Category.category_name == category_name, Category.category_id != category.category_id).first()
                if duplicate_category:
                    flash("Категория с таким именем уже существует.", 'danger')
                    return redirect(url_for('seller.manage_categories'))

                category.category_name = category_name
                db.session.commit()
                flash("Категория успешно обновлена.", 'success')
                logging.debug("Category updated successfully.")
                return redirect(url_for('seller.manage_categories'))

            else:
                flash("Название категории не может быть пустым.", 'danger')
                return redirect(url_for('seller.manage_categories'))

    categories = Category.query.all()
    return render_template('seller/manage_categories.html', categories=categories)


# Управление продуктами
@seller_bp.route('/manage_products', methods=['GET', 'POST'])
@login_required
@seller_required
def manage_products():
    if request.method == 'POST':
        try:
            product_id = int(request.form.get('product_id'))
            category_id = int(request.form.get('category_id'))
            action = request.form.get('action')

            product = Product.query.get(product_id)
            category = Category.query.get(category_id)

            if not product or not category:
                flash("Продукт или категория не найдены.", 'danger')
                return redirect(url_for('seller.manage_products'))

            if action == 'add_category':
                existing_entry = CategoryProduct.query.filter_by(product_id=product_id, category_id=category_id).first()
                if not existing_entry:
                    new_entry = CategoryProduct(product_id=product_id, category_id=category_id)
                    db.session.add(new_entry)
                    db.session.commit()
                    flash(f"Категория '{category.category_name}' добавлена к товару '{product.product_name}'.", 'success')
                else:
                    flash("Этот товар уже связан с указанной категорией.", 'danger')

            elif action == 'remove_category':
                entry = CategoryProduct.query.filter_by(product_id=product_id, category_id=category_id).first()
                if entry:
                    db.session.delete(entry)
                    db.session.commit()
                    flash(f"Категория '{category.category_name}' удалена из товара '{product.product_name}'.", 'success')
                else:
                    flash("Этот товар не связан с указанной категорией.", 'danger')

        except ValueError:
            flash("Некорректные данные.", 'danger')
            return redirect(url_for('seller.manage_products'))

    # получение всех продуктов продавца и категорий 
    products = Product.query.filter_by(seller_id=current_user.seller_id).all()
    categories = Category.query.all()
    return render_template('seller/manage_products.html', products=products, categories=categories)