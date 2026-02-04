"""
Run database migrations on Supabase.
Execute SQL migrations using the Supabase service role.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from supabase import create_client
from app.core.config import settings


def run_migration(migration_file: str):
    """Execute a SQL migration file."""

    print(f"🔄 Connecting to Supabase: {settings.supabase_url}")

    # Create admin client with service role key
    supabase = create_client(
        settings.supabase_url,
        settings.supabase_service_role_key
    )

    # Read migration file
    migration_path = Path(__file__).parent.parent / "migrations" / migration_file

    if not migration_path.exists():
        print(f"❌ Migration file not found: {migration_path}")
        return False

    print(f"📄 Reading migration: {migration_file}")

    with open(migration_path, 'r', encoding='utf-8') as f:
        sql = f.read()

    # Split into individual statements (simple approach)
    # Note: This works for most cases but may need refinement for complex SQL
    statements = [s.strip() for s in sql.split(';') if s.strip() and not s.strip().startswith('--')]

    print(f"📊 Found {len(statements)} SQL statements to execute")

    # Execute via RPC call
    try:
        print("\n🚀 Executing migration...")
        print("=" * 60)

        # Supabase Python client doesn't have direct SQL execution
        # We need to use the REST API directly
        import httpx

        headers = {
            "apikey": settings.supabase_service_role_key,
            "Authorization": f"Bearer {settings.supabase_service_role_key}",
            "Content-Type": "application/json"
        }

        # Execute the full SQL via the PostgREST /rpc endpoint
        # Note: This requires creating a function, or using the SQL Editor API

        print("\n⚠️  Direct SQL execution requires Supabase Management API.")
        print("Please execute the migration using one of these methods:\n")

        print("METHOD 1: Supabase Dashboard (Recommended)")
        print("-" * 60)
        print("1. Go to: https://supabase.com/dashboard/project/nltzetpmvsbazhhkuqiq/sql/new")
        print("2. Copy and paste the contents of:")
        print(f"   {migration_path}")
        print("3. Click 'Run' to execute\n")

        print("METHOD 2: Supabase CLI")
        print("-" * 60)
        print("1. Install: npm install -g supabase")
        print("2. Login: supabase login")
        print("3. Link project: supabase link --project-ref nltzetpmvsbazhhkuqiq")
        print(f"4. Run: supabase db execute -f {migration_path.relative_to(Path.cwd())}\n")

        print("METHOD 3: Direct PostgreSQL Connection")
        print("-" * 60)
        print("1. Get your database connection string from Supabase Dashboard")
        print("2. Use psql or any PostgreSQL client")
        print(f"3. Execute: psql <connection-string> -f {migration_path}\n")

        # Write SQL to a temporary file for easy copying
        output_file = Path(__file__).parent.parent / "migration_to_run.sql"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(sql)

        print(f"✅ Migration SQL saved to: {output_file}")
        print("   Copy this file content to Supabase SQL Editor\n")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  ALMIRA - Database Migration Runner")
    print("=" * 60 + "\n")

    # Check if migration file is provided
    if len(sys.argv) > 1:
        migration_file = sys.argv[1]
    else:
        migration_file = "001_initial_schema.sql"

    success = run_migration(migration_file)

    if success:
        print("\n✅ Migration preparation completed!")
        print("   Follow the instructions above to execute the migration.\n")
    else:
        print("\n❌ Migration preparation failed.\n")
        sys.exit(1)
