# Source of data - They are considered to be already preprocessed
INPUT_PATH = '/home/gchoumo/Documents/jira-guru-detector/datasets/preprocessed'
INPUT_FILE = 'combined.csv'

# Consider only users that are still active in Jira. Default = True
ACTIVE_ONLY = True

# Consider only users that are currently members of WH team
CURRENT_WH_ONLY = True

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
    from redacted import IGNORE_AUTHOR_GROUPS, WIL_USERS_ACTIVE
except ImportError:
    print("No valid redacted settings found.")