import os
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
