"""
Run Supabase Migrations
"""
from supabase import create_client
import os
from pathlib import Path

SUPABASE_URL = "https://nltzetpmvsbazhhkuqiq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5sdHpldHBtdnNiYXpoaGt1cWlxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDIwODY4NywiZXhwIjoyMDg1Nzg0Njg3fQ.4I-SurqZq2mw-ffo5aMrL8Z6kd0f-_O0dfU2Og5TUsM"

def run_migration(supabase, migration_file):
    """Execute a migration file"""
    print(f"\n{'='*60}")
    print(f"Running: {migration_file.name}")
    print('='*60)

    with open(migration_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    try:
        # Use the REST API to execute SQL via RPC
        result = supabase.rpc('exec_sql', {'query': sql_content}).execute()
        print(f"✓ SUCCESS: {migration_file.name}")
        return True
    except Exception as e:
        print(f"✗ ERROR: {migration_file.name}")
        print(f"   {str(e)}")
        return False

def main():
    # Initialize Supabase client
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Get migrations directory
    migrations_dir = Path(__file__).parent

    # List of migrations to run in order
    migrations = [
        "001_initial_schema.sql",
        "002_fix_rls_policies.sql",
        "003_support_contact_tables.sql",
        "004_storage_buckets_setup.sql",
        "005_add_payment_fields.sql",
    ]

    print("Starting migration process...")
    print(f"Project: {SUPABASE_URL}")

    results = []
    for migration_name in migrations:
        migration_file = migrations_dir / migration_name
        if migration_file.exists():
            success = run_migration(supabase, migration_file)
            results.append((migration_name, success))
        else:
            print(f"\n⚠ WARNING: {migration_name} not found, skipping...")
            results.append((migration_name, False))

    # Summary
    print("\n" + "="*60)
    print("MIGRATION SUMMARY")
    print("="*60)
    for name, success in results:
        status = "✓ SUCCESS" if success else "✗ FAILED"
        print(f"{status}: {name}")

    total = len(results)
    passed = sum(1 for _, success in results if success)
    print(f"\nTotal: {passed}/{total} migrations applied successfully")

if __name__ == "__main__":
    main()
