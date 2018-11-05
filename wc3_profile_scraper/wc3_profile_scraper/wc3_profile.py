"""Scrapes a WC3 profile page from battlenet and returns json."""
from bs4 import BeautifulSoup
import requests


def get_soup(player=None, server=None):
    url = 'http://classic.battle.net/war3/ladder/w3xp-player-profile.aspx?'
    params = {'Gateway': server, 'PlayerName': player}
    try:
        r = requests.get(url, params=params)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(e)
    soup = BeautifulSoup(r.content, 'lxml')
    return soup


def parse_data(soup):
    data = {}
    tables = find_tables(soup)
    data['individual'] = parse_individual_data(tables['individual'])
    data['team'] = parse_team_data(tables['team'])
    return data


def find_tables(soup):
    soup = soup.find('table', {'class': 'mainTable'})
    tables = soup.find_all('td', {'align': 'center', 'valign': 'top'})
    tables = dict(zip(['info', 'individual', 'team'], tables))
    return tables


def parse_individual_data(table_individual):
    type_ = 'games'
    game_types = ['Team Games', 'Solo Games', 'FFA Games']
    vocab = {'Team Games': 'random_team', 'Solo Games': 'solo', 'FFA Games': 'free_for_all'}
    data = {}

    for game_type, new_key in vocab.items():
        container = table_individual.find(text=game_type)
        if container is not None:
            table = container.parent.parent.parent.parent.parent
            values = [x.get_text() for x in table.find_all('b')]
            d = format_values(type_, values)
            d['win_percentage'] = calc_win_percentage(d['wins'], d['losses'])
            new_key = vocab[game_type]
            data[new_key] = d

    return data


def parse_team_data(table_teams):
    type_ = 'teams'
    teams = table_teams.find_all(text='Partner(s):')
    data = []

    for team in teams:
        table = team.parent.parent.parent.parent.parent.parent.parent.parent
        values = extract_values(table)
        d = format_values(type_, values)
        d['level'] = format_level(table, d['level_base'])
        d.pop('level_base')
        d['win_percentage'] = calc_win_percentage(d['wins'], d['losses'])
        data.append(d)

    return data


def format_values(type_, values):
    fields = ['wins', 'losses', 'partners', 'level', 'rank', 'experience']
    data = {}

    for field in fields:
        meta_data = data_positions[type_][field]
        if not meta_data:
            continue
        i = meta_data['position']
        v = values[i]
        if not v:
            continue
        formatter = meta_data['function']
        if formatter:
            value = formatter(v)
        else:
            value = v

        data[field] = value

    return data


def string_to_int(x):
    return int(x.replace(',', ''))


def format_level(value):
    value = int(value.split('\t')[-1])
    return value


def format_level_decimal(table):
    level_decimal = table.find('td', {'background': '/war3/images/ladder/expbar-bg.gif'})
    level_decimal = level_decimal.find('img').get('width')
    level_decimal = float('00.{}'.format(level_decimal.replace('%', '')))
    return level_decimal


# def get_accurate_level(table, level_base):
#     # level_decimal = format_level_decimal(table)
#     # level = level_base - 1 + (level_decimal * 2)
#     return level_base


def format_rank(value):
    if value == 'Unranked':
        return None
    else:
        return int(value[:-2])


def extract_values(table):
    values = []
    values_old = table.find_all('b')

    for i, value in enumerate(values_old):
        if i == 3:
            partners = [x.get_text() for x in value]
            if len(partners) > 1:
                partners.remove('')
            values.append(partners)

        else:
            values.append(value.get_text())

    return values


def calc_win_percentage(wins, losses):
    win_percentage = round((100 * int(wins)) / (int(wins) + int(losses)), 2)
    return win_percentage


def validate_player(player=None, soup=None):
    error_span = soup.find('span', class_='colorRed')
    if error_span is not None:
        raise Exception('Invalid player: {}'.format(player))


def validate_server(server):
    servers = ['azeroth', 'lordaeron', 'northrend', 'kalimdor']
    if not server.lower() in servers:
        raise Exception('Invalid server: {}'.format(server))

data_positions = {
    'teams':
    {
        'wins':
        {
            'position': 0,
            'function': int
        },
        'losses':
        {
            'position': 1,
            'function': int
        },
        'level':
        {
            'position': 2,
            'function': format_level
        },
        'partners':
        {
            'position': 3,
            'function': None
        },
        'rank':
        {
            'position': 4,
            'function': format_rank
        },
        'experience': None
    },
    'games':
    {
        'wins':
        {
            'position': 4,
            'function': int
        },
        'losses':
        {
            'position': 5,
            'function': int
        },
        'level':
        {
            'position': 1,
            'function': format_level
        },
        'partners': None,
        'rank':
        {
            'position': 3,
            'function': format_rank
        },
        'experience':
        {
            'position': 2,
            'function': string_to_int
        }
    }
}
