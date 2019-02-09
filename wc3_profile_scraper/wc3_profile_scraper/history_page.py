"""Scrapes a WC3 game history page from battlenet and returns json."""
from helpers import wash_player_name
from config import data_positions_history
from urllib.parse import parse_qs
import pandas as pd
import json
from bnet_page import BnetPage
from profile_page import ProfilePage


class HistoryPage(BnetPage):
    def __init__(self, player, server, page=1):
        url = 'http://classic.battle.net/war3/ladder/w3xp-player-logged-games.aspx'
        params = {'PlayerName': player, 'PageNo': page, 'Gateway': server}
        super().__init__(server, url, params)
        self.player = player
        self.page = page

    @property
    def game_containers(self):
        return self.soup.find('table', id='tblGames').find_all('tr', class_='rankingRow')

    @property
    def games(self):
        for game in self.game_containers:
            yield Game(self.player, game).parse()

    @property
    def next_page(self):
        url = self.soup.find(text='Next\xa0Page').parent.get('href')
        if url is not None:
            next_page = parse_qs(url).get('PageNo')[0]
            return int(next_page)


class Game:
    def __init__(self, player, soup):
        self.player = player
        self.soup = soup

    def parse(self):
        values = self.soup.find_all(['td'])
        values = [x.get_text().strip() for x in values]
        data = self.parse_values(values)
        game_id = self.soup.find_all(['td'])[0].a.get('href').split('&GameID=')[1]
        data['game_id'] = int(game_id)
        data['team_one'].append(self.player)

        for players in ['team_one', 'team_two']:
            data[players] = [wash_player_name(player) for player in data[players]]

        if data['winner'] == 'Win':
            data['winner'] = data['team_one']
        elif data['winner'] == 'Tie':
            data['winner'] = None
        else:
            data['winner'] = data['team_two']

        return data

    @staticmethod
    def parse_values(values):
        data = {}
        for field, meta_data in data_positions_history.items():
            i = meta_data['position']
            v = values[i]
            formatter = meta_data['function']
            if formatter:
                value = formatter(v)
            data[field] = value

        return data


if __name__ == '__main__':
    print('-- Testing --')
    players = [
        {
            'player': 'Fithydenk',
            'server': 'azeroth'
        }
        # {
        #     'player': 'romantichuman',
        #     'server': 'northrend'
        # },
        # {
        #     'player': 'followgrubby',
        #     'server': 'northrend'
        # },
        # {
        #     'player': 'nightend',
        #     'server': 'northrend'
        # },
        # {
        #     'player': 'tanymommy',
        #     'server': 'northrend'
        # },
        # {
        #     'player': 'ilovenecropolis',
        #     'server': 'northrend'
        # },
        # {
        #     'player': 'alanford',
        #     'server': 'northrend'
        # },
        # {
        #     'player': '123456789012345',
        #     'server': 'northrend'
        # },
        # {
        #     'player': 'ZveroBoy',
        #     'server': 'northrend'
        # },
        # {
        #     'player': 'Feanor',
        #     'server': 'northrend'
        # },
        # {
        #     'player': 'SyDe',
        #     'server': 'northrend'
        # },
        # {
        #     'player': 'Nicker59',
        #     'server': 'northrend'
        # },
        # {
        #     'player': 'rg-back2game',
        #     'server': 'northrend'
        # },
        # {
        #     'player': 'ukto',
        #     'server': 'northrend'
        # },
        # {
        #     'player': 'pieck',
        #     'server': 'northrend'
        # },
        # {
        #     'player': 'IamTry',
        #     'server': 'northrend'
        # },
        # {
        #     'player': 'MisterWinner',
        #     'server': 'northrend'
        # },
        # {
        #     'player': 'Pieck',
        #     'server': 'azeroth'
        # },
        # {
        #     'player': 'Cocaine.',
        #     'server': 'azeroth'
        # },
        # {
        #     'player': 'ALANFORD',
        #     'server': 'Northrend'
        # },
    ]

    for player in players:
        page = 1
        games_all = []

        profile = ProfilePage(**player)
        print("\n{}".format(profile))
        while True:

            history_page = HistoryPage(player.get('player'), player.get('server'), page)
            games = list(history_page.games)
            games_all.extend(games)
            next_page = history_page.next_page
            if (next_page > 10) or (page >= next_page):
                break
            page = next_page

        df = pd.DataFrame(games_all)
        print("Number of games found: {}".format(len(df)))
        print("Most recent game: {}".format(df.loc[0, "date"]))

        data = df.to_dict(orient='records')
        for d in data:
            print(d)
        file_path = './data_backfill/partial/{}/{}.json'.format(
            player.get('server'), player.get('player'))

        with open(file_path, 'w') as f:
            json.dump(data, f)
