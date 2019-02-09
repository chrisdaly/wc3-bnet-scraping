"""Scrapes a WC3 profile page from battlenet and returns json."""
from bnet_page import BnetPage
import re


class LadderPage(BnetPage):
    def __init__(self, server, page=1):
        url = 'http://classic.battle.net/war3/ladder/w3xp-ladder-solo.aspx'
        params = {'Gateway': server, 'PageNo': page}
        super().__init__(server, url, params)

    def __str__(self):
        return '@{}'.format(self.server)

    def __repr__(self):
        return '@{}'.format(self.server)

    @property
    def rows_soup(self):
        return self.soup.find('table', id='LeaderBoard').find_all('tr', class_='rankingRow')

    @property
    def rows(self):
        for rank_row in self.rows_soup:
            yield Row(rank_row).parse()


class Row:
    def __init__(self, soup):
        self.soup = soup

    def parse(self):
        player = self.soup.find('span', class_='rankingName').get_text()
        rank_string = self.soup.find('td').get_text().strip()
        rank = int(re.findall(r'\d+', rank_string)[0])
        data = {
            'player': player,
            'rank': rank
        }
        return data


if __name__ == '__main__':
    server = 'northrend'

    print('-- Testing --')
    ladder_page = LadderPage('northrend')
    print(ladder_page)
    print(list(ladder_page.rows))
