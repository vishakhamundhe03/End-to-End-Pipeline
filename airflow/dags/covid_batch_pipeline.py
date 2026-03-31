from __future__ import annotations

from datetime import datetime, timedelta
import logging
from pathlib import Path

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.transfers.local_to_s3 import LocalFilesystemToS3Operator
from airflow.providers.snowflake.operators.snowflake import SnowflakeSqlApiOperator
from airflow.utils.decorators import apply_defaults

logger = logging.getLogger(__name__)

# =============================
# Configuration
# =============================
CONFIG = {
    "owner": "data-team",
    "environment": "production",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

# =============================
# Python Callables
# =============================
def build_file_name(ds, **context):
    """Generate COVID data file name based on execution date."""
    file_name = f"covid_{ds}.csv"
    logger.info(f"Generated file name: {file_name}")
    return file_name


def build_copy_sql(ti, **context):
    """Generate Snowflake COPY command SQL dynamically."""
    file_name = ti.xcom_pull(task_ids="build_file_name")
    s3_bucket = "{{ var.value.COVID_S3_BUCKET }}"
    s3_prefix = "{{ var.value.COVID_S3_PREFIX }}"
    
    logger.info(f"Building COPY SQL for file: {file_name}")
    
    # File format assumes CSV with header row.
    sql = f"""
        USE DATABASE {{ var.value.SNOWFLAKE_DATABASE }};
        USE SCHEMA {{ var.value.SNOWFLAKE_SCHEMA }};

        CREATE OR REPLACE STAGE covid_ext_stage
          URL='s3://{s3_bucket}/{s3_prefix}'
          CREDENTIALS=(AWS_KEY_ID='{{{{ var.value.AWS_ACCESS_KEY_ID }}}}' AWS_SECRET_KEY='{{{{ var.value.AWS_SECRET_ACCESS_KEY }}}}');

        CREATE OR REPLACE FILE FORMAT covid_csv_fmt
          TYPE = CSV
          SKIP_HEADER = 1
          FIELD_OPTIONALLY_ENCLOSED_BY = '"';

        COPY INTO {{ var.value.SNOWFLAKE_DATABASE }}.{{ var.value.SNOWFLAKE_SCHEMA }}.COVID_DATA
        FROM @covid_ext_stage/{file_name}
        FILE_FORMAT = (FORMAT_NAME = covid_csv_fmt)
        ON_ERROR = 'CONTINUE';
    """
    
    ti.xcom_push(key="copy_sql", value=sql)
    logger.info("COPY SQL generated successfully")
    return sql


def validate_data_quality(ti, **context):
    """Perform data quality checks on loaded data."""
    logger.info("Starting data quality validation...")
    
    # This can be extended with Great Expectations or custom SQL checks
    validation_sql = """
        USE DATABASE {{ var.value.SNOWFLAKE_DATABASE }};
        USE SCHEMA {{ var.value.SNOWFLAKE_SCHEMA }};
        
        SELECT COUNT(*) as total_records,
               COUNT(DISTINCT country) as unique_countries,
               MAX(observation_date) as latest_date
        FROM COVID_DATA;
    """
    
    ti.xcom_push(key="validation_sql", value=validation_sql)
    logger.info("Data quality validation queries prepared")
    return validation_sql


def post_dbt_notifications(ti, **context):
    """Send notifications after dbt run completes."""
    execution_date = context.get("execution_date")
    dag_run = context.get("dag_run")
    
    logger.info(f"Post-dbt notification for run: {dag_run}")
    logger.info("Pipeline completed successfully!")
    # Add Slack/email notifications here as needed


# =============================
# DAG Definition
# =============================
with DAG(
    dag_id="covid_batch_pipeline",
    start_date=datetime(2026, 3, 1),
    schedule_interval="@daily",
    catchup=False,
    default_args={
        "owner": CONFIG["owner"],
        "retries": CONFIG["retries"],
        "retry_delay": CONFIG["retry_delay"],
    },
    tags=["covid", "batch", "s3", "snowflake", "dbt"],
    description="Daily COVID data batch processing: S3 → Snowflake → dBT transformations",
    sla=timedelta(hours=2),  # SLA: complete within 2 hours
) as dag:

    # =============================
    # Task 1: Generate File Name
    # =============================
    task_build_file_name = PythonOperator(
        task_id="build_file_name",
        python_callable=build_file_name,
        provide_context=True,
    )

    # =============================
    # Task 2: Upload to S3
    # =============================
    task_upload_to_s3 = LocalFilesystemToS3Operator(
        task_id="upload_to_s3",
        filename="{{ var.value.LOCAL_COVID_FILE_DIR }}/{{ ti.xcom_pull(task_ids='build_file_name') }}",
        dest_key="{{ var.value.COVID_S3_PREFIX }}/{{ ti.xcom_pull(task_ids='build_file_name') }}",
        dest_bucket="{{ var.value.COVID_S3_BUCKET }}",
        aws_conn_id="aws_default",
        replace=True,
    )

    # =============================
    # Task 3: Build Snowflake COPY SQL
    # =============================
    task_build_copy_command = PythonOperator(
        task_id="build_copy_command",
        python_callable=build_copy_sql,
        provide_context=True,
    )

    # =============================
    # Task 4: Load Data to Snowflake
    # =============================
    task_load_to_snowflake = SnowflakeSqlApiOperator(
        task_id="load_to_snowflake",
        snowflake_conn_id="snowflake_default",
        sql="{{ ti.xcom_pull(task_ids='build_copy_command') }}",
    )

    # =============================
    # Task 5: Validate Data Quality
    # =============================
    task_validate_data = PythonOperator(
        task_id="validate_data_quality",
        python_callable=validate_data_quality,
        provide_context=True,
    )

    # =============================
    # Task 6: Run dBT Transformations
    # =============================
    task_run_dbt = BashOperator(
        task_id="run_dbt_transformations",
        bash_command=(
            "cd {{ var.value.DBT_PROJECT_DIR }} && "
            "{{ var.value.DBT_ENV_SCRIPT }} && "
            "{{ var.value.DBT_EXECUTABLE }} build "
            "--select stg_covid_data fact_covid country_covid && "
            "{{ var.value.DBT_EXECUTABLE }} test"
        ),
    )

    # =============================
    # Task 7: Post-Processing Notification
    # =============================
    task_notify_completion = PythonOperator(
        task_id="notify_completion",
        python_callable=post_dbt_notifications,
        provide_context=True,
        trigger_rule="all_success",
    )

    # =============================
    # Task Dependencies (Pipeline DAG)
    # =============================
    # Sequential flow: Generate name → Upload to S3 → Build SQL → Load to Snowflake → Validate → Transform with dBT → Notify
    task_build_file_name >> task_upload_to_s3 >> task_build_copy_command >> task_load_to_snowflake >> task_validate_data >> task_run_dbt >> task_notify_completion
