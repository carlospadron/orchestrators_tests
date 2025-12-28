"""Data generators for benchmark tests."""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Literal

import pandas as pd


def generate_sample_data(
    num_rows: int,
    output_format: Literal["csv", "json", "parquet"] = "csv",
    output_path: str | Path | None = None,
) -> pd.DataFrame:
    """
    Generate sample e-commerce transaction data.
    
    Args:
        num_rows: Number of rows to generate
        output_format: Output format (csv, json, parquet)
        output_path: Path to save the file. If None, returns DataFrame only
        
    Returns:
        DataFrame with generated data
    """
    # Generate realistic transaction data
    categories = ["Electronics", "Clothing", "Books", "Home & Garden", "Sports", "Toys"]
    statuses = ["completed", "pending", "cancelled", "refunded"]
    payment_methods = ["credit_card", "debit_card", "paypal", "crypto"]
    
    start_date = datetime(2023, 1, 1)
    
    data = {
        "transaction_id": [f"TXN{i:08d}" for i in range(num_rows)],
        "customer_id": [f"CUST{random.randint(1, num_rows // 10):06d}" for _ in range(num_rows)],
        "product_name": [f"Product_{random.randint(1, 1000)}" for _ in range(num_rows)],
        "category": [random.choice(categories) for _ in range(num_rows)],
        "quantity": [random.randint(1, 10) for _ in range(num_rows)],
        "unit_price": [round(random.uniform(5.0, 500.0), 2) for _ in range(num_rows)],
        "total_amount": [0.0] * num_rows,  # Will calculate below
        "discount_percent": [random.choice([0, 5, 10, 15, 20]) for _ in range(num_rows)],
        "tax_rate": [0.08] * num_rows,  # 8% tax
        "payment_method": [random.choice(payment_methods) for _ in range(num_rows)],
        "status": [random.choice(statuses) for _ in range(num_rows)],
        "transaction_date": [
            (start_date + timedelta(days=random.randint(0, 700))).strftime("%Y-%m-%d %H:%M:%S")
            for _ in range(num_rows)
        ],
        "shipping_country": [
            random.choice(["USA", "Canada", "UK", "Germany", "France", "Australia"])
            for _ in range(num_rows)
        ],
        "customer_email": [
            f"customer{random.randint(1, num_rows // 10)}@example.com"
            for _ in range(num_rows)
        ],
    }
    
    df = pd.DataFrame(data)
    
    # Calculate total_amount
    df["total_amount"] = (
        df["quantity"] * df["unit_price"] * (1 - df["discount_percent"] / 100) * (1 + df["tax_rate"])
    ).round(2)
    
    # Save to file if path provided
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if output_format == "csv":
            df.to_csv(output_path, index=False)
        elif output_format == "json":
            df.to_json(output_path, orient="records", lines=True)
        elif output_format == "parquet":
            df.to_parquet(output_path, index=False)
            
        print(f"Generated {num_rows} rows and saved to {output_path}")
    
    return df


def create_test_datasets(base_path: str | Path = "data/raw"):
    """Create all test datasets (small, medium, large)."""
    base_path = Path(base_path)
    
    datasets = {
        "small": 10_000,
        "medium": 1_000_000,
        "large": 10_000_000,
    }
    
    for size_name, num_rows in datasets.items():
        print(f"\nGenerating {size_name} dataset ({num_rows:,} rows)...")
        
        # CSV format
        csv_path = base_path / f"transactions_{size_name}.csv"
        generate_sample_data(num_rows, "csv", csv_path)
        
        # JSON format
        json_path = base_path / f"transactions_{size_name}.json"
        generate_sample_data(num_rows, "json", json_path)
        
        # Parquet format
        parquet_path = base_path / f"transactions_{size_name}.parquet"
        generate_sample_data(num_rows, "parquet", parquet_path)
    
    print("\n✓ All datasets generated successfully!")


if __name__ == "__main__":
    create_test_datasets()
