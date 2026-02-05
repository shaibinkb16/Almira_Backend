-- =====================================================
-- ALMIRA - Supabase Storage Buckets Setup
-- =====================================================
-- Execute this in Supabase SQL Editor
-- Creates storage buckets and access policies

-- ===========================================
-- 1. CREATE STORAGE BUCKETS
-- ===========================================

-- Products bucket (admin only uploads, public read)
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'products',
    'products',
    true,
    5242880, -- 5MB
    ARRAY['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'image/gif']
)
ON CONFLICT (id) DO NOTHING;

-- Reviews bucket (authenticated users upload, public read)
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'reviews',
    'reviews',
    true,
    5242880, -- 5MB
    ARRAY['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'image/gif']
)
ON CONFLICT (id) DO NOTHING;

-- Support bucket (authenticated users upload, private)
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'support',
    'support',
    false,
    10485760, -- 10MB
    ARRAY['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'image/gif',
          'application/pdf', 'application/msword',
          'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
)
ON CONFLICT (id) DO NOTHING;

-- Avatars bucket (authenticated users upload, public read)
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'avatars',
    'avatars',
    true,
    2097152, -- 2MB
    ARRAY['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
)
ON CONFLICT (id) DO NOTHING;

-- ===========================================
-- 2. PRODUCTS BUCKET POLICIES
-- ===========================================

-- Public read access
CREATE POLICY "products_public_read"
ON storage.objects FOR SELECT
TO public
USING (bucket_id = 'products');

-- Admin upload
CREATE POLICY "products_admin_upload"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (
    bucket_id = 'products' AND
    EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin')
);

-- Admin update
CREATE POLICY "products_admin_update"
ON storage.objects FOR UPDATE
TO authenticated
USING (
    bucket_id = 'products' AND
    EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin')
);

-- Admin delete
CREATE POLICY "products_admin_delete"
ON storage.objects FOR DELETE
TO authenticated
USING (
    bucket_id = 'products' AND
    EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin')
);

-- ===========================================
-- 3. REVIEWS BUCKET POLICIES
-- ===========================================

-- Public read access
CREATE POLICY "reviews_public_read"
ON storage.objects FOR SELECT
TO public
USING (bucket_id = 'reviews');

-- Authenticated users can upload to their own folder
CREATE POLICY "reviews_auth_upload"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (
    bucket_id = 'reviews' AND
    (storage.foldername(name))[1] = auth.uid()::text
);

-- Users can delete their own files
CREATE POLICY "reviews_own_delete"
ON storage.objects FOR DELETE
TO authenticated
USING (
    bucket_id = 'reviews' AND
    (storage.foldername(name))[1] = auth.uid()::text
);

-- Admin can delete any file
CREATE POLICY "reviews_admin_delete"
ON storage.objects FOR DELETE
TO authenticated
USING (
    bucket_id = 'reviews' AND
    EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin')
);

-- ===========================================
-- 4. SUPPORT BUCKET POLICIES
-- ===========================================

-- Authenticated users can upload to their own folder
CREATE POLICY "support_auth_upload"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (
    bucket_id = 'support' AND
    (storage.foldername(name))[1] = auth.uid()::text
);

-- Users can read their own files
CREATE POLICY "support_own_read"
ON storage.objects FOR SELECT
TO authenticated
USING (
    bucket_id = 'support' AND
    (storage.foldername(name))[1] = auth.uid()::text
);

-- Admin can read all files
CREATE POLICY "support_admin_read"
ON storage.objects FOR SELECT
TO authenticated
USING (
    bucket_id = 'support' AND
    EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin')
);

-- Users can delete their own files
CREATE POLICY "support_own_delete"
ON storage.objects FOR DELETE
TO authenticated
USING (
    bucket_id = 'support' AND
    (storage.foldername(name))[1] = auth.uid()::text
);

-- ===========================================
-- 5. AVATARS BUCKET POLICIES
-- ===========================================

-- Public read access
CREATE POLICY "avatars_public_read"
ON storage.objects FOR SELECT
TO public
USING (bucket_id = 'avatars');

-- Authenticated users can upload to their own folder
CREATE POLICY "avatars_auth_upload"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (
    bucket_id = 'avatars' AND
    (storage.foldername(name))[1] = auth.uid()::text
);

-- Users can update their own avatar
CREATE POLICY "avatars_own_update"
ON storage.objects FOR UPDATE
TO authenticated
USING (
    bucket_id = 'avatars' AND
    (storage.foldername(name))[1] = auth.uid()::text
);

-- Users can delete their own avatar
CREATE POLICY "avatars_own_delete"
ON storage.objects FOR DELETE
TO authenticated
USING (
    bucket_id = 'avatars' AND
    (storage.foldername(name))[1] = auth.uid()::text
);

-- ===========================================
-- VERIFICATION
-- ===========================================

DO $$
DECLARE
    bucket_count INTEGER;
    policy_count INTEGER;
BEGIN
    -- Count buckets
    SELECT COUNT(*) INTO bucket_count
    FROM storage.buckets
    WHERE id IN ('products', 'reviews', 'support', 'avatars');

    -- Count policies
    SELECT COUNT(*) INTO policy_count
    FROM pg_policies
    WHERE schemaname = 'storage' AND tablename = 'objects'
    AND policyname LIKE 'products_%'
       OR policyname LIKE 'reviews_%'
       OR policyname LIKE 'support_%'
       OR policyname LIKE 'avatars_%';

    RAISE NOTICE '✓ Storage setup completed!';
    RAISE NOTICE '✓ Created % buckets: products, reviews, support, avatars', bucket_count;
    RAISE NOTICE '✓ Applied % storage policies', policy_count;
END $$;
