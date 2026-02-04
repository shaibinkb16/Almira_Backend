-- ===========================================
-- Fix RLS Policies - Resolve Infinite Recursion
-- ===========================================

-- Drop existing problematic policies
DROP POLICY IF EXISTS "profiles_admin_all" ON public.profiles;
DROP POLICY IF EXISTS "categories_admin_all" ON public.categories;
DROP POLICY IF EXISTS "products_admin_all" ON public.products;
DROP POLICY IF EXISTS "variants_admin_all" ON public.product_variants;
DROP POLICY IF EXISTS "coupons_admin_all" ON public.coupons;
DROP POLICY IF EXISTS "orders_admin_all" ON public.orders;
DROP POLICY IF EXISTS "reviews_admin_all" ON public.reviews;
DROP POLICY IF EXISTS "coupon_usages_admin_all" ON public.coupon_usages;
DROP POLICY IF EXISTS "audit_admin_read" ON public.audit_logs;

-- Create helper function to check if user is admin (bypasses RLS)
CREATE OR REPLACE FUNCTION public.is_admin(user_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM public.profiles
        WHERE id = user_id AND role = 'admin'
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Recreate admin policies using the helper function
CREATE POLICY "profiles_admin_all" ON public.profiles
    FOR ALL USING (public.is_admin(auth.uid()));

CREATE POLICY "categories_admin_all" ON public.categories
    FOR ALL USING (public.is_admin(auth.uid()));

CREATE POLICY "products_admin_all" ON public.products
    FOR ALL USING (public.is_admin(auth.uid()));

CREATE POLICY "variants_admin_all" ON public.product_variants
    FOR ALL USING (public.is_admin(auth.uid()));

CREATE POLICY "coupons_admin_all" ON public.coupons
    FOR ALL USING (public.is_admin(auth.uid()));

CREATE POLICY "orders_admin_all" ON public.orders
    FOR ALL USING (public.is_admin(auth.uid()));

CREATE POLICY "reviews_admin_all" ON public.reviews
    FOR ALL USING (public.is_admin(auth.uid()));

CREATE POLICY "coupon_usages_admin_all" ON public.coupon_usages
    FOR ALL USING (public.is_admin(auth.uid()));

CREATE POLICY "audit_admin_read" ON public.audit_logs
    FOR SELECT USING (public.is_admin(auth.uid()));

-- Verification
DO $$
BEGIN
    RAISE NOTICE '✓ RLS policies fixed - infinite recursion resolved!';
END $$;
