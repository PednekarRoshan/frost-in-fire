#!/usr/bin/env python3
"""
FROST IN FIRE - Automated Project Builder
Architected for Hyper-Local Direct-to-WhatsApp E-Commerce
"""

import os
import sys

FILES = {}

# ==========================================
# 1. REQUIREMENTS & RUNTIME
# ==========================================
FILES["requirements.txt"] = """Flask==3.0.3
Flask-SQLAlchemy==3.1.1
Flask-Login==0.6.3
Werkzeug==3.0.3
"""

FILES["run.py"] = """import os
from app import create_app, db
from app.models import User, Product
from werkzeug.security import generate_password_hash

app = create_app()

def seed_database():
    with app.app_context():
        db.create_all()
        # Seed default Admin
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                password_hash=generate_password_hash('FrostFire@2026')
            )
            db.session.add(admin)
            print("[INFO] Seeded Default Admin (User: admin | Pass: FrostFire@2026)")

        # Seed initial catalog if empty
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

if __name__ == '__main__':
    seed_database()
    print("\\n=======================================================")
    print(" FROST IN FIRE Server Running!")
    print(" Access on PC:      http://127.0.0.1:5000")
    print(" Access on Mobile:  http://<YOUR_LOCAL_IP>:5000")
    print(" Admin Portal:      http://127.0.0.1:5000/admin/login")
    print("=======================================================\\n")
    app.run(host='0.0.0.0', port=5000, debug=True)
"""

# ==========================================
# 2. APPLICATION FACTORY & CONFIG
# ==========================================
FILES["app/__init__.py"] = """import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.dirname(app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')), exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'admin_bp.login'
    login_manager.login_message_category = 'warning'

    from app.blueprints.public import public_bp
    from app.blueprints.admin import admin_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')

    return app
"""

FILES["app/config.py"] = """import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'frost-in-fire-super-secret-key-2026')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 
        f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'frostinfire.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024  # 8 MB max upload limit

    # Hyperlocal business variables
    DELIVERY_PINCODE = os.environ.get('DELIVERY_PINCODE', '400011')
    STORE_WHATSAPP_NUMBER = os.environ.get('STORE_WHATSAPP_NUMBER', '919876543210')
"""

FILES["app/models.py"] = """from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(20), nullable=False)  # 'Veg' or 'Non-Veg'
    mrp = db.Column(db.Float, nullable=False)
    selling_price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def discount_percent(self):
        if self.mrp and self.mrp > self.selling_price:
            return round(((self.mrp - self.selling_price) / self.mrp) * 100)
        return 0

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    order_code = db.Column(db.String(32), unique=True, nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    delivery_address = db.Column(db.Text, nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    delivery_notes = db.Column(db.Text, nullable=True)
    total_mrp = db.Column(db.Float, nullable=False, default=0.0)
    total_savings = db.Column(db.Float, nullable=False, default=0.0)
    final_amount = db.Column(db.Float, nullable=False, default=0.0)
    status = db.Column(db.String(20), default='NEW')  # NEW, CONFIRMED, PACKED, DELIVERED, CANCELLED
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    items = db.relationship('OrderItem', backref='order', cascade='all, delete-orphan', lazy=True)

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=True)
    product_name = db.Column(db.String(120), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Float, nullable=False)
    line_total = db.Column(db.Float, nullable=False)
"""

# ==========================================
# 3. BLUEPRINTS: PUBLIC & ADMIN
# ==========================================
FILES["app/blueprints/__init__.py"] = ""

FILES["app/blueprints/public.py"] = """import re
import urllib.parse
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, current_app
from app import db
from app.models import Product, Order, OrderItem

public_bp = Blueprint('public_bp', __name__)

def clean_pincode(pin: str) -> str:
    return re.sub(r'[^0-9]', '', str(pin or ''))

@public_bp.context_processor
def inject_config():
    return {
        'TARGET_PINCODE': current_app.config['DELIVERY_PINCODE'],
        'STORE_PHONE': current_app.config['STORE_WHATSAPP_NUMBER']
    }

@public_bp.route('/')
def index():
    selected_category = request.args.get('category', 'all').strip().lower()
    query = Product.query.filter_by(is_active=True)
    if selected_category == 'veg':
        query = query.filter_by(category='Veg')
    elif selected_category == 'non-veg':
        query = query.filter_by(category='Non-Veg')
        
    products = query.order_by(Product.id.desc()).all()
    return render_template('public/index.html', products=products, active_cat=selected_category)

@public_bp.route('/cart')
def cart():
    return render_template('public/cart.html')

@public_bp.route('/order-success/<order_code>')
def order_success(order_code):
    order = Order.query.filter_by(order_code=order_code).first_or_404()
    return render_template('public/order_success.html', order=order)

@public_bp.route('/api/orders', methods=['POST'])
def place_order():
    data = request.get_json() or {}
    
    # 1. Pincode verification
    raw_pincode = data.get('pincode', '')
    customer_pincode = clean_pincode(raw_pincode)
    allowed_pincode = clean_pincode(current_app.config['DELIVERY_PINCODE'])

    if customer_pincode != allowed_pincode:
        return jsonify({
            'success': False,
            'message': f"Frost in Fire is currently serving exclusively in Pincode {current_app.config['DELIVERY_PINCODE']}. We are expanding to your area soon!"
        }), 400

    items = data.get('items', [])
    if not items:
        return jsonify({'success': False, 'message': 'Your cart is empty!'}), 400

    name = data.get('name', '').strip()
    phone = data.get('phone', '').strip()
    address = data.get('address', '').strip()
    notes = data.get('notes', '').strip()

    if not name or not phone or not address:
        return jsonify({'success': False, 'message': 'Please fill all mandatory contact fields.'}), 400

    # 2. Server-side totals calculation
    calculated_mrp = 0.0
    calculated_final = 0.0
    order_items_payload = []

    for item in items:
        prod_id = item.get('id')
        qty = int(item.get('qty', 1))
        product = Product.query.get(prod_id)
        if product:
            line_mrp = product.mrp * qty
            line_cost = product.selling_price * qty
            calculated_mrp += line_mrp
            calculated_final += line_cost
            order_items_payload.append({
                'product_id': product.id,
                'name': product.name,
                'qty': qty,
                'unit_price': product.selling_price,
                'line_total': line_cost
            })

    total_savings = calculated_mrp - calculated_final
    if total_savings < 0:
        total_savings = 0.0

    # 3. Create unique Order Code
    now_str = datetime.now().strftime('%Y%m%d')
    import random
    suffix = f"{random.randint(1000, 9999)}"
    order_code = f"FIF-{now_str}-{suffix}"

    new_order = Order(
        order_code=order_code,
        customer_name=name,
        customer_phone=phone,
        delivery_address=address,
        pincode=customer_pincode,
        delivery_notes=notes,
        total_mrp=round(calculated_mrp, 2),
        total_savings=round(total_savings, 2),
        final_amount=round(calculated_final, 2),
        status='NEW'
    )
    db.session.add(new_order)
    db.session.flush()

    for oi in order_items_payload:
        db_item = OrderItem(
            order_id=new_order.id,
            product_id=oi['product_id'],
            product_name=oi['name'],
            quantity=oi['qty'],
            unit_price=oi['unit_price'],
            line_total=oi['line_total']
        )
        db.session.add(db_item)

    db.session.commit()

    # 4. Compose WhatsApp Message
    wa_lines = [
        f"🔥 *NEW ORDER PLACED: {order_code}* 🔥",
        f"*Store:* Frost in Fire (Hyperlocal Frozen Food)",
        "",
        f"*Customer:* {name}",
        f"*Phone:* {phone}",
        f"*Delivery Address:* {address}",
        f"*Pincode:* {customer_pincode}",
    ]
    if notes:
        wa_lines.append(f"*Cooking/Delivery Note:* {notes}")

    wa_lines.append("")
    wa_lines.append("*--- ORDER BREAKDOWN ---*")
    for oi in order_items_payload:
        wa_lines.append(f"• {oi['name']} x {oi['qty']} = Rs. {oi['line_total']:.2f}")

    wa_lines.append("---------------------------")
    wa_lines.append(f"Original MRP: ~Rs. {calculated_mrp:.2f}~")
    wa_lines.append(f"Frost Discount Savings: -Rs. {total_savings:.2f}")
    wa_lines.append(f"*FINAL AMOUNT PAYABLE: Rs. {calculated_final:.2f}*")
    wa_lines.append("---------------------------")
    wa_lines.append("Please confirm delivery timeline & availability. Thank you!")

    full_message = "\\n".join(wa_lines)
    encoded_message = urllib.parse.quote(full_message)
    store_number = current_app.config['STORE_WHATSAPP_NUMBER']
    whatsapp_url = f"https://wa.me/{store_number}?text={encoded_message}"

    return jsonify({
        'success': True,
        'order_code': order_code,
        'whatsapp_url': whatsapp_url
    })
"""

FILES["app/blueprints/admin.py"] = """import os
import uuid
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from app import db
from app.models import User, Product, Order

admin_bp = Blueprint('admin_bp', __name__)

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_bp.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Signed in successfully!', 'success')
            return redirect(url_for('admin_bp.dashboard'))
        flash('Invalid username or password.', 'danger')

    return render_template('admin/login.html')

@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out safely.', 'info')
    return redirect(url_for('admin_bp.login'))

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    total_orders = Order.query.count()
    total_products = Product.query.count()
    pending_orders = Order.query.filter_by(status='NEW').count()
    recent_orders = Order.query.order_by(Order.id.desc()).limit(5).all()
    
    return render_template(
        'admin/dashboard.html',
        total_orders=total_orders,
        total_products=total_products,
        pending_orders=pending_orders,
        recent_orders=recent_orders,
        router_phone=current_app.config['STORE_WHATSAPP_NUMBER']
    )

@admin_bp.route('/products', methods=['GET', 'POST'])
@login_required
def products():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', 'Veg')
        mrp = float(request.form.get('mrp', 0.0))
        selling_price = float(request.form.get('selling_price', 0.0))
        
        # Photo upload handling (smartphone camera or PC files)
        file = request.files.get('image')
        image_url = None

        if file and file.filename:
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex[:10]}_{filename}"
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(upload_path)
            image_url = url_for('static', filename=f'uploads/{unique_filename}')
        else:
            # Fallback to category placeholder
            if category == 'Veg':
                image_url = "https://images.unsplash.com/photo-1541592106381-b31e9677c0e5?w=600&auto=format&fit=crop&q=80"
            else:
                image_url = "https://images.unsplash.com/photo-1562967914-608f82629710?w=600&auto=format&fit=crop&q=80"

        new_prod = Product(
            name=name,
            description=description,
            category=category,
            mrp=mrp,
            selling_price=selling_price,
            image_url=image_url
        )
        db.session.add(new_prod)
        db.session.commit()
        flash('New Frozen Product added to catalog!', 'success')
        return redirect(url_for('admin_bp.products'))

    all_products = Product.query.order_by(Product.id.desc()).all()
    return render_template('admin/products.html', products=all_products)

@admin_bp.route('/products/delete/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    prod = Product.query.get_or_404(product_id)
    db.session.delete(prod)
    db.session.commit()
    flash(f"Product '{prod.name}' deleted.", 'warning')
    return redirect(url_for('admin_bp.products'))

@admin_bp.route('/orders')
@login_required
def orders():
    all_orders = Order.query.order_by(Order.id.desc()).all()
    return render_template('admin/orders.html', orders=all_orders)

@admin_bp.route('/orders/status/<int:order_id>', methods=['POST'])
@login_required
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')
    if new_status in ['NEW', 'CONFIRMED', 'PACKED', 'DELIVERED', 'CANCELLED']:
        order.status = new_status
        db.session.commit()
        flash(f"Order #{order.order_code} marked as {new_status}!", 'success')
    return redirect(url_for('admin_bp.orders'))
"""

# ==========================================
# 4. STATIC ASSETS: CSS & JAVASCRIPT
# ==========================================
FILES["app/static/css/style.css"] = """/* ========================================================
   FROST IN FIRE - Core Brand Theme (Ice & Fire Aesthetic)
   ======================================================== */
:root {
  --fif-fire-primary: #E63946;
  --fif-fire-warm: #FF5722;
  --fif-ice-deep: #003459;
  --fif-ice-blue: #00A8E8;
  --fif-ice-bg: #F8F9FA;
  --fif-charcoal: #212529;
  --fif-success-green: #2E7D32;
  --fif-card-shadow: 0 10px 25px rgba(0, 52, 89, 0.08);
}

body {
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  background-color: var(--fif-ice-bg);
  color: var(--fif-charcoal);
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

main {
  flex: 1 0 auto;
}

/* BRAND NAVBAR */
.navbar-brand-frost {
  font-weight: 900;
  letter-spacing: -0.5px;
  color: var(--fif-fire-primary) !important;
  font-size: 1.35rem;
  display: inline-flex;
  align-items: center;
}
.navbar-brand-frost span {
  color: var(--fif-ice-deep);
}

.top-nav {
  background: #ffffff;
  border-bottom: 2px solid rgba(0, 168, 232, 0.2);
  box-shadow: 0 2px 10px rgba(0,0,0,0.04);
}

/* HEADER CART BUTTON */
.nav-cart-btn {
  background: linear-gradient(135deg, var(--fif-fire-primary), var(--fif-fire-warm));
  color: #ffffff !important;
  border-radius: 50px;
  font-weight: 700;
  padding: 0.45rem 1rem;
  border: none;
  box-shadow: 0 4px 12px rgba(230, 57, 70, 0.3);
  transition: transform 0.15s ease-in-out;
}
.nav-cart-btn:hover {
  transform: scale(1.04);
  color: #ffffff;
}

/* INDIAN FOOD SYMBOLS (Veg & Non-Veg) */
.food-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  border-radius: 3px;
  vertical-align: middle;
}
.food-badge.veg {
  border: 2px solid #28a745;
}
.food-badge.veg .badge-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #28a745;
}
.food-badge.non-veg {
  border: 2px solid #b02a37;
}
.food-badge.non-veg .badge-dot {
  width: 0; 
  height: 0; 
  border-left: 5px solid transparent;
  border-right: 5px solid transparent;
  border-bottom: 8px solid #b02a37;
}

/* PRODUCT CARDS */
.product-card {
  border: none;
  border-radius: 16px;
  overflow: hidden;
  background: #ffffff;
  box-shadow: var(--fif-card-shadow);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  height: 100%;
  display: flex;
  flex-direction: column;
}
.product-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 16px 30px rgba(0, 52, 89, 0.12);
}
.product-img-wrapper {
  position: relative;
  width: 100%;
  padding-top: 66%; /* 3:2 aspect ratio */
  background: #e9ecef;
  overflow: hidden;
}
.product-img-wrapper img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.discount-pill {
  position: absolute;
  top: 10px;
  left: 10px;
  background-color: #2E7D32;
  color: #ffffff;
  font-weight: 800;
  font-size: 0.75rem;
  padding: 4px 8px;
  border-radius: 8px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.25);
  letter-spacing: 0.5px;
}
.price-current {
  color: var(--fif-fire-primary);
  font-weight: 800;
  font-size: 1.3rem;
}
.price-mrp {
  color: #8d99ae;
  text-decoration: line-through;
  font-size: 0.95rem;
  margin-left: 6px;
}

.btn-frost-fire {
  background: linear-gradient(135deg, var(--fif-fire-primary), var(--fif-fire-warm));
  color: #ffffff;
  font-weight: 700;
  border: none;
  border-radius: 10px;
  transition: all 0.2s;
}
.btn-frost-fire:hover {
  background: linear-gradient(135deg, var(--fif-fire-warm), var(--fif-fire-primary));
  color: #ffffff;
  box-shadow: 0 4px 15px rgba(255, 87, 34, 0.4);
}

.btn-outline-ice {
  color: var(--fif-ice-deep);
  border: 1.5px solid var(--fif-ice-blue);
  border-radius: 50px;
  font-weight: 600;
}
.btn-outline-ice.active, .btn-outline-ice:hover {
  background: var(--fif-ice-deep);
  color: #ffffff;
  border-color: var(--fif-ice-deep);
}

/* SAVINGS CELEBRATION BANNER */
.savings-banner {
  background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
  border: 1px dashed #2E7D32;
  border-radius: 12px;
  padding: 12px 16px;
  color: #1b5e20;
  font-weight: 700;
}

/* STATUS BADGES */
.badge-status-NEW { background-color: #00A8E8; color: #fff; }
.badge-status-CONFIRMED { background-color: #003459; color: #fff; }
.badge-status-PACKED { background-color: #ff9800; color: #fff; }
.badge-status-DELIVERED { background-color: #2E7D32; color: #fff; }
.badge-status-CANCELLED { background-color: #d32f2f; color: #fff; }

/* TOAST / ALERTS */
#fif-toast-container {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 9999;
}
"""

FILES["app/static/js/cart.js"] = """/**
 * FROST IN FIRE - Cart & Hyperlocal Checkout Engine
 */

const FIF_CART_KEY = 'frost_in_fire_cart';

function getCart() {
  try {
    return JSON.parse(localStorage.getItem(FIF_CART_KEY)) || [];
  } catch (e) {
    return [];
  }
}

function saveCart(cart) {
  localStorage.setItem(FIF_CART_KEY, JSON.stringify(cart));
  updateCartBadge();
}

function updateCartBadge() {
  const cart = getCart();
  const totalCount = cart.reduce((acc, item) => acc + item.qty, 0);
  const badges = document.querySelectorAll('.cart-badge-count');
  badges.forEach(badge => {
    badge.textContent = totalCount;
  });
}

function showToast(message, type = 'info') {
  let container = document.getElementById('fif-toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'fif-toast-container';
    document.body.appendChild(container);
  }
  const toast = document.createElement('div');
  const bg = type === 'success' ? '#2E7D32' : (type === 'danger' ? '#d32f2f' : '#003459');
  toast.style.cssText = `background: ${bg}; color: #fff; padding: 12px 18px; border-radius: 10px; margin-top: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.2); font-weight: 600; font-size: 0.9rem; animation: fadeIn 0.3s forwards;`;
  toast.innerText = message;
  container.appendChild(toast);
  setTimeout(() => {
    toast.remove();
  }, 3200);
}

// 5 Arguments signature as requested
function addToCart(id, name, selling_price, mrp, image_url) {
  let cart = getCart();
  const existingIndex = cart.findIndex(item => item.id === Number(id));

  if (existingIndex > -1) {
    cart[existingIndex].qty += 1;
  } else {
    cart.push({
      id: Number(id),
      name: name,
      selling_price: Number(selling_price),
      mrp: Number(mrp),
      image_url: image_url,
      qty: 1
    });
  }
  saveCart(cart);
  showToast(`Added "${name}" to cart! 🔥`, 'success');
}

function changeQty(id, delta) {
  let cart = getCart();
  const idx = cart.findIndex(i => i.id === Number(id));
  if (idx > -1) {
    cart[idx].qty += delta;
    if (cart[idx].qty <= 0) {
      cart.splice(idx, 1);
    }
    saveCart(cart);
    renderCart();
  }
}

function removeItem(id) {
  let cart = getCart();
  cart = cart.filter(i => i.id !== Number(id));
  saveCart(cart);
  renderCart();
  showToast('Item removed from cart.', 'info');
}

function clearCart() {
  localStorage.removeItem(FIF_CART_KEY);
  updateCartBadge();
}

function cleanPincode(pin) {
  return String(pin || '').replace(/[^0-9]/g, '');
}

function renderCart() {
  const cartContainer = document.getElementById('cart-items-container');
  const summaryContainer = document.getElementById('cart-summary-container');
  if (!cartContainer || !summaryContainer) return;

  const cart = getCart();
  if (cart.length === 0) {
    cartContainer.innerHTML = `
      <div class="text-center py-5">
        <div style="font-size: 3.5rem;">❄️</div>
        <h4 class="mt-3 fw-bold">Your Freezer Bag is Empty</h4>
        <p class="text-muted">Fill it up with sizzling hot frozen snacks!</p>
        <a href="/" class="btn btn-frost-fire px-4 py-2 mt-2">Explore Frozen Treats</a>
      </div>
    `;
    summaryContainer.style.display = 'none';
    return;
  }

  summaryContainer.style.display = 'block';

  let itemsHtml = '';
  let totalMRP = 0;
  let finalAmount = 0;

  cart.forEach(item => {
    const lineMRP = item.mrp * item.qty;
    const lineTotal = item.selling_price * item.qty;
    totalMRP += lineMRP;
    finalAmount += lineTotal;

    itemsHtml += `
      <div class="card mb-3 border-0 shadow-sm rounded-3">
        <div class="card-body p-3">
          <div class="row align-items-center">
            <div class="col-3 col-md-2">
              <img src="${item.image_url}" alt="${item.name}" class="img-fluid rounded-3" style="aspect-ratio: 1/1; object-fit: cover;">
            </div>
            <div class="col-9 col-md-5">
              <h6 class="mb-1 fw-bold text-dark">${item.name}</h6>
              <div class="small">
                <span class="fw-bold text-danger">Rs. ${item.selling_price}</span>
                <span class="text-muted text-decoration-line-through ms-2">Rs. ${item.mrp}</span>
              </div>
            </div>
            <div class="col-6 col-md-3 mt-3 mt-md-0">
              <div class="input-group input-group-sm" style="max-width: 120px;">
                <button class="btn btn-outline-secondary" onclick="changeQty(${item.id}, -1)">-</button>
                <span class="input-group-text bg-white fw-bold px-3">${item.qty}</span>
                <button class="btn btn-outline-secondary" onclick="changeQty(${item.id}, 1)">+</button>
              </div>
            </div>
            <div class="col-6 col-md-2 mt-3 mt-md-0 text-end">
              <div class="fw-bold fs-6">Rs. ${lineTotal.toFixed(2)}</div>
              <button class="btn btn-sm text-danger p-0 mt-1" onclick="removeItem(${item.id})">
                <i class="bi bi-trash"></i> Remove
              </button>
            </div>
          </div>
        </div>
      </div>
    `;
  });

  const totalSavings = totalMRP - finalAmount;
  cartContainer.innerHTML = itemsHtml;

  document.getElementById('sum-total-mrp').innerText = `Rs. ${totalMRP.toFixed(2)}`;
  document.getElementById('sum-discount-savings').innerText = `- Rs. ${totalSavings.toFixed(2)}`;
  document.getElementById('sum-final-amount').innerText = `Rs. ${finalAmount.toFixed(2)}`;
  
  const banner = document.getElementById('sum-celebration-banner');
  if (banner) {
    if (totalSavings > 0) {
      banner.style.display = 'block';
      document.getElementById('sum-savings-text').innerText = `You are saving Rs. ${totalSavings.toFixed(2)} on this order! 🎉`;
    } else {
      banner.style.display = 'none';
    }
  }
}

async function handleWhatsAppCheckout(event, allowedPincode) {
  event.preventDefault();
  const cart = getCart();
  if (cart.length === 0) {
    showToast('Your cart is empty!', 'danger');
    return;
  }

  const name = document.getElementById('cust_name').value.trim();
  const phone = document.getElementById('cust_phone').value.trim();
  const address = document.getElementById('cust_address').value.trim();
  const rawPincode = document.getElementById('cust_pincode').value.trim();
  const notes = document.getElementById('cust_notes').value.trim();

  // HYPER-LOCAL FRONTEND PINCODE RESTRICTION
  const cleanedCustPin = cleanPincode(rawPincode);
  const cleanedTargetPin = cleanPincode(allowedPincode);

  if (cleanedCustPin !== cleanedTargetPin) {
    alert(`Frost in Fire is currently serving exclusively in Pincode ${allowedPincode}. We are expanding to your area soon!`);
    return;
  }

  const submitBtn = document.getElementById('btn-place-order');
  const originalText = submitBtn.innerHTML;
  submitBtn.disabled = true;
  submitBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span>Connecting WhatsApp...`;

  try {
    const response = await fetch('/api/orders', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: name,
        phone: phone,
        address: address,
        pincode: rawPincode,
        notes: notes,
        items: cart
      })
    });

    const result = await response.json();

    if (result.success) {
      clearCart();
      window.location.href = result.whatsapp_url;
    } else {
      alert(result.message || 'Failed to place order.');
      submitBtn.disabled = false;
      submitBtn.innerHTML = originalText;
    }
  } catch (err) {
    console.error(err);
    alert('An unexpected error occurred. Please check your network.');
    submitBtn.disabled = false;
    submitBtn.innerHTML = originalText;
  }
}

document.addEventListener('DOMContentLoaded', () => {
  updateCartBadge();
  renderCart();
});
"""

# ==========================================
# 5. JINJA2 TEMPLATES (PUBLIC & ADMIN)
# ==========================================
FILES["app/templates/base.html"] = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{% block title %}Frost in Fire - Hyperlocal Frozen Foods{% endblock %}</title>
  <meta name="description" content="Crispy, Fresh & Frozen to Perfection. Direct WhatsApp ordering for local frozen snacks & meats.">
  
  <!-- Bootstrap 5.3 & Icons -->
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
  <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>

  <!-- TOP HEADER NAVIGATION -->
  <nav class="navbar navbar-expand-lg top-nav sticky-top">
    <div class="container py-1">
      <a class="navbar-brand navbar-brand-frost" href="{{ url_for('public_bp.index') }}">
        <span class="me-1">❄️</span>FROST <span class="ms-1" style="color:var(--fif-fire-primary);">IN FIRE</span>
      </a>

      <div class="d-flex align-items-center ms-auto order-lg-last">
        <!-- Persistent Cart Button (Hidden only if on cart page) -->
        {% if request.endpoint != 'public_bp.cart' %}
        <a href="{{ url_for('public_bp.cart') }}" class="btn nav-cart-btn me-2 d-inline-flex align-items-center">
          <i class="bi bi-cart3 me-1"></i> Cart
          <span class="badge bg-white text-dark ms-2 rounded-pill cart-badge-count">0</span>
        </a>
        {% endif %}

        <button class="navbar-toggler border-0 shadow-none" type="button" data-bs-toggle="collapse" data-bs-target="#navMenu">
          <i class="bi bi-list fs-2"></i>
        </button>
      </div>

      <div class="collapse navbar-collapse" id="navMenu">
        <ul class="navbar-nav me-auto mb-2 mb-lg-0 mt-2 mt-lg-0">
          <li class="nav-nav-item">
            <a class="nav-link fw-semibold text-dark" href="{{ url_for('public_bp.index') }}">Full Menu</a>
          </li>
          <li class="nav-item">
            <a class="nav-link fw-semibold text-dark" href="{{ url_for('public_bp.index', category='veg') }}">Veg Specials</a>
          </li>
          <li class="nav-item">
            <a class="nav-link fw-semibold text-dark" href="{{ url_for('public_bp.index', category='non-veg') }}">Non-Veg Specials</a>
          </li>
          {% if current_user.is_authenticated %}
          <li class="nav-item">
            <a class="nav-link text-primary fw-bold" href="{{ url_for('admin_bp.dashboard') }}">Admin Suite</a>
          </li>
          {% endif %}
        </ul>
        <div class="d-none d-lg-block text-muted small">
          <i class="bi bi-geo-alt-fill text-danger"></i> Serving Pincode: <strong>{{ TARGET_PINCODE }}</strong>
        </div>
      </div>
    </div>
  </nav>

  <!-- FLASH MESSAGES -->
  <div class="container mt-3">
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% if messages %}
        {% for category, message in messages %}
          <div class="alert alert-{{ category }} alert-dismissible fade show" role="alert">
            {{ message }}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
          </div>
        {% endfor %}
      {% endif %}
    {% endwith %}
  </div>

  <main>
    {% block content %}{% endblock %}
  </main>

  <footer class="bg-white border-top py-4 mt-5">
    <div class="container text-center text-muted small">
      <div class="fw-bold fs-6 text-dark mb-1">FROST IN FIRE</div>
      <div>Crispy, Fresh & Frozen to Perfection • Hyperlocal Express Delivery</div>
      <div class="mt-2 text-danger fw-bold">Strictly Serving Pincode: {{ TARGET_PINCODE }}</div>
      <div class="mt-3">
        <a href="{{ url_for('admin_bp.login') }}" class="text-secondary text-decoration-none">Staff Login</a>
      </div>
    </div>
  </footer>

  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
  <script src="{{ url_for('static', filename='js/cart.js') }}"></script>
  {% block scripts %}{% endblock %}
</body>
</html>
"""

FILES["app/templates/public/index.html"] = """{% extends 'base.html' %}
{% block title %}Frost in Fire - Crispy, Fresh & Frozen to Perfection{% endblock %}

{% block content %}
<!-- HERO BANNER -->
<section class="py-4 py-md-5 text-white" style="background: linear-gradient(135deg, #003459, #00171f);">
  <div class="container text-center py-2">
    <span class="badge bg-danger px-3 py-2 rounded-pill fw-bold mb-2">⚡ 15-30 MIN FREEZER TO PAN</span>
    <h1 class="display-5 fw-black fw-bold">CRISPY, FRESH & FROZEN</h1>
    <p class="lead text-light mb-3">Premium frozen party appetizers, snacks & meats ready to sizzle at home.</p>
    <div class="d-inline-flex align-items-center bg-white text-dark px-3 py-2 rounded-pill shadow-sm small">
      <i class="bi bi-geo-alt-fill text-danger me-2"></i>
      <span>Delivering Exclusively to Pincode: <strong>{{ TARGET_PINCODE }}</strong></span>
    </div>
  </div>
</section>

<!-- CATEGORY FILTER PILLS -->
<section class="container mt-4 mb-4">
  <div class="d-flex justify-content-center gap-2">
    <a href="{{ url_for('public_bp.index') }}" class="btn btn-outline-ice px-4 {% if active_cat == 'all' %}active{% endif %}">
      All Snacks
    </a>
    <a href="{{ url_for('public_bp.index', category='veg') }}" class="btn btn-outline-ice px-4 {% if active_cat == 'veg' %}active{% endif %}">
      <span class="food-badge veg me-1"><span class="badge-dot"></span></span> Pure Veg
    </a>
    <a href="{{ url_for('public_bp.index', category='non-veg') }}" class="btn btn-outline-ice px-4 {% if active_cat == 'non-veg' %}active{% endif %}">
      <span class="food-badge non-veg me-1"><span class="badge-dot"></span></span> Non-Veg
    </a>
  </div>
</section>

<!-- PRODUCT CATALOG -->
<section class="container mb-5">
  <div class="row g-4">
    {% for product in products %}
    <div class="col-6 col-md-4 col-lg-3">
      <div class="product-card">
        <div class="product-img-wrapper">
          <img src="{{ product.image_url }}" alt="{{ product.name }}" loading="lazy">
          {% if product.discount_percent > 0 %}
          <div class="discount-pill">{{ product.discount_percent }}% OFF</div>
          {% endif %}
        </div>
        <div class="p-3 d-flex flex-column flex-grow-1">
          <div class="d-flex align-items-center justify-content-between mb-2">
            <span class="food-badge {{ 'veg' if product.category == 'Veg' else 'non-veg' }}" title="{{ product.category }}">
              <span class="badge-dot"></span>
            </span>
            <span class="badge bg-light text-secondary border small">{{ product.category }}</span>
          </div>

          <h5 class="fw-bold mb-1 fs-6 text-truncate" title="{{ product.name }}">{{ product.name }}</h5>
          <p class="text-muted small mb-3 flex-grow-1" style="display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;min-height:36px;">
            {{ product.description }}
          </p>

          <div class="d-flex align-items-baseline mb-3">
            <span class="price-current">Rs. {{ product.selling_price|int }}</span>
            <span class="price-mrp">Rs. {{ product.mrp|int }}</span>
          </div>

          <!-- Add to cart with 5 exact arguments -->
          <button class="btn btn-frost-fire w-100 py-2" 
                  onclick="addToCart('{{ product.id }}', '{{ product.name|replace(\"'\", \"\\\\'\") }}', '{{ product.selling_price }}', '{{ product.mrp }}', '{{ product.image_url }}')">
            <i class="bi bi-plus-circle me-1"></i> Add to Cart
          </button>
        </div>
      </div>
    </div>
    {% else %}
    <div class="col-12 text-center py-5">
      <p class="text-muted">No frozen products currently active in this category.</p>
    </div>
    {% endfor %}
  </div>
</section>
{% endblock %}
"""

FILES["app/templates/public/cart.html"] = """{% extends 'base.html' %}
{% block title %}Freezer Bag & WhatsApp Checkout - Frost in Fire{% endblock %}

{% block content %}
<div class="container py-4">
  <div class="row g-4">
    
    <!-- LEFT: CART ITEMS LIST -->
    <div class="col-lg-7">
      <div class="d-flex align-items-center justify-content-between mb-3">
        <h4 class="fw-bold mb-0">Your Freezer Bag</h4>
        <button class="btn btn-sm btn-outline-danger" onclick="clearCart()">Empty Cart</button>
      </div>
      <div id="cart-items-container">
        <!-- Rendered dynamically by cart.js -->
      </div>
    </div>

    <!-- RIGHT: SAVINGS BREAKDOWN & GUEST CHECKOUT -->
    <div class="col-lg-5" id="cart-summary-container" style="display:none;">
      
      <!-- SAVINGS CELEBRATION BANNER -->
      <div id="sum-celebration-banner" class="savings-banner mb-3 shadow-sm text-center" style="display:none;">
        <i class="bi bi-stars fs-5 me-1 text-success"></i>
        <span id="sum-savings-text">You are saving Rs. 0.00 on this order!</span>
      </div>

      <!-- PRICE BREAKDOWN CARD -->
      <div class="card border-0 shadow-sm rounded-3 mb-4">
        <div class="card-body p-4">
          <h5 class="fw-bold mb-3">Order Summary</h5>
          
          <div class="d-flex justify-content-between mb-2">
            <span class="text-muted">Original MRP Total:</span>
            <span class="text-decoration-line-through text-muted" id="sum-total-mrp">Rs. 0.00</span>
          </div>

          <div class="d-flex justify-content-between mb-2">
            <span class="text-success fw-bold">Frost Discount Savings:</span>
            <span class="text-success fw-bold" id="sum-discount-savings">- Rs. 0.00</span>
          </div>

          <hr>

          <div class="d-flex justify-content-between align-items-center">
            <span class="fs-5 fw-bold text-dark">Final Amount to Pay:</span>
            <span class="fs-4 fw-black fw-bold text-danger" id="sum-final-amount">Rs. 0.00</span>
          </div>
          <div class="small text-muted mt-1">* Payment settled directly with store owner on WhatsApp</div>
        </div>
      </div>

      <!-- GUEST CHECKOUT FORM (NO PASSWORDS, NO OTPS) -->
      <div class="card border-0 shadow-sm rounded-3">
        <div class="card-body p-4">
          <h5 class="fw-bold mb-3">Guest Delivery Details</h5>
          
          <form onsubmit="handleWhatsAppCheckout(event, '{{ TARGET_PINCODE }}')">
            <div class="mb-3">
              <label class="form-label small fw-bold">Your Full Name *</label>
              <input type="text" class="form-control" id="cust_name" required placeholder="e.g. Rahul Sharma">
            </div>

            <div class="mb-3">
              <label class="form-label small fw-bold">WhatsApp Mobile Number *</label>
              <input type="tel" class="form-control" id="cust_phone" required placeholder="e.g. 9876543210">
            </div>

            <div class="mb-3">
              <label class="form-label small fw-bold">Full Delivery Address (Flat / Wing / Building) *</label>
              <textarea class="form-control" id="cust_address" rows="2" required placeholder="e.g. Flat 402, Sunshine Heights, Main Road"></textarea>
            </div>

            <div class="mb-3">
              <label class="form-label small fw-bold">Pincode *</label>
              <input type="text" class="form-control fw-bold" id="cust_pincode" value="{{ TARGET_PINCODE }}" required>
              <div class="form-text small text-danger">Exclusively delivering to Pincode: {{ TARGET_PINCODE }}</div>
            </div>

            <div class="mb-4">
              <label class="form-label small fw-bold">Cooking / Delivery Instructions (Optional)</label>
              <input type="text" class="form-control" id="cust_notes" placeholder="e.g. Extra spicy dip, call before arriving">
            </div>

            <button type="submit" id="btn-place-order" class="btn btn-frost-fire w-100 py-3 fw-bold fs-6">
              <i class="bi bi-whatsapp me-2 fs-5"></i> Place Order via WhatsApp
            </button>
          </form>
        </div>
      </div>

    </div>
  </div>
</div>
{% endblock %}
"""

FILES["app/templates/public/order_success.html"] = """{% extends 'base.html' %}
{% block title %}Order Placed - Frost in Fire{% endblock %}

{% block content %}
<div class="container py-5 text-center">
  <div class="card border-0 shadow-sm rounded-4 p-4 mx-auto" style="max-width: 500px;">
    <div style="font-size: 3.5rem;">🔥</div>
    <h3 class="fw-bold mt-2">Order Confirmed!</h3>
    <p class="text-muted">Order Code: <strong class="text-danger">{{ order.order_code }}</strong></p>
    
    <div class="alert alert-light border text-start small">
      <strong>Customer:</strong> {{ order.customer_name }}<br>
      <strong>Deliver To:</strong> {{ order.delivery_address }} ({{ order.pincode }})<br>
      <strong>Payable on Delivery:</strong> Rs. {{ order.final_amount }}
    </div>

    <p class="small text-muted">Your order details have been forwarded to the kitchen via WhatsApp.</p>
    <a href="{{ url_for('public_bp.index') }}" class="btn btn-frost-fire mt-2">Order More Snacks</a>
  </div>
</div>
{% endblock %}
"""

# ==========================================
# 6. ADMIN JINJA2 TEMPLATES
# ==========================================
FILES["app/templates/admin/login.html"] = """{% extends 'base.html' %}
{% block title %}Admin Sign In - Frost in Fire{% endblock %}

{% block content %}
<div class="container py-5">
  <div class="row justify-content-center">
    <div class="col-md-5">
      <div class="card border-0 shadow-lg rounded-4 p-4">
        <div class="text-center mb-4">
          <h3 class="fw-bold text-dark">Staff Control Suite</h3>
          <p class="text-muted small">Sign in to manage catalog, stock and fulfillment</p>
        </div>
        <form method="POST" action="{{ url_for('admin_bp.login') }}">
          <div class="mb-3">
            <label class="form-label small fw-bold">Admin Username</label>
            <input type="text" name="username" class="form-control" required placeholder="admin">
          </div>
          <div class="mb-4">
            <label class="form-label small fw-bold">Password</label>
            <input type="password" name="password" class="form-control" required placeholder="••••••••">
          </div>
          <button type="submit" class="btn btn-frost-fire w-100 py-2 fw-bold">Sign In</button>
        </form>
      </div>
    </div>
  </div>
</div>
{% endblock %}
"""

FILES["app/templates/admin/dashboard.html"] = """{% extends 'base.html' %}
{% block title %}Admin Dashboard - Frost in Fire{% endblock %}

{% block content %}
<div class="container py-4">
  <div class="d-flex justify-content-between align-items-center mb-4">
    <div>
      <h3 class="fw-bold mb-0">Operational Dashboard</h3>
      <div class="text-muted small">Routing orders to WhatsApp: <strong>+{{ router_phone }}</strong></div>
    </div>
    <div>
      <a href="{{ url_for('admin_bp.products') }}" class="btn btn-outline-dark me-2">Products</a>
      <a href="{{ url_for('admin_bp.orders') }}" class="btn btn-frost-fire me-2">Orders Board</a>
      <a href="{{ url_for('admin_bp.logout') }}" class="btn btn-danger btn-sm">Sign Out</a>
    </div>
  </div>

  <!-- METRICS CARDS -->
  <div class="row g-3 mb-4">
    <div class="col-md-4">
      <div class="card border-0 shadow-sm rounded-3 p-3">
        <div class="text-muted small">Pending Fulfillment</div>
        <div class="fs-2 fw-bold text-danger">{{ pending_orders }}</div>
      </div>
    </div>
    <div class="col-md-4">
      <div class="card border-0 shadow-sm rounded-3 p-3">
        <div class="text-muted small">Total Orders Logged</div>
        <div class="fs-2 fw-bold text-primary">{{ total_orders }}</div>
      </div>
    </div>
    <div class="col-md-4">
      <div class="card border-0 shadow-sm rounded-3 p-3">
        <div class="text-muted small">Active Products in Freezer</div>
        <div class="fs-2 fw-bold text-success">{{ total_products }}</div>
      </div>
    </div>
  </div>

  <!-- RECENT ORDERS SNAPSHOT -->
  <div class="card border-0 shadow-sm rounded-3">
    <div class="card-header bg-white py-3">
      <h5 class="fw-bold mb-0">Recent Order Submissions</h5>
    </div>
    <div class="table-responsive">
      <table class="table align-middle mb-0">
        <thead class="table-light">
          <tr>
            <th>Order Code</th>
            <th>Customer</th>
            <th>Pincode</th>
            <th>Payable</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {% for order in recent_orders %}
          <tr>
            <td class="fw-bold">{{ order.order_code }}</td>
            <td>{{ order.customer_name }} ({{ order.customer_phone }})</td>
            <td>{{ order.pincode }}</td>
            <td class="fw-bold text-danger">Rs. {{ order.final_amount }}</td>
            <td><span class="badge badge-status-{{ order.status }}">{{ order.status }}</span></td>
          </tr>
          {% else %}
          <tr>
            <td colspan="5" class="text-center py-4 text-muted">No orders placed yet.</td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
  </div>
</div>
{% endblock %}
"""

FILES["app/templates/admin/products.html"] = """{% extends 'base.html' %}
{% block title %}Manage Catalog - Frost in Fire{% endblock %}

{% block content %}
<div class="container py-4">
  <div class="d-flex justify-content-between align-items-center mb-4">
    <h3 class="fw-bold mb-0">Product Catalog Management</h3>
    <a href="{{ url_for('admin_bp.dashboard') }}" class="btn btn-outline-secondary">Back to Dashboard</a>
  </div>

  <div class="row g-4">
    <!-- ADD PRODUCT FORM -->
    <div class="col-lg-4">
      <div class="card border-0 shadow-sm rounded-3 p-3">
        <h5 class="fw-bold mb-3">Add Frozen Snack</h5>
        <form method="POST" action="{{ url_for('admin_bp.products') }}" enctype="multipart/form-data">
          
          <div class="mb-2">
            <label class="form-label small fw-bold">Snack Name</label>
            <input type="text" name="name" class="form-control" required placeholder="e.g. Cheese Balls">
          </div>

          <div class="mb-2">
            <label class="form-label small fw-bold">Category</label>
            <select name="category" class="form-select">
              <option value="Veg">Pure Veg</option>
              <option value="Non-Veg">Non-Veg</option>
            </select>
          </div>

          <div class="row g-2 mb-2">
            <div class="col-6">
              <label class="form-label small fw-bold">MRP (Rs.)</label>
              <input type="number" step="0.5" name="mrp" class="form-control" required placeholder="200">
            </div>
            <div class="col-6">
              <label class="form-label small fw-bold">Selling Price</label>
              <input type="number" step="0.5" name="selling_price" class="form-control" required placeholder="160">
            </div>
          </div>

          <div class="mb-2">
            <label class="form-label small fw-bold">Upload Photo (PC or Phone Camera)</label>
            <input type="file" name="image" class="form-control" accept="image/*">
            <div class="form-text small">Instant capture from smartphone supported.</div>
          </div>

          <div class="mb-3">
            <label class="form-label small fw-bold">Short Description</label>
            <textarea name="description" class="form-control" rows="2" placeholder="Taste profile, pcs count, cooking mode"></textarea>
          </div>

          <button type="submit" class="btn btn-frost-fire w-100 py-2 fw-bold">Add to Catalog</button>
        </form>
      </div>
    </div>

    <!-- PRODUCTS LIST -->
    <div class="col-lg-8">
      <div class="card border-0 shadow-sm rounded-3">
        <div class="card-header bg-white py-3">
          <h5 class="fw-bold mb-0">Active Items ({{ products|length }})</h5>
        </div>
        <div class="table-responsive">
          <table class="table align-middle mb-0">
            <thead class="table-light">
              <tr>
                <th>Item</th>
                <th>Category</th>
                <th>Pricing</th>
                <th>Discount</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {% for p in products %}
              <tr>
                <td>
                  <div class="d-flex align-items-center">
                    <img src="{{ p.image_url }}" alt="{{ p.name }}" class="rounded me-2" style="width: 48px; height: 48px; object-fit: cover;">
                    <div class="fw-bold text-dark">{{ p.name }}</div>
                  </div>
                </td>
                <td>
                  <span class="food-badge {{ 'veg' if p.category == 'Veg' else 'non-veg' }} me-1">
                    <span class="badge-dot"></span>
                  </span>
                  {{ p.category }}
                </td>
                <td>
                  <div class="fw-bold">Rs. {{ p.selling_price }}</div>
                  <div class="text-muted small text-decoration-line-through">Rs. {{ p.mrp }}</div>
                </td>
                <td><span class="badge bg-success">{{ p.discount_percent }}% OFF</span></td>
                <td>
                  <form method="POST" action="{{ url_for('admin_bp.delete_product', product_id=p.id) }}" onsubmit="return confirm('Are you sure you want to delete this snack?');">
                    <button class="btn btn-sm btn-outline-danger"><i class="bi bi-trash"></i></button>
                  </form>
                </td>
              </tr>
              {% else %}
              <tr><td colspan="5" class="text-center py-4 text-muted">No items found.</td></tr>
              {% endfor %}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</div>
{% endblock %}
"""

FILES["app/templates/admin/orders.html"] = """{% extends 'base.html' %}
{% block title %}Orders Fulfillment Board - Frost in Fire{% endblock %}

{% block content %}
<div class="container py-4">
  <div class="d-flex justify-content-between align-items-center mb-4">
    <div>
      <h3 class="fw-bold mb-0">Orders Fulfillment Board</h3>
      <p class="text-muted small">Manage order states from New to Delivered</p>
    </div>
    <a href="{{ url_for('admin_bp.dashboard') }}" class="btn btn-outline-secondary">Back to Dashboard</a>
  </div>

  <div class="card border-0 shadow-sm rounded-3">
    <div class="table-responsive">
      <table class="table align-middle mb-0">
        <thead class="table-light">
          <tr>
            <th>Order Code</th>
            <th>Customer & Contact</th>
            <th>Delivery Address</th>
            <th>Itemized Order</th>
            <th>Final Amount</th>
            <th>Status Update</th>
          </tr>
        </thead>
        <tbody>
          {% for order in orders %}
          <tr>
            <td class="fw-bold">{{ order.order_code }}<br><small class="text-muted">{{ order.created_at.strftime('%d-%b %H:%M') }}</small></td>
            <td>
              <strong>{{ order.customer_name }}</strong><br>
              <a href="https://wa.me/{{ order.customer_phone }}" target="_blank" class="text-success small fw-bold">
                <i class="bi bi-whatsapp"></i> {{ order.customer_phone }}
              </a>
            </td>
            <td class="small" style="max-width: 200px;">
              {{ order.delivery_address }}<br>
              <strong class="text-danger">PIN: {{ order.pincode }}</strong>
              {% if order.delivery_notes %}
              <div class="text-primary mt-1"><em>Note: {{ order.delivery_notes }}</em></div>
              {% endif %}
            </td>
            <td>
              <ul class="list-unstyled mb-0 small">
                {% for item in order.items %}
                <li>• {{ item.product_name }} <strong>x {{ item.quantity }}</strong></li>
                {% endfor %}
              </ul>
            </td>
            <td class="fw-bold fs-6 text-danger">Rs. {{ order.final_amount }}</td>
            <td>
              <form method="POST" action="{{ url_for('admin_bp.update_order_status', order_id=order.id) }}" class="d-inline-flex gap-1">
                <select name="status" class="form-select form-select-sm" onchange="this.form.submit()">
                  {% for st in ['NEW', 'CONFIRMED', 'PACKED', 'DELIVERED', 'CANCELLED'] %}
                  <option value="{{ st }}" {% if order.status == st %}selected{% endif %}>{{ st }}</option>
                  {% endfor %}
                </select>
              </form>
            </td>
          </tr>
          {% else %}
          <tr>
            <td colspan="6" class="text-center py-4 text-muted">No orders logged yet.</td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
  </div>
</div>
{% endblock %}
"""

# ==========================================
# BUILDER EXECUTION LOGIC
# ==========================================
def main():
    print("=" * 65)
    print(" 🔥 GENERATING 'FROST IN FIRE' LOCAL E-COMMERCE ENGINE 🔥 ")
    print("=" * 65)

    base_dir = os.path.abspath(os.path.dirname(__file__))

    for rel_path, content in FILES.items():
        full_path = os.path.join(base_dir, rel_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f" [+] Created: {rel_path}")

    print("\n" + "=" * 65)
    print(" SUCCESS! Project files written successfully.")
    print("=" * 65)
    print("\nNext steps to run the application:\n")
    print("1. Install dependencies:")
    print("   pip install -r requirements.txt\n")
    print("2. (Optional) Set your custom WhatsApp number and Pincode:")
    print("   export DELIVERY_PINCODE='400011'             # On Windows: set DELIVERY_PINCODE=400011")
    print("   export STORE_WHATSAPP_NUMBER='919876543210'  # On Windows: set STORE_WHATSAPP_NUMBER=919876543210\n")
    print("3. Start the application:")
    print("   python run.py\n")
    print("4. Access:")
    print("   - Storefront: http://127.0.0.1:5000")
    print("   - Admin:      http://127.0.0.1:5000/admin/login")
    print("     Credentials: admin / FrostFire@2026")
    print("   - Mobile: Connect your phone to the same Wi-Fi and open http://<YOUR_PC_IP>:5000\n")

if __name__ == '__main__':
    main()