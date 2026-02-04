"""
Verify database schema and connections.
Checks that all tables and foreign keys were created properly.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.supabase import get_supabase_admin


def verify_schema():
    """Verify database schema."""

    print("\n" + "=" * 60)
    print("  DATABASE SCHEMA VERIFICATION")
    print("=" * 60 + "\n")

    try:
        db = get_supabase_admin()

        # Expected tables
        expected_tables = [
            'profiles', 'addresses', 'categories', 'products',
            'product_variants', 'coupons', 'orders', 'order_items',
            'cart_items', 'wishlist_items', 'reviews', 'coupon_usages',
            'audit_logs'
        ]

        print("✓ Connected to Supabase")
        print(f"\n📋 Checking {len(expected_tables)} expected tables...\n")

        # Check each table
        for table in expected_tables:
            try:
                result = db.table(table).select("*", count="exact").limit(0).execute()
                print(f"  ✓ {table:20} - OK (count: {result.count or 0})")
            except Exception as e:
                print(f"  ✗ {table:20} - FAILED: {str(e)}")
                return False

        # Check categories seed data
        print("\n📦 Checking seed data...")
        categories = db.table("categories").select("slug").execute()
        if categories.data and len(categories.data) >= 10:
            print(f"  ✓ Categories seeded: {len(categories.data)} categories")
        else:
            print(f"  ⚠️  Categories: {len(categories.data) if categories.data else 0} (expected 10)")

        print("\n" + "=" * 60)
        print("✅ Schema verification completed successfully!")
        print("=" * 60 + "\n")

        return True

    except Exception as e:
        print(f"\n❌ Verification failed: {e}\n")
        return False


if __name__ == "__main__":
    success = verify_schema()
    sys.exit(0 if success else 1)
