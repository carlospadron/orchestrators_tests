"""Shared ETL operations for all orchestrators."""

from pathlib import Path
from typing import Literal

import pandas as pd
from sqlalchemy import create_engine


def extract_data(
    file_path: str | Path,
    file_format: Literal["csv", "json", "parquet"] = "csv",
) -> pd.DataFrame:
    """
    Extract data from file.
    
    Args:
        file_path: Path to data file
        file_format: Format of the file (csv, json, parquet)
        
    Returns:
        DataFrame with extracted data
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    print(f"Extracting data from {file_path}...")
    
    if file_format == "csv":
        df = pd.read_csv(file_path)
    elif file_format == "json":
        df = pd.read_json(file_path, lines=True)
    elif file_format == "parquet":
        df = pd.read_parquet(file_path)
    else:
        raise ValueError(f"Unsupported format: {file_format}")
    
    print(f"✓ Extracted {len(df):,} rows")
    return df


def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform data: clean, validate, enrich.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Transformed DataFrame
    """
    print(f"Transforming {len(df):,} rows...")
    
    # Create a copy to avoid modifying original
    df = df.copy()
    
    # Data cleaning
    # Remove duplicates
    original_count = len(df)
    df = df.drop_duplicates(subset=["transaction_id"])
    duplicates_removed = original_count - len(df)
    if duplicates_removed > 0:
        print(f"  - Removed {duplicates_removed} duplicate rows")
    
    # Handle missing values
    df = df.dropna(subset=["transaction_id", "customer_id", "total_amount"])
    
    # Data validation
    # Remove invalid transactions (negative amounts)
    df = df[df["total_amount"] > 0]
    df = df[df["quantity"] > 0]
    
    # Convert date strings to datetime
    df["transaction_date"] = pd.to_datetime(df["transaction_date"])
    
    # Data enrichment
    # Add derived columns
    df["year"] = df["transaction_date"].dt.year
    df["month"] = df["transaction_date"].dt.month
    df["day_of_week"] = df["transaction_date"].dt.day_name()
    df["is_weekend"] = df["transaction_date"].dt.dayofweek >= 5
    
    # Categorize customers by purchase amount
    df["customer_segment"] = pd.cut(
        df["total_amount"],
        bins=[0, 50, 200, float("inf")],
        labels=["low_value", "medium_value", "high_value"],
    )
    
    # Calculate profit margin (simplified)
    df["estimated_profit"] = (df["total_amount"] * 0.3).round(2)
    
    print(f"✓ Transformed data: {len(df):,} rows")
    return df


def create_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create summary statistics by category.
    
    Args:
        df: Transformed DataFrame
        
    Returns:
        Summary DataFrame
    """
    print("Creating summary statistics...")
    
    summary = (
        df.groupby("category")
        .agg(
            total_transactions=("transaction_id", "count"),
            total_revenue=("total_amount", "sum"),
            avg_order_value=("total_amount", "mean"),
            total_quantity=("quantity", "sum"),
        )
        .reset_index()
    )
    
    summary["total_revenue"] = summary["total_revenue"].round(2)
    summary["avg_order_value"] = summary["avg_order_value"].round(2)
    
    print(f"✓ Created summary with {len(summary)} categories")
    return summary


def load_to_database(
    df: pd.DataFrame,
    table_name: str,
    database_url: str,
    if_exists: Literal["fail", "replace", "append"] = "append",
    batch_size: int = 10000,
):
    """
    Load data to PostgreSQL database.
    
    Args:
        df: DataFrame to load
        table_name: Target table name
        database_url: Database connection URL
        if_exists: How to behave if table exists
        batch_size: Number of rows per batch
    """
    print(f"Loading {len(df):,} rows to {table_name}...")
    
    engine = create_engine(database_url)
    
    # Load in batches for better performance
    df.to_sql(
        table_name,
        engine,
        if_exists=if_exists,
        index=False,
        chunksize=batch_size,
        method="multi",
    )
    
    print(f"✓ Loaded {len(df):,} rows to {table_name}")


def run_etl_pipeline(
    input_file: str | Path,
    database_url: str,
    file_format: Literal["csv", "json", "parquet"] = "csv",
):
    """
    Run complete ETL pipeline.
    
    Args:
        input_file: Path to input data file
        database_url: Database connection URL
        file_format: Input file format
    """
    print("\n" + "=" * 60)
    print("Starting ETL Pipeline")
    print("=" * 60)
    
    # Extract
    df = extract_data(input_file, file_format)
    
    # Transform
    df_transformed = transform_data(df)
    
    # Load main data
    load_to_database(df_transformed, "transactions", database_url, if_exists="replace")
    
    # Create and load summary
    df_summary = create_summary(df_transformed)
    load_to_database(df_summary, "transaction_summary", database_url, if_exists="replace")
    
    print("\n" + "=" * 60)
    print("✓ ETL Pipeline completed successfully!")
    print("=" * 60 + "\n")
    
    return {
        "rows_processed": len(df_transformed),
        "categories": len(df_summary),
        "total_revenue": float(df_summary["total_revenue"].sum()),
    }


if __name__ == "__main__":
    import sys
    from database_utils import get_database_url
    
    if len(sys.argv) < 2:
        print("Usage: python etl_operations.py <input_file> [format]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    file_format = sys.argv[2] if len(sys.argv) > 2 else "csv"
    
    db_url = get_database_url()
    run_etl_pipeline(input_file, db_url, file_format)
