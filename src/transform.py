import pandas as pd

def transform_and_normalize(df):
    """
    Cleans raw data and splits it into 6 normalized DataFrames, 
    matching the database schema and current load.py logic.
    """
    
    # ---------------------------------------------------------
    # 1. Standardizing Text Fields
    # ---------------------------------------------------------
    df['customer_city'] = df['customer_city'].str.title().str.strip()
    df['branch_city'] = df['branch_city'].str.title().str.strip()
    df['payment_method'] = df['payment_method'].str.upper().str.strip()
    df['sales_channel'] = df['sales_channel'].str.lower().str.strip()
    
    # ---------------------------------------------------------
    # 2. Date Parsing (Handling mixed formats)
    # ---------------------------------------------------------
    date_columns = ['sale_date', 'customer_signup_date', 'inventory_snapshot_date']
    for col in date_columns:
        # 'mixed' format allows parsing both slash and dash date formats correctly
        df[col] = pd.to_datetime(df[col], format='mixed', errors='coerce').dt.date

    # ---------------------------------------------------------
    # 3. Generate Category IDs for Product Mapping
    # ---------------------------------------------------------
    # Extract and sort categories so ID assignment matches database auto-increment behavior
    unique_categories = df[['category_name']].dropna().drop_duplicates().sort_values('category_name').reset_index(drop=True)
    unique_categories['category_id'] = unique_categories.index + 1
    
    # Add category_id back to the main dataframe for the products table
    df = df.merge(unique_categories, on='category_name', how='left')

    # ---------------------------------------------------------
    # 4. Extracting Dimension Tables
    # ---------------------------------------------------------
    
    # --- dim_customers ---
    dim_customers = df[[
        'customer_id', 'customer_first_name', 'customer_last_name', 
        'customer_email', 'customer_phone', 'customer_city', 'customer_signup_date'
    ]].copy()
    dim_customers.rename(columns={
        'customer_first_name': 'first_name',
        'customer_last_name': 'last_name',
        'customer_email': 'email',
        'customer_phone': 'phone',
        'customer_city': 'city',
        'customer_signup_date': 'signup_date'
    }, inplace=True)
    dim_customers = dim_customers.drop_duplicates(subset=['customer_id'])

    # --- dim_categories ---
    # Sending only category_name to avoid conflicts with DB identity generation
    dim_categories = unique_categories[['category_name']].copy()

    # --- dim_products ---
    dim_products = df[[
        'product_id', 'product_name', 'category_id', 'unit_cost', 'unit_price'
    ]].copy()
    dim_products = dim_products.drop_duplicates(subset=['product_id'])

    # --- dim_branches ---
    dim_branches = df[[
        'branch_id', 'branch_name', 'branch_city'
    ]].copy()
    dim_branches.rename(columns={'branch_city': 'city'}, inplace=True)
    dim_branches = dim_branches.drop_duplicates(subset=['branch_id'])

    # ---------------------------------------------------------
    # 5. Extracting Fact Tables
    # ---------------------------------------------------------
    
    # --- fact_sales ---
    fact_sales = df[[
        'sale_id', 'sale_date', 'customer_id', 'product_id', 'branch_id', 
        'sales_channel', 'quantity', 'discount_percent', 'payment_method'
    ]].copy()
    fact_sales = fact_sales.drop_duplicates(subset=['sale_id'])

    # --- fact_inventory_snapshot ---
    fact_inventory_snapshot = df[[
        'product_id', 'branch_id', 'inventory_snapshot_date', 
        'stock_quantity', 'reorder_level'
    ]].copy()
    fact_inventory_snapshot.rename(columns={'inventory_snapshot_date': 'snapshot_date'}, inplace=True)
    # Ensure uniqueness for the composite primary key defined in the database schema
    fact_inventory_snapshot = fact_inventory_snapshot.drop_duplicates(subset=['product_id', 'branch_id', 'snapshot_date'])

    # ---------------------------------------------------------
    # 6. Return Outputs
    # ---------------------------------------------------------
    return {
        "dim_customers": dim_customers,
        "dim_categories": dim_categories,
        "dim_products": dim_products,
        "dim_branches": dim_branches,
        "fact_sales": fact_sales,
        "fact_inventory_snapshot": fact_inventory_snapshot
    }
