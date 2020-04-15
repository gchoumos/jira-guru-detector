# This is an issue that needs to be taken into consideration with regards to Cross Validation
# https://github.com/scikit-learn/scikit-learn/issues/11777
# In multiclass problems with classes being so many this is a common case, so we may want to
# consider excluding some labels (and their comments) from the cross validation process.

# Tested and works fine with scikit learn versions 0.19.1 and 0.21.3

import re
import pickle
import pandas as pd
import numpy as np

from settings import *

from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.feature_selection import SelectFromModel
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import log_loss, make_scorer

from feature_union_sklearn import (
                            ItemSelector,
                            MainExtractor
                        )

# Tool to decide if author belongs to the ignored group
def ignored(author):
    return True in [bool(re.match(x, author)) for x in IGNORE_AUTHOR_GROUPS]

# Tool to decide if author belongs to the current team active users
def current_team_member(author):
    return author in ACTIVE_USERS[TEAM].keys()

# Read our csv
data = pd.read_csv('{0}/{1}'.format(INPUT_PATH,INPUT_FILE))

# Keep only data from users that are still active
if ACTIVE_ONLY == True:
    rows_before = data.shape[0]
    data = data[data.active == True]
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
    print("CONFIG: Dropped {0} comments by ignored Author groups."
            .format(rows_before-data.shape[0]))

# Only include comments that are coming from currently active team members
if CURRENT_ONLY:
    rows_before = data.shape[0]
    data = data[data.apply(lambda row: current_team_member(row.author), axis=1) == True]
    print("CONFIG: Dropped {0} comments by authors NOT currently in {0} team.".format(TEAM)
            .format(rows_before-data.shape[0]))

# Find authors will less comments than the configured appearance threshold
if APPEARANCE_THRESHOLD > 0:
    all_authors = list(data[data.comment.notnull()]['author'].unique())
    author_freqs = data.groupby('author').comment.nunique().sort_values()
    rejection_list = author_freqs >= APPEARANCE_THRESHOLD
    rare_authors = [x for x in rejection_list.index if rejection_list[x] == False]
    rows_before = data.shape[0]
    data = data[data.apply(lambda row: row.author not in rare_authors, axis =1) == True]
    print("CONFIG: Dropped {0} comments by rare Authors (less than {1} comments)."
            .format(rows_before-data.shape[0],APPEARANCE_THRESHOLD))

# Index has many holes now, maybe a good idea to reset it
data.reset_index(drop=True, inplace=True)

# Get the comments as a feature by dropping the na rows
tr_comments = data[data.comment.notnull()]['comment']

training = np.dstack([
    tr_comments,
])
training = training[:][0]

# Get the labels. In our case, they are persons.
tr_labels = data[data.comment.notnull()]['author']


# The logistic regression for comments
# multi_class to 'auto' instead of the default 'ovr' improved the fit (probably because 'auto` eventually 'selects `multinomial`)
logr_comments = LogisticRegression(penalty='l2', tol=1e-05, multi_class='auto')

thres_all = None
pipeline = Pipeline([
    ('main_extractor', MainExtractor()),

    # Use FeatureUnion to combine the features
    ('union', FeatureUnion(
        transformer_list=[
            # Comment unigrams
            ('comment_unigrams', Pipeline([
                ('selector', ItemSelector(key='comment')),
                ('vect', CountVectorizer(decode_error='ignore', stop_words='english', max_df=0.5, min_df=0.00001,ngram_range=(1,1))),
                ('tfidf', TfidfTransformer(norm='l2',sublinear_tf=True)),
                ('sfm_comm_uni', SelectFromModel(logr_comments,threshold=thres_all)),
            ])),

            # Comment bigrams
            ('comment_bigrams', Pipeline([
                ('selector', ItemSelector(key='comment')),
                ('vect', CountVectorizer(decode_error='ignore', stop_words='english', max_df=0.6, min_df=0.001,ngram_range=(2,2))),
                ('tfidf', TfidfTransformer(norm='l2',sublinear_tf=True)),
                ('sfm_comm_bi', SelectFromModel(logr_comments,threshold=thres_all)),
            ])),

            # ('comment_trigrams', Pipeline([
            #     ('selector', ItemSelector(key='comment')),
            #     ('vect', CountVectorizer(decode_error='ignore', stop_words='english', max_df=0.6, min_df=0.0001,ngram_range=(3,3))),
            #     ('tfidf', TfidfTransformer(norm='l2',sublinear_tf=True)),
            #     ('sfm_comm_tri', SelectFromModel(logr_comments,threshold=thres_all)),
            # ])),
        ],

        # Weight components in FeatureUnion - Here are the optimals
        transformer_weights={ # Best combination till now - 1.504
            'comment_unigrams': 1.40, # 1.40
            'comment_bigrams':  1.00, # 0.90 # 1.00
            # 'comment_trigrams': 1.00, # 1.00
        },
    )),

    ('logr', LogisticRegression(penalty='l2', tol=0.0001, multi_class='auto')),
])

parameters = {}

# The default scorer is the accuracy, but we want the log loss in our case.
log_loss_scorer = make_scorer(log_loss, greater_is_better=False, needs_proba=True)

grid_search = GridSearchCV(pipeline, parameters, cv=3, n_jobs=-1, verbose=10, scoring=log_loss_scorer)
grid_search.fit(training,tr_labels)

# Display the (best) score of the model.
print("Best score: %0.3f" % grid_search.best_score_)

# Save the model to a file
pickle.dump(grid_search,open('{0}_{1:.3f}.save'.format(TEAM,abs(grid_search.best_score_)),'wb'))
