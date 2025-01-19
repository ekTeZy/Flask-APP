from flask import Blueprint, render_template, get_flashed_messages
from .models import Product, ProductImage

catalog_bp = Blueprint('catalog', __name__)

# забираем продукты из базы для каталога 
@catalog_bp.route('/catalog')
def catalog():
    get_flashed_messages()
    products = Product.query.all()
    for product in products:
        primary_image = ProductImage.query.filter_by(product_id=product.product_id).first()
        product.image_url = primary_image.image_url if primary_image else "default_image.png"
    
    return render_template('catalog/catalog.html', products=products)