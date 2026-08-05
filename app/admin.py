from decimal import Decimal

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_

from app import db
from app.forms import OrderStatusForm
from app.models import CartItem, Category, FoodItem, Order, OrderItem, User
from app.utils import admin_required, delete_food_image, save_food_image

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/dashboard")
@login_required
@admin_required
def dashboard():
    total_orders = Order.query.count()
    total_customers = User.query.filter_by(role="customer").count()
    total_foods = FoodItem.query.count()
    total_revenue = (
        db.session.query(db.func.coalesce(db.func.sum(Order.total_amount), 0))
        .filter(Order.status == "delivered")
        .scalar()
    )
    pending_orders = Order.query.filter_by(status="pending").count()
    recent_orders = Order.query.order_by(Order.order_date.desc()).limit(8).all()
    popular_foods = FoodItem.query.order_by(FoodItem.popularity.desc()).limit(5).all()

    return render_template(
        "admin_dashboard.html",
        total_orders=total_orders,
        total_customers=total_customers,
        total_foods=total_foods,
        total_revenue=float(total_revenue or 0),
        pending_orders=pending_orders,
        recent_orders=recent_orders,
        popular_foods=popular_foods,
    )


@admin_bp.route("/foods")
@login_required
@admin_required
def manage_foods():
    page = request.args.get("page", 1, type=int)
    search = request.args.get("q", "").strip()
    category_id = request.args.get("category", type=int)

    query = FoodItem.query
    if search:
        query = query.filter(FoodItem.name.ilike(f"%{search}%"))
    if category_id:
        query = query.filter_by(category_id=category_id)

    pagination = query.order_by(FoodItem.name).paginate(
        page=page, per_page=current_app.config["ADMIN_ITEMS_PER_PAGE"], error_out=False
    )
    categories = Category.query.order_by(Category.name).all()
    return render_template(
        "manage_foods.html",
        foods=pagination.items,
        pagination=pagination,
        categories=categories,
        search=search,
        selected_category=category_id,
    )


@admin_bp.route("/food/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_food():
    from app.forms import FoodItemForm

    form = FoodItemForm()
    form.category_id.choices = [(c.id, c.name) for c in Category.query.order_by(Category.name).all()]

    if form.validate_on_submit():
        try:
            image_filename = save_food_image(form.image.data) if form.image.data else "default_food.jpg"
        except ValueError as e:
            flash(str(e), "danger")
            return render_template("add_food.html", form=form)

        food = FoodItem(
            name=form.name.data.strip(),
            description=form.description.data,
            price=form.price.data,
            category_id=form.category_id.data,
            image=image_filename or "default_food.jpg",
            available=form.available.data,
        )
        db.session.add(food)
        db.session.commit()
        flash("Food item added successfully.", "success")
        return redirect(url_for("admin.manage_foods"))

    return render_template("add_food.html", form=form)


@admin_bp.route("/food/<int:food_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_food(food_id):
    from app.forms import FoodItemForm

    food = db.get_or_404(FoodItem, food_id)
    form = FoodItemForm(obj=food)
    form.category_id.choices = [(c.id, c.name) for c in Category.query.order_by(Category.name).all()]

    if form.validate_on_submit():
        try:
            if form.image.data:
                delete_food_image(food.image)
                food.image = save_food_image(form.image.data) or food.image
        except ValueError as e:
            flash(str(e), "danger")
            return render_template("edit_food.html", form=form, food=food)

        food.name = form.name.data.strip()
        food.description = form.description.data
        food.price = form.price.data
        food.category_id = form.category_id.data
        food.available = form.available.data
        db.session.commit()
        flash("Food item updated successfully.", "success")
        return redirect(url_for("admin.manage_foods"))

    return render_template("edit_food.html", form=form, food=food)


@admin_bp.route("/food/<int:food_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_food(food_id):
    food = db.get_or_404(FoodItem, food_id)
    delete_food_image(food.image)
    db.session.delete(food)
    db.session.commit()
    flash("Food item deleted.", "success")
    return redirect(url_for("admin.manage_foods"))


@admin_bp.route("/categories")
@login_required
@admin_required
def manage_categories():
    categories = Category.query.order_by(Category.name).all()
    return render_template("manage_categories.html", categories=categories)


@admin_bp.route("/categories/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_category():
    from app.forms import CategoryForm

    form = CategoryForm()
    if form.validate_on_submit():
        if Category.query.filter_by(name=form.name.data.strip()).first():
            flash("Category already exists.", "warning")
        else:
            category = Category(name=form.name.data.strip(), description=form.description.data)
            db.session.add(category)
            db.session.commit()
            flash("Category created.", "success")
            return redirect(url_for("admin.manage_categories"))
    return render_template("add_category.html", form=form)


@admin_bp.route("/categories/<int:category_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_category(category_id):
    from app.forms import CategoryForm

    category = db.get_or_404(Category, category_id)
    form = CategoryForm(obj=category)
    if form.validate_on_submit():
        existing = Category.query.filter(
            Category.name == form.name.data.strip(), Category.id != category.id
        ).first()
        if existing:
            flash("Category name already exists.", "warning")
        else:
            category.name = form.name.data.strip()
            category.description = form.description.data
            db.session.commit()
            flash("Category updated.", "success")
            return redirect(url_for("admin.manage_categories"))
    return render_template("edit_category.html", form=form, category=category)


@admin_bp.route("/categories/<int:category_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_category(category_id):
    category = db.get_or_404(Category, category_id)
    if category.food_items.count() > 0:
        flash("Cannot delete category with assigned food items.", "danger")
    else:
        db.session.delete(category)
        db.session.commit()
        flash("Category deleted.", "success")
    return redirect(url_for("admin.manage_categories"))


@admin_bp.route("/customers")
@login_required
@admin_required
def manage_customers():
    page = request.args.get("page", 1, type=int)
    search = request.args.get("q", "").strip()
    query = User.query.filter_by(role="customer")
    if search:
        query = query.filter(or_(User.name.ilike(f"%{search}%"), User.email.ilike(f"%{search}%")))
    pagination = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=current_app.config["ADMIN_ITEMS_PER_PAGE"], error_out=False
    )
    return render_template("manage_customers.html", customers=pagination.items, pagination=pagination, search=search)


@admin_bp.route("/orders")
@login_required
@admin_required
def manage_orders():
    page = request.args.get("page", 1, type=int)
    status = request.args.get("status", "")
    query = Order.query
    if status:
        query = query.filter_by(status=status)
    pagination = query.order_by(Order.order_date.desc()).paginate(
        page=page, per_page=current_app.config["ADMIN_ITEMS_PER_PAGE"], error_out=False
    )
    return render_template(
        "manage_orders.html",
        orders=pagination.items,
        pagination=pagination,
        selected_status=status,
        statuses=Order.STATUS_CHOICES,
    )


@admin_bp.route("/orders/<int:order_id>", methods=["GET", "POST"])
@login_required
@admin_required
def order_detail(order_id):
    order = db.get_or_404(Order, order_id)
    form = OrderStatusForm(status=order.status)
    if form.validate_on_submit():
        order.status = form.status.data
        db.session.commit()
        flash("Order status updated.", "success")
        return redirect(url_for("admin.order_detail", order_id=order.id))
    items = order.items.all()
    return render_template("admin_order_detail.html", order=order, items=items, form=form)
