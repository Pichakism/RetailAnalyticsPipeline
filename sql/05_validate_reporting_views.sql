
-- ============================================================
-- REPORTING VIEWS VALIDATION
-- Retail Analytics Pipeline
--
-- Purpose:
-- This script validates the reporting views created for the
-- Retail Analytics Pipeline.
--
-- The validation includes:
-- 1. Reporting view existence
-- 2. Reporting view row counts
-- 3. Monthly sales coverage
-- 4. Product performance aggregation
-- 5. Branch performance aggregation
-- 6. Sales channel aggregation
-- 7. Category performance aggregation
-- 8. Latest inventory status distribution
-- 9. Sales KPI consistency
-- 10. Negative values in reporting results
-- ============================================================


-- ============================================================
-- 1. REPORTING VIEW EXISTENCE
--
-- This query lists all reporting views in the public schema.
--
-- The reporting layer is expected to contain seven views:
-- monthly sales, product performance, branch performance,
-- sales channel performance, category performance,
-- latest inventory, and sales KPIs.
--
-- This check confirms that the expected views are available
-- in the database.
-- ============================================================

\echo ''
\echo '============================================================'
\echo '1. REPORTING VIEW EXISTENCE'
\echo '============================================================'
\echo 'This section lists all reporting views in the public schema.'
\echo ''

SELECT
    table_schema,
    table_name
FROM information_schema.views
WHERE table_schema = 'public'
  AND table_name LIKE 'reporting_%'
ORDER BY table_name;


-- ============================================================
-- 2. REPORTING VIEW ROW COUNTS
--
-- This query displays the number of records returned by
-- each reporting view.
--
-- Row counts help confirm that the views are not unexpectedly
-- empty and provide a basic overview of the reporting layer.
--
-- Different views naturally have different row counts:
-- monthly sales is grouped by month, product performance is
-- grouped by product, and branch performance is grouped
-- by branch.
-- ============================================================

\echo ''
\echo '============================================================'
\echo '2. REPORTING VIEW ROW COUNTS'
\echo '============================================================'
\echo 'This section displays the number of records returned'
\echo 'by each reporting view.'
\echo ''

SELECT
    'reporting_monthly_sales' AS view_name,
    COUNT(*) AS row_count
FROM reporting_monthly_sales

UNION ALL

SELECT
    'reporting_product_performance' AS view_name,
    COUNT(*) AS row_count
FROM reporting_product_performance

UNION ALL

SELECT
    'reporting_branch_performance' AS view_name,
    COUNT(*) AS row_count
FROM reporting_branch_performance

UNION ALL

SELECT
    'reporting_sales_channel_performance' AS view_name,
    COUNT(*) AS row_count
FROM reporting_sales_channel_performance

UNION ALL

SELECT
    'reporting_category_performance' AS view_name,
    COUNT(*) AS row_count
FROM reporting_category_performance

UNION ALL

SELECT
    'reporting_latest_inventory' AS view_name,
    COUNT(*) AS row_count
FROM reporting_latest_inventory

UNION ALL

SELECT
    'reporting_sales_kpis' AS view_name,
    COUNT(*) AS row_count
FROM reporting_sales_kpis

ORDER BY view_name;


-- ============================================================
-- 3. MONTHLY SALES VIEW VALIDATION
--
-- This query checks the reporting period covered by the
-- monthly sales view.
--
-- The result includes the number of reporting months,
-- the first month, the last month, total transactions,
-- total quantity, gross revenue, and net revenue.
--
-- This check helps confirm that the monthly aggregation
-- covers the expected period and contains meaningful values.
-- ============================================================

\echo ''
\echo '============================================================'
\echo '3. MONTHLY SALES VIEW VALIDATION'
\echo '============================================================'
\echo 'This section checks the reporting period and aggregated'
\echo 'values in the monthly sales view.'
\echo ''

SELECT
    COUNT(*) AS month_count,
    MIN(sales_month) AS first_month,
    MAX(sales_month) AS last_month,
    SUM(total_sales) AS total_sales,
    SUM(total_quantity) AS total_quantity,
    ROUND(SUM(gross_revenue), 2) AS total_gross_revenue,
    ROUND(SUM(net_revenue), 2) AS total_net_revenue
FROM reporting_monthly_sales;


-- ============================================================
-- 4. PRODUCT PERFORMANCE VIEW VALIDATION
--
-- This query checks the number of rows and unique products
-- in the product performance view.
--
-- The view is expected to contain one aggregated record
-- for each product that appears in the sales data.
--
-- The duplicate difference should be zero when each product
-- appears only once in the reporting result.
-- ============================================================

\echo ''
\echo '============================================================'
\echo '4. PRODUCT PERFORMANCE VIEW VALIDATION'
\echo '============================================================'
\echo 'This section checks product-level aggregation and duplicate rows.'
\echo ''

SELECT
    COUNT(*) AS total_rows,
    COUNT(DISTINCT product_id) AS unique_products,
    COUNT(*) - COUNT(DISTINCT product_id) AS duplicate_row_difference
FROM reporting_product_performance;


-- ============================================================
-- 5. BRANCH PERFORMANCE VIEW VALIDATION
--
-- This query checks the number of rows and unique branches
-- in the branch performance view.
--
-- The view is expected to contain one aggregated record
-- for each branch represented in the sales data.
--
-- The duplicate difference should be zero when each branch
-- appears only once in the reporting result.
-- ============================================================

\echo ''
\echo '============================================================'
\echo '5. BRANCH PERFORMANCE VIEW VALIDATION'
\echo '============================================================'
\echo 'This section checks branch-level aggregation and duplicate rows.'
\echo ''

SELECT
    COUNT(*) AS total_rows,
    COUNT(DISTINCT branch_id) AS unique_branches,
    COUNT(*) - COUNT(DISTINCT branch_id) AS duplicate_row_difference
FROM reporting_branch_performance;


-- ============================================================
-- 6. SALES CHANNEL PERFORMANCE VIEW VALIDATION
--
-- This query checks the number of sales channels and identifies
-- possible NULL values in the sales channel column.
--
-- Each available sales channel is expected to appear once
-- in the aggregated reporting view.
--
-- A NULL channel value may indicate incomplete source data
-- and should be investigated if it appears.
-- ============================================================

\echo ''
\echo '============================================================'
\echo '6. SALES CHANNEL PERFORMANCE VIEW VALIDATION'
\echo '============================================================'
\echo 'This section checks sales channel aggregation and NULL values.'
\echo ''

SELECT
    COUNT(*) AS total_rows,
    COUNT(DISTINCT sales_channel) AS unique_channels,
    COUNT(*) FILTER (
        WHERE sales_channel IS NULL
    ) AS null_channel_count
FROM reporting_sales_channel_performance;


-- ============================================================
-- 7. CATEGORY PERFORMANCE VIEW VALIDATION
--
-- This query checks the number of rows and unique categories
-- in the category performance view.
--
-- The view is expected to contain one aggregated record
-- for each category represented in the sales data.
--
-- The duplicate difference should be zero when each category
-- appears only once in the reporting result.
-- ============================================================

\echo ''
\echo '============================================================'
\echo '7. CATEGORY PERFORMANCE VIEW VALIDATION'
\echo '============================================================'
\echo 'This section checks category-level aggregation and duplicate rows.'
\echo ''

SELECT
    COUNT(*) AS total_rows,
    COUNT(DISTINCT category_id) AS unique_categories,
    COUNT(*) - COUNT(DISTINCT category_id) AS duplicate_row_difference
FROM reporting_category_performance;


-- ============================================================
-- 8. LATEST INVENTORY VIEW VALIDATION
--
-- This query summarizes the inventory status distribution
-- in the latest inventory reporting view.
--
-- The view contains the latest available inventory record
-- for each product and branch combination.
--
-- The result groups records by inventory status and shows
-- the number of records, total stock quantity, average stock,
-- and average reorder level.
--
-- This is a summary validation query, so it does not display
-- every individual inventory record.
-- ============================================================

\echo ''
\echo '============================================================'
\echo '8. LATEST INVENTORY VIEW VALIDATION'
\echo '============================================================'
\echo 'This section summarizes the latest inventory status distribution.'
\echo ''

SELECT
    inventory_status,
    COUNT(*) AS inventory_record_count,
    SUM(stock_quantity) AS total_stock_quantity,
    ROUND(AVG(stock_quantity), 2) AS average_stock_quantity,
    ROUND(AVG(reorder_level), 2) AS average_reorder_level
FROM reporting_latest_inventory
GROUP BY inventory_status
ORDER BY inventory_status;


-- ============================================================
-- 9. SALES KPI VALIDATION
--
-- This query compares the KPI values in the reporting view
-- with values calculated directly from the source tables.
--
-- The comparison checks transaction count, quantity sold,
-- unique customers, unique products, active branches,
-- total net revenue, and average sale value.
--
-- Each *_match column returns TRUE when the value in the
-- reporting view matches the value calculated from the
-- source tables.
--
-- This check helps confirm that the reporting KPI view
-- correctly represents the underlying sales data.
-- ============================================================

\echo ''
\echo '============================================================'
\echo '9. SALES KPI VALIDATION'
\echo '============================================================'
\echo 'This section compares reporting KPI values with source table calculations.'
\echo ''

WITH source_kpis AS (
    SELECT
        COUNT(*) AS total_sales,
        SUM(fs.quantity) AS total_quantity_sold,
        COUNT(DISTINCT fs.customer_id) AS unique_customers,
        COUNT(DISTINCT fs.product_id) AS unique_products,
        COUNT(DISTINCT fs.branch_id) AS active_branches,
        ROUND(
            SUM(
                fs.quantity * dp.unit_price
                * (1 - COALESCE(fs.discount_percent, 0) / 100)
            ),
            2
        ) AS total_net_revenue,
        ROUND(
            SUM(
                fs.quantity * dp.unit_price
                * (1 - COALESCE(fs.discount_percent, 0) / 100)
            ) / COUNT(*),
            2
        ) AS average_sale_value
    FROM fact_sales fs
    JOIN dim_products dp
        ON fs.product_id = dp.product_id
)
SELECT
    rv.total_sales AS view_total_sales,
    sk.total_sales AS source_total_sales,
    rv.total_sales = sk.total_sales AS total_sales_match,

    rv.total_quantity_sold AS view_total_quantity_sold,
    sk.total_quantity_sold AS source_total_quantity_sold,
    rv.total_quantity_sold = sk.total_quantity_sold
        AS total_quantity_match,

    rv.unique_customers AS view_unique_customers,
    sk.unique_customers AS source_unique_customers,
    rv.unique_customers = sk.unique_customers
        AS unique_customers_match,

    rv.unique_products AS view_unique_products,
    sk.unique_products AS source_unique_products,
    rv.unique_products = sk.unique_products
        AS unique_products_match,

    rv.active_branches AS view_active_branches,
    sk.active_branches AS source_active_branches,
    rv.active_branches = sk.active_branches
        AS active_branches_match,

    rv.total_net_revenue AS view_total_net_revenue,
    sk.total_net_revenue AS source_total_net_revenue,
    rv.total_net_revenue = sk.total_net_revenue
        AS total_net_revenue_match,

    rv.average_sale_value AS view_average_sale_value,
    sk.average_sale_value AS source_average_sale_value,
    rv.average_sale_value = sk.average_sale_value
        AS average_sale_value_match

FROM reporting_sales_kpis rv
CROSS JOIN source_kpis sk;


-- ============================================================
-- 10. NEGATIVE VALUES IN REPORTING RESULTS
--
-- This query checks for negative quantity and revenue values
-- in product, branch, and category reporting views.
--
-- The data quality layer already filters invalid quantities
-- and negative product prices. Therefore, negative aggregated
-- values would indicate a potential data or calculation issue.
--
-- The expected result should contain zero rows for all
-- negative-value counters.
-- ============================================================

\echo ''
\echo '============================================================'
\echo '10. NEGATIVE VALUES IN REPORTING RESULTS'
\echo '============================================================'
\echo 'This section checks for negative quantity and revenue values.'
\echo ''

SELECT
    'product_performance' AS report_name,
    COUNT(*) FILTER (
        WHERE total_quantity_sold < 0
    ) AS negative_quantity_rows,
    COUNT(*) FILTER (
        WHERE gross_revenue < 0
    ) AS negative_gross_revenue_rows,
    COUNT(*) FILTER (
        WHERE net_revenue < 0
    ) AS negative_net_revenue_rows
FROM reporting_product_performance

UNION ALL

SELECT
    'branch_performance' AS report_name,
    COUNT(*) FILTER (
        WHERE total_quantity_sold < 0
    ) AS negative_quantity_rows,
    COUNT(*) FILTER (
        WHERE gross_revenue < 0
    ) AS negative_gross_revenue_rows,
    COUNT(*) FILTER (
        WHERE net_revenue < 0
    ) AS negative_net_revenue_rows
FROM reporting_branch_performance

UNION ALL

SELECT
    'category_performance' AS report_name,
    COUNT(*) FILTER (
        WHERE total_quantity_sold < 0
    ) AS negative_quantity_rows,
    COUNT(*) FILTER (
        WHERE gross_revenue < 0
    ) AS negative_gross_revenue_rows,
    COUNT(*) FILTER (
        WHERE net_revenue < 0
    ) AS negative_net_revenue_rows
FROM reporting_category_performance;