
import pandas as pd


def _clean_text_column(
    df: pd.DataFrame,
    column: str,
    case: str = "original",
) -> None:
    """Clean a text column in place."""
    if column not in df.columns:
        return

    df[column] = df[column].astype("string").str.strip()

    if case == "lower":
        df[column] = df[column].str.lower()
    elif case == "upper":
        df[column] = df[column].str.upper()
    elif case == "title":
        df[column] = df[column].str.title()

    df[column] = df[column].replace("", pd.NA)


def _convert_numeric_columns(
    df: pd.DataFrame,
    columns: list[str],
) -> None:
    """Convert specified columns to numeric values in place."""
    for column in columns:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce",
            )


def _convert_date_columns(
    df: pd.DataFrame,
    columns: list[str],
) -> None:
    """Convert date columns and invalid values to Python date objects."""
    for column in columns:
        if column not in df.columns:
            continue

        parsed_dates = pd.to_datetime(
            df[column],
            format="mixed",
            errors="coerce",
        )

        df[column] = parsed_dates.dt.date


def _create_category_mapping(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Create a category mapping and add category_id to the main DataFrame.

    The generated category_id values are temporary transformation-level
    identifiers. They must be mapped to the actual PostgreSQL category_id
    values during the database loading stage.
    """
    unique_categories = (
        df[["category_name"]]
        .dropna(subset=["category_name"])
        .drop_duplicates()
        .sort_values("category_name")
        .reset_index(drop=True)
    )

    unique_categories["category_id"] = (
        unique_categories.index + 1
    )

    df = df.merge(
        unique_categories,
        on="category_name",
        how="left",
    )

    dim_categories = unique_categories[
        ["category_name"]
    ].copy()

    return df, dim_categories


def _create_customer_dimension(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Create the customer dimension."""
    dim_customers = df[
        [
            "customer_id",
            "customer_first_name",
            "customer_last_name",
            "customer_email",
            "customer_phone",
            "customer_city",
            "customer_signup_date",
        ]
    ].copy()

    dim_customers = dim_customers.rename(
        columns={
            "customer_first_name": "first_name",
            "customer_last_name": "last_name",
            "customer_email": "email",
            "customer_phone": "phone",
            "customer_city": "city",
            "customer_signup_date": "signup_date",
        }
    )

    dim_customers = dim_customers.drop_duplicates(
        subset=["customer_id"],
        keep="first",
    )

    return dim_customers


def _create_category_dimension(
    dim_categories: pd.DataFrame,
) -> pd.DataFrame:
    """Create the category dimension."""
    return dim_categories[
        ["category_name"]
    ].drop_duplicates(
        subset=["category_name"],
        keep="first",
    ).reset_index(drop=True)


def _create_product_dimension(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Create the product dimension."""
    dim_products = df[
        [
            "product_id",
            "product_name",
            "category_name",
            "category_id",
            "unit_cost",
            "unit_price",
        ]
    ].copy()

    dim_products = dim_products.drop_duplicates(
        subset=["product_id"],
        keep="first",
    )

    return dim_products


def _create_branch_dimension(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Create the branch dimension."""
    dim_branches = df[
        [
            "branch_id",
            "branch_name",
            "branch_city",
        ]
    ].copy()

    dim_branches = dim_branches.rename(
        columns={
            "branch_city": "city",
        }
    )

    dim_branches = dim_branches.drop_duplicates(
        subset=["branch_id"],
        keep="first",
    )

    return dim_branches


def _create_sales_fact(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Create the sales fact table."""
    fact_sales = df[
        [
            "sale_id",
            "sale_date",
            "customer_id",
            "product_id",
            "branch_id",
            "sales_channel",
            "quantity",
            "discount_percent",
            "payment_method",
        ]
    ].copy()

    fact_sales = fact_sales.drop_duplicates(
        subset=["sale_id"],
        keep="first",
    )

    return fact_sales


def _create_inventory_fact(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Create the inventory snapshot fact table."""
    fact_inventory_snapshot = df[
        [
            "product_id",
            "branch_id",
            "inventory_snapshot_date",
            "stock_quantity",
            "reorder_level",
        ]
    ].copy()

    fact_inventory_snapshot = (
        fact_inventory_snapshot.rename(
            columns={
                "inventory_snapshot_date": "snapshot_date",
            }
        )
    )

    fact_inventory_snapshot = (
        fact_inventory_snapshot.drop_duplicates(
            subset=[
                "product_id",
                "branch_id",
                "snapshot_date",
            ],
            keep="first",
        )
    )

    return fact_inventory_snapshot


def transform_and_normalize(
    df: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    """
    Clean raw data and split it into six normalized DataFrames.

    Returned tables:
        - dim_customers
        - dim_categories
        - dim_products
        - dim_branches
        - fact_sales
        - fact_inventory_snapshot

    Invalid records are not quarantined in this function.
    They are passed to the quality-checking stage.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError(
            "The input must be a pandas DataFrame."
        )

    if df.empty:
        raise ValueError(
            "The input DataFrame is empty."
        )

    df = df.copy()

    # 1. Remove exact duplicate rows
    df = df.drop_duplicates(
        keep="first",
    ).reset_index(drop=True)

    # 2. Standardize text columns
    title_columns = [
        "customer_city",
        "branch_city",
        "category_name",
    ]

    upper_columns = [
        "payment_method",
    ]

    lower_columns = [
        "sales_channel",
    ]

    original_case_columns = [
        "customer_first_name",
        "customer_last_name",
        "customer_email",
        "customer_phone",
        "product_name",
        "branch_name",
        "customer_id",
        "product_id",
        "branch_id",
        "sale_id",
    ]

    for column in title_columns:
        _clean_text_column(
            df,
            column,
            case="title",
        )

    for column in upper_columns:
        _clean_text_column(
            df,
            column,
            case="upper",
        )

    for column in lower_columns:
        _clean_text_column(
            df,
            column,
            case="lower",
        )

    for column in original_case_columns:
        _clean_text_column(
            df,
            column,
            case="original",
        )

    # 3. Convert date columns
    date_columns = [
        "sale_date",
        "customer_signup_date",
        "inventory_snapshot_date",
    ]

    _convert_date_columns(
        df,
        date_columns,
    )

    # 4. Convert numeric columns
    numeric_columns = [
        "unit_cost",
        "unit_price",
        "quantity",
        "discount_percent",
        "stock_quantity",
        "reorder_level",
    ]

    _convert_numeric_columns(
        df,
        numeric_columns,
    )

    # 5. Create category mapping
    df, dim_categories = _create_category_mapping(
        df,
    )

    # 6. Create dimension tables
    dim_customers = _create_customer_dimension(
        df,
    )

    dim_categories = _create_category_dimension(
        dim_categories,
    )

    dim_products = _create_product_dimension(
        df,
    )

    dim_branches = _create_branch_dimension(
        df,
    )

    # 7. Create fact tables
    fact_sales = _create_sales_fact(
        df,
    )

    fact_inventory_snapshot = _create_inventory_fact(
        df,
    )

    # 8. Return all normalized tables
    return {
        "dim_customers": dim_customers,
        "dim_categories": dim_categories,
        "dim_products": dim_products,
        "dim_branches": dim_branches,
        "fact_sales": fact_sales,
        "fact_inventory_snapshot": fact_inventory_snapshot,
    }