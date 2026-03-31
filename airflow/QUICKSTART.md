# Airflow Batch Pipeline - Quick Start Guide

## 5-Minute Setup

### 1. Install Dependencies
```powershell
cd covid_project\airflow
pip install -r requirements.txt
```

### 2. Set Environment Variables
```powershell
# Copy the template and fill in your values
Copy-Item .env.example .env

# Edit .env with your credentials
notepad .env
```

### 3. Initialize Airflow
```powershell
# Create database
airflow db upgrade

# Create admin user
airflow users create --username admin --password admin --firstname Admin --lastname Admin --role Admin --email admin@example.com
```

### 4. Configure Connections
```powershell
# Run setup script
.\setup_airflow_env.ps1 `
  -AwsAccessKey "your_key" `
  -AwsSecretKey "your_secret" `
  -SnowflakeUser "your_user" `
  -SnowflakePassword "your_pass" `
  -SnowflakeAccount "xy12345.us-east-1"
```

### 5. Start Airflow

**Terminal 1:**
```powershell
airflow scheduler
```

**Terminal 2:**
```powershell
airflow webserver --port 8080
```

### 6. Access Web UI
- Open: http://localhost:8080
- Login: admin / admin
- Go to: DAGs → covid_batch_pipeline

---

## Pipeline Overview

```
┌─────────────────┐
│  Local CSV File │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Upload to S3   │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│  Snowflake COPY Command │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────┐
│  Load to Snowflake  │
└────────┬────────────┘
         │
         ▼
┌──────────────────────┐
│  Data Quality Checks │
└────────┬─────────────┘
         │
         ▼
┌──────────────────────┐
│  dBT Transformations │
└────────┬─────────────┘
         │
         ▼
┌────────────────────┐
│  Notify Completion │
└────────────────────┘
```

---

## Configuration Quick Reference

### Airflow Variables
| Variable | Where to Set |
|----------|-------------|
| `COVID_S3_BUCKET` | .env or `airflow variables set` |
| `SNOWFLAKE_DATABASE` | .env or `airflow variables set` |
| `DBT_PROJECT_DIR` | .env or `airflow variables set` |

### Connections
| Connection | Type | Command |
|----------|------|---------|
| `aws_default` | AWS | `airflow connections add 'aws_default' --conn-type 'aws' ...` |
| `snowflake_default` | Snowflake | `airflow connections add 'snowflake_default' --conn-type 'snowflake' ...` |

---

## Common Commands

### View DAG
```powershell
airflow dags list
airflow dags show covid_batch_pipeline
```

### Trigger Pipeline
```powershell
# Manual trigger
airflow dags trigger covid_batch_pipeline

# With specific date
airflow dags trigger covid_batch_pipeline --exec-date 2026-03-31
```

### View Logs
```powershell
# Recent logs
airflow logs covid_batch_pipeline run_dbt_transformations -n 20

# Specific task
airflow logs covid_batch_pipeline load_to_snowflake 2026-03-31
```

### Validate DAG
```powershell
airflow dags test covid_batch_pipeline 2026-03-31
```

---

## Troubleshooting

### Port 8080 Already in Use
```powershell
airflow webserver --port 8081
```

### Reset Airflow
```powershell
airflow db reset  # Warning: deletes all data
airflow db upgrade
```

### View All Variables
```powershell
airflow variables list
```

### View All Connections
```powershell
airflow connections list
```

---

## Docker Deployment

### Using Docker Compose
```powershell
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## Next Steps

1. ✅ Verify CSV data is in `C:\data\covid`
2. ✅ Test S3 connection: `aws s3 ls covid-data-bucket`
3. ✅ Test Snowflake connection in dBT: `dbt debug`
4. ✅ Trigger first DAG run: `airflow dags trigger covid_batch_pipeline`
5. ✅ Monitor in Web UI: http://localhost:8080

---

## Support

See [README.md](README.md) for detailed documentation

For issues, check:
1. Airflow logs: `./logs/`
2. Airflow UI: Task logs for specific errors
3. Snowflake account: Query history for COPY command status
