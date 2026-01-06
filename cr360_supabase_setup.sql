-- =============================================================================
-- CR360 ACCOUNT-LEVEL DATA - SUPABASE/POSTGRESQL VERSION
-- =============================================================================
-- Description: PostgreSQL schema for account-level credit risk analytics
-- Migration: Transitioned from aggregated star schema to granular account data
--
-- Setup Instructions:
-- 1. Backup existing data if needed
-- 2. Go to Supabase SQL Editor
-- 3. Paste and run this entire script
-- 4. Run data loading script to populate from Excel
--
-- Data Source: CR360__Synthetic Data.xlsx
-- =============================================================================

-- =============================================================================
-- DROP EXISTING TABLES (Complete Replacement)
-- =============================================================================
DROP TABLE IF EXISTS agg_monthly_summary CASCADE;
DROP TABLE IF EXISTS dim_date CASCADE;
DROP TABLE IF EXISTS dim_product CASCADE;
DROP TABLE IF EXISTS dim_region CASCADE;
DROP TABLE IF EXISTS dim_segment CASCADE;
DROP TABLE IF EXISTS dim_vintage CASCADE;

-- =============================================================================
-- MAIN ACCOUNTS TABLE (Account-Level Granular Data)
-- =============================================================================

CREATE TABLE accounts (
    -- =========================================================================
    -- IDENTIFIERS
    -- =========================================================================
    account_id VARCHAR(50) NOT NULL,
    customer_id VARCHAR(50) NOT NULL,
    customer_name VARCHAR(100),

    -- =========================================================================
    -- CLASSIFICATIONS (Denormalized - No FK to dimension tables)
    -- =========================================================================
    product_code VARCHAR(10) NOT NULL,          -- MTG, AUTO, CC, PL, HELOC
    region_code VARCHAR(20) NOT NULL,           -- Northeast, Southeast, Midwest, West, Central
    customer_segment VARCHAR(20),                -- PRIME, NEAR_PRIME, SUBPRIME
    application_channel VARCHAR(30),             -- BRANCH, ONLINE, MOBILE, BROKER, DEALER, DIRECT_MAIL

    -- =========================================================================
    -- TEMPORAL ATTRIBUTES
    -- =========================================================================
    as_of_date DATE NOT NULL,                    -- Quarterly snapshot date
    origination_date DATE,                       -- Date loan was originated
    funded_date DATE,                            -- Date funds were disbursed
    vintage_year INTEGER,                        -- Year of origination (for cohort analysis)
    age_on_book_months INTEGER,                  -- Months since origination
    last_payment_date DATE,                      -- Most recent payment date

    -- =========================================================================
    -- FINANCIAL BALANCES (All in USD)
    -- =========================================================================
    adjusted_eop_balance DECIMAL(18,2),          -- End-of-period outstanding balance
    current_credit_limit DECIMAL(18,2),          -- Maximum credit available
    funded_amount DECIMAL(18,2),                 -- Original disbursement amount
    exposure_at_default DECIMAL(18,2),           -- Estimated exposure if default occurs (EAD)
    current_property_value DECIMAL(18,2),        -- Current collateral value (NULL for unsecured)
    annual_income DECIMAL(18,2),                 -- Borrower annual gross income
    last_payment_amount DECIMAL(18,2),           -- Amount of most recent payment

    -- =========================================================================
    -- DELINQUENCY & ACCOUNT STATUS
    -- =========================================================================
    days_past_due INTEGER DEFAULT 0,             -- Number of days payment is overdue
    account_status VARCHAR(20),                  -- ACTIVE, CLOSED, PAID_OFF, CHARGED_OFF
    impaired_flag VARCHAR(1),                    -- Y/N - Credit-impaired under IFRS 9
    ecl_stage INTEGER,                           -- 1=Performing, 2=Underperforming, 3=Non-performing
    ever_30_dpd_flag VARCHAR(1),                 -- Y/N - Has ever been 30+ days past due (never resets)
    max_dpd_12m INTEGER,                         -- Maximum days past due in trailing 12 months

    -- =========================================================================
    -- CREDIT SCORES & RISK METRICS
    -- =========================================================================
    current_credit_score DECIMAL(10,2),          -- Current credit bureau score (FICO-like)
    origination_credit_score DECIMAL(10,2),      -- Credit score at loan origination (static)
    twelve_month_pd DECIMAL(10,6),               -- Probability of default within next 12 months (0-1)
    loss_given_default DECIMAL(10,4),            -- Expected loss percentage if default occurs (0-1)
    expected_credit_loss DECIMAL(18,2),          -- 12-month ECL provision (IFRS 9)

    -- =========================================================================
    -- LOAN CHARACTERISTICS
    -- =========================================================================
    current_ltv DECIMAL(10,4),                   -- Current Loan-to-Value ratio (0-1.5+)
    origination_ltv DECIMAL(10,4),               -- LTV at origination (0-1)
    debt_to_income DECIMAL(10,4),                -- DTI ratio (0-1+)
    utilization_rate DECIMAL(10,4),              -- Credit utilization for revolving accounts (0-1+)
    current_interest_rate DECIMAL(10,4),         -- Annual interest rate (e.g., 0.065 = 6.5%)
    rate_type VARCHAR(20),                       -- FIXED or VARIABLE
    original_term_months INTEGER,                -- Original contractual loan term
    remaining_term_months INTEGER,               -- Months remaining until maturity

    -- =========================================================================
    -- LOSS METRICS (Cumulative)
    -- =========================================================================
    gross_charge_off_amount DECIMAL(18,2) DEFAULT 0,     -- Total amount written off as uncollectible
    recovery_amount_ytd DECIMAL(18,2) DEFAULT 0,         -- Amount recovered YTD after charge-off
    net_charge_off_ytd DECIMAL(18,2) DEFAULT 0,          -- Net loss after recoveries (YTD)

    -- =========================================================================
    -- METADATA
    -- =========================================================================
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- =========================================================================
    -- PRIMARY KEY (Composite: account + date for time series data)
    -- =========================================================================
    PRIMARY KEY (account_id, as_of_date)
);

-- =============================================================================
-- COMPUTED METRICS TABLE (Pre-Aggregated Portfolio Metrics)
-- =============================================================================
-- Optional table for fast dashboard queries
-- Contains portfolio-level aggregations by as_of_date

CREATE TABLE computed_metrics (
    -- =========================================================================
    -- PRIMARY KEY
    -- =========================================================================
    as_of_date DATE PRIMARY KEY,

    -- =========================================================================
    -- PORTFOLIO TOTALS
    -- =========================================================================
    total_outstanding_balance DECIMAL(18,2),
    total_previous_eop_balance DECIMAL(18,2),
    total_current_credit_limit DECIMAL(18,2),
    total_funded_amount DECIMAL(18,2),
    total_exposure_at_default DECIMAL(18,2),
    total_gross_credit_exposure DECIMAL(18,2),
    total_undrawn_amount DECIMAL(18,2),

    -- =========================================================================
    -- ACCOUNT COUNTS
    -- =========================================================================
    total_accounts INTEGER,
    num_active_accounts INTEGER,
    num_closed_accounts INTEGER,
    num_paid_off_accounts INTEGER,
    num_outstanding_accounts INTEGER,
    unique_customers INTEGER,

    -- =========================================================================
    -- DELINQUENCY METRICS
    -- =========================================================================
    num_accounts_30_plus_dpd INTEGER,
    num_accounts_60_plus_dpd INTEGER,
    num_accounts_90_plus_dpd INTEGER,
    delinquent_amount_30_plus DECIMAL(18,2),
    delinquent_amount_60_plus DECIMAL(18,2),
    delinquent_amount_90_plus DECIMAL(18,2),
    delinquency_rate_30_plus DECIMAL(10,4),
    delinquency_rate_60_plus DECIMAL(10,4),
    delinquency_rate_90_plus DECIMAL(10,4),
    num_accounts_ever_30_dpd INTEGER,
    num_impaired_accounts INTEGER,
    impaired_amount DECIMAL(18,2),

    -- =========================================================================
    -- EXPECTED CREDIT LOSS (ECL) METRICS
    -- =========================================================================
    total_expected_credit_loss DECIMAL(18,2),
    total_allowance_amount DECIMAL(18,2),
    ecl_coverage_ratio DECIMAL(10,4),

    -- ECL Stage Breakdown
    stage_1_balance DECIMAL(18,2),
    stage_2_balance DECIMAL(18,2),
    stage_3_balance DECIMAL(18,2),
    stage_1_ecl DECIMAL(18,2),
    stage_2_ecl DECIMAL(18,2),
    stage_3_ecl DECIMAL(18,2),
    stage_1_accounts INTEGER,
    stage_2_accounts INTEGER,
    stage_3_accounts INTEGER,
    stage_1_ecl_coverage DECIMAL(10,4),
    stage_2_ecl_coverage DECIMAL(10,4),
    stage_3_ecl_coverage DECIMAL(10,4),

    -- =========================================================================
    -- LOSS METRICS
    -- =========================================================================
    total_gross_charge_off DECIMAL(18,2),
    total_recovery_amount_ytd DECIMAL(18,2),
    total_net_charge_off_ytd DECIMAL(18,2),
    num_charged_off_accounts INTEGER,
    net_charge_off_rate DECIMAL(10,4),

    -- =========================================================================
    -- CREDIT SCORE METRICS
    -- =========================================================================
    weighted_avg_current_score DECIMAL(10,2),
    weighted_avg_origination_score DECIMAL(10,2),
    avg_current_credit_score DECIMAL(10,2),
    avg_origination_credit_score DECIMAL(10,2),
    num_high_risk_accounts INTEGER,
    high_risk_amount DECIMAL(18,2),

    -- =========================================================================
    -- LOAN-TO-VALUE (LTV) METRICS
    -- =========================================================================
    weighted_avg_current_ltv DECIMAL(10,4),
    weighted_avg_origination_ltv DECIMAL(10,4),
    num_accounts_ltv_above_80 INTEGER,
    num_accounts_ltv_above_100 INTEGER,
    num_accounts_ltv_above_120 INTEGER,
    amount_ltv_above_80 DECIMAL(18,2),
    amount_ltv_above_100 DECIMAL(18,2),
    total_property_value DECIMAL(18,2),

    -- =========================================================================
    -- RISK METRICS
    -- =========================================================================
    weighted_avg_pd DECIMAL(10,6),
    weighted_avg_lgd DECIMAL(10,4),
    portfolio_1yr_pd_weighted DECIMAL(10,6),
    avg_twelve_month_pd DECIMAL(10,6),
    avg_loss_given_default DECIMAL(10,4),

    -- =========================================================================
    -- UTILIZATION METRICS
    -- =========================================================================
    total_revolving_balance DECIMAL(18,2),
    total_revolving_limit DECIMAL(18,2),
    portfolio_utilization_rate DECIMAL(10,4),
    weighted_avg_utilization DECIMAL(10,4),
    num_accounts_util_above_50 INTEGER,
    num_accounts_util_above_75 INTEGER,
    num_accounts_util_above_90 INTEGER,

    -- =========================================================================
    -- INCOME & DTI METRICS
    -- =========================================================================
    total_annual_income DECIMAL(18,2),
    avg_annual_income DECIMAL(18,2),
    weighted_avg_dti DECIMAL(10,4),
    avg_debt_to_income DECIMAL(10,4),
    num_accounts_dti_above_43 INTEGER,

    -- =========================================================================
    -- BY PRODUCT
    -- =========================================================================
    num_accounts_mtg INTEGER,
    balance_mtg DECIMAL(18,2),
    ecl_mtg DECIMAL(18,2),
    num_accounts_auto INTEGER,
    balance_auto DECIMAL(18,2),
    ecl_auto DECIMAL(18,2),
    num_accounts_cc INTEGER,
    balance_cc DECIMAL(18,2),
    ecl_cc DECIMAL(18,2),
    num_accounts_pl INTEGER,
    balance_pl DECIMAL(18,2),
    ecl_pl DECIMAL(18,2),
    num_accounts_heloc INTEGER,
    balance_heloc DECIMAL(18,2),
    ecl_heloc DECIMAL(18,2),

    -- =========================================================================
    -- BY REGION
    -- =========================================================================
    num_accounts_northeast INTEGER,
    balance_northeast DECIMAL(18,2),
    num_accounts_southeast INTEGER,
    balance_southeast DECIMAL(18,2),
    num_accounts_midwest INTEGER,
    balance_midwest DECIMAL(18,2),
    num_accounts_west INTEGER,
    balance_west DECIMAL(18,2),
    num_accounts_central INTEGER,
    balance_central DECIMAL(18,2),

    -- =========================================================================
    -- BY SEGMENT
    -- =========================================================================
    num_accounts_prime INTEGER,
    balance_prime DECIMAL(18,2),
    ecl_prime DECIMAL(18,2),
    num_accounts_near_prime INTEGER,
    balance_near_prime DECIMAL(18,2),
    ecl_near_prime DECIMAL(18,2),
    num_accounts_subprime INTEGER,
    balance_subprime DECIMAL(18,2),
    ecl_subprime DECIMAL(18,2),

    -- =========================================================================
    -- BY VINTAGE YEAR
    -- =========================================================================
    num_accounts_vintage_2018 INTEGER,
    balance_vintage_2018 DECIMAL(18,2),
    num_accounts_vintage_2019 INTEGER,
    balance_vintage_2019 DECIMAL(18,2),
    num_accounts_vintage_2020 INTEGER,
    balance_vintage_2020 DECIMAL(18,2),
    num_accounts_vintage_2021 INTEGER,
    balance_vintage_2021 DECIMAL(18,2),
    num_accounts_vintage_2022 INTEGER,
    balance_vintage_2022 DECIMAL(18,2),
    num_accounts_vintage_2023 INTEGER,
    balance_vintage_2023 DECIMAL(18,2),
    num_accounts_vintage_2024 INTEGER,
    balance_vintage_2024 DECIMAL(18,2),
    num_accounts_vintage_2025 INTEGER,
    balance_vintage_2025 DECIMAL(18,2),

    -- =========================================================================
    -- BY APPLICATION CHANNEL
    -- =========================================================================
    num_accounts_channel_branch INTEGER,
    balance_channel_branch DECIMAL(18,2),
    num_accounts_channel_mobile INTEGER,
    balance_channel_mobile DECIMAL(18,2),
    num_accounts_channel_online INTEGER,
    balance_channel_online DECIMAL(18,2),
    num_accounts_channel_dealer INTEGER,
    balance_channel_dealer DECIMAL(18,2),
    num_accounts_channel_broker INTEGER,
    balance_channel_broker DECIMAL(18,2),
    num_accounts_channel_direct_mail INTEGER,
    balance_channel_direct_mail DECIMAL(18,2),

    -- =========================================================================
    -- LOAN TERMS
    -- =========================================================================
    weighted_avg_interest_rate DECIMAL(10,4),
    avg_interest_rate DECIMAL(10,4),
    num_fixed_rate_accounts INTEGER,
    num_variable_rate_accounts INTEGER,
    avg_original_term_months DECIMAL(10,2),
    avg_remaining_term_months DECIMAL(10,2),
    avg_age_on_book_months DECIMAL(10,2),
    weighted_avg_age_on_book DECIMAL(10,2),

    -- =========================================================================
    -- FORBEARANCE & MODIFICATION METRICS
    -- =========================================================================
    num_modified_accounts INTEGER,
    modified_amount DECIMAL(18,2),
    num_forbearance_accounts INTEGER,
    forbearance_amount DECIMAL(18,2),

    -- =========================================================================
    -- METADATA
    -- =========================================================================
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- INDEXES FOR PERFORMANCE
-- =============================================================================

-- Accounts Table Indexes
CREATE INDEX idx_accounts_as_of_date ON accounts(as_of_date);
CREATE INDEX idx_accounts_product ON accounts(product_code);
CREATE INDEX idx_accounts_region ON accounts(region_code);
CREATE INDEX idx_accounts_segment ON accounts(customer_segment);
CREATE INDEX idx_accounts_status ON accounts(account_status);
CREATE INDEX idx_accounts_vintage ON accounts(vintage_year);
CREATE INDEX idx_accounts_customer ON accounts(customer_id);
CREATE INDEX idx_accounts_channel ON accounts(application_channel);
CREATE INDEX idx_accounts_dpd ON accounts(days_past_due);
CREATE INDEX idx_accounts_ecl_stage ON accounts(ecl_stage);

-- Composite indexes for common query patterns
CREATE INDEX idx_accounts_date_product ON accounts(as_of_date, product_code);
CREATE INDEX idx_accounts_date_region ON accounts(as_of_date, region_code);
CREATE INDEX idx_accounts_date_segment ON accounts(as_of_date, customer_segment);
CREATE INDEX idx_accounts_product_region ON accounts(product_code, region_code);
CREATE INDEX idx_accounts_date_prod_reg ON accounts(as_of_date, product_code, region_code);

-- Computed Metrics Table Index
CREATE INDEX idx_computed_metrics_date ON computed_metrics(as_of_date);

-- =============================================================================
-- COMMENTS FOR DOCUMENTATION
-- =============================================================================

COMMENT ON TABLE accounts IS 'Account-level granular credit risk data with quarterly snapshots';
COMMENT ON TABLE computed_metrics IS 'Pre-aggregated portfolio-level metrics for fast dashboard queries';

COMMENT ON COLUMN accounts.adjusted_eop_balance IS 'End-of-period outstanding balance adjusted for accrued interest and fees';
COMMENT ON COLUMN accounts.days_past_due IS 'Number of days payment is overdue (0 = current)';
COMMENT ON COLUMN accounts.ecl_stage IS 'IFRS 9 ECL staging: 1=Performing, 2=Underperforming, 3=Non-performing';
COMMENT ON COLUMN accounts.twelve_month_pd IS 'Probability of default within next 12 months (0-1)';
COMMENT ON COLUMN accounts.expected_credit_loss IS '12-month expected credit loss provision under IFRS 9';

-- =============================================================================
-- DATA LOADING NOTES
-- =============================================================================
-- After running this schema, load data using:
--   python scripts/load_data_from_excel.py
--
-- Data source: CR360__Synthetic Data.xlsx
--   - Sheet 1: "Accounts Data" (1,142 rows) -> accounts table
--   - Sheet 2: "computed metrics" (8 rows) -> computed_metrics table
-- =============================================================================
