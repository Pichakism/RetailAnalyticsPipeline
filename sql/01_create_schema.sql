-- ============================================================
-- Retail Analytics Pipeline
-- Database Schema
-- ============================================================

-- 1. Dimension: Customers

CREATE TABLE IF NOT EXISTS dim_customers (
    customer_id VARCHAR(20) PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(30),
    city VARCHAR(100),
    signup_date DATE
);


-- 2. Dimension: Categories

CREATE TABLE IF NOT EXISTS dim_categories (
    category_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE
);


-- 3. Dimension: Products

CREATE TABLE IF NOT EXISTS dim_products (
    product_id VARCHAR(20) PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,

    category_id INTEGER NOT NULL,

    unit_cost NUMERIC(12, 2) NOT NULL,
    unit_price NUMERIC(12, 2) NOT NULL,

    CONSTRAINT fk_products_category
        FOREIGN KEY (category_id)
        REFERENCES dim_categories(category_id),

    CONSTRAINT chk_products_unit_cost
        CHECK (unit_cost >= 0),

    CONSTRAINT chk_products_unit_price
        CHECK (unit_price >= 0)
);


-- 4. Dimension: Branches

CREATE TABLE IF NOT EXISTS dim_branches (
    branch_id VARCHAR(20) PRIMARY KEY,
    branch_name VARCHAR(255) NOT NULL,
    city VARCHAR(100)
);


-- 5. Fact: Sales

CREATE TABLE IF NOT EXISTS fact_sales (
    sale_id VARCHAR(30) PRIMARY KEY,

    sale_date DATE NOT NULL,

    customer_id VARCHAR(20) NOT NULL,
    product_id VARCHAR(20) NOT NULL,
    branch_id VARCHAR(20) NOT NULL,

    sales_channel VARCHAR(50),
    quantity INTEGER NOT NULL,
    discount_percent NUMERIC(5, 2),
    payment_method VARCHAR(50),

    CONSTRAINT fk_sales_customer
        FOREIGN KEY (customer_id)
        REFERENCES dim_customers(customer_id),

    CONSTRAINT fk_sales_product
        FOREIGN KEY (product_id)
        REFERENCES dim_products(product_id),

    CONSTRAINT fk_sales_branch
        FOREIGN KEY (branch_id)
        REFERENCES dim_branches(branch_id),

    CONSTRAINT chk_sales_quantity
        CHECK (quantity > 0),

    CONSTRAINT chk_sales_discount
        CHECK (
            discount_percent IS NULL
            OR discount_percent BETWEEN 0 AND 100
        )
);


-- 6. Fact: Inventory Snapshot

CREATE TABLE IF NOT EXISTS fact_inventory_snapshot (
    product_id VARCHAR(20) NOT NULL,
    branch_id VARCHAR(20) NOT NULL,
    snapshot_date DATE NOT NULL,

    stock_quantity INTEGER NOT NULL,
    reorder_level INTEGER NOT NULL,

    CONSTRAINT pk_inventory_snapshot
        PRIMARY KEY (product_id, branch_id, snapshot_date),

    CONSTRAINT fk_inventory_product
        FOREIGN KEY (product_id)
        REFERENCES dim_products(product_id),

    CONSTRAINT fk_inventory_branch
        FOREIGN KEY (branch_id)
        REFERENCES dim_branches(branch_id),

    CONSTRAINT chk_inventory_stock
        CHECK (stock_quantity >= 0),

    CONSTRAINT chk_inventory_reorder_level
        CHECK (reorder_level >= 0)
);