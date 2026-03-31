End-to-End Data Engineering Pipeline: COVID-19 Analytics

Overview
This project implements a production-style end-to-end data pipeline to process and analyze COVID-19 data.
It demonstrates how raw data is ingested, cleaned, transformed, validated, and visualized using modern data engineering tools.

Problem Statement
COVID-19 data is large, inconsistent, and difficult to analyze manually.
The goal of this project is to build an automated pipeline that:
Cleans and standardizes raw data
Generates reliable metrics
Enables time-based and country-level analysis
Supports decision-making through dashboards

Architecture
AWS S3 (Data Lake)
        ↓
Snowflake (Data Warehouse)
        ↓
dbt (Staging → Fact → Mart Models)
        ↓
Apache Airflow (Batch Orchestration)
        ↓
Power BI (Dashboard)



Tech Stack
Cloud Storage: AWS S3
Data Warehouse: Snowflake
Transformations: dbt
Orchestration: Apache Airflow
Visualization: Power BI
Languages: Python, SQL

Pipeline Workflow
1. Data Ingestion
COVID dataset downloaded from Kaggle
Uploaded to AWS S3 (data lake)
2. Data Loading
Snowflake connected to S3 using external stage
Data loaded using COPY INTO
3. Data Transformation (dbt)
Staging layer: cleaned and standardized data
Fact layer: granular aggregations
Mart layer: business-level metrics
4. Orchestration (Batch Processing)
Airflow DAG automates the pipeline
Pipeline runs daily
Includes retries, logging, and validation
5. Visualization
Power BI dashboard built using transformed tables

Data Model (dbt)
source(raw.covid_data)
        ↓
stg_covid_data
        ↓
fact_covid
        ↓
country_covid



Staging Layer (stg_covid_data)
Parsed dates and timestamps
Cleaned country and province values
Ensured non-negative metrics
Derived metric:
active_cases = max(confirmed - deaths - recovered, 0)



Fact Layer (fact_covid)
Grain:
observation_date + country + province
Metrics:
confirmed_cases
death_cases
recovered_cases
active_cases
Advanced features:
Daily changes using window functions

Mart Layer (country_covid)
Country-level metrics:
Latest cases
Peak cases
Average cases

Data Quality
Implemented using dbt tests:
Not null checks
Unique constraints
Schema validations
Result:
All tests passed
Zero failures

Airflow Orchestration
The pipeline is automated using Apache Airflow.
DAG tasks:
Build file name
Upload to S3
Generate Snowflake COPY SQL
Load data into Snowflake
Data quality validation
Run dbt transformations
Completion notification

Dashboard (Power BI)
Visualizations:
COVID cases over time (line chart)
Top countries by cases (bar chart)
KPI cards (confirmed, deaths, recovered)
Date filter

How to Run
1. Upload Data to S3
Create bucket
Upload dataset
2. Load into Snowflake
Create stage
Run COPY command
3. Run dbt
dbt build


4. Run Airflow
airflow webserver
airflow scheduler


5. Open Power BI
Connect to Snowflake
Load tables:
fact_covid
country_covid




