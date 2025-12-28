"""
Airflow DAG for ETL Pipeline Test.

Tests ETL capabilities with different data sizes.
"""

from datetime import datetime, timedelta
from pathlib import Path
import sys

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable

# Add shared module to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "shared"))

from etl_operations import extract_data, transform_data, create_summary, load_to_database
from database_utils import get_database_url, truncate_tables


# Configuration
DB_URL = get_database_url(
    host=Variable.get("db_host", default_var="localhost"),
    port=int(Variable.get("db_port", default_var="5432")),
    database=Variable.get("db_name", default_var="orchestrator_test"),
    user=Variable.get("db_user", default_var="postgres"),
    password=Variable.get("db_password", default_var="postgres"),
)

DATA_DIR = Path(__file__).parent.parent.parent / "data" / "raw"


def extract_task(file_path: str, file_format: str = "csv", **context):
    """Extract data from file."""
    df = extract_data(file_path, file_format)
    # Push data shape to XCom for monitoring
    context["task_instance"].xcom_push(key="extracted_rows", value=len(df))
    return df.to_json(orient="split")  # Serialize for XCom


def transform_task(**context):
    """Transform extracted data."""
    import pandas as pd
    
    # Pull data from previous task
    json_data = context["task_instance"].xcom_pull(task_ids="extract_data")
    df = pd.read_json(json_data, orient="split")
    
    df_transformed = transform_data(df)
    context["task_instance"].xcom_push(key="transformed_rows", value=len(df_transformed))
    return df_transformed.to_json(orient="split")


def create_summary_task(**context):
    """Create summary statistics."""
    import pandas as pd
    
    json_data = context["task_instance"].xcom_pull(task_ids="transform_data")
    df = pd.read_json(json_data, orient="split")
    
    df_summary = create_summary(df)
    return df_summary.to_json(orient="split")


def load_main_data_task(**context):
    """Load transformed data to database."""
    import pandas as pd
    
    json_data = context["task_instance"].xcom_pull(task_ids="transform_data")
    df = pd.read_json(json_data, orient="split")
    
    load_to_database(df, "transactions", DB_URL, if_exists="replace")


def load_summary_data_task(**context):
    """Load summary data to database."""
    import pandas as pd
    
    json_data = context["task_instance"].xcom_pull(task_ids="create_summary")
    df = pd.read_json(json_data, orient="split")
    
    load_to_database(df, "transaction_summary", DB_URL, if_exists="replace")


def log_metrics_task(**context):
    """Log pipeline metrics."""
    ti = context["task_instance"]
    extracted = ti.xcom_pull(key="extracted_rows", task_ids="extract_data")
    transformed = ti.xcom_pull(key="transformed_rows", task_ids="transform_data")
    
    print(f"\n{'='*60}")
    print("ETL Pipeline Metrics")
    print(f"{'='*60}")
    print(f"Extracted rows: {extracted:,}")
    print(f"Transformed rows: {transformed:,}")
    print(f"Data quality: {(transformed/extracted*100):.2f}%")
    print(f"{'='*60}\n")


# Default arguments
default_args = {
    "owner": "data-team",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
}


def create_etl_dag(dag_id: str, schedule: str, data_size: str):
    """Create ETL DAG for specific data size."""
    
    with DAG(
        dag_id=dag_id,
        default_args=default_args,
        description=f"ETL Pipeline - {data_size} dataset",
        schedule_interval=schedule,
        start_date=datetime(2025, 1, 1),
        catchup=False,
        tags=["etl", "benchmark", data_size],
    ) as dag:
        
        input_file = str(DATA_DIR / f"transactions_{data_size}.csv")
        
        extract = PythonOperator(
            task_id="extract_data",
            python_callable=extract_task,
            op_kwargs={"file_path": input_file, "file_format": "csv"},
        )
        
        transform = PythonOperator(
            task_id="transform_data",
            python_callable=transform_task,
        )
        
        summary = PythonOperator(
            task_id="create_summary",
            python_callable=create_summary_task,
        )
        
        load_main = PythonOperator(
            task_id="load_main_data",
            python_callable=load_main_data_task,
        )
        
        load_summary = PythonOperator(
            task_id="load_summary_data",
            python_callable=load_summary_data_task,
        )
        
        log_metrics = PythonOperator(
            task_id="log_metrics",
            python_callable=log_metrics_task,
        )
        
        # Define dependencies
        extract >> transform >> [summary, load_main]
        summary >> load_summary
        [load_main, load_summary] >> log_metrics
        
    return dag


# Create DAGs for different data sizes
etl_small = create_etl_dag("etl_pipeline_small", "@daily", "small")
etl_medium = create_etl_dag("etl_pipeline_medium", "@weekly", "medium")
etl_large = create_etl_dag("etl_pipeline_large", None, "large")  # Manual trigger only
