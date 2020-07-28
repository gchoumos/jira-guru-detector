# The team that we will be running this for
TEAM = 'WIL'

# Source of data - They are considered to be already preprocessed
INPUT_PATH = '/home/gchoumo/Documents/jira-guru-detector/datasets/preprocessed_{0}'.format(TEAM)
INPUT_FILE = 'combined_{0}.csv'.format(TEAM)

# Consider only users that are still active in Jira. Default = True
ACTIVE_ONLY = True

# Consider only users that are *currently* members of team
CURRENT_ONLY = True

# Columns that we don't want for training so can be dropped
UNUSED_COLUMNS = [
    'key',
    'created',
    'issuetype',
    'code',
    'quotes',
    'noformats',
    'panels',
]

IGNORE_AUTHOR_GROUPS = []

APPEARANCE_THRESHOLD = 3

# Redacted settings
try:
    from redacted import ACTIVE_USERS
except ImportError:
    print("No valid redacted settings found.")