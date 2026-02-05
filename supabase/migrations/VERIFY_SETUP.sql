-- =====================================================
-- ALMIRA - Setup Verification Query
-- =====================================================
-- Run this to verify your database setup is complete
-- Execute this in Supabase SQL Editor

-- ===========================================
-- 1. CHECK ALL TABLES EXIST
-- ===========================================
SELECT
    '✓ DATABASE TABLES' AS check_type,
    COUNT(*) AS found,
    15 AS expected,
    CASE WHEN COUNT(*) = 15 THEN '✅ PASS' ELSE '❌ MISSING TABLES' END AS status
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN (
    'profiles', 'addresses', 'categories', 'products', 'product_variants',
    'orders', 'order_items', 'cart_items', 'wishlist_items', 'reviews',
    'coupons', 'coupon_usages', 'audit_logs',
    'contact_submissions', 'support_tickets', 'support_messages'
)

UNION ALL

-- ===========================================
-- 2. CHECK STORAGE BUCKETS
-- ===========================================
SELECT
    '✓ STORAGE BUCKETS' AS check_type,
    COUNT(*) AS found,
    4 AS expected,
    CASE WHEN COUNT(*) = 4 THEN '✅ PASS' ELSE '❌ MISSING BUCKETS' END AS status
FROM storage.buckets
WHERE id IN ('products', 'reviews', 'support', 'avatars')

UNION ALL

-- ===========================================
-- 3. CHECK RLS POLICIES
-- ===========================================
SELECT
    '✓ RLS POLICIES' AS check_type,
    COUNT(*) AS found,
    0 AS expected,
    CASE WHEN COUNT(*) > 30 THEN '✅ PASS' ELSE '⚠ FEW POLICIES' END AS status
FROM pg_policies
WHERE schemaname = 'public'

UNION ALL

-- ===========================================
-- 4. CHECK STORAGE POLICIES
-- ===========================================
SELECT
    '✓ STORAGE POLICIES' AS check_type,
    COUNT(*) AS found,
    0 AS expected,
    CASE WHEN COUNT(*) > 10 THEN '✅ PASS' ELSE '⚠ FEW POLICIES' END AS status
FROM pg_policies
WHERE schemaname = 'storage'

UNION ALL

-- ===========================================
-- 5. CHECK TRIGGERS & FUNCTIONS
-- ===========================================
SELECT
    '✓ TRIGGERS' AS check_type,
    COUNT(*) AS found,
    0 AS expected,
    CASE WHEN COUNT(*) > 10 THEN '✅ PASS' ELSE '⚠ FEW TRIGGERS' END AS status
FROM information_schema.triggers
WHERE trigger_schema = 'public'

UNION ALL

-- ===========================================
-- 6. CHECK CATEGORIES SEEDED
-- ===========================================
SELECT
    '✓ SEED DATA (Categories)' AS check_type,
    COUNT(*) AS found,
    10 AS expected,
    CASE WHEN COUNT(*) >= 10 THEN '✅ PASS' ELSE '❌ NO SEED DATA' END AS status
FROM public.categories

UNION ALL

-- ===========================================
-- 7. CHECK ADMIN USER
-- ===========================================
SELECT
    '✓ ADMIN USER' AS check_type,
    COUNT(*) AS found,
    1 AS expected,
    CASE
        WHEN COUNT(*) = 0 THEN '❌ NO ADMIN USER'
        WHEN COUNT(*) >= 1 THEN '✅ PASS'
    END AS status
FROM public.profiles
WHERE role = 'admin';

-- ===========================================
-- DETAILED TABLE LIST
-- ===========================================
SELECT
    '
========================================
DETAILED TABLE INFORMATION
========================================' AS info;

SELECT
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE columns.table_name = tables.table_name) AS columns,
    (SELECT COUNT(*) FROM pg_indexes WHERE schemaname = 'public' AND tablename = tables.table_name) AS indexes,
    CASE
        WHEN EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = tables.table_name AND rowsecurity = true)
        THEN '✓ Enabled'
        ELSE '✗ Disabled'
    END AS rls_enabled
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_type = 'BASE TABLE'
ORDER BY table_name;

-- ===========================================
-- STORAGE BUCKET DETAILS
-- ===========================================
SELECT
    '
========================================
STORAGE BUCKET DETAILS
========================================' AS info;

SELECT
    id AS bucket_name,
    CASE WHEN public THEN 'Public' ELSE 'Private' END AS access,
    ROUND(file_size_limit / 1024.0 / 1024.0, 1) || ' MB' AS max_size,
    array_length(allowed_mime_types, 1) AS allowed_types,
    created_at
FROM storage.buckets
WHERE id IN ('products', 'reviews', 'support', 'avatars')
ORDER BY id;

-- ===========================================
-- ADMIN USER DETAILS
-- ===========================================
SELECT
    '
========================================
ADMIN USER DETAILS
========================================' AS info;

SELECT
    email,
    full_name,
    role,
    is_active,
    email_verified,
    created_at
FROM public.profiles
WHERE role = 'admin'
ORDER BY created_at DESC;

-- ===========================================
-- FINAL SUMMARY
-- ===========================================
SELECT
    '
========================================
SETUP STATUS SUMMARY
========================================' AS info;

SELECT
    CASE
        WHEN (
            (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'
             AND table_name IN ('profiles', 'products', 'orders', 'contact_submissions', 'support_tickets')) = 5
            AND (SELECT COUNT(*) FROM storage.buckets WHERE id IN ('products', 'reviews', 'support', 'avatars')) = 4
            AND (SELECT COUNT(*) FROM public.profiles WHERE role = 'admin') >= 1
        ) THEN '
✅ ✅ ✅ ALL CHECKS PASSED ✅ ✅ ✅

Your Almira E-Commerce setup is COMPLETE!

Next steps:
1. Start backend: cd Backend && uvicorn app.main:app --reload
2. Start frontend: cd Frontend && npm run dev
3. Login as admin: http://localhost:5173/admin
   Email: admin@almira.com
   Password: Admin@2026!Almira

Happy selling! 🚀
'
        ELSE '
❌ SETUP INCOMPLETE

Please run all migration files in order:
1. 001_initial_schema.sql
2. 002_fix_rls_policies.sql
3. 003_support_contact_tables.sql
4. 004_storage_buckets_setup.sql

Then create admin user using:
- SQL: UPDATE profiles SET role = ''admin'' WHERE email = ''admin@almira.com''
- Or: cd Backend/scripts && python add_admin_direct.py

Run this verification script again after completing setup.
'
    END AS final_status;
