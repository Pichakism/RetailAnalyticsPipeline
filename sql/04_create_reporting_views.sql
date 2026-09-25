
-- ============================================================
-- REMOVE PREVIOUS REPORTING VIEWS
-- This operation removes views only and does not delete data
-- from the underlying tables.
-- ============================================================

-- DROP VIEW IF EXISTS
--     reporting_monthly_sales,
--     reporting_product_performance,
--     reporting_branch_performance,
--     reporting_sales_channel_performance,
--     reporting_category_performance,
--     reporting_latest_inventory,
--     reporting_sales_kpis
-- CASCADE;


-- ============================================================
-- REPORTING VIEWS
-- Retail Analytics Pipeline
-- ============================================================


-- 1. Monthly Sales Reporting View

CREATE VIEW reporting_monthly_sales AS
SELECT
    DATE_TRUNC('month', fs.sale_date)::date AS sales_month,
    COUNT(*) AS total_sales,
    SUM(fs.quantity) AS total_quantity,
    ROUND(
        SUM(fs.quantity * dp.unit_price),
        2
    ) AS gross_revenue,
    ROUND(
        SUM(
            fs.quantity * dp.unit_price
            * (1 - COALESCE(fs.discount_percent, 0) / 100)
        ),
        2
    ) AS net_revenue
FROM fact_sales fs
JOIN dim_products dp
    ON fs.product_id = dp.product_id
GROUP BY DATE_TRUNC('month', fs.sale_date)
ORDER BY sales_month;


-- 2. Product Performance Reporting View

CREATE VIEW reporting_product_performance AS
SELECT
    dp.product_id,
    dp.product_name,
    dc.category_name,
    SUM(fs.quantity) AS total_quantity_sold,
    COUNT(*) AS total_sales,
    ROUND(
        SUM(fs.quantity * dp.unit_price),
        2
    ) AS gross_revenue,
    ROUND(
        SUM(
            fs.quantity * dp.unit_price
            * (1 - COALESCE(fs.discount_percent, 0) / 100)
        ),
        2
    ) AS net_revenue
FROM fact_sales fs
JOIN dim_products dp
    ON fs.product_id = dp.product_id
JOIN dim_categories dc
    ON dp.category_id = dc.category_id
GROUP BY
    dp.product_id,
    dp.product_name,
    dc.category_name;


-- 3. Branch Performance Reporting View

CREATE VIEW reporting_branch_performance AS
SELECT
    db.branch_id,
    db.branch_name,
    db.city,
    COUNT(*) AS total_sales,
    SUM(fs.quantity) AS total_quantity_sold,
    ROUND(
        SUM(fs.quantity * dp.unit_price),
        2
    ) AS gross_revenue,
    ROUND(
        SUM(
            fs.quantity * dp.unit_price
            * (1 - COALESCE(fs.discount_percent, 0) / 100)
        ),
        2
    ) AS net_revenue
FROM fact_sales fs
JOIN dim_branches db
    ON fs.branch_id = db.branch_id
JOIN dim_products dp
    ON fs.product_id = dp.product_id
GROUP BY
    db.branch_id,
    db.branch_name,
    db.city;


-- 4. Sales Channel Performance Reporting View

CREATE VIEW reporting_sales_channel_performance AS
SELECT
    fs.sales_channel,
    COUNT(*) AS total_sales,
    SUM(fs.quantity) AS total_quantity_sold,
    ROUND(
        SUM(fs.quantity * dp.unit_price),
        2
    ) AS gross_revenue,
    ROUND(
        SUM(
            fs.quantity * dp.unit_price
            * (1 - COALESCE(fs.discount_percent, 0) / 100)
        ),
        2
    ) AS net_revenue
FROM fact_sales fs
JOIN dim_products dp
    ON fs.product_id = dp.product_id
GROUP BY fs.sales_channel;


-- 5. Category Performance Reporting View

CREATE VIEW reporting_category_performance AS
SELECT
    dc.category_id,
    dc.category_name,
    COUNT(*) AS total_sales,
    SUM(fs.quantity) AS total_quantity_sold,
    ROUND(
        SUM(fs.quantity * dp.unit_price),
        2
    ) AS gross_revenue,
    ROUND(
        SUM(
            fs.quantity * dp.unit_price
            * (1 - COALESCE(fs.discount_percent, 0) / 100)
        ),
        2
    ) AS net_revenue
FROM fact_sales fs
JOIN dim_products dp
    ON fs.product_id = dp.product_id
JOIN dim_categories dc
    ON dp.category_id = dc.category_id
GROUP BY
    dc.category_id,
    dc.category_name;


-- 6. Latest Inventory Reporting View

CREATE VIEW reporting_latest_inventory AS
WITH latest_inventory AS (
    SELECT
        fis.product_id,
        fis.branch_id,
        fis.snapshot_date,
        fis.stock_quantity,
        fis.reorder_level,
        ROW_NUMBER() OVER (
            PARTITION BY fis.product_id, fis.branch_id
            ORDER BY fis.snapshot_date DESC
        ) AS row_number
    FROM fact_inventory_snapshot fis
)
SELECT
    li.product_id,
    dp.product_name,
    li.branch_id,
    db.branch_name,
    li.snapshot_date,
    li.stock_quantity,
    li.reorder_level,
    CASE
        WHEN li.stock_quantity <= li.reorder_level
            THEN 'REORDER_REQUIRED'
        ELSE 'STOCK_AVAILABLE'
    END AS inventory_status
FROM latest_inventory li
JOIN dim_products dp
    ON li.product_id = dp.product_id
JOIN dim_branches db
    ON li.branch_id = db.branch_id
WHERE li.row_number = 1;


-- 7. Sales KPI Reporting View

CREATE VIEW reporting_sales_kpis AS
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
    ON fs.product_id = dp.product_id;