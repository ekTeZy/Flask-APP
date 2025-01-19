from app import create_app
from app.db import clear_users, clear_wishlist, clear_orders, clear_order_products
from flask import render_template

app = create_app()

# True/False для очистки юзеров/корзины при старте приложения
CLEAN_MARKERS = {
    "CLEAR_WL_ON_STARTUP": False,
    "CLEAR_USER_ON_STARTUP": False,
    "CLEAR_ORDERS_ON_STARTUP": False,
    "CLEAN_ORDER_PRODUCT_ON_STARTUP": False
}
@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    with app.app_context():
        for marker in CLEAN_MARKERS:
            if CLEAN_MARKERS[marker]:
                if marker == "CLEAR_WL_ON_STARTUP":
                    clear_wishlist()
                elif marker == "CLEAR_USER_ON_STARTUP":
                    clear_users()
                elif marker == "CLEAR_ORDERS_ON_STARTUP":
                    clear_orders()
                elif marker == "CLEAN_ORDER_PRODUCT_ON_STARTUP":
                    clear_order_products()
    app.run(debug=True, host='0.0.0.0', port=5000)