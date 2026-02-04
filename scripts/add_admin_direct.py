"""
Direct Admin User Creation
Automatically creates admin user with predefined credentials
Run this to instantly create an admin account
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.supabase import get_supabase_admin

# ==========================================
# ADMIN CREDENTIALS
# ==========================================
ADMIN_EMAIL = "admin@almira.com"
ADMIN_PASSWORD = "Admin@2026!Almira"
ADMIN_NAME = "Admin User"


def create_admin_directly():
    """Create admin user with predefined credentials"""
    print("=" * 60)
    print("ALMIRA - Direct Admin Creation")
    print("=" * 60)
    print()
    print("Creating admin user with:")
    print(f"  Email: {ADMIN_EMAIL}")
    print(f"  Password: {ADMIN_PASSWORD}")
    print(f"  Name: {ADMIN_NAME}")
    print()

    try:
        # Get Supabase admin client
        admin = get_supabase_admin()

        # Check if user already exists
        print("1. Checking if user already exists...")
        existing = admin.table("profiles").select("id, email, role").eq("email", ADMIN_EMAIL).execute()

        if existing.data:
            user = existing.data[0]
            if user.get("role") == "admin":
                print()
                print("✅ Admin user already exists!")
                print(f"   Email: {ADMIN_EMAIL}")
                print(f"   Role: {user.get('role')}")
                print()
                print("You can login at: http://localhost:5173/admin")
                print(f"Email: {ADMIN_EMAIL}")
                print(f"Password: {ADMIN_PASSWORD}")
                print("=" * 60)
                return
            else:
                # User exists but not admin, promote them
                print(f"   User exists with role: {user.get('role')}")
                print("   Promoting to admin...")
                admin.table("profiles").update({"role": "admin"}).eq("email", ADMIN_EMAIL).execute()
                print("✅ User promoted to admin!")
                print()
                print("Login at: http://localhost:5173/admin")
                print(f"Email: {ADMIN_EMAIL}")
                print(f"Password: [your existing password]")
                print("=" * 60)
                return

        # Create new user
        print("   User does not exist. Creating new user...")

        # Create user in Supabase Auth
        print("2. Creating user in Supabase Auth...")
        auth_response = admin.auth.admin.create_user({
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD,
            "email_confirm": True,  # Auto-confirm email
            "user_metadata": {
                "full_name": ADMIN_NAME,
            }
        })

        if not auth_response.user:
            print("❌ Error: Failed to create user in Supabase Auth")
            print("   The email might already be registered.")
            print()
            print("To check, go to Supabase Dashboard:")
            print("  Authentication → Users → Search for", ADMIN_EMAIL)
            return

        user_id = auth_response.user.id
        print(f"✅ User created with ID: {user_id}")

        # Wait a moment for trigger to create profile
        print("3. Waiting for profile creation...")
        import time
        time.sleep(2)

        # Update profile to admin role
        print("4. Setting admin role...")
        result = admin.table("profiles").update({
            "role": "admin",
            "full_name": ADMIN_NAME,
        }).eq("id", user_id).execute()

        if not result.data:
            # Profile might not exist yet, try to create it
            print("   Profile not found, creating manually...")
            admin.table("profiles").insert({
                "id": user_id,
                "email": ADMIN_EMAIL,
                "full_name": ADMIN_NAME,
                "role": "admin",
                "is_active": True,
            }).execute()
            print("✅ Profile created with admin role")
        else:
            print("✅ Admin role assigned")

        # Verify
        print("5. Verifying admin user...")
        verify = admin.table("profiles").select("id, email, role, full_name").eq("id", user_id).single().execute()

        if verify.data and verify.data.get("role") == "admin":
            print()
            print("=" * 60)
            print("✅ SUCCESS! Admin user created and verified")
            print("=" * 60)
            print()
            print("ADMIN LOGIN CREDENTIALS:")
            print("-" * 60)
            print(f"  URL:      http://localhost:5173/admin")
            print(f"  Email:    {ADMIN_EMAIL}")
            print(f"  Password: {ADMIN_PASSWORD}")
            print(f"  Role:     admin")
            print("-" * 60)
            print()
            print("⚠️  IMPORTANT: Save these credentials securely!")
            print("⚠️  Change password after first login for security")
            print()
            print("=" * 60)
        else:
            print()
            print("⚠️  Warning: User created but verification failed")
            print("   Please check Supabase dashboard manually")

    except Exception as e:
        print()
        print(f"❌ Error: {str(e)}")
        print()
        print("Troubleshooting:")
        print("  1. Check Backend/.env has correct Supabase credentials:")
        print("     - SUPABASE_URL")
        print("     - SUPABASE_SERVICE_KEY (not anon key!)")
        print()
        print("  2. Verify Supabase database is accessible")
        print()
        print("  3. Check if profiles table exists:")
        print("     SELECT * FROM profiles LIMIT 1;")
        print()
        print("  4. If user already exists, promote via SQL:")
        print(f"     UPDATE profiles SET role = 'admin' WHERE email = '{ADMIN_EMAIL}';")
        print()
        return


if __name__ == "__main__":
    create_admin_directly()
