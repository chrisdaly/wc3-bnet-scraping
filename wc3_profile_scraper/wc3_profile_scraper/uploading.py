import os
import json
from google.cloud import bigquery

file_path = './data_backfill/followgrubby.json'
with open(file_path, 'r') as f:
    data = json.loads(f.read())
    print(len(data))
    print(data)
bigquery_credpath = os.path.abspath('./BigQuery Reader Project-88493810ca62.json')
client = bigquery.Client.from_service_account_json(bigquery_credpath)
job_config = bigquery.LoadJobConfig()
job_config.skip_leading_rows = 1
job_config.autodetect = True

dataset_id = 'wc3'
table_name = 'history2'
dataset_ref = client.dataset(dataset_id)
table_ref = dataset_ref.table(table_name)
table = client.get_table(table_ref)
print(table)
errors = client.insert_rows(table, data)
try:
    assert errors == []
except Exception:
    print(Exception, errors[0])
print(errors)
