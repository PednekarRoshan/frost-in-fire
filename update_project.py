#!/usr/bin/env python3
"""
FROST IN FIRE - Automated Feature Updater
Adds Admin WhatsApp Phone Management & Live Order Routing
"""

import os
import sqlite3

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

FILES = {}

# ==========================================
# 1. UPDATED: app/models.py (Added user phone)
# ==========================================
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
    phone = db.Column(db.String(20), default='919876543210')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(20), nullable=False)
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
    status = db.Column(db.String(20), default='NEW')
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
# 2. UPDATED: app/blueprints/admin.py (Added update-phone route)
# ==========================================
FILES["app/blueprints/admin.py"] = """import os
import re
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
    
    current_phone = current_user.phone or current_app.config.get('STORE_WHATSAPP_NUMBER', '919876543210')
    
    return render_template(
        'admin/dashboard.html',
        total_orders=total_orders,
        total_products=total_products,
        pending_orders=pending_orders,
        recent_orders=recent_orders,
        router_phone=current_phone
    )

@admin_bp.route('/update-phone', methods=['POST'])
@login_required
def update_phone():
    new_phone = request.form.get('phone', '').strip()
    clean_phone = re.sub(r'[^0-9]', '', new_phone)

    if len(clean_phone) < 10:
        flash('Please enter a valid phone number with country code (e.g., 919876543210).', 'danger')
    else:
        current_user.phone = clean_phone
        db.session.commit()
        flash(f'WhatsApp order routing number updated to +{clean_phone}!', 'success')

    return redirect(url_for('admin_bp.dashboard'))

@admin_bp.route('/products', methods=['GET', 'POST'])
@login_required
def products():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', 'Veg')
        mrp = float(request.form.get('mrp', 0.0))
        selling_price = float(request.form.get('selling_price', 0.0))
        
        file = request.files.get('image')
        image_url = None

        if file and file.filename:
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex[:10]}_{filename}"
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(upload_path)
            image_url = url_for('static', filename=f'uploads/{unique_filename}')
        else:
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
# 3. UPDATED: app/blueprints/public.py (Dynamic WhatsApp number)
# ==========================================
FILES["app/blueprints/public.py"] = """import re
import urllib.parse
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, current_app
from app import db
from app.models import Product, Order, OrderItem, User

public_bp = Blueprint('public_bp', __name__)

def clean_pincode(pin: str) -> str:
    return re.sub(r'[^0-9]', '', str(pin or ''))

def get_active_store_phone() -> str:
    admin = User.query.filter_by(username='admin').first()
    if admin and admin.phone:
        return admin.phone
    return current_app.config.get('STORE_WHATSAPP_NUMBER', '919876543210')

@public_bp.context_processor
def inject_config():
    return {
        'TARGET_PINCODE': current_app.config['DELIVERY_PINCODE'],
        'STORE_PHONE': get_active_store_phone()
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

    # Route dynamically to saved Admin number
    store_number = get_active_store_phone()
    whatsapp_url = f"https://wa.me/{store_number}?text={encoded_message}"

    return jsonify({
        'success': True,
        'order_code': order_code,
        'whatsapp_url': whatsapp_url
    })
"""

# ==========================================
# 4. UPDATED: app/templates/admin/dashboard.html
# ==========================================
FILES["app/templates/admin/dashboard.html"] = """{% extends 'base.html' %}
{% block title %}Admin Dashboard - Frost in Fire{% endblock %}

{% block content %}
<div class="container py-4">
  <div class="d-flex justify-content-between align-items-center mb-4">
    <div>
      <h3 class="fw-bold mb-0">Operational Dashboard</h3>
      <div class="text-muted small">Current WhatsApp Router: <strong class="text-success">+{{ router_phone }}</strong></div>
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

  <!-- WHATSAPP NUMBER SETTINGS CARD -->
  <div class="card border-0 shadow-sm rounded-3 mb-4">
    <div class="card-body p-4">
      <div class="row align-items-center">
        <div class="col-lg-7">
          <h5 class="fw-bold mb-1"><i class="bi bi-whatsapp text-success me-2"></i>Order Routing WhatsApp Number</h5>
          <p class="text-muted small mb-0">
            Incoming customer orders from checkout will open this WhatsApp chat. Format: Country Code + Phone (e.g. <code>919876543210</code>).
          </p>
        </div>
        <div class="col-lg-5 mt-3 mt-lg-0">
          <form method="POST" action="{{ url_for('admin_bp.update_phone') }}" class="d-flex gap-2">
            <input type="text" name="phone" class="form-control" value="{{ router_phone }}" required placeholder="919876543210">
            <button type="submit" class="btn btn-success fw-bold text-nowrap">Save Number</button>
          </form>
          <div class="mt-2 text-end">
            <a href="https://wa.me/{{ router_phone }}?text=Frost%20in%20Fire%20Routing%20Test" target="_blank" class="small text-decoration-none text-muted">
              <i class="bi bi-box-arrow-up-right me-1"></i>Test WhatsApp Link
            </a>
          </div>
        </div>
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

# ==========================================
# 5. UPDATED: run.py
# ==========================================
FILES["run.py"] = """import os
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

if __name__ == '__main__':
    seed_database()
    print("\\n=======================================================")
    print(" FROST IN FIRE Server Running!")
    print(" Access on PC:      http://127.0.0.1:5000")
    print(" Admin Portal:      http://127.0.0.1:5000/admin/login")
    print("=======================================================\\n")
    app.run(host='0.0.0.0', port=5000, debug=True)
"""

def main():
    print("=" * 60)
    print(" Applying Admin Phone Management Update...")
    print("=" * 60)

    # 1. Overwrite updated application files
    for rel_path, content in FILES.items():
        full_path = os.path.join(BASE_DIR, rel_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f" [+] Updated: {rel_path}")

    # 2. Safely migrate existing SQLite database if it exists
    db_file = os.path.join(BASE_DIR, "instance", "frostinfire.db")
    if os.path.exists(db_file):
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            cursor.execute("ALTER TABLE users ADD COLUMN phone VARCHAR(20) DEFAULT '919876543210'")
            conn.commit()
            conn.close()
            print(" [+] Database Migrated: Added 'phone' column to 'users' table.")
        except sqlite3.OperationalError:
            print(" [i] Database column 'phone' already active.")

    print("\n" + "=" * 60)
    print(" Update Completed Successfully!")
    print("=" * 60)
    print("Now run the server:")
    print("    python run.py\n")

if __name__ == '__main__':
    main()