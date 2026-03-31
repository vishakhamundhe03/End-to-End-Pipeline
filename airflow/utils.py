"""
Airflow utilities for COVID data pipeline
Includes data validation, quality checks, and helpers
"""

import logging
from typing import Dict, List, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class DataValidator:
    """Validate COVID data quality"""
    
    @staticmethod
    def validate_csv_format(filepath: str) -> Tuple[bool, str]:
        """
        Validate CSV file format and structure
        
        Args:
            filepath: Path to CSV file
            
        Returns:
            Tuple of (is_valid, message)
        """
        try:
            import pandas as pd
            
            df = pd.read_csv(filepath)
            
            # Check required columns
            required_columns = {
                'country', 'province', 'observation_date', 
                'confirmed_cases', 'death_cases', 'recovered_cases'
            }
            
            missing_columns = required_columns - set(df.columns)
            if missing_columns:
                return False, f"Missing columns: {missing_columns}"
            
            # Check for empty dataframe
            if df.empty:
                return False, "CSV file is empty"
            
            # Check for null values in key columns
            null_in_key = df[['country', 'observation_date']].isnull().any()
            if null_in_key.any():
                return False, "Null values found in key columns"
            
            logger.info(f"✓ CSV validation passed: {len(df)} rows")
            return True, f"Valid CSV with {len(df)} records"
            
        except Exception as e:
            return False, f"CSV validation error: {str(e)}"
    
    @staticmethod
    def generate_validation_queries() -> Dict[str, str]:
        """Generate SQL validation queries for Snowflake"""
        return {
            "row_count": """
                SELECT COUNT(*) as total_rows 
                FROM {{ var.value.SNOWFLAKE_DATABASE }}.{{ var.value.SNOWFLAKE_SCHEMA }}.COVID_DATA
            """,
            
            "null_check": """
                SELECT 
                    SUM(CASE WHEN country IS NULL THEN 1 ELSE 0 END) as null_country,
                    SUM(CASE WHEN observation_date IS NULL THEN 1 ELSE 0 END) as null_date,
                    SUM(CASE WHEN source_row_id IS NULL THEN 1 ELSE 0 END) as null_row_id
                FROM {{ var.value.SNOWFLAKE_DATABASE }}.{{ var.value.SNOWFLAKE_SCHEMA }}.COVID_DATA
            """,
            
            "date_range": """
                SELECT 
                    MIN(observation_date) as earliest_date,
                    MAX(observation_date) as latest_date
                FROM {{ var.value.SNOWFLAKE_DATABASE }}.{{ var.value.SNOWFLAKE_SCHEMA }}.COVID_DATA
            """,
            
            "duplicates": """
                SELECT 
                    source_row_id, 
                    COUNT(*) as duplicate_count
                FROM {{ var.value.SNOWFLAKE_DATABASE }}.{{ var.value.SNOWFLAKE_SCHEMA }}.COVID_DATA
                GROUP BY source_row_id
                HAVING COUNT(*) > 1
            """,
            
            "statistics": """
                SELECT 
                    COUNT(DISTINCT country) as unique_countries,
                    COUNT(DISTINCT province) as unique_provinces,
                    MIN(confirmed_cases) as min_cases,
                    MAX(confirmed_cases) as max_cases,
                    AVG(confirmed_cases) as avg_cases
                FROM {{ var.value.SNOWFLAKE_DATABASE }}.{{ var.value.SNOWFLAKE_SCHEMA }}.COVID_DATA
            """
        }


class PipelineConfig:
    """Pipeline configuration helper"""
    
    # Default values
    DEFAULTS = {
        'retries': 2,
        'retry_delay_minutes': 5,
        'sla_hours': 2,
        'schedule': '@daily',
        'owner': 'data-team',
    }
    
    @staticmethod
    def get_environment_config() -> Dict:
        """Load configuration from environment variables"""
        import os
        
        return {
            'aws_access_key': os.getenv('AWS_ACCESS_KEY_ID'),
            'aws_secret_key': os.getenv('AWS_SECRET_ACCESS_KEY'),
            's3_bucket': os.getenv('COVID_S3_BUCKET', 'covid-data-bucket'),
            's3_prefix': os.getenv('COVID_S3_PREFIX', 'covid-data'),
            'snowflake_user': os.getenv('SNOWFLAKE_USER'),
            'snowflake_account': os.getenv('SNOWFLAKE_ACCOUNT'),
            'snowflake_database': os.getenv('SNOWFLAKE_DATABASE', 'COVID_DB'),
            'snowflake_schema': os.getenv('SNOWFLAKE_SCHEMA', 'RAW'),
        }


class NotificationHelper:
    """Helper for sending notifications"""
    
    @staticmethod
    def format_slack_message(dag_id: str, status: str, details: Dict) -> Dict:
        """Format Slack notification message"""
        return {
            'text': f"DAG: {dag_id} - Status: {status}",
            'blocks': [
                {
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': f"*DAG*: {dag_id}\n*Status*: {status}\n*Time*: {datetime.now()}"
                    }
                },
                {
                    'type': 'section',
                    'fields': [
                        {'type': 'mrkdwn', 'text': f"*Duration*:\n{details.get('duration', 'N/A')}"},
                        {'type': 'mrkdwn', 'text': f"*Records Loaded*:\n{details.get('records_loaded', 'N/A')}"},
                    ]
                }
            ]
        }
    
    @staticmethod
    def format_email_body(dag_id: str, status: str, details: Dict) -> str:
        """Format email notification body"""
        return f"""
        <h2>Pipeline Execution Report</h2>
        
        <p>
            <strong>DAG ID:</strong> {dag_id}<br>
            <strong>Status:</strong> {status}<br>
            <strong>Execution Time:</strong> {datetime.now()}<br>
            <strong>Duration:</strong> {details.get('duration', 'N/A')}<br>
            <strong>Records Loaded:</strong> {details.get('records_loaded', 'N/A')}<br>
        </p>
        
        <h3>Summary</h3>
        <pre>{details.get('summary', 'N/A')}</pre>
        """


# Export utilities
__all__ = ['DataValidator', 'PipelineConfig', 'NotificationHelper']
