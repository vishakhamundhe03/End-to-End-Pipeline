# Airflow Directory Structure

## Complete Setup

```
covid_project/
├── airflow/                           # ← Airflow root directory
│   ├── dags/                          # DAG definitions
│   │   └── covid_batch_pipeline.py    # ✨ Main pipeline (7 tasks)
│   │
│   ├── config/                        # Configuration files
│   │   └── airflow_config_template.txt # Config reference
│   │
│   ├── logs/                          # Auto-generated logs
│   │   └── covid_batch_pipeline/      # DAG logs
│   │       ├── build_file_name/       # Task logs
│   │       ├── upload_to_s3/
│   │       ├── build_copy_command/
│   │       ├── load_to_snowflake/
│   │       ├── validate_data_quality/
│   │       ├── run_dbt_transformations/
│   │       └── notify_completion/
│   │
│   ├── .env.example                   # Environment template ⭐
│   ├── .env                           # Environment variables (CREATE THIS)
│   ├── airflow.db                     # SQLite database (auto-created)
│   ├── webserver_config.py            # Optional webserver config
│   ├── unittests.cfg                  # Test configuration (auto)
│   │
│   ├── requirements.txt               # ✨ Python dependencies
│   ├── utils.py                       # ✨ Utility functions
│   ├── setup_airflow_env.ps1          # ✨ Setup script
│   │
│   ├── Dockerfile                     # ✨ Docker image
│   ├── docker-compose.yml             # ✨ Docker Compose setup
│   │
│   ├── README.md                      # ✨ Complete guide
│   ├── QUICKSTART.md                  # ✨ 5-min setup
│   ├── ARCHITECTURE.md                # ✨ System design
│   └── IMPLEMENTATION_SUMMARY.md      # ✨ This implementation
│
├── [other dbt files...]
└── [other project files...]
```

## File Descriptions

### Core Airflow Files

#### `dags/covid_batch_pipeline.py` ⭐ **MAIN**
- **7 Tasks**: File → S3 → Snowflake → Validate → dBT → Transform → Notify
- **Scheduling**: Daily at midnight UTC
- **SLA**: 2 hours
- **Retries**: 2 with 5-minute delay
- **Features**: Logging, error handling, data validation

#### `requirements.txt` 📦
```
apache-airflow==2.10.5
apache-airflow-providers-amazon==9.0.0
apache-airflow-providers-snowflake==6.0.0
apache-airflow-providers-dbt-cloud==4.4.0
apache-airflow-providers-slack==8.5.1
boto3==1.37.0
snowflake-connector-python==3.16.0
great-expectations==0.18.20
python-dotenv==1.0.1
pydantic==2.5.0
```

### Configuration Files

#### `.env.example` & `.env` 🔐
Environment variables template & actual config
```
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=yyy
SNOWFLAKE_USER=user
SNOWFLAKE_PASSWORD=pass
SNOWFLAKE_ACCOUNT=account
COVID_S3_BUCKET=covid-data-bucket
...
```

#### `config/airflow_config_template.txt`
Reference configuration for airflow.cfg (core, database, webserver, scheduler settings)

### Utility & Setup Files

#### `utils.py` 🛠️
**Classes**:
- `DataValidator` - CSV validation, SQL validation queries
- `PipelineConfig` - Configuration helpers
- `NotificationHelper` - Slack/Email formatting

#### `setup_airflow_env.ps1` 🔧
PowerShell script to configure:
- Airflow variables
- AWS connection
- Snowflake connection
Handles all setup interactively

### Docker Deployment

#### `Dockerfile` 🐳
- Base: apache/airflow:2.10.5-python3.11
- Installs requirements
- Creates necessary directories
- Initializes database

#### `docker-compose.yml` 🐳
**Services**:
- PostgreSQL (metadata)
- Redis (task queue)
- Airflow Webserver (port 8080)
- Airflow Scheduler

### Documentation Files

#### `README.md` 📖 **COMPREHENSIVE**
- Full reference guide
- Installation steps
- Configuration details
- Troubleshooting
- Monitoring guide
- Production considerations

#### `QUICKSTART.md` ⚡ **QUICK**
- 5-minute setup
- Key commands
- Docker usage
- Troubleshooting quick ref

#### `ARCHITECTURE.md` 🏗️
- System design
- Data flow diagrams
- Technology stack
- Deployment options
- Monitoring metrics
- Maintenance tasks

#### `IMPLEMENTATION_SUMMARY.md` ✅ **THIS FILE**
- What was added
- Architecture overview
- Configuration checklist
- Quick start steps
- Integration points

---

## How to Set Up (Step by Step)

### Step 1: Navigate to Airflow Directory
```powershell
cd c:\Users\hp\OneDrive\Desktop\DataCamp\covid_project\airflow
```

### Step 2: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 3: Create .env File
```powershell
Copy-Item .env.example .env
# Edit .env with your credentials
```

### Step 4: Initialize Airflow
```powershell
airflow db upgrade
airflow users create --username admin --password admin --firstname Admin --lastname Admin --role Admin --email admin@example.com
```

### Step 5: Configure Connections (Choose One)

**Option A: Automatic (Recommended)**
```powershell
.\setup_airflow_env.ps1 `
  -AwsAccessKey "your_key" `
  -AwsSecretKey "your_secret" `
  -SnowflakeUser "your_user" `
  -SnowflakePassword "your_pass" `
  -SnowflakeAccount "xy12345.us-east-1"
```

**Option B: Manual via CLI**
```powershell
# AWS Connection
airflow connections add 'aws_default' \
  --conn-type 'aws' \
  --conn-login 'YOUR_KEY' \
  --conn-password 'YOUR_SECRET'

# Snowflake Connection
airflow connections add 'snowflake_default' \
  --conn-type 'snowflake' \
  --conn-login 'your_user' \
  --conn-password 'your_pass' \
  --conn-host 'your_account.snowflakecomputing.com'
```

### Step 6: Set Airflow Variables
```powershell
airflow variables set COVID_S3_BUCKET covid-data-bucket
airflow variables set COVID_S3_PREFIX covid-data
airflow variables set SNOWFLAKE_DATABASE COVID_DB
airflow variables set SNOWFLAKE_SCHEMA RAW
airflow variables set DBT_PROJECT_DIR ../
# ... etc (see setup_airflow_env.ps1 for full list)
```

### Step 7: Start Airflow

**Terminal 1:**
```powershell
airflow scheduler
```

**Terminal 2:**
```powershell
airflow webserver --port 8080
```

### Step 8: Access UI
Open http://localhost:8080 in browser
Login: admin/admin

---

## Pipeline Overview

```
Daily Trigger (Midnight UTC)
        ↓
┌───────────────────────────────────┐
│ Task 1: build_file_name           │  Generate covid_YYYY-MM-DD.csv
└───────┬─────────────────────────────┘
        ↓
┌───────────────────────────────────┐
│ Task 2: upload_to_s3              │  Upload CSV to S3://bucket/prefix/
└───────┬─────────────────────────────┘
        ↓
┌───────────────────────────────────┐
│ Task 3: build_copy_command        │  Generate Snowflake COPY SQL
└───────┬─────────────────────────────┘
        ↓
┌───────────────────────────────────┐
│ Task 4: load_to_snowflake         │  Execute COPY: S3 → COVID_DB.RAW
└───────┬─────────────────────────────┘
        ↓
┌───────────────────────────────────┐
│ Task 5: validate_data_quality     │  Check nulls, duplicates, ranges
└───────┬─────────────────────────────┘
        ↓
┌───────────────────────────────────┐
│ Task 6: run_dbt_transformations   │  dBT build: stg → fact → marts
└───────┬─────────────────────────────┘
        ↓
┌───────────────────────────────────┐
│ Task 7: notify_completion         │  Log completion, send alerts
└───────────────────────────────────┘
        ↓
    COMPLETE (Typically ~21 min)
```

---

## Key Commands

### View Pipeline
```powershell
airflow dags list                    # List all DAGs
airflow dags show covid_batch_pipeline  # Visualize DAG
airflow tasks list covid_batch_pipeline # List tasks
```

### Run Pipeline
```powershell
airflow dags trigger covid_batch_pipeline          # Trigger manually
airflow dags trigger covid_batch_pipeline --exec-date 2026-03-31  # Specific date
```

### Monitor
```powershell
airflow dags list-runs covid_batch_pipeline       # Past runs
airflow logs covid_batch_pipeline load_to_snowflake 2026-03-31  # Task logs
airflow variables list              # View variables
airflow connections list            # View connections
```

### Debug
```powershell
airflow dags test covid_batch_pipeline 2026-03-31  # Test DAG
airflow tasks test covid_batch_pipeline build_file_name 2026-03-31  # Test task
```

---

## Configuration Variables Reference

| Variable | Example | Purpose |
|----------|---------|---------|
| `COVID_S3_BUCKET` | covid-data-bucket | S3 bucket name |
| `COVID_S3_PREFIX` | covid-data | S3 folder path |
| `LOCAL_COVID_FILE_DIR` | C:\data\covid | Local data source |
| `SNOWFLAKE_DATABASE` | COVID_DB | Target database |
| `SNOWFLAKE_SCHEMA` | RAW | Target schema |
| `SNOWFLAKE_WAREHOUSE` | COMPUTE_WH | Compute warehouse |
| `AWS_ACCESS_KEY_ID` | xxxx | AWS credentials |
| `AWS_SECRET_ACCESS_KEY` | yyyy | AWS credentials |
| `DBT_PROJECT_DIR` | ../  | dBT project path |
| `DBT_EXECUTABLE` | ../.dbt-venv/Scripts/dbt.exe | dBT executable |

---

## Connections Reference

### aws_default (AWS)
```
Type: aws
Access Key: YOUR_ACCESS_KEY
Secret Key: YOUR_SECRET_KEY
```

### snowflake_default (Snowflake)
```
Type: snowflake
Host: account.snowflakecomputing.com
Port: 443
User: your_username
Password: your_password
```

---

## Troubleshooting Quick Ref

| Issue | Solution |
|-------|----------|
| DAG not showing | Check: dags/ folder, DAG syntax, airflow db upgrade |
| Connection error | Run: airflow connections list, verify credentials |
| S3 error | Check: AWS credentials, bucket name, permissions |
| Snowflake error | Check: Account, user, password, network access |
| dBT error | Run: dbt debug, check dbt_project.yml |
| Port 8080 used | Use: airflow webserver --port 8081 |

---

## Docker Quick Start

```powershell
# Create .env file from template
copy .env.example .env

# Start services
docker-compose up -d

# Check logs
docker-compose logs -f airflow-webserver

# Access UI
# http://localhost:8080 (admin/admin)

# Stop services
docker-compose down
```

---

## Files You Need to Create/Edit

| File | Action | Notes |
|------|--------|-------|
| `.env` | CREATE | Copy from `.env.example`, fill credentials |
| `C:\data\covid\covid_YYYY-MM-DD.csv` | CREATE | Daily data files |
| S3 bucket | CREATE | Via AWS console |
| Snowflake tables | CREATE | COVID_DB.RAW.COVID_DATA |

---

## Production Checklist

- [ ] Use PostgreSQL instead of SQLite
- [ ] Store secrets in AWS Secrets Manager or Vault
- [ ] Enable Airflow authentication
- [ ] Set up email notifications
- [ ] Configure monitoring/alerting
- [ ] Set up backups
- [ ] Test failover procedures
- [ ] Document runbooks
- [ ] Set up audit logging

---

## Support & Resources

- **Main Guide**: [README.md](README.md)
- **Quick Start**: [QUICKSTART.md](QUICKSTART.md)
- **Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **Airflow Docs**: https://airflow.apache.org/
- **Snowflake Docs**: https://docs.snowflake.com/

---

**Everything is ready to go! 🚀**

Next step: Run `.\setup_airflow_env.ps1` with your credentials!
