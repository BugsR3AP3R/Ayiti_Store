// AyitiStore - Main JS

document.addEventListener('DOMContentLoaded', function () {

  // ===== CART AJAX =====
  document.querySelectorAll('.add-to-cart-btn').forEach(btn => {
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      const productId = this.dataset.productId;
      const size = document.querySelector('.size-btn.active')?.dataset.size || '';
      const color = document.querySelector('.color-dot.active')?.dataset.color || '';
      const qty = document.querySelector('#qty-input')?.value || 1;

      fetch(`/panier/ajouter/${productId}/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCookie('csrftoken'),
          'X-Requested-With': 'XMLHttpRequest',
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `size=${size}&color=${color}&quantity=${qty}`
      })
        .then(r => r.json())
        .then(data => {
          if (data.success) {
            updateCartBadge(data.cart_count);
            showToast('✓ Article ajouté au panier!', 'success');
          }
        });
    });
  });

  // ===== WISHLIST AJAX =====
  document.querySelectorAll('.wishlist-btn').forEach(btn => {
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      const productId = this.dataset.productId;
      fetch(`/favoris/toggle/${productId}/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCookie('csrftoken'),
          'X-Requested-With': 'XMLHttpRequest',
        }
      })
        .then(r => r.json())
        .then(data => {
          const icon = this.querySelector('i');
          if (data.action === 'added') {
            this.classList.add('active');
            if (icon) { icon.classList.remove('bi-heart'); icon.classList.add('bi-heart-fill'); }
            showToast('♥ Ajouté aux favoris!', 'success');
          } else {
            this.classList.remove('active');
            if (icon) { icon.classList.add('bi-heart'); icon.classList.remove('bi-heart-fill'); }
            showToast('Retiré des favoris', 'info');
          }
          updateWishlistBadge(data.wishlist_count);
        });
    });
  });

  // ===== CART QTY =====
  document.querySelectorAll('.qty-btn').forEach(btn => {
    btn.addEventListener('click', function () {
      const itemId = this.dataset.itemId;
      const display = document.querySelector(`#qty-${itemId}`);
      if (!display) return;
      let qty = parseInt(display.value);
      if (this.dataset.action === 'plus') qty++;
      else if (this.dataset.action === 'minus' && qty > 1) qty--;
      else if (this.dataset.action === 'minus' && qty <= 1) {
        if (confirm('Retirer cet article du panier?')) removeCartItem(itemId);
        return;
      }
      display.value = qty;
      updateCartQty(itemId, qty);
    });
  });

  // ===== PRODUCT GALLERY =====
  document.querySelectorAll('.thumb-img').forEach(thumb => {
    thumb.addEventListener('click', function () {
      const mainImg = document.querySelector('#main-product-img');
      if (mainImg) mainImg.src = this.src;
      document.querySelectorAll('.thumb-img').forEach(t => t.classList.remove('active'));
      this.classList.add('active');
    });
  });

  // ===== SIZE SELECT =====
  document.querySelectorAll('.size-btn').forEach(btn => {
    btn.addEventListener('click', function () {
      document.querySelectorAll('.size-btn').forEach(b => b.classList.remove('active'));
      this.classList.add('active');
    });
  });

  // ===== COLOR SELECT =====
  document.querySelectorAll('.color-dot').forEach(dot => {
    dot.addEventListener('click', function () {
      document.querySelectorAll('.color-dot').forEach(d => d.classList.remove('active'));
      this.classList.add('active');
    });
  });

  // ===== PAYMENT OPTIONS =====
  document.querySelectorAll('.payment-option').forEach(opt => {
    opt.addEventListener('click', function () {
      document.querySelectorAll('.payment-option').forEach(o => o.classList.remove('selected'));
      this.classList.add('selected');
      const radio = this.querySelector('input[type=radio]');
      if (radio) radio.checked = true;
      const method = this.dataset.method;
      showPaymentFields(method);
    });
  });

  // ===== QTY INPUT inline =====
  const qtyInput = document.querySelector('#qty-input');
  if (qtyInput) {
    document.querySelector('#qty-plus')?.addEventListener('click', () => {
      qtyInput.value = parseInt(qtyInput.value) + 1;
    });
    document.querySelector('#qty-minus')?.addEventListener('click', () => {
      if (parseInt(qtyInput.value) > 1) qtyInput.value = parseInt(qtyInput.value) - 1;
    });
  }

  // Auto-dismiss alerts
  setTimeout(() => {
    document.querySelectorAll('.auto-dismiss').forEach(el => {
      el.style.opacity = '0';
      el.style.transition = 'opacity 0.5s';
      setTimeout(() => el.remove(), 500);
    });
  }, 4000);
});

// ===== HELPERS =====
function getCookie(name) {
  let v = document.cookie.match('(^|;) ?' + name + '=([^;]*)(;|$)');
  return v ? v[2] : null;
}

function updateCartBadge(count) {
  document.querySelectorAll('.cart-badge').forEach(b => {
    b.textContent = count;
    b.style.display = count > 0 ? 'inline-flex' : 'none';
  });
}

function updateWishlistBadge(count) {
  document.querySelectorAll('.wishlist-badge').forEach(b => {
    b.textContent = count;
    b.style.display = count > 0 ? 'inline-flex' : 'none';
  });
}

function updateCartQty(itemId, qty) {
  fetch(`/panier/modifier/${itemId}/`, {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCookie('csrftoken'),
      'X-Requested-With': 'XMLHttpRequest',
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: `quantity=${qty}`
  })
    .then(r => r.json())
    .then(data => {
      if (data.success) {
        const itemTotalEl = document.querySelector(`#item-total-${itemId}`);
        if (itemTotalEl) itemTotalEl.textContent = formatHTG(data.item_total);
        const subtotalEl = document.querySelector('#cart-subtotal');
        if (subtotalEl) subtotalEl.textContent = formatHTG(data.cart_subtotal);
        updateCartBadge(data.cart_count);
      }
    });
}

function removeCartItem(itemId) {
  fetch(`/panier/retirer/${itemId}/`, {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCookie('csrftoken'),
      'X-Requested-With': 'XMLHttpRequest',
    }
  })
    .then(r => r.json())
    .then(data => {
      if (data.success) {
        const row = document.querySelector(`#cart-item-${itemId}`);
        if (row) { row.style.opacity = '0'; setTimeout(() => row.remove(), 300); }
        updateCartBadge(data.cart_count);
      }
    });
}

function showToast(message, type = 'success') {
  let toast = document.querySelector('#global-toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'global-toast';
    toast.className = 'toast-ayiti';
    document.body.appendChild(toast);
  }
  toast.innerHTML = message;
  toast.className = 'toast-ayiti show';
  setTimeout(() => toast.classList.remove('show'), 3000);
}

function showPaymentFields(method) {
  document.querySelectorAll('.payment-fields').forEach(f => f.style.display = 'none');
  const fields = document.querySelector(`#fields-${method}`);
  if (fields) fields.style.display = 'block';
}

function formatHTG(amount) {
  return new Intl.NumberFormat('fr-HT', { minimumFractionDigits: 2 }).format(amount) + ' HTG';
}

// Animated number counter
document.querySelectorAll('.stat-num[data-target]').forEach(el => {
  const target = parseInt(el.dataset.target);
  let count = 0;
  const step = target / 60;
  const timer = setInterval(() => {
    count += step;
    if (count >= target) { el.textContent = el.dataset.suffix ? target + el.dataset.suffix : target + '+'; clearInterval(timer); }
    else el.textContent = Math.floor(count) + (el.dataset.suffix || '+');
  }, 30);
});
