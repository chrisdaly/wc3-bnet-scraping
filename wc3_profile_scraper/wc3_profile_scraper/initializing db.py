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


def get_schema_from_json(json, schema=[]):
    input_json = json.copy()
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


def database_setup(configuration, client, dataset_id):
    dataset_ref = client.dataset(dataset_id)
    create_dataset(dataset_ref, location='US')

    for table_name in ['northrend', 'azeroth']:
        fields = configuration.get('fields')
        schema = get_schema_from_json(fields, [])
        file_path = './data_backfill/{}.json'.format(table_name)
        try:
            with open(file_path, 'r') as f:
                data = json.loads(f.read())
        except Exception:
            print('No data found')

        create_table(dataset_id, table_name, schema, data)


def create_table(dataset_id, table_name, schema, data):
    dataset_ref = client.dataset(dataset_id)
    table_ref = dataset_ref.table(table_name)
    table = bigquery.Table(table_ref, schema=schema)
    if check_table_exists(table_ref):
        print('\n-- Table {} already exists --\n'.format(table_ref))
        return

    table = client.create_table(table)
    batches = divide_into_batches(data, 10000)
    for batch in batches:
        errors = client.insert_rows(table, batch)
        try:
            assert errors == []
        except Exception:
            print(Exception, errors[0])
    print('\n-- Table {} created --\n'.format(table_name))


def update_table(dataset_id, table_name, new_games):
    dataset_ref = client.dataset(dataset_id)
    table_ref = dataset_ref.table(table_name)
    table = client.get_table(table_ref)
    errors = client.insert_rows(table, new_games, insertId='game_id')
    try:
        assert errors == []
    except Exception:
        print(Exception, errors[0])
    print('Uploaded {} new games'.format(len(new_games)))

bigquery_credpath = os.path.abspath('/Users/cdaly/Box Sync/Daly, Christopher/Keys/BigQuery Reader Project-88493810ca62.json')
client = bigquery.Client.from_service_account_json(bigquery_credpath)
job_config = bigquery.LoadJobConfig()
job_config.skip_leading_rows = 1
job_config.autodetect = True
dataset_id = 'wc3'

with open('./table_config.json', 'r') as f:
    configuration = json.loads(f.read())
database_setup(configuration, client, dataset_id)
