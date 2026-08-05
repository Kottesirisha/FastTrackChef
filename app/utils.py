import os
import uuid
from functools import wraps

from flask import abort, current_app
from flask_login import current_user
from werkzeug.utils import secure_filename


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)

    return decorated_function


def customer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        if current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)

    return decorated_function


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in current_app.config["ALLOWED_EXTENSIONS"]
    )


def save_food_image(file_storage):
    if not file_storage or not file_storage.filename:
        return None

    if not allowed_file(file_storage.filename):
        raise ValueError("Invalid image format. Allowed: PNG, JPG, JPEG, GIF, WEBP.")

    ext = file_storage.filename.rsplit(".", 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = current_app.config["UPLOAD_FOLDER"] / filename
    file_storage.save(filepath)
    return filename


def delete_food_image(filename):
    if filename and filename != "default_food.jpg":
        filepath = current_app.config["UPLOAD_FOLDER"] / filename
        if filepath.exists():
            os.remove(filepath)


def get_cart_total(user_id):
    from app.models import CartItem, FoodItem

    items = CartItem.query.filter_by(user_id=user_id).all()
    total = 0
    for item in items:
        if item.food_item and item.food_item.available:
            total += float(item.food_item.price) * item.quantity
    return total


def food_to_dict(food):
    return {
        "id": food.id,
        "name": food.name,
        "description": food.description,
        "price": float(food.price),
        "category_id": food.category_id,
        "category_name": food.category.name if food.category else None,
        "image": food.image,
        "image_url": food.image_url,
        "available": food.available,
        "popularity": food.popularity,
    }
