
-- ============================================================
-- BUSINESS ANALYSIS QUERIES
-- Retail Analytics Pipeline
--
-- Purpose:
-- This script provides analytical queries for evaluating sales,
-- products, branches, customers, inventory, and business KPIs.
--
-- Each section contains an explanation of the business purpose
-- of the query before displaying its results.
-- ============================================================


-- ============================================================
-- 1. MONTHLY SALES PERFORMANCE
--
-- This analysis examines how sales performance changes over time.
-- Transactions are grouped by month, allowing the business to
-- compare sales volume and revenue across different periods.
--
-- total_sales represents the number of sales transactions.
-- total_quantity represents the total number of items sold.
-- gross_revenue represents revenue before discounts.
-- net_revenue represents revenue after applying discounts.
--
-- This report can be used to identify monthly sales trends,
-- periods of higher activity, and changes in revenue.
-- ============================================================

\echo ''
\echo '============================================================'
\echo '1. MONTHLY SALES PERFORMANCE'
\echo '============================================================'
\echo 'This report shows monthly sales volume, quantity, gross revenue,'
\echo 'and net revenue. Gross revenue is calculated before discounts,'
\echo 'while net revenue is calculated after applying discounts.'
\echo ''

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


-- ============================================================
-- 2. TOP 20 PRODUCTS BY QUANTITY SOLD
--
-- This analysis identifies the products with the highest sales
-- quantity across the entire dataset.
--
-- The report includes the product identifier, product name,
-- category, total quantity sold, and number of transactions.
--
-- A high quantity sold indicates that a product has been sold
-- frequently or in large quantities. However, quantity alone
-- does not represent profitability or total revenue.
--
-- This report is useful for understanding product demand
-- and identifying frequently purchased products.
-- ============================================================

\echo ''
\echo '============================================================'
\echo '2. TOP 20 PRODUCTS BY QUANTITY SOLD'
\echo '============================================================'
\echo 'This report identifies the 20 products with the highest'
\echo 'total quantity sold across all sales transactions.'
\echo ''

SELECT
    dp.product_id,
    dp.product_name,
    dc.category_name,
    SUM(fs.quantity) AS total_quantity_sold,
    COUNT(*) AS total_sales
FROM fact_sales fs
JOIN dim_products dp
    ON fs.product_id = dp.product_id
JOIN dim_categories dc
    ON dp.category_id = dc.category_id
GROUP BY
    dp.product_id,
    dp.product_name,
    dc.category_name
ORDER BY total_quantity_sold DESC
LIMIT 20;


-- ============================================================
-- 3. TOP 20 PRODUCTS BY NET REVENUE
--
-- This analysis identifies the products that generate the
-- highest total net revenue.
--
-- Net revenue is calculated by multiplying the quantity sold
-- by the product unit price and subtracting the applicable
-- discount percentage.
--
-- This report is different from the quantity-based product
-- ranking because a product with fewer sales may generate
-- more revenue due to its higher unit price.
--
-- The result helps identify products that contribute
-- significantly to the total business revenue.
-- ============================================================

\echo ''
\echo '============================================================'
\echo '3. TOP 20 PRODUCTS BY NET REVENUE'
\echo '============================================================'
\echo 'This report identifies the 20 products generating the highest'
\echo 'net revenue after applying the recorded discounts.'
\echo ''

SELECT
    dp.product_id,
    dp.product_name,
    dc.category_name,
    SUM(fs.quantity) AS total_quantity_sold,
    COUNT(*) AS total_sales,
    ROUND(
        SUM(
            fs.quantity * dp.unit_price
            * (1 - COALESCE(fs.discount_percent, 0) / 100)
        ),
        2
    ) AS total_net_revenue
FROM fact_sales fs
JOIN dim_products dp
    ON fs.product_id = dp.product_id
JOIN dim_categories dc
    ON dp.category_id = dc.category_id
GROUP BY
    dp.product_id,
    dp.product_name,
    dc.category_name
ORDER BY total_net_revenue DESC
LIMIT 20;


-- ============================================================
-- 4. BRANCH PERFORMANCE
--
-- This analysis compares the performance of the different
-- branches in the retail business.
--
-- The report includes transaction count, quantity sold,
-- gross revenue, and net revenue for each branch.
--
-- Comparing branches helps identify differences in sales
-- activity and revenue generation between locations.
--
-- The results can support further investigation into branch
-- performance, customer demand, and sales distribution.
-- ============================================================

\echo ''
\echo '============================================================'
\echo '4. BRANCH PERFORMANCE'
\echo '============================================================'
\echo 'This report compares branches using transaction count,'
\echo 'quantity sold, gross revenue, and net revenue.'
\echo ''

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
    db.city
ORDER BY net_revenue DESC;


-- ============================================================
-- 5. SALES CHANNEL PERFORMANCE
--
-- This analysis compares sales performance across the available
-- sales channels.
--
-- The report calculates the number of transactions, quantity sold,
-- gross revenue, and net revenue for each sales channel.
--
-- The results help explain how sales are distributed between
-- different channels and how much revenue each channel generates.
-- ============================================================

\echo ''
\echo '============================================================'
\echo '5. SALES CHANNEL PERFORMANCE'
\echo '============================================================'
\echo 'This report compares sales volume and revenue across'
\echo 'the available sales channels.'
\echo ''

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
GROUP BY fs.sales_channel
ORDER BY net_revenue DESC;


-- ============================================================
-- 6. PAYMENT METHOD ANALYSIS
--
-- This analysis examines the distribution of transactions
-- across different payment methods.
--
-- The report includes transaction count, quantity sold,
-- and net revenue for each payment method.
--
-- This information can help the business understand customer
-- payment preferences and the contribution of each payment
-- method to total sales revenue.
-- ============================================================

\echo ''
\echo '============================================================'
\echo '6. PAYMENT METHOD ANALYSIS'
\echo '============================================================'
\echo 'This report shows transaction volume, quantity sold,'
\echo 'and net revenue for each payment method.'
\echo ''

SELECT
    fs.payment_method,
    COUNT(*) AS total_sales,
    SUM(fs.quantity) AS total_quantity_sold,
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
GROUP BY fs.payment_method
ORDER BY net_revenue DESC;


-- ============================================================
-- 7. CATEGORY PERFORMANCE
--
-- This analysis evaluates sales performance at the product
-- category level.
--
-- The report includes transaction count, quantity sold,
-- gross revenue, and net revenue for each category.
--
-- Category-level analysis provides a broader view than
-- individual product analysis and helps identify categories
-- that contribute significantly to sales and revenue.
-- ============================================================

\echo ''
\echo '============================================================'
\echo '7. CATEGORY PERFORMANCE'
\echo '============================================================'
\echo 'This report compares sales volume and revenue across'
\echo 'the available product categories.'
\echo ''

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
    dc.category_name
ORDER BY net_revenue DESC;


-- ============================================================
-- 8. INVENTORY STATUS SUMMARY
--
-- This analysis evaluates the latest inventory condition for
-- each product and branch combination.
--
-- The source inventory table may contain multiple snapshots
-- for the same product and branch. Therefore, the query first
-- selects the most recent snapshot for each combination.
--
-- An inventory record is classified as REORDER_REQUIRED when
-- the current stock quantity is less than or equal to the
-- reorder level.
--
-- Otherwise, the record is classified as STOCK_AVAILABLE.
--
-- Instead of displaying a very large list of individual
-- inventory records, this report summarizes the inventory
-- condition using record count, total stock, average stock,
-- and average reorder level.
-- ============================================================

\echo ''
\echo '============================================================'
\echo '8. INVENTORY STATUS SUMMARY'
\echo '============================================================'
\echo 'This report summarizes the latest inventory status for'
\echo 'product and branch combinations.'
\echo 'It groups records into reorder-required and stock-available'
\echo 'categories instead of displaying every inventory record.'
\echo ''

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
    CASE
        WHEN stock_quantity <= reorder_level
            THEN 'REORDER_REQUIRED'
        ELSE 'STOCK_AVAILABLE'
    END AS inventory_status,
    COUNT(*) AS inventory_record_count,
    SUM(stock_quantity) AS total_stock_quantity,
    ROUND(AVG(stock_quantity), 2) AS average_stock_quantity,
    ROUND(AVG(reorder_level), 2) AS average_reorder_level
FROM latest_inventory
WHERE row_number = 1
GROUP BY
    CASE
        WHEN stock_quantity <= reorder_level
            THEN 'REORDER_REQUIRED'
        ELSE 'STOCK_AVAILABLE'
    END
ORDER BY inventory_status;


-- ============================================================
-- 9. REORDER REQUIREMENTS BY BRANCH
--
-- This analysis identifies branches that have products
-- requiring replenishment.
--
-- The query selects the latest inventory snapshot for each
-- product and branch combination.
--
-- A product is considered to require replenishment when its
-- latest stock quantity is less than or equal to the reorder
-- level.
--
-- The result is grouped by branch to avoid producing a very
-- large detailed table. It shows the number of products
-- requiring reorder, total current stock, and average stock
-- for each affected branch.
--
-- This report is useful for identifying branches that may
-- require inventory management attention.
-- ============================================================

\echo ''
\echo '============================================================'
\echo '9. REORDER REQUIREMENTS BY BRANCH'
\echo '============================================================'
\echo 'This report summarizes products requiring replenishment'
\echo 'for each branch.'
\echo 'It shows the number of affected products and their current stock.'
\echo ''

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
    db.branch_id,
    db.branch_name,
    db.city,
    COUNT(*) AS products_requiring_reorder,
    SUM(li.stock_quantity) AS total_current_stock,
    ROUND(AVG(li.stock_quantity), 2) AS average_current_stock
FROM latest_inventory li
JOIN dim_branches db
    ON li.branch_id = db.branch_id
WHERE li.row_number = 1
  AND li.stock_quantity <= li.reorder_level
GROUP BY
    db.branch_id,
    db.branch_name,
    db.city
ORDER BY
    products_requiring_reorder DESC,
    db.branch_id;


-- ============================================================
-- 10. CUSTOMER DISTRIBUTION BY CITY
--
-- This analysis shows how customers are distributed across
-- different cities.
--
-- The report counts the number of customers registered in
-- each city and orders the result by customer count.
--
-- This information provides a basic overview of the geographical
-- distribution of the customer base.
--
-- The result describes customer registration distribution,
-- not actual purchase activity.
-- ============================================================

\echo ''
\echo '============================================================'
\echo '10. CUSTOMER DISTRIBUTION BY CITY'
\echo '============================================================'
\echo 'This report shows the number of registered customers'
\echo 'in each city.'
\echo ''

SELECT
    city,
    COUNT(*) AS customer_count
FROM dim_customers
GROUP BY city
ORDER BY customer_count DESC, city;


-- ============================================================
-- 11. SALES BY CUSTOMER CITY
--
-- This analysis examines sales performance based on the city
-- associated with each customer.
--
-- The report includes transaction count, quantity sold,
-- number of unique customers, and net revenue.
--
-- Unlike the previous customer distribution analysis, this
-- query focuses on purchasing activity rather than registration.
--
-- The result helps identify cities contributing to sales
-- volume and revenue.
-- ============================================================

\echo ''
\echo '============================================================'
\echo '11. SALES BY CUSTOMER CITY'
\echo '============================================================'
\echo 'This report compares sales activity and net revenue'
\echo 'based on customer city.'
\echo ''

SELECT
    dc.city,
    COUNT(*) AS total_sales,
    SUM(fs.quantity) AS total_quantity_sold,
    COUNT(DISTINCT fs.customer_id) AS unique_customers,
    ROUND(
        SUM(
            fs.quantity * dp.unit_price
            * (1 - COALESCE(fs.discount_percent, 0) / 100)
        ),
        2
    ) AS net_revenue
FROM fact_sales fs
JOIN dim_customers dc
    ON fs.customer_id = dc.customer_id
JOIN dim_products dp
    ON fs.product_id = dp.product_id
GROUP BY dc.city
ORDER BY net_revenue DESC;


-- ============================================================
-- 12. OVERALL SALES KPIs
--
-- This analysis calculates the main overall performance
-- indicators for the loaded sales dataset.
--
-- total_sales represents the number of valid sales transactions.
-- total_quantity_sold represents the total number of items sold.
-- unique_customers represents the number of customers involved
-- in the sales transactions.
-- unique_products represents the number of products sold.
-- active_branches represents the number of branches involved
-- in the sales transactions.
-- total_net_revenue represents revenue after discounts.
-- average_sale_value represents total net revenue divided
-- by the number of sales transactions.
--
-- These indicators provide a high-level overview of the
-- business performance and can be used in reporting dashboards.
-- ============================================================

\echo ''
\echo '============================================================'
\echo '12. OVERALL SALES KPIs'
\echo '============================================================'
\echo 'This report presents the main overall sales performance indicators.'
\echo 'It includes transaction count, quantity sold, unique customers,'
\echo 'unique products, active branches, total net revenue,'
\echo 'and average sale value.'
\echo ''

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