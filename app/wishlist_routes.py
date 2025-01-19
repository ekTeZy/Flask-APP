from flask import Blueprint, render_template, redirect, url_for, flash, get_flashed_messages
from flask_login import login_required, current_user
from flask import request, redirect, url_for, flash
from .models import db, Wishlist, Product, ProductImage

wishlist_bp = Blueprint('wishlist', __name__, url_prefix='/wishlist')

# Маршрут для отображения списка избранного (wishlist)
@wishlist_bp.route('/')
@login_required
def view_wishlist():
    get_flashed_messages()

    # получение всех записей из wishlist для текущего пользователя
    wishlist_items = Wishlist.query.filter_by(user_id=current_user.user_id).all()
    
    # формируем список данных для передачи в шаблон с информацией о продукте и изображении
    wishlist_data = [
        {
            'wishlist_id': item.wishlist_id,                     
            'product_name': item.product.product_name,            
            'product_price': item.product.price,                   
            'total_quantity': item.total_quantity,                
            'total_price': item.total_price,                       
            'product_image_url': ProductImage.query.filter_by(product_id=item.product_id).first().image_url 
        }
        for item in wishlist_items
    ]

    # общая стоимость всех товаров 
    wishlist_total = sum(item['total_price'] for item in wishlist_data)
    
    # обновление страницы и проверка на изменения
    return render_template('wishlist/wishlist.html', wishlist_items=wishlist_data, wishlist_total=wishlist_total)


@wishlist_bp.route('/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_wishlist(product_id):
    # получаем id товара 
    product = Product.query.get_or_404(product_id)
    # устанавливваем форму для количества 
    quantity = int(request.form.get('quantity', 1))  
    
    # проверка на количество 
    if product.stock_quantity < 1:
        flash(f'Товар недоступен в наличии.', 'danger')
        return redirect(url_for('product.product_detail', product_id=product_id))

    if quantity > product.stock_quantity and product.stock_quantity > 0:
        flash(f'Вы не можете добавить больше, чем {product.stock_quantity} шт. этого товара.', 'danger')
        return redirect(url_for('product.product_detail', product_id=product_id))
    

    wishlist_item = Wishlist.query.filter_by(user_id=current_user.user_id, product_id=product_id).first()


    if wishlist_item:
        new_quantity = wishlist_item.total_quantity + quantity
        if new_quantity > product.stock_quantity:
            flash(f'Доступно только {product.stock_quantity} шт. для покупки.', 'danger')
            wishlist_item.total_quantity = product.stock_quantity
        else:
            wishlist_item.total_quantity = new_quantity
            flash('Товар добавлен в корзину!', 'success')
        wishlist_item.total_price = wishlist_item.total_quantity * product.price
    else:
        new_item = Wishlist(
            user_id=current_user.user_id,
            product_id=product_id,
            total_price=quantity * product.price,
            total_quantity=quantity
        )
        db.session.add(new_item)
        flash('Товар добавлен в корзину!', 'success')

    db.session.commit()
    return redirect(url_for('product.product_detail', product_id=product_id))


# удаление продукта 
@wishlist_bp.route('/remove/<int:wishlist_id>', methods=['POST'])
@login_required
def remove_from_wishlist(wishlist_id):
    get_flashed_messages()
    # получение продукта по его ID
    wishlist_item = Wishlist.query.get_or_404(wishlist_id)
    
    # проверка на текущего пользователя, если он владеет продуктом, то удалаяем его из базы 
    if wishlist_item.user_id == current_user.user_id:
        db.session.delete(wishlist_item)  
        db.session.commit()               
    
    # возвращение на wishlist
    flash('Товар успешно удален из корзины!', 'success')
    return redirect(url_for('wishlist.view_wishlist'))
