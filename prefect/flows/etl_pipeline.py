"""
Prefect flow for ETL Pipeline Test.

Tests ETL capabilities with different data sizes.
"""

from pathlib import Path
from typing import Dict, Literal
import sys

import pandas as pd
from prefect import flow, task
from prefect.artifacts import create_table_artifact, create_markdown_artifact

# Add shared module to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "shared"))

from etl_operations import extract_data, transform_data, create_summary, load_to_database
from database_utils import get_database_url


# Configuration
DATA_DIR = Path(__file__).parent.parent.parent / "data" / "raw"
DB_URL = get_database_url()


@task(name="Extract Data", retries=3, retry_delay_seconds=60)
def extract_task(
    file_path: Path,
    file_format: Literal["csv", "json", "parquet"] = "csv",
) -> pd.DataFrame:
    """Extract data from file."""
    df = extract_data(file_path, file_format)
    return df


@task(name="Transform Data")
def transform_task(df: pd.DataFrame) -> pd.DataFrame:
    """Transform extracted data."""
    df_transformed = transform_data(df)
    return df_transformed


@task(name="Create Summary")
def create_summary_task(df: pd.DataFrame) -> pd.DataFrame:
    """Create summary statistics."""
    df_summary = create_summary(df)
    return df_summary


@task(name="Load Main Data", retries=2)
def load_main_data_task(df: pd.DataFrame, database_url: str):
    """Load transformed data to database."""
    load_to_database(df, "transactions", database_url, if_exists="replace")


@task(name="Load Summary Data", retries=2)
def load_summary_data_task(df: pd.DataFrame, database_url: str):
    """Load summary data to database."""
    load_to_database(df, "transaction_summary", database_url, if_exists="replace")


@task(name="Create Metrics Artifact")
def create_metrics_artifact(
    raw_df: pd.DataFrame,
    transformed_df: pd.DataFrame,
    summary_df: pd.DataFrame,
):
    """Create metrics artifact for monitoring."""
    data_quality = (len(transformed_df) / len(raw_df)) * 100
    
    # Create markdown artifact
    markdown = f"""
# ETL Pipeline Metrics

## Data Processing
- **Extracted Rows**: {len(raw_df):,}
- **Transformed Rows**: {len(transformed_df):,}
- **Data Quality**: {data_quality:.2f}%
- **Rows Removed**: {len(raw_df) - len(transformed_df):,}

## Business Metrics
- **Categories**: {len(summary_df)}
- **Total Revenue**: ${summary_df['total_revenue'].sum():,.2f}
- **Average Order Value**: ${summary_df['avg_order_value'].mean():,.2f}
- **Total Transactions**: {summary_df['total_transactions'].sum():,}
"""
    
    create_markdown_artifact(
        key="etl-metrics",
        markdown=markdown,
        description="ETL pipeline execution metrics",
    )
    
    # Create summary table artifact
    create_table_artifact(
        key="category-summary",
        table=summary_df.to_dict("records"),
        description="Transaction summary by category",
    )


@flow(
    name="ETL Pipeline",
    description="Extract, Transform, and Load transaction data",
    log_prints=True,
)
def etl_pipeline(
    data_size: Literal["small", "medium", "large"] = "small",
    file_format: Literal["csv", "json", "parquet"] = "csv",
) -> Dict:
    """
    Run complete ETL pipeline.
    
    Args:
        data_size: Size of dataset to process (small, medium, large)
        file_format: Input file format (csv, json, parquet)
        
    Returns:
        Dictionary with pipeline metrics
    """
    print(f"\n{'='*60}")
    print(f"Starting ETL Pipeline - {data_size} dataset")
    print(f"{'='*60}\n")
    
    # Construct file path
    input_file = DATA_DIR / f"transactions_{data_size}.{file_format}"
    
    # Extract
    raw_df = extract_task(input_file, file_format)
    
    # Transform
    transformed_df = transform_task(raw_df)
    
    # Create summary
    summary_df = create_summary_task(transformed_df)
    
    # Load in parallel
    load_main_data_task.submit(transformed_df, DB_URL)
    load_summary_data_task.submit(summary_df, DB_URL)
    
    # Create metrics
    create_metrics_artifact(raw_df, transformed_df, summary_df)
    
    print(f"\n{'='*60}")
    print("✓ ETL Pipeline completed successfully!")
    print(f"{'='*60}\n")
    
    return {
        "rows_processed": len(transformed_df),
        "categories": len(summary_df),
        "total_revenue": float(summary_df["total_revenue"].sum()),
        "data_quality_pct": (len(transformed_df) / len(raw_df)) * 100,
    }


# Create deployment-ready flows for different sizes
@flow(name="ETL Pipeline - Small")
def etl_pipeline_small():
    """ETL pipeline for small dataset (10K rows)."""
    return etl_pipeline(data_size="small")


@flow(name="ETL Pipeline - Medium")
def etl_pipeline_medium():
    """ETL pipeline for medium dataset (1M rows)."""
    return etl_pipeline(data_size="medium")


@flow(name="ETL Pipeline - Large")
def etl_pipeline_large():
    """ETL pipeline for large dataset (10M rows)."""
    return etl_pipeline(data_size="large")


if __name__ == "__main__":
    # Run locally for testing
    import sys
    
    size = sys.argv[1] if len(sys.argv) > 1 else "small"
    result = etl_pipeline(data_size=size)
    print(f"\nPipeline Results: {result}")
