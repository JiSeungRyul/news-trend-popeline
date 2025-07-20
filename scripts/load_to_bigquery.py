import os
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
from datetime import datetime, timedelta
from dotenv import load_dotenv
from google.cloud.exceptions import NotFound

load_dotenv()

gcp_key_path = os.getenv("GCP_KEY_PATH")
if not gcp_key_path:
    raise ValueError("GCP_KEY_PATH is not set in .env")

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = gcp_key_path

# today = datetime.now().strftime("%Y%m%d")
today = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")

csv_file = f"data/naver_top30_news_{today}.csv"
    
project_id  = os.getenv("PROJECT_ID")
if not project_id:
    raise ValueError("PROJECT_ID is not set in .env")

dataset_id = os.getenv("DATASET_ID")
if not dataset_id:
    raise ValueError("DATASET_ID is not set in .env")

table_id  = os.getenv("TABLE_ID")
if not table_id:
    raise ValueError("TABLE_ID is not set in .env")

def load_to_bigquery():
    df = pd.read_csv(csv_file)
    
    client = bigquery.Client(project=project_id)
    dataset_ref = client.dataset(dataset_id)

    try:
        client.get_dataset(dataset_ref)
    except NotFound:
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "asia-northeast3"
        client.create_dataset(dataset)
        print(f"📦 Created dataset {dataset_id}")

    table_ref = f"{project_id}.{dataset_id}.{table_id}"

    job_config = bigquery.LoadJobConfig(
        autodetect=True,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        allow_quoted_newlines=True,
        quote_character='"',
        encoding="UTF-8",
        field_delimiter=","
    )

    with open(csv_file, "rb") as f:
        job = client.load_table_from_file(f, table_ref, job_config=job_config)
    job.result()

    print(f"✅ Loaded {df.shape[0]} rows into {table_ref}")

if __name__ == "__main__":
    load_to_bigquery()
