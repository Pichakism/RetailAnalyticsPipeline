import os
import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
from src.config import DATABASE_URL

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHARTS_DIR = os.path.join(BASE_DIR, "reports", "charts")
VIEWS_SQL_PATH = os.path.join(BASE_DIR, "sql", "04_create_reporting_views.sql")

def create_reporting_views():
    """Execute the SQL file to create reporting views in the database."""
    print("Checking reporting views...")
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cursor:
                with open(VIEWS_SQL_PATH, "r", encoding="utf-8") as file:
                    cursor.execute(file.read())
    except Exception as e:
        if "already exists" in str(e):
            pass # Ignore smoothly if views are already built
        else:
            raise e

def get_dataframe_from_view(query: str) -> pd.DataFrame:
    """Fetch data from PostgreSQL and return as Pandas DataFrame."""
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description]
            data = cursor.fetchall()
            return pd.DataFrame(data, columns=columns)

def generate_charts():
    """Generate and save business reports using matplotlib."""
    os.makedirs(CHARTS_DIR, exist_ok=True)
    
    # 0. Ensure views exist
    create_reporting_views()
    
    print("Generating business charts...")

    # 1. Monthly Sales Trend (Line Chart)
    df_monthly = get_dataframe_from_view("SELECT sales_month, net_revenue FROM reporting_monthly_sales ORDER BY sales_month;")
    if not df_monthly.empty:
        df_monthly['net_revenue'] = pd.to_numeric(df_monthly['net_revenue'], errors='coerce').fillna(0)
        plt.figure(figsize=(10, 5))
        plt.plot(df_monthly['sales_month'].astype(str), df_monthly['net_revenue'], marker='o', linestyle='-', color='#1f77b4')
        plt.title('Monthly Net Revenue Trend')
        plt.xlabel('Month')
        plt.ylabel('Net Revenue ($)')
        plt.xticks(rotation=45)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig(os.path.join(CHARTS_DIR, '01_monthly_sales_trend.png'))
        plt.close()

    # 2. Top 10 Products by Net Revenue (Bar Chart)
    df_products = get_dataframe_from_view("SELECT product_name, net_revenue FROM reporting_product_performance ORDER BY net_revenue DESC LIMIT 10;")
    if not df_products.empty:
        df_products['net_revenue'] = pd.to_numeric(df_products['net_revenue'], errors='coerce').fillna(0)
        plt.figure(figsize=(10, 6))
        plt.barh(df_products['product_name'][::-1], df_products['net_revenue'][::-1], color='#2ca02c')
        plt.title('Top 10 Products by Net Revenue')
        plt.xlabel('Net Revenue ($)')
        plt.tight_layout()
        plt.savefig(os.path.join(CHARTS_DIR, '02_top_10_products.png'))
        plt.close()

    # 3. Branch Performance (Bar Chart)
    df_branch = get_dataframe_from_view("SELECT branch_name, net_revenue FROM reporting_branch_performance ORDER BY net_revenue DESC;")
    if not df_branch.empty:
        df_branch['net_revenue'] = pd.to_numeric(df_branch['net_revenue'], errors='coerce').fillna(0)
        plt.figure(figsize=(8, 5))
        plt.bar(df_branch['branch_name'], df_branch['net_revenue'], color='#ff7f0e')
        plt.title('Net Revenue by Branch')
        plt.ylabel('Net Revenue ($)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(CHARTS_DIR, '03_branch_performance.png'))
        plt.close()

    # 4. Sales Channel Distribution (Pie Chart)
    df_channel = get_dataframe_from_view("SELECT sales_channel, net_revenue FROM reporting_sales_channel_performance;")
    if not df_channel.empty:
        # Strictly clean data for Pie Chart to prevent crashes
        df_channel['net_revenue'] = pd.to_numeric(df_channel['net_revenue'], errors='coerce').fillna(0)
        df_channel = df_channel[df_channel['net_revenue'] > 0] 
        df_channel['sales_channel'] = df_channel['sales_channel'].fillna('Unknown')
        
        if not df_channel.empty:
            plt.figure(figsize=(7, 7))
            plt.pie(df_channel['net_revenue'], labels=df_channel['sales_channel'], autopct='%1.1f%%', startangle=140)
            plt.title('Revenue Distribution by Sales Channel')
            plt.tight_layout()
            plt.savefig(os.path.join(CHARTS_DIR, '04_sales_channel_distribution.png'))
            plt.close()

    # 5. Category Performance (Bar Chart)
    df_category = get_dataframe_from_view("SELECT category_name, net_revenue FROM reporting_category_performance ORDER BY net_revenue DESC;")
    if not df_category.empty:
        df_category['net_revenue'] = pd.to_numeric(df_category['net_revenue'], errors='coerce').fillna(0)
        plt.figure(figsize=(10, 5))
        plt.bar(df_category['category_name'], df_category['net_revenue'], color='#d62728')
        plt.title('Net Revenue by Category')
        plt.ylabel('Net Revenue ($)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(CHARTS_DIR, '05_category_performance.png'))
        plt.close()

    print(f"5 charts successfully generated and saved in: {CHARTS_DIR}")

if __name__ == "__main__":
    generate_charts()
