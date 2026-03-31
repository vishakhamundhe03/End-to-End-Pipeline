FROM apache/airflow:2.10.5-python3.11

# Switch to root to install system dependencies
USER root

RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Switch back to airflow user
USER airflow

# Copy requirements and install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Create necessary directories
RUN mkdir -p /home/airflow/dags \
    /home/airflow/logs \
    /home/airflow/config \
    /home/airflow/plugins

# Set environment
ENV AIRFLOW_HOME=/home/airflow
ENV PYTHONUNBUFFERED=1

# Initialize Airflow database
RUN airflow db upgrade

EXPOSE 8080

CMD ["webserver"]
