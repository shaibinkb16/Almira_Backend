-- ===========================================
-- ALMIRA E-COMMERCE - Database Schema
-- ===========================================
-- Clean, properly connected tables with foreign keys
-- Execute this in Supabase SQL Editor

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ===========================================
-- 1. PROFILES (extends auth.users)
-- ===========================================
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL UNIQUE,
    full_name TEXT,
    avatar_url TEXT,
    phone TEXT,
    date_of_birth DATE,
    gender TEXT CHECK (gender IN ('male', 'female', 'other')),
    role TEXT NOT NULL DEFAULT 'customer' CHECK (role IN ('customer', 'admin')),
    is_active BOOLEAN NOT NULL DEFAULT true,
    email_verified BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_profiles_email ON public.profiles(email);
CREATE INDEX IF NOT EXISTS idx_profiles_role ON public.profiles(role);

-- ===========================================
-- 2. ADDRESSES (belongs to profiles)
-- ===========================================
CREATE TABLE IF NOT EXISTS public.addresses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    full_name TEXT NOT NULL,
    phone TEXT NOT NULL,
    address_line1 TEXT NOT NULL,
    address_line2 TEXT,
    landmark TEXT,
    city TEXT NOT NULL,
    state TEXT NOT NULL,
    postal_code TEXT NOT NULL CHECK (postal_code ~ '^\d{6}$'),
    country TEXT NOT NULL DEFAULT 'India',
    address_type TEXT NOT NULL DEFAULT 'shipping' CHECK (address_type IN ('shipping', 'billing', 'both')),
    is_default BOOLEAN NOT NULL DEFAULT false,
    label TEXT CHECK (label IN ('home', 'work', 'other')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_addresses_user
        FOREIGN KEY (user_id) REFERENCES public.profiles(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_addresses_user_id ON public.addresses(user_id);
CREATE INDEX IF NOT EXISTS idx_addresses_default ON public.addresses(user_id, is_default) WHERE is_default = true;

-- ===========================================
-- 3. CATEGORIES (self-referencing hierarchy)
-- ===========================================
CREATE TABLE IF NOT EXISTS public.categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    description TEXT,
    image_url TEXT,
    parent_id UUID,
    is_active BOOLEAN NOT NULL DEFAULT true,
    display_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_categories_parent
        FOREIGN KEY (parent_id) REFERENCES public.categories(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_categories_slug ON public.categories(slug);
CREATE INDEX IF NOT EXISTS idx_categories_parent ON public.categories(parent_id);
CREATE INDEX IF NOT EXISTS idx_categories_active ON public.categories(is_active) WHERE is_active = true;

-- ===========================================
-- 4. PRODUCTS (belongs to category)
-- ===========================================
CREATE TABLE IF NOT EXISTS public.products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    description TEXT,
    short_description TEXT,
    base_price DECIMAL(12, 2) NOT NULL CHECK (base_price > 0),
    sale_price DECIMAL(12, 2) CHECK (sale_price IS NULL OR sale_price < base_price),
    cost_price DECIMAL(12, 2),
    sku TEXT NOT NULL UNIQUE,
    barcode TEXT,
    stock_quantity INTEGER NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
    low_stock_threshold INTEGER DEFAULT 10,
    category_id UUID,
    status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'out_of_stock', 'archived')),
    is_featured BOOLEAN NOT NULL DEFAULT false,
    -- Images stored as JSONB array: [{"url": "", "alt": "", "position": 0}]
    images JSONB NOT NULL DEFAULT '[]',
    tags TEXT[] DEFAULT '{}',
    -- Jewelry-specific fields
    material TEXT,
    purity TEXT,
    weight DECIMAL(10, 3),
    weight_unit TEXT DEFAULT 'gm' CHECK (weight_unit IN ('gm', 'kg', 'ct')),
    gemstones JSONB,
    -- Fashion-specific
    brand TEXT,
    size_chart JSONB,
    care_instructions TEXT,
    -- SEO
    meta_title TEXT,
    meta_description TEXT,
    -- Stats (auto-updated by trigger)
    rating DECIMAL(3, 2) NOT NULL DEFAULT 0 CHECK (rating >= 0 AND rating <= 5),
    review_count INTEGER NOT NULL DEFAULT 0 CHECK (review_count >= 0),
    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_products_category
        FOREIGN KEY (category_id) REFERENCES public.categories(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_products_slug ON public.products(slug);
CREATE INDEX IF NOT EXISTS idx_products_sku ON public.products(sku);
CREATE INDEX IF NOT EXISTS idx_products_category ON public.products(category_id);
CREATE INDEX IF NOT EXISTS idx_products_status ON public.products(status);
CREATE INDEX IF NOT EXISTS idx_products_price ON public.products(base_price);
CREATE INDEX IF NOT EXISTS idx_products_featured ON public.products(is_featured) WHERE is_featured = true;
CREATE INDEX IF NOT EXISTS idx_products_search ON public.products
    USING GIN (to_tsvector('english', name || ' ' || COALESCE(description, '') || ' ' || COALESCE(brand, '')));

-- ===========================================
-- 5. PRODUCT VARIANTS (belongs to product)
-- ===========================================
CREATE TABLE IF NOT EXISTS public.product_variants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID NOT NULL,
    sku TEXT NOT NULL UNIQUE,
    name TEXT,
    size TEXT,
    color TEXT,
    color_code TEXT,
    material TEXT,
    price_adjustment DECIMAL(12, 2) NOT NULL DEFAULT 0,
    stock_quantity INTEGER NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
    image_url TEXT,
    is_active BOOLEAN NOT NULL DEFAULT true,
    display_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_variants_product
        FOREIGN KEY (product_id) REFERENCES public.products(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_variants_product ON public.product_variants(product_id);
CREATE INDEX IF NOT EXISTS idx_variants_sku ON public.product_variants(sku);

-- ===========================================
-- 6. COUPONS (standalone - referenced by orders)
-- ===========================================
CREATE TABLE IF NOT EXISTS public.coupons (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code TEXT NOT NULL UNIQUE,
    description TEXT,
    discount_type TEXT NOT NULL CHECK (discount_type IN ('percentage', 'fixed')),
    discount_value DECIMAL(12, 2) NOT NULL CHECK (discount_value > 0),
    min_order_amount DECIMAL(12, 2) DEFAULT 0,
    max_discount_amount DECIMAL(12, 2),
    usage_limit INTEGER,
    usage_limit_per_user INTEGER DEFAULT 1,
    used_count INTEGER NOT NULL DEFAULT 0,
    applicable_categories UUID[],
    applicable_products UUID[],
    valid_from TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    valid_until TIMESTAMPTZ,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_coupons_code ON public.coupons(code);
CREATE INDEX IF NOT EXISTS idx_coupons_active ON public.coupons(is_active, valid_from, valid_until);

-- ===========================================
-- 7. ORDERS (belongs to profile, optionally uses coupon)
-- ===========================================
CREATE TABLE IF NOT EXISTS public.orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_number TEXT NOT NULL UNIQUE,
    user_id UUID NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'confirmed', 'processing', 'shipped', 'out_for_delivery', 'delivered', 'cancelled', 'returned', 'refunded')),
    payment_status TEXT NOT NULL DEFAULT 'pending'
        CHECK (payment_status IN ('pending', 'paid', 'failed', 'refunded', 'partially_refunded')),
    payment_method TEXT NOT NULL
        CHECK (payment_method IN ('cod', 'card', 'upi', 'netbanking', 'wallet')),
    payment_id TEXT,
    -- Amounts (in INR)
    subtotal DECIMAL(12, 2) NOT NULL CHECK (subtotal >= 0),
    shipping_amount DECIMAL(12, 2) NOT NULL DEFAULT 0 CHECK (shipping_amount >= 0),
    tax_amount DECIMAL(12, 2) NOT NULL DEFAULT 0 CHECK (tax_amount >= 0),
    discount_amount DECIMAL(12, 2) NOT NULL DEFAULT 0 CHECK (discount_amount >= 0),
    total_amount DECIMAL(12, 2) NOT NULL CHECK (total_amount >= 0),
    -- Coupon reference
    coupon_id UUID,
    coupon_code TEXT,
    -- Address snapshots (denormalized for order history)
    shipping_address JSONB NOT NULL,
    billing_address JSONB NOT NULL,
    -- Delivery
    shipping_method TEXT DEFAULT 'standard',
    tracking_number TEXT,
    tracking_url TEXT,
    estimated_delivery DATE,
    -- Notes
    customer_notes TEXT,
    admin_notes TEXT,
    cancellation_reason TEXT,
    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    confirmed_at TIMESTAMPTZ,
    shipped_at TIMESTAMPTZ,
    delivered_at TIMESTAMPTZ,
    cancelled_at TIMESTAMPTZ,

    CONSTRAINT fk_orders_user
        FOREIGN KEY (user_id) REFERENCES public.profiles(id) ON DELETE RESTRICT,
    CONSTRAINT fk_orders_coupon
        FOREIGN KEY (coupon_id) REFERENCES public.coupons(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_orders_user ON public.orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_number ON public.orders(order_number);
CREATE INDEX IF NOT EXISTS idx_orders_status ON public.orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_payment ON public.orders(payment_status);
CREATE INDEX IF NOT EXISTS idx_orders_created ON public.orders(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_orders_coupon ON public.orders(coupon_id) WHERE coupon_id IS NOT NULL;

-- ===========================================
-- 8. ORDER ITEMS (belongs to order, references product/variant)
-- ===========================================
CREATE TABLE IF NOT EXISTS public.order_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID NOT NULL,
    product_id UUID NOT NULL,
    variant_id UUID,
    -- Snapshot of product details at time of purchase (immutable)
    product_name TEXT NOT NULL,
    product_slug TEXT NOT NULL,
    product_image TEXT,
    product_sku TEXT NOT NULL,
    variant_name TEXT,
    variant_sku TEXT,
    -- Pricing
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(12, 2) NOT NULL CHECK (unit_price >= 0),
    discount_amount DECIMAL(12, 2) NOT NULL DEFAULT 0,
    total_price DECIMAL(12, 2) NOT NULL CHECK (total_price >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_order_items_order
        FOREIGN KEY (order_id) REFERENCES public.orders(id) ON DELETE CASCADE,
    CONSTRAINT fk_order_items_product
        FOREIGN KEY (product_id) REFERENCES public.products(id) ON DELETE RESTRICT,
    CONSTRAINT fk_order_items_variant
        FOREIGN KEY (variant_id) REFERENCES public.product_variants(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_order_items_order ON public.order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product ON public.order_items(product_id);

-- ===========================================
-- 9. CART ITEMS (belongs to profile, references product/variant)
-- ===========================================
CREATE TABLE IF NOT EXISTS public.cart_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    product_id UUID NOT NULL,
    variant_id UUID,
    quantity INTEGER NOT NULL DEFAULT 1 CHECK (quantity > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_cart_user
        FOREIGN KEY (user_id) REFERENCES public.profiles(id) ON DELETE CASCADE,
    CONSTRAINT fk_cart_product
        FOREIGN KEY (product_id) REFERENCES public.products(id) ON DELETE CASCADE,
    CONSTRAINT fk_cart_variant
        FOREIGN KEY (variant_id) REFERENCES public.product_variants(id) ON DELETE CASCADE,
    CONSTRAINT uq_cart_item UNIQUE(user_id, product_id, variant_id)
);

CREATE INDEX IF NOT EXISTS idx_cart_user ON public.cart_items(user_id);

-- ===========================================
-- 10. WISHLIST ITEMS (belongs to profile, references product)
-- ===========================================
CREATE TABLE IF NOT EXISTS public.wishlist_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    product_id UUID NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_wishlist_user
        FOREIGN KEY (user_id) REFERENCES public.profiles(id) ON DELETE CASCADE,
    CONSTRAINT fk_wishlist_product
        FOREIGN KEY (product_id) REFERENCES public.products(id) ON DELETE CASCADE,
    CONSTRAINT uq_wishlist_item UNIQUE(user_id, product_id)
);

CREATE INDEX IF NOT EXISTS idx_wishlist_user ON public.wishlist_items(user_id);

-- ===========================================
-- 11. REVIEWS (belongs to profile & product, optionally links to order)
-- ===========================================
CREATE TABLE IF NOT EXISTS public.reviews (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID NOT NULL,
    user_id UUID NOT NULL,
    order_id UUID,
    order_item_id UUID,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    title TEXT,
    comment TEXT,
    images TEXT[] DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
    is_verified_purchase BOOLEAN NOT NULL DEFAULT false,
    helpful_count INTEGER NOT NULL DEFAULT 0 CHECK (helpful_count >= 0),
    moderation_note TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_reviews_product
        FOREIGN KEY (product_id) REFERENCES public.products(id) ON DELETE CASCADE,
    CONSTRAINT fk_reviews_user
        FOREIGN KEY (user_id) REFERENCES public.profiles(id) ON DELETE CASCADE,
    CONSTRAINT fk_reviews_order
        FOREIGN KEY (order_id) REFERENCES public.orders(id) ON DELETE SET NULL,
    CONSTRAINT fk_reviews_order_item
        FOREIGN KEY (order_item_id) REFERENCES public.order_items(id) ON DELETE SET NULL,
    CONSTRAINT uq_review_per_product UNIQUE(product_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_reviews_product ON public.reviews(product_id);
CREATE INDEX IF NOT EXISTS idx_reviews_user ON public.reviews(user_id);
CREATE INDEX IF NOT EXISTS idx_reviews_status ON public.reviews(status);
CREATE INDEX IF NOT EXISTS idx_reviews_rating ON public.reviews(product_id, rating) WHERE status = 'approved';

-- ===========================================
-- 12. COUPON USAGES (tracks coupon usage per user)
-- ===========================================
CREATE TABLE IF NOT EXISTS public.coupon_usages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    coupon_id UUID NOT NULL,
    user_id UUID NOT NULL,
    order_id UUID NOT NULL,
    discount_applied DECIMAL(12, 2) NOT NULL,
    used_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_coupon_usage_coupon
        FOREIGN KEY (coupon_id) REFERENCES public.coupons(id) ON DELETE CASCADE,
    CONSTRAINT fk_coupon_usage_user
        FOREIGN KEY (user_id) REFERENCES public.profiles(id) ON DELETE CASCADE,
    CONSTRAINT fk_coupon_usage_order
        FOREIGN KEY (order_id) REFERENCES public.orders(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_coupon_usage_coupon ON public.coupon_usages(coupon_id);
CREATE INDEX IF NOT EXISTS idx_coupon_usage_user ON public.coupon_usages(user_id);
CREATE INDEX IF NOT EXISTS idx_coupon_usage_user_coupon ON public.coupon_usages(user_id, coupon_id);

-- ===========================================
-- 13. AUDIT LOGS (security tracking)
-- ===========================================
CREATE TABLE IF NOT EXISTS public.audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID,
    action TEXT NOT NULL,
    table_name TEXT NOT NULL,
    record_id UUID,
    old_data JSONB,
    new_data JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_audit_user
        FOREIGN KEY (user_id) REFERENCES public.profiles(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_audit_user ON public.audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_action ON public.audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_table ON public.audit_logs(table_name);
CREATE INDEX IF NOT EXISTS idx_audit_created ON public.audit_logs(created_at DESC);

-- ===========================================
-- ROW LEVEL SECURITY POLICIES
-- ===========================================

-- Profiles RLS
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "profiles_select_own" ON public.profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "profiles_update_own" ON public.profiles
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "profiles_admin_all" ON public.profiles
    FOR ALL USING (
        EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin')
    );

-- Addresses RLS
ALTER TABLE public.addresses ENABLE ROW LEVEL SECURITY;

CREATE POLICY "addresses_own" ON public.addresses
    FOR ALL USING (auth.uid() = user_id);

-- Categories RLS (public read)
ALTER TABLE public.categories ENABLE ROW LEVEL SECURITY;

CREATE POLICY "categories_public_read" ON public.categories
    FOR SELECT USING (is_active = true);

CREATE POLICY "categories_admin_all" ON public.categories
    FOR ALL USING (
        EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin')
    );

-- Products RLS (public read active)
ALTER TABLE public.products ENABLE ROW LEVEL SECURITY;

CREATE POLICY "products_public_read" ON public.products
    FOR SELECT USING (status = 'active');

CREATE POLICY "products_admin_all" ON public.products
    FOR ALL USING (
        EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin')
    );

-- Product Variants RLS
ALTER TABLE public.product_variants ENABLE ROW LEVEL SECURITY;

CREATE POLICY "variants_public_read" ON public.product_variants
    FOR SELECT USING (
        EXISTS (SELECT 1 FROM public.products WHERE id = product_id AND status = 'active')
    );

CREATE POLICY "variants_admin_all" ON public.product_variants
    FOR ALL USING (
        EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin')
    );

-- Coupons RLS
ALTER TABLE public.coupons ENABLE ROW LEVEL SECURITY;

CREATE POLICY "coupons_auth_read" ON public.coupons
    FOR SELECT USING (auth.uid() IS NOT NULL AND is_active = true);

CREATE POLICY "coupons_admin_all" ON public.coupons
    FOR ALL USING (
        EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin')
    );

-- Orders RLS
ALTER TABLE public.orders ENABLE ROW LEVEL SECURITY;

CREATE POLICY "orders_select_own" ON public.orders
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "orders_insert_own" ON public.orders
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "orders_admin_all" ON public.orders
    FOR ALL USING (
        EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin')
    );

-- Order Items RLS
ALTER TABLE public.order_items ENABLE ROW LEVEL SECURITY;

CREATE POLICY "order_items_via_order" ON public.order_items
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.orders
            WHERE id = order_id AND (user_id = auth.uid() OR
                EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin'))
        )
    );

CREATE POLICY "order_items_insert_via_order" ON public.order_items
    FOR INSERT WITH CHECK (
        EXISTS (SELECT 1 FROM public.orders WHERE id = order_id AND user_id = auth.uid())
    );

-- Cart Items RLS
ALTER TABLE public.cart_items ENABLE ROW LEVEL SECURITY;

CREATE POLICY "cart_own" ON public.cart_items
    FOR ALL USING (auth.uid() = user_id);

-- Wishlist Items RLS
ALTER TABLE public.wishlist_items ENABLE ROW LEVEL SECURITY;

CREATE POLICY "wishlist_own" ON public.wishlist_items
    FOR ALL USING (auth.uid() = user_id);

-- Reviews RLS
ALTER TABLE public.reviews ENABLE ROW LEVEL SECURITY;

CREATE POLICY "reviews_public_approved" ON public.reviews
    FOR SELECT USING (status = 'approved');

CREATE POLICY "reviews_own" ON public.reviews
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "reviews_insert_own" ON public.reviews
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "reviews_update_own_pending" ON public.reviews
    FOR UPDATE USING (auth.uid() = user_id AND status = 'pending');

CREATE POLICY "reviews_admin_all" ON public.reviews
    FOR ALL USING (
        EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin')
    );

-- Coupon Usages RLS
ALTER TABLE public.coupon_usages ENABLE ROW LEVEL SECURITY;

CREATE POLICY "coupon_usages_own" ON public.coupon_usages
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "coupon_usages_admin_all" ON public.coupon_usages
    FOR ALL USING (
        EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin')
    );

-- Audit Logs RLS (admin only)
ALTER TABLE public.audit_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "audit_admin_read" ON public.audit_logs
    FOR SELECT USING (
        EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin')
    );

-- ===========================================
-- FUNCTIONS & TRIGGERS
-- ===========================================

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION public.update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply updated_at trigger to tables
DO $$
DECLARE
    tbl TEXT;
BEGIN
    FOR tbl IN
        SELECT unnest(ARRAY['profiles', 'addresses', 'categories', 'products',
                           'product_variants', 'cart_items', 'orders', 'reviews', 'coupons'])
    LOOP
        EXECUTE format('
            DROP TRIGGER IF EXISTS trg_%I_updated_at ON public.%I;
            CREATE TRIGGER trg_%I_updated_at
                BEFORE UPDATE ON public.%I
                FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();
        ', tbl, tbl, tbl, tbl);
    END LOOP;
END $$;

-- Create profile on user signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, email, full_name, avatar_url)
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'full_name', split_part(NEW.email, '@', 1)),
        NEW.raw_user_meta_data->>'avatar_url'
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Generate sequential order number
CREATE OR REPLACE FUNCTION public.generate_order_number()
RETURNS TEXT AS $$
DECLARE
    yr TEXT;
    seq INTEGER;
BEGIN
    yr := TO_CHAR(NOW(), 'YYYY');
    SELECT COALESCE(MAX(CAST(SUBSTRING(order_number FROM 10) AS INTEGER)), 0) + 1
    INTO seq FROM public.orders WHERE order_number LIKE 'ALM-' || yr || '-%';
    RETURN 'ALM-' || yr || '-' || LPAD(seq::TEXT, 6, '0');
END;
$$ LANGUAGE plpgsql;

-- Auto-set order number before insert
CREATE OR REPLACE FUNCTION public.set_order_number()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.order_number IS NULL OR NEW.order_number = '' THEN
        NEW.order_number := public.generate_order_number();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_orders_number ON public.orders;
CREATE TRIGGER trg_orders_number
    BEFORE INSERT ON public.orders
    FOR EACH ROW EXECUTE FUNCTION public.set_order_number();

-- Update product rating when review changes
CREATE OR REPLACE FUNCTION public.update_product_rating()
RETURNS TRIGGER AS $$
DECLARE
    pid UUID;
BEGIN
    pid := COALESCE(NEW.product_id, OLD.product_id);

    UPDATE public.products SET
        rating = COALESCE((
            SELECT ROUND(AVG(rating)::NUMERIC, 2)
            FROM public.reviews
            WHERE product_id = pid AND status = 'approved'
        ), 0),
        review_count = (
            SELECT COUNT(*)
            FROM public.reviews
            WHERE product_id = pid AND status = 'approved'
        )
    WHERE id = pid;

    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_reviews_rating ON public.reviews;
CREATE TRIGGER trg_reviews_rating
    AFTER INSERT OR UPDATE OR DELETE ON public.reviews
    FOR EACH ROW EXECUTE FUNCTION public.update_product_rating();

-- Update coupon used_count
CREATE OR REPLACE FUNCTION public.update_coupon_usage()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE public.coupons SET used_count = used_count + 1 WHERE id = NEW.coupon_id;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE public.coupons SET used_count = GREATEST(used_count - 1, 0) WHERE id = OLD.coupon_id;
    END IF;
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_coupon_usage ON public.coupon_usages;
CREATE TRIGGER trg_coupon_usage
    AFTER INSERT OR DELETE ON public.coupon_usages
    FOR EACH ROW EXECUTE FUNCTION public.update_coupon_usage();

-- Ensure only one default address per user
CREATE OR REPLACE FUNCTION public.ensure_single_default_address()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.is_default = true THEN
        UPDATE public.addresses
        SET is_default = false
        WHERE user_id = NEW.user_id
          AND id != NEW.id
          AND address_type = NEW.address_type;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_addresses_default ON public.addresses;
CREATE TRIGGER trg_addresses_default
    BEFORE INSERT OR UPDATE ON public.addresses
    FOR EACH ROW EXECUTE FUNCTION public.ensure_single_default_address();

-- Verify purchase for reviews
CREATE OR REPLACE FUNCTION public.verify_review_purchase()
RETURNS TRIGGER AS $$
BEGIN
    NEW.is_verified_purchase := EXISTS (
        SELECT 1 FROM public.order_items oi
        JOIN public.orders o ON o.id = oi.order_id
        WHERE oi.product_id = NEW.product_id
          AND o.user_id = NEW.user_id
          AND o.status = 'delivered'
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_reviews_verify ON public.reviews;
CREATE TRIGGER trg_reviews_verify
    BEFORE INSERT ON public.reviews
    FOR EACH ROW EXECUTE FUNCTION public.verify_review_purchase();

-- ===========================================
-- SEED DATA
-- ===========================================

INSERT INTO public.categories (name, slug, description, display_order, is_active) VALUES
    ('Necklaces', 'necklaces', 'Elegant necklaces for every occasion', 1, true),
    ('Earrings', 'earrings', 'Statement earrings to complete your look', 2, true),
    ('Rings', 'rings', 'Beautiful rings for everyday and special occasions', 3, true),
    ('Bangles', 'bangles', 'Traditional and modern bangles', 4, true),
    ('Bracelets', 'bracelets', 'Stylish bracelets for any outfit', 5, true),
    ('Pendants', 'pendants', 'Exquisite pendants and chains', 6, true),
    ('Ethnic Wear', 'ethnic-wear', 'Traditional Indian ethnic wear', 7, true),
    ('Western Wear', 'western-wear', 'Contemporary western fashion', 8, true),
    ('Sarees', 'sarees', 'Beautiful sarees for all occasions', 9, true),
    ('Accessories', 'accessories', 'Fashion accessories and more', 10, true)
ON CONFLICT (slug) DO NOTHING;

-- ===========================================
-- SCHEMA VERIFICATION
-- ===========================================

DO $$
DECLARE
    fk_count INTEGER;
    tbl_count INTEGER;
BEGIN
    -- Count foreign keys
    SELECT COUNT(*) INTO fk_count
    FROM information_schema.table_constraints
    WHERE constraint_type = 'FOREIGN KEY'
    AND table_schema = 'public';

    -- Count tables
    SELECT COUNT(*) INTO tbl_count
    FROM information_schema.tables
    WHERE table_schema = 'public'
    AND table_type = 'BASE TABLE';

    RAISE NOTICE '✓ Migration completed successfully!';
    RAISE NOTICE '✓ Created % tables with % foreign key relationships', tbl_count, fk_count;
END $$;
