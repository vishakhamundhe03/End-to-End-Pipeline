# Airflow Batch Pipeline for COVID Data Processing

## Overview
This Airflow DAG orchestrates a complete data pipeline for COVID-19 data processing:

```
Local Data → S3 Bucket → Snowflake (Raw) → dBT Transformations → Analytics Tables
```

## Architecture

### Pipeline Flow
1. **Build File Name**: Generate timestamped file name (e.g., `covid_2026-03-31.csv`)
2. **Upload to S3**: Transfer local CSV file to AWS S3 bucket
3. **Build COPY SQL**: Generate dynamic Snowflake COPY command
4. **Load to Snowflake**: Execute COPY command to load data into RAW schema
5. **Validate Data Quality**: Run data quality checks
6. **Run dBT Transformations**: Execute dBT models for staging and marts
7. **Notify Completion**: Send notifications (Slack, email, etc.)

### Scheduled Execution
- **Schedule**: Daily at midnight UTC (`@daily`)
- **SLA**: 2 hours
- **Retries**: 2 attempts with 5-minute delay between retries
- **Catchup**: Disabled (only runs for current and future dates)

## Prerequisites

### Required Software
- Apache Airflow 2.10.5+
- Python 3.9+
- dBT (for transformations)
- AWS CLI (optional, for S3 management)

### AWS Setup
1. Create S3 bucket for data staging (e.g., `covid-data-bucket`)
2. Create IAM user with S3 access permissions
3. Generate Access Key ID and Secret Access Key

### Snowflake Setup
1. Create database: `COVID_DB`
2. Create schema: `RAW` (for staging data)
3. Create table: `COVID_DATA` with appropriate columns
4. Create warehouse: `COMPUTE_WH` (or existing warehouse)

### Local Data
- Place COVID data CSV files in: `C:\data\covid\`
- File naming format: `covid_YYYY-MM-DD.csv`
- CSV header row required

## Installation & Configuration

### Step 1: Install Requirements
```powershell
cd covid_project\airflow
pip install -r requirements.txt
```

### Step 2: Initialize Airflow Database
```powershell
airflow db upgrade
```

### Step 3: Create Admin User
```powershell
airflow users create `
  --username admin `
  --password admin `
  --firstname Admin `
  --lastname Admin `
  --role Admin `
  --email admin@example.com
```

### Step 4: Configure Environment Variables
Edit `setup_airflow_env.ps1` with your credentials:

```powershell
.\setup_airflow_env.ps1 `
  -AwsAccessKey "YOUR_AWS_ACCESS_KEY" `
  -AwsSecretKey "YOUR_AWS_SECRET_KEY" `
  -SnowflakeUser "YOUR_SF_USER" `
  -SnowflakePassword "YOUR_SF_PASSWORD" `
  -SnowflakeAccount "YOUR_SF_ACCOUNT" `
  -S3Bucket "covid-data-bucket" `
  -SnowflakeDatabase "COVID_DB" `
  -SnowflakeSchema "RAW"
```

### Step 5: Start Airflow Services

**Terminal 1 - Start Scheduler:**
```powershell
airflow scheduler
```

**Terminal 2 - Start Web Server:**
```powershell
airflow webserver --port 8080
```

Access Airflow UI: http://localhost:8080

## Configuration Variables

The following Airflow variables must be configured:

| Variable | Description | Example |
|----------|-------------|---------|
| `COVID_S3_BUCKET` | S3 bucket name | `covid-data-bucket` |
| `COVID_S3_PREFIX` | S3 folder path | `covid-data` |
| `LOCAL_COVID_FILE_DIR` | Local data directory | `C:\data\covid` |
| `SNOWFLAKE_DATABASE` | Snowflake database | `COVID_DB` |
| `SNOWFLAKE_SCHEMA` | Snowflake schema | `RAW` |
| `SNOWFLAKE_WAREHOUSE` | Snowflake warehouse | `COMPUTE_WH` |
| `DBT_PROJECT_DIR` | dBT project directory | `C:\...\covid_project` |
| `DBT_EXECUTABLE` | dBT executable path | `.dbt-venv\Scripts\dbt.exe` |

## Connections

### AWS Connection (`aws_default`)
- **Type**: AWS
- **Access Key ID**: Your AWS access key
- **Secret Access Key**: Your AWS secret key

### Snowflake Connection (`snowflake_default`)
- **Type**: Snowflake
- **Host**: `<account>.snowflakecomputing.com`
- **Port**: `443`
- **User**: Your Snowflake username
- **Password**: Your Snowflake password
- **Database**: `COVID_DB`
- **Schema**: `RAW`
- **Warehouse**: `COMPUTE_WH`

## Monitoring & Troubleshooting

### View DAG
```
Airflow UI → DAGs → covid_batch_pipeline
```

### View Logs
```powershell
# List available logs
airflow tasks list covid_batch_pipeline

# View specific task logs
airflow logs covid_batch_pipeline run_dbt_transformations 2026-03-31
```

### Trigger Manual Run
```powershell
# Via CLI
airflow dags trigger covid_batch_pipeline --exec-date 2026-03-31

# Via Web UI
Airflow UI → DAGs → covid_batch_pipeline → Trigger DAG
```

### Common Issues

**Issue**: Task fails with "File not found"
- **Solution**: Verify CSV file exists in `LOCAL_COVID_FILE_DIR`

**Issue**: Snowflake COPY fails
- **Solution**: Check S3 credentials and Snowflake STAGE permissions

**Issue**: dBT transformation fails
- **Solution**: Run dBT locally first: `dbt build --select stg_covid_data`

## Advanced Features

### Adding Data Quality Checks
Edit `validate_data_quality()` function to add custom checks:
```python
def validate_data_quality(ti, **context):
    validation_sql = """
        SELECT COUNT(*) FROM COVID_DATA
        WHERE observation_date IS NULL;
    """
    # Add assertions
```

### Adding Slack Notifications
Update `post_dbt_notifications()` function:
```python
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator
```

### Adding Data Profiling
Integrate Great Expectations:
```python
from airflow.providers.great_expectations.operators.great_expectations import GreatExpectationsOperator
```

## Deployment

### Docker Deployment
See [Docker Compose](docker-compose.yml) for containerized setup.

### Production Considerations
1. Use strong passwords for database credentials
2. Store secrets in Airflow's secret backend (AWS Secrets Manager, Vault)
3. Enable audit logging
4. Set up alerting for SLA misses
5. Configure backup and disaster recovery
6. Monitor Airflow scheduler and webserver health

## Support & Documentation

- [Airflow Documentation](https://airflow.apache.org/docs/)
- [Snowflake Airflow Provider](https://airflow.apache.org/docs/apache-airflow-providers-snowflake/)
- [AWS Airflow Provider](https://airflow.apache.org/docs/apache-airflow-providers-amazon/)
- [dBT Documentation](https://docs.getdbt.com/)

## License
Same as parent project
