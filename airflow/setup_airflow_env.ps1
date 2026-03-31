# ========================================
# Airflow Environment Setup Script
# Setup Airflow Variables and Connections
# ========================================

param(
    [string]$AirflowHome = $env:AIRFLOW_HOME,
    [string]$AwsAccessKey = "",
    [string]$AwsSecretKey = "",
    [string]$SnowflakeUser = "",
    [string]$SnowflakePassword = "",
    [string]$SnowflakeAccount = "",
    [string]$SnowflakeWarehouse = "COMPUTE_WH",
    [string]$SnowflakeDatabase = "COVID_DB",
    [string]$SnowflakeSchema = "RAW",
    [string]$S3Bucket = "covid-data-bucket",
    [string]$S3Prefix = "covid-data",
    [string]$LocalFilePath = "C:\data\covid",
    [string]$DbtProjectDir = "$PSScriptRoot\..\",
    [string]$DbtExecutable = "..\..\.dbt-venv\Scripts\dbt.exe"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Airflow Environment Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Check if Airflow is installed
if (-not (Get-Command airflow -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Airflow is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Airflow found: $(airflow version)" -ForegroundColor Green

# ========================================
# Set Airflow Variables
# ========================================
Write-Host "`n[1/3] Setting up Airflow Variables..." -ForegroundColor Yellow

$variables = @{
    "COVID_S3_BUCKET" = $S3Bucket
    "COVID_S3_PREFIX" = $S3Prefix
    "LOCAL_COVID_FILE_DIR" = $LocalFilePath
    "SNOWFLAKE_DATABASE" = $SnowflakeDatabase
    "SNOWFLAKE_SCHEMA" = $SnowflakeSchema
    "SNOWFLAKE_WAREHOUSE" = $SnowflakeWarehouse
    "AWS_ACCESS_KEY_ID" = $AwsAccessKey
    "AWS_SECRET_ACCESS_KEY" = $AwsSecretKey
    "DBT_PROJECT_DIR" = $DbtProjectDir
    "DBT_ENV_SCRIPT" = ". $DbtProjectDir\..\set_snowflake_env.ps1"
    "DBT_EXECUTABLE" = $DbtExecutable
}

foreach ($var in $variables.GetEnumerator()) {
    Write-Host "Setting variable: $($var.Name)" -ForegroundColor Gray
    airflow variables set $var.Name $var.Value
}

Write-Host "✓ Airflow variables configured" -ForegroundColor Green

# ========================================
# Create AWS Connection
# ========================================
Write-Host "`n[2/3] Setting up Connections..." -ForegroundColor Yellow

Write-Host "Setting up AWS connection..." -ForegroundColor Gray
airflow connections add 'aws_default' `
    --conn-type 'aws' `
    --conn-login "$AwsAccessKey" `
    --conn-password "$AwsSecretKey"

Write-Host "✓ AWS connection created" -ForegroundColor Green

# ========================================
# Create Snowflake Connection
# ========================================
Write-Host "Setting up Snowflake connection..." -ForegroundColor Gray

$snowflake_conn = "snowflake://${SnowflakeUser}:${SnowflakePassword}@${SnowflakeAccount}/${SnowflakeDatabase}/${SnowflakeSchema}?warehouse=${SnowflakeWarehouse}"

airflow connections add 'snowflake_default' `
    --conn-type 'snowflake' `
    --conn-login "$SnowflakeUser" `
    --conn-password "$SnowflakePassword" `
    --conn-host "$SnowflakeAccount" `
    --conn-port '443'

Write-Host "✓ Snowflake connection created" -ForegroundColor Green

# ========================================
# Validate Setup
# ========================================
Write-Host "`n[3/3] Validating Setup..." -ForegroundColor Yellow

Write-Host "`nConfigured Variables:" -ForegroundColor Gray
airflow variables list

Write-Host "`nConfigured Connections:" -ForegroundColor Gray
airflow connections list

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

Write-Host @"

Next Steps:
1. Ensure your local COVID data file exists at: $LocalFilePath
2. Create S3 bucket and configure AWS credentials
3. Update Snowflake connection details
4. Initialize Airflow DB: airflow db upgrade
5. Create Airflow user: airflow users create --username admin --password admin --firstname Admin --lastname Admin --role Admin --email admin@example.com
6. Start Airflow scheduler: airflow scheduler
7. Start Airflow webserver: airflow webserver --port 8080

Access Airflow UI at: http://localhost:8080
"@ -ForegroundColor Cyan
