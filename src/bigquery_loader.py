"""
BigQuery Data Pipeline for MetaMask On-Ramp Quotes
Uploads processed tabular quotes data to Google BigQuery.
Includes schema validation, dataset creation, and authentication fallbacks.
"""

import os
import logging
from typing import Optional
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

TABLE_SCHEMA = [
    {"name": "scraped_timestamp", "type": "TIMESTAMP", "mode": "REQUIRED"},
    {"name": "country_code", "type": "STRING", "mode": "REQUIRED"},
    {"name": "country_name", "type": "STRING", "mode": "NULLABLE"},
    {"name": "fiat_currency", "type": "STRING", "mode": "REQUIRED"},
    {"name": "price_point", "type": "FLOAT64", "mode": "REQUIRED"},
    {"name": "price_bin", "type": "STRING", "mode": "NULLABLE"},
    {"name": "bin_min", "type": "FLOAT64", "mode": "NULLABLE"},
    {"name": "bin_max", "type": "FLOAT64", "mode": "NULLABLE"},
    {"name": "cryptocurrency_symbol", "type": "STRING", "mode": "REQUIRED"},
    {"name": "cryptocurrency_name", "type": "STRING", "mode": "NULLABLE"},
    {"name": "blockchain_network", "type": "STRING", "mode": "NULLABLE"},
    {"name": "crypto_currency_id", "type": "STRING", "mode": "NULLABLE"},
    {"name": "payment_method_id", "type": "STRING", "mode": "REQUIRED"},
    {"name": "payment_method_name", "type": "STRING", "mode": "NULLABLE"},
    {"name": "provider_code", "type": "STRING", "mode": "REQUIRED"},
    {"name": "provider_name", "type": "STRING", "mode": "REQUIRED"},
    {"name": "quote_fiat_amount", "type": "FLOAT64", "mode": "REQUIRED"},
    {"name": "quote_crypto_amount", "type": "FLOAT64", "mode": "REQUIRED"},
    {"name": "quoted_exchange_rate", "type": "FLOAT64", "mode": "NULLABLE"},
    {"name": "reference_spot_price", "type": "FLOAT64", "mode": "NULLABLE"},
    {"name": "provider_fee", "type": "FLOAT64", "mode": "NULLABLE"},
    {"name": "network_fee", "type": "FLOAT64", "mode": "NULLABLE"},
    {"name": "extra_fee", "type": "FLOAT64", "mode": "NULLABLE"},
    {"name": "implicit_spread", "type": "FLOAT64", "mode": "NULLABLE"},
    {"name": "total_fee", "type": "FLOAT64", "mode": "NULLABLE"},
    {"name": "effective_fee_pct", "type": "FLOAT64", "mode": "NULLABLE"},
    {"name": "spread_pct", "type": "FLOAT64", "mode": "NULLABLE"},
    {"name": "fair_crypto_value", "type": "FLOAT64", "mode": "NULLABLE"},
]


def upload_to_bigquery(
    df: pd.DataFrame,
    project_id: str,
    dataset_id: str = "moonpay_growth_study",
    table_id: str = "metamask_provider_quotes",
    credentials_path: Optional[str] = None,
    write_disposition: str = "WRITE_TRUNCATE",
) -> bool:
    """
    Upload DataFrame to BigQuery table with schema enforcement.
    """
    try:
        from google.cloud import bigquery
        from google.oauth2 import service_account

        if credentials_path and os.path.exists(credentials_path):
            credentials = service_account.Credentials.from_service_account_file(credentials_path)
            client = bigquery.Client(project=project_id, credentials=credentials)
        else:
            client = bigquery.Client(project=project_id)

        dataset_ref = client.dataset(dataset_id)

        # Create dataset if not exists
        try:
            client.get_dataset(dataset_ref)
            logger.info("Dataset %s already exists.", dataset_id)
        except Exception:
            dataset = bigquery.Dataset(dataset_ref)
            dataset.location = "US"
            client.create_dataset(dataset, timeout=30)
            logger.info("Created dataset %s in location US.", dataset_id)

        table_ref = dataset_ref.table(table_id)

        # Configure load job
        schema = [bigquery.SchemaField(f["name"], f["type"], mode=f["mode"]) for f in TABLE_SCHEMA]
        job_config = bigquery.LoadJobConfig(
            schema=schema,
            write_disposition=getattr(bigquery.WriteDisposition, write_disposition),
        )

        logger.info("Uploading %d rows to BigQuery table: %s.%s.%s ...", len(df), project_id, dataset_id, table_id)
        job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
        job.result()  # Wait for the job to complete

        table = client.get_table(table_ref)
        logger.info("Successfully loaded %d rows to %s.%s", table.num_rows, dataset_id, table_id)
        return True

    except Exception as e:
        logger.error("BigQuery upload failed: %s", e)
        logger.info("Exporting DataFrame locally as CSV and Parquet for manual/CLI upload.")
        df.to_parquet(f"data/{table_id}.parquet", index=False)
        df.to_csv(f"data/{table_id}.csv", index=False)
        return False


def get_bigquery_cli_instructions(project_id: str = "YOUR_GCP_PROJECT_ID", dataset_id: str = "moonpay_growth_study", table_id: str = "metamask_provider_quotes") -> str:
    """
    Returns step-by-step CLI commands for candidate to run with their Gmail account.
    """
    return f"""
# Step 1: Login to your free GCP account with Gmail:
gcloud auth login
gcloud config set project {project_id}

# Step 2: Create the BigQuery dataset:
bq --location=US mk --dataset {project_id}:{dataset_id}

# Step 3: Load the scraped data CSV into BigQuery:
bq load --autodetect --source_format=CSV \\
    {project_id}:{dataset_id}.{table_id} \\
    data/metamask_provider_quotes.csv
"""
