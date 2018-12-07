from history_page import HistoryPage
from profile_page import ProfilePage


if __name__ == '__main__':
    players = [
        {'player': 'Rellik', 'server': 'northrend'}
    ]

    print('-- Testing --')
    for player in players:
        page = 1
        data_all = []

        while True:
                history_page = HistoryPage(player.get('player'), player.get('server'), page)
                print(history_page)
                data = list(history_page.games)
                data_all.extend(data)
                next_page = history_page.next_page
                if page >= next_page:
                        break
                page = next_page

        df = pd.DataFrame(data_all)
        print(df.shape)
        print(df.head(3))

    data = df.to_dict(orient='records')
    print(data)
    with open('./data_backfill/{}.json'.format(player.get('player')), 'w') as f:
        json.dump(data, f)
