"""
Clean existing products and seed with proper data
"""

from supabase import create_client
import uuid

# Supabase credentials
SUPABASE_URL = "https://nltzetpmvsbazhhkuqiq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5sdHpldHBtdnNiYXpoaGt1cWlxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDIwODY4NywiZXhwIjoyMDg1Nzg0Njg3fQ.4I-SurqZq2mw-ffo5aMrL8Z6kd0f-_O0dfU2Og5TUsM"

def generate_slug(name):
    """Generate URL-friendly slug"""
    return name.lower().replace(' ', '-').replace('&', 'and').replace(',', '').replace("'", '')

# Complete product catalog with high-quality images
PRODUCTS = [
    # NECKLACES
    {
        "name": "Golden Chain Necklace",
        "category_slug": "necklaces",
        "description": "Elegant 18k gold plated chain necklace perfect for everyday wear. Features delicate craftsmanship and timeless design that complements any outfit.",
        "short_description": "Classic gold chain necklace for daily wear",
        "base_price": 2499.00,
        "sale_price": 1999.00,
        "stock_quantity": 50,
        "material": "Gold Plated",
        "purity": "18K",
        "weight": 15.5,
        "images": [
            {"url": "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=800&q=80", "alt": "Golden chain necklace", "position": 0},
            {"url": "https://images.unsplash.com/photo-1611591437281-460bfbe1220a?w=800&q=80", "alt": "Necklace detail", "position": 1},
        ],
        "tags": ["gold", "chain", "everyday", "elegant"],
        "is_featured": True,
    },
    {
        "name": "Pearl Drop Necklace",
        "category_slug": "necklaces",
        "description": "Beautiful pearl drop necklace with sterling silver chain. Perfect for weddings and special occasions.",
        "short_description": "Elegant pearl necklace with silver chain",
        "base_price": 3999.00,
        "sale_price": 3499.00,
        "stock_quantity": 30,
        "material": "Sterling Silver",
        "images": [
            {"url": "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=800&q=80", "alt": "Pearl necklace", "position": 0},
        ],
        "tags": ["pearl", "silver", "elegant", "wedding"],
        "is_featured": True,
    },
    {
        "name": "Diamond Pendant Necklace",
        "category_slug": "necklaces",
        "description": "Stunning diamond pendant on 14k gold chain. Features a brilliant cut diamond in elegant setting.",
        "short_description": "Diamond pendant with gold chain",
        "base_price": 8999.00,
        "sale_price": 7499.00,
        "stock_quantity": 15,
        "material": "Gold",
        "purity": "14K",
        "weight": 8.2,
        "images": [
            {"url": "https://images.unsplash.com/photo-1603561591411-07134e71a2a9?w=800&q=80", "alt": "Diamond pendant", "position": 0},
        ],
        "tags": ["diamond", "gold", "luxury", "pendant"],
        "is_featured": True,
    },
    {
        "name": "Layered Chain Necklace Set",
        "category_slug": "necklaces",
        "description": "Trendy layered chain necklace set with 3 chains of varying lengths. Perfect for creating a stylish layered look.",
        "short_description": "3-layer chain necklace set",
        "base_price": 1999.00,
        "sale_price": 1499.00,
        "stock_quantity": 60,
        "material": "Alloy",
        "images": [
            {"url": "https://images.unsplash.com/photo-1602751584552-8ba73aad10e1?w=800&q=80", "alt": "Layered necklaces", "position": 0},
        ],
        "tags": ["layered", "trendy", "set", "fashion"],
    },
    {
        "name": "Heart Pendant Necklace",
        "category_slug": "necklaces",
        "description": "Romantic heart-shaped pendant with rose gold finish. Perfect gift for loved ones.",
        "short_description": "Rose gold heart pendant",
        "base_price": 2799.00,
        "sale_price": None,
        "stock_quantity": 40,
        "material": "Rose Gold Plated",
        "images": [
            {"url": "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=800&q=80", "alt": "Heart necklace", "position": 0},
        ],
        "tags": ["heart", "romantic", "rose-gold", "gift"],
    },

    # EARRINGS
    {
        "name": "Diamond Stud Earrings",
        "category_slug": "earrings",
        "description": "Classic diamond stud earrings in 18k white gold. Timeless elegance for any occasion.",
        "short_description": "Classic diamond studs in white gold",
        "base_price": 12999.00,
        "sale_price": 10999.00,
        "stock_quantity": 25,
        "material": "White Gold",
        "purity": "18K",
        "images": [
            {"url": "https://images.unsplash.com/photo-1635767798638-3e25273a8236?w=800&q=80", "alt": "Diamond earrings", "position": 0},
        ],
        "tags": ["diamond", "stud", "white-gold", "luxury"],
        "is_featured": True,
    },
    {
        "name": "Gold Hoop Earrings",
        "category_slug": "earrings",
        "description": "Classic gold hoop earrings in various sizes. Essential accessory for every jewelry collection.",
        "short_description": "Classic gold hoop earrings",
        "base_price": 1899.00,
        "sale_price": 1599.00,
        "stock_quantity": 80,
        "material": "Gold Plated",
        "images": [
            {"url": "https://images.unsplash.com/photo-1617038220319-276d3cfab638?w=800&q=80", "alt": "Hoop earrings", "position": 0},
        ],
        "tags": ["hoop", "gold", "classic", "everyday"],
        "is_featured": True,
    },
    {
        "name": "Pearl Drop Earrings",
        "category_slug": "earrings",
        "description": "Elegant pearl drop earrings with silver hooks. Perfect for formal occasions and weddings.",
        "short_description": "Pearl drop earrings with silver",
        "base_price": 2999.00,
        "sale_price": 2499.00,
        "stock_quantity": 45,
        "material": "Sterling Silver",
        "images": [
            {"url": "https://images.unsplash.com/photo-1630019333476-f629b277c5e7?w=800&q=80", "alt": "Pearl earrings", "position": 0},
        ],
        "tags": ["pearl", "drop", "elegant", "silver"],
    },
    {
        "name": "Statement Chandelier Earrings",
        "category_slug": "earrings",
        "description": "Bold chandelier earrings with crystals and intricate design. Perfect statement piece for parties.",
        "short_description": "Crystal chandelier earrings",
        "base_price": 3499.00,
        "sale_price": None,
        "stock_quantity": 20,
        "material": "Brass",
        "images": [
            {"url": "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=800&q=80", "alt": "Chandelier earrings", "position": 0},
        ],
        "tags": ["statement", "chandelier", "party", "crystal"],
    },
    {
        "name": "Minimalist Stud Set",
        "category_slug": "earrings",
        "description": "Set of 5 minimalist stud earrings in gold and silver tones. Mix and match for different looks.",
        "short_description": "5-piece minimalist stud set",
        "base_price": 1299.00,
        "sale_price": 999.00,
        "stock_quantity": 100,
        "material": "Mixed Metal",
        "images": [
            {"url": "https://images.unsplash.com/photo-1589128777073-263566ae5e4d?w=800&q=80", "alt": "Stud set", "position": 0},
        ],
        "tags": ["minimalist", "set", "everyday", "versatile"],
    },

    # RINGS
    {
        "name": "Solitaire Diamond Ring",
        "category_slug": "rings",
        "description": "Classic solitaire diamond engagement ring in platinum. Timeless symbol of eternal love.",
        "short_description": "Platinum diamond solitaire ring",
        "base_price": 45999.00,
        "sale_price": 39999.00,
        "stock_quantity": 10,
        "material": "Platinum",
        "purity": "950 Platinum",
        "weight": 5.2,
        "images": [
            {"url": "https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=800&q=80", "alt": "Diamond ring", "position": 0},
        ],
        "tags": ["diamond", "engagement", "solitaire", "platinum"],
        "is_featured": True,
    },
    {
        "name": "Gold Band Ring",
        "category_slug": "rings",
        "description": "Simple 22k gold band ring for everyday wear. Classic design that never goes out of style.",
        "short_description": "22k gold band ring",
        "base_price": 8999.00,
        "sale_price": None,
        "stock_quantity": 35,
        "material": "Gold",
        "purity": "22K",
        "weight": 3.5,
        "images": [
            {"url": "https://images.unsplash.com/photo-1611591437281-460bfbe1220a?w=800&q=80", "alt": "Gold band", "position": 0},
        ],
        "tags": ["gold", "band", "simple", "everyday"],
    },
    {
        "name": "Stackable Ring Set",
        "category_slug": "rings",
        "description": "Set of 3 stackable rings in rose gold. Wear together or separately for versatile styling.",
        "short_description": "3-piece stackable ring set",
        "base_price": 2499.00,
        "sale_price": 1999.00,
        "stock_quantity": 55,
        "material": "Rose Gold Plated",
        "images": [
            {"url": "https://images.unsplash.com/photo-1603561596112-0a132b757442?w=800&q=80", "alt": "Stackable rings", "position": 0},
        ],
        "tags": ["stackable", "set", "rose-gold", "trendy"],
    },
    {
        "name": "Emerald Cocktail Ring",
        "category_slug": "rings",
        "description": "Bold emerald cocktail ring in gold setting. Perfect statement piece for special occasions.",
        "short_description": "Gold emerald cocktail ring",
        "base_price": 15999.00,
        "sale_price": 13499.00,
        "stock_quantity": 12,
        "material": "Gold",
        "purity": "18K",
        "images": [
            {"url": "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=800&q=80", "alt": "Emerald ring", "position": 0},
        ],
        "tags": ["emerald", "cocktail", "statement", "gold"],
    },
    {
        "name": "Infinity Band Ring",
        "category_slug": "rings",
        "description": "Delicate infinity symbol band ring in sterling silver. Symbol of eternal love and friendship.",
        "short_description": "Silver infinity band ring",
        "base_price": 1599.00,
        "sale_price": 1299.00,
        "stock_quantity": 70,
        "material": "Sterling Silver",
        "images": [
            {"url": "https://images.unsplash.com/photo-1611591437281-460bfbe1220a?w=800&q=80", "alt": "Infinity ring", "position": 0},
        ],
        "tags": ["infinity", "silver", "delicate", "symbolic"],
    },

    # BANGLES
    {
        "name": "Gold Bangle Set of 4",
        "category_slug": "bangles",
        "description": "Traditional 22k gold bangle set of 4 pieces. Classic design perfect for weddings and festivals.",
        "short_description": "22k gold bangle set (4pcs)",
        "base_price": 35999.00,
        "sale_price": 32999.00,
        "stock_quantity": 15,
        "material": "Gold",
        "purity": "22K",
        "weight": 45.0,
        "images": [
            {"url": "https://images.unsplash.com/photo-1611591437281-460bfbe1220a?w=800&q=80", "alt": "Gold bangles", "position": 0},
        ],
        "tags": ["gold", "traditional", "set", "wedding"],
        "is_featured": True,
    },
    {
        "name": "Kundan Bangle Pair",
        "category_slug": "bangles",
        "description": "Beautiful kundan work bangles with meenakari. Traditional Indian craftsmanship at its finest.",
        "short_description": "Kundan meenakari bangles",
        "base_price": 4999.00,
        "sale_price": 4299.00,
        "stock_quantity": 25,
        "material": "Gold Plated Brass",
        "images": [
            {"url": "https://images.unsplash.com/photo-1611591437281-460bfbe1220a?w=800&q=80", "alt": "Kundan bangles", "position": 0},
        ],
        "tags": ["kundan", "traditional", "ethnic", "festive"],
    },
    {
        "name": "Silver Oxidized Bangles",
        "category_slug": "bangles",
        "description": "Set of 6 oxidized silver bangles with traditional patterns. Bohemian style accessory.",
        "short_description": "Oxidized silver bangle set (6pcs)",
        "base_price": 1999.00,
        "sale_price": 1699.00,
        "stock_quantity": 40,
        "material": "Oxidized Silver",
        "images": [
            {"url": "https://images.unsplash.com/photo-1611591437281-460bfbe1220a?w=800&q=80", "alt": "Silver bangles", "position": 0},
        ],
        "tags": ["silver", "oxidized", "ethnic", "boho"],
    },

    # BRACELETS
    {
        "name": "Diamond Tennis Bracelet",
        "category_slug": "bracelets",
        "description": "Classic tennis bracelet with diamonds in 18k white gold. Elegant and timeless accessory.",
        "short_description": "Diamond tennis bracelet",
        "base_price": 25999.00,
        "sale_price": 22999.00,
        "stock_quantity": 8,
        "material": "White Gold",
        "purity": "18K",
        "images": [
            {"url": "https://images.unsplash.com/photo-1611591437281-460bfbe1220a?w=800&q=80", "alt": "Tennis bracelet", "position": 0},
        ],
        "tags": ["diamond", "tennis", "luxury", "elegant"],
        "is_featured": True,
    },
    {
        "name": "Charm Bracelet",
        "category_slug": "bracelets",
        "description": "Sterling silver charm bracelet with 5 charms. Personalize with additional charms.",
        "short_description": "Silver charm bracelet with 5 charms",
        "base_price": 2799.00,
        "sale_price": 2299.00,
        "stock_quantity": 35,
        "material": "Sterling Silver",
        "images": [
            {"url": "https://images.unsplash.com/photo-1611591437281-460bfbe1220a?w=800&q=80", "alt": "Charm bracelet", "position": 0},
        ],
        "tags": ["charm", "silver", "fun", "personalized"],
    },
    {
        "name": "Leather Wrap Bracelet",
        "category_slug": "bracelets",
        "description": "Trendy leather wrap bracelet with beads. Bohemian style unisex accessory.",
        "short_description": "Leather wrap bracelet with beads",
        "base_price": 999.00,
        "sale_price": 799.00,
        "stock_quantity": 90,
        "material": "Leather",
        "images": [
            {"url": "https://images.unsplash.com/photo-1611591437281-460bfbe1220a?w=800&q=80", "alt": "Leather bracelet", "position": 0},
        ],
        "tags": ["leather", "casual", "boho", "unisex"],
    },

    # PENDANTS
    {
        "name": "Evil Eye Pendant",
        "category_slug": "pendants",
        "description": "Protective evil eye pendant with blue stone in gold setting. Traditional talisman for protection.",
        "short_description": "Gold evil eye pendant",
        "base_price": 1499.00,
        "sale_price": 1199.00,
        "stock_quantity": 60,
        "material": "Gold Plated",
        "images": [
            {"url": "https://images.unsplash.com/photo-1611591437281-460bfbe1220a?w=800&q=80", "alt": "Evil eye pendant", "position": 0},
        ],
        "tags": ["evil-eye", "protection", "trendy", "symbolic"],
    },
    {
        "name": "Zodiac Sign Pendant",
        "category_slug": "pendants",
        "description": "Personalized zodiac sign pendant in gold plating. Choose your zodiac sign.",
        "short_description": "Personalized zodiac pendant",
        "base_price": 1999.00,
        "sale_price": None,
        "stock_quantity": 100,
        "material": "Gold Plated",
        "images": [
            {"url": "https://images.unsplash.com/photo-1611591437281-460bfbe1220a?w=800&q=80", "alt": "Zodiac pendant", "position": 0},
        ],
        "tags": ["zodiac", "personalized", "astrology", "gift"],
    },

    # SAREES
    {
        "name": "Banarasi Silk Saree",
        "category_slug": "sarees",
        "description": "Pure Banarasi silk saree with intricate zari work. Traditional handwoven masterpiece perfect for weddings.",
        "short_description": "Pure Banarasi silk with zari work",
        "base_price": 8999.00,
        "sale_price": 7499.00,
        "stock_quantity": 20,
        "brand": "Traditional Weaves",
        "images": [
            {"url": "https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=800&q=80", "alt": "Banarasi saree", "position": 0},
        ],
        "tags": ["saree", "silk", "traditional", "wedding"],
        "is_featured": True,
    },
    {
        "name": "Chanderi Cotton Saree",
        "category_slug": "sarees",
        "description": "Lightweight chanderi cotton saree perfect for summer. Elegant and comfortable daily wear.",
        "short_description": "Lightweight chanderi cotton saree",
        "base_price": 3499.00,
        "sale_price": 2999.00,
        "stock_quantity": 35,
        "brand": "Handloom Collection",
        "images": [
            {"url": "https://images.unsplash.com/photo-1583391733981-9b149c7f1bbd?w=800&q=80", "alt": "Chanderi saree", "position": 0},
        ],
        "tags": ["saree", "cotton", "handloom", "summer"],
    },
    {
        "name": "Designer Georgette Saree",
        "category_slug": "sarees",
        "description": "Trendy georgette saree with sequin work. Modern design perfect for parties and celebrations.",
        "short_description": "Sequin work georgette saree",
        "base_price": 4999.00,
        "sale_price": 4299.00,
        "stock_quantity": 25,
        "brand": "Modern Drapes",
        "images": [
            {"url": "https://images.unsplash.com/photo-1596928527160-8e15a5b5c40b?w=800&q=80", "alt": "Georgette saree", "position": 0},
        ],
        "tags": ["saree", "georgette", "party", "designer"],
    },

    # ETHNIC WEAR
    {
        "name": "Anarkali Suit Set",
        "category_slug": "ethnic-wear",
        "description": "Beautiful anarkali suit with dupatta. Elegant ethnic wear perfect for festivals and celebrations.",
        "short_description": "Anarkali suit with dupatta",
        "base_price": 5999.00,
        "sale_price": 4999.00,
        "stock_quantity": 30,
        "brand": "Ethnic Couture",
        "images": [
            {"url": "https://images.unsplash.com/photo-1583391733956-6c78339b27b5?w=800&q=80", "alt": "Anarkali suit", "position": 0},
        ],
        "tags": ["anarkali", "suit", "ethnic", "festive"],
        "is_featured": True,
    },
    {
        "name": "Palazzo Suit Set",
        "category_slug": "ethnic-wear",
        "description": "Comfortable palazzo suit with embroidery. Modern ethnic wear for daily use and casual occasions.",
        "short_description": "Palazzo suit with embroidery",
        "base_price": 3499.00,
        "sale_price": 2999.00,
        "stock_quantity": 45,
        "brand": "Comfort Ethnic",
        "images": [
            {"url": "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=800&q=80", "alt": "Palazzo suit", "position": 0},
        ],
        "tags": ["palazzo", "comfortable", "ethnic", "casual"],
    },
    {
        "name": "Kurta Set with Dupatta",
        "category_slug": "ethnic-wear",
        "description": "Cotton kurta set perfect for everyday wear. Comfortable and stylish ethnic fashion.",
        "short_description": "Cotton kurta set with dupatta",
        "base_price": 1999.00,
        "sale_price": 1699.00,
        "stock_quantity": 60,
        "brand": "Daily Wear Co",
        "images": [
            {"url": "https://images.unsplash.com/photo-1589987607837-aa1a94e0738e?w=800&q=80", "alt": "Kurta set", "position": 0},
        ],
        "tags": ["kurta", "cotton", "everyday", "comfortable"],
    },

    # WESTERN WEAR
    {
        "name": "Classic Denim Jacket",
        "category_slug": "western-wear",
        "description": "Classic denim jacket perfect for layering. Timeless fashion staple for all seasons.",
        "short_description": "Classic denim jacket",
        "base_price": 2499.00,
        "sale_price": 1999.00,
        "stock_quantity": 50,
        "brand": "Urban Style",
        "images": [
            {"url": "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=800&q=80", "alt": "Denim jacket", "position": 0},
        ],
        "tags": ["denim", "jacket", "casual", "layering"],
        "is_featured": True,
    },
    {
        "name": "Floral Maxi Dress",
        "category_slug": "western-wear",
        "description": "Beautiful floral print maxi dress. Perfect summer outfit for parties and casual outings.",
        "short_description": "Floral print maxi dress",
        "base_price": 2999.00,
        "sale_price": 2499.00,
        "stock_quantity": 40,
        "brand": "Summer Collection",
        "images": [
            {"url": "https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=800&q=80", "alt": "Maxi dress", "position": 0},
        ],
        "tags": ["dress", "floral", "maxi", "summer"],
    },
    {
        "name": "High-Waisted Jeans",
        "category_slug": "western-wear",
        "description": "Comfortable high-waisted skinny jeans. Essential wardrobe staple in premium denim.",
        "short_description": "High-waisted skinny jeans",
        "base_price": 1999.00,
        "sale_price": 1699.00,
        "stock_quantity": 80,
        "brand": "Fit Perfect",
        "images": [
            {"url": "https://images.unsplash.com/photo-1542272604-787c3835535d?w=800&q=80", "alt": "Jeans", "position": 0},
        ],
        "tags": ["jeans", "high-waisted", "denim", "basics"],
    },

    # ACCESSORIES
    {
        "name": "Designer Handbag",
        "category_slug": "accessories",
        "description": "Elegant designer handbag in vegan leather. Spacious and stylish for daily use.",
        "short_description": "Vegan leather designer handbag",
        "base_price": 3999.00,
        "sale_price": 3499.00,
        "stock_quantity": 25,
        "brand": "Luxe Bags",
        "images": [
            {"url": "https://images.unsplash.com/photo-1564422170194-896b89110ef8?w=800&q=80", "alt": "Handbag", "position": 0},
        ],
        "tags": ["handbag", "vegan-leather", "designer", "luxury"],
        "is_featured": True,
    },
    {
        "name": "Silk Scarf",
        "category_slug": "accessories",
        "description": "Premium silk scarf with floral print. Versatile accessory for multiple styling options.",
        "short_description": "Premium silk floral scarf",
        "base_price": 1499.00,
        "sale_price": 1199.00,
        "stock_quantity": 55,
        "brand": "Silk Stories",
        "images": [
            {"url": "https://images.unsplash.com/photo-1601924994987-69e26d50dc26?w=800&q=80", "alt": "Silk scarf", "position": 0},
        ],
        "tags": ["scarf", "silk", "accessory", "elegant"],
    },
    {
        "name": "UV Protection Sunglasses",
        "category_slug": "accessories",
        "description": "Stylish sunglasses with UV400 protection. Fashion meets function for eye protection.",
        "short_description": "UV400 sunglasses",
        "base_price": 1299.00,
        "sale_price": 999.00,
        "stock_quantity": 100,
        "brand": "Vision Style",
        "images": [
            {"url": "https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=800&q=80", "alt": "Sunglasses", "position": 0},
        ],
        "tags": ["sunglasses", "uv-protection", "fashion", "summer"],
    },
]

def clean_and_seed():
    """Delete existing products and seed with clean data"""
    print("="*60)
    print("CLEANING AND SEEDING PRODUCTS")
    print("="*60)

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Step 1: Delete all existing products
    print("\n[1/3] Deleting existing products...")
    try:
        # Get count first
        existing = supabase.table("products").select("id", count="exact").execute()
        count = existing.count or 0

        if count > 0:
            # Delete all
            supabase.table("products").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
            print(f"Deleted {count} existing products")
        else:
            print("No existing products to delete")
    except Exception as e:
        print(f"Error deleting products: {str(e)}")

    # Step 2: Get categories
    print("\n[2/3] Fetching categories...")
    categories_result = supabase.table("categories").select("id, slug").execute()
    categories = {cat["slug"]: cat["id"] for cat in categories_result.data}
    print(f"Found {len(categories)} categories")

    # Step 3: Seed products
    print(f"\n[3/3] Seeding {len(PRODUCTS)} products...")
    print("-"*60)

    added_count = 0
    errors = []

    for idx, product in enumerate(PRODUCTS, 1):
        try:
            slug = generate_slug(product["name"])
            category_id = categories.get(product["category_slug"])

            if not category_id:
                errors.append(f"{product['name']}: Category not found")
                continue

            sku = f"ALM-{str(uuid.uuid4())[:8].upper()}"

            product_data = {
                "name": product["name"],
                "slug": slug,
                "description": product["description"],
                "short_description": product.get("short_description"),
                "base_price": float(product["base_price"]),
                "sale_price": float(product["sale_price"]) if product.get("sale_price") else None,
                "sku": sku,
                "stock_quantity": product["stock_quantity"],
                "category_id": category_id,
                "status": "active",
                "is_featured": product.get("is_featured", False),
                "images": product["images"],
                "tags": product.get("tags", []),
                "material": product.get("material"),
                "purity": product.get("purity"),
                "weight": product.get("weight"),
                "brand": product.get("brand"),
                "rating": 0.0,
                "review_count": 0,
            }

            result = supabase.table("products").insert(product_data).execute()

            if result.data:
                price_str = f"Rs.{product['base_price']:.0f}"
                if product.get("sale_price"):
                    price_str = f"Rs.{product['sale_price']:.0f} (was Rs.{product['base_price']:.0f})"
                print(f"[{idx}/{len(PRODUCTS)}] Added: {product['name']} - {price_str}")
                added_count += 1

        except Exception as e:
            errors.append(f"{product['name']}: {str(e)}")

    # Summary
    print("-"*60)
    print(f"\nSUCCESS: Added {added_count}/{len(PRODUCTS)} products")

    if errors:
        print(f"\nERRORS ({len(errors)}):")
        for error in errors:
            print(f"  - {error}")

    print("\n" + "="*60)
    print("SEEDING COMPLETE!")
    print("="*60)

if __name__ == "__main__":
    try:
        clean_and_seed()
    except Exception as e:
        print(f"\nFatal error: {str(e)}")
        import traceback
        traceback.print_exc()
