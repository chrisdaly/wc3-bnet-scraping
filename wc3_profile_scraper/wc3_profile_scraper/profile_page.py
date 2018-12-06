"""Scrapes a WC3 profile page from battlenet and returns json."""
from bs4 import BeautifulSoup
from botocore.vendored import requests
import dateparser
import pandas as pd
from config import data_positions_profile


class ProfilePage:
    def __init__(self, player, server):
        self.player = player
        self.server = server.title()
        self.params = {'PlayerName': self.player, 'Gateway': self.server}
        self.url = 'http://classic.battle.net/war3/ladder/w3xp-player-profile.aspx?'
        self.servers = ['azeroth', 'lordaeron', 'northrend', 'kalimdor']
        self.soup = self.get_soup()
        self._validate()
        self.tables = self._parse_tables()

    def __str__(self):
        return '{}@{}'.format(self.player, self.server)

    def get_soup(self):
        try:
            r = requests.get(self.url, params=self.params, timeout=5)
        except:
            raise
        return BeautifulSoup(r.content, 'lxml')

    def _validate(self):
        self.validate_server()
        self.validate_player()
        self.valiidate_page()

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
            'player': self.player,
            'server': self.server,
            'clan': self.clan,
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
        last_ladder_game = soup.find(text='Last Ladder Game:')
        if last_ladder_game is not None:
            last_ladder_game = last_ladder_game.parent.parent.b.get_text()
        last_ladder_game = str(dateparser.parse(last_ladder_game).date())
        return last_ladder_game

    @property
    def main_race(self):
        soup = self.tables.get('info')
        overall_stats_table = soup.find('td', class_='rankingHeader')
        if overall_stats_table is not None:
            overall_stats_table = overall_stats_table.parent.parent
        rows = overall_stats_table.find_all('tr')[1:-1]
        df = self.parse_stats_table(rows)
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
        clan_url = soup.find('a', href=lambda x: x and x.startswith('w3xp-clan-profile.aspx?'))
        if clan_url is not None:
            return clan_url.get_text()
        return 'N/A'

    @staticmethod
    def format_values(type_, values):
        fields = ['wins', 'losses', 'partners', 'level', 'rank', 'experience']
        data = {}

        for field in fields:
            meta_data = data_positions_profile[type_][field]
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

    def validate_server(self):
        if self.server.lower() not in self.servers:
            raise Exception('{} | Invalid server'.format(str(self)))

    def validate_player(self):
        error_span = self.soup.find('span', class_='colorRed')
        if error_span is not None:
            raise Exception('{} | Profile not found'.format(str(self)))

    def valiidate_page(self):
        if self.soup.find(text='Error Encountered'):
            raise Exception('{} | Invalid request'.format(str(self)))

    def request_solo(self):
        data = self.individual.get('solo')
        if data is not None:
            data.update({
                'main_race': self.main_race,
                'player': self.player,
                'server': self.server,
            })
        return data

    def request_random_team(self):
        data = self.individual.get('random_team')
        if data is not None:
            data.update({
                'main_race': self.main_race,
                'player': self.player,
                'server': self.server,
            })
        return data

    def request_info(self):
        data = self.information
        if data is not None:
            return data

if __name__ == '__main__':
    players = [
        {
            'player': 'romantichuman',
            'server': 'northrend'
        },
        {
            'player': 'pieck',
            'server': 'northrend'
        },
        {
            'player': 'pieck',
            'server': 'azeroth'
        },
        {
            'player': 'wearefoals',
            'server': 'northrend'
        },
        {
            'player': 'wearefoals',
            'server': 'azeroth'
        },
        {
            'player': 'wearefoals',
            'server': 'fake_server'
        },
        {
            'player': 'fake_player',
            'server': 'azeroth'
        },
        {
            'player': 'moon1234',
            'server': 'northrend'
        },
    ]
    print('-- Testing --')
    for player in players:
        print()
        try:
            profile = ProfilePage(**player)
            print(profile)
            print(profile.parse())
        except Exception as e:
            print(e)
