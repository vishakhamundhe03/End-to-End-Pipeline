# COVID Data Pipeline - Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     AIRFLOW ORCHESTRATION LAYER                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐          │
│  │   Webserver  │      │  Scheduler   │      │    Metadata  │          │
│  │  (Port 8080) │      │  (Daemon)    │      │   Database   │          │
│  └──────────────┘      └──────────────┘      └──────────────┘          │
│                                                                          │
│  TASKS:                                                                  │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ 1. Build File Name    →  2. Upload to S3  →  3. Build COPY SQL │   │
│  │                                                                  │   │
│  │ 4. Load to Snowflake  →  5. Validate Data  →  6. Run dBT      │   │
│  │                                                                  │   │
│  │ 7. Notify Completion                                            │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
        ┌──────────────────┐  ┌──────────────┐  ┌──────────────────┐
        │   AWS S3         │  │  Snowflake   │  │   dBT Cloud      │
        │                  │  │              │  │  (Local/Cloud)   │
        │ ├─ Raw Data CSV  │  │ ├─ Raw Layer │  │                  │
        │ └─ Staging       │  │ ├─ Staging   │  │ ├─ Models        │
        │                  │  │ └─ Marts     │  │ ├─ Tests         │
        └──────────────────┘  └──────────────┘  │ └─ Docs          │
                                                  └──────────────────┘
```

## Data Flow

### Step 1: Generate File Name
```
Trigger: Daily at scheduled time (default: midnight UTC)
Input: Execution date (YYYY-MM-DD)
Process: Generate timestamped filename
Output: covid_YYYY-MM-DD.csv
```

### Step 2: Upload to S3
```
Input: Local CSV file from C:\data\covid\covid_YYYY-MM-DD.csv
Provider: LocalFilesystemToS3Operator
Destination: s3://covid-data-bucket/covid-data/covid_YYYY-MM-DD.csv
Error Handling: Retry up to 2 times with 5-minute delay
```

### Step 3: Generate Snowflake COPY Command
```
Input: S3 file location, credentials
Process: Build dynamic SQL for COPY command
Features:
  - Create external stage pointing to S3
  - Define CSV format with header row
  - Configure error handling
Output: Executable SQL statement
```

### Step 4: Load to Snowflake
```
Connection: snowflake_default
Target: COVID_DB.RAW.COVID_DATA
Process:
  - Execute COPY command
  - Skip 1 header row
  - Quote fields as needed
  - Continue on errors
Result: Data loaded into raw staging table
```

### Step 5: Data Quality Validation
```
Checks:
  - Record count validation
  - Null value detection
  - Duplicate detection
  - Date range validation
  - Statistical summary
Failure Mode: Warning logged, pipeline continues
```

### Step 6: Run dBT Transformations
```
Models Executed:
  - stg_covid_data (Staging layer)
  - fact_covid (Fact table)
  - country_covid (Aggregated by country)
  
Tests Included:
  - Not null constraints
  - Unique constraints
  - Custom validations
  
Output: Transformed data in dBT-managed schemas
```

### Step 7: Completion Notification
```
Event: Pipeline success/failure
Actions:
  - Log completion time
  - Send Slack notification (optional)
  - Send email notification (optional)
  - Record execution metrics
```

---

## Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Orchestration | Apache Airflow | 2.10.5 |
| Data Lake | AWS S3 | Latest |
| Data Warehouse | Snowflake | Any |
| Transformation | dBT | Any |
| Database (Airflow) | PostgreSQL/SQLite | 15/Latest |
| Task Queue | LocalExecutor | Built-in |
| Monitoring | Airflow UI | Built-in |

---

## Deployment Options

### 1. Local Development
```
Requirements:
- Python 3.9+
- PostgreSQL (optional, SQLite default)
- AWS Account (for S3)
- Snowflake Account
- dBT installed

Startup:
  airflow scheduler  # Terminal 1
  airflow webserver  # Terminal 2
```

### 2. Docker Compose (Recommended for Testing)
```
Components:
- PostgreSQL container (metadata store)
- Redis container (optional, for Celery)
- Airflow Webserver container
- Airflow Scheduler container

Startup:
  docker-compose up -d
  
Access:
  http://localhost:8080 (admin/admin)
```

### 3. Kubernetes (Production)
```
Use: Airflow KubernetesExecutor
Benefits:
- Scalability
- Isolation
- Resource optimization
- High availability
```

---

## Configuration Overview

### Environment Variables
```
AIRFLOW_HOME=/path/to/airflow
AIRFLOW__CORE__EXECUTOR=LocalExecutor
AIRFLOW__CORE__SQL_ALCHEMY_CONN=sqlite:///./airflow.db

# COVID-specific
COVID_S3_BUCKET=covid-data-bucket
COVID_S3_PREFIX=covid-data
SNOWFLAKE_DATABASE=COVID_DB
SNOWFLAKE_SCHEMA=RAW
DBT_PROJECT_DIR=/path/to/covid_project
```

### Airflow Variables
Set via UI or CLI:
```powershell
airflow variables set COVID_S3_BUCKET covid-data-bucket
airflow variables set SNOWFLAKE_DATABASE COVID_DB
# ... etc
```

### Airflow Connections
```
1. aws_default (AWS)
   - Type: AWS
   - Access Key: YOUR_KEY
   - Secret Key: YOUR_SECRET

2. snowflake_default (Snowflake)
   - Type: Snowflake
   - Host: account.snowflakecomputing.com
   - User: username
   - Password: password
```

---

## Execution Timeline

### Daily Execution (Typical)
```
00:00 UTC - Scheduler triggers DAG
00:00-00:02 - Generate filename
00:02-00:05 - Upload to S3 (~3 min for average file)
00:05-00:06 - Build COPY SQL
00:06-00:10 - Load to Snowflake (~4 min for ~1M rows)
00:10-00:11 - Data quality validation
00:11-00:20 - dBT transformations (~9 min for 3 models)
00:20-00:21 - Notify completion
─────────────────────────────
TOTAL: ~21 minutes (well under 2-hour SLA)
```

### Failure Scenarios
```
If Task 2 Fails (Upload to S3):
  → Retry immediately
  → Retry after 5 minutes
  → Alert after 2 failures

If Task 4 Fails (Load to Snowflake):
  → Entire pipeline stops
  → Downstream tasks marked as skipped
  → Notification sent to data team

If Task 6 Fails (dBT):
  → Data already loaded correctly
  → Transformations not available
  → Manual intervention may be needed
```

---

## Monitoring & Metrics

### Airflow UI Metrics
- Task duration
- Success/failure rates
- SLA compliance
- Retry history
- XCom variable passing

### Custom Metrics
- Records loaded
- Data quality check results
- dBT model row counts
- Transformation statistics

### Logging
```
Logs stored in: /airflow/logs/covid_batch_pipeline/
Format: {dag_id}/{task_id}/{execution_date}/{try_number}.log
```

---

## Maintenance Tasks

### Weekly
- Check DAG health and success rate
- Review logs for warnings
- Monitor S3 costs

### Monthly
- Update dBT models if needed
- Review and optimize Snowflake COPY settings
- Test disaster recovery procedures

### Quarterly
- Performance tuning review
- Capacity planning
- Security audit
- Cost optimization

---

## Key Features

✅ **Reliability**
- Automatic retries with exponential backoff
- Error handling and logging
- Data quality checks
- SLA monitoring

✅ **Scalability**
- Can handle increasing data volume
- Configurable parallelism
- Docker/Kubernetes ready

✅ **Observability**
- Web UI dashboard
- Detailed logging
- Metrics and monitoring
- Email/Slack alerts

✅ **Maintainability**
- Well-documented configuration
- Version controlled DAGs
- Clear error messages
- Production-ready setup

---

## Troubleshooting Guide

See [README.md](README.md) for comprehensive troubleshooting section.

Quick commands:
```powershell
# View DAG
airflow dags show covid_batch_pipeline

# Test DAG
airflow dags test covid_batch_pipeline 2026-03-31

# View variables
airflow variables list

# View connections
airflow connections list

# Trigger manually
airflow dags trigger covid_batch_pipeline
```

---

## Resources

- [Airflow Documentation](https://airflow.apache.org/)
- [Snowflake + Airflow](https://airflow.apache.org/docs/apache-airflow-providers-snowflake/)
- [AWS Provider](https://airflow.apache.org/docs/apache-airflow-providers-amazon/)
- [dBT Documentation](https://docs.getdbt.com/)

