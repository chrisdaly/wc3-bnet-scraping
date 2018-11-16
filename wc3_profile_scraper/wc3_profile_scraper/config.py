data_positions = {
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
