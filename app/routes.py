from flask import Blueprint, render_template
from app.models import Category, FoodItem, Order
from app import db

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    print("=" * 80)
    print("DATABASE URL:", db.engine.url)
    print("=" * 80)

    featured_items = (
        FoodItem.query.filter_by(available=True)
        .order_by(FoodItem.popularity.desc())
        .limit(6)
        .all()
    )

    categories = Category.query.order_by(Category.name).all()

    stats = {
        "food_count": FoodItem.query.filter_by(available=True).count(),
        "category_count": Category.query.count(),
        "order_count": Order.query.filter_by(status="delivered").count(),
    }

    return render_template(
        "index.html",
        featured_items=featured_items,
        categories=categories,
        stats=stats,
    )