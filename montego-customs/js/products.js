/* Montego Customs — Product Catalog */

const PRODUCTS = [
  // ───────────────────────── B2B / CORPORATE ─────────────────────────
  {
    id: "mc-001",
    name: "Walnut Business Card Holder",
    category: "b2b",
    categoryLabel: "B2B & Corporate",
    price: 34.00,
    image: "images/card-holder.svg",
    badge: "Bulk Pricing",
    short: "Solid walnut desk card holder, laser-engraved with your company logo.",
    description: "A weighty, oiled-walnut card holder that anchors any executive desk. We deep-engrave your logo or monogram across the face for permanent, ink-free branding. Volume discounts available for client gifting and onboarding kits — ask us about runs of 25+.",
    options: { label: "Wood", values: ["Walnut", "White Oak", "Cherry"] }
  },
  {
    id: "mc-002",
    name: "Slate Logo Coaster Set (6)",
    category: "b2b",
    categoryLabel: "B2B & Corporate",
    price: 42.00,
    image: "images/slate-coasters.svg",
    badge: "Best Seller",
    short: "Six natural slate coasters etched with your brand mark. Cork-backed.",
    description: "Natural-edge slate coasters with a crisp, frost-white laser etch of your logo. Cork backing protects every surface. The conference-room upgrade your brand deserves — and a client gift that never gets thrown away. Custom packaging sleeves available.",
    options: { label: "Etch Style", values: ["Logo Only", "Logo + Tagline", "Monogram"] }
  },
  {
    id: "mc-003",
    name: "Executive Pen & Case Set",
    category: "b2b",
    categoryLabel: "B2B & Corporate",
    price: 58.00,
    image: "images/pen-set.svg",
    badge: null,
    short: "Brass-trimmed rosewood pen in a fitted engraved presentation case.",
    description: "A twist-action rosewood ballpoint with brass furniture, seated in a flocked presentation case. We engrave a name and title on the barrel and your company mark on the lid. The standard for promotions, retirements, and closing gifts.",
    options: { label: "Finish", values: ["Rosewood / Brass", "Ebony / Chrome"] }
  },
  {
    id: "mc-004",
    name: "Brushed Steel Office Sign",
    category: "b2b",
    categoryLabel: "B2B & Corporate",
    price: 189.00,
    badge: "Made to Order",
    image: "images/steel-sign.svg",
    short: "12\" × 24\" brushed stainless signage, fiber-laser marked. Standoffs included.",
    description: "Architectural-grade brushed stainless steel, fiber-laser annealed with your logo and lettering in deep contrast black. Includes polished standoff mounting hardware. Indoor or covered-outdoor rated. Send us a vector file or let our studio redraw your mark.",
    options: { label: "Size", values: ["12\" × 24\"", "18\" × 36\"", "24\" × 48\" (+$120)"] }
  },
  {
    id: "mc-005",
    name: "Summit Award Plaque",
    category: "b2b",
    categoryLabel: "B2B & Corporate",
    price: 96.00,
    badge: null,
    image: "images/award-plaque.svg",
    short: "Beveled jet-black acrylic award on a walnut base. Fully personalized.",
    description: "A beveled jet-black acrylic peak mounted on a solid walnut base. Recipient name, achievement, and date are engraved in metallic gold infill. Order singles or commission a matched series for your annual awards night.",
    options: { label: "Engraving Fill", values: ["Gold", "Silver", "Natural Frost"] }
  },
  {
    id: "mc-006",
    name: "Leatherette Portfolio — Branded",
    category: "b2b",
    categoryLabel: "B2B & Corporate",
    price: 49.00,
    badge: "Bulk Pricing",
    image: "images/portfolio.svg",
    short: "A4 leatherette portfolio, laser-debossed logo. Ideal for sales teams.",
    description: "Saddle-stitched leatherette portfolio with interior pad, card slots, and pen loop. Laser debossing burns your logo into the cover for a sharp, tactile, sewn-in look that outlasts foil stamping. Outfit the whole sales floor — tiered pricing from 10 units.",
    options: { label: "Color", values: ["Black", "Saddle Brown", "Slate Gray"] }
  },

  // ───────────────────── WEDDINGS / GROUPS / EVENTS ─────────────────────
  {
    id: "mc-007",
    name: "Wedding Welcome Sign",
    category: "events",
    categoryLabel: "Weddings & Events",
    price: 145.00,
    badge: "Made to Order",
    image: "images/wedding-sign.svg",
    short: "24\" × 36\" engraved wood welcome sign with names and wedding date.",
    description: "A statement piece for the ceremony entrance: select-grade birch engraved with your names, date, and flourish-work in our signature script. Choose natural, white-washed, or ebonized finish. Easel-ready, and yours to keep long after the last dance.",
    options: { label: "Finish", values: ["Natural", "White-wash", "Ebonized"] }
  },
  {
    id: "mc-008",
    name: "Mr. & Mrs. Cutting Board",
    category: "events",
    categoryLabel: "Weddings & Events",
    price: 64.00,
    badge: "Best Seller",
    image: "images/cutting-board.svg",
    short: "End-grain maple board engraved with the couple's names and date.",
    description: "An end-grain hard-maple board, food-safe oiled, engraved with the couple's surname, established date, and your choice of motif. The wedding gift that gets used every day and shown off every dinner party.",
    options: { label: "Motif", values: ["Classic Script", "Modern Block", "Wreath & Initials"] }
  },
  {
    id: "mc-009",
    name: "Bachelorette Flute Set (8)",
    category: "events",
    categoryLabel: "Weddings & Events",
    price: 78.00,
    badge: null,
    image: "images/flute-set.svg",
    short: "Eight champagne flutes, each etched with a name and party title.",
    description: "Eight toasting flutes, individually etched — \"Bride,\" \"Maid of Honor,\" and every name in the crew. Frost-etched lettering that survives the dishwasher and the weekend. Add more flutes for larger parties; gift boxing included.",
    options: { label: "Lettering", values: ["Script", "Tall Serif", "Retro Block"] }
  },
  {
    id: "mc-010",
    name: "Groomsmen Whiskey Glass Set (4)",
    category: "events",
    categoryLabel: "Weddings & Events",
    price: 88.00,
    badge: "Best Seller",
    image: "images/whiskey-set.svg",
    short: "Four heavyweight rocks glasses, deep-etched monograms. Gift-boxed.",
    description: "Heavy-bottom 10 oz rocks glasses, deep-etched with each groomsman's monogram and an optional line — name, date, or inside joke. Ships in a kraft gift box with wood wool. The ask-them-to-stand-up-with-you standard.",
    options: { label: "Etch", values: ["Monogram", "Monogram + Name", "Full Custom"] }
  },
  {
    id: "mc-011",
    name: "Reunion Keepsake Keytags (25)",
    category: "events",
    categoryLabel: "Weddings & Events",
    price: 115.00,
    badge: "Bulk Pricing",
    image: "images/keytags.svg",
    short: "25 engraved hardwood keytags — school, class year, and mascot.",
    description: "Twenty-five hardwood keytags engraved with your school crest or mascot, class year, and an optional name per tag. The class-reunion favor people actually keep. Need 50, 100, 250? Tiered pricing kicks in automatically at checkout.",
    options: { label: "Shape", values: ["Rounded Rectangle", "Circle", "Shield"] }
  },
  {
    id: "mc-012",
    name: "Save-the-Date Wood Magnets (50)",
    category: "events",
    categoryLabel: "Weddings & Events",
    price: 130.00,
    badge: null,
    image: "images/save-the-date.svg",
    short: "Fifty engraved birch save-the-date magnets with envelopes.",
    description: "Fifty 1/8\" birch magnets engraved with your names, date, and city — a save-the-date that goes on the fridge, not in the trash. Kraft envelopes included; addressing service available. Allow 7–10 days production.",
    options: { label: "Shape", values: ["Arch", "Hex", "Classic Rectangle"] }
  },

  // ───────────────────────── GEEK / POP CULTURE ─────────────────────────
  {
    id: "mc-013",
    name: "Dragon's Hoard Dice Vault",
    category: "geek",
    categoryLabel: "The Geek Vault",
    price: 72.00,
    badge: "Best Seller",
    image: "images/dice-vault.svg",
    short: "Magnetic hardwood dice vault with a deep-engraved d20 dragon lid.",
    description: "A magnetic-latch hardwood vault that holds two full polyhedral sets, lined in charcoal felt. The lid carries our deep-relief dragon coiled around a d20 — natural-20 face up, obviously. Add a name or character title on the base at no charge. Roll initiative.",
    options: { label: "Wood", values: ["Walnut", "Padauk", "Wenge"] }
  },
  {
    id: "mc-014",
    name: "Critical Hit Wall Art — Layered d20",
    category: "geek",
    categoryLabel: "The Geek Vault",
    price: 98.00,
    badge: null,
    image: "images/d20-wall-art.svg",
    short: "Three-layer laser-cut d20 wall piece, 18\" across, ember backlit edge.",
    description: "Three stacked, laser-cut layers — geometric d20 core, rune ring, and shadowbox frame — with an ember-tone inlay that glows under warm light. 18\" across, keyhole-mounted. The table centerpiece for any game room, no attunement required.",
    options: { label: "Inlay Tone", values: ["Ember", "Arcane Blue", "Poison Green"] }
  },
  {
    id: "mc-015",
    name: "Interplanetary Delivery Crew Plaque",
    category: "geek",
    categoryLabel: "The Geek Vault",
    price: 54.00,
    badge: null,
    image: "images/delivery-plaque.svg",
    short: "Retro-futurist delivery-crew wall plaque. \"Good news, everyone!\"",
    description: "A retro-futurist engraved plaque for fans of a certain 31st-century delivery crew — rocket ship, planet ring, and the immortal opener: \"Good news, everyone!\" Engraved birch with ebonized frame. Original fan art from our studio; not affiliated with any network.",
    options: { label: "Size", values: ["9\" × 12\"", "12\" × 16\""] }
  },
  {
    id: "mc-016",
    name: "DON'T PANIC Desk Sign",
    category: "geek",
    categoryLabel: "The Geek Vault",
    price: 46.00,
    badge: "Best Seller",
    image: "images/dont-panic.svg",
    short: "Two-sided hitchhiker's desk sign: DON'T PANIC / mostly harmless.",
    description: "The two words every desk needs, engraved large and friendly on ebonized hardwood — with \"mostly harmless\" on the reverse and a 42 worked into the base, because of course. A towel is not included, but you already knew where yours is.",
    options: { label: "Base", values: ["Walnut", "Black Acrylic"] }
  },
  {
    id: "mc-017",
    name: "8-Bit Arcade Wall Panel",
    category: "geek",
    categoryLabel: "The Geek Vault",
    price: 62.00,
    badge: null,
    image: "images/arcade-panel.svg",
    short: "Pixel-perfect engraved arcade tribute panel — joystick, invaders, HI-SCORE.",
    description: "A pixel-grid engraved tribute to the golden age of the arcade: invader formations, a joystick-and-button cluster, and your initials in the HI-SCORE slot (three characters, naturally). Engraved on ebonized birch with ember pixel inlays.",
    options: { label: "HI-SCORE Initials", values: ["AAA", "Custom (note at checkout)"] }
  },
  {
    id: "mc-018",
    name: "Arcane Spellbook Journal",
    category: "geek",
    categoryLabel: "The Geek Vault",
    price: 38.00,
    badge: null,
    image: "images/spellbook.svg",
    short: "Leatherette grimoire journal, sigil-engraved cover, 240 dotted pages.",
    description: "A leatherette-bound journal engraved with a full arcane sigil circle and your name in runic banding. 240 dot-grid pages for campaign notes, spell lists, or the novel you keep threatening to write. Elastic closure and ribbon marker.",
    options: { label: "Cover", values: ["Umber Brown", "Onyx Black", "Dragonhide Green"] }
  }
];

const CATEGORIES = {
  b2b:    { label: "B2B & Corporate",  blurb: "Branding that doesn't peel, fade, or wash off." },
  events: { label: "Weddings & Events", blurb: "Weddings, bachelorette weekends, reunions — engraved for the whole crew." },
  geek:   { label: "The Geek Vault",   blurb: "D&D, retro sci-fi, arcade-era art. Fan-made, studio-built." }
};

function getProduct(id) {
  return PRODUCTS.find(p => p.id === id) || null;
}

function formatPrice(n) {
  return "$" + n.toFixed(2);
}
