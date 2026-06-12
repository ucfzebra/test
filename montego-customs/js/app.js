/* Montego Customs — cart engine + page controllers
   Pages declare themselves via <body data-page="...">           */

/* ═══════════════ CART STORAGE ═══════════════ */

const CART_KEY = "mc_cart_v1";

function loadCart() {
  try { return JSON.parse(localStorage.getItem(CART_KEY)) || []; }
  catch { return []; }
}

function saveCart(cart) {
  localStorage.setItem(CART_KEY, JSON.stringify(cart));
  renderCartCount();
}

function cartLineKey(id, option) { return id + "::" + (option || ""); }

function addToCart(id, qty, option) {
  const product = getProduct(id);
  if (!product) return;
  qty = Math.max(1, parseInt(qty, 10) || 1);
  const cart = loadCart();
  const key = cartLineKey(id, option);
  const line = cart.find(l => l.key === key);
  if (line) line.qty += qty;
  else cart.push({ key, id, option: option || null, qty });
  saveCart(cart);
  toast(`<b>${product.name}</b> added to cart`);
}

function setQty(key, qty) {
  const cart = loadCart();
  const line = cart.find(l => l.key === key);
  if (!line) return;
  line.qty = Math.max(1, parseInt(qty, 10) || 1);
  saveCart(cart);
}

function removeLine(key) {
  saveCart(loadCart().filter(l => l.key !== key));
}

function clearCart() { saveCart([]); }

function cartTotals() {
  const cart = loadCart();
  let subtotal = 0, count = 0;
  for (const l of cart) {
    const p = getProduct(l.id);
    if (!p) continue;
    subtotal += p.price * l.qty;
    count += l.qty;
  }
  const shipping = count === 0 ? 0 : (subtotal >= 150 ? 0 : 12);
  const tax = +(subtotal * 0.07).toFixed(2);
  return { subtotal, shipping, tax, total: subtotal + shipping + tax, count };
}

/* ═══════════════ SHARED UI ═══════════════ */

function renderCartCount() {
  const el = document.querySelector(".cart-count");
  if (el) el.textContent = cartTotals().count;
}

let toastTimer = null;
function toast(html) {
  let el = document.getElementById("toast");
  if (!el) {
    el = document.createElement("div");
    el.id = "toast";
    document.body.appendChild(el);
  }
  el.innerHTML = html;
  el.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => el.classList.remove("show"), 2600);
}

function productCard(p) {
  return `
    <article class="card">
      <div class="thumb">
        <a href="product.html?id=${p.id}"><img src="${p.image}" alt="${p.name}"></a>
        ${p.badge ? `<span class="badge">${p.badge}</span>` : ""}
      </div>
      <div class="body">
        <span class="cat">${p.categoryLabel}</span>
        <h3><a href="product.html?id=${p.id}">${p.name}</a></h3>
        <p class="short">${p.short}</p>
        <div class="row">
          <span class="price">${formatPrice(p.price)}</span>
          <button class="btn ghost sm" data-add="${p.id}">Add to Cart</button>
        </div>
      </div>
    </article>`;
}

function bindAddButtons(scope) {
  (scope || document).querySelectorAll("[data-add]").forEach(btn => {
    btn.addEventListener("click", () => addToCart(btn.dataset.add, 1, null));
  });
}

/* ═══════════════ PAGE CONTROLLERS ═══════════════ */

function initHome() {
  const featured = ["mc-002", "mc-013", "mc-010", "mc-016", "mc-007", "mc-004", "mc-014", "mc-008"];
  const grid = document.getElementById("featured-grid");
  grid.innerHTML = featured.map(id => productCard(getProduct(id))).join("");
  bindAddButtons(grid);
}

function initShop() {
  const grid = document.getElementById("shop-grid");
  const buttons = document.querySelectorAll(".filter-bar button");
  const params = new URLSearchParams(location.search);
  let active = params.get("cat") || "all";

  function draw() {
    const list = active === "all" ? PRODUCTS : PRODUCTS.filter(p => p.category === active);
    grid.innerHTML = list.map(productCard).join("");
    bindAddButtons(grid);
    buttons.forEach(b => b.classList.toggle("on", b.dataset.cat === active));
    const head = document.getElementById("shop-blurb");
    if (head) head.textContent = active === "all"
      ? `${PRODUCTS.length} pieces, engraved to order in our studio.`
      : CATEGORIES[active].blurb;
  }

  buttons.forEach(b => b.addEventListener("click", () => {
    active = b.dataset.cat;
    history.replaceState(null, "", active === "all" ? "shop.html" : `shop.html?cat=${active}`);
    draw();
  }));
  draw();
}

function initProduct() {
  const id = new URLSearchParams(location.search).get("id");
  const p = getProduct(id);
  const mount = document.getElementById("pdp-mount");
  if (!p) {
    mount.innerHTML = `<div class="empty-state"><h2>Piece not found</h2>
      <p>That item may have been retired from the catalog.</p>
      <a class="btn" href="shop.html">Back to the Shop</a></div>`;
    return;
  }
  document.title = `${p.name} — Montego Customs`;
  mount.innerHTML = `
    <nav class="crumbs wrap"><a href="index.html">Home</a> / <a href="shop.html?cat=${p.category}">${p.categoryLabel}</a> / ${p.name}</nav>
    <div class="pdp wrap">
      <div class="photo"><img src="${p.image}" alt="${p.name}"></div>
      <div>
        <span class="kicker">${p.categoryLabel}</span>
        <h1>${p.name}</h1>
        <div class="price">${formatPrice(p.price)}</div>
        <p class="desc">${p.description}</p>
        <label for="opt">${p.options.label}</label>
        <select id="opt">${p.options.values.map(v => `<option>${v}</option>`).join("")}</select>
        <label>Quantity</label>
        <div class="qty">
          <button type="button" id="qdown" aria-label="Decrease quantity">−</button>
          <input id="qty" type="number" min="1" value="1">
          <button type="button" id="qup" aria-label="Increase quantity">+</button>
        </div>
        <button class="btn block" id="add-btn">Add to Cart — ${formatPrice(p.price)}</button>
        <div class="trust">
          <span>Engraved to order in 3–5 business days</span>
          <span>Free shipping on orders over $150</span>
          <span>Proof sent for approval on all custom artwork</span>
        </div>
      </div>
    </div>`;

  const qty = document.getElementById("qty");
  const updateBtn = () => {
    const n = Math.max(1, parseInt(qty.value, 10) || 1);
    document.getElementById("add-btn").textContent = `Add to Cart — ${formatPrice(p.price * n)}`;
  };
  document.getElementById("qdown").onclick = () => { qty.value = Math.max(1, (+qty.value || 1) - 1); updateBtn(); };
  document.getElementById("qup").onclick = () => { qty.value = (+qty.value || 1) + 1; updateBtn(); };
  qty.addEventListener("input", updateBtn);
  document.getElementById("add-btn").onclick = () =>
    addToCart(p.id, qty.value, document.getElementById("opt").value);
}

function initCart() {
  const mount = document.getElementById("cart-mount");

  function draw() {
    const cart = loadCart();
    if (cart.length === 0) {
      mount.innerHTML = `<div class="empty-state wrap">
        <h2>Your cart is empty</h2>
        <p>Nothing on the laser bed yet. Let's fix that.</p>
        <a class="btn" href="shop.html">Browse the Shop</a></div>`;
      return;
    }
    const t = cartTotals();
    mount.innerHTML = `
      <div class="cart-layout wrap">
        <div class="cart-lines">
          ${cart.map(l => {
            const p = getProduct(l.id);
            return `
            <div class="cart-line" data-key="${l.key}">
              <img src="${p.image}" alt="${p.name}">
              <div>
                <h3><a href="product.html?id=${p.id}">${p.name}</a></h3>
                ${l.option ? `<div class="meta">${p.options.label}: ${l.option}</div>` : ""}
                <div class="unit">${formatPrice(p.price)} each</div>
              </div>
              <div class="right">
                <span class="line-total">${formatPrice(p.price * l.qty)}</span>
                <div class="qty">
                  <button type="button" data-step="-1" aria-label="Decrease">−</button>
                  <input type="number" min="1" value="${l.qty}">
                  <button type="button" data-step="1" aria-label="Increase">+</button>
                </div>
                <button class="remove-btn">Remove</button>
              </div>
            </div>`;
          }).join("")}
        </div>
        <aside class="summary">
          <h2>Order Summary</h2>
          <div class="row"><span>Subtotal (${t.count} item${t.count === 1 ? "" : "s"})</span><span>${formatPrice(t.subtotal)}</span></div>
          <div class="row"><span>Shipping</span><span>${t.shipping === 0 ? "Free" : formatPrice(t.shipping)}</span></div>
          <div class="row"><span>Estimated tax (7%)</span><span>${formatPrice(t.tax)}</span></div>
          <div class="row total"><span>Total</span><span>${formatPrice(t.total)}</span></div>
          <a class="btn block" href="checkout.html">Proceed to Checkout</a>
          <p class="note">Free shipping on orders over $150. Custom artwork proofs are emailed before anything hits the laser.</p>
        </aside>
      </div>`;

    mount.querySelectorAll(".cart-line").forEach(row => {
      const key = row.dataset.key;
      const input = row.querySelector("input");
      row.querySelectorAll("[data-step]").forEach(b =>
        b.addEventListener("click", () => {
          setQty(key, (+input.value || 1) + (+b.dataset.step));
          draw();
        }));
      input.addEventListener("change", () => { setQty(key, input.value); draw(); });
      row.querySelector(".remove-btn").addEventListener("click", () => { removeLine(key); draw(); });
    });
  }
  draw();
}

function initCheckout() {
  const mount = document.getElementById("checkout-summary");
  const cart = loadCart();
  if (cart.length === 0) {
    document.getElementById("checkout-mount").innerHTML = `<div class="empty-state wrap">
      <h2>Nothing to check out</h2>
      <p>Your cart is empty — add a piece or two first.</p>
      <a class="btn" href="shop.html">Browse the Shop</a></div>`;
    return;
  }
  const t = cartTotals();
  mount.innerHTML = `
    <h2>Your Order</h2>
    ${cart.map(l => {
      const p = getProduct(l.id);
      return `<div class="row"><span>${p.name} × ${l.qty}</span><span>${formatPrice(p.price * l.qty)}</span></div>`;
    }).join("")}
    <div class="row"><span>Shipping</span><span>${t.shipping === 0 ? "Free" : formatPrice(t.shipping)}</span></div>
    <div class="row"><span>Tax (7%)</span><span>${formatPrice(t.tax)}</span></div>
    <div class="row total"><span>Total</span><span>${formatPrice(t.total)}</span></div>
    <p class="note">Demo storefront — no payment is processed and no card data leaves this page.</p>`;

  const form = document.getElementById("checkout-form");

  // formatting niceties
  const cardNo = form.elements.cardNumber;
  cardNo.addEventListener("input", () => {
    cardNo.value = cardNo.value.replace(/\D/g, "").slice(0, 16).replace(/(.{4})/g, "$1 ").trim();
  });
  const exp = form.elements.cardExp;
  exp.addEventListener("input", () => {
    let v = exp.value.replace(/\D/g, "").slice(0, 4);
    exp.value = v.length > 2 ? v.slice(0, 2) + "/" + v.slice(2) : v;
  });
  form.elements.cardCvc.addEventListener("input", e => {
    e.target.value = e.target.value.replace(/\D/g, "").slice(0, 4);
  });

  form.addEventListener("submit", e => {
    e.preventDefault();
    let ok = true;
    form.querySelectorAll(".field").forEach(f => {
      const input = f.querySelector("input, select");
      let valid = input.value.trim().length > 0;
      if (valid && input.name === "email") valid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(input.value);
      if (valid && input.name === "cardNumber") valid = input.value.replace(/\s/g, "").length >= 15;
      if (valid && input.name === "cardExp") valid = /^\d{2}\/\d{2}$/.test(input.value);
      if (valid && input.name === "cardCvc") valid = input.value.length >= 3;
      f.classList.toggle("invalid", !valid);
      if (!valid) ok = false;
    });
    if (!ok) {
      toast("Please fix the highlighted fields");
      form.querySelector(".field.invalid input, .field.invalid select")?.focus();
      return;
    }
    const orderNo = "MC-" + Date.now().toString(36).toUpperCase().slice(-6);
    sessionStorage.setItem("mc_last_order", JSON.stringify({
      orderNo,
      email: form.elements.email.value,
      total: cartTotals().total
    }));
    clearCart();
    location.href = "confirmation.html";
  });
}

function initConfirmation() {
  let order = null;
  try { order = JSON.parse(sessionStorage.getItem("mc_last_order")); } catch {}
  if (order) {
    document.getElementById("order-no").textContent = "Order " + order.orderNo;
    document.getElementById("order-email").innerHTML =
      `A confirmation and your engraving proof timeline are headed to <b>${order.email}</b>.`;
    document.getElementById("order-total").textContent =
      "Total charged (demo): " + formatPrice(order.total);
  }
}

function initQuote() {
  const form = document.getElementById("quote-form");
  form.addEventListener("submit", e => {
    e.preventDefault();
    let ok = true;
    form.querySelectorAll(".field[data-required]").forEach(f => {
      const input = f.querySelector("input, select, textarea");
      let valid = input.value.trim().length > 0;
      if (valid && input.name === "email") valid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(input.value);
      f.classList.toggle("invalid", !valid);
      if (!valid) ok = false;
    });
    if (!ok) { toast("Please fix the highlighted fields"); return; }
    form.style.display = "none";
    document.getElementById("quote-thanks").style.display = "block";
    window.scrollTo({ top: 0, behavior: "smooth" });
  });
}

/* ═══════════════ BOOT ═══════════════ */

document.addEventListener("DOMContentLoaded", () => {
  renderCartCount();

  const toggle = document.querySelector(".nav-toggle");
  if (toggle) toggle.addEventListener("click", () =>
    document.querySelector(".main-nav").classList.toggle("open"));

  const page = document.body.dataset.page;
  const init = {
    home: initHome,
    shop: initShop,
    product: initProduct,
    cart: initCart,
    checkout: initCheckout,
    confirmation: initConfirmation,
    quote: initQuote
  }[page];
  if (init) init();
});
