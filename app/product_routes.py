from flask import Blueprint, render_template, get_flashed_messages
from flask_login import login_required
from .models import Product, ProductImage

product_bp = Blueprint('product', __name__)
# формирование карточки товара
@product_bp.route('/<int:product_id>')
def product_detail(product_id):
    get_flashed_messages()

    product = Product.query.get_or_404(product_id)
    # выбираем основную картинку
    primary_image = ProductImage.query.filter_by(product_id=product_id).first()
    main_image_url = primary_image.image_url if primary_image else "default_image.png"
    # собираем все оставшиеся картинки 
    additional_images = ProductImage.query.filter(ProductImage.product_id == product_id).all()

    return render_template(
        'product/product_detail.html',
        product={
            "product_id": product.product_id, 
            "name": product.product_name,
            "description": product.description,
            "price": product.price,
            "image_url": main_image_url
        },
        additional_images=additional_images
    )
