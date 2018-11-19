import json
import sys
# sys.path.insert(0, './wc3_profile_scraper/wc3_profile_scraper/')
from wc3_profile_scraper import *

def lambda_handler(event, context):
    print(event)
    path = event.get('requestContext').get('resourcePath')
    params = event.get('queryStringParameters')
    print(path, params)

    try:
        profile = Profile(**params)
        router = {
            '/solo': profile.request_solo(),
            '/random_team': profile.request_random_team(),
            '/info': profile.request_info()
        }

        message = router.get(path)
        return {
            'statusCode': 200,
            'body': json.dumps(message)
        }

    except Exception as e:
        return {
            'statusCode': 400,
            'body': json.dumps(str(e))
        }

if __name__ == '__main__':
    player = 'romantichuman2'
    server = 'azeroth'
    path = '/solo'
    event = {'resource': '/', 'path': '/', 'httpMethod': 'GET', 'headers': {'accept': 'application/json', 'Host': 'bqeat6w63f.execute-api.us-east-1.amazonaws.com', 'X-Amzn-Trace-Id': 'Root=1-5bee09ca-65f4c47d59fc60984c0a93eb', 'X-Forwarded-For': '18.212.29.137', 'X-Forwarded-Port': '443', 'X-Forwarded-Proto': 'https'}, 'multiValueHeaders': {'accept': ['application/json'], 'Host': ['bqeat6w63f.execute-api.us-east-1.amazonaws.com'], 'X-Amzn-Trace-Id': ['Root=1-5bee09ca-65f4c47d59fc60984c0a93eb'], 'X-Forwarded-For': ['18.212.29.137'], 'X-Forwarded-Port': ['443'], 'X-Forwarded-Proto': ['https']}, 'queryStringParameters': {'player': '{}'.format(player), 'server': '{}'.format(server)}, 'multiValueQueryStringParameters': {'player': ['boys-fuk-me'], 'server': ['nort2hrend']}, 'pathParameters': None, 'stageVariables': None, 'requestContext': {'resourceId': 'mdicp3cstd', 'resourcePath': '{}'.format(path), 'httpMethod': 'GET', 'extendedRequestId': 'QbZ3mHoyoAMFmCw=', 'requestTime': '16/Nov/2018:00:05:30 +0000', 'path': '/dev', 'accountId': '153852854695', 'protocol': 'HTTP/1.1', 'stage': 'dev', 'domainPrefix': 'bqeat6w63f', 'requestTimeEpoch': 1542326730241, 'requestId': '5457479a-e933-11e8-b1bd-7b60b897e033', 'identity': {'cognitoIdentityPoolId': None, 'accountId': None, 'cognitoIdentityId': None, 'caller': None, 'sourceIp': '18.212.29.137', 'accessKey': None, 'cognitoAuthenticationType': None, 'cognitoAuthenticationProvider': None, 'userArn': None, 'userAgent': None, 'user': None}, 'domainName': 'bqeat6w63f.execute-api.us-east-1.amazonaws.com', 'apiId': 'bqeat6w63f'}, 'body': None, 'isBase64Encoded': False}
    result = lambda_handler(event, None)
    print(result)
