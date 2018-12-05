import os
import json
from google.cloud import bigquery


def create_dataset(dataset_ref, location='US'):
    dataset = bigquery.Dataset(dataset_ref)
    try:
        dataset = client.create_dataset(dataset)
        print('\n-- Dataset {} created --'.format(dataset_id))
    except:
        print('\n-- Dataset {} already exists --'.format(dataset_id))


def check_table_exists(table_ref):
    try:
        client.get_table(table_ref)
        return True
    except:
        return False


def get_schema_from_json(input_json, schema=[]):
    if not input_json:
        return schema

    cur = input_json.pop()
    name = cur['name']
    field_type = cur['type']
    mode = cur['mode']
    fields = [] if 'fields' not in cur else get_schema_from_json(cur['fields'], [])
    schema.append(bigquery.SchemaField(name=name, field_type=field_type, mode=mode, fields=fields))

    return get_schema_from_json(input_json, schema)


def divide_into_batches(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

bigquery_credpath = os.path.abspath('./BigQuery Reader Project-88493810ca62.json')
client = bigquery.Client.from_service_account_json(bigquery_credpath)
job_config = bigquery.LoadJobConfig()
job_config.skip_leading_rows = 1
job_config.autodetect = True

dataset_id = 'wc3'
dataset_ref = client.dataset(dataset_id)

create_dataset(dataset_ref, location='US')

print('STARTING')
with open('./table_config.json', 'r') as f:
    config = json.loads(f.read())
dataset_id = 'wc3'
dataset_ref = client.dataset(dataset_id)
create_dataset(dataset_ref)

for table_name in ['northrend']:
    # config = configurations[0]
    # table_name = config.get('name')
    fields = config.get('fields')
    print(table_name)
    schema = get_schema_from_json(fields, [])
    print(schema)

    table_ref = dataset_ref.table(table_name)
    table = bigquery.Table(table_ref, schema=schema)
    if check_table_exists(table_ref):
        print('\n-- Table {} already exists --\n\n'.format(table_ref))

    else:
        table = client.create_table(table)
        file_path = './data_backfill/{}.json'.format(table_name)
        with open(file_path, 'r') as f:
            data = json.loads(f.read())
            print(len(data))

        batches = divide_into_batches(data, 10000)
        for batch in batches:
            errors = client.insert_rows(table, batch)
            try:
                assert errors == []
            except Exception:
                print(Exception, errors[0])
        print('\n-- Table {} created --\n\n'.format(table_name))
