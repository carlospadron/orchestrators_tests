# Orchestrator Comparison: Airflow, Dagster & Prefect

A comprehensive benchmark and comparison project for evaluating three leading workflow orchestration tools for data engineering, data science, and spatial data processing workloads.

## 🎯 Objectives

- Compare **Apache Airflow**, **Dagster**, and **Prefect** across various dimensions
- Evaluate performance, developer experience, and operational characteristics
- Provide actionable insights for tool selection

## 🛠️ Tools Under Test

| Tool | Version | Description |
|------|---------|-------------|
| **Apache Airflow** | 3.x | Industry-standard workflow orchestration platform |
| **Dagster** | 1.x | Data orchestrator with asset-based paradigm |
| **Prefect** | 3.x | Modern workflow orchestration with dynamic DAGs |

## 📋 Test Categories

**Philosophy**: Tests use simple operations (sleep, basic math, file I/O) to focus on orchestrator capabilities, not Python processing complexity.

### 1. Task Definition & DAG Structure

#### 1.1 Simple Linear DAG
- **Description**: 5 sequential tasks (A → B → C → D → E)
- **Task Operation**: Each task sleeps 2s, prints task name, returns timestamp
- **Key Metrics**: 
  - Task definition syntax clarity
  - Parameter passing between tasks
  - Task execution order correctness
  - Total orchestration overhead

#### 1.2 Fan-Out/Fan-In Pattern
- **Description**: 1 task fans out to 10 parallel tasks, then aggregates
- **Structure**: `start → [task_1...task_10] → aggregate → end`
- **Task Operation**: Each parallel task sleeps 3s, returns random number
- **Key Metrics**:
  - Parallel execution handling
  - Result collection mechanism
  - DAG visualization clarity
  - Memory efficiency with task results

#### 1.3 Complex Dependency Graph
- **Description**: 20 tasks with mixed dependencies (diamond patterns, multiple paths)
- **Task Operation**: Simple arithmetic (add, multiply) with 1s sleep
- **Key Metrics**:
  - Dependency resolution correctness
  - Execution order optimization
  - DAG rendering performance
  - Code readability for complex flows

#### 1.4 Dynamic Task Generation
- **Description**: Generate N tasks at runtime based on config/input
- **Task Operation**: Process list of items discovered during execution
- **Key Metrics**:
  - Dynamic DAG support (native vs. workaround)
  - Code complexity for dynamic workflows
  - UI/visualization of dynamic tasks
  - Debugging capabilities

### 2. Scheduling & Triggers

#### 2.1 Cron-Based Scheduling
- **Description**: Test various schedules (hourly, daily, weekly, custom cron)
- **Task Operation**: Single task that logs execution time
- **Key Metrics**:
  - Schedule definition syntax
  - Accuracy of scheduled execution
  - Handling of DST and timezones
  - Missed run behavior (skip vs. catchup)

#### 2.2 Backfilling Historical Runs
- **Description**: Execute workflow for past 30 days
- **Task Operation**: Date-aware task that logs execution date
- **Key Metrics**:
  - Backfill command/API usability
  - Performance with many historical runs
  - Date parameter passing
  - Resource management during backfill

#### 2.3 Event-Driven Triggers
- **Description**: Trigger workflow on file arrival, API webhook, or sensor
- **Task Operation**: Simple validation of trigger payload
- **Key Metrics**:
  - Sensor/trigger implementation complexity
  - Resource consumption while waiting
  - Trigger-to-execution latency
  - Multiple trigger support

#### 2.4 Conditional Execution
- **Description**: Execute different branches based on runtime conditions
- **Task Operation**: Check condition (time, file exists, API status) → branch
- **Key Metrics**:
  - Conditional branching syntax
  - Skip task capability
  - UI visualization of skipped paths
  - State handling for conditional flows

### 3. Parallel Execution & Concurrency

#### 3.1 Maximum Parallelism Test
- **Description**: 100 independent tasks that can run simultaneously
- **Task Operation**: Each sleeps 10s
- **Key Metrics**:
  - Maximum concurrent tasks achieved
  - Worker/executor configuration complexity
  - Queue management behavior
  - Resource utilization efficiency

#### 3.2 Task Pools & Priority
- **Description**: Limited pool (5 slots), 20 tasks with different priorities
- **Task Operation**: Sleep 5s
- **Key Metrics**:
  - Pool/queue configuration
  - Priority execution order
  - Queue visibility in UI
  - Pool exhaustion handling

#### 3.3 Cross-DAG Dependencies
- **Description**: DAG B waits for DAG A to complete
- **Task Operation**: Simple status check
- **Key Metrics**:
  - Cross-DAG trigger mechanism
  - Data passing between DAGs
  - Deadlock prevention
  - UI visibility of cross-DAG dependencies

### 4. Retry Logic & Error Handling

#### 4.1 Task Retry on Failure
- **Description**: Task fails 2 times, succeeds on 3rd attempt
- **Task Operation**: Randomly fail with 66% probability
- **Key Metrics**:
  - Retry configuration (count, delay, exponential backoff)
  - Retry visibility in logs/UI
  - Total time with retries
  - State persistence between retries

#### 4.2 Partial Failure Recovery
- **Description**: 10 parallel tasks, 3 fail permanently
- **Task Operation**: Random success/failure
- **Key Metrics**:
  - Downstream task handling (run, skip, or fail?)
  - Manual task re-run capability
  - Failure notification/alerting
  - Resume from failure point

#### 4.3 Timeout Handling
- **Description**: Tasks with different timeout configurations
- **Task Operation**: Sleep longer than timeout limit
- **Key Metrics**:
  - Timeout configuration granularity
  - Timeout enforcement accuracy
  - Task cleanup after timeout
  - Timeout vs. retry interaction

#### 4.4 Exception Propagation
- **Description**: Test different exception types (temporary, permanent, data)
- **Task Operation**: Raise specific exceptions
- **Key Metrics**:
  - Exception type handling
  - Error message visibility
  - Callback hooks (on_failure, on_retry)
  - Integration with error tracking (Sentry, etc.)

### 5. Logging & Observability

#### 5.1 Task Log Management
- **Description**: Tasks generate various log volumes
- **Task Operation**: Print 100 lines, 10K lines, 1M lines
- **Key Metrics**:
  - Log streaming/buffering
  - Log search and filtering in UI
  - Log retention and rotation
  - Remote log storage integration

#### 5.2 Metrics & Monitoring
- **Description**: Expose workflow execution metrics
- **Task Operation**: Standard test with metric collection
- **Key Metrics**:
  - Built-in metrics (duration, success rate, queue depth)
  - Custom metric support
  - Prometheus/StatsD integration
  - Pre-built Grafana dashboards

#### 5.3 Execution History & Audit
- **Description**: Query past executions, analyze trends
- **Task Operation**: Run workflow 50 times
- **Key Metrics**:
  - Historical data retention
  - Query/filter capabilities
  - Trend visualization
  - Audit trail completeness

#### 5.4 Debugging Capabilities
- **Description**: Debug failed or slow tasks
- **Task Operation**: Tasks with intentional issues
- **Key Metrics**:
  - Local execution/testing mode
  - Task isolation for debugging
  - Variable inspection
  - Execution replay capability

### 6. Kubernetes & Scaling

#### 6.1 Kubernetes Deployment
- **Description**: Deploy orchestrator to K8s cluster
- **Task Operation**: Simple task to verify deployment
- **Key Metrics**:
  - Helm chart quality and documentation
  - Configuration complexity
  - Time to first successful run
  - Required K8s knowledge level

#### 6.2 Horizontal Scaling (Task Execution)
- **Description**: Scale workers/agents from 1 to 10 based on load
- **Task Operation**: Submit 100 tasks, monitor worker scaling
- **Key Metrics**:
  - Auto-scaling configuration
  - Scale-up time (task queue → new worker)
  - Scale-down behavior (idle timeout)
  - Worker startup overhead

#### 6.3 Task Isolation with K8s Pods
- **Description**: Run each task in isolated K8s pod
- **Task Operation**: Task with specific resource requirements
- **Key Metrics**:
  - Pod startup latency
  - Resource request/limit configuration
  - Pod cleanup reliability
  - Task-to-pod overhead ratio

#### 6.4 Resource Constraints
- **Description**: Run workflows with CPU/memory limits
- **Task Operation**: Tasks with known resource usage
- **Key Metrics**:
  - Resource limit enforcement
  - Behavior when limits exceeded
  - Task queuing with resource constraints
  - Node affinity/selector support

#### 6.5 High Availability Testing
- **Description**: Kill scheduler/webserver pods during execution
- **Task Operation**: Long-running workflow (50 tasks)
- **Key Metrics**:
  - Recovery time after pod restart
  - Task state persistence
  - Zero-downtime deployment support
  - Leader election (if applicable)

### 7. Developer Experience

#### 7.1 Local Development Setup
- **Description**: Time to first "Hello World" workflow
- **Key Metrics**:
  - Installation steps
  - Required dependencies
  - Local execution mode
  - Documentation quality

#### 7.2 Testing Workflows
- **Description**: Unit test a workflow without running orchestrator
- **Key Metrics**:
  - Testing framework availability
  - Mock/fixture support
  - CI/CD integration ease
  - Test execution speed

#### 7.3 Version Control & GitOps
- **Description**: Manage workflows as code in Git
- **Key Metrics**:
  - File structure for version control
  - Workflow versioning support
  - Diff visibility for changes
  - Deployment from Git (ArgoCD, etc.)

#### 7.4 IDE Support & Type Safety
- **Description**: Workflow development in VS Code/PyCharm
- **Key Metrics**:
  - Autocomplete quality
  - Type hints support
  - Linting/validation
  - Refactoring support

## 🎯 Evaluation Criteria

### Developer Experience (35%)
- **Ease of workflow definition**: Syntax clarity, boilerplate required
- **Local development**: Setup time, testing without infrastructure
- **Documentation quality**: Examples, API docs, troubleshooting guides
- **IDE support**: Autocomplete, type hints, refactoring
- **Debugging**: Error messages, local execution, task isolation
- **Learning curve**: Time to productivity for new developers

### Orchestrator Features (30%)
- **Scheduling**: Cron, intervals, event-based triggers
- **Task dependencies**: Complex DAGs, dynamic generation
- **Parallel execution**: Concurrency, pooling, priority queues
- **Retry logic**: Configuration, exponential backoff, conditional retries
- **State management**: Parameter passing, XCom/artifacts
- **Conditional execution**: Branching, skip tasks

### Operational Excellence (25%)
- **Monitoring**: Built-in metrics, Prometheus integration, dashboards
- **Logging**: Log aggregation, search, retention
- **Error handling**: Failure recovery, alerting, notifications
- **Scalability**: Horizontal scaling, resource efficiency
- **High availability**: Fault tolerance, zero-downtime deployments
- **Deployment**: Helm charts, configuration management

### Kubernetes Integration (10%)
- **K8s executor quality**: Pod isolation, resource limits
- **Scaling behavior**: HPA, worker autoscaling
- **Resource efficiency**: Overhead, startup time
- **HA in K8s**: Pod failures, state persistence
- **Deployment complexity**: Configuration, upgrades

## 📊 Benchmark Metrics

For each test, we measure:

### Orchestrator Metrics
- **Task Overhead**: Time from task submission to start execution
- **Scheduling Accuracy**: Deviation from expected schedule time
- **Parallelism Efficiency**: Actual vs. theoretical parallel execution
- **Retry Latency**: Time between retry attempts
- **State Persistence**: Time to save/load task state

### Developer Metrics
- **Lines of Code**: Workflow definition size
- **Time to Implement**: Development time for each test
- **Configuration Complexity**: Number of settings required
- **Debug Time**: Time to identify and fix intentional bugs

### Operational Metrics
- **Resource Usage**: CPU, memory, disk I/O during execution
- **Log Volume**: Bytes generated per task
- **UI Response Time**: Dashboard load time with N DAGs
- **Query Performance**: Time to fetch execution history

### Kubernetes Metrics
- **Pod Startup Time**: Container pull + init time
- **Worker Scale-up Time**: From task queue to ready worker
- **Resource Overhead**: Idle consumption (scheduler, webserver)
- **HA Recovery Time**: Time to restore after component failure

## 🏗️ Project Structure

```
orchestrators_tests/
├── airflow/
│   ├── dags/
│   │   ├── 01_simple_linear.py
│   │   ├── 02_fan_out_fan_in.py
│   │   ├── 03_complex_dependencies.py
│   │   ├── 04_dynamic_tasks.py
│   │   ├── 05_retry_logic.py
│   │   ├── 06_parallel_execution.py
│   │   └── 07_conditional_branching.py
│   ├── k8s/
│   │   ├── helm-values.yaml
│   │   ├── keda-scaler.yaml
│   │   └── resource-limits.yaml
│   └── tests/
│       └── test_dags.py
├── dagster/
│   ├── jobs/
│   │   ├── simple_linear.py
│   │   ├── fan_out_fan_in.py
│   │   ├── complex_dependencies.py
│   │   └── retry_logic.py
│   ├── k8s/
│   │   ├── helm-values.yaml
│   │   └── resource-limits.yaml
│   └── tests/
│       └── test_jobs.py
├── prefect/
│   ├── flows/
│   │   ├── simple_linear.py
│   │   ├── fan_out_fan_in.py
│   │   ├── complex_dependencies.py
│   │   └── retry_logic.py
│   ├── k8s/
│   │   ├── helm-values.yaml
│   │   └── resource-limits.yaml
│   └── tests/
│       └── test_flows.py
├── shared/
│   ├── tasks.py              # Simple reusable task functions
│   ├── benchmark_utils.py    # Metric collection
│   └── chaos.py              # Failure injection utilities
├── k8s/
│   ├── minikube-setup.sh
│   ├── monitoring/
│   │   ├── prometheus.yaml
│   │   └── grafana-dashboards/
│   └── chaos-mesh/           # For HA testing
├── results/
│   ├── metrics/              # Raw benchmark data
│   └── reports/              # Generated analysis
├── notebooks/
│   └── analysis.ipynb        # Results visualization
└── docs/
    ├── setup.md
    ├── running-tests.md
    └── findings.md
```

## 🚀 Getting Started

### Prerequisites
```bash
- Python 3.12+
- uv (https://docs.astral.sh/uv/)
- Docker & Docker Compose
- Kubernetes cluster (minikube/kind for local, optional for K8s tests)
- kubectl CLI tool (if running K8s tests)
- Helm 3.x (if running K8s tests)
- PostgreSQL 14+ (can use Docker container)
- 4GB+ RAM (8GB for K8s tests)
```

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd orchestrators_tests
```

2. Initialize project with uv:
```bash
# uv sync automatically creates venv and installs dependencies
uv sync
```

3. Set up each orchestrator:
```bash
# Airflow
cd airflow && docker-compose up -d

# Dagster
cd dagster && dagster dev

# Prefect
cd prefect && prefect server start
```

## 📦 Dependencies

**Key Principle**: Minimal dependencies - focus on orchestrator features, not data processing libraries.

### Core (All Orchestrators)
- `python = "^3.12"`
- `psycopg2-binary` - PostgreSQL connectivity
- `requests` - For API trigger tests

### Orchestrators
- `apache-airflow[postgres]` - Airflow with PostgreSQL support
- `dagster`, `dagster-webserver`, `dagster-postgres` - Dagster stack
- `prefect`, `prefect-sqlalchemy` - Prefect with database support

### Testing & Benchmarking
- `pytest` - Test framework
- `pytest-benchmark` - Performance testing
- `pandas` - Results analysis only
- `matplotlib`, `seaborn` - Visualization

### Optional (K8s Tests)
- `kubernetes` - K8s Python client for automation
- `prometheus-client` - Custom metrics

## 🧪 Running Tests

### Quick Start - Basic Tests
```bash
# Run a simple linear DAG on each orchestrator
python scripts/run_test.py --test simple_linear --orchestrator airflow
python scripts/run_test.py --test simple_linear --orchestrator dagster
python scripts/run_test.py --test simple_linear --orchestrator prefect
```

### Run Test Category
```bash
# Run all retry/error handling tests
python scripts/run_benchmark.py --category retry_logic --all-orchestrators

# Run all parallel execution tests
python scripts/run_benchmark.py --category parallel_execution --all-orchestrators
```

### Run Full Benchmark Suite
```bash
# Run all tests (excludes K8s tests by default)
python scripts/run_benchmark.py --all

# Include Kubernetes tests (requires K8s cluster)
python scripts/run_benchmark.py --all --include-k8s
```

### Kubernetes Tests
```bash
# Setup local K8s cluster
./k8s/minikube-setup.sh

# Deploy orchestrators to K8s
python scripts/deploy_k8s.py --orchestrator airflow
python scripts/deploy_k8s.py --orchestrator dagster
python scripts/deploy_k8s.py --orchestrator prefect

# Run K8s-specific tests
python scripts/run_benchmark.py --category kubernetes --all-orchestrators
```

### Generate Report
```bash
# Create comprehensive comparison report
python scripts/generate_report.py --format html --output results/report.html

# Quick CLI summary
python scripts/generate_report.py --format cli
```

## 📈 Expected Outputs

### Test Results
- **Execution Logs**: Detailed logs for each workflow run
- **Metrics JSON**: Raw performance data (timing, resources, overhead)
- **Screenshots**: UI captures for each test scenario
- **Error Logs**: Intentional failure scenarios and recovery

### Benchmark Reports
- **HTML Dashboard**: Interactive comparison across all dimensions
- **PDF Report**: Executive summary with recommendations
- **CSV Data**: Raw metrics for custom analysis
- **Comparison Matrix**: Side-by-side feature comparison

### Visualizations
- **Execution Time Charts**: Task overhead by orchestrator
- **Parallelism Graphs**: Actual vs. theoretical parallel execution
- **Resource Usage**: CPU/Memory consumption over time
- **Scaling Behavior**: Worker autoscaling patterns (K8s tests)
- **Developer Experience**: LOC, complexity scores

## 🤝 Contributing

Contributions welcome! Areas of interest:
- Additional orchestrator capability tests
- Alternative orchestrators (Argo Workflows, Temporal, etc.)
- Performance optimizations
- K8s deployment improvements
- Documentation enhancements

## 📄 License

See LICENSE file for details.

## 📚 References

- [Apache Airflow Documentation](https://airflow.apache.org/docs/)
- [Dagster Documentation](https://docs.dagster.io/)
- [Prefect Documentation](https://docs.prefect.io/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [KEDA (Kubernetes Event-Driven Autoscaling)](https://keda.sh/) 
