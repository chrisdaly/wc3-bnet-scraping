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


def get_tables(soup):
    soup = soup.find('table', {'class': 'mainTable'})
    game_tables = soup.find_all('td', {'align': 'center', 'valign': 'top'})
    tables = {
        'stats': game_tables[0],
        'individual': game_tables[1],
        'team': game_tables[2]
    }

    return tables


def get_individual_data(table_player):
    type_ = 'games'
    game_types = ['Team Games', 'Solo Games', 'FFA Games']
    vocab = {'Team Games': 'random_team', 'Solo Games': 'solo', 'FFA Games': 'free_for_all'}
    data = {}

    for game_type in game_types:
        table = table_player.find(text=game_type)
        if table:
            table = table_player.find(text=game_type).parent.parent.parent.parent.parent
            values = [x.get_text() for x in table.find_all('b')]
            d = parse_values(type_, values)
            d['level'] = get_level(table, d['level_base'])
            d.pop('level_base')
            d['win_percentage'] = calc_win_percentage(d['wins'], d['losses'])
            key = vocab[game_type]
            data[key] = d

    return data


def parse_values(type_, values):
    fields = ['wins', 'losses', 'partners', 'level_base', 'rank', 'experience']
    data = {}

    for field in fields:
        d = data_positions[type_][field]
        if not d:
            continue
        i = d['position']
        v = values[i]
        if not v:
            continue
        f = d['function']
        if f:
            value = f(v)
        else:
            value = v

        data[field] = value

    return data


def get_team_data(table_teams):
    type_ = 'teams'
    teams = table_teams.find_all(text='Partner(s):')
    data = []

    for team in teams:
        table = team.parent.parent.parent.parent.parent.parent.parent.parent
        values = extract_values(table)
        d = parse_values(type_, values)
        d['level'] = get_level(table, d['level_base'])
        d.pop('level_base')
        d['win_percentage'] = calc_win_percentage(d['wins'], d['losses'])
        data.append(d)

    return data


def parse_soup(soup):
    data = {}
    tables = get_tables(soup)
    data['individual'] = get_individual_data(tables['individual'])
    data['team'] = get_team_data(tables['team'])
    return data


def make_int(x):
    return int(x)


def get_level_base(value):
    value = int(value.split('\t')[-1])
    return value


def get_level_decimal(table):
    level_decimal = table.find('td', {'background': '/war3/images/ladder/expbar-bg.gif'})
    level_decimal = level_decimal.find('img').get('width')
    level_decimal = float('00.{}'.format(level_decimal.replace('%', '')))
    return level_decimal


def get_level(table, level_base):
    level_decimal = get_level_decimal(table)
    level = level_base - 1 + (level_decimal * 2)
    return level


def get_rank(value):
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
            'function': make_int
        },
        'losses':
        {
            'position': 1,
            'function': make_int
        },
        'level_base':
        {
            'position': 2,
            'function': get_level_base
        },
        'partners':
        {
            'position': 3,
            'function': None
        },
        'rank':
        {
            'position': 4,
            'function': get_rank
        },
        'experience': None
    },
    'games':
    {
        'wins':
        {
            'position': 4,
            'function': make_int
        },
        'losses':
        {
            'position': 5,
            'function': make_int
        },
        'level_base':
        {
            'position': 1,
            'function': get_level_base
        },
        'partners': None,
        'rank':
        {
            'position': 3,
            'function': get_rank
        },
        'experience':
        {
            'position': 2,
            'function': None
        }
    }
}
