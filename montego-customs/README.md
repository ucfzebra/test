# Montego Customs — E-Commerce Site

Storefront for **Montego Customs**, a precision laser engraving studio serving
three audiences: B2B/corporate clients, large groups (weddings, bachelorette
parties, class reunions), and geek/pop-culture collectors.

## Theme

**"Forged Ember"** — modern, stylish, masculine, professional.

- Charcoal black base (`#0d0f12`) with graphite panels
- Signature ember amber (`#e8842c`) — the glow of a laser on wood
- Warm bone-white type (`#e8e4dc`), brushed-steel grays
- Oswald (condensed display caps) + Inter (body)

## Pages

| Page | Purpose |
|---|---|
| `index.html` | Home — hero, category tiles, featured work, process, quote CTA |
| `shop.html` | Full catalog with category filters (`?cat=b2b\|events\|geek`) |
| `product.html?id=…` | Product detail — options, quantity, add to cart |
| `cart.html` | Cart with quantity editing, removal, totals |
| `checkout.html` | Shipping, payment (demo), engraving notes, validation |
| `confirmation.html` | Order confirmation with generated order number |
| `quote.html` | Custom quotes / special requests form |

## Inventory

18 products across three categories, each with original SVG product art in
`images/`:

- **B2B & Corporate (6):** card holder, slate coaster set, executive pen set,
  brushed steel signage, award plaque, branded portfolio
- **Weddings & Events (6):** welcome sign, cutting board, bachelorette flutes,
  groomsmen whiskey set, reunion keytags, save-the-date magnets
- **The Geek Vault (6):** dice vault, layered d20 wall art, retro sci-fi
  delivery-crew plaque, DON'T PANIC desk sign, 8-bit arcade panel,
  spellbook journal

Catalog data lives in `js/products.js`; cart/checkout logic in `js/app.js`
(cart persists in `localStorage`).

## Running

Pure static site — no build step. Open `index.html` directly or serve the
folder:

```sh
python3 -m http.server 8000
# → http://localhost:8000/montego-customs/
```

> Demo storefront: checkout validates input and generates an order number,
> but no payment is processed. Fan-art pieces are original studio designs,
> unaffiliated with any franchise.
