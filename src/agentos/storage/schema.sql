-- =========================================================
-- AgentOS: Enterprise Finance + Support Schema
-- PostgreSQL 16
-- =========================================================

-- =========================
-- 1. ORGANIZATIONS
-- =========================

CREATE TABLE organizations (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL UNIQUE,
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- =========================
-- 2. VENDORS
-- =========================

CREATE TABLE vendors (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES organizations(tenant_id),
    vendor_code TEXT NOT NULL,
    name TEXT NOT NULL,
    tax_id TEXT,
    status TEXT NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'inactive', 'blocked')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (tenant_id, vendor_code),
    UNIQUE (tenant_id, id)
);


-- =========================
-- 3. PURCHASE ORDERS
-- =========================

CREATE TABLE purchase_orders (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES organizations(tenant_id),
    vendor_id UUID NOT NULL,
    po_number TEXT NOT NULL,
    total_amount NUMERIC(12, 2) NOT NULL
        CHECK (total_amount >= 0),
    currency TEXT NOT NULL DEFAULT 'INR',
    status TEXT NOT NULL
        CHECK (status IN ('draft', 'approved', 'completed', 'cancelled')),
    ordered_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (tenant_id, po_number),
    UNIQUE (tenant_id, id),

    FOREIGN KEY (tenant_id, vendor_id)
        REFERENCES vendors (tenant_id, id)
);


-- =========================
-- 4. INVOICES
-- =========================

CREATE TABLE invoices (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES organizations(tenant_id),
    vendor_id UUID NOT NULL,
    purchase_order_id UUID,
    invoice_number TEXT NOT NULL,
    total_amount NUMERIC(12, 2) NOT NULL
        CHECK (total_amount >= 0),
    currency TEXT NOT NULL DEFAULT 'INR',
    status TEXT NOT NULL
        CHECK (status IN ('pending', 'approved', 'rejected', 'paid')),
    invoice_date DATE NOT NULL,
    due_date DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (tenant_id, invoice_number),
    UNIQUE (tenant_id, id),
    UNIQUE (tenant_id, id, vendor_id),

    FOREIGN KEY (tenant_id, vendor_id)
        REFERENCES vendors (tenant_id, id),

    FOREIGN KEY (tenant_id, purchase_order_id)
        REFERENCES purchase_orders (tenant_id, id),

    CHECK (due_date IS NULL OR due_date >= invoice_date)
);


-- =========================
-- 5. PAYMENT LEDGER
-- =========================

CREATE TABLE payment_ledger (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES organizations(tenant_id),
    invoice_id UUID NOT NULL,
    transaction_reference TEXT NOT NULL,
    amount NUMERIC(12, 2) NOT NULL
        CHECK (amount > 0),
    currency TEXT NOT NULL DEFAULT 'INR',
    status TEXT NOT NULL
        CHECK (status IN ('initiated', 'completed', 'failed', 'reversed')),
    payment_date TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (tenant_id, transaction_reference),

    FOREIGN KEY (tenant_id, invoice_id)
        REFERENCES invoices (tenant_id, id)
);


-- =========================
-- 6. RISK SIGNALS
-- =========================

CREATE TABLE risk_signals (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES organizations(tenant_id),
    vendor_id UUID NOT NULL,
    invoice_id UUID,
    signal_type TEXT NOT NULL,
    severity TEXT NOT NULL
        CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    description TEXT NOT NULL,
    is_resolved BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    FOREIGN KEY (tenant_id, vendor_id)
        REFERENCES vendors (tenant_id, id),

    FOREIGN KEY (tenant_id, invoice_id, vendor_id)
        REFERENCES invoices (tenant_id, id, vendor_id)
);


-- =========================
-- 7. APPROVAL RECORDS
-- =========================

CREATE TABLE approval_records (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES organizations(tenant_id),
    invoice_id UUID NOT NULL,
    decision TEXT NOT NULL
        CHECK (decision IN ('pending', 'approved', 'rejected')),
    approver_reference TEXT,
    comments TEXT,
    decided_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    FOREIGN KEY (tenant_id, invoice_id)
        REFERENCES invoices (tenant_id, id),

    CHECK (
        (decision = 'pending' AND decided_at IS NULL)
        OR
        (decision IN ('approved', 'rejected') AND decided_at IS NOT NULL)
    )
);


-- =========================
-- 8. CUSTOMERS
-- =========================

CREATE TABLE customers (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES organizations(tenant_id),
    customer_code TEXT NOT NULL,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'inactive', 'blocked')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (tenant_id, customer_code),
    UNIQUE (tenant_id, id)
);


-- =========================
-- 9. CUSTOMER ORDERS
-- =========================

CREATE TABLE customer_orders (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES organizations(tenant_id),
    customer_id UUID NOT NULL,
    order_number TEXT NOT NULL,
    total_amount NUMERIC(12, 2) NOT NULL
        CHECK (total_amount >= 0),
    currency TEXT NOT NULL DEFAULT 'INR',
    status TEXT NOT NULL
        CHECK (
            status IN (
                'placed', 'processing', 'shipped',
                'delivered', 'cancelled', 'refunded'
            )
        ),
    ordered_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (tenant_id, order_number),
    UNIQUE (tenant_id, id, customer_id),

    FOREIGN KEY (tenant_id, customer_id)
        REFERENCES customers (tenant_id, id)
);


-- =========================
-- 10. CUSTOMER PAYMENTS
-- =========================

CREATE TABLE customer_payments (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES organizations(tenant_id),
    customer_id UUID NOT NULL,
    order_id UUID NOT NULL,
    transaction_reference TEXT NOT NULL,
    amount NUMERIC(12, 2) NOT NULL
        CHECK (amount > 0),
    currency TEXT NOT NULL DEFAULT 'INR',
    status TEXT NOT NULL
        CHECK (status IN ('pending', 'completed', 'failed', 'refunded')),
    payment_method TEXT NOT NULL,
    paid_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (tenant_id, transaction_reference),

    FOREIGN KEY (tenant_id, customer_id)
        REFERENCES customers (tenant_id, id),

    FOREIGN KEY (tenant_id, order_id, customer_id)
        REFERENCES customer_orders (tenant_id, id, customer_id)
);


-- =========================
-- 11. SUPPORT TICKETS
-- =========================

CREATE TABLE support_tickets (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES organizations(tenant_id),
    customer_id UUID NOT NULL,
    ticket_number TEXT NOT NULL,
    subject TEXT NOT NULL,
    description TEXT NOT NULL,
    category TEXT NOT NULL,
    priority TEXT NOT NULL
        CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    status TEXT NOT NULL
        CHECK (status IN ('open', 'in_progress', 'resolved', 'closed')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (tenant_id, ticket_number),
    UNIQUE (tenant_id, id),

    FOREIGN KEY (tenant_id, customer_id)
        REFERENCES customers (tenant_id, id)
);


-- =========================
-- 12. SUPPORT POLICIES
-- =========================

CREATE TABLE support_policies (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES organizations(tenant_id),
    policy_code TEXT NOT NULL,
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    content TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (tenant_id, policy_code),
    UNIQUE (tenant_id, id)
);


-- =========================
-- 13. ESCALATIONS
-- =========================

CREATE TABLE escalations (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES organizations(tenant_id),
    ticket_id UUID NOT NULL,
    escalation_level INTEGER NOT NULL
        CHECK (escalation_level BETWEEN 1 AND 5),
    reason TEXT NOT NULL,
    assigned_team TEXT NOT NULL,
    status TEXT NOT NULL
        CHECK (status IN ('pending', 'accepted', 'resolved')),
    escalated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at TIMESTAMPTZ,

    FOREIGN KEY (tenant_id, ticket_id)
        REFERENCES support_tickets (tenant_id, id),

    CHECK (resolved_at IS NULL OR resolved_at >= escalated_at)
);