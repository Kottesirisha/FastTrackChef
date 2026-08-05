from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from flask_restful import Api, Resource

from app import db
from app.models import Category, FoodItem, Order, OrderItem
from app.utils import admin_required, food_to_dict, save_food_image

api_bp = Blueprint("api", __name__)
api = Api(api_bp)


def _parse_bool(value, default=True):
    if value is None:
        return default
    return str(value).lower() in ("1", "true", "yes")


class FoodListResource(Resource):
    def get(self):
        search = request.args.get("q", "").strip()
        category_id = request.args.get("category_id", type=int)
        sort = request.args.get("sort", "name")
        available_only = _parse_bool(request.args.get("available_only"), True)

        query = FoodItem.query
        if available_only:
            query = query.filter_by(available=True)
        if search:
            query = query.filter(FoodItem.name.ilike(f"%{search}%"))
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

        foods = query.all()
        return {"success": True, "count": len(foods), "data": [food_to_dict(f) for f in foods]}

    @login_required
    def post(self):
        if not current_user.is_admin:
            return {"success": False, "message": "Admin access required."}, 403

        data = request.get_json(silent=True) or {}
        required = ["name", "price", "category_id"]
        missing = [f for f in required if f not in data]
        if missing:
            return {"success": False, "message": f"Missing fields: {', '.join(missing)}"}, 400

        category = db.session.get(Category, data["category_id"])
        if not category:
            return {"success": False, "message": "Invalid category_id."}, 400

        food = FoodItem(
            name=data["name"].strip(),
            description=data.get("description", ""),
            price=data["price"],
            category_id=data["category_id"],
            available=_parse_bool(data.get("available"), True),
        )
        db.session.add(food)
        db.session.commit()
        return {"success": True, "data": food_to_dict(food)}, 201


class FoodDetailResource(Resource):
    def get(self, food_id):
        food = db.session.get(FoodItem, food_id)
        if not food:
            return {"success": False, "message": "Food not found."}, 404
        return {"success": True, "data": food_to_dict(food)}

    @login_required
    def put(self, food_id):
        if not current_user.is_admin:
            return {"success": False, "message": "Admin access required."}, 403

        food = db.session.get(FoodItem, food_id)
        if not food:
            return {"success": False, "message": "Food not found."}, 404

        data = request.get_json(silent=True) or {}
        if "name" in data:
            food.name = data["name"].strip()
        if "description" in data:
            food.description = data["description"]
        if "price" in data:
            food.price = data["price"]
        if "category_id" in data:
            if not db.session.get(Category, data["category_id"]):
                return {"success": False, "message": "Invalid category_id."}, 400
            food.category_id = data["category_id"]
        if "available" in data:
            food.available = _parse_bool(data["available"])

        db.session.commit()
        return {"success": True, "data": food_to_dict(food)}

    @login_required
    def delete(self, food_id):
        if not current_user.is_admin:
            return {"success": False, "message": "Admin access required."}, 403

        food = db.session.get(FoodItem, food_id)
        if not food:
            return {"success": False, "message": "Food not found."}, 404

        db.session.delete(food)
        db.session.commit()
        return {"success": True, "message": "Food deleted."}


class CategoryListResource(Resource):
    def get(self):
        categories = Category.query.order_by(Category.name).all()
        return {
            "success": True,
            "count": len(categories),
            "data": [
                {"id": c.id, "name": c.name, "description": c.description, "food_count": c.food_items.count()}
                for c in categories
            ],
        }


class OrderListResource(Resource):
    @login_required
    def get(self):
        if current_user.is_admin:
            orders = Order.query.order_by(Order.order_date.desc()).all()
        else:
            orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.order_date.desc()).all()

        return {
            "success": True,
            "count": len(orders),
            "data": [
                {
                    "id": o.id,
                    "user_id": o.user_id,
                    "order_date": o.order_date.isoformat(),
                    "total_amount": float(o.total_amount),
                    "status": o.status,
                    "items": [
                        {
                            "food_id": i.food_id,
                            "food_name": i.food_item.name if i.food_item else None,
                            "quantity": i.quantity,
                            "price": float(i.price),
                        }
                        for i in o.items.all()
                    ],
                }
                for o in orders
            ],
        }


api.add_resource(FoodListResource, "/foods")
api.add_resource(FoodDetailResource, "/foods/<int:food_id>")
api.add_resource(CategoryListResource, "/categories")
api.add_resource(OrderListResource, "/orders")
