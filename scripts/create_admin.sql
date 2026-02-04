-- =====================================================
-- CREATE ADMIN USER - SQL Script
-- =====================================================
-- Run this in Supabase SQL Editor after registering
-- a user through the app or Supabase Auth UI
-- =====================================================

-- METHOD 1: Promote existing user to admin by email
-- Replace 'admin@almira.com' with your email
UPDATE profiles
SET role = 'admin'
WHERE email = 'admin@almira.com';

-- Verify the update
SELECT id, email, full_name, role, created_at
FROM profiles
WHERE email = 'admin@almira.com';


-- =====================================================
-- METHOD 2: Promote existing user to admin by ID
-- Replace 'user-uuid-here' with actual user ID
-- =====================================================
UPDATE profiles
SET role = 'admin'
WHERE id = 'user-uuid-here';


-- =====================================================
-- METHOD 3: Create multiple admins at once
-- =====================================================
UPDATE profiles
SET role = 'admin'
WHERE email IN (
  'admin@almira.com',
  'admin2@almira.com',
  'superadmin@almira.com'
);


-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================

-- Check all admin users
SELECT
  id,
  email,
  full_name,
  role,
  is_active,
  created_at
FROM profiles
WHERE role = 'admin'
ORDER BY created_at DESC;

-- Count admins vs customers
SELECT
  role,
  COUNT(*) as count
FROM profiles
GROUP BY role;


-- =====================================================
-- TROUBLESHOOTING
-- =====================================================

-- If profile doesn't exist (should be created by trigger)
-- You may need to create it manually:
INSERT INTO profiles (id, email, full_name, role, is_active)
VALUES (
  'user-id-from-auth-users',
  'admin@almira.com',
  'Admin User',
  'admin',
  true
);

-- Check if user exists in auth.users
SELECT id, email, created_at, email_confirmed_at
FROM auth.users
WHERE email = 'admin@almira.com';


-- =====================================================
-- RESET USER TO CUSTOMER (if needed)
-- =====================================================
UPDATE profiles
SET role = 'customer'
WHERE email = 'admin@almira.com';
