"""
Dagster assets for ETL Pipeline Test.

Tests ETL capabilities with different data sizes using Software-Defined Assets.
"""

from pathlib import Path
from typing import Dict
import sys

import pandas as pd
from dagster import (
    asset,
    AssetExecutionContext,
    MetadataValue,
    Output,
    Config,
    op,
    job,
    AssetIn,
    DailyPartitionsDefinition,
)

# Add shared module to path
sys.path.insert(0, str(Path(__file__).parent.parent / "shared"))

from etl_operations import extract_data, transform_data, create_summary, load_to_database
from database_utils import get_database_url


# Configuration
DATA_DIR = Path(__file__).parent.parent / "data" / "raw"
DB_URL = get_database_url()


class ETLConfig(Config):
    """ETL pipeline configuration."""
    data_size: str = "small"
    file_format: str = "csv"


@asset(
    description="Raw transaction data extracted from source files",
    compute_kind="pandas",
)
def raw_transactions(config: ETLConfig, context: AssetExecutionContext) -> Output[pd.DataFrame]:
    """Extract raw transaction data."""
    input_file = DATA_DIR / f"transactions_{config.data_size}.{config.file_format}"
    
    context.log.info(f"Extracting data from {input_file}")
    df = extract_data(input_file, config.file_format)
    
    return Output(
        df,
        metadata={
            "num_rows": len(df),
            "num_columns": len(df.columns),
            "file_size_mb": input_file.stat().st_size / (1024 * 1024),
            "preview": MetadataValue.md(df.head().to_markdown()),
        },
    )


@asset(
    description="Cleaned and transformed transaction data",
    compute_kind="pandas",
    ins={"raw_transactions": AssetIn()},
)
def transformed_transactions(
    context: AssetExecutionContext,
    raw_transactions: pd.DataFrame,
) -> Output[pd.DataFrame]:
    """Transform raw transaction data."""
    context.log.info(f"Transforming {len(raw_transactions):,} rows")
    
    df_transformed = transform_data(raw_transactions)
    
    # Calculate data quality metrics
    data_quality = (len(df_transformed) / len(raw_transactions)) * 100
    
    return Output(
        df_transformed,
        metadata={
            "num_rows": len(df_transformed),
            "data_quality_pct": data_quality,
            "rows_removed": len(raw_transactions) - len(df_transformed),
            "categories": df_transformed["category"].nunique(),
            "date_range": f"{df_transformed['transaction_date'].min()} to {df_transformed['transaction_date'].max()}",
            "preview": MetadataValue.md(df_transformed.head().to_markdown()),
        },
    )


@asset(
    description="Transaction summary statistics by category",
    compute_kind="pandas",
    ins={"transformed_transactions": AssetIn()},
)
def transaction_summary(
    context: AssetExecutionContext,
    transformed_transactions: pd.DataFrame,
) -> Output[pd.DataFrame]:
    """Create transaction summary."""
    context.log.info("Creating summary statistics")
    
    df_summary = create_summary(transformed_transactions)
    
    return Output(
        df_summary,
        metadata={
            "num_categories": len(df_summary),
            "total_revenue": float(df_summary["total_revenue"].sum()),
            "avg_order_value": float(df_summary["avg_order_value"].mean()),
            "summary_table": MetadataValue.md(df_summary.to_markdown()),
        },
    )


@asset(
    description="Transactions loaded to PostgreSQL database",
    compute_kind="postgres",
    ins={"transformed_transactions": AssetIn()},
)
def transactions_db(
    context: AssetExecutionContext,
    transformed_transactions: pd.DataFrame,
) -> Output[None]:
    """Load transactions to database."""
    context.log.info(f"Loading {len(transformed_transactions):,} rows to database")
    
    load_to_database(
        transformed_transactions,
        "transactions",
        DB_URL,
        if_exists="replace",
    )
    
    return Output(
        None,
        metadata={
            "rows_loaded": len(transformed_transactions),
            "table_name": "transactions",
        },
    )


@asset(
    description="Transaction summary loaded to PostgreSQL database",
    compute_kind="postgres",
    ins={"transaction_summary": AssetIn()},
)
def transaction_summary_db(
    context: AssetExecutionContext,
    transaction_summary: pd.DataFrame,
) -> Output[None]:
    """Load transaction summary to database."""
    context.log.info(f"Loading {len(transaction_summary)} summary rows to database")
    
    load_to_database(
        transaction_summary,
        "transaction_summary",
        DB_URL,
        if_exists="replace",
    )
    
    return Output(
        None,
        metadata={
            "rows_loaded": len(transaction_summary),
            "table_name": "transaction_summary",
        },
    )


# Define asset groups for different data sizes
from dagster import define_asset_job, AssetSelection

# Jobs for different data sizes
etl_small_job = define_asset_job(
    name="etl_pipeline_small",
    selection=AssetSelection.all(),
    description="ETL pipeline for small dataset (10K rows)",
    config={
        "ops": {
            "raw_transactions": {
                "config": {"data_size": "small", "file_format": "csv"}
            }
        }
    },
)

etl_medium_job = define_asset_job(
    name="etl_pipeline_medium",
    selection=AssetSelection.all(),
    description="ETL pipeline for medium dataset (1M rows)",
    config={
        "ops": {
            "raw_transactions": {
                "config": {"data_size": "medium", "file_format": "csv"}
            }
        }
    },
)

etl_large_job = define_asset_job(
    name="etl_pipeline_large",
    selection=AssetSelection.all(),
    description="ETL pipeline for large dataset (10M rows)",
    config={
        "ops": {
            "raw_transactions": {
                "config": {"data_size": "large", "file_format": "csv"}
            }
        }
    },
)
