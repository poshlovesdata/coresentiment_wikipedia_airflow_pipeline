from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator 
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.smtp.operators.smtp import EmailOperator
from scripts.python.process_txt import transform_txt_file
from scripts.python.load_database import load_db
from scripts.python.utils import record_end_time, record_start_time, task_failure_alert
import datetime

with DAG(
    dag_id="wiki_etl_pipeline",
    start_date=datetime.datetime(2025,10,22),
    schedule="@daily",
    catchup=False
) as dag:
    
    record_start = PythonOperator(
        task_id="record_start_time",
        python_callable=record_start_time
    )
    
    download_file_task = BashOperator(
        task_id="download_wiki",
        bash_command="{{ '/opt/airflow/scripts/bash/download_file.sh' }}",
        do_xcom_push=True
    )

    transform_txt_file_task = PythonOperator(
        task_id='transform_txt',
        python_callable=transform_txt_file
    )

    load_db_task = PythonOperator(
        task_id='load_db',
        python_callable=load_db
    )
    
    record_end = PythonOperator(
        task_id='record_end_time',
        python_callable=record_end_time,
    )
    
    send_notification = EmailOperator(
        task_id="send_notification",
        to=['poshbeatss@gmail.com'],
        subject='Wiki Pipeline Notification {{ ds }}',
        html_content="""
        <h3>Pipeline Ran Successfully</h3>
        <p>Date: {{ ds }}</p>
        """
    )

    download_file_task >>  transform_txt_file_task >> load_db_task