import os
import pandas as pd

# Define paths dynamically
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REJECTED_DATA_DIR = os.path.join(BASE_DIR, "data", "processed", "rejected_records")

def run_quality_checks(tables):
    """
    Validates data quality rules based on project requirements.
    Quarantines invalid records into CSV files and returns a dictionary of valid DataFrames.
    """
    os.makedirs(REJECTED_DATA_DIR, exist_ok=True)
    
    # Extract dataframes for easier reference
    dim_customers = tables["dim_customers"].copy()
    dim_categories = tables["dim_categories"].copy()
    dim_products = tables["dim_products"].copy()
    dim_branches = tables["dim_branches"].copy()
    fact_sales = tables["fact_sales"].copy()
    fact_inventory = tables["fact_inventory_snapshot"].copy()

    valid_tables = {}

    # ---------------------------------------------------------
    # 1. Validate Dimension Tables (Prices, Costs, Null PKs)
    # ---------------------------------------------------------
    # Products validation (no negative prices/costs, must have ID)
    invalid_products_mask = (
        dim_products['product_id'].isnull() |
        (dim_products['unit_price'] < 0) |
        (dim_products['unit_cost'] < 0)
    )
    valid_tables["dim_products"] = dim_products[~invalid_products_mask]
    rejected_products = dim_products[invalid_products_mask]
    
    if not rejected_products.empty:
        rejected_products.to_csv(os.path.join(REJECTED_DATA_DIR, "rejected_products.csv"), index=False)
        print(f"Quarantined {len(rejected_products)} invalid products.")

    # Other dimensions (ensure Primary Keys are not null)
    valid_tables["dim_customers"] = dim_customers[dim_customers['customer_id'].notnull()]
    valid_tables["dim_categories"] = dim_categories[dim_categories['category_name'].notnull()]
    valid_tables["dim_branches"] = dim_branches[dim_branches['branch_id'].notnull()]

    # ---------------------------------------------------------
    # 2. Validate Fact Sales
    # ---------------------------------------------------------
    # Sales validation (positive quantity, valid dates/IDs, and Referential Integrity)
    invalid_sales_mask = (
        fact_sales['sale_id'].isnull() |
        fact_sales['sale_date'].isnull() |
        (fact_sales['quantity'] <= 0) |
        (fact_sales['discount_percent'] < 0) | 
        (fact_sales['discount_percent'] > 100) |
        (~fact_sales['customer_id'].isin(valid_tables["dim_customers"]['customer_id'])) |
        (~fact_sales['product_id'].isin(valid_tables["dim_products"]['product_id'])) |
        (~fact_sales['branch_id'].isin(valid_tables["dim_branches"]['branch_id']))
    )
    valid_tables["fact_sales"] = fact_sales[~invalid_sales_mask]
    rejected_sales = fact_sales[invalid_sales_mask]
    
    if not rejected_sales.empty:
        rejected_sales.to_csv(os.path.join(REJECTED_DATA_DIR, "rejected_sales.csv"), index=False)
        print(f"Quarantined {len(rejected_sales)} invalid sales records.")

    # ---------------------------------------------------------
    # 3. Validate Fact Inventory
    # ---------------------------------------------------------
    # Inventory validation (no negative stock, and Referential Integrity)
    invalid_inventory_mask = (
        fact_inventory['snapshot_date'].isnull() |
        (fact_inventory['stock_quantity'] < 0) |
        (fact_inventory['reorder_level'] < 0) |
        (~fact_inventory['product_id'].isin(valid_tables["dim_products"]['product_id'])) |
        (~fact_inventory['branch_id'].isin(valid_tables["dim_branches"]['branch_id']))
    )
    valid_tables["fact_inventory_snapshot"] = fact_inventory[~invalid_inventory_mask]
    rejected_inventory = fact_inventory[invalid_inventory_mask]
    
    if not rejected_inventory.empty:
        rejected_inventory.to_csv(os.path.join(REJECTED_DATA_DIR, "rejected_inventory.csv"), index=False)
        print(f"Quarantined {len(rejected_inventory)} invalid inventory records.")

    print("Data quality checks completed successfully.")
    return valid_tables
