import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

def load_db(**kwargs):
    """Load filtered CSV into PostgreSQL table `wiki_views`. Expects CSV path from XCom."""
    ti = kwargs['ti']
    csv_file_path = ti.xcom_pull(task_ids='transform_txt')
    db_url = os.getenv("CLOUD_POSTGRES_URL")
    db_connection_str = db_url
    
    engine = create_engine(db_connection_str)

    if not csv_file_path:
        raise ValueError("Did not receive CSV file path from transform_task")
    df = pd.read_csv(csv_file_path)
    
    table_name = 'wiki_views'

    try:
        df.to_sql(table_name, engine, if_exists='replace', index=False)
        print(f"Data from {csv_file_path} successfully loaded into {table_name} in PostgreSQL.")
    except Exception as e:
        print(f"Error loading data: {e}")
    
# load_db()
