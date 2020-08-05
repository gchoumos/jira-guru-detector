""" Dataloader settings """
SETTINGS = {
    'jiraPrj': ['WIL'],
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

# Will take value by the redacted settings. For now assign dummy values to expose the structure.
ACTIVE_USERS = {
    'TEAM1': {
        'username1': 'Full Name1',
        'username2': 'Full Name2',
    },
    'TEAM2': {
        'username3': 'Full Name3',
        'username4': 'Full Name4',
    }
}


# Holds the Jira batches with boundaries that do exist. That's because if any
# boundary does not exist, search with JQL against issuekey (or id) fails!
# If there is another way to elegantly avoid this, then do so. To be clear
# on this, it's not something that I haven't thought of, it's because of
# a Jira Server **BUG**. I won't be doing funny hacks in the code just to
# make this work by overcoming the Jira Server bugs. This should  be fixed
# by Atlassian.
#
# They are to be taken in pairs (from - to)
#
# It will be overriden by the redacted settings. For now assign dummy values to expose the structure.
BATCH_INTERVALS = {
    'TEAM1': [
           1,  199,  200,  399,  400,  599,  600,  799,  800,  999,
        1000, 1199, 1200, 1399, 1400, 1599, 1600, 1799, 1800, 1999,
    ],
    'TEAM2': [
           1,  199,  200,  399,  400,  599,  600,  799,  800,  999,
        1000, 1199, 1200, 1399, 1400, 1599, 1600, 1799, 1800, 1999,
        2000, 2199, 2200, 2399, 2400, 2499, 2500, 2799, 2800, 2999,
    ],
}

try:
    from redacted import *
except ImportError:
    print("No valid redacted settings found.")
