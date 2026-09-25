
# Retail Analytics Pipeline

## 1. Project Overview

Retail Analytics Pipeline is a data engineering project designed to process retail sales and inventory data and load the cleaned data into a PostgreSQL data warehouse.

The project implements an end-to-end data pipeline that extracts raw data from a CSV file, transforms and normalizes the data, performs data quality checks, creates the relational database schema, and loads the validated data into PostgreSQL.

The project also includes SQL scripts for database validation, business analysis, reporting views, and reporting view validation.

The main objective is to convert raw retail data into structured and reliable dimension and fact tables that can be used for reporting, analysis, and business intelligence.

---

## 2. Project Objectives

The main objectives of this project are:

- Extract retail data from a raw CSV file.
- Validate the existence of required source columns.
- Clean and normalize textual, date, and numeric fields.
- Separate the raw data into dimension and fact tables.
- Detect and reject invalid records.
- Validate required fields and business rules.
- Create a relational PostgreSQL database schema.
- Load dimension tables before fact tables.
- Maintain referential integrity through foreign keys.
- Support repeated pipeline execution through conflict handling.
- Validate the loaded database records.
- Provide SQL queries for business analysis.
- Create reporting views for analytical use cases.
- Validate reporting views and their results.

---

## 3. Technology Stack

The project uses the following technologies:

- Python
- Pandas
- PostgreSQL 17
- Docker and Docker Compose
- Psycopg2
- SQL
- Git and GitHub
- pgAdmin

Python is used for data extraction, transformation, data quality validation, and database loading.

PostgreSQL is used as the target relational database.

Docker Compose is used to run PostgreSQL and pgAdmin in isolated containers.

Pandas is used to process and transform the raw dataset.

Psycopg2 is used to establish a connection between Python and PostgreSQL and to insert processed data into the database.

---

## 4. Project Architecture

The pipeline follows the sequence below:

```text
Raw CSV File
     |
     v
Extract
     |
     v
Transform and Normalize
     |
     v
Data Quality Checks
     |
     v
Database Schema Creation
     |
     v
Load Data into PostgreSQL
     |
     v
Validation and Reporting SQL Scripts
```

The main Python pipeline is executed through:

```bash
python -m main
```

This command runs the main pipeline stages sequentially.

---

## 5. Pipeline Stages

### 5.1 Extract

The Extract stage reads the raw CSV file using Pandas.

The extraction module checks whether the required source columns exist in the input file.

The extracted data is loaded into a Pandas DataFrame and passed to the transformation stage.

The main responsibilities of this stage are:

- Read the raw CSV file.
- Validate required columns.
- Display basic information about the input data.
- Return the extracted DataFrame.

Main file:

```text
src/extract.py
```

Main function:

```python
extract_data()
```

---

### 5.2 Transform and Normalize

The Transform stage cleans and normalizes the extracted data.

The raw dataset contains information about customers, products, categories, branches, sales, and inventory snapshots.

The transformation stage converts the original dataset into separate dimension and fact tables.

The following tables are generated:

- dim_customers
- dim_categories
- dim_products
- dim_branches
- fact_sales
- fact_inventory_snapshot

The transformation process includes operations such as:

- Cleaning textual fields.
- Converting date fields.
- Converting numeric fields.
- Removing exact duplicate records.
- Creating category information.
- Preparing dimension records.
- Preparing sales fact records.
- Preparing inventory snapshot records.

Main file:

```text
src/transform.py
```

Main function:

```python
transform_and_normalize(df)
```

The function returns a dictionary containing the six processed DataFrames.

---

### 5.3 Data Quality Checks

The Data Quality stage checks the transformed data before it is loaded into PostgreSQL.

The quality checks help prevent invalid records from entering the database.

The validation process includes:

- Checking required fields.
- Detecting duplicate records.
- Validating numeric values.
- Validating discount percentages.
- Checking foreign key relationships.
- Checking product and branch references.
- Validating inventory snapshot keys.
- Rejecting invalid records.

Rejected records are saved in:

```text
data/processed/rejected_records
```

Only valid records are passed to the loading stage.

Main file:

```text
src/quality.py
```

Main function:

```python
run_quality_checks(tables)
```

The function receives a dictionary of transformed tables and returns a dictionary containing valid tables.

---

### 5.4 Database Schema Creation

The database schema is created using the following SQL file:

```text
sql/01_create_schema.sql
```

The schema contains dimension tables and fact tables.

The database schema includes primary keys, foreign keys, unique constraints, and business rule constraints.

The schema creation stage is executed by the function:

```python
execute_schema()
```

This function is implemented in:

```text
src/load.py
```

The function reads the schema SQL file and executes it against PostgreSQL.

---

### 5.5 Data Loading

The Load stage inserts the validated data into PostgreSQL.

Dimension tables are loaded before fact tables because fact tables contain foreign keys referencing dimension tables.

The loading order is:

```text
1. dim_customers
2. dim_categories
3. dim_products
4. dim_branches
5. fact_sales
6. fact_inventory_snapshot
```

The loading module uses PostgreSQL conflict handling to support repeated execution.

For example, existing customer, product, branch, and sales records are updated when their primary keys already exist.

Category records use the category name to prevent duplicate categories.

The real PostgreSQL category IDs are retrieved after inserting the categories. These IDs are then used when inserting products.

Main file:

```text
src/load.py
```

Main functions:

```python
get_connection()
execute_schema()
normalize_dataframe()
load_data()
```

---

## 6. Database Configuration

The project uses PostgreSQL running through Docker Compose.

The main database configuration is:

| Setting | Value |
|---|---|
| Database engine | PostgreSQL |
| PostgreSQL version | 17 |
| Database name | retail_analytics |
| Database user | retail_user |
| Database password | retail_password |
| Host | localhost |
| Host port | 5433 |
| Container port | 5432 |
| PostgreSQL service | postgres |
| PostgreSQL container | retail-analytics-postgres |
| pgAdmin host port | 5051 |

The database connection URL is configured through the project configuration module.

The connection URL follows this format:

```text
postgresql://retail_user:retail_password@localhost:5433/retail_analytics
```

The project should use the `.env` file for database configuration instead of hardcoding credentials in multiple files.

---

## 7. Database Schema

The database contains the following tables.

### 7.1 dim_customers

This table stores customer information.

Main columns include:

- customer_id
- first_name
- last_name
- email
- phone
- city
- signup_date

The primary key is:

```text
customer_id
```

---

### 7.2 dim_categories

This table stores product category information.

Main columns include:

- category_id
- category_name

The primary key is:

```text
category_id
```

The category name is unique.

---

### 7.3 dim_products

This table stores product information.

Main columns include:

- product_id
- product_name
- category_id
- unit_cost
- unit_price

The primary key is:

```text
product_id
```

The category_id column references the dim_categories table.

---

### 7.4 dim_branches

This table stores branch information.

Main columns include:

- branch_id
- branch_name
- city

The primary key is:

```text
branch_id
```

---

### 7.5 fact_sales

This table stores sales transactions.

Main columns include:

- sale_id
- sale_date
- customer_id
- product_id
- branch_id
- sales_channel
- quantity
- discount_percent
- payment_method

The primary key is:

```text
sale_id
```

The table contains foreign key references to the customer, product, and branch dimension tables.

The quantity must be greater than zero.

The discount percentage must be between zero and one hundred when it is not NULL.

---

### 7.6 fact_inventory_snapshot

This table stores inventory snapshots for products and branches.

Main columns include:

- product_id
- branch_id
- snapshot_date
- stock_quantity
- reorder_level

The table uses a composite primary key:

```text
product_id
branch_id
snapshot_date
```

The product_id and branch_id columns reference the corresponding dimension tables.

The stock quantity and reorder level must not be negative.

---

## 8. Project Structure

The main project structure is:

```text
RetailAnalyticsPipeline/
|
|-- data/
|   |-- raw/
|   |-- processed/
|       |-- rejected_records/
|
|-- docs/
|   |-- database_and_reporting.md
|
|-- sql/
|   |-- 01_create_schema.sql
|   |-- 02_validate_loaded_data.sql
|   |-- 03_business_analysis.sql
|   |-- 04_create_reporting_views.sql
|   |-- 05_validate_reporting_views.sql
|
|-- src/
|   |-- __init__.py
|   |-- config.py
|   |-- extract.py
|   |-- transform.py
|   |-- quality.py
|   |-- load.py
|
|-- main.py
|-- .env
|-- .gitignore
|-- docker-compose.yml
|-- README.md
```

The raw input file should be placed in the expected location configured in:

```text
src/extract.py
```

---

## 9. Running the Project

### 9.1 Start Docker Services

Start PostgreSQL and pgAdmin using Docker Compose:

```bash
docker compose up -d
```

Check the running containers:

```bash
docker compose ps
```

The PostgreSQL container should be running before starting the Python pipeline.

---

### 9.2 Activate the Python Virtual Environment

On Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

If the virtual environment has not been created yet, create it using:

```powershell
python -m venv venv
```

Then activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

---

### 9.3 Install Dependencies

Install the required Python packages:

```bash
pip install pandas psycopg2-binary python-dotenv openpyxl
```

If the project contains a requirements file, dependencies can be installed using:

```bash
pip install -r requirements.txt
```

---

### 9.4 Run the Complete Pipeline

Run the following command from the project root directory:

```bash
python -m main
```

The main file executes the pipeline stages in the following order:

```text
Extract
Transform
Data Quality Checks
Database Schema Creation
Load
```

The pipeline displays the current stage and reports whether execution completed successfully or failed.

---

## 10. Data Validation

The following SQL file is used to validate the loaded data:

```text
sql/02_validate_loaded_data.sql
```

The validation script checks:

- Row counts.
- Duplicate primary keys.
- Invalid foreign key references.
- NULL values in required columns.
- Invalid business rule values.
- Duplicate inventory composite keys.

The validation script helps confirm that the loaded database records satisfy the expected structural and business constraints.

---

## 11. Business Analysis

The following SQL file contains business analysis queries:

```text
sql/03_business_analysis.sql
```

The analysis includes:

1. Monthly sales performance.
2. Top products by quantity sold.
3. Top products by net revenue.
4. Branch performance.
5. Sales channel performance.
6. Payment method analysis.
7. Category performance.
8. Inventory status summary.
9. Reorder requirements by branch.
10. Customer distribution by city.
11. Sales by customer city.
12. Overall sales KPIs.

These queries are designed to support retail performance analysis and provide information about sales, products, branches, customers, and inventory.

---

## 12. Reporting Views

The project includes SQL views for reusable reporting queries.

The reporting views are created using:

```text
sql/04_create_reporting_views.sql
```

The reporting views provide summarized information for:

- Monthly sales.
- Product performance.
- Branch performance.
- Sales channel performance.
- Category performance.
- Latest inventory status.
- Overall sales KPIs.

Views allow analytical queries to be reused without repeating the complete aggregation logic in every report.

---

## 13. Reporting View Validation

The reporting views are validated using:

```text
sql/05_validate_reporting_views.sql
```

The validation script checks:

- Whether the expected views exist.
- Whether the views return records.
- Monthly sales aggregation.
- Product-level aggregation.
- Branch-level aggregation.
- Sales channel aggregation.
- Category aggregation.
- Latest inventory status.
- KPI consistency.
- Negative values in analytical results.

---

## 14. Database Access

The PostgreSQL database can be accessed through pgAdmin.

The pgAdmin service is exposed on:

```text
http://localhost:5051
```

The PostgreSQL connection settings in pgAdmin are:

```text
Host: postgres
Port: 5432
Database: retail_analytics
Username: retail_user
Password: retail_password
```

When connecting from the Windows host instead of another Docker container, use:

```text
Host: localhost
Port: 5433
```

The internal Docker port is different from the host port.

---

## 15. Data Loading Behavior

The loading process uses conflict handling for repeated executions.

The following behavior is supported:

- Existing customers are updated using customer_id.
- Existing products are updated using product_id.
- Existing branches are updated using branch_id.
- Existing sales records are updated using sale_id.
- Existing inventory snapshots are updated using the composite key.
- Existing categories are not inserted again when the category name already exists.

Running the pipeline again does not automatically delete all existing database data.

The loading logic is designed to insert new records and update records when matching keys already exist.

---

## 16. Important Notes

- PostgreSQL must be running before the Python pipeline is executed.
- The database connection settings must match the Docker Compose configuration.
- The raw CSV file must be placed in the expected input directory.
- Required source columns must exist in the raw dataset.
- Invalid records are separated during the data quality stage.
- Dimension tables are loaded before fact tables.
- The pipeline should be executed from the project root directory.
- Large input files may require considerable memory and processing time.
- SQL scripts should be executed against the correct database.
- The reporting views should be recreated after structural changes to their definitions.

---

## 17. Current Project Scope

The current project focuses on:

- Data extraction.
- Data transformation.
- Data quality validation.
- Relational database modeling.
- PostgreSQL data loading.
- SQL-based validation.
- Business analysis.
- Reporting views.

The project does not currently include:

- A web dashboard.
- Automated cloud deployment.
- A production orchestration platform.
- Streaming data processing.
- Real-time data ingestion.
- Advanced machine learning models.

These features can be considered as future extensions.

---

## 18. Project Execution Summary

The complete Python pipeline can be executed using one command:

```bash
python -m main
```

The pipeline performs the following operations:

```text
1. Read the raw retail dataset.
2. Transform and normalize the data.
3. Run data quality checks.
4. Create the PostgreSQL schema.
5. Load the valid records into PostgreSQL.
6. Display the execution result.
```

After the main pipeline has completed successfully, the SQL scripts can be used for database validation, business analysis, reporting view creation, and reporting view validation.
