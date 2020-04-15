""" Dataloader settings """
SETTINGS = {
    'jiraPrj': 'WIL',
    'options': {
        'server': 'https://jira.openbet.com',
    },
    'maxResults': 200, # (defaults to 50)
    'fields': [
        'key',
        'summary',
        'assignee',
        'created',
        'issuetype',
        'description',
        'comment',
        'labels',
        'creator',
    ],
    'summaries_fields': [
        'key',
        'summary',
        'creator',
        'created',
    ],
    'output_path': '/home/gchoumo/Documents/jira-guru-detector/datasets',
}

# Will take value by the redacted settings
"""
    # dict of dicts
    {
        'TEAM1': {
            'username1': 'Full Name1',
            'username2': 'Full Name2',
        },
        'TEAM2': {
            'username3': 'Full Name3',
            'username4': 'Full Name4',
        }
    }
"""
ACTIVE_USERS = {}

# It will be populated by the redacted settings (see end of file)
"""
    # dict of lists
    # The below will translate to tickets TEAM-1 to TEAM-199, then TEAM-200 to TEAM-399 etc.
    {
        'TEAM1': [
            1, 199, 200, 399, 400, 599
        ]
    }
"""
BATCH_INTERVALS = {}

try:
    from redacted import *
except ImportError:
    print("No valid redacted settings found.")
