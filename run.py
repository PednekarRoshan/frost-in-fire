import os
from app import create_app, db
from app.models import User, Product
from werkzeug.security import generate_password_hash
from sqlalchemy import text

app = create_app()

def seed_database():
    with app.app_context():
        db.create_all()

        # Check and migrate phone column if DB already exists
        with db.engine.connect() as conn:
            try:
                conn.execute(text("ALTER TABLE users ADD COLUMN phone VARCHAR(20) DEFAULT '919876543210'"))
                conn.commit()
            except Exception:
                pass

        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                password_hash=generate_password_hash('FrostFire@2026'),
                phone='919876543210'
            )
            db.session.add(admin)
            print("[INFO] Seeded Default Admin (User: admin | Pass: FrostFire@2026)")

        if Product.query.count() == 0:
            seed_products = [
                Product(
                    name="Crispy French Fries (Salted)",
                    description="Grade-A golden russet potatoes cut thick, ready to flash-fry to a golden crunch.",
                    category="Veg",
                    mrp=160.00,
                    selling_price=120.00,
                    image_url="https://images.unsplash.com/photo-1576107232684-1279f3908594?w=600&auto=format&fit=crop&q=80"
                ),
                Product(
                    name="Cheese Corn Triangles",
                    description="Crispy crumb coating packed with gooey melted mozzarella and sweet corn kernels.",
                    category="Veg",
                    mrp=220.00,
                    selling_price=175.00,
                    image_url="https://images.unsplash.com/photo-1541592106381-b31e9677c0e5?w=600&auto=format&fit=crop&q=80"
                ),
                Product(
                    name="Darjeeling Veg Momos (12 Pcs)",
                    description="Thin handmade wrappers stuffed with finely minced fresh seasonal vegetables & herbs.",
                    category="Veg",
                    mrp=190.00,
                    selling_price=149.00,
                    image_url="https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?w=600&auto=format&fit=crop&q=80"
                ),
                Product(
                    name="Crispy Paneer Popcorn",
                    description="Cottage cheese cubes tossed in spicy tandoori rub with an ultra-crispy outer layer.",
                    category="Veg",
                    mrp=240.00,
                    selling_price=189.00,
                    image_url="https://images.unsplash.com/photo-1567188040759-fb8a883dc6d8?w=600&auto=format&fit=crop&q=80"
                ),
                Product(
                    name="Crunchy Chicken Nuggets (15 Pcs)",
                    description="Tender whole breast chicken bites seasoned with cracked pepper and panko crust.",
                    category="Non-Veg",
                    mrp=260.00,
                    selling_price=199.00,
                    image_url="https://images.unsplash.com/photo-1562967914-608f82629710?w=600&auto=format&fit=crop&q=80"
                ),
                Product(
                    name="Juicy Chicken Momos (12 Pcs)",
                    description="Authentic Himalayan style dumplings loaded with savory, juicy chicken mince.",
                    category="Non-Veg",
                    mrp=230.00,
                    selling_price=179.00,
                    image_url="https://images.unsplash.com/photo-1625246333195-78d9c38ad449?w=600&auto=format&fit=crop&q=80"
                ),
                Product(
                    name="Smoked Chicken Seekh Kebabs (4 Skewers)",
                    description="Spiced ground chicken infused with fresh coriander, mint, and natural charcoal smoke.",
                    category="Non-Veg",
                    mrp=310.00,
                    selling_price=249.00,
                    image_url="https://images.unsplash.com/photo-1599488615731-7e5c2823ff28?w=600&auto=format&fit=crop&q=80"
                ),
                Product(
                    name="Golden Crispy Fish Fingers (8 Pcs)",
                    description="Premium Basa fillet strips coated in herbed breadcrumbs. Crisps up in 3 minutes.",
                    category="Non-Veg",
                    mrp=340.00,
                    selling_price=269.00,
                    image_url="https://images.unsplash.com/photo-1544025162-d76694265947?w=600&auto=format&fit=crop&q=80"
                )
            ]
            db.session.bulk_save_objects(seed_products)
            print("[INFO] Seeded 8 Starter Frozen Products.")

        db.session.commit()

# --- Run seeding immediately when Gunicorn loads this file ---
seed_database()

if __name__ == '__main__':
    print("\n=======================================================")
    print(" FROST IN FIRE Server Running!")
    print("=======================================================\n")
    app.run(host='0.0.0.0', port=5000, debug=True)