from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime
from app.models import db, Order, OrderProduct, Wishlist, Product, ProductImage

purchase_bp = Blueprint('purchase', __name__)

@purchase_bp.route('/')
@login_required
def show_purchase():
    # получение всех продуктов из wishlist пользователя
    wishlist_items = Wishlist.query.filter_by(user_id=current_user.user_id).all()
    
    # если нет товара нет перенаправления  
    if not wishlist_items:
        flash('Ваша корзина пуста. Для оформления заказа добавьте товары в корзину.', 'info')
        return redirect(url_for('wishlist.view_wishlist'))

    # общая сумма товаров в корзине
    total_price = sum(item.total_price for item in wishlist_items)
    
    return render_template('purchase/purchase.html', wishlist_items=wishlist_items, total_price=total_price)



@purchase_bp.route('/complete_purchase', methods=['POST'])
@login_required
def complete_purchase():
    wishlist_items = Wishlist.query.filter_by(user_id=current_user.user_id).all()
    total_price = sum(item.total_price for item in wishlist_items)

    order = Order(
        buyer_id=current_user.user_id,
        created_at=datetime.utcnow(),
        order_status="pending", 
        status="active",  
        seller_id=wishlist_items[0].product.seller_id if wishlist_items else None,
        total_price=total_price
    )
    db.session.add(order)
    db.session.commit()

    for item in wishlist_items:
        order_product = OrderProduct(
            product_id=item.product_id,
            order_id=order.order_id,
            quantity=item.total_quantity,
        )
        db.session.add(order_product)
    
    db.session.commit()

    for item in wishlist_items:
        db.session.delete(item)
    db.session.commit()

    flash("Заказ успешно создан!", "success")

    return redirect(url_for("catalog.catalog"))




