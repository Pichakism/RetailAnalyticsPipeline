import os
import pandas as pd

# Define paths dynamically based on the project structure
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_PATH = os.path.join(BASE_DIR, "data", "raw", "retail_transactions_denormalized.csv")

# Define all expected columns based on the raw dataset
REQUIRED_COLUMNS = [
    "sale_id", "sale_date", "customer_id", "customer_first_name", 
    "customer_last_name", "customer_email", "customer_phone", 
    "customer_city", "customer_signup_date", "product_id", 
    "product_name", "category_name", "unit_cost", "unit_price", 
    "branch_id", "branch_name", "branch_city", "sales_channel", 
    "quantity", "discount_percent", "payment_method", 
    "inventory_snapshot_date", "stock_quantity", "reorder_level"
]

def extract_data():
    """
    Reads the raw denormalized CSV file, validates its structure,
    and prints an initial profiling summary.
    """
    
    # 1. Validate that the required file exists
    if not os.path.exists(RAW_DATA_PATH):
        raise FileNotFoundError(f"Raw data file not found at: {RAW_DATA_PATH}")
    
    print(f"Reading raw data from {RAW_DATA_PATH}...")
    df = pd.read_csv(RAW_DATA_PATH)
    
    # 2. Log the raw row count and column count
    row_count, col_count = df.shape
    print(f"Loaded {row_count} rows and {col_count} columns.")
    
    # 3. Validate that required columns exist
    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns in raw data: {missing_columns}")
    
    print("All required columns are present in the dataset.")
    
    # 4. Produce an initial profiling summary
    print("\n" + "="*40)
    print("DATA PROFILING SUMMARY")
    print("="*40)
    
    # Duplicate counts
    duplicate_count = df.duplicated().sum()
    print(f"Exact Duplicate Rows: {duplicate_count}")
    
    # Null counts
    print("\nNull Values Count per Column:")
    null_counts = df.isnull().sum()
    null_columns = null_counts[null_counts > 0]
    if not null_columns.empty:
        print(null_columns.to_string())
    else:
        print("No null values found.")
    
    # Basic numeric statistics
    print("\nBasic Numeric Statistics:")
    numeric_columns = df.select_dtypes(include=['number'])
    if not numeric_columns.empty:
        # Transpose and select key stats for better readability in terminal
        stats = numeric_columns.describe().T[['count', 'mean', 'min', 'max']]
        print(stats.to_string())
    else:
        print("No numeric columns found.")
        
    print("="*40 + "\n")
    
    return df