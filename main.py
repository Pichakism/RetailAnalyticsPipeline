
import sys
import os
import time

# Add the project root directory to Python path.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.extract import extract_data
from src.transform import transform_and_normalize
from src.quality import run_quality_checks
from src.load import execute_schema, load_data


def print_stage_header(stage_number, stage_name):
    """Print a clear header for each pipeline stage."""
    print()
    print("=" * 70)
    print(f"STAGE {stage_number}: {stage_name}")
    print("=" * 70)


def print_table_summary(tables):
    """Print the number of rows in each processed table."""
    print()
    print("Processed table summary:")
    print("-" * 50)

    for table_name, dataframe in tables.items():
        print(f"{table_name:<35} {len(dataframe):>10,} rows")

    print("-" * 50)


def main():
    """Run the complete data pipeline in the correct order."""
    pipeline_start_time = time.time()

    print("=" * 70)
    print("RETAIL ANALYTICS PIPELINE")
    print("Starting complete pipeline execution")
    print("=" * 70)

    try:
        # Stage 1: Extract
        print_stage_header(1, "EXTRACT")

        raw_data = extract_data()

        print(
            f"Extraction completed successfully. "
            f"Rows extracted: {len(raw_data):,}"
        )

        # Stage 2: Transform
        print_stage_header(2, "TRANSFORM")

        transformed_tables = transform_and_normalize(raw_data)

        print("Transformation and normalization completed successfully.")

        print_table_summary(transformed_tables)

        # Stage 3: Data Quality
        print_stage_header(3, "DATA QUALITY CHECKS")

        valid_tables = run_quality_checks(transformed_tables)

        print("Data quality checks completed successfully.")

        print_table_summary(valid_tables)

        # Stage 4: Database Schema
        print_stage_header(4, "DATABASE SCHEMA CREATION")

        execute_schema()

        print("Database schema is ready.")

        # Stage 5: Load
        print_stage_header(5, "LOAD")

        load_data(
            dim_customers=valid_tables["dim_customers"],
            dim_categories=valid_tables["dim_categories"],
            dim_products=valid_tables["dim_products"],
            dim_branches=valid_tables["dim_branches"],
            fact_sales=valid_tables["fact_sales"],
            fact_inventory_snapshot=valid_tables[
                "fact_inventory_snapshot"
            ],
        )

        print("All data was loaded into PostgreSQL successfully.")

        # Pipeline completion
        elapsed_time = time.time() - pipeline_start_time

        print()
        print("=" * 70)
        print("PIPELINE COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print(f"Total execution time: {elapsed_time:.2f} seconds")
        print("=" * 70)

    except Exception as error:
        elapsed_time = time.time() - pipeline_start_time

        print()
        print("=" * 70)
        print("PIPELINE FAILED")
        print("=" * 70)
        print(f"Error: {error}")
        print(f"Execution time before failure: {elapsed_time:.2f} seconds")
        print("=" * 70)

        raise


if __name__ == "__main__":
    main()