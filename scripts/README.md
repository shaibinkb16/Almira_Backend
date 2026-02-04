# Admin Creation Scripts

Quick scripts to create admin users for Almira E-Commerce.

---

## 🚀 Quick Start (One Command)

### Windows

```bash
cd Backend\scripts
create_admin.bat
```

### Linux/Mac

```bash
cd Backend/scripts
python add_admin_direct.py
```

**That's it!** Admin user is created automatically.

---

## 📋 What Gets Created

**Default Admin Credentials:**
```
Email:    admin@almira.com
Password: Admin@2026!Almira
Role:     admin
Name:     Admin User
```

**Login URL:** http://localhost:5173/admin

---

## 📝 Available Scripts

### 1. `add_admin_direct.py` (Recommended)

**Automatically creates admin with predefined credentials.**

```bash
python add_admin_direct.py
```

**What it does:**
- ✅ Checks if admin already exists
- ✅ Creates user in Supabase Auth
- ✅ Sets role to 'admin' in profiles table
- ✅ Auto-confirms email
- ✅ Shows credentials after creation

**Output:**
```
✅ SUCCESS! Admin user created and verified

ADMIN LOGIN CREDENTIALS:
  URL:      http://localhost:5173/admin
  Email:    admin@almira.com
  Password: Admin@2026!Almira
  Role:     admin
```

---

### 2. `create_admin.py` (Interactive)

**Lets you choose email and password.**

```bash
python create_admin.py
```

**Options:**
1. Create new admin user (custom credentials)
2. List existing admins

**Example:**
```
Admin Email: myemail@example.com
Admin Password: MySecurePass123!
Confirm Password: MySecurePass123!
Full Name: My Name
```

---

### 3. `create_admin.sql` (Manual SQL)

**Run directly in Supabase SQL Editor.**

```sql
-- After registering user normally, promote to admin:
UPDATE profiles
SET role = 'admin'
WHERE email = 'your@email.com';
```

---

## 🔧 Requirements

1. **Backend .env configured:**
   ```env
   SUPABASE_URL=your-project-url
   SUPABASE_SERVICE_KEY=your-service-key
   ```

2. **Python dependencies installed:**
   ```bash
   cd Backend
   pip install -r requirements.txt
   ```

3. **Supabase database set up:**
   - `profiles` table exists
   - Auth trigger configured

---

## ✅ Verification Steps

After running script:

1. **Check output for success message:**
   ```
   ✅ SUCCESS! Admin user created and verified
   ```

2. **Try logging in:**
   - Go to http://localhost:5173/admin
   - Email: `admin@almira.com`
   - Password: `Admin@2026!Almira`

3. **Verify in Supabase Dashboard:**
   - **Authentication** → **Users** → Find admin@almira.com
   - **Table Editor** → **profiles** → Check role = 'admin'

---

## 🐛 Troubleshooting

### Error: "Failed to create user in Supabase Auth"

**Cause:** User already exists

**Solution:**
```bash
# Check if user exists
python create_admin.py
# Select option 2: List existing admins

# OR promote existing user via SQL:
UPDATE profiles SET role = 'admin' WHERE email = 'admin@almira.com';
```

### Error: "Invalid Supabase credentials"

**Cause:** .env file missing or incorrect

**Solution:**
1. Check `Backend/.env` exists
2. Verify SUPABASE_URL is correct
3. Verify SUPABASE_SERVICE_KEY (not anon key!)
4. Restart script

### Error: "Profile not found"

**Cause:** Database trigger not working

**Solution:**
```sql
-- Manually create profile in Supabase SQL Editor:
INSERT INTO profiles (id, email, full_name, role, is_active)
SELECT
  id,
  email,
  'Admin User',
  'admin',
  true
FROM auth.users
WHERE email = 'admin@almira.com';
```

### Script runs but admin can't login

**Cause:** Role not updated or email not confirmed

**Solution:**
```sql
-- Check user status
SELECT id, email, role, is_active FROM profiles WHERE email = 'admin@almira.com';

-- Update role
UPDATE profiles SET role = 'admin' WHERE email = 'admin@almira.com';

-- Activate account
UPDATE profiles SET is_active = true WHERE email = 'admin@almira.com';
```

---

## 🔒 Security Notes

**Default Password:**
- Default password is `Admin@2026!Almira`
- **Change it immediately after first login!**
- Use a strong, unique password

**Production:**
- Delete or disable default admin after creating your own
- Use unique credentials for production
- Enable 2FA when available
- Monitor admin activity logs

---

## 📊 Managing Admins

### List All Admins

```bash
python create_admin.py
# Select option 2
```

### Promote User to Admin

```sql
UPDATE profiles SET role = 'admin' WHERE email = 'user@example.com';
```

### Demote Admin to Customer

```sql
UPDATE profiles SET role = 'customer' WHERE email = 'admin@example.com';
```

### Delete Admin (Deactivate)

```sql
UPDATE profiles SET is_active = false WHERE email = 'admin@example.com';
```

---

## 📞 Need Help?

1. Check script output for error messages
2. Verify Supabase credentials in .env
3. Check Supabase logs in dashboard
4. Run verification queries in SQL Editor
5. Check Backend/logs/ for errors

---

**Quick Command Reference:**

```bash
# Create admin (automatic)
python add_admin_direct.py

# Create admin (interactive)
python create_admin.py

# List admins
python create_admin.py  # then select option 2

# Windows shortcut
create_admin.bat
```

---

**Default Credentials:** admin@almira.com / Admin@2026!Almira

**Login URL:** http://localhost:5173/admin
