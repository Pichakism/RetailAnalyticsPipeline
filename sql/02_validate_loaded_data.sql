
-- ============================================================
-- Post-Load Data Validation
-- RetailAnalyticsPipeline
-- ============================================================


-- ============================================================
-- 1. Row Counts
-- ============================================================

SELECT
    'dim_customers' AS table_name,
    COUNT(*) AS row_count
FROM dim_customers

UNION ALL

SELECT
    'dim_categories' AS table_name,
    COUNT(*) AS row_count
FROM dim_categories

UNION ALL

SELECT
    'dim_products' AS table_name,
    COUNT(*) AS row_count
FROM dim_products

UNION ALL

SELECT
    'dim_branches' AS table_name,
    COUNT(*) AS row_count
FROM dim_branches

UNION ALL

SELECT
    'fact_sales' AS table_name,
    COUNT(*) AS row_count
FROM fact_sales

UNION ALL

SELECT
    'fact_inventory_snapshot' AS table_name,
    COUNT(*) AS row_count
FROM fact_inventory_snapshot;


-- ============================================================
-- 2. Duplicate Primary Keys
-- ============================================================

SELECT
    'dim_customers' AS table_name,
    customer_id AS duplicate_key,
    COUNT(*) AS duplicate_count
FROM dim_customers
GROUP BY customer_id
HAVING COUNT(*) > 1

UNION ALL

SELECT
    'dim_products' AS table_name,
    product_id AS duplicate_key,
    COUNT(*) AS duplicate_count
FROM dim_products
GROUP BY product_id
HAVING COUNT(*) > 1

UNION ALL

SELECT
    'dim_branches' AS table_name,
    branch_id AS duplicate_key,
    COUNT(*) AS duplicate_count
FROM dim_branches
GROUP BY branch_id
HAVING COUNT(*) > 1

UNION ALL

SELECT
    'fact_sales' AS table_name,
    sale_id AS duplicate_key,
    COUNT(*) AS duplicate_count
FROM fact_sales
GROUP BY sale_id
HAVING COUNT(*) > 1;


-- ============================================================
-- 3. Foreign Key Validation: Products → Categories
-- ============================================================

SELECT
    COUNT(*) AS invalid_product_category_references
FROM dim_products p
LEFT JOIN dim_categories c
    ON p.category_id = c.category_id
WHERE c.category_id IS NULL;


-- ============================================================
-- 4. Foreign Key Validation: Sales → Customers
-- ============================================================

SELECT
    COUNT(*) AS invalid_sales_customer_references
FROM fact_sales s
LEFT JOIN dim_customers c
    ON s.customer_id = c.customer_id
WHERE c.customer_id IS NULL;


-- ============================================================
-- 5. Foreign Key Validation: Sales → Products
-- ============================================================

SELECT
    COUNT(*) AS invalid_sales_product_references
FROM fact_sales s
LEFT JOIN dim_products p
    ON s.product_id = p.product_id
WHERE p.product_id IS NULL;


-- ============================================================
-- 6. Foreign Key Validation: Sales → Branches
-- ============================================================

SELECT
    COUNT(*) AS invalid_sales_branch_references
FROM fact_sales s
LEFT JOIN dim_branches b
    ON s.branch_id = b.branch_id
WHERE b.branch_id IS NULL;


-- ============================================================
-- 7. Foreign Key Validation: Inventory → Products
-- ============================================================

SELECT
    COUNT(*) AS invalid_inventory_product_references
FROM fact_inventory_snapshot i
LEFT JOIN dim_products p
    ON i.product_id = p.product_id
WHERE p.product_id IS NULL;


-- ============================================================
-- 8. Foreign Key Validation: Inventory → Branches
-- ============================================================

SELECT
    COUNT(*) AS invalid_inventory_branch_references
FROM fact_inventory_snapshot i
LEFT JOIN dim_branches b
    ON i.branch_id = b.branch_id
WHERE b.branch_id IS NULL;


-- ============================================================
-- 9. Required Column NULL Checks
-- ============================================================

SELECT
    'dim_customers.customer_id' AS column_name,
    COUNT(*) AS null_count
FROM dim_customers
WHERE customer_id IS NULL

UNION ALL

SELECT
    'dim_customers.first_name' AS column_name,
    COUNT(*) AS null_count
FROM dim_customers
WHERE first_name IS NULL

UNION ALL

SELECT
    'dim_products.product_id' AS column_name,
    COUNT(*) AS null_count
FROM dim_products
WHERE product_id IS NULL

UNION ALL

SELECT
    'dim_products.unit_cost' AS column_name,
    COUNT(*) AS null_count
FROM dim_products
WHERE unit_cost IS NULL

UNION ALL

SELECT
    'dim_products.unit_price' AS column_name,
    COUNT(*) AS null_count
FROM dim_products
WHERE unit_price IS NULL

UNION ALL

SELECT
    'fact_sales.sale_id' AS column_name,
    COUNT(*) AS null_count
FROM fact_sales
WHERE sale_id IS NULL

UNION ALL

SELECT
    'fact_sales.quantity' AS column_name,
    COUNT(*) AS null_count
FROM fact_sales
WHERE quantity IS NULL;


-- ============================================================
-- 10. Business Rule Validation
-- ============================================================

SELECT
    COUNT(*) AS invalid_sales_quantity
FROM fact_sales
WHERE quantity <= 0;


SELECT
    COUNT(*) AS invalid_sales_discount
FROM fact_sales
WHERE discount_percent < 0
   OR discount_percent > 100;


SELECT
    COUNT(*) AS invalid_product_cost
FROM dim_products
WHERE unit_cost < 0;


SELECT
    COUNT(*) AS invalid_product_price
FROM dim_products
WHERE unit_price < 0;


SELECT
    COUNT(*) AS invalid_inventory_stock
FROM fact_inventory_snapshot
WHERE stock_quantity < 0;


SELECT
    COUNT(*) AS invalid_inventory_reorder_level
FROM fact_inventory_snapshot
WHERE reorder_level < 0;


-- ============================================================
-- 11. Duplicate Inventory Composite Keys
-- ============================================================

SELECT
    product_id,
    branch_id,
    snapshot_date,
    COUNT(*) AS duplicate_count
FROM fact_inventory_snapshot
GROUP BY
    product_id,
    branch_id,
    snapshot_date
HAVING COUNT(*) > 1;