
import os

import pandas as pd


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

REJECTED_DATA_DIR = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "rejected_records",
)


def _save_rejected_records(
    dataframe: pd.DataFrame,
    filename: str,
) -> None:
    """Save rejected records to the quarantine directory."""
    if dataframe.empty:
        return

    os.makedirs(
        REJECTED_DATA_DIR,
        exist_ok=True,
    )

    output_path = os.path.join(
        REJECTED_DATA_DIR,
        filename,
    )

    dataframe.to_csv(
        output_path,
        index=False,
    )

    print(
        f"Quarantined {len(dataframe)} records "
        f"to {output_path}."
    )


def _validate_required_columns(
    dataframe: pd.DataFrame,
    columns: list[str],
) -> pd.Series:
    """Return a mask for rows with missing required values."""
    existing_columns = [
        column
        for column in columns
        if column in dataframe.columns
    ]

    if not existing_columns:
        return pd.Series(
            False,
            index=dataframe.index,
        )

    return dataframe[existing_columns].isna().any(
        axis=1
    )


def run_quality_checks(
    tables: dict[str, pd.DataFrame],
) -> dict[str, pd.DataFrame]:
    """
    Validate data quality rules and quarantine invalid records.

    Returns:
        A dictionary containing valid DataFrames.
    """
    os.makedirs(
        REJECTED_DATA_DIR,
        exist_ok=True,
    )

    required_tables = [
        "dim_customers",
        "dim_categories",
        "dim_products",
        "dim_branches",
        "fact_sales",
        "fact_inventory_snapshot",
    ]

    missing_tables = [
        table_name
        for table_name in required_tables
        if table_name not in tables
    ]

    if missing_tables:
        raise KeyError(
            f"Missing required tables: {missing_tables}"
        )

    dim_customers = tables[
        "dim_customers"
    ].copy()

    dim_categories = tables[
        "dim_categories"
    ].copy()

    dim_products = tables[
        "dim_products"
    ].copy()

    dim_branches = tables[
        "dim_branches"
    ].copy()

    fact_sales = tables[
        "fact_sales"
    ].copy()

    fact_inventory = tables[
        "fact_inventory_snapshot"
    ].copy()

    valid_tables = {}

    # 1. Validate Customers
    customer_required_columns = [
        "customer_id",
        "first_name",
        "last_name",
    ]

    invalid_customers_mask = (
        _validate_required_columns(
            dim_customers,
            customer_required_columns,
        )
    )

    invalid_customers_mask |= (
        dim_customers["customer_id"]
        .duplicated(keep=False)
    )

    rejected_customers = dim_customers[
        invalid_customers_mask
    ]

    valid_tables["dim_customers"] = dim_customers[
        ~invalid_customers_mask
    ].copy()

    _save_rejected_records(
        rejected_customers,
        "rejected_customers.csv",
    )

    # 2. Validate Categories
    category_required_columns = [
        "category_name",
    ]

    invalid_categories_mask = (
        _validate_required_columns(
            dim_categories,
            category_required_columns,
        )
    )

    invalid_categories_mask |= (
        dim_categories["category_name"]
        .duplicated(keep=False)
    )

    rejected_categories = dim_categories[
        invalid_categories_mask
    ]

    valid_tables["dim_categories"] = dim_categories[
        ~invalid_categories_mask
    ].copy()

    _save_rejected_records(
        rejected_categories,
        "rejected_categories.csv",
    )

    # 3. Validate Products
    product_required_columns = [
        "product_id",
        "product_name",
        "category_id",
        "unit_cost",
        "unit_price",
    ]

    invalid_products_mask = (
        _validate_required_columns(
            dim_products,
            product_required_columns,
        )
    )

    invalid_products_mask |= (
        dim_products["product_id"]
        .duplicated(keep=False)
    )

    invalid_products_mask |= (
        dim_products["unit_cost"] < 0
    )

    invalid_products_mask |= (
        dim_products["unit_price"] < 0
    )

    rejected_products = dim_products[
        invalid_products_mask
    ]

    valid_tables["dim_products"] = dim_products[
        ~invalid_products_mask
    ].copy()

    _save_rejected_records(
        rejected_products,
        "rejected_products.csv",
    )

    # 4. Validate Branches
    branch_required_columns = [
        "branch_id",
        "branch_name",
    ]

    invalid_branches_mask = (
        _validate_required_columns(
            dim_branches,
            branch_required_columns,
        )
    )

    invalid_branches_mask |= (
        dim_branches["branch_id"]
        .duplicated(keep=False)
    )

    rejected_branches = dim_branches[
        invalid_branches_mask
    ]

    valid_tables["dim_branches"] = dim_branches[
        ~invalid_branches_mask
    ].copy()

    _save_rejected_records(
        rejected_branches,
        "rejected_branches.csv",
    )

    # 5. Validate Sales
    sales_required_columns = [
        "sale_id",
        "sale_date",
        "customer_id",
        "product_id",
        "branch_id",
        "quantity",
    ]

    invalid_sales_mask = (
        _validate_required_columns(
            fact_sales,
            sales_required_columns,
        )
    )

    invalid_sales_mask |= (
        fact_sales["sale_id"]
        .duplicated(keep=False)
    )

    invalid_sales_mask |= (
        fact_sales["quantity"] <= 0
    )

    invalid_sales_mask |= (
        fact_sales["discount_percent"] < 0
    )

    invalid_sales_mask |= (
        fact_sales["discount_percent"] > 100
    )

    invalid_sales_mask |= ~(
        fact_sales["customer_id"].isin(
            valid_tables["dim_customers"][
                "customer_id"
            ]
        )
    )

    invalid_sales_mask |= ~(
        fact_sales["product_id"].isin(
            valid_tables["dim_products"][
                "product_id"
            ]
        )
    )

    invalid_sales_mask |= ~(
        fact_sales["branch_id"].isin(
            valid_tables["dim_branches"][
                "branch_id"
            ]
        )
    )

    rejected_sales = fact_sales[
        invalid_sales_mask
    ]

    valid_tables["fact_sales"] = fact_sales[
        ~invalid_sales_mask
    ].copy()

    _save_rejected_records(
        rejected_sales,
        "rejected_sales.csv",
    )

    # 6. Validate Inventory Snapshots
    inventory_required_columns = [
        "product_id",
        "branch_id",
        "snapshot_date",
        "stock_quantity",
        "reorder_level",
    ]

    invalid_inventory_mask = (
        _validate_required_columns(
            fact_inventory,
            inventory_required_columns,
        )
    )

    invalid_inventory_mask |= (
        fact_inventory["stock_quantity"] < 0
    )

    invalid_inventory_mask |= (
        fact_inventory["reorder_level"] < 0
    )

    invalid_inventory_mask |= ~(
        fact_inventory["product_id"].isin(
            valid_tables["dim_products"][
                "product_id"
            ]
        )
    )

    invalid_inventory_mask |= ~(
        fact_inventory["branch_id"].isin(
            valid_tables["dim_branches"][
                "branch_id"
            ]
        )
    )

    inventory_key_columns = [
        "product_id",
        "branch_id",
        "snapshot_date",
    ]

    invalid_inventory_mask |= (
        fact_inventory[
            inventory_key_columns
        ].duplicated(keep=False)
    )

    rejected_inventory = fact_inventory[
        invalid_inventory_mask
    ]

    valid_tables["fact_inventory_snapshot"] = (
        fact_inventory[
            ~invalid_inventory_mask
        ].copy()
    )

    _save_rejected_records(
        rejected_inventory,
        "rejected_inventory.csv",
    )

    # 7. Print Summary
    print(
        "Data quality checks completed successfully."
    )

    for table_name, dataframe in valid_tables.items():
        print(
            f"{table_name}: "
            f"{len(dataframe)} valid rows"
        )

    return valid_tables