import json

import bnet_scraper


def lambda_handler(event, context):
    print('event ', event)
    params = event.get('queryStringParameters')
    print('params ', params)
    if not params:
        return {
            'statusCode': 200,
            'body': 'No data provided.'
        }

    server = params.get('server')
    player = params.get('player')

    bnet_scraper.validate_server(server)
    soup = bnet_scraper.get_soup(player, server)
    bnet_scraper.validate_player(player, soup)
    data = bnet_scraper.parse_soup(soup)

    return {
        'statusCode': 200,
        'body': json.dumps(data)
    }
