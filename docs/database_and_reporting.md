
# Database and Reporting Documentation

## 1. Overview

The Retail Analytics Pipeline processes denormalized retail transaction data and stores the transformed data in a PostgreSQL database.

The database layer separates descriptive information from transactional and inventory data. This structure improves data organization, supports relational integrity, and provides a foundation for analytical reporting.

The pipeline includes the following main stages:

1. Data extraction
2. Data transformation
3. Data quality validation
4. Database schema creation
5. Data loading
6. Reporting and analytical queries
7. Reporting view validation

---

## 2. Technology Stack

| Component | Technology |
|---|---|
| Database | PostgreSQL 17 |
| Database Container | Docker |
| Database Driver | psycopg2 |
| Data Processing | Python and Pandas |
| Configuration | Python Dotenv |
| Reporting | PostgreSQL SQL Queries and Views |
| Database Administration Interface | pgAdmin |

---

## 3. Database Configuration

The PostgreSQL database runs inside a Docker container.

| Configuration | Value |
|---|---|
| Database Service | `postgres` |
| Container Name | `retail-analytics-postgres` |
| Database Name | `retail_analytics` |
| Database User | `retail_user` |
| Container Port | `5432` |
| Host Port | `5433` |
| pgAdmin Host Port | `5051` |

The database connection is configured through environment variables.

The database URL follows this structure:

```text
postgresql://retail_user:retail_password@localhost:5433/retail_analytics
```

The database is exposed through the local host port and is intended for local development and project testing.

---

## 4. Data Pipeline

The data pipeline is divided into multiple processing stages.

### 4.1. Extraction

The extraction stage reads the raw denormalized CSV file from the project data directory.

The extraction process performs the following operations:

- Checks whether the source file exists.
- Reads the CSV file using Pandas.
- Checks whether the required columns are available.
- Reports the number of rows and columns.
- Displays duplicate row information.
- Displays missing-value information.
- Displays basic numeric statistics.

The extraction stage does not create database records. It returns the raw dataset for subsequent processing.

---

### 4.2. Transformation

The transformation stage converts the denormalized dataset into separate dimension and fact tables.

The transformation process includes:

- Removing exact duplicate rows.
- Cleaning text values.
- Converting numeric columns to numeric data types.
- Converting date columns to date values.
- Creating category mappings.
- Preparing customer dimension data.
- Preparing category dimension data.
- Preparing product dimension data.
- Preparing branch dimension data.
- Preparing sales fact data.
- Preparing inventory snapshot fact data.

The transformation stage prepares the data for relational storage and subsequent quality validation.

---

### 4.3. Data Quality Validation

The data quality stage validates the transformed tables before loading them into PostgreSQL.

The validation process checks:

- Required columns and values.
- Duplicate business identifiers.
- Invalid product prices and costs.
- Invalid sales quantities.
- Invalid discount percentages.
- Invalid inventory quantities.
- Foreign key relationships.
- Duplicate inventory composite keys.

Invalid records are saved in the following directory:

```text
data/processed/rejected_records
```

The rejected records are separated from the valid records so that invalid data does not prevent the valid portion of the dataset from being loaded.

---

### 4.4. Database Schema Creation

The database schema is created using:

```text
sql/01_create_schema.sql
```

The schema contains six main tables:

- `dim_customers`
- `dim_categories`
- `dim_products`
- `dim_branches`
- `fact_sales`
- `fact_inventory_snapshot`

The schema defines primary keys, foreign keys, required fields, and selected business rules through database constraints.

---

### 4.5. Data Loading

The loading stage inserts the validated data into PostgreSQL.

The loading process:

1. Opens a database connection.
2. Executes the database schema script.
3. Loads dimension tables.
4. Resolves category identifiers.
5. Loads the sales fact table.
6. Loads the inventory snapshot fact table.
7. Uses database transactions to maintain consistency.
8. Rolls back the transaction if a loading error occurs.

The loading process uses the database schema and the validated transformed data as its input.

---

## 5. Database Schema

### 5.1. Dimension Tables

Dimension tables contain descriptive information used to explain transactional data.

#### `dim_customers`

Stores customer information.

Main attributes include:

- Customer identifier
- First name
- Last name
- Email
- Phone
- City
- Signup date

The primary key is:

```text
customer_id
```

#### `dim_categories`

Stores product category information.

Main attributes include:

- Category identifier
- Category name

The category identifier is generated by the database.

#### `dim_products`

Stores product information.

Main attributes include:

- Product identifier
- Product name
- Category identifier
- Unit cost
- Unit price

The product table references the category table through `category_id`.

#### `dim_branches`

Stores branch information.

Main attributes include:

- Branch identifier
- Branch name
- City

The primary key is:

```text
branch_id
```

---

### 5.2. Fact Tables

Fact tables contain transactional and operational measurements.

#### `fact_sales`

Stores sales transactions.

Main attributes include:

- Sale identifier
- Sale date
- Customer identifier
- Product identifier
- Branch identifier
- Sales channel
- Quantity
- Discount percentage
- Payment method

The table references customers, products, and branches through foreign keys.

The following business rules are enforced:

- Quantity must be greater than zero.
- Discount percentage must be between zero and one hundred when provided.
- Customer, product, and branch references must exist.

#### `fact_inventory_snapshot`

Stores inventory measurements for products at branches on specific dates.

Main attributes include:

- Product identifier
- Branch identifier
- Snapshot date
- Stock quantity
- Reorder level

The table uses a composite primary key:

```text
(product_id, branch_id, snapshot_date)
```

This key ensures that a product and branch combination cannot have multiple records for the same snapshot date.

---

## 6. Reporting Layer

The reporting layer provides reusable SQL views for analytical queries.

The reporting views are created through:

```text
sql/04_create_reporting_views.sql
```

The reporting layer contains the following views.

| View | Purpose |
|---|---|
| `reporting_monthly_sales` | Monthly sales and revenue analysis |
| `reporting_product_performance` | Product-level sales and revenue analysis |
| `reporting_branch_performance` | Branch-level performance analysis |
| `reporting_sales_channel_performance` | Sales channel comparison |
| `reporting_category_performance` | Category-level performance analysis |
| `reporting_latest_inventory` | Latest inventory status by product and branch |
| `reporting_sales_kpis` | Overall sales performance indicators |

The reporting views are based on the fact and dimension tables and are intended to simplify repeated analytical queries.

---

## 7. Business Analysis Queries

The business analysis queries are stored in:

```text
sql/03_business_analysis.sql
```

The analysis script includes the following sections:

1. Monthly sales performance
2. Top products by quantity sold
3. Top products by net revenue
4. Branch performance
5. Sales channel performance
6. Payment method analysis
7. Category performance
8. Inventory status summary
9. Reorder requirements by branch
10. Customer distribution by city
11. Sales by customer city
12. Overall sales KPIs

The analysis script includes explanatory comments and output descriptions before each query.

The generated report can be saved to:

```text
reports/business_analysis_output.txt
```

---

## 8. Reporting Validation

The reporting validation script is stored in:

```text
sql/05_validate_reporting_views.sql
```

The validation script checks:

- Reporting view existence.
- Row counts for reporting views.
- Monthly reporting coverage.
- Product-level aggregation.
- Branch-level aggregation.
- Sales channel aggregation.
- Category-level aggregation.
- Latest inventory status distribution.
- Sales KPI consistency.
- Negative quantities and revenue values.

The validation output can be saved to:

```text
reports/reporting_views_validation.txt
```

The validation process compares selected reporting values with calculations performed directly on the source fact and dimension tables.

---

## 9. Execution Commands

### 9.1. Start the Database Services

```powershell
docker compose up -d
```

### 9.2. Execute the Database Schema

```powershell
Get-Content .\sql\01_create_schema.sql |
docker compose exec -T postgres psql -U retail_user -d retail_analytics
```

### 9.3. Create Reporting Views

```powershell
Get-Content .\sql\04_create_reporting_views.sql |
docker compose exec -T postgres psql -U retail_user -d retail_analytics
```

### 9.4. Generate the Business Analysis Report

```powershell
Get-Content .\sql\03_business_analysis.sql |
docker compose exec -T postgres psql -U retail_user -d retail_analytics |
Out-File -FilePath .\reports\business_analysis_output.txt -Encoding utf8
```

### 9.5. Validate Reporting Views

```powershell
Get-Content .\sql\05_validate_reporting_views.sql |
docker compose exec -T postgres psql -U retail_user -d retail_analytics |
Out-File -FilePath .\reports\reporting_views_validation.txt -Encoding utf8
```

---

## 10. Project Outputs

The project generates the following important outputs:

| Output | Description |
|---|---|
| `data/processed/rejected_records` | Invalid records separated during data quality validation |
| `reports/business_analysis_output.txt` | Results of business analysis queries |
| `reports/reporting_views_validation.txt` | Results of reporting view validation |
| `sql/01_create_schema.sql` | Database schema definition |
| `sql/02_validate_loaded_data.sql` | Validation of loaded database records |
| `sql/03_business_analysis.sql` | Business analysis queries |
| `sql/04_create_reporting_views.sql` | Reporting view definitions |
| `sql/05_validate_reporting_views.sql` | Reporting layer validation queries |

---

## 11. Current Scope

The current implementation focuses on:

- Loading retail transaction data into PostgreSQL.
- Separating dimension and fact tables.
- Validating data quality before loading.
- Creating reusable reporting views.
- Running business analysis queries.
- Validating the reporting layer.

The current reporting layer is designed for analytical queries and database reporting. Dashboard development, automated scheduling, and advanced visualization can be added in future development stages.