import dateparser

data_positions_profile = {
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
            'function': lambda x: int(x.split('\t')[-1])
        },
        'partners':
        {
            'position': 3,
            'function': None
        },
        'rank':
        {
            'position': 4,
            'function': lambda x: x if x == 'Unranked' else 'Rank {}'.format(int(x[:-2]))
        },
        'experience': None
    },
    'individual':
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
            'function': lambda x: int(x.split('\t')[-1])
        },
        'partners': None,
        'rank':
        {
            'position': 3,
            'function': lambda x: x if x == 'Unranked' else 'Rank {}'.format(int(x[:-2]))
        },
        'experience':
        {
            'position': 2,
            'function': lambda x: int(x.replace(',', ''))
        }
    }
}


data_positions_history = {
    'date': {
        'position': 1,
        'function': lambda x: str(dateparser.parse(x).strftime("%Y-%m-%d %H:%M:%S"))
    },
    'game_type': {
        'position': 2,
        'function': lambda x: x.strip()
    },
    'map': {
        'position': 3,
        'function': lambda x: x.strip()
    },
    'team_one': {
        'position': 6,
        'function': lambda x: [] if x is '' else x.strip().split(',')
    },
    'team_two': {
        'position': 8,
        'function': lambda x: [] if x is '' else x.strip().split(',')
    },
    'game_length': {
        'position': 9,
        'function': lambda x: int(x.strip())
    },
    'winner': {
        'position': 10,
        'function': lambda x: x.strip()
    }
}

emoji_dict = {
    'Human': 'grubHU',
    'Orc': 'grubORC',
    'Night Elf': 'grubNE',
    'Undead': 'grubUD'
}
