"""Seed database with admin user, categories, and sample food items."""

from app import create_app, db
from app.config import Config
from app.models import Category, FoodItem, User


def create_default_image():
    from PIL import Image, ImageDraw, ImageFont

    upload_dir = Config.UPLOAD_FOLDER
    upload_dir.mkdir(parents=True, exist_ok=True)
    path = upload_dir / "default_food.jpg"
    if path.exists():
        return

    img = Image.new("RGB", (400, 300), color=(220, 53, 69))
    draw = ImageDraw.Draw(img)
    draw.text((120, 130), "FastTrackChef", fill=(255, 255, 255))
    img.save(path, "JPEG")


def seed():
    app = create_app()
    with app.app_context():
        db.create_all()
        create_default_image()

        if not User.query.filter_by(email="admin@fasttrackchef.com").first():
            admin = User(
                name="Admin User",
                email="admin@fasttrackchef.com",
                phone="9876543210",
                role="admin",
            )
            admin.set_password("Admin@123")
            db.session.add(admin)
            print("Created admin: admin@fasttrackchef.com / Admin@123")

        if not User.query.filter_by(email="customer@demo.com").first():
            customer = User(
                name="Demo Customer",
                email="customer@demo.com",
                phone="9123456780",
                address="123 Food Street, City",
                role="customer",
            )
            customer.set_password("Customer@123")
            db.session.add(customer)
            print("Created customer: customer@demo.com / Customer@123")

        categories_data = [
            ("Appetizers", "Starters and small bites"),
            ("Main Course", "Hearty main dishes"),
            ("Desserts", "Sweet treats"),
            ("Beverages", "Drinks and refreshments"),
        ]
        for name, desc in categories_data:
            if not Category.query.filter_by(name=name).first():
                db.session.add(Category(name=name, description=desc))

        db.session.commit()

        sample_foods = [
            ("Margherita Pizza", "Classic tomato and mozzarella pizza", 12.99, "Main Course"),
            ("Caesar Salad", "Crisp romaine with parmesan and croutons", 8.49, "Appetizers"),
            ("Grilled Chicken", "Herb-marinated grilled chicken breast", 15.99, "Main Course"),
            ("Chocolate Lava Cake", "Warm chocolate cake with molten center", 6.99, "Desserts"),
            ("Fresh Lemonade", "Homemade refreshing lemonade", 3.99, "Beverages"),
            ("Garlic Bread", "Toasted bread with garlic butter", 4.99, "Appetizers"),
        ]

        for name, desc, price, cat_name in sample_foods:
            if not FoodItem.query.filter_by(name=name).first():
                category = Category.query.filter_by(name=cat_name).first()
                if category:
                    db.session.add(
                        FoodItem(
                            name=name,
                            description=desc,
                            price=price,
                            category_id=category.id,
                            available=True,
                        )
                    )

        db.session.commit()
        print("Database seeded successfully!")


if __name__ == "__main__":
    seed()
