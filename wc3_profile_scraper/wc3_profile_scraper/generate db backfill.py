import os
import json
import dateparser
from ladder_page import LadderPage
from history_page import HistoryPage

def get_new_games(player, server, last_bq_date=None):
    print('Looking for new games...')
    def no_more_dates():
        if last_bq_date is None:
            return False
        else:
            return current_date <= last_bq_date
        
    def no_more_pages():
        return page >= next_page
    
    new_games = []
    page = 1
    
    while True:
        
        history_page = HistoryPage(player, server, page)
        games = history_page.games
        next_page = history_page.next_page

        for d in games:
            current_date = dateparser.parse(d.get('date'))
            if no_more_dates():
                return new_games
            else:
                new_games.append(d)
        
        if no_more_pages():
            return new_games
        else:
            page = next_page


if __name__ == '__main__':
	servers = ['azeroth', 'lordaeron', 'northrend']
	for server in servers:
		dir_ = './data_backfill/{}'.format(server)
		if not os.path.exists(dir_):
			os.makedirs(dir_)

		ladder_page = LadderPage(server)
		print(ladder_page)

		for row in ladder_page.rows:
			player = row.get('player')
			print(player, server)
			games = get_new_games(player, server)
			print(len(games))

			with open('{}/{}.json'.format(dir_, player), 'w') as f:
				json.dump(games, f)