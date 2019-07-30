# Source of data - They are considered to be already preprocessed
INPUT_PATH = '/home/gchoumo/Documents/jira-guru-detector/datasets/preprocessed'
INPUT_FILE = 'comments.csv'

# Consider only users that are still active in Jira. Default = True
ACTIVE_ONLY = True

# Columns that we don't want for training so can be dropped
UNUSED_COLUMNS = [
    'key',
    'created',
    'code',
    'quotes',
    'noformats',
    'panels',
]

IGNORE_AUTHOR_GROUPS = []

# Redacted settings
try:
    from redacted import IGNORE_AUTHOR_GROUPS
except ImportError:
    print("No valid redacted settings found.")