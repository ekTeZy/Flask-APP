from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.db import db
from app.models import Order, OrderProduct

orders_bp = Blueprint('orders', __name__, template_folder='templates/orders')

# маршрут для отображения всех заказов пользователя
@orders_bp.route('/my_orders', methods=['GET'])
@login_required
def my_orders():
    orders = Order.query.filter_by(buyer_id=current_user.user_id).all()
    return render_template('orders/my_orders.html', orders=orders)

# маршрут для подтверждения заказа
@orders_bp.route('/confirm_order/<int:order_id>', methods=['POST'])
@login_required
def confirm_order(order_id):
    order = Order.query.get_or_404(order_id)

    if order.order_status != 'completed':
        order.order_status = 'completed'
        
        # уменьшаем количество товаров на складе
        for item in order.order_products:
            product = item.product
            if product.stock_quantity >= item.quantity:
                product.stock_quantity -= item.quantity
            else:
                flash(f"Недостаточно товара {product.product_name} для подтверждения заказа.")
                db.session.rollback()
                return redirect(url_for('orders.my_orders'))
        
        db.session.commit()
        flash("Заказ успешно подтвержден.")
    else:
        flash("Этот заказ уже подтвержден.")

    return redirect(url_for('orders.my_orders'))

# маршрут для отмены заказа
@orders_bp.route('/cancel_order/<int:order_id>', methods=['POST'])
@login_required
def cancel_order(order_id):
    order = Order.query.filter_by(order_id=order_id, buyer_id=current_user.user_id).first()
    if not order:
        flash("Заказ не найден или у вас нет доступа к нему.", "error")
        return redirect(url_for('orders.my_orders'))
    
    OrderProduct.query.filter_by(order_id=order.order_id).delete()
    
    db.session.delete(order)
    db.session.commit()
    
    flash("Заказ успешно отменен.", "success")
    return redirect(url_for('orders.my_orders'))
