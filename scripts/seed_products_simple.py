"""
Simple product seeding script - Direct Supabase connection
"""

import os
import sys
from pathlib import Path
from supabase import create_client
import uuid

# Supabase credentials
SUPABASE_URL = "https://nltzetpmvsbazhhkuqiq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5sdHpldHBtdnNiYXpoaGt1cWlxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDIwODY4NywiZXhwIjoyMDg1Nzg0Njg3fQ.4I-SurqZq2mw-ffo5aMrL8Z6kd0f-_O0dfU2Og5TUsM"

def generate_slug(name):
    """Generate URL-friendly slug"""
    return name.lower().replace(' ', '-').replace('&', 'and').replace(',', '')

# Products with high-quality images
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
        "images": [
            {"url": "https://images.unsplash.com/photo-1603561591411-07134e71a2a9?w=800", "alt": "Diamond pendant", "position": 0},
        ],
        "tags": ["diamond", "gold", "luxury", "pendant"],
        "is_featured": True,
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

    # SAREES
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
]

def seed_products():
    """Seed products into Supabase"""
    print("Starting product seeding...")
    print(f"Total products to add: {len(PRODUCTS)}")

    # Create Supabase client
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Get categories
    print("\nFetching categories...")
    categories_result = supabase.table("categories").select("id, slug").execute()
    categories = {cat["slug"]: cat["id"] for cat in categories_result.data}
    print(f"Found {len(categories)} categories")

    added_count = 0
    skipped_count = 0

    for product in PRODUCTS:
        try:
            slug = generate_slug(product["name"])

            # Check if exists
            existing = supabase.table("products").select("id").eq("slug", slug).execute()
            if existing.data:
                print(f"Skipping '{product['name']}' (already exists)")
                skipped_count += 1
                continue

            # Get category ID
            category_id = categories.get(product["category_slug"])
            if not category_id:
                print(f"Category '{product['category_slug']}' not found for '{product['name']}'")
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
                "brand": product.get("brand"),
            }

            # Insert product
            result = supabase.table("products").insert(product_data).execute()

            if result.data:
                print(f"Added: {product['name']} (Rs.{product['base_price']})")
                added_count += 1
            else:
                print(f"Failed to add: {product['name']}")

        except Exception as e:
            print(f"Error adding '{product['name']}': {str(e)}")
            continue

    print("\n" + "="*60)
    print(f"Successfully added: {added_count} products")
    print(f"Skipped: {skipped_count} products")
    print(f"Total in database: {added_count + skipped_count} products")
    print("="*60)
    print("\nProduct seeding completed!")

if __name__ == "__main__":
    try:
        seed_products()
    except Exception as e:
        print(f"\nFatal error: {str(e)}")
        import traceback
        traceback.print_exc()
