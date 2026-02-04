-- =====================================================
-- ALMIRA - Customer Support & Contact Tables
-- =====================================================
-- Execute this in Supabase SQL Editor

-- ===========================================
-- 1. CONTACT SUBMISSIONS (Public contact form)
-- ===========================================
CREATE TABLE IF NOT EXISTS public.contact_submissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    subject TEXT NOT NULL,
    message TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'new'
        CHECK (status IN ('new', 'in_progress', 'resolved', 'closed')),
    assigned_to UUID,
    admin_notes TEXT,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at TIMESTAMPTZ,

    CONSTRAINT fk_contact_assigned
        FOREIGN KEY (assigned_to) REFERENCES public.profiles(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_contact_email ON public.contact_submissions(email);
CREATE INDEX IF NOT EXISTS idx_contact_status ON public.contact_submissions(status);
CREATE INDEX IF NOT EXISTS idx_contact_created ON public.contact_submissions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_contact_assigned ON public.contact_submissions(assigned_to) WHERE assigned_to IS NOT NULL;

-- ===========================================
-- 2. SUPPORT TICKETS (Authenticated users)
-- ===========================================
CREATE TABLE IF NOT EXISTS public.support_tickets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticket_number TEXT NOT NULL UNIQUE,
    user_id UUID NOT NULL,
    order_id UUID,
    subject TEXT NOT NULL,
    description TEXT NOT NULL,
    category TEXT NOT NULL
        CHECK (category IN ('order_issue', 'product_issue', 'shipping', 'refund', 'technical', 'other')),
    priority TEXT NOT NULL DEFAULT 'medium'
        CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    status TEXT NOT NULL DEFAULT 'open'
        CHECK (status IN ('open', 'in_progress', 'waiting_customer', 'resolved', 'closed')),
    assigned_to UUID,
    -- Attachments stored as array of URLs
    attachments TEXT[] DEFAULT '{}',
    admin_notes TEXT,
    resolution_notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at TIMESTAMPTZ,
    closed_at TIMESTAMPTZ,

    CONSTRAINT fk_tickets_user
        FOREIGN KEY (user_id) REFERENCES public.profiles(id) ON DELETE CASCADE,
    CONSTRAINT fk_tickets_order
        FOREIGN KEY (order_id) REFERENCES public.orders(id) ON DELETE SET NULL,
    CONSTRAINT fk_tickets_assigned
        FOREIGN KEY (assigned_to) REFERENCES public.profiles(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_tickets_number ON public.support_tickets(ticket_number);
CREATE INDEX IF NOT EXISTS idx_tickets_user ON public.support_tickets(user_id);
CREATE INDEX IF NOT EXISTS idx_tickets_order ON public.support_tickets(order_id) WHERE order_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_tickets_status ON public.support_tickets(status);
CREATE INDEX IF NOT EXISTS idx_tickets_priority ON public.support_tickets(priority);
CREATE INDEX IF NOT EXISTS idx_tickets_assigned ON public.support_tickets(assigned_to) WHERE assigned_to IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_tickets_created ON public.support_tickets(created_at DESC);

-- ===========================================
-- 3. SUPPORT MESSAGES (Ticket conversation)
-- ===========================================
CREATE TABLE IF NOT EXISTS public.support_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticket_id UUID NOT NULL,
    user_id UUID NOT NULL,
    message TEXT NOT NULL,
    attachments TEXT[] DEFAULT '{}',
    is_internal BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_messages_ticket
        FOREIGN KEY (ticket_id) REFERENCES public.support_tickets(id) ON DELETE CASCADE,
    CONSTRAINT fk_messages_user
        FOREIGN KEY (user_id) REFERENCES public.profiles(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_messages_ticket ON public.support_messages(ticket_id);
CREATE INDEX IF NOT EXISTS idx_messages_created ON public.support_messages(created_at);

-- ===========================================
-- ROW LEVEL SECURITY
-- ===========================================

-- Contact Submissions (Admin only)
ALTER TABLE public.contact_submissions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "contact_admin_all" ON public.contact_submissions
    FOR ALL USING (
        EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin')
    );

-- Support Tickets
ALTER TABLE public.support_tickets ENABLE ROW LEVEL SECURITY;

CREATE POLICY "tickets_select_own" ON public.support_tickets
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "tickets_insert_own" ON public.support_tickets
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "tickets_update_own" ON public.support_tickets
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "tickets_admin_all" ON public.support_tickets
    FOR ALL USING (
        EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin')
    );

-- Support Messages
ALTER TABLE public.support_messages ENABLE ROW LEVEL SECURITY;

CREATE POLICY "messages_via_ticket" ON public.support_messages
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.support_tickets
            WHERE id = ticket_id AND (
                user_id = auth.uid() OR
                EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin')
            )
        )
    );

CREATE POLICY "messages_insert_via_ticket" ON public.support_messages
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.support_tickets
            WHERE id = ticket_id AND (
                user_id = auth.uid() OR
                EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin')
            )
        )
    );

CREATE POLICY "messages_admin_internal" ON public.support_messages
    FOR ALL USING (
        is_internal = false OR
        EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin')
    );

-- ===========================================
-- FUNCTIONS & TRIGGERS
-- ===========================================

-- Apply updated_at trigger
DROP TRIGGER IF EXISTS trg_contact_updated_at ON public.contact_submissions;
CREATE TRIGGER trg_contact_updated_at
    BEFORE UPDATE ON public.contact_submissions
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();

DROP TRIGGER IF EXISTS trg_tickets_updated_at ON public.support_tickets;
CREATE TRIGGER trg_tickets_updated_at
    BEFORE UPDATE ON public.support_tickets
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();

-- Generate sequential ticket number
CREATE OR REPLACE FUNCTION public.generate_ticket_number()
RETURNS TEXT AS $$
DECLARE
    yr TEXT;
    seq INTEGER;
BEGIN
    yr := TO_CHAR(NOW(), 'YYYY');
    SELECT COALESCE(MAX(CAST(SUBSTRING(ticket_number FROM 10) AS INTEGER)), 0) + 1
    INTO seq FROM public.support_tickets WHERE ticket_number LIKE 'TKT-' || yr || '-%';
    RETURN 'TKT-' || yr || '-' || LPAD(seq::TEXT, 6, '0');
END;
$$ LANGUAGE plpgsql;

-- Auto-set ticket number before insert
CREATE OR REPLACE FUNCTION public.set_ticket_number()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.ticket_number IS NULL OR NEW.ticket_number = '' THEN
        NEW.ticket_number := public.generate_ticket_number();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_tickets_number ON public.support_tickets;
CREATE TRIGGER trg_tickets_number
    BEFORE INSERT ON public.support_tickets
    FOR EACH ROW EXECUTE FUNCTION public.set_ticket_number();

-- Update ticket timestamp when new message added
CREATE OR REPLACE FUNCTION public.update_ticket_on_message()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE public.support_tickets
    SET updated_at = NOW()
    WHERE id = NEW.ticket_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_messages_update_ticket ON public.support_messages;
CREATE TRIGGER trg_messages_update_ticket
    AFTER INSERT ON public.support_messages
    FOR EACH ROW EXECUTE FUNCTION public.update_ticket_on_message();

-- ===========================================
-- VERIFICATION
-- ===========================================

DO $$
DECLARE
    tbl_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO tbl_count
    FROM information_schema.tables
    WHERE table_schema = 'public'
    AND table_name IN ('contact_submissions', 'support_tickets', 'support_messages');

    IF tbl_count = 3 THEN
        RAISE NOTICE '✓ Support & contact tables created successfully!';
        RAISE NOTICE '✓ Created: contact_submissions, support_tickets, support_messages';
    ELSE
        RAISE WARNING '⚠ Expected 3 tables, found %', tbl_count;
    END IF;
END $$;
