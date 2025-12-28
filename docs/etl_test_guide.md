# ETL Pipeline Test

This directory contains the ETL Pipeline test implementation for all three orchestrators.

## Test Overview

The ETL Pipeline test processes transaction data through three stages:
1. **Extract**: Read data from CSV/JSON/Parquet files
2. **Transform**: Clean, validate, and enrich the data
3. **Load**: Store results in PostgreSQL database

## Test Datasets

Three dataset sizes are provided:
- **Small**: 10,000 rows (~1MB)
- **Medium**: 1,000,000 rows (~100MB)  
- **Large**: 10,000,000 rows (~1GB)

## Setup

1. **Install dependencies**:
```bash
uv sync
```

2. **Start PostgreSQL** (with Docker):
```bash
docker run -d \
  --name postgres-test \
  -e POSTGRES_DB=orchestrator_test \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  postgres:16
```

3. **Setup test environment**:
```bash
python setup_test_env.py
```

This will:
- Create database tables
- Generate test datasets (small, medium, large)

## Running Tests

### Airflow

1. Start Airflow:
```bash
cd airflow
export AIRFLOW_HOME=$(pwd)
airflow db init
airflow users create \
  --username admin \
  --password admin \
  --firstname Admin \
  --lastname User \
  --role Admin \
  --email admin@example.com

airflow webserver &
airflow scheduler &
```

2. Access UI at http://localhost:8080
3. Enable and trigger DAGs:
   - `etl_pipeline_small`
   - `etl_pipeline_medium`
   - `etl_pipeline_large`

### Dagster

1. Start Dagster:
```bash
cd dagster
dagster dev -f etl_pipeline.py
```

2. Access UI at http://localhost:3000
3. Materialize assets or run jobs:
   - `etl_pipeline_small`
   - `etl_pipeline_medium`
   - `etl_pipeline_large`

### Prefect

1. Start Prefect server:
```bash
prefect server start
```

2. Run flows:
```bash
# Small dataset
python prefect/flows/etl_pipeline.py small

# Medium dataset
python prefect/flows/etl_pipeline.py medium

# Large dataset
python prefect/flows/etl_pipeline.py large
```

Or create deployments:
```bash
cd prefect/flows
prefect deploy etl_pipeline.py:etl_pipeline_small
prefect deploy etl_pipeline.py:etl_pipeline_medium
prefect deploy etl_pipeline.py:etl_pipeline_large
```

## What to Measure

### Performance Metrics
- Total execution time
- Task startup overhead
- Memory usage per task
- Parallelization efficiency

### Developer Experience
- Lines of code required
- Implementation complexity
- Debugging ease
- Type safety

### Operational Metrics
- Retry behavior on failure
- Error messages quality
- Monitoring/observability
- Resource utilization

## Expected Results

After successful execution, you should see:
- Data in `transactions` table
- Summary statistics in `transaction_summary` table
- Execution metrics in each orchestrator's UI

## Verification

Query the database to verify results:

```sql
-- Check loaded data
SELECT COUNT(*) FROM transactions;
SELECT * FROM transactions LIMIT 10;

-- Check summary
SELECT * FROM transaction_summary ORDER BY total_revenue DESC;

-- Verify data quality
SELECT 
  category,
  COUNT(*) as count,
  SUM(total_amount) as revenue,
  AVG(total_amount) as avg_order
FROM transactions
GROUP BY category;
```

## Troubleshooting

**Database connection errors**:
- Ensure PostgreSQL is running: `docker ps`
- Check connection parameters in `shared/database_utils.py`

**Missing data files**:
- Run `python setup_test_env.py` to generate datasets

**Import errors**:
- Ensure you're running from the project root
- Activate virtual environment: `source .venv/bin/activate`
