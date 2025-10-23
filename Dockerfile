# Dockerfile
FROM apache/airflow:3.1.0

# Set PYTHONPATH at build/runtime level
# ENV PYTHONPATH=/opt/airflow/dags:/opt/airflow/scripts
ENV PYTHONPATH=/opt/airflow:/opt/airflow/dags:/opt/airflow/scripts

USER airflow
COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt