"""
Create Admin User Script
Creates the first admin user in Supabase
Run this after setting up your Supabase project
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.supabase import get_supabase_admin
from getpass import getpass


def create_admin_user():
    """Create an admin user with provided credentials"""
    print("=" * 50)
    print("ALMIRA - Create Admin User")
    print("=" * 50)
    print()

    # Get admin details
    email = input("Admin Email: ")
    password = getpass("Admin Password (min 8 chars): ")
    confirm_password = getpass("Confirm Password: ")
    full_name = input("Full Name: ")

    # Validate
    if not email or "@" not in email:
        print("❌ Error: Invalid email address")
        return

    if len(password) < 8:
        print("❌ Error: Password must be at least 8 characters")
        return

    if password != confirm_password:
        print("❌ Error: Passwords do not match")
        return

    if not full_name:
        full_name = "Admin User"

    print()
    print(f"Creating admin user...")
    print(f"  Email: {email}")
    print(f"  Name: {full_name}")
    print()

    try:
        # Get Supabase admin client
        admin = get_supabase_admin()

        # Create user in Supabase Auth
        print("1. Creating user in Supabase Auth...")
        auth_response = admin.auth.admin.create_user({
            "email": email,
            "password": password,
            "email_confirm": True,  # Auto-confirm email
            "user_metadata": {
                "full_name": full_name,
            }
        })

        if not auth_response.user:
            print("❌ Error: Failed to create user in Supabase Auth")
            return

        user_id = auth_response.user.id
        print(f"✅ User created with ID: {user_id}")

        # Update profile to admin role
        print("2. Setting admin role in profiles table...")
        result = admin.table("profiles").update({
            "role": "admin",
            "full_name": full_name,
        }).eq("id", user_id).execute()

        if not result.data:
            print("⚠️  Warning: Profile not found. It may be created by trigger.")
            print("   Waiting 2 seconds and retrying...")
            import time
            time.sleep(2)

            result = admin.table("profiles").update({
                "role": "admin",
                "full_name": full_name,
            }).eq("id", user_id).execute()

        if result.data:
            print("✅ Admin role assigned successfully")
        else:
            print("⚠️  Profile update may have failed. Check manually.")

        # Verify admin was created
        print("3. Verifying admin user...")
        verify = admin.table("profiles").select("id, email, role, full_name").eq("id", user_id).single().execute()

        if verify.data and verify.data.get("role") == "admin":
            print()
            print("=" * 50)
            print("✅ SUCCESS! Admin user created")
            print("=" * 50)
            print()
            print("Admin Credentials:")
            print(f"  Email: {email}")
            print(f"  Password: {password}")
            print(f"  Role: admin")
            print()
            print("Login at: http://localhost:5173/admin")
            print()
            print("⚠️  IMPORTANT: Save these credentials securely!")
            print("=" * 50)
        else:
            print()
            print("⚠️  Warning: User created but admin role not confirmed.")
            print("   Please check Supabase dashboard and verify role.")
            print()
            print("Manual verification SQL:")
            print(f"  SELECT * FROM profiles WHERE id = '{user_id}';")

    except Exception as e:
        print()
        print(f"❌ Error: {str(e)}")
        print()
        print("Possible issues:")
        print("  - Supabase credentials not configured in .env")
        print("  - Database connection failed")
        print("  - User with this email already exists")
        print("  - profiles table doesn't exist or trigger not set up")
        return


def list_admins():
    """List all admin users"""
    try:
        admin = get_supabase_admin()
        result = admin.table("profiles").select("id, email, full_name, role, created_at").eq("role", "admin").execute()

        if not result.data:
            print("No admin users found.")
            return

        print()
        print("Current Admin Users:")
        print("-" * 80)
        print(f"{'Email':<30} {'Name':<25} {'Created':<20}")
        print("-" * 80)
        for user in result.data:
            email = user.get("email", "N/A")
            name = user.get("full_name", "N/A")
            created = user.get("created_at", "N/A")[:10] if user.get("created_at") else "N/A"
            print(f"{email:<30} {name:<25} {created:<20}")
        print("-" * 80)
        print(f"Total: {len(result.data)} admin user(s)")
        print()

    except Exception as e:
        print(f"Error listing admins: {e}")


if __name__ == "__main__":
    print()
    choice = input("Options:\n  1. Create new admin user\n  2. List existing admins\n\nSelect (1 or 2): ")
    print()

    if choice == "1":
        create_admin_user()
    elif choice == "2":
        list_admins()
    else:
        print("Invalid choice")
