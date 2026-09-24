
import os

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

from src.config import DATABASE_URL


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SCHEMA_PATH = os.path.join(
    BASE_DIR,
    "sql",
    "01_create_schema.sql",
)


def get_connection():
    """Create and return a PostgreSQL database connection."""
    return psycopg2.connect(DATABASE_URL)


def execute_schema():
    """Create database tables using the schema SQL file."""
    connection = None

    try:
        connection = get_connection()

        with connection:
            with connection.cursor() as cursor:
                with open(
                    SCHEMA_PATH,
                    "r",
                    encoding="utf-8",
                ) as sql_file:
                    schema_sql = sql_file.read()

                cursor.execute(schema_sql)

        print("Database schema created successfully.")

    except Exception:
        if connection is not None:
            connection.rollback()

        raise

    finally:
        if connection is not None:
            connection.close()


def normalize_dataframe(dataframe):
    """
    Convert Pandas missing values to Python None.

    Python None is converted to SQL NULL by psycopg2.
    This is necessary for nullable PostgreSQL columns.
    """

    normalized_dataframe = dataframe.astype(object).where(
        pd.notna(dataframe),
        None,
    )

    return normalized_dataframe


def load_data(
    dim_customers,
    dim_categories,
    dim_products,
    dim_branches,
    fact_sales,
    fact_inventory_snapshot,
):
    """
    Load six cleaned DataFrames into PostgreSQL.

    Dimensions are loaded before facts because fact tables
    contain foreign keys referencing dimension tables.

    Category IDs are retrieved from PostgreSQL using category_name.
    Pandas missing values are converted to SQL NULL.
    """

    connection = None

    try:
        # ------------------------------------------------------------
        # 0. Normalize missing values
        # ------------------------------------------------------------
        dim_customers = normalize_dataframe(dim_customers)
        dim_categories = normalize_dataframe(dim_categories)
        dim_products = normalize_dataframe(dim_products)
        dim_branches = normalize_dataframe(dim_branches)
        fact_sales = normalize_dataframe(fact_sales)
        fact_inventory_snapshot = normalize_dataframe(
            fact_inventory_snapshot
        )

        connection = get_connection()

        with connection:
            with connection.cursor() as cursor:

                # ----------------------------------------------------
                # 1. Customers
                # ----------------------------------------------------
                customer_query = """
                    INSERT INTO dim_customers (
                        customer_id,
                        first_name,
                        last_name,
                        email,
                        phone,
                        city,
                        signup_date
                    )
                    VALUES %s
                    ON CONFLICT (customer_id)
                    DO UPDATE SET
                        first_name = EXCLUDED.first_name,
                        last_name = EXCLUDED.last_name,
                        email = EXCLUDED.email,
                        phone = EXCLUDED.phone,
                        city = EXCLUDED.city,
                        signup_date = EXCLUDED.signup_date;
                """

                customer_values = [
                    (
                        row["customer_id"],
                        row["first_name"],
                        row["last_name"],
                        row["email"],
                        row["phone"],
                        row["city"],
                        row["signup_date"],
                    )
                    for _, row in dim_customers.iterrows()
                ]

                if customer_values:
                    execute_values(
                        cursor,
                        customer_query,
                        customer_values,
                    )

                # ----------------------------------------------------
                # 2. Categories
                # ----------------------------------------------------
                category_query = """
                    INSERT INTO dim_categories (
                        category_name
                    )
                    VALUES %s
                    ON CONFLICT (category_name)
                    DO NOTHING;
                """

                category_values = [
                    (row["category_name"],)
                    for _, row in dim_categories.iterrows()
                ]

                if category_values:
                    execute_values(
                        cursor,
                        category_query,
                        category_values,
                    )

                # ----------------------------------------------------
                # 3. Retrieve real category IDs from PostgreSQL
                # ----------------------------------------------------
                cursor.execute(
                    """
                    SELECT category_id, category_name
                    FROM dim_categories;
                    """
                )

                category_mapping = {
                    category_name: category_id
                    for category_id, category_name in cursor.fetchall()
                }

                # ----------------------------------------------------
                # 4. Products
                # ----------------------------------------------------
                product_values = []

                for _, row in dim_products.iterrows():
                    category_name = row["category_name"]

                    category_id = category_mapping.get(category_name)

                    if category_id is None:
                        raise ValueError(
                            f"Category '{category_name}' was not found "
                            "in dim_categories."
                        )

                    product_values.append(
                        (
                            row["product_id"],
                            row["product_name"],
                            category_id,
                            row["unit_cost"],
                            row["unit_price"],
                        )
                    )

                product_query = """
                    INSERT INTO dim_products (
                        product_id,
                        product_name,
                        category_id,
                        unit_cost,
                        unit_price
                    )
                    VALUES %s
                    ON CONFLICT (product_id)
                    DO UPDATE SET
                        product_name = EXCLUDED.product_name,
                        category_id = EXCLUDED.category_id,
                        unit_cost = EXCLUDED.unit_cost,
                        unit_price = EXCLUDED.unit_price;
                """

                if product_values:
                    execute_values(
                        cursor,
                        product_query,
                        product_values,
                    )

                # ----------------------------------------------------
                # 5. Branches
                # ----------------------------------------------------
                branch_query = """
                    INSERT INTO dim_branches (
                        branch_id,
                        branch_name,
                        city
                    )
                    VALUES %s
                    ON CONFLICT (branch_id)
                    DO UPDATE SET
                        branch_name = EXCLUDED.branch_name,
                        city = EXCLUDED.city;
                """

                branch_values = [
                    (
                        row["branch_id"],
                        row["branch_name"],
                        row["city"],
                    )
                    for _, row in dim_branches.iterrows()
                ]

                if branch_values:
                    execute_values(
                        cursor,
                        branch_query,
                        branch_values,
                    )

                # ----------------------------------------------------
                # 6. Sales
                # ----------------------------------------------------
                sales_query = """
                    INSERT INTO fact_sales (
                        sale_id,
                        sale_date,
                        customer_id,
                        product_id,
                        branch_id,
                        sales_channel,
                        quantity,
                        discount_percent,
                        payment_method
                    )
                    VALUES %s
                    ON CONFLICT (sale_id)
                    DO UPDATE SET
                        sale_date = EXCLUDED.sale_date,
                        customer_id = EXCLUDED.customer_id,
                        product_id = EXCLUDED.product_id,
                        branch_id = EXCLUDED.branch_id,
                        sales_channel = EXCLUDED.sales_channel,
                        quantity = EXCLUDED.quantity,
                        discount_percent = EXCLUDED.discount_percent,
                        payment_method = EXCLUDED.payment_method;
                """

                sales_values = [
                    (
                        row["sale_id"],
                        row["sale_date"],
                        row["customer_id"],
                        row["product_id"],
                        row["branch_id"],
                        row["sales_channel"],
                        row["quantity"],
                        row["discount_percent"],
                        row["payment_method"],
                    )
                    for _, row in fact_sales.iterrows()
                ]

                if sales_values:
                    execute_values(
                        cursor,
                        sales_query,
                        sales_values,
                    )

                # ----------------------------------------------------
                # 7. Inventory Snapshot
                # ----------------------------------------------------
                inventory_query = """
                    INSERT INTO fact_inventory_snapshot (
                        product_id,
                        branch_id,
                        snapshot_date,
                        stock_quantity,
                        reorder_level
                    )
                    VALUES %s
                    ON CONFLICT (
                        product_id,
                        branch_id,
                        snapshot_date
                    )
                    DO UPDATE SET
                        stock_quantity = EXCLUDED.stock_quantity,
                        reorder_level = EXCLUDED.reorder_level;
                """

                inventory_values = [
                    (
                        row["product_id"],
                        row["branch_id"],
                        row["snapshot_date"],
                        row["stock_quantity"],
                        row["reorder_level"],
                    )
                    for _, row in fact_inventory_snapshot.iterrows()
                ]

                if inventory_values:
                    execute_values(
                        cursor,
                        inventory_query,
                        inventory_values,
                    )

        print("Data load completed successfully.")

    except Exception:
        if connection is not None:
            connection.rollback()

        raise

    finally:
        if connection is not None:
            connection.close()