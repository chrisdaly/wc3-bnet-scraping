import requests
from bs4 import BeautifulSoup


class BnetPage:
    def __init__(self, server, url, params):
        self.server = server.title()
        self.url = url
        self.servers = ['azeroth', 'lordaeron', 'northrend', 'kalimdor']
        self.timeout = 10
        self.params = params
        self.soup = self.get_soup()
        self._validate()

    def __str__(self):
        return '{}@{}'.format(self.params.get('PlayerName'), self.server)

    def __repr__(self):
        return '{}@{}'.format(self.params.get('PlayerName'), self.server)

    def _validate(self):
        self.validate_server()
        self.validate_player()
        self.validate_page()

    def validate_player(self):
        error_span = self.soup.find('span', class_='colorRed')
        if error_span is not None:
            raise Exception('{} | Profile not found'.format(str(self)))

    def validate_server(self):
        if self.server.lower() not in self.servers:
            raise Exception('{} | Invalid server'.format(str(self)))

    def validate_page(self):
        if self.soup.find(text='Error Encountered'):
            raise Exception('{} | Invalid request'.format(str(self)))

    def get_soup(self):
        try:
            r = requests.get(self.url, params=self.params, timeout=self.timeout)
        except:
            raise
        return BeautifulSoup(r.content, 'lxml')

if __name__ == '__main__':
    players = [
        {
            'player': 'Rellik',
            'server': 'northrend'
        }
    ]
    url = 'http://classic.battle.net/war3/ladder/w3xp-player-profile.aspx'
    print('-- Testing --')
    for player in players:
        params = {'PlayerName': player.get('player'), 'Gateway': player.get('server')}
        page = BnetPage(player.get('server'), url, params)
        print(page)
