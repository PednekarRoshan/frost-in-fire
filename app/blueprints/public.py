import re
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

    full_message = "\n".join(wa_lines)
    encoded_message = urllib.parse.quote(full_message)

    # Route dynamically to saved Admin number
    store_number = get_active_store_phone()
    whatsapp_url = f"https://wa.me/{store_number}?text={encoded_message}"

    return jsonify({
        'success': True,
        'order_code': order_code,
        'whatsapp_url': whatsapp_url
    })
