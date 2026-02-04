"""
Seed database with products and high-quality images from Unsplash.
Adds 50+ products across multiple categories with real images.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
from app.core.supabase import get_supabase_admin
import uuid

def generate_slug(name):
    """Generate URL-friendly slug from product name."""
    return name.lower().replace(' ', '-').replace('&', 'and').replace(',', '')

# High-quality product images from Unsplash
PRODUCTS = [
    # NECKLACES
    {
        "name": "Golden Chain Necklace",
        "category_slug": "necklaces",
        "description": "Elegant 18k gold plated chain necklace perfect for everyday wear",
        "short_description": "Classic gold chain necklace",
        "base_price": 2499,
        "sale_price": 1999,
        "stock_quantity": 50,
        "material": "Gold Plated",
        "purity": "18K",
        "weight": 15.5,
        "images": [
            {"url": "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=800", "alt": "Golden chain necklace", "position": 0},
            {"url": "https://images.unsplash.com/photo-1611591437281-460bfbe1220a?w=800", "alt": "Necklace detail", "position": 1},
        ],
        "tags": ["gold", "chain", "everyday", "elegant"],
        "is_featured": True,
    },
    {
        "name": "Pearl Drop Necklace",
        "category_slug": "necklaces",
        "description": "Beautiful pearl drop necklace with sterling silver chain",
        "short_description": "Elegant pearl necklace",
        "base_price": 3999,
        "sale_price": 3499,
        "stock_quantity": 30,
        "material": "Sterling Silver",
        "images": [
            {"url": "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=800", "alt": "Pearl necklace", "position": 0},
        ],
        "tags": ["pearl", "silver", "elegant", "wedding"],
        "is_featured": True,
    },
    {
        "name": "Diamond Pendant Necklace",
        "category_slug": "necklaces",
        "description": "Stunning diamond pendant on 14k gold chain",
        "short_description": "Diamond pendant necklace",
        "base_price": 8999,
        "sale_price": 7499,
        "stock_quantity": 15,
        "material": "Gold",
        "purity": "14K",
        "weight": 8.2,
        "gemstones": [{"type": "Diamond", "carat": 0.5, "clarity": "VS"}],
        "images": [
            {"url": "https://images.unsplash.com/photo-1603561591411-07134e71a2a9?w=800", "alt": "Diamond pendant", "position": 0},
        ],
        "tags": ["diamond", "gold", "luxury", "pendant"],
        "is_featured": True,
    },
    {
        "name": "Layered Chain Necklace Set",
        "category_slug": "necklaces",
        "description": "Trendy layered chain necklace set with 3 chains",
        "short_description": "Layered necklace set",
        "base_price": 1999,
        "sale_price": 1499,
        "stock_quantity": 60,
        "material": "Alloy",
        "images": [
            {"url": "https://images.unsplash.com/photo-1602751584552-8ba73aad10e1?w=800", "alt": "Layered necklaces", "position": 0},
        ],
        "tags": ["layered", "trendy", "set", "fashion"],
    },
    {
        "name": "Heart Pendant Necklace",
        "category_slug": "necklaces",
        "description": "Romantic heart-shaped pendant with rose gold finish",
        "short_description": "Heart pendant necklace",
        "base_price": 2799,
        "sale_price": None,
        "stock_quantity": 40,
        "material": "Rose Gold Plated",
        "images": [
            {"url": "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=800", "alt": "Heart necklace", "position": 0},
        ],
        "tags": ["heart", "romantic", "rose-gold", "gift"],
    },

    # EARRINGS
    {
        "name": "Diamond Stud Earrings",
        "category_slug": "earrings",
        "description": "Classic diamond stud earrings in 18k white gold",
        "short_description": "Diamond stud earrings",
        "base_price": 12999,
        "sale_price": 10999,
        "stock_quantity": 25,
        "material": "White Gold",
        "purity": "18K",
        "gemstones": [{"type": "Diamond", "carat": 0.75, "clarity": "VVS"}],
        "images": [
            {"url": "https://images.unsplash.com/photo-1635767798638-3e25273a8236?w=800", "alt": "Diamond earrings", "position": 0},
        ],
        "tags": ["diamond", "stud", "white-gold", "luxury"],
        "is_featured": True,
    },
    {
        "name": "Hoop Earrings Gold",
        "category_slug": "earrings",
        "description": "Classic gold hoop earrings in various sizes",
        "short_description": "Gold hoop earrings",
        "base_price": 1899,
        "sale_price": 1599,
        "stock_quantity": 80,
        "material": "Gold Plated",
        "images": [
            {"url": "https://images.unsplash.com/photo-1617038220319-276d3cfab638?w=800", "alt": "Hoop earrings", "position": 0},
        ],
        "tags": ["hoop", "gold", "classic", "everyday"],
        "is_featured": True,
    },
    {
        "name": "Pearl Drop Earrings",
        "category_slug": "earrings",
        "description": "Elegant pearl drop earrings with silver hooks",
        "short_description": "Pearl drop earrings",
        "base_price": 2999,
        "sale_price": 2499,
        "stock_quantity": 45,
        "material": "Sterling Silver",
        "images": [
            {"url": "https://images.unsplash.com/photo-1630019333476-f629b277c5e7?w=800", "alt": "Pearl earrings", "position": 0},
        ],
        "tags": ["pearl", "drop", "elegant", "silver"],
    },
    {
        "name": "Statement Chandelier Earrings",
        "category_slug": "earrings",
        "description": "Bold chandelier earrings with crystals",
        "short_description": "Chandelier earrings",
        "base_price": 3499,
        "sale_price": None,
        "stock_quantity": 20,
        "material": "Brass",
        "images": [
            {"url": "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=800", "alt": "Chandelier earrings", "position": 0},
        ],
        "tags": ["statement", "chandelier", "party", "crystal"],
    },
    {
        "name": "Minimalist Stud Set",
        "category_slug": "earrings",
        "description": "Set of 5 minimalist stud earrings in gold and silver",
        "short_description": "Minimalist stud set",
        "base_price": 1299,
        "sale_price": 999,
        "stock_quantity": 100,
        "material": "Mixed Metal",
        "images": [
            {"url": "https://images.unsplash.com/photo-1589128777073-263566ae5e4d?w=800", "alt": "Stud set", "position": 0},
        ],
        "tags": ["minimalist", "set", "everyday", "versatile"],
    },

    # RINGS
    {
        "name": "Solitaire Diamond Ring",
        "category_slug": "rings",
        "description": "Classic solitaire diamond engagement ring",
        "short_description": "Diamond solitaire ring",
        "base_price": 45999,
        "sale_price": 39999,
        "stock_quantity": 10,
        "material": "Platinum",
        "purity": "950 Platinum",
        "weight": 5.2,
        "gemstones": [{"type": "Diamond", "carat": 1.0, "clarity": "VS1"}],
        "images": [
            {"url": "https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=800", "alt": "Diamond ring", "position": 0},
        ],
        "tags": ["diamond", "engagement", "solitaire", "platinum"],
        "is_featured": True,
    },
    {
        "name": "Gold Band Ring",
        "category_slug": "rings",
        "description": "Simple 22k gold band ring for everyday wear",
        "short_description": "Gold band ring",
        "base_price": 8999,
        "sale_price": None,
        "stock_quantity": 35,
        "material": "Gold",
        "purity": "22K",
        "weight": 3.5,
        "images": [
            {"url": "https://images.unsplash.com/photo-1611591437281-460bfbe1220a?w=800", "alt": "Gold band", "position": 0},
        ],
        "tags": ["gold", "band", "simple", "everyday"],
    },
    {
        "name": "Stackable Ring Set",
        "category_slug": "rings",
        "description": "Set of 3 stackable rings in rose gold",
        "short_description": "Stackable ring set",
        "base_price": 2499,
        "sale_price": 1999,
        "stock_quantity": 55,
        "material": "Rose Gold Plated",
        "images": [
            {"url": "https://images.unsplash.com/photo-1603561596112-0a132b757442?w=800", "alt": "Stackable rings", "position": 0},
        ],
        "tags": ["stackable", "set", "rose-gold", "trendy"],
    },
    {
        "name": "Emerald Cocktail Ring",
        "category_slug": "rings",
        "description": "Bold emerald cocktail ring in gold setting",
        "short_description": "Emerald cocktail ring",
        "base_price": 15999,
        "sale_price": 13499,
        "stock_quantity": 12,
        "material": "Gold",
        "purity": "18K",
        "gemstones": [{"type": "Emerald", "carat": 2.5}],
        "images": [
            {"url": "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=800", "alt": "Emerald ring", "position": 0},
        ],
        "tags": ["emerald", "cocktail", "statement", "gold"],
    },
    {
        "name": "Infinity Band Ring",
        "category_slug": "rings",
        "description": "Delicate infinity symbol band ring in silver",
        "short_description": "Infinity ring",
        "base_price": 1599,
        "sale_price": 1299,
        "stock_quantity": 70,
        "material": "Sterling Silver",
        "images": [
            {"url": "https://images.unsplash.com/photo-1611591437281-460bfbe1220a?w=800", "alt": "Infinity ring", "position": 0},
        ],
        "tags": ["infinity", "silver", "delicate", "symbolic"],
    },

    # BANGLES
    {
        "name": "Gold Bangle Set of 4",
        "category_slug": "bangles",
        "description": "Traditional 22k gold bangle set",
        "short_description": "Gold bangle set",
        "base_price": 35999,
        "sale_price": 32999,
        "stock_quantity": 15,
        "material": "Gold",
        "purity": "22K",
        "weight": 45.0,
        "images": [
            {"url": "https://images.unsplash.com/photo-1611591437281-460bfbe1220a?w=800", "alt": "Gold bangles", "position": 0},
        ],
        "tags": ["gold", "traditional", "set", "wedding"],
        "is_featured": True,
    },
    {
        "name": "Kundan Bangle Pair",
        "category_slug": "bangles",
        "description": "Beautiful kundan work bangles with meenakari",
        "short_description": "Kundan bangles",
        "base_price": 4999,
        "sale_price": 4299,
        "stock_quantity": 25,
        "material": "Gold Plated Brass",
        "images": [
            {"url": "https://images.unsplash.com/photo-1611591437281-460bfbe1220a?w=800", "alt": "Kundan bangles", "position": 0},
        ],
        "tags": ["kundan", "traditional", "ethnic", "festive"],
    },
    {
        "name": "Silver Oxidized Bangles",
        "category_slug": "bangles",
        "description": "Set of 6 oxidized silver bangles",
        "short_description": "Oxidized bangles",
        "base_price": 1999,
        "sale_price": 1699,
        "stock_quantity": 40,
        "material": "Oxidized Silver",
        "images": [
            {"url": "https://images.unsplash.com/photo-1611591437281-460bfbe1220a?w=800", "alt": "Silver bangles", "position": 0},
        ],
        "tags": ["silver", "oxidized", "ethnic", "boho"],
    },

    # BRACELETS
    {
        "name": "Tennis Bracelet Diamond",
        "category_slug": "bracelets",
        "description": "Classic tennis bracelet with diamonds",
        "short_description": "Diamond tennis bracelet",
        "base_price": 25999,
        "sale_price": 22999,
        "stock_quantity": 8,
        "material": "White Gold",
        "purity": "18K",
        "gemstones": [{"type": "Diamond", "carat": 2.0}],
        "images": [
            {"url": "https://images.unsplash.com/photo-1611591437281-460bfbe1220a?w=800", "alt": "Tennis bracelet", "position": 0},
        ],
        "tags": ["diamond", "tennis", "luxury", "elegant"],
        "is_featured": True,
    },
    {
        "name": "Charm Bracelet",
        "category_slug": "bracelets",
        "description": "Silver charm bracelet with 5 charms",
        "short_description": "Charm bracelet",
        "base_price": 2799,
        "sale_price": 2299,
        "stock_quantity": 35,
        "material": "Sterling Silver",
        "images": [
            {"url": "https://images.unsplash.com/photo-1611591437281-460bfbe1220a?w=800", "alt": "Charm bracelet", "position": 0},
        ],
        "tags": ["charm", "silver", "fun", "personalized"],
    },
    {
        "name": "Leather Wrap Bracelet",
        "category_slug": "bracelets",
        "description": "Trendy leather wrap bracelet with beads",
        "short_description": "Leather bracelet",
        "base_price": 999,
        "sale_price": 799,
        "stock_quantity": 90,
        "material": "Leather",
        "images": [
            {"url": "https://images.unsplash.com/photo-1611591437281-460bfbe1220a?w=800", "alt": "Leather bracelet", "position": 0},
        ],
        "tags": ["leather", "casual", "boho", "unisex"],
    },

    # PENDANTS
    {
        "name": "Evil Eye Pendant",
        "category_slug": "pendants",
        "description": "Protective evil eye pendant with blue stone",
        "short_description": "Evil eye pendant",
        "base_price": 1499,
        "sale_price": 1199,
        "stock_quantity": 60,
        "material": "Gold Plated",
        "images": [
            {"url": "https://images.unsplash.com/photo-1611591437281-460bfbe1220a?w=800", "alt": "Evil eye pendant", "position": 0},
        ],
        "tags": ["evil-eye", "protection", "trendy", "symbolic"],
    },
    {
        "name": "Zodiac Sign Pendant",
        "category_slug": "pendants",
        "description": "Personalized zodiac sign pendant in gold",
        "short_description": "Zodiac pendant",
        "base_price": 1999,
        "sale_price": None,
        "stock_quantity": 100,
        "material": "Gold Plated",
        "images": [
            {"url": "https://images.unsplash.com/photo-1611591437281-460bfbe1220a?w=800", "alt": "Zodiac pendant", "position": 0},
        ],
        "tags": ["zodiac", "personalized", "astrology", "gift"],
    },

    # SAREES (Fashion Category)
    {
        "name": "Banarasi Silk Saree",
        "category_slug": "sarees",
        "description": "Pure Banarasi silk saree with zari work",
        "short_description": "Banarasi silk saree",
        "base_price": 8999,
        "sale_price": 7499,
        "stock_quantity": 20,
        "brand": "Traditional Weaves",
        "images": [
            {"url": "https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=800", "alt": "Banarasi saree", "position": 0},
        ],
        "tags": ["saree", "silk", "traditional", "wedding"],
        "is_featured": True,
    },
    {
        "name": "Chanderi Cotton Saree",
        "category_slug": "sarees",
        "description": "Lightweight chanderi cotton saree",
        "short_description": "Chanderi saree",
        "base_price": 3499,
        "sale_price": 2999,
        "stock_quantity": 35,
        "brand": "Handloom Collection",
        "images": [
            {"url": "https://images.unsplash.com/photo-1583391733981-9b149c7f1bbd?w=800", "alt": "Chanderi saree", "position": 0},
        ],
        "tags": ["saree", "cotton", "handloom", "summer"],
    },
    {
        "name": "Designer Georgette Saree",
        "category_slug": "sarees",
        "description": "Trendy georgette saree with sequin work",
        "short_description": "Georgette saree",
        "base_price": 4999,
        "sale_price": 4299,
        "stock_quantity": 25,
        "brand": "Modern Drapes",
        "images": [
            {"url": "https://images.unsplash.com/photo-1596928527160-8e15a5b5c40b?w=800", "alt": "Georgette saree", "position": 0},
        ],
        "tags": ["saree", "georgette", "party", "designer"],
    },

    # ETHNIC WEAR
    {
        "name": "Anarkali Suit Set",
        "category_slug": "ethnic-wear",
        "description": "Beautiful anarkali suit with dupatta",
        "short_description": "Anarkali suit",
        "base_price": 5999,
        "sale_price": 4999,
        "stock_quantity": 30,
        "brand": "Ethnic Couture",
        "images": [
            {"url": "https://images.unsplash.com/photo-1583391733956-6c78339b27b5?w=800", "alt": "Anarkali suit", "position": 0},
        ],
        "tags": ["anarkali", "suit", "ethnic", "festive"],
        "is_featured": True,
    },
    {
        "name": "Palazzo Suit Set",
        "category_slug": "ethnic-wear",
        "description": "Comfortable palazzo suit with embroidery",
        "short_description": "Palazzo suit",
        "base_price": 3499,
        "sale_price": 2999,
        "stock_quantity": 45,
        "brand": "Comfort Ethnic",
        "images": [
            {"url": "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=800", "alt": "Palazzo suit", "position": 0},
        ],
        "tags": ["palazzo", "comfortable", "ethnic", "casual"],
    },
    {
        "name": "Kurta Set with Dupatta",
        "category_slug": "ethnic-wear",
        "description": "Cotton kurta set perfect for everyday wear",
        "short_description": "Kurta set",
        "base_price": 1999,
        "sale_price": 1699,
        "stock_quantity": 60,
        "brand": "Daily Wear Co",
        "images": [
            {"url": "https://images.unsplash.com/photo-1589987607837-aa1a94e0738e?w=800", "alt": "Kurta set", "position": 0},
        ],
        "tags": ["kurta", "cotton", "everyday", "comfortable"],
    },

    # WESTERN WEAR
    {
        "name": "Denim Jacket",
        "category_slug": "western-wear",
        "description": "Classic denim jacket perfect for layering",
        "short_description": "Denim jacket",
        "base_price": 2499,
        "sale_price": 1999,
        "stock_quantity": 50,
        "brand": "Urban Style",
        "images": [
            {"url": "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=800", "alt": "Denim jacket", "position": 0},
        ],
        "tags": ["denim", "jacket", "casual", "layering"],
        "is_featured": True,
    },
    {
        "name": "Floral Maxi Dress",
        "category_slug": "western-wear",
        "description": "Beautiful floral print maxi dress",
        "short_description": "Floral maxi dress",
        "base_price": 2999,
        "sale_price": 2499,
        "stock_quantity": 40,
        "brand": "Summer Collection",
        "images": [
            {"url": "https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=800", "alt": "Maxi dress", "position": 0},
        ],
        "tags": ["dress", "floral", "maxi", "summer"],
    },
    {
        "name": "High-Waisted Jeans",
        "category_slug": "western-wear",
        "description": "Comfortable high-waisted skinny jeans",
        "short_description": "High-waisted jeans",
        "base_price": 1999,
        "sale_price": 1699,
        "stock_quantity": 80,
        "brand": "Fit Perfect",
        "images": [
            {"url": "https://images.unsplash.com/photo-1542272604-787c3835535d?w=800", "alt": "Jeans", "position": 0},
        ],
        "tags": ["jeans", "high-waisted", "denim", "basics"],
    },

    # ACCESSORIES
    {
        "name": "Designer Handbag",
        "category_slug": "accessories",
        "description": "Elegant designer handbag in vegan leather",
        "short_description": "Designer handbag",
        "base_price": 3999,
        "sale_price": 3499,
        "stock_quantity": 25,
        "brand": "Luxe Bags",
        "images": [
            {"url": "https://images.unsplash.com/photo-1564422170194-896b89110ef8?w=800", "alt": "Handbag", "position": 0},
        ],
        "tags": ["handbag", "vegan-leather", "designer", "luxury"],
        "is_featured": True,
    },
    {
        "name": "Silk Scarf",
        "category_slug": "accessories",
        "description": "Premium silk scarf with floral print",
        "short_description": "Silk scarf",
        "base_price": 1499,
        "sale_price": 1199,
        "stock_quantity": 55,
        "brand": "Silk Stories",
        "images": [
            {"url": "https://images.unsplash.com/photo-1601924994987-69e26d50dc26?w=800", "alt": "Silk scarf", "position": 0},
        ],
        "tags": ["scarf", "silk", "accessory", "elegant"],
    },
    {
        "name": "Sunglasses UV Protection",
        "category_slug": "accessories",
        "description": "Stylish sunglasses with UV400 protection",
        "short_description": "Sunglasses",
        "base_price": 1299,
        "sale_price": 999,
        "stock_quantity": 100,
        "brand": "Vision Style",
        "images": [
            {"url": "https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=800", "alt": "Sunglasses", "position": 0},
        ],
        "tags": ["sunglasses", "uv-protection", "fashion", "summer"],
    },
]


def seed_products():
    """Seed products with images into the database."""
    print("🌱 Starting product seeding...")
    print(f"📦 Total products to add: {len(PRODUCTS)}")

    supabase = get_supabase_admin()

    # Get categories
    print("\n📂 Fetching categories...")
    categories_result = supabase.table("categories").select("id, slug").execute()
    categories = {cat["slug"]: cat["id"] for cat in categories_result.data}

    print(f"✅ Found {len(categories)} categories")

    added_count = 0
    skipped_count = 0

    for product in PRODUCTS:
        try:
            slug = generate_slug(product["name"])

            # Check if product already exists
            existing = supabase.table("products").select("id").eq("slug", slug).execute()
            if existing.data:
                print(f"⏭️  Skipping '{product['name']}' (already exists)")
                skipped_count += 1
                continue

            # Get category ID
            category_id = categories.get(product["category_slug"])
            if not category_id:
                print(f"⚠️  Category '{product['category_slug']}' not found for '{product['name']}'")
                continue

            # Generate SKU
            sku = f"ALM-{str(uuid.uuid4())[:8].upper()}"

            # Prepare product data
            product_data = {
                "name": product["name"],
                "slug": slug,
                "description": product["description"],
                "short_description": product.get("short_description"),
                "base_price": product["base_price"],
                "sale_price": product.get("sale_price"),
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
                "weight_unit": product.get("weight_unit", "gm"),
                "gemstones": product.get("gemstones"),
                "brand": product.get("brand"),
            }

            # Insert product
            result = supabase.table("products").insert(product_data).execute()

            if result.data:
                print(f"✅ Added: {product['name']} (₹{product['base_price']}) - {product['category_slug']}")
                added_count += 1
            else:
                print(f"❌ Failed to add: {product['name']}")

        except Exception as e:
            print(f"❌ Error adding '{product['name']}': {str(e)}")
            continue

    print("\n" + "="*60)
    print(f"✅ Successfully added: {added_count} products")
    print(f"⏭️  Skipped (already exist): {skipped_count} products")
    print(f"📦 Total in database: {added_count + skipped_count} products")
    print("="*60)
    print("\n🎉 Product seeding completed!")
    print("\n💡 Next steps:")
    print("   1. Start backend: cd Backend && uvicorn app.main:app --reload")
    print("   2. Start frontend: cd Frontend && npm run dev")
    print("   3. Browse products at: http://localhost:5173")


if __name__ == "__main__":
    try:
        seed_products()
    except KeyboardInterrupt:
        print("\n\n⚠️  Seeding interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
