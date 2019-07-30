import re
import pandas as pd

from settings import *

# Tool to decide if author belongs to the ignored group
def ignored(author):
    return True in [bool(re.match(x, author)) for x in IGNORE_AUTHOR_GROUPS]

# Read our csv
data = pd.read_csv('{0}/{1}'.format(INPUT_PATH,INPUT_FILE))

# Keep only data from users that are still active
if ACTIVE_ONLY == True:
    rows_before = data.shape[0]
    data = data[data.active == 'True']
    print("CONFIG: Keeping only data from active accounts. {0} rows have been removed."
            .format(rows_before-data.shape[0]))

# The active column is not useful now so we can drop it
data.drop(['active'], axis=1, inplace=True)

# Drop any other columns that will not be used
if len(UNUSED_COLUMNS) > 0:
    data.drop(UNUSED_COLUMNS, axis=1, inplace=True)
    print("CONFIG: Dropped the following columns: {0}".format(UNUSED_COLUMNS))

# Ignore comments of author groups that should be ignored (non-OB for the moment)
if len(IGNORE_AUTHOR_GROUPS) > 0:
    rows_before = data.shape[0]
    data = data[data.apply(lambda row: ignored(row.author), axis=1) == False]
    print("CONFIG: Dropped {0} comments by ignored Author groups:"
            .format(rows_before-data.shape[0]))

# Index has many holes now, maybe a good idea to reset it
data.reset_index(drop=True, inplace=True)

