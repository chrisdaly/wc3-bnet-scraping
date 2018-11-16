"""Scrapes a WC3 profile page from battlenet and returns json."""
from bs4 import BeautifulSoup
import requests
import re
import dateparser
import pandas as pd
from config import data_positions

class Profile:
    def __init__(self, player, server):
        self.player = player
        self.server = server.title()
        self.params = {'PlayerName': self.player, 'Gateway': self.server}
        self.url = 'http://classic.battle.net/war3/ladder/w3xp-player-profile.aspx?'
        self.soup = self.get_soup()
        self._validate()
        self.tables = self._parse_tables()

    def get_soup(self):
        try:
            r = requests.get(self.url, params=self.params)
        except requests.exceptions.RequestException as e:
            print(e)

        return BeautifulSoup(r.content, 'lxml')

    def _validate(self):
        self.validate_server()
        self.validate_player()

    def parse(self):
        data = {}
        data['info'] = self.information
        data['individual'] = self.individual
        data['team'] = self.team
        return data

    def _parse_tables(self):
        soup = self.soup.find('table', class_='mainTable')
        tables = soup.find_all('td', {'align': 'center', 'valign': 'top'})
        tables = dict(zip(['info', 'individual', 'team'], tables))
        return tables

    @property
    def information(self):
        return {
            'clan': self.clan,
            'player': self.player,
            'server': self.server,
            'main_race': self.main_race,
            'home_page': self.home_page,
            'additional_info': self.parse_additional_info,
            'last_ladder_game': self.last_ladder_game
        }

    @property
    def individual(self):
        soup = self.tables.get('individual')
        type_ = 'individual'
        vocab = {'Team Games': 'random_team', 'Solo Games': 'solo', 'FFA Games': 'free_for_all'}
        data = {}

        for game_type, new_key in vocab.items():
            container = soup.find(text=game_type)
            if container is not None:
                table = container.parent.parent.parent.parent.parent
                values = [x.get_text() for x in table.find_all('b')]
                d = self.format_values(type_, values)
                d['win_percentage'] = self.calc_win_percentage(d['wins'], d['losses'])
                new_key = vocab[game_type]
                data[new_key] = d

        return data

    @property
    def team(self):
        soup = self.tables.get('team')
        type_ = 'teams'
        teams = soup.find_all(text='Partner(s):')
        data = []

        for team in teams:
            table = team.parent.parent.parent.parent.parent.parent.parent.parent
            values = self.extract_values(table)
            d = self.format_values(type_, values)
            d['win_percentage'] = self.calc_win_percentage(d['wins'], d['losses'])
            data.append(d)

        return data

    @property
    def home_page(self):
        soup = self.tables.get('info')
        home_page = soup.find('div', {'id': 'homePage'})
        home_page = home_page.b.get_text().strip()
        if home_page == '':
            return 'N/A'
        return home_page

    @property
    def parse_additional_info(self):
        soup = self.tables.get('info')
        additional_info_div = soup.find('div', {'id': 'additionalInfo'})
        script = additional_info_div.script.get_text()
        text_start = 'document.write("'
        i = script.find(text_start)
        if i == -1:
            additional_info = None
        else:
            i += len(text_start)

        text_end = '");'
        j = script[i:].find(text_end)
        additional_info = script[i: i + j]

        if additional_info in ['', None]:
            return 'N/A'
        return additional_info

    @property
    def last_ladder_game(self):
        soup = self.tables.get('info')
        last_ladder_game = soup.find(text='Last Ladder Game:').parent.parent.b.get_text()
        last_ladder_game = str(dateparser.parse(last_ladder_game).date())
        return last_ladder_game

    @property
    def main_race(self):
        soup = self.tables.get('info')
        overall_stats_table = soup.find('td', class_='rankingHeader').parent.parent
        rows = overall_stats_table.find_all('tr')[1:-1]
        df = self.parse_stats_table(rows)
        i = df['total_games'].idxmax()

        if len(df[df['percentage_games'] >= 75]) != 0:
            main_race = df[df['percentage_games'] >= 75]['race'].values[0].title() 
        else:
            main_race = 'No main race'

        return main_race

    @staticmethod
    def parse_stats_table(rows):
        data = []
        keys = ['race', 'wins', 'losses', 'win_percentage']

        for row in rows:
            row = [x.get_text().strip() for x in row.find_all('td')]
            row = dict(zip(keys, row))
            row['num_games'] = int(row['losses']) + int(row['wins'])
            data.append(row)

        df = pd.DataFrame(data)
        df['percentage_games'] = df['num_games'] * 100 / sum(df['num_games'])
        df['race'] = df['race'].apply(lambda x: x.lower().replace(':', ''))

        for col in ['wins', 'losses']:
            df[col] = df[col].astype(int)

        df['total_games'] = df['losses'] + df['wins']

        return df

    @property
    def clan(self):
        soup = self.tables.get('info')
        clan_url = soup.find(href=re.compile('ClanTag='))
        if clan_url is not None:
            return clan_url.get_text()

    @staticmethod
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

    @staticmethod
    def calc_win_percentage(wins, losses):
        win_percentage = round((100 * int(wins)) / (int(wins) + int(losses)), 2)
        return '{0:.2f}%'.format(win_percentage)

    @staticmethod
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

    def validate_player(self):
        error_span = self.soup.find('span', class_='colorRed')
        if error_span is not None:
            raise Exception('{}@{} | Profile not found'.format(self.player, self.server))

    def validate_server(self):
        servers = ['azeroth', 'lordaeron', 'northrend', 'kalimdor']
        if self.server.lower() not in servers:
            raise Exception('{}@{} | Invalid server'.format(self.player, self.server))

    def request_solo(self):
        data = self.individual.get('solo')
        if data is None:
            return '{}@{} | {} | SOLO, N/A'.format(self.player, self.server, self.main_race)
        data.update({
            'main_race': self.main_race,
            'player': self.player,
            'server': self.server,
        })
        message = '{player}@{server} | {main_race} | SOLO, Level {level}, {rank}, {wins} Wins, {losses} Losses, {win_percentage}'
        return message.format(**data)

    def request_random_team(self):
        data = self.individual.get('random_team')
        if data is None:
            return '{}@{} | {} | TEAM, N/A'.format(self.player, self.server, self.main_race)

        data.update({
            'main_race': self.main_race,
            'player': self.player,
            'server': self.server,
        })
        message = '{player}@{server} | {main_race} | RANDOM TEAM, Level {level}, {rank}, {wins} Wins, {losses} Losses, {win_percentage}'
        return message.format(**data)

    def request_info(self):
        data = self.information
        if data is None:
            return '{}@{} | {} | INFORMATION, N/A'.format(self.player, self.server, self.main_race)
        message = '{player}@{server} | {main_race} | INFORMATION, Clan {clan}, Last ladder game {last_ladder_game}, {home_page}, {additional_info}'
        return message.format(**data)

if __name__ == '__main__':
    # players = [
    #     {
    #         'player': 'romantichuman',
    #         'server': 'northrend'
    #     },
    #     {
    #         'player': 'wearefoals',
    #         'server': 'northrend'
    #     },
    #     {
    #         'player': 'wearefoals',
    #         'server': 'azeroth'
    #     },
    # ]
    # for player in players:
    #     profile = Profile(**player)
    #     print(profile.request_solo())
    #     print(profile.request_random_team())
    #     print(profile.request_info())
    #     print()

    event = {'resource': '/', 'path': '/', 'httpMethod': 'GET', 'headers': {'accept': 'application/json', 'Host': 'bqeat6w63f.execute-api.us-east-1.amazonaws.com', 'X-Amzn-Trace-Id': 'Root=1-5bee09ca-65f4c47d59fc60984c0a93eb', 'X-Forwarded-For': '18.212.29.137', 'X-Forwarded-Port': '443', 'X-Forwarded-Proto': 'https'}, 'multiValueHeaders': {'accept': ['application/json'], 'Host': ['bqeat6w63f.execute-api.us-east-1.amazonaws.com'], 'X-Amzn-Trace-Id': ['Root=1-5bee09ca-65f4c47d59fc60984c0a93eb'], 'X-Forwarded-For': ['18.212.29.137'], 'X-Forwarded-Port': ['443'], 'X-Forwarded-Proto': ['https']}, 'queryStringParameters': {'player': 'wearefoals', 'server': 'northrend'}, 'multiValueQueryStringParameters': {'player': ['boys-fuk-me'], 'server': ['nort2hrend']}, 'pathParameters': None, 'stageVariables': None, 'requestContext': {'resourceId': 'mdicp3cstd', 'resourcePath': '/', 'httpMethod': 'GET', 'extendedRequestId': 'QbZ3mHoyoAMFmCw=', 'requestTime': '16/Nov/2018:00:05:30 +0000', 'path': '/dev', 'accountId': '153852854695', 'protocol': 'HTTP/1.1', 'stage': 'dev', 'domainPrefix': 'bqeat6w63f', 'requestTimeEpoch': 1542326730241, 'requestId': '5457479a-e933-11e8-b1bd-7b60b897e033', 'identity': {'cognitoIdentityPoolId': None, 'accountId': None, 'cognitoIdentityId': None, 'caller': None, 'sourceIp': '18.212.29.137', 'accessKey': None, 'cognitoAuthenticationType': None, 'cognitoAuthenticationProvider': None, 'userArn': None, 'userAgent': None, 'user': None}, 'domainName': 'bqeat6w63f.execute-api.us-east-1.amazonaws.com', 'apiId': 'bqeat6w63f'}, 'body': None, 'isBase64Encoded': False}
    params = event.get('queryStringParameters')
    profile = Profile(**params)
    print(profile.request_solo())
    # validate_server(server)
    # soup = get_soup(player, server)
    # validate_player(player, soup)
    # data = parse_data(soup)
    # print(data)
