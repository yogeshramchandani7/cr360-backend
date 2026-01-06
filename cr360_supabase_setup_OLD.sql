-- =============================================================================
-- CR360 SYNTHETIC DATA - SUPABASE/POSTGRESQL VERSION
-- =============================================================================
-- Description: PostgreSQL-compatible schema for Supabase deployment
-- 
-- Setup Instructions:
-- 1. Create a new Supabase project at https://supabase.com
-- 2. Go to SQL Editor
-- 3. Paste and run this entire script
-- 4. Your tables will be created in the 'public' schema
--
-- Connection from Python:
--   pip install supabase
--   from supabase import create_client
--   supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
--
-- Or use direct PostgreSQL connection:
--   pip install psycopg2-binary
--   Connection string available in Supabase Dashboard > Settings > Database
-- =============================================================================

-- Enable UUID extension (already enabled in Supabase by default)
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================================================
-- DROP EXISTING TABLES (if re-running)
-- =============================================================================
DROP TABLE IF EXISTS agg_monthly_summary CASCADE;
DROP TABLE IF EXISTS dim_date CASCADE;
DROP TABLE IF EXISTS dim_product CASCADE;
DROP TABLE IF EXISTS dim_region CASCADE;
DROP TABLE IF EXISTS dim_segment CASCADE;
DROP TABLE IF EXISTS dim_vintage CASCADE;

-- =============================================================================
-- DIMENSION TABLES
-- =============================================================================

-- Date Dimension
CREATE TABLE dim_date (
    date_skey INTEGER PRIMARY KEY,
    calendar_date DATE NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    quarter_name VARCHAR(10) NOT NULL,
    month INTEGER NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    is_month_end BOOLEAN DEFAULT FALSE,
    is_quarter_end BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Product Dimension
CREATE TABLE dim_product (
    product_skey INTEGER PRIMARY KEY,
    product_code VARCHAR(20) NOT NULL,
    product_name VARCHAR(100) NOT NULL,
    product_type VARCHAR(50) NOT NULL,
    product_family VARCHAR(50) NOT NULL,
    product_category VARCHAR(50) NOT NULL,
    is_secured BOOLEAN DEFAULT FALSE,
    is_revolving BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Region Dimension  
CREATE TABLE dim_region (
    region_skey INTEGER PRIMARY KEY,
    region_code VARCHAR(10) NOT NULL,
    region_name VARCHAR(50) NOT NULL,
    country VARCHAR(50) NOT NULL,
    state_province VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Segment Dimension
CREATE TABLE dim_segment (
    segment_skey INTEGER PRIMARY KEY,
    segment_code VARCHAR(20) NOT NULL,
    segment_name VARCHAR(50) NOT NULL,
    segment_type VARCHAR(20) NOT NULL,
    retail_classification VARCHAR(20),
    wholesale_classification VARCHAR(30),
    risk_tier INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Vintage Dimension
CREATE TABLE dim_vintage (
    vintage_skey INTEGER PRIMARY KEY,
    vintage_year INTEGER NOT NULL,
    vintage_quarter INTEGER NOT NULL,
    vintage_month INTEGER NOT NULL,
    vintage_quarter_name VARCHAR(10) NOT NULL,
    vintage_cohort VARCHAR(20) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- FACT/AGGREGATE TABLE
-- =============================================================================

CREATE TABLE agg_monthly_summary (
    id SERIAL,
    as_of_date_skey INTEGER NOT NULL REFERENCES dim_date(date_skey),
    product_skey INTEGER NOT NULL REFERENCES dim_product(product_skey),
    region_skey INTEGER NOT NULL REFERENCES dim_region(region_skey),
    segment_skey INTEGER NOT NULL REFERENCES dim_segment(segment_skey),
    
    -- Counts
    account_count INTEGER DEFAULT 0,
    delinquent_account_count INTEGER DEFAULT 0,
    dpd_30_account_count INTEGER DEFAULT 0,
    dpd_60_account_count INTEGER DEFAULT 0,
    dpd_90_account_count INTEGER DEFAULT 0,
    npl_account_count INTEGER DEFAULT 0,
    charge_off_account_count INTEGER DEFAULT 0,
    
    -- Balances (stored in dollars, display in millions/billions)
    total_exposure DECIMAL(18,2) DEFAULT 0,
    total_outstanding DECIMAL(18,2) DEFAULT 0,
    total_credit_limit DECIMAL(18,2) DEFAULT 0,
    delinquent_balance DECIMAL(18,2) DEFAULT 0,
    dpd_30_balance DECIMAL(18,2) DEFAULT 0,
    dpd_60_balance DECIMAL(18,2) DEFAULT 0,
    dpd_90_balance DECIMAL(18,2) DEFAULT 0,
    npl_balance DECIMAL(18,2) DEFAULT 0,
    
    -- Loss Metrics
    net_charge_off_mtd DECIMAL(18,2) DEFAULT 0,
    net_charge_off_qtd DECIMAL(18,2) DEFAULT 0,
    net_charge_off_ytd DECIMAL(18,2) DEFAULT 0,
    ecl_balance DECIMAL(18,2) DEFAULT 0,
    allowance_balance DECIMAL(18,2) DEFAULT 0,
    
    -- Origination Metrics
    origination_count INTEGER DEFAULT 0,
    origination_volume DECIMAL(18,2) DEFAULT 0,
    funded_count INTEGER DEFAULT 0,
    funded_volume DECIMAL(18,2) DEFAULT 0,
    
    -- Weighted Averages
    avg_credit_score DECIMAL(10,2),
    avg_origination_score DECIMAL(10,2),
    avg_ltv DECIMAL(10,4),
    avg_pd DECIMAL(10,6),
    avg_utilization DECIMAL(10,4),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    PRIMARY KEY (as_of_date_skey, product_skey, region_skey, segment_skey)
);

-- =============================================================================
-- INDEXES FOR PERFORMANCE
-- =============================================================================

CREATE INDEX idx_agg_date ON agg_monthly_summary(as_of_date_skey);
CREATE INDEX idx_agg_product ON agg_monthly_summary(product_skey);
CREATE INDEX idx_agg_region ON agg_monthly_summary(region_skey);
CREATE INDEX idx_agg_segment ON agg_monthly_summary(segment_skey);
CREATE INDEX idx_date_quarter ON dim_date(quarter_name);
CREATE INDEX idx_region_name ON dim_region(region_name);
CREATE INDEX idx_segment_class ON dim_segment(retail_classification);
CREATE INDEX idx_product_type ON dim_product(product_type);

-- =============================================================================
-- POPULATE DIMENSION DATA
-- =============================================================================

-- Date Dimension (8 quarters: Q1-2024 through Q4-2025)
INSERT INTO dim_date (date_skey, calendar_date, year, quarter, quarter_name, month, month_name, is_month_end, is_quarter_end) VALUES
(20240331, '2024-03-31', 2024, 1, 'Q1-2024', 3, 'March', TRUE, TRUE),
(20240630, '2024-06-30', 2024, 2, 'Q2-2024', 6, 'June', TRUE, TRUE),
(20240930, '2024-09-30', 2024, 3, 'Q3-2024', 9, 'September', TRUE, TRUE),
(20241231, '2024-12-31', 2024, 4, 'Q4-2024', 12, 'December', TRUE, TRUE),
(20250331, '2025-03-31', 2025, 1, 'Q1-2025', 3, 'March', TRUE, TRUE),
(20250630, '2025-06-30', 2025, 2, 'Q2-2025', 6, 'June', TRUE, TRUE),
(20250930, '2025-09-30', 2025, 3, 'Q3-2025', 9, 'September', TRUE, TRUE),
(20251231, '2025-12-31', 2025, 4, 'Q4-2025', 12, 'December', TRUE, TRUE);

-- Product Dimension
INSERT INTO dim_product (product_skey, product_code, product_name, product_type, product_family, product_category, is_secured, is_revolving) VALUES
(1, 'MTG', 'Mortgage', 'Mortgage', 'Secured', 'Retail', TRUE, FALSE),
(2, 'AUTO', 'Auto Loan', 'Auto', 'Secured', 'Retail', TRUE, FALSE),
(3, 'CC', 'Credit Card', 'Credit Card', 'Unsecured', 'Retail', FALSE, TRUE),
(4, 'PL', 'Personal Loan', 'Personal Loan', 'Unsecured', 'Retail', FALSE, FALSE),
(5, 'HELOC', 'Home Equity Line', 'HELOC', 'Secured', 'Retail', TRUE, TRUE),
(6, 'COMM', 'Commercial', 'Commercial', 'Secured', 'Commercial', TRUE, FALSE);

-- Region Dimension
INSERT INTO dim_region (region_skey, region_code, region_name, country, state_province) VALUES
(1, 'NE', 'Northeast', 'United States', 'New York'),
(2, 'SE', 'Southeast', 'United States', 'Florida'),
(3, 'MW', 'Midwest', 'United States', 'Illinois'),
(4, 'WE', 'West', 'United States', 'California'),
(5, 'CA', 'Canada', 'Canada', 'Ontario');

-- Segment Dimension
INSERT INTO dim_segment (segment_skey, segment_code, segment_name, segment_type, retail_classification, wholesale_classification, risk_tier) VALUES
(1, 'PRIME', 'Prime', 'Retail', 'Prime', NULL, 1),
(2, 'NPRIME', 'Near-Prime', 'Retail', 'Near-Prime', NULL, 2),
(3, 'SUBP', 'Subprime', 'Retail', 'Subprime', NULL, 3);

-- Vintage Dimension (sample vintages)
INSERT INTO dim_vintage (vintage_skey, vintage_year, vintage_quarter, vintage_month, vintage_quarter_name, vintage_cohort) VALUES
(202401, 2024, 1, 1, 'Q1-2024', '2024'),
(202404, 2024, 2, 4, 'Q2-2024', '2024'),
(202407, 2024, 3, 7, 'Q3-2024', '2024'),
(202410, 2024, 4, 10, 'Q4-2024', '2024'),
(202501, 2025, 1, 1, 'Q1-2025', '2025'),
(202504, 2025, 2, 4, 'Q2-2025', '2025'),
(202507, 2025, 3, 7, 'Q3-2025', '2025'),
(202510, 2025, 4, 10, 'Q4-2025', '2025');

-- =============================================================================
-- POPULATE AGGREGATE DATA WITH REALISTIC PATTERNS
-- =============================================================================
-- Total Portfolio: ~$400B
-- 
-- BUILT-IN DEMO PATTERNS:
-- 1. Southeast region: High originations but deteriorating credit quality
-- 2. Subprime segment: Rising delinquency trend (5% → 8%+)
-- 3. Auto product: Elevated charge-offs
-- 4. Credit Card: High utilization in stressed segments
-- 5. Canada: Best performer (control group)
-- =============================================================================

-- ============================================
-- Q1-2024 (BASELINE PERIOD)
-- ============================================

-- Northeast - Mortgage
INSERT INTO agg_monthly_summary (as_of_date_skey, product_skey, region_skey, segment_skey, account_count, delinquent_account_count, dpd_30_account_count, dpd_60_account_count, dpd_90_account_count, npl_account_count, charge_off_account_count, total_exposure, total_outstanding, total_credit_limit, delinquent_balance, dpd_30_balance, dpd_60_balance, dpd_90_balance, npl_balance, net_charge_off_mtd, net_charge_off_qtd, net_charge_off_ytd, ecl_balance, allowance_balance, origination_count, origination_volume, funded_count, funded_volume, avg_credit_score, avg_origination_score, avg_ltv, avg_pd, avg_utilization) VALUES
(20240331, 1, 1, 1, 125000, 1500, 1275, 750, 450, 300, 100, 35000000000, 30000000000, 38000000000, 450000000, 382500000, 225000000, 135000000, 90000000, 7500000, 22500000, 90000000, 675000000, 540000000, 6250, 1500000000, 6000, 1440000000, 745, 760, 0.72, 0.012, NULL),
(20240331, 1, 1, 2, 48000, 1200, 1020, 600, 360, 240, 95, 13500000000, 11500000000, 14500000000, 287500000, 244375000, 143750000, 86250000, 57500000, 4791667, 14375000, 57500000, 431250000, 345000000, 2400, 575000000, 2300, 552000000, 700, 715, 0.74, 0.020, NULL),
(20240331, 1, 1, 3, 19200, 1100, 935, 550, 330, 220, 110, 5400000000, 4600000000, 5800000000, 230000000, 195500000, 115000000, 69000000, 46000000, 3833333, 11500000, 46000000, 345000000, 276000000, 960, 230000000, 920, 220800000, 630, 645, 0.78, 0.045, NULL);

-- Northeast - Auto
INSERT INTO agg_monthly_summary (as_of_date_skey, product_skey, region_skey, segment_skey, account_count, delinquent_account_count, dpd_30_account_count, dpd_60_account_count, dpd_90_account_count, npl_account_count, charge_off_account_count, total_exposure, total_outstanding, total_credit_limit, delinquent_balance, dpd_30_balance, dpd_60_balance, dpd_90_balance, npl_balance, net_charge_off_mtd, net_charge_off_qtd, net_charge_off_ytd, ecl_balance, allowance_balance, origination_count, origination_volume, funded_count, funded_volume, avg_credit_score, avg_origination_score, avg_ltv, avg_pd, avg_utilization) VALUES
(20240331, 2, 1, 1, 45000, 1350, 1148, 675, 405, 270, 135, 1350000000, 1260000000, 1500000000, 47880000, 40698000, 23940000, 14364000, 9576000, 1260000, 3780000, 15120000, 71820000, 57456000, 2250, 63000000, 2160, 60480000, 695, 710, NULL, 0.032, NULL),
(20240331, 2, 1, 2, 17300, 1080, 918, 540, 324, 216, 130, 519000000, 484000000, 576000000, 25410000, 21599000, 12705000, 7623000, 5082000, 645333, 1936000, 7744000, 38115000, 30492000, 865, 24200000, 830, 23232000, 650, 665, NULL, 0.048, NULL),
(20240331, 2, 1, 3, 6900, 990, 842, 495, 297, 198, 150, 207000000, 193000000, 230000000, 20272000, 17231000, 10136000, 6082000, 4054000, 515667, 1547000, 6188000, 30408000, 24326000, 345, 9660000, 331, 9274000, 580, 595, NULL, 0.095, NULL);

-- Northeast - Credit Card
INSERT INTO agg_monthly_summary (as_of_date_skey, product_skey, region_skey, segment_skey, account_count, delinquent_account_count, dpd_30_account_count, dpd_60_account_count, dpd_90_account_count, npl_account_count, charge_off_account_count, total_exposure, total_outstanding, total_credit_limit, delinquent_balance, dpd_30_balance, dpd_60_balance, dpd_90_balance, npl_balance, net_charge_off_mtd, net_charge_off_qtd, net_charge_off_ytd, ecl_balance, allowance_balance, origination_count, origination_volume, funded_count, funded_volume, avg_credit_score, avg_origination_score, avg_ltv, avg_pd, avg_utilization) VALUES
(20240331, 3, 1, 1, 280000, 5600, 4760, 2800, 1680, 1120, 840, 2520000000, 2380000000, 3500000000, 59500000, 50575000, 29750000, 17850000, 11900000, 6958333, 20875000, 83500000, 89250000, 71400000, 14000, 119000000, 13440, 114240000, 710, 725, NULL, 0.021, 0.30),
(20240331, 3, 1, 2, 107700, 4480, 3808, 2240, 1344, 896, 800, 969300000, 915000000, 1346250000, 31725000, 26966250, 15862500, 9517500, 6345000, 3708333, 11125000, 44500000, 47587500, 38070000, 5385, 45750000, 5170, 43920000, 665, 680, NULL, 0.030, 0.35),
(20240331, 3, 1, 3, 43100, 4100, 3485, 2050, 1230, 820, 920, 387900000, 366000000, 538500000, 25620000, 21777000, 12810000, 7686000, 5124000, 2998333, 8995000, 35980000, 38430000, 30744000, 2155, 18300000, 2069, 17568000, 595, 610, NULL, 0.065, 0.42);

-- Southeast - Mortgage (STRESS REGION)
INSERT INTO agg_monthly_summary (as_of_date_skey, product_skey, region_skey, segment_skey, account_count, delinquent_account_count, dpd_30_account_count, dpd_60_account_count, dpd_90_account_count, npl_account_count, charge_off_account_count, total_exposure, total_outstanding, total_credit_limit, delinquent_balance, dpd_30_balance, dpd_60_balance, dpd_90_balance, npl_balance, net_charge_off_mtd, net_charge_off_qtd, net_charge_off_ytd, ecl_balance, allowance_balance, origination_count, origination_volume, funded_count, funded_volume, avg_credit_score, avg_origination_score, avg_ltv, avg_pd, avg_utilization) VALUES
(20240331, 1, 2, 1, 156250, 2250, 1913, 1125, 675, 450, 150, 43750000000, 37500000000, 47500000000, 675000000, 573750000, 337500000, 202500000, 135000000, 11250000, 33750000, 135000000, 1012500000, 810000000, 7813, 1875000000, 7500, 1800000000, 740, 755, 0.73, 0.015, NULL),
(20240331, 1, 2, 2, 60000, 1800, 1530, 900, 540, 360, 140, 16875000000, 14375000000, 18125000000, 431250000, 366562500, 215625000, 129375000, 86250000, 7187500, 21562500, 86250000, 646875000, 517500000, 3000, 718750000, 2880, 690000000, 695, 710, 0.75, 0.025, NULL),
(20240331, 1, 2, 3, 24000, 1650, 1403, 825, 495, 330, 165, 6750000000, 5750000000, 7250000000, 345000000, 293250000, 172500000, 103500000, 69000000, 5750000, 17250000, 69000000, 517500000, 414000000, 1200, 287500000, 1152, 276000000, 625, 640, 0.80, 0.055, NULL);

-- Southeast - Auto (STRESS REGION)
INSERT INTO agg_monthly_summary (as_of_date_skey, product_skey, region_skey, segment_skey, account_count, delinquent_account_count, dpd_30_account_count, dpd_60_account_count, dpd_90_account_count, npl_account_count, charge_off_account_count, total_exposure, total_outstanding, total_credit_limit, delinquent_balance, dpd_30_balance, dpd_60_balance, dpd_90_balance, npl_balance, net_charge_off_mtd, net_charge_off_qtd, net_charge_off_ytd, ecl_balance, allowance_balance, origination_count, origination_volume, funded_count, funded_volume, avg_credit_score, avg_origination_score, avg_ltv, avg_pd, avg_utilization) VALUES
(20240331, 2, 2, 1, 56250, 2025, 1721, 1013, 608, 405, 200, 1687500000, 1575000000, 1875000000, 71820000, 61047000, 35910000, 21546000, 14364000, 1890000, 5670000, 22680000, 107730000, 86184000, 2813, 78750000, 2700, 75600000, 690, 705, NULL, 0.040, NULL),
(20240331, 2, 2, 2, 21625, 1620, 1377, 810, 486, 324, 190, 648750000, 605000000, 720000000, 38115000, 32397750, 19057500, 11434500, 7623000, 969167, 2907500, 11630000, 57172500, 45738000, 1081, 30250000, 1038, 29040000, 645, 660, NULL, 0.058, NULL),
(20240331, 2, 2, 3, 8625, 1485, 1262, 743, 446, 297, 220, 258750000, 241250000, 287500000, 30408000, 25846800, 15204000, 9122400, 6081600, 773333, 2320000, 9280000, 45612000, 36489600, 431, 12062500, 414, 11580000, 575, 590, NULL, 0.115, NULL);

-- Southeast - Credit Card (STRESS REGION)
INSERT INTO agg_monthly_summary (as_of_date_skey, product_skey, region_skey, segment_skey, account_count, delinquent_account_count, dpd_30_account_count, dpd_60_account_count, dpd_90_account_count, npl_account_count, charge_off_account_count, total_exposure, total_outstanding, total_credit_limit, delinquent_balance, dpd_30_balance, dpd_60_balance, dpd_90_balance, npl_balance, net_charge_off_mtd, net_charge_off_qtd, net_charge_off_ytd, ecl_balance, allowance_balance, origination_count, origination_volume, funded_count, funded_volume, avg_credit_score, avg_origination_score, avg_ltv, avg_pd, avg_utilization) VALUES
(20240331, 3, 2, 1, 350000, 8400, 7140, 4200, 2520, 1680, 1260, 3150000000, 2975000000, 4375000000, 89250000, 75862500, 44625000, 26775000, 17850000, 10437500, 31312500, 125250000, 133875000, 107100000, 17500, 148750000, 16800, 142800000, 705, 720, NULL, 0.026, 0.32),
(20240331, 3, 2, 2, 134625, 6720, 5712, 3360, 2016, 1344, 1200, 1211625000, 1143750000, 1682812500, 47587500, 40449375, 23793750, 14276250, 9517500, 5562500, 16687500, 66750000, 71381250, 57105000, 6731, 57187500, 6462, 54900000, 660, 675, NULL, 0.036, 0.38),
(20240331, 3, 2, 3, 53875, 6150, 5228, 3075, 1845, 1230, 1380, 484875000, 457500000, 673125000, 38430000, 32665500, 19215000, 11529000, 7686000, 4493750, 13481250, 53925000, 57645000, 46116000, 2694, 22875000, 2586, 21960000, 590, 605, NULL, 0.078, 0.45);

-- Midwest - Mortgage
INSERT INTO agg_monthly_summary (as_of_date_skey, product_skey, region_skey, segment_skey, account_count, delinquent_account_count, dpd_30_account_count, dpd_60_account_count, dpd_90_account_count, npl_account_count, charge_off_account_count, total_exposure, total_outstanding, total_credit_limit, delinquent_balance, dpd_30_balance, dpd_60_balance, dpd_90_balance, npl_balance, net_charge_off_mtd, net_charge_off_qtd, net_charge_off_ytd, ecl_balance, allowance_balance, origination_count, origination_volume, funded_count, funded_volume, avg_credit_score, avg_origination_score, avg_ltv, avg_pd, avg_utilization) VALUES
(20240331, 1, 3, 1, 112500, 1350, 1148, 675, 405, 270, 90, 31500000000, 27000000000, 34200000000, 405000000, 344250000, 202500000, 121500000, 81000000, 6750000, 20250000, 81000000, 607500000, 486000000, 5625, 1350000000, 5400, 1296000000, 748, 763, 0.71, 0.011, NULL),
(20240331, 1, 3, 2, 43200, 1080, 918, 540, 324, 216, 85, 12150000000, 10350000000, 13050000000, 258750000, 219937500, 129375000, 77625000, 51750000, 4312500, 12937500, 51750000, 388125000, 310500000, 2160, 517500000, 2074, 496800000, 703, 718, 0.73, 0.018, NULL),
(20240331, 1, 3, 3, 17280, 990, 842, 495, 297, 198, 100, 4860000000, 4140000000, 5220000000, 207000000, 175950000, 103500000, 62100000, 41400000, 3450000, 10350000, 41400000, 310500000, 248400000, 864, 207000000, 829, 198720000, 633, 648, 0.77, 0.042, NULL);

-- West - Mortgage
INSERT INTO agg_monthly_summary (as_of_date_skey, product_skey, region_skey, segment_skey, account_count, delinquent_account_count, dpd_30_account_count, dpd_60_account_count, dpd_90_account_count, npl_account_count, charge_off_account_count, total_exposure, total_outstanding, total_credit_limit, delinquent_balance, dpd_30_balance, dpd_60_balance, dpd_90_balance, npl_balance, net_charge_off_mtd, net_charge_off_qtd, net_charge_off_ytd, ecl_balance, allowance_balance, origination_count, origination_volume, funded_count, funded_volume, avg_credit_score, avg_origination_score, avg_ltv, avg_pd, avg_utilization) VALUES
(20240331, 1, 4, 1, 125000, 1375, 1169, 688, 413, 275, 88, 35000000000, 30000000000, 38000000000, 412500000, 350625000, 206250000, 123750000, 82500000, 6875000, 20625000, 82500000, 618750000, 495000000, 6250, 1500000000, 6000, 1440000000, 750, 765, 0.70, 0.010, NULL),
(20240331, 1, 4, 2, 48000, 1100, 935, 550, 330, 220, 83, 13500000000, 11500000000, 14500000000, 263625000, 224081250, 131812500, 79087500, 52725000, 4393750, 13181250, 52725000, 395437500, 316350000, 2400, 575000000, 2304, 552000000, 705, 720, 0.72, 0.017, NULL),
(20240331, 1, 4, 3, 19200, 1010, 859, 505, 303, 202, 98, 5400000000, 4600000000, 5800000000, 210900000, 179265000, 105450000, 63270000, 42180000, 3515000, 10545000, 42180000, 316350000, 253080000, 960, 230000000, 922, 220800000, 635, 650, 0.76, 0.040, NULL);

-- Canada - Mortgage (BEST PERFORMER)
INSERT INTO agg_monthly_summary (as_of_date_skey, product_skey, region_skey, segment_skey, account_count, delinquent_account_count, dpd_30_account_count, dpd_60_account_count, dpd_90_account_count, npl_account_count, charge_off_account_count, total_exposure, total_outstanding, total_credit_limit, delinquent_balance, dpd_30_balance, dpd_60_balance, dpd_90_balance, npl_balance, net_charge_off_mtd, net_charge_off_qtd, net_charge_off_ytd, ecl_balance, allowance_balance, origination_count, origination_volume, funded_count, funded_volume, avg_credit_score, avg_origination_score, avg_ltv, avg_pd, avg_utilization) VALUES
(20240331, 1, 5, 1, 75000, 750, 638, 375, 225, 150, 45, 21000000000, 18000000000, 22800000000, 247500000, 210375000, 123750000, 74250000, 49500000, 4125000, 12375000, 49500000, 371250000, 297000000, 3750, 900000000, 3600, 864000000, 755, 770, 0.68, 0.009, NULL),
(20240331, 1, 5, 2, 28800, 600, 510, 300, 180, 120, 42, 8100000000, 6900000000, 8700000000, 141450000, 120232500, 70725000, 42435000, 28290000, 2357500, 7072500, 28290000, 212175000, 169740000, 1440, 345000000, 1382, 331200000, 710, 725, 0.70, 0.014, NULL),
(20240331, 1, 5, 3, 11520, 550, 468, 275, 165, 110, 50, 3240000000, 2760000000, 3480000000, 113160000, 96186000, 56580000, 33948000, 22632000, 1886000, 5658000, 22632000, 169740000, 135792000, 576, 138000000, 553, 132480000, 640, 655, 0.74, 0.035, NULL);

-- ============================================
-- Q4-2024 (STRESS BUILDING)
-- ============================================

-- Southeast - showing increased stress
INSERT INTO agg_monthly_summary (as_of_date_skey, product_skey, region_skey, segment_skey, account_count, delinquent_account_count, dpd_30_account_count, dpd_60_account_count, dpd_90_account_count, npl_account_count, charge_off_account_count, total_exposure, total_outstanding, total_credit_limit, delinquent_balance, dpd_30_balance, dpd_60_balance, dpd_90_balance, npl_balance, net_charge_off_mtd, net_charge_off_qtd, net_charge_off_ytd, ecl_balance, allowance_balance, origination_count, origination_volume, funded_count, funded_volume, avg_credit_score, avg_origination_score, avg_ltv, avg_pd, avg_utilization) VALUES
(20241231, 1, 2, 1, 164063, 2813, 2391, 1406, 844, 563, 200, 45937500000, 39375000000, 49875000000, 843750000, 717187500, 421875000, 253125000, 168750000, 14062500, 42187500, 168750000, 1265625000, 1012500000, 8203, 1968750000, 7875, 1890000000, 735, 750, 0.74, 0.018, NULL),
(20241231, 1, 2, 2, 63000, 2250, 1913, 1125, 675, 450, 185, 17718750000, 15093750000, 19031250000, 538125000, 457406250, 269062500, 161437500, 107625000, 8968750, 26906250, 107625000, 807187500, 645750000, 3150, 754687500, 3024, 724500000, 690, 705, 0.76, 0.030, NULL),
(20241231, 1, 2, 3, 25200, 2063, 1753, 1031, 619, 413, 220, 7087500000, 6037500000, 7612500000, 431250000, 366562500, 215625000, 129375000, 86250000, 7187500, 21562500, 86250000, 646875000, 517500000, 1260, 301875000, 1210, 289800000, 620, 635, 0.81, 0.068, NULL),
(20241231, 2, 2, 3, 9056, 1856, 1578, 928, 557, 371, 295, 271687500, 253312500, 301875000, 38010000, 32308500, 19005000, 11403000, 7602000, 966750, 2900250, 11601000, 57015000, 45612000, 453, 12665625, 435, 12157200, 570, 585, NULL, 0.145, NULL),
(20241231, 3, 2, 3, 56569, 7688, 6534, 3844, 2306, 1538, 1840, 509118750, 480562500, 706828125, 48037500, 40831875, 24018750, 14411250, 9607500, 5616563, 16849688, 67398750, 72056250, 57645000, 2828, 24028125, 2715, 23058000, 585, 600, NULL, 0.098, 0.50);

-- ============================================
-- Q4-2025 (CURRENT PERIOD - FULL STRESS VISIBLE)
-- ============================================

-- Northeast
INSERT INTO agg_monthly_summary (as_of_date_skey, product_skey, region_skey, segment_skey, account_count, delinquent_account_count, dpd_30_account_count, dpd_60_account_count, dpd_90_account_count, npl_account_count, charge_off_account_count, total_exposure, total_outstanding, total_credit_limit, delinquent_balance, dpd_30_balance, dpd_60_balance, dpd_90_balance, npl_balance, net_charge_off_mtd, net_charge_off_qtd, net_charge_off_ytd, ecl_balance, allowance_balance, origination_count, origination_volume, funded_count, funded_volume, avg_credit_score, avg_origination_score, avg_ltv, avg_pd, avg_utilization) VALUES
(20251231, 1, 1, 1, 131325, 2145, 1823, 1073, 644, 429, 165, 36771000000, 31518000000, 39923000000, 643500000, 546975000, 321750000, 193050000, 128700000, 10725000, 32175000, 128700000, 965250000, 772200000, 6566, 1575900000, 6304, 1512864000, 740, 755, 0.73, 0.018, NULL),
(20251231, 1, 1, 2, 50429, 1872, 1591, 936, 562, 374, 165, 14183250000, 12082050000, 15233550000, 461760000, 392496000, 230880000, 138528000, 92352000, 7696000, 23088000, 92352000, 692640000, 554112000, 2521, 604102500, 2421, 580178400, 695, 710, 0.75, 0.031, NULL),
(20251231, 1, 1, 3, 20172, 1788, 1519, 894, 537, 358, 200, 5673420000, 4833180000, 6093780000, 388700000, 330395000, 194350000, 116610000, 77740000, 6478333, 19435000, 77740000, 583050000, 466440000, 1009, 241659000, 969, 231993000, 625, 640, 0.79, 0.073, NULL),
(20251231, 2, 1, 1, 45900, 1890, 1607, 945, 567, 378, 203, 1377000000, 1285200000, 1530000000, 67068000, 57007800, 33534000, 20120400, 13413600, 1765800, 5297400, 21189600, 100602000, 80481600, 2295, 64260000, 2203, 61689600, 690, 705, NULL, 0.045, NULL),
(20251231, 2, 1, 2, 17646, 1512, 1285, 756, 454, 302, 195, 529380000, 493680000, 587520000, 35612400, 30270540, 17806200, 10683720, 7122480, 905040, 2715120, 10860480, 53418600, 42734880, 882, 24684000, 847, 23696640, 645, 660, NULL, 0.068, NULL),
(20251231, 2, 1, 3, 7038, 1386, 1178, 693, 416, 277, 225, 211140000, 196860000, 234600000, 28392120, 24133302, 14196060, 8517636, 5678424, 721820, 2165460, 8661840, 42588180, 34070544, 352, 9843000, 338, 9449280, 575, 590, NULL, 0.135, NULL),
(20251231, 3, 1, 1, 285600, 6855, 5827, 3428, 2057, 1371, 1080, 2570400000, 2427600000, 3570000000, 72810000, 61888500, 36405000, 21843000, 14562000, 8512500, 25537500, 102150000, 109215000, 87372000, 14280, 121380000, 13709, 116526000, 705, 720, NULL, 0.026, 0.33),
(20251231, 3, 1, 2, 109857, 5478, 4656, 2739, 1644, 1096, 979, 988713000, 933285000, 1372571250, 38831625, 33006781, 19415906, 11649544, 7766363, 4537656, 13612969, 54451875, 58247438, 46597950, 5493, 46664250, 5273, 44797680, 660, 675, NULL, 0.037, 0.38);

-- Southeast (MAXIMUM STRESS - DEMO FOCAL POINT)
INSERT INTO agg_monthly_summary (as_of_date_skey, product_skey, region_skey, segment_skey, account_count, delinquent_account_count, dpd_30_account_count, dpd_60_account_count, dpd_90_account_count, npl_account_count, charge_off_account_count, total_exposure, total_outstanding, total_credit_limit, delinquent_balance, dpd_30_balance, dpd_60_balance, dpd_90_balance, npl_balance, net_charge_off_mtd, net_charge_off_qtd, net_charge_off_ytd, ecl_balance, allowance_balance, origination_count, origination_volume, funded_count, funded_volume, avg_credit_score, avg_origination_score, avg_ltv, avg_pd, avg_utilization) VALUES
(20251231, 1, 2, 1, 171866, 3656, 3108, 1828, 1097, 731, 275, 48122500000, 41250000000, 52250000000, 1097812500, 933240625, 548906250, 329343750, 219562500, 18296875, 54890625, 219562500, 1646718750, 1317375000, 8593, 2062500000, 8250, 1980000000, 730, 745, 0.75, 0.023, NULL),
(20251231, 1, 2, 2, 65940, 2925, 2486, 1463, 878, 585, 255, 18546562500, 15804937500, 19932187500, 700218750, 595185938, 350109375, 210065625, 140043750, 11670313, 35010938, 140043750, 1050328125, 840262500, 3297, 790246875, 3165, 758636625, 685, 700, 0.77, 0.039, NULL),
(20251231, 1, 2, 3, 26376, 2681, 2279, 1341, 804, 536, 303, 7418625000, 6321975000, 7972875000, 560812500, 476690625, 280406250, 168243750, 112162500, 9346875, 28040625, 112162500, 841218750, 672975000, 1319, 316098750, 1266, 303454800, 615, 630, 0.82, 0.088, NULL),
(20251231, 2, 2, 1, 61816, 3291, 2797, 1645, 987, 658, 365, 1854487500, 1731225000, 2062125000, 116776875, 99260344, 58388438, 35033063, 23355375, 3074063, 9222188, 36888750, 175165313, 140132250, 3091, 86561250, 2967, 83098800, 680, 695, NULL, 0.065, NULL),
(20251231, 2, 2, 2, 23769, 2633, 2238, 1316, 790, 526, 347, 713062500, 665137500, 792225000, 61930125, 52640606, 30965063, 18579038, 12386025, 1575225, 4725675, 18902700, 92895188, 74316150, 1188, 33256875, 1141, 31926600, 635, 650, NULL, 0.094, NULL),
(20251231, 2, 2, 3, 9478, 2412, 2050, 1206, 724, 482, 405, 284343750, 265218750, 316125000, 49411125, 42009456, 24705563, 14823338, 9882225, 1256775, 3770325, 15081300, 74116688, 59293350, 474, 13262344, 455, 12731850, 565, 580, NULL, 0.188, NULL),
(20251231, 3, 2, 1, 384825, 13650, 11603, 6825, 4095, 2730, 2310, 3463425000, 3269625000, 4808531250, 145163438, 123388922, 72581719, 43549031, 29032688, 16972969, 50918906, 203675625, 217745156, 174196125, 19241, 163481250, 18472, 157102500, 695, 710, NULL, 0.042, 0.40),
(20251231, 3, 2, 2, 148023, 10920, 9282, 5460, 3276, 2184, 2200, 1332206250, 1257982500, 1850198438, 77430000, 65815500, 38715000, 23229000, 15486000, 9046875, 27140625, 108562500, 116103750, 92883000, 7401, 62899125, 7105, 60382680, 650, 665, NULL, 0.058, 0.48),
(20251231, 3, 2, 3, 59236, 10010, 8509, 5005, 3003, 2002, 2530, 533124375, 503374500, 740178938, 62508750, 53132438, 31254375, 18752625, 12501750, 7306250, 21918750, 87675000, 93763125, 75010500, 2962, 25168688, 2843, 24161940, 580, 595, NULL, 0.128, 0.58);

-- Midwest
INSERT INTO agg_monthly_summary (as_of_date_skey, product_skey, region_skey, segment_skey, account_count, delinquent_account_count, dpd_30_account_count, dpd_60_account_count, dpd_90_account_count, npl_account_count, charge_off_account_count, total_exposure, total_outstanding, total_credit_limit, delinquent_balance, dpd_30_balance, dpd_60_balance, dpd_90_balance, npl_balance, net_charge_off_mtd, net_charge_off_qtd, net_charge_off_ytd, ecl_balance, allowance_balance, origination_count, origination_volume, funded_count, funded_volume, avg_credit_score, avg_origination_score, avg_ltv, avg_pd, avg_utilization) VALUES
(20251231, 1, 3, 1, 114750, 1755, 1492, 878, 527, 351, 124, 32130000000, 27540000000, 34884000000, 526500000, 447525000, 263250000, 157950000, 105300000, 8775000, 26325000, 105300000, 789750000, 631800000, 5738, 1377000000, 5508, 1321920000, 745, 760, 0.72, 0.014, NULL),
(20251231, 1, 3, 2, 44064, 1404, 1193, 702, 421, 281, 117, 12393000000, 10557000000, 13314600000, 336150000, 285727500, 168075000, 100845000, 67230000, 5602500, 16807500, 67230000, 504225000, 403380000, 2203, 527850000, 2115, 506736000, 700, 715, 0.74, 0.023, NULL),
(20251231, 1, 3, 3, 17626, 1287, 1094, 644, 386, 258, 138, 4957200000, 4222800000, 5325840000, 269100000, 228735000, 134550000, 80730000, 53820000, 4485000, 13455000, 53820000, 403650000, 322920000, 881, 211140000, 846, 202694400, 630, 645, 0.78, 0.055, NULL);

-- West
INSERT INTO agg_monthly_summary (as_of_date_skey, product_skey, region_skey, segment_skey, account_count, delinquent_account_count, dpd_30_account_count, dpd_60_account_count, dpd_90_account_count, npl_account_count, charge_off_account_count, total_exposure, total_outstanding, total_credit_limit, delinquent_balance, dpd_30_balance, dpd_60_balance, dpd_90_balance, npl_balance, net_charge_off_mtd, net_charge_off_qtd, net_charge_off_ytd, ecl_balance, allowance_balance, origination_count, origination_volume, funded_count, funded_volume, avg_credit_score, avg_origination_score, avg_ltv, avg_pd, avg_utilization) VALUES
(20251231, 1, 4, 1, 127500, 1788, 1519, 894, 537, 358, 121, 35700000000, 30600000000, 38760000000, 536250000, 455812500, 268125000, 160875000, 107250000, 8937500, 26812500, 107250000, 804375000, 643500000, 6375, 1530000000, 6120, 1468800000, 747, 762, 0.71, 0.013, NULL),
(20251231, 1, 4, 2, 48960, 1430, 1216, 715, 429, 286, 114, 13770000000, 11730000000, 14790000000, 342720000, 291312000, 171360000, 102816000, 68544000, 5712000, 17136000, 68544000, 514080000, 411264000, 2448, 586500000, 2350, 563040000, 702, 717, 0.73, 0.022, NULL),
(20251231, 1, 4, 3, 19584, 1313, 1116, 656, 394, 262, 135, 5508000000, 4692000000, 5916000000, 274230000, 233095500, 137115000, 82269000, 54846000, 4570500, 13711500, 54846000, 411345000, 329076000, 979, 234600000, 940, 225216000, 632, 647, 0.77, 0.052, NULL);

-- Canada (BEST PERFORMER)
INSERT INTO agg_monthly_summary (as_of_date_skey, product_skey, region_skey, segment_skey, account_count, delinquent_account_count, dpd_30_account_count, dpd_60_account_count, dpd_90_account_count, npl_account_count, charge_off_account_count, total_exposure, total_outstanding, total_credit_limit, delinquent_balance, dpd_30_balance, dpd_60_balance, dpd_90_balance, npl_balance, net_charge_off_mtd, net_charge_off_qtd, net_charge_off_ytd, ecl_balance, allowance_balance, origination_count, origination_volume, funded_count, funded_volume, avg_credit_score, avg_origination_score, avg_ltv, avg_pd, avg_utilization) VALUES
(20251231, 1, 5, 1, 76500, 975, 829, 488, 293, 195, 62, 21420000000, 18360000000, 23256000000, 321750000, 273487500, 160875000, 96525000, 64350000, 5362500, 16087500, 64350000, 482625000, 386100000, 3825, 918000000, 3672, 881280000, 752, 767, 0.69, 0.012, NULL),
(20251231, 1, 5, 2, 29376, 780, 663, 390, 234, 156, 58, 8262000000, 7038000000, 8877600000, 183780000, 156213000, 91890000, 55134000, 36756000, 3063000, 9189000, 36756000, 275670000, 220536000, 1469, 351900000, 1410, 337824000, 707, 722, 0.71, 0.018, NULL),
(20251231, 1, 5, 3, 11750, 715, 608, 358, 215, 143, 69, 3304800000, 2815200000, 3550800000, 147015000, 124962750, 73507500, 44104500, 29403000, 2450250, 7350750, 29403000, 220522500, 176418000, 588, 140760000, 564, 135129600, 637, 652, 0.75, 0.045, NULL);


-- =============================================================================
-- VERIFICATION QUERIES
-- =============================================================================

-- Total portfolio check
SELECT 
    'Total Portfolio Q4-2025' AS check_name,
    ROUND(SUM(total_outstanding)::numeric / 1e9, 1) AS outstanding_billions,
    SUM(account_count) AS total_accounts
FROM agg_monthly_summary
WHERE as_of_date_skey = 20251231;

-- Regional comparison
SELECT 
    r.region_name,
    ROUND(SUM(a.total_outstanding)::numeric / 1e9, 1) AS outstanding_B,
    ROUND((SUM(a.dpd_30_balance) / NULLIF(SUM(a.total_outstanding), 0) * 100)::numeric, 2) AS dpd_30_pct
FROM agg_monthly_summary a
JOIN dim_region r ON a.region_skey = r.region_skey
WHERE a.as_of_date_skey = 20251231
GROUP BY r.region_name
ORDER BY dpd_30_pct DESC;

-- Segment stress in Southeast
SELECT 
    s.retail_classification AS segment,
    ROUND(SUM(a.total_outstanding)::numeric / 1e9, 2) AS outstanding_B,
    ROUND((SUM(a.dpd_30_balance) / NULLIF(SUM(a.total_outstanding), 0) * 100)::numeric, 2) AS dpd_30_pct,
    ROUND((SUM(a.avg_credit_score * a.total_outstanding) / NULLIF(SUM(a.total_outstanding), 0))::numeric, 0) AS avg_score
FROM agg_monthly_summary a
JOIN dim_segment s ON a.segment_skey = s.segment_skey
JOIN dim_region r ON a.region_skey = r.region_skey
WHERE a.as_of_date_skey = 20251231 
  AND r.region_name = 'Southeast'
GROUP BY s.retail_classification
ORDER BY dpd_30_pct DESC;

-- =============================================================================
-- ROW LEVEL SECURITY (Optional - for multi-tenant access)
-- =============================================================================
-- Uncomment if you want to enable RLS for different user access levels

-- ALTER TABLE agg_monthly_summary ENABLE ROW LEVEL SECURITY;

-- CREATE POLICY "Allow read for authenticated users" ON agg_monthly_summary
--     FOR SELECT
--     TO authenticated
--     USING (true);

-- =============================================================================
-- GRANT PERMISSIONS
-- =============================================================================

-- Grant read access to anon and authenticated roles (Supabase default)
GRANT SELECT ON ALL TABLES IN SCHEMA public TO anon;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO authenticated;

-- =============================================================================
-- COMPLETE
-- =============================================================================
-- Your CR360 prototype database is ready!
-- 
-- Quick test queries:
-- 
-- 1. SELECT * FROM dim_region;
-- 2. SELECT * FROM agg_monthly_summary WHERE as_of_date_skey = 20251231 LIMIT 10;
-- 3. Run the verification queries above
-- =============================================================================
