/**
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
