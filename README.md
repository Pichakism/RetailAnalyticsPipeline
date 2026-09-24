# Retail Analytics Pipeline

A data engineering project for extracting, transforming, validating, and loading retail sales and inventory data into a PostgreSQL data warehouse.

The project processes large-scale retail data and organizes it into a dimensional data model consisting of dimension tables and fact tables. It also provides SQL-based data quality validation, business analysis queries, and reporting views for analytical purposes.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Project Objectives](#project-objectives)
- [System Architecture](#system-architecture)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Data Source](#data-source)
- [Data Pipeline](#data-pipeline)
- [Database Design](#database-design)
- [Database Tables](#database-tables)
- [Data Quality Validation](#data-quality-validation)
- [Business Analysis](#business-analysis)
- [Reporting Views](#reporting-views)
- [Environment Configuration](#environment-configuration)
- [Installation and Setup](#installation-and-setup)
- [Running the Project](#running-the-project)
- [Database Validation](#database-validation)
- [Project Outputs](#project-outputs)
- [Current Scope](#current-scope)
- [Future Improvements](#future-improvements)
- [Contributors](#contributors)

---

## Project Overview

The Retail Analytics Pipeline is designed to process retail transaction and inventory data and load the cleaned and validated data into a PostgreSQL database.

The project follows a structured data pipeline:

1. Extract data from the source file.
2. Transform and standardize the raw data.
3. Validate data quality and identify invalid records.
4. Create the database schema.
5. Load the validated data into PostgreSQL.
6. Execute business analysis queries.
7. Create and validate reporting views.

The project uses a dimensional data model to separate descriptive information from transactional and inventory-related data.

The resulting database can be used for analytical queries related to:

- Sales performance
- Product performance
- Customer distribution
- Branch performance
- Sales channels
- Payment methods
- Product categories
- Inventory levels
- Reorder requirements

---

## Project Objectives

The main objectives of this project are:

- Build a reproducible retail data pipeline.
- Process a large retail dataset efficiently.
- Clean and standardize raw data.
- Identify invalid and rejected records.
- Design a relational data warehouse schema.
- Separate fact data from dimension data.
- Maintain referential integrity between tables.
- Validate business rules and data quality constraints.
- Load structured data into PostgreSQL.
- Provide reusable SQL queries for business analysis.
- Create reporting views for analytical access.
- Document the database and pipeline processes.

---

## System Architecture

The project consists of several main components:

```text
                    Source Data
                        |
                        v
                +---------------+
                |    Extract    |
                +---------------+
                        |
                        v
                +---------------+
                |   Transform   |
                +---------------+
                        |
                        v
                +---------------+
                |    Quality    |
                |    Checks     |
                +---------------+
                        |
                        v
                +---------------+
                | Schema Setup  |
                +---------------+
                        |
                        v
                +---------------+
                |     Load      |
                +---------------+
                        |
                        v
                +---------------+
                |  PostgreSQL   |
                |   Database    |
                +---------------+
                        |
                        v
        +-------------------------------+
        | Business Analysis and Views  |
        +-------------------------------+