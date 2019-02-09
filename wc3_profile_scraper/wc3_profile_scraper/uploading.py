import os
import json
from google.cloud import bigquery
from history_page import HistoryPage


def get_new_games(player, server, last_bq_date=None):
    def no_more_dates():
        if last_bq_date is None:
            return False
        else:
            return current_date <= last_bq_date

    def no_more_pages():
        return page >= next_page

    data_all = []
    page = 1

    while True:
        history_page = HistoryPage(player, server, page)
        data = history_page.games()
        next_page = history_page.next_page

        for d in data:
            current_date = dateparser.parse(d.get('date'))
            if no_more_dates() or no_more_pages():
                return data_all
            else:
                data_all.append(d)

        page = next_page


def lambda_handler(event, context):
    print(event)
    data_input = event.get('queryStringParameters')
    print(data_input)

    bigquery_credpath = os.path.abspath('./BigQuery Reader Project-88493810ca62.json')
    client = bigquery.Client.from_service_account_json(bigquery_credpath)
    job_config = bigquery.LoadJobConfig()
    job_config.skip_leading_rows = 1
    job_config.autodetect = True
    dataset_id = 'wc3'
    dataset_ref = client.dataset(dataset_id)
    table_name = players.get('server')
    table_ref = dataset_ref.table(table_name)

    history_page = HistoryPage(data_input.get('player_one'), data_input.get('server'))
    data = list(history_page.games())
    query = ('''SELECT date FROM  `bigquery-reader-project.wc3.{server}`,
        UNNEST(team_one) AS first WHERE first IN ('{player_one}') ORDER BY date DESC LIMIT 1
    '''.format(**data_input))

    job = client.query(query)
    row = list(job.result())[0]
    last_bq_date = row.get('date')
    print(last_bq_date)

    history_page = HistoryPage(data_input.get('player_one'), data_input.get('server'))
    data = list(history_page.games())
    df_new = pd.DataFrame(data)
    df_new['date'] = pd.to_datetime(df_new['date'])
    df_new = df_new[df_new['date'] > last_date]
    new_games = get_new_games(player, server, last_bq_date=None)

    if len(new_games) > 0:
        data = df_new.to_dict(orient='records')
        table = client.get_table(table_ref)
        errors = client.insert_rows(table, new_games)
# try:
    #     profile = Profile(**params)
    #     router = {
    #         '/solo': profile.request_solo(),
    #         '/random_team': profile.request_random_team(),
    #         '/info': profile.request_info()
    #     }

    #     message = router.get(path)
    #     return {
    #         'statusCode': 200,
    #         'body': json.dumps(message)
    #     }

    # except Exception as e:
    #     return {
    #         'statusCode': 400,
    #         'body': json.dumps(str(e))
    #     }

if __name__ == '__main__':
    player = 'romantichuman2'
    server = 'azeroth'
    path = '/solo'
    event = {'resource': '/', 'path': '/', 'httpMethod': 'GET', 'headers': {'accept': 'application/json', 'Host': 'bqeat6w63f.execute-api.us-east-1.amazonaws.com', 'X-Amzn-Trace-Id': 'Root=1-5bee09ca-65f4c47d59fc60984c0a93eb', 'X-Forwarded-For': '18.212.29.137', 'X-Forwarded-Port': '443', 'X-Forwarded-Proto': 'https'}, 'multiValueHeaders': {'accept': ['application/json'], 'Host': ['bqeat6w63f.execute-api.us-east-1.amazonaws.com'], 'X-Amzn-Trace-Id': ['Root=1-5bee09ca-65f4c47d59fc60984c0a93eb'], 'X-Forwarded-For': ['18.212.29.137'], 'X-Forwarded-Port': ['443'], 'X-Forwarded-Proto': ['https']}, 'queryStringParameters': {
            'player_one': 'followgrubby',
            'player_two': 'Fall3n',
            'server': 'northrend'
        }, 'multiValueQueryStringParameters': {'player': ['boys-fuk-me'], 'server': ['nort2hrend']}, 'pathParameters': None, 'stageVariables': None, 'requestContext': {'resourceId': 'mdicp3cstd', 'resourcePath': '{}'.format(path), 'httpMethod': 'GET', 'extendedRequestId': 'QbZ3mHoyoAMFmCw=', 'requestTime': '16/Nov/2018:00:05:30 +0000', 'path': '/dev', 'accountId': '153852854695', 'protocol': 'HTTP/1.1', 'stage': 'dev', 'domainPrefix': 'bqeat6w63f', 'requestTimeEpoch': 1542326730241, 'requestId': '5457479a-e933-11e8-b1bd-7b60b897e033', 'identity': {'cognitoIdentityPoolId': None, 'accountId': None, 'cognitoIdentityId': None, 'caller': None, 'sourceIp': '18.212.29.137', 'accessKey': None, 'cognitoAuthenticationType': None, 'cognitoAuthenticationProvider': None, 'userArn': None, 'userAgent': None, 'user': None}, 'domainName': 'bqeat6w63f.execute-api.us-east-1.amazonaws.com', 'apiId': 'bqeat6w63f'}, 'body': None, 'isBase64Encoded': False}
    result = lambda_handler(event, None)
    print(result)

# file_path = './data_backfill/ALANFORD.json'
# with open(file_path, 'r') as f:
#     data = json.loads(f.read())
#     print(len(data))
#     print(data)
# bigquery_credpath = os.path.abspath('/Users/cdaly/Box Sync/Daly, Christopher/Keys/BigQuery Reader Project-88493810ca62.json')
# client = bigquery.Client.from_service_account_json(bigquery_credpath)
# job_config = bigquery.LoadJobConfig()
# job_config.skip_leading_rows = 1
# job_config.autodetect = True

# dataset_id = 'wc3'
# table_name = 'northrend'
# dataset_ref = client.dataset(dataset_id)
# table_ref = dataset_ref.table(table_name)
# table = client.get_table(table_ref)
# print(table)
# errors = client.insert_rows(table, data)
# try:
#     assert errors == []
# except Exception:
#     print(Exception, errors[0])
# print(errors)
