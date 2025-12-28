"""Setup test environment: generate data and create database tables."""

import sys
from pathlib import Path

# Add shared to path
sys.path.insert(0, str(Path(__file__).parent / "shared"))

from data_generators import create_test_datasets
from database_utils import create_tables, get_database_url


def setup_environment():
    """Set up complete test environment."""
    print("\n" + "="*70)
    print("Setting up ETL Test Environment")
    print("="*70)
    
    # Step 1: Create database tables
    print("\n[1/2] Creating database tables...")
    try:
        db_url = get_database_url()
        create_tables(db_url)
    except Exception as e:
        print(f"⚠ Database setup failed: {e}")
        print("  Make sure PostgreSQL is running and accessible")
        print(f"  Connection: {db_url}")
        return False
    
    # Step 2: Generate test datasets
    print("\n[2/2] Generating test datasets...")
    try:
        create_test_datasets()
    except Exception as e:
        print(f"✗ Dataset generation failed: {e}")
        return False
    
    print("\n" + "="*70)
    print("✓ Test environment setup complete!")
    print("="*70)
    print("\nYou can now run the ETL pipelines:")
    print("  - Airflow: Navigate to http://localhost:8080")
    print("  - Dagster: Run 'dagster dev' in the dagster directory")
    print("  - Prefect: Run 'python prefect/flows/etl_pipeline.py'")
    print()
    
    return True


if __name__ == "__main__":
    success = setup_environment()
    sys.exit(0 if success else 1)
