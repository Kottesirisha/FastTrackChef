from decimal import Decimal

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_

from app import db
from app.models import CartItem, Category, FoodItem, Order, OrderItem
from app.utils import customer_required, get_cart_total

customer_bp = Blueprint("customer", __name__)


def _get_cart_items(user_id):
    items = CartItem.query.filter_by(user_id=user_id).all()
    cart_data = []
    total = Decimal("0.00")
    for item in items:
        food = item.food_item
        if food and food.available:
            subtotal = Decimal(str(food.price)) * item.quantity
            cart_data.append({"item": item, "food": food, "subtotal": subtotal})
            total += subtotal
    return cart_data, total


@customer_bp.route("/menu")
def menu():
    page = request.args.get("page", 1, type=int)
    search = request.args.get("q", "").strip()
    category_id = request.args.get("category", type=int)
    sort = request.args.get("sort", "name")

    query = FoodItem.query.filter_by(available=True)

    if search:
        query = query.filter(
            or_(FoodItem.name.ilike(f"%{search}%"), FoodItem.description.ilike(f"%{search}%"))
        )
    if category_id:
        query = query.filter_by(category_id=category_id)

    if sort == "price_asc":
        query = query.order_by(FoodItem.price.asc())
    elif sort == "price_desc":
        query = query.order_by(FoodItem.price.desc())
    elif sort == "popularity":
        query = query.order_by(FoodItem.popularity.desc())
    else:
        query = query.order_by(FoodItem.name.asc())

    from flask import current_app

    pagination = query.paginate(
        page=page, per_page=current_app.config["ITEMS_PER_PAGE"], error_out=False
    )
    categories = Category.query.order_by(Category.name).all()

    return render_template(
        "menu.html",
        items=pagination.items,
        pagination=pagination,
        categories=categories,
        search=search,
        selected_category=category_id,
        sort=sort,
    )


@customer_bp.route("/food/<int:food_id>")
def food_detail(food_id):
    food = db.get_or_404(FoodItem, food_id)
    if not food.available and not (current_user.is_authenticated and current_user.is_admin):
        flash("This item is currently unavailable.", "warning")
        return redirect(url_for("customer.menu"))
    related = (
        FoodItem.query.filter(
            FoodItem.category_id == food.category_id,
            FoodItem.id != food.id,
            FoodItem.available.is_(True),
        )
        .limit(4)
        .all()
    )
    return render_template("food_detail.html", food=food, related=related)


@customer_bp.route("/cart/add/<int:food_id>", methods=["POST"])
@login_required
@customer_required
def add_to_cart(food_id):
    food = db.get_or_404(FoodItem, food_id)
    if not food.available:
        flash("This item is unavailable.", "warning")
        return redirect(request.referrer or url_for("customer.menu"))

    quantity = request.form.get("quantity", 1, type=int)
    quantity = max(1, min(quantity, 99))

    cart_item = CartItem.query.filter_by(user_id=current_user.id, food_id=food_id).first()
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(user_id=current_user.id, food_id=food_id, quantity=quantity)
        db.session.add(cart_item)

    db.session.commit()
    flash(f"{food.name} added to cart.", "success")
    return redirect(request.referrer or url_for("customer.cart"))


@customer_bp.route("/cart")
@login_required
@customer_required
def cart():
    cart_data, total = _get_cart_items(current_user.id)
    return render_template("cart.html", cart_items=cart_data, total=total)


@customer_bp.route("/cart/update/<int:item_id>", methods=["POST"])
@login_required
@customer_required
def update_cart(item_id):
    cart_item = CartItem.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
    action = request.form.get("action")

    if action == "increase":
        cart_item.quantity = min(cart_item.quantity + 1, 99)
    elif action == "decrease":
        cart_item.quantity -= 1
        if cart_item.quantity <= 0:
            db.session.delete(cart_item)
    elif action == "set":
        qty = request.form.get("quantity", 1, type=int)
        if qty <= 0:
            db.session.delete(cart_item)
        else:
            cart_item.quantity = min(qty, 99)

    db.session.commit()
    return redirect(url_for("customer.cart"))


@customer_bp.route("/cart/remove/<int:item_id>", methods=["POST"])
@login_required
@customer_required
def remove_from_cart(item_id):
    cart_item = CartItem.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
    db.session.delete(cart_item)
    db.session.commit()
    flash("Item removed from cart.", "info")
    return redirect(url_for("customer.cart"))


@customer_bp.route("/checkout", methods=["GET", "POST"])
@login_required
@customer_required
def checkout():
    cart_data, total = _get_cart_items(current_user.id)
    if not cart_data:
        flash("Your cart is empty.", "warning")
        return redirect(url_for("customer.menu"))

    if request.method == "POST":
        order = Order(user_id=current_user.id, total_amount=total, status="pending")

        for entry in cart_data:
            food = entry["food"]
            order.items.append(
                OrderItem(
                    food_id=food.id,
                    quantity=entry["item"].quantity,
                    price=food.price,
                )
            )
            food.popularity += entry["item"].quantity

        db.session.add(order)
        CartItem.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        flash(f"Order #{order.id} placed successfully!", "success")
        return redirect(url_for("customer.orders"))

    return render_template("checkout.html", cart_items=cart_data, total=total)


@customer_bp.route("/orders")
@login_required
@customer_required
def orders():
    page = request.args.get("page", 1, type=int)
    from flask import current_app

    pagination = (
        Order.query.filter_by(user_id=current_user.id)
        .order_by(Order.order_date.desc())
        .paginate(page=page, per_page=current_app.config["ADMIN_ITEMS_PER_PAGE"], error_out=False)
    )
    return render_template("orders.html", orders=pagination.items, pagination=pagination)


@customer_bp.route("/orders/<int:order_id>")
@login_required
@customer_required
def order_detail(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    items = order.items.all()
    return render_template("order_detail.html", order=order, items=items)
