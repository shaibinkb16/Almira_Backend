-- =====================================================
-- Add Payment Fields to Orders Table
-- =====================================================
-- Execute this in Supabase SQL Editor

-- Add payment fields to orders table
ALTER TABLE public.orders
ADD COLUMN IF NOT EXISTS payment_method TEXT DEFAULT 'cod',
ADD COLUMN IF NOT EXISTS payment_status TEXT DEFAULT 'pending' CHECK (payment_status IN ('pending', 'paid', 'failed', 'refunded')),
ADD COLUMN IF NOT EXISTS razorpay_order_id TEXT,
ADD COLUMN IF NOT EXISTS razorpay_payment_id TEXT,
ADD COLUMN IF NOT EXISTS paid_at TIMESTAMPTZ;

-- Create index on payment status
CREATE INDEX IF NOT EXISTS idx_orders_payment_status ON public.orders(payment_status);
CREATE INDEX IF NOT EXISTS idx_orders_razorpay_order_id ON public.orders(razorpay_order_id);

-- Update existing orders to have payment_method as COD
UPDATE public.orders
SET payment_method = 'cod', payment_status = 'pending'
WHERE payment_method IS NULL;

-- Verification
DO $$
BEGIN
    RAISE NOTICE 'Payment fields added to orders table successfully!';
    RAISE NOTICE 'Fields added: payment_method, payment_status, razorpay_order_id, razorpay_payment_id, paid_at';
END $$;
