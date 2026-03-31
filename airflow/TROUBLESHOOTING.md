# Airflow Troubleshooting Guide

## Common Issues & Solutions

### 1. Airflow Webserver Won't Start

**Error**: `Port 8080 is already in use`
```powershell
# Solution: Use a different port
airflow webserver --port 8081
```

**Error**: `Database locked` or `sqlite3.OperationalError`
```powershell
# Solution: Reset the database
airflow db reset
airflow db upgrade
```

**Error**: `No module named 'airflow'`
```powershell
# Solution: Install Airflow
pip install -r requirements.txt
```

---

### 2. DAG Not Showing in Web UI

**Problem**: DAG doesn't appear in Airflow UI

**Checklist**:
```powershell
# 1. Verify DAG file exists
Test-Path "dags/covid_batch_pipeline.py"

# 2. Check DAG syntax
airflow dags validate

# 3. List all DAGs
airflow dags list

# 4. Test DAG parsing
python -m py_compile dags/covid_batch_pipeline.py

# 5. Restart webserver and scheduler
```

**Solutions**:
- Ensure file is in `dags/` folder (not subdirectories)
- Check for Python syntax errors
- Verify DAG ID matches file content
- Wait 300 seconds (default dag_dir_list_interval)

---

### 3. Connection Errors

**Error**: `Connection 'aws_default' does not exist`

```powershell
# Check if connection exists
airflow connections list | findstr aws_default

# If not found, create it
airflow connections add 'aws_default' `
  --conn-type 'aws' `
  --conn-login 'YOUR_ACCESS_KEY' `
  --conn-password 'YOUR_SECRET_KEY'

# Verify
airflow connections list | findstr aws_default
```

**Error**: `Connection 'snowflake_default' does not exist`

```powershell
# Create Snowflake connection
airflow connections add 'snowflake_default' `
  --conn-type 'snowflake' `
  --conn-login 'your_username' `
  --conn-password 'your_password' `
  --conn-host 'xy12345.snowflakecomputing.com' `
  --conn-port '443'
```

---

### 4. Variable Errors

**Error**: `Variable 'COVID_S3_BUCKET' does not exist`

```powershell
# Check if variable exists
airflow variables list | findstr COVID_S3_BUCKET

# If not found, create it
airflow variables set COVID_S3_BUCKET covid-data-bucket

# Verify
airflow variables get COVID_S3_BUCKET
```

**Error**: Variables not persisting across restarts

```powershell
# Solution: Check database connection
airflow db check

# If using SQLite, verify file exists
Test-Path "airflow.db"

# If using PostgreSQL, test connection
psql -U airflow -d airflow -h localhost
```

---

### 5. Task Execution Issues

**Error**: `Task failed: [ModuleNotFoundError: No module named 'xxx']`

```powershell
# Install missing package
pip install missing_package

# Or add to requirements.txt and reinstall
pip install -r requirements.txt
```

**Error**: `BashOperator task fails when running dBT`

```powershell
# 1. Verify dBT is installed
dbt --version

# 2. Check dBT project path
Test-Path "../dbt_project.yml"

# 3. Run dBT command manually
cd ..
dbt build --select stg_covid_data

# 4. Test dBT connection
dbt debug

# 5. Verify environment variables
dbt parse --show-config
```

---

### 6. S3 Upload Issues

**Error**: `Access Denied when uploading to S3`

```powershell
# 1. Verify AWS credentials
$env:AWS_ACCESS_KEY_ID
$env:AWS_SECRET_ACCESS_KEY

# 2. Test S3 connectivity
aws s3 ls covid-data-bucket

# 3. Verify bucket exists
aws s3api list-buckets

# 4. Check IAM permissions
# User needs: s3:GetObject, s3:PutObject, s3:ListBucket
```

**Error**: `File not found when uploading to S3`

```powershell
# 1. Verify local file exists
Test-Path "C:\data\covid\covid_2026-03-31.csv"

# 2. Check file permissions
Get-Item "C:\data\covid\covid_2026-03-31.csv" | Get-Acl

# 3. Verify Airflow variable
airflow variables get LOCAL_COVID_FILE_DIR

# 4. Create directory if missing
mkdir -Force "C:\data\covid"
```

---

### 7. Snowflake Issues

**Error**: `Invalid credentials` when connecting to Snowflake

```powershell
# 1. Test connection manually
snowflake-sql --username user --account account

# 2. Verify credentials in connection
airflow connections get snowflake_default

# 3. Check account format
# Should be: xy12345.us-east-1
# Not: xy12345.snowflakecomputing.com
```

**Error**: `Database 'COVID_DB' does not exist`

```powershell
# 1. Create database in Snowflake
# In Snowflake WebUI or CLI:
CREATE DATABASE COVID_DB;
CREATE SCHEMA COVID_DB.RAW;
CREATE TABLE COVID_DB.RAW.COVID_DATA (...);

# 2. Verify database name in variables
airflow variables get SNOWFLAKE_DATABASE
```

**Error**: `COPY command fails`

```powershell
# 1. Check S3 file exists
aws s3 ls s3://covid-data-bucket/covid-data/

# 2. Verify Snowflake stage permissions
# In Snowflake:
SHOW STAGES;
DESC STAGE covid_ext_stage;

# 3. Check file format configuration
# In Snowflake:
SHOW FILE FORMATS;

# 4. Verify AWS key/secret in SQL
# The keys must be passed correctly in the SQL
```

---

### 8. dBT Issues

**Error**: `dBT: Profile not found`

```powershell
# 1. Check dBT profiles directory
Test-Path "$env:USERPROFILE\.dbt\profiles.yml"

# 2. Set profiles directory
$env:DBT_PROFILES_DIR = "$env:USERPROFILE\.dbt"

# 3. Create profiles.yml if missing
# See set_snowflake_env.ps1 for template
```

**Error**: `dBT: Schema 'RAW' does not exist`

```powershell
# 1. Create schema in Snowflake
# In Snowflake:
CREATE SCHEMA COVID_DB.RAW;

# 2. Verify schema name in profiles.yml
cat "$env:USERPROFILE\.dbt\profiles.yml"

# 3. Verify dBT models configuration
cat "dbt_project.yml"
```

---

### 9. Logging Issues

**Error**: `Can't read logs` or logs are empty

```powershell
# 1. Check logs directory
Test-Path "logs/"
Get-ChildItem "logs/" -Recurse

# 2. Verify Airflow logging config
# Check: $AIRFLOW_HOME/airflow.cfg [logging] section

# 3. Check file permissions
Get-Item "logs/" | Get-Acl

# 4. Clear old logs and test
Remove-Item "logs/" -Recurse -Force
airflow dags trigger covid_batch_pipeline
```

---

### 10. Docker Issues

**Error**: `Docker command not found`

```powershell
# 1. Install Docker Desktop for Windows
# Download from: https://www.docker.com/products/docker-desktop

# 2. Verify installation
docker --version
docker-compose --version
```

**Error**: `Port 5432 already in use (PostgreSQL)`

```powershell
# 1. List running containers
docker-compose ps

# 2. Stop running services
docker-compose down

# 3. Kill processes on port 5432
Get-Process | Where-Object {$_.Port -eq 5432} | Stop-Process -Force

# 4. Use different port in docker-compose.yml
# Change: "5432:5432" to "5433:5432"
```

**Error**: `Connection refused` when accessing Airflow UI

```powershell
# 1. Check if containers are running
docker-compose ps

# 2. Check container logs
docker-compose logs airflow-webserver

# 3. Wait for startup (may take 1-2 minutes)
# Then try: http://localhost:8080

# 4. Force restart
docker-compose restart
```

---

## Debug Commands

### View Task Logs
```powershell
# Latest logs for a task
airflow logs covid_batch_pipeline upload_to_s3 -n 50

# Specific execution date
airflow logs covid_batch_pipeline load_to_snowflake 2026-03-31

# All logs for a DAG
airflow logs covid_batch_pipeline -n 100
```

### Test DAG
```powershell
# Test DAG parsing
airflow dags validate

# Test DAG execution (dry run)
airflow dags test covid_batch_pipeline 2026-03-31

# Test specific task
airflow tasks test covid_batch_pipeline build_file_name 2026-03-31
```

### View Configuration
```powershell
# Show all variables
airflow variables list

# Show specific variable
airflow variables get COVID_S3_BUCKET

# Show all connections
airflow connections list

# Show specific connection
airflow connections get aws_default

# Show all configurations
airflow config list
```

### Database Health
```powershell
# Check database
airflow db check

# Check migrations
airflow db upgrade --only-alembic

# Show database details
airflow db show-config
```

---

## Performance Issues

### DAG Taking Too Long

```powershell
# 1. View task durations
airflow dags show covid_batch_pipeline --no-save

# 2. Identify slow task
# Look at: logs/covid_batch_pipeline/*/

# 3. Optimize specific task:
# - Reduce data volume
# - Increase resources
# - Optimize queries

# 4. Monitor Snowflake performance
# Check: QUERY_HISTORY in Snowflake
```

### High Memory Usage

```powershell
# 1. Check Airflow logs for memory errors
Get-Content "logs/scheduler/latest.log" -Tail 50 | findstr -i memory

# 2. Reduce DAG complexity
# - Split into smaller DAGs
# - Reduce parallelism

# 3. Increase system resources
# - Add RAM
# - Increase swap space
```

---

## Reset & Clean Up

### Complete Reset (Development Only)
```powershell
# WARNING: This deletes all Airflow data!

# 1. Stop services
airflow scheduler --stop
# [Ctrl+C] in webserver terminal

# 2. Remove database
Remove-Item "airflow.db"

# 3. Remove logs
Remove-Item "logs" -Recurse

# 4. Reinitialize
airflow db upgrade
airflow users create --username admin --password admin --firstname Admin --lastname Admin --role Admin --email admin@example.com
```

### Clear Specific DAG
```powershell
# Delete DAG from Airflow (keeps data)
airflow dags delete covid_batch_pipeline

# Remove DAG file
Remove-Item "dags/covid_batch_pipeline.py"
```

---

## Getting Help

### Check Logs First
```powershell
# 1. Check task logs
airflow logs covid_batch_pipeline {task_name} {execution_date}

# 2. Check scheduler logs
cat "logs/scheduler/latest.log"

# 3. Check webserver logs
cat "logs/webserver/latest.log"
```

### Check Configuration
```powershell
# Verify all required variables
airflow variables list | findstr COVID

# Verify all connections
airflow connections list

# Check Airflow config
airflow config list
```

### Test Components Individually
```powershell
# Test AWS connectivity
aws s3 ls covid-data-bucket

# Test Snowflake connectivity
dbt debug

# Test dBT models
cd ..
dbt parse
dbt run --select stg_covid_data
```

---

## Contact Support

If you still need help:
1. Check the [README.md](README.md) for comprehensive documentation
2. Review [ARCHITECTURE.md](ARCHITECTURE.md) for system design
3. Check Airflow logs in `logs/` directory
4. Search Airflow documentation: https://airflow.apache.org/docs/

---

## Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `ModuleNotFoundError` | Missing package | `pip install package_name` |
| `Connection not found` | Missing Airflow connection | Create via `airflow connections add` |
| `Variable not found` | Missing Airflow variable | Set via `airflow variables set` |
| `Access Denied` | AWS/Snowflake permissions | Check IAM/Snowflake roles |
| `File not found` | Missing data file | Verify local file path |
| `Database error` | Snowflake connectivity | Test connection, check network |
| `dBT error` | dBT execution issue | Run `dbt debug`, check SQL |
| `Port in use` | Service already running | Kill process or use different port |

---

**Still stuck? Check the detailed guides in the airflow/ directory!**
