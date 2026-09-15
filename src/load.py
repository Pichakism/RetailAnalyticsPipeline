import psycopg2
from psycopg2.extras import execute_values

from src.config import DATABASE_URL


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
                    "sql/01_create_schema.sql",
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
    """
    connection = None

    try:
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
                # 3. Products
                # ----------------------------------------------------
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

                product_values = [
                    (
                        row["product_id"],
                        row["product_name"],
                        row["category_id"],
                        row["unit_cost"],
                        row["unit_price"],
                    )
                    for _, row in dim_products.iterrows()
                ]

                if product_values:
                    execute_values(
                        cursor,
                        product_query,
                        product_values,
                    )

                # ----------------------------------------------------
                # 4. Branches
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
                # 5. Sales
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
                # 6. Inventory Snapshot
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