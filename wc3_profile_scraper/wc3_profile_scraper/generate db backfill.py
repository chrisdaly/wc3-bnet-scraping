import os
import json
import dateparser
import datetime
from ladder_page import LadderPage
from history_page import HistoryPage
from profile_page import ProfilePage


def get_games(player, server, last_date=datetime.datetime(2016, 1, 1)):
    def no_more_dates(current_date):
        # If a game has gone past the last_date (database one or "epoch") then return True.
        return current_date <= last_date

    def no_more_pages():
        return page >= next_page

    games_all = []
    page = 1

    profile = ProfilePage(player=player, server=server)
    print("\n{}".format(profile))

    while True:
        history_page = HistoryPage(player, server, page)
        games = history_page.games
        next_page = history_page.next_page

        for d in games:
            current_date = dateparser.parse(d.get('date'))
            # Check if a game on this page has gone past the period of interest.
            if no_more_dates(current_date):
                return games_all
            else:
                games_all.append(d)

        if no_more_pages():
            return games_all
        else:
            page = next_page


def combine_games_into_server(server):
    dir_ = './data_backfill/partial/{}'.format(server)
    file_names = os.listdir(dir_)
    file_names = [x for x in file_names if not x.startswith(".")]

    data = []
    for file_name in file_names:
        file_path = '{}/{}'.format(dir_, file_name)
        with open(file_path, 'r') as f:
            g = json.loads(f.read())
        data.extend(g)

    with open('./data_backfill/{}.json'.format(server), 'w') as f:
        json.dump(data, f)

    print("{}: {} games".format(server, len(data)))


if __name__ == '__main__':
    servers = ['azeroth', 'northrend']
    for server in servers:
        dir_ = './data_backfill/partial/{}'.format(server)
        if not os.path.exists(dir_):
            os.makedirs(dir_)

        ladder_page = LadderPage(server)
        print(ladder_page)

        for row in ladder_page.rows:
            player = row.get('player')
            games = get_games(player, server)
            print("{} games found".format(len(games)))

            with open('{}/{}.json'.format(dir_, player), 'w') as f:
                json.dump(games, f, ensure_ascii=True)

        combine_games_into_server(server)
