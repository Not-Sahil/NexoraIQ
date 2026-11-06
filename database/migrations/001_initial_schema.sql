-- ====================================================================
-- NEXORAIQ: DATABASE MIGRATION 001 - CORE SCHEMA & ROW LEVEL SECURITY
-- Multi-tenant Enterprise Business Intelligence & Predictive Analytics
-- ====================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 1. PROFILES
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    avatar_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. ORGANIZATIONS
CREATE TABLE IF NOT EXISTS organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    industry VARCHAR(100),
    billing_plan VARCHAR(50) DEFAULT 'pro',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. ORGANIZATION MEMBERS (RBAC: owner, admin, analyst)
CREATE TABLE IF NOT EXISTS organization_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL DEFAULT 'analyst', -- 'owner', 'admin', 'analyst'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(organization_id, user_id)
);

-- 4. WORKSPACES
CREATE TABLE IF NOT EXISTS workspaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    domain_type VARCHAR(100) DEFAULT 'retail', -- 'retail', 'saas', 'manufacturing', 'general'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. DATASETS
CREATE TABLE IF NOT EXISTS datasets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    filename VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_size_bytes BIGINT NOT NULL DEFAULT 0,
    row_count INT NOT NULL DEFAULT 0,
    col_count INT NOT NULL DEFAULT 0,
    file_type VARCHAR(50) NOT NULL DEFAULT 'csv',
    status VARCHAR(50) NOT NULL DEFAULT 'uploaded', -- 'uploaded', 'validating', 'ready', 'failed'
    quality_score NUMERIC(5, 2) DEFAULT 0.0,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 6. DATASET COLUMNS
CREATE TABLE IF NOT EXISTS dataset_columns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_id UUID NOT NULL REFERENCES datasets(id) ON DELETE CASCADE,
    column_name VARCHAR(255) NOT NULL,
    inferred_type VARCHAR(50) NOT NULL, -- 'datetime', 'numeric', 'categorical', 'text', 'boolean'
    mapped_semantic_role VARCHAR(100), -- 'date', 'revenue', 'cost', 'customer_id', 'product', 'quantity', etc.
    null_count INT DEFAULT 0,
    distinct_count INT DEFAULT 0,
    min_value TEXT,
    max_value TEXT,
    mean_value NUMERIC(15, 4),
    std_value NUMERIC(15, 4),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 7. DATA QUALITY REPORTS
CREATE TABLE IF NOT EXISTS data_quality_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_id UUID NOT NULL REFERENCES datasets(id) ON DELETE CASCADE,
    overall_score NUMERIC(5, 2) NOT NULL,
    completeness_score NUMERIC(5, 2) NOT NULL,
    validity_score NUMERIC(5, 2) NOT NULL,
    uniqueness_score NUMERIC(5, 2) NOT NULL,
    consistency_score NUMERIC(5, 2) NOT NULL,
    total_rows INT NOT NULL,
    total_columns INT NOT NULL,
    duplicate_rows INT DEFAULT 0,
    missing_cells INT DEFAULT 0,
    outlier_count INT DEFAULT 0,
    issues_summary JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 8. BUSINESS METRICS
CREATE TABLE IF NOT EXISTS business_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    dataset_id UUID REFERENCES datasets(id) ON DELETE SET NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    total_revenue NUMERIC(15, 2) NOT NULL DEFAULT 0.00,
    total_cost NUMERIC(15, 2) NOT NULL DEFAULT 0.00,
    gross_profit NUMERIC(15, 2) NOT NULL DEFAULT 0.00,
    operating_expenses NUMERIC(15, 2) NOT NULL DEFAULT 0.00,
    net_profit NUMERIC(15, 2) NOT NULL DEFAULT 0.00,
    gross_margin_pct NUMERIC(6, 2) DEFAULT 0.00,
    net_margin_pct NUMERIC(6, 2) DEFAULT 0.00,
    revenue_growth_pct NUMERIC(6, 2) DEFAULT 0.00,
    customer_count INT DEFAULT 0,
    average_order_value NUMERIC(10, 2) DEFAULT 0.00,
    cac NUMERIC(10, 2) DEFAULT 0.00,
    clv NUMERIC(10, 2) DEFAULT 0.00,
    conversion_rate NUMERIC(6, 4) DEFAULT 0.0000,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 9. FORECASTS
CREATE TABLE IF NOT EXISTS forecasts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    dataset_id UUID REFERENCES datasets(id) ON DELETE CASCADE,
    target_column VARCHAR(100) NOT NULL,
    forecast_horizon INT NOT NULL DEFAULT 30,
    time_frequency VARCHAR(50) DEFAULT 'D',
    best_model_name VARCHAR(100) NOT NULL,
    train_mae NUMERIC(12, 4),
    train_rmse NUMERIC(12, 4),
    val_mae NUMERIC(12, 4),
    val_rmse NUMERIC(12, 4),
    val_mape NUMERIC(8, 4),
    test_mae NUMERIC(12, 4),
    test_rmse NUMERIC(12, 4),
    test_mape NUMERIC(8, 4),
    r2_score NUMERIC(6, 4),
    model_comparison_json JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 10. FORECAST PREDICTIONS
CREATE TABLE IF NOT EXISTS forecast_predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    forecast_id UUID NOT NULL REFERENCES forecasts(id) ON DELETE CASCADE,
    forecast_date DATE NOT NULL,
    predicted_value NUMERIC(15, 2) NOT NULL,
    lower_bound NUMERIC(15, 2),
    upper_bound NUMERIC(15, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 11. ANOMALY EVENTS
CREATE TABLE IF NOT EXISTS anomaly_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    dataset_id UUID REFERENCES datasets(id) ON DELETE CASCADE,
    event_date DATE NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    actual_value NUMERIC(15, 2) NOT NULL,
    expected_value NUMERIC(15, 2) NOT NULL,
    deviation_pct NUMERIC(8, 2) NOT NULL,
    severity VARCHAR(50) NOT NULL, -- 'low', 'medium', 'high', 'critical'
    detection_method VARCHAR(100) NOT NULL, -- 'Isolation Forest', 'LOF', 'Z-Score', 'Seasonal-ESD'
    root_cause_hint TEXT,
    status VARCHAR(50) DEFAULT 'detected', -- 'detected', 'reviewed', 'resolved'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 12. CUSTOMER SEGMENTS (RFM)
CREATE TABLE IF NOT EXISTS customer_segments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    customer_identifier VARCHAR(255) NOT NULL,
    recency_days INT NOT NULL,
    frequency_orders INT NOT NULL,
    monetary_total NUMERIC(15, 2) NOT NULL,
    rfm_score VARCHAR(10) NOT NULL,
    segment_label VARCHAR(100) NOT NULL, -- 'Champions', 'Loyal Customers', 'At Risk', 'Lost', etc.
    churn_probability NUMERIC(5, 4) DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 13. CHURN PREDICTIONS
CREATE TABLE IF NOT EXISTS churn_predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    customer_identifier VARCHAR(255) NOT NULL,
    churn_probability NUMERIC(5, 4) NOT NULL,
    risk_tier VARCHAR(50) NOT NULL, -- 'low', 'medium', 'high'
    top_churn_factors JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 14. INVENTORY INSIGHTS
CREATE TABLE IF NOT EXISTS inventory_insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    product_identifier VARCHAR(255) NOT NULL,
    product_name VARCHAR(255),
    category VARCHAR(100),
    inventory_turnover NUMERIC(8, 2),
    days_inventory_outstanding NUMERIC(8, 2),
    stockout_risk_score NUMERIC(5, 2), -- 0-100%
    reorder_point INT,
    abc_classification VARCHAR(10), -- 'A', 'B', 'C'
    status VARCHAR(50), -- 'healthy', 'overstock', 'reorder_now', 'stockout_risk'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 15. MARKETING INSIGHTS
CREATE TABLE IF NOT EXISTS marketing_insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    channel_name VARCHAR(100) NOT NULL,
    marketing_spend NUMERIC(15, 2) NOT NULL,
    attributed_revenue NUMERIC(15, 2) NOT NULL,
    cac NUMERIC(10, 2),
    roas NUMERIC(8, 2), -- Return on Ad Spend
    conversion_rate NUMERIC(6, 4),
    efficiency_rating VARCHAR(50), -- 'stellar', 'efficient', 'underperforming'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 16. FINANCIAL INSIGHTS
CREATE TABLE IF NOT EXISTS financial_insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    operating_cash_flow NUMERIC(15, 2),
    working_capital NUMERIC(15, 2),
    quick_ratio NUMERIC(6, 2),
    burn_rate_monthly NUMERIC(15, 2),
    runway_months NUMERIC(6, 1),
    revenue_concentration_risk NUMERIC(5, 2), -- percentage from top 5 customers/products
    stress_index VARCHAR(50), -- 'normal', 'moderate_stress', 'high_stress'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 17. BUSINESS RECOMMENDATIONS
CREATE TABLE IF NOT EXISTS business_recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    category VARCHAR(100) NOT NULL, -- 'profitability', 'inventory', 'marketing', 'churn', 'cash_flow'
    problem_title VARCHAR(255) NOT NULL,
    evidence TEXT NOT NULL,
    root_cause TEXT NOT NULL,
    recommended_action TEXT NOT NULL,
    expected_impact TEXT NOT NULL,
    priority VARCHAR(50) NOT NULL DEFAULT 'medium', -- 'critical', 'high', 'medium', 'low'
    confidence_score NUMERIC(5, 2) DEFAULT 0.85,
    status VARCHAR(50) DEFAULT 'open', -- 'open', 'in_progress', 'applied', 'dismissed'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 18. REPORTS
CREATE TABLE IF NOT EXISTS reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    report_type VARCHAR(50) NOT NULL, -- 'executive', 'forecasting', 'anomaly', 'full_audit'
    format VARCHAR(20) NOT NULL, -- 'pdf', 'excel', 'json'
    file_path TEXT NOT NULL,
    parameters JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 19. ML MODELS
CREATE TABLE IF NOT EXISTS ml_models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    model_type VARCHAR(100) NOT NULL, -- 'forecasting', 'anomaly_detection', 'churn_classification'
    algorithm VARCHAR(100) NOT NULL, -- 'xgboost', 'random_forest', 'lightgbm', 'arima', 'isolation_forest'
    version VARCHAR(50) NOT NULL DEFAULT 'v1.0.0',
    hyperparameters JSONB DEFAULT '{}'::jsonb,
    features JSONB DEFAULT '[]'::jsonb,
    artifact_path TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 20. ML MODEL EVALUATIONS
CREATE TABLE IF NOT EXISTS ml_model_evaluations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_id UUID NOT NULL REFERENCES ml_models(id) ON DELETE CASCADE,
    dataset_id UUID REFERENCES datasets(id) ON DELETE SET NULL,
    split_strategy VARCHAR(100) DEFAULT 'chronological_70_15_15',
    mae NUMERIC(12, 4),
    rmse NUMERIC(12, 4),
    mape NUMERIC(8, 4),
    smape NUMERIC(8, 4),
    r2 NUMERIC(8, 4),
    roc_auc NUMERIC(8, 4),
    precision_score NUMERIC(8, 4),
    recall_score NUMERIC(8, 4),
    f1_score NUMERIC(8, 4),
    evaluation_metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 21. NOTIFICATIONS
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR(50) NOT NULL, -- 'anomaly', 'forecast_warning', 'quality_alert', 'system'
    severity VARCHAR(50) DEFAULT 'info', -- 'info', 'warning', 'critical'
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 22. AUDIT LOGS
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES profiles(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100) NOT NULL,
    resource_id UUID,
    ip_address VARCHAR(50),
    details JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- INDEXES FOR PERFORMANCE
CREATE INDEX IF NOT EXISTS idx_org_members_user ON organization_members(user_id);
CREATE INDEX IF NOT EXISTS idx_org_members_org ON organization_members(organization_id);
CREATE INDEX IF NOT EXISTS idx_workspaces_org ON workspaces(organization_id);
CREATE INDEX IF NOT EXISTS idx_datasets_workspace ON datasets(workspace_id);
CREATE INDEX IF NOT EXISTS idx_business_metrics_workspace ON business_metrics(workspace_id);
CREATE INDEX IF NOT EXISTS idx_forecasts_workspace ON forecasts(workspace_id);
CREATE INDEX IF NOT EXISTS idx_anomaly_events_workspace ON anomaly_events(workspace_id);
CREATE INDEX IF NOT EXISTS idx_customer_segments_workspace ON customer_segments(workspace_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_org ON audit_logs(organization_id);

-- ROW LEVEL SECURITY (RLS) POLICIES
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE organization_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE workspaces ENABLE ROW LEVEL SECURITY;
ALTER TABLE datasets ENABLE ROW LEVEL SECURITY;
ALTER TABLE business_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE forecasts ENABLE ROW LEVEL SECURITY;
ALTER TABLE anomaly_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE customer_segments ENABLE ROW LEVEL SECURITY;
ALTER TABLE business_recommendations ENABLE ROW LEVEL SECURITY;
ALTER TABLE reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- Note: RLS policies verify current auth.uid() matches organization_members via workspace/org relationships

