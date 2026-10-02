import pandas as pd

def transform_and_normalize(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Clean raw data and split it into normalized DataFrames."""
    if not isinstance(df, pd.DataFrame) or df.empty:
        raise ValueError("Input must be a non-empty pandas DataFrame.")

    df = df.copy().drop_duplicates(keep="first").reset_index(drop=True)

    # 1. Standardize text columns (Vectorized)
    str_cols = df.select_dtypes(include=['object', 'string']).columns
    for col in str_cols:
        df[col] = df[col].astype("string").str.strip().replace("", pd.NA)

    df["customer_city"] = df["customer_city"].str.title()
    df["branch_city"] = df["branch_city"].str.title()
    df["category_name"] = df["category_name"].str.title()
    df["payment_method"] = df["payment_method"].str.upper()
    df["sales_channel"] = df["sales_channel"].str.lower()

    # 2. Convert date columns
    date_cols = ["sale_date", "customer_signup_date", "inventory_snapshot_date"]
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], format="mixed", errors="coerce").dt.date

    # 3. Convert numeric columns
    num_cols = ["unit_cost", "unit_price", "quantity", "discount_percent", "stock_quantity", "reorder_level"]
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # 4. Create category mapping
    dim_categories = df[["category_name"]].dropna().drop_duplicates().sort_values("category_name").reset_index(drop=True)
    dim_categories["category_id"] = dim_categories.index + 1
    df = df.merge(dim_categories, on="category_name", how="left")

    # 5. Extract Dimensions and Facts
    return {
        "dim_customers": df[[
            "customer_id", "customer_first_name", "customer_last_name", 
            "customer_email", "customer_phone", "customer_city", "customer_signup_date"
        ]].rename(columns=lambda x: x.replace("customer_", "") if x != "customer_id" else x).drop_duplicates(subset=["customer_id"]),
        
        "dim_categories": dim_categories[["category_name"]], # ID gets generated in PostgreSQL
        
        "dim_products": df[[
            "product_id", "product_name", "category_name", "category_id", "unit_cost", "unit_price"
        ]].drop_duplicates(subset=["product_id"]),
        
        "dim_branches": df[[
            "branch_id", "branch_name", "branch_city"
        ]].rename(columns={"branch_city": "city"}).drop_duplicates(subset=["branch_id"]),
        
        "fact_sales": df[[
            "sale_id", "sale_date", "customer_id", "product_id", "branch_id", 
            "sales_channel", "quantity", "discount_percent", "payment_method"
        ]].drop_duplicates(subset=["sale_id"]),
        
        "fact_inventory_snapshot": df[[
            "product_id", "branch_id", "inventory_snapshot_date", "stock_quantity", "reorder_level"
        ]].rename(columns={"inventory_snapshot_date": "snapshot_date"}).drop_duplicates(subset=["product_id", "branch_id", "snapshot_date"])
    }
