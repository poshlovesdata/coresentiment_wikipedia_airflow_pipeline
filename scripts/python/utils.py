import time
from dotenv import load_dotenv
import os
from airflow.providers.smtp.operators.smtp import EmailOperator

load_dotenv()

def record_start_time(**context):
    """Push start time to XCom for later duration calculation."""
    start_time = time.time()
    context['ti'].xcom_push(key='start_time', value=start_time)


def record_end_time(**context):
    """Calculate run duration from XCom start time and push to XCom."""
    start_time = context['ti'].xcom_pull(key='start_time', task_ids='record_start_time')
    end_time = time.time()
    duration = end_time - start_time
    context['ti'].xcom_push(key='duration', value=duration)


def task_failure_alert(context):
    """Send an HTML email with task failure details and a link to logs."""
    dag_id = context.get('dag').dag_id
    task_id = context.get('task_instance').task_id
    execution_date = context.get('execution_date')
    log_url = context.get('task_instance').log_url
    exception = context.get('exception')

    subject = f"Airflow Alert: {dag_id} - Task {task_id} Failed"
    html_content = f"""
    <h3>Airflow Task Failed</h3>
    <p><b>DAG:</b> {dag_id}</p>
    <p><b>Task:</b> {task_id}</p>
    <p><b>Execution Date:</b> {execution_date}</p>
    <p><b>Error:</b> {exception}</p>
    <p><b>Logs:</b> <a href="{log_url}">View Logs</a></p>
    """

    email = EmailOperator(
        task_id='failure_notification',
        from_email=f'{os.getenv("FROM_EMAIL")}',
        to=['poshlovesdata@gmail.com'],
        subject=subject,
        html_content=html_content,
        conn_id="smtp_conn"
    )
    email.execute(context=context)