import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REJECTED_DATA_DIR = os.path.join(BASE_DIR, "data", "processed", "rejected_records")

def _save_rejected_records(df: pd.DataFrame, filename: str) -> None:
    """Save rejected records to the quarantine directory."""
    if df.empty:
        return
    os.makedirs(REJECTED_DATA_DIR, exist_ok=True)
    output_path = os.path.join(REJECTED_DATA_DIR, filename)
    df.to_csv(output_path, index=False)
    print(f"Quarantined {len(df)} records to {output_path}.")

def run_quality_checks(tables: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """Validate data quality rules and quarantine invalid records."""
    os.makedirs(REJECTED_DATA_DIR, exist_ok=True)
    valid_tables = {}

    # Define validation rules: Required columns
    required_cols = {
        "dim_customers": ["customer_id", "first_name", "last_name"],
        "dim_categories": ["category_name"],
        "dim_products": ["product_id", "product_name", "category_id", "unit_cost", "unit_price"],
        "dim_branches": ["branch_id", "branch_name"],
        "fact_sales": ["sale_id", "sale_date", "customer_id", "product_id", "branch_id", "quantity"],
        "fact_inventory_snapshot": ["product_id", "branch_id", "snapshot_date", "stock_quantity", "reorder_level"]
    }

    # Define Primary Keys for duplication checks
    pks = {
        "dim_customers": ["customer_id"],
        "dim_categories": ["category_name"],
        "dim_products": ["product_id"],
        "dim_branches": ["branch_id"],
        "fact_sales": ["sale_id"],
        "fact_inventory_snapshot": ["product_id", "branch_id", "snapshot_date"]
    }

    for table_name, df in tables.items():
        if table_name not in required_cols:
            continue
            
        mask = pd.Series(False, index=df.index)
        
        # 1. Check missing required columns
        existing_cols = [c for c in required_cols[table_name] if c in df.columns]
        if existing_cols:
            mask |= df[existing_cols].isna().any(axis=1)
            
        # 2. Check duplicates
        mask |= df.duplicated(subset=pks[table_name], keep=False)

        # 3. Table specific rules
        if table_name == "dim_products":
            mask |= (df["unit_cost"] < 0) | (df["unit_price"] < 0)
            
        elif table_name == "fact_sales":
            mask |= (df["quantity"] <= 0) | (df["discount_percent"] < 0) | (df["discount_percent"] > 100)
            # Foreign Key Checks
            mask |= ~df["customer_id"].isin(valid_tables["dim_customers"]["customer_id"])
            mask |= ~df["product_id"].isin(valid_tables["dim_products"]["product_id"])
            mask |= ~df["branch_id"].isin(valid_tables["dim_branches"]["branch_id"])

        elif table_name == "fact_inventory_snapshot":
            mask |= (df["stock_quantity"] < 0) | (df["reorder_level"] < 0)
            # Foreign Key Checks
            mask |= ~df["product_id"].isin(valid_tables["dim_products"]["product_id"])
            mask |= ~df["branch_id"].isin(valid_tables["dim_branches"]["branch_id"])

        # Split and save
        rejected = df[mask]
        valid_tables[table_name] = df[~mask].copy()
        _save_rejected_records(rejected, f"rejected_{table_name.replace('dim_', '').replace('fact_', '')}.csv")

    print("\nData quality checks completed successfully.")
    for name, df in valid_tables.items():
        print(f"{name}: {len(df)} valid rows")

    return valid_tables
