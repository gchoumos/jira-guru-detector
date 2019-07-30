# Author: Matt Terry <matt.terry@gmail.com>
#
# License: BSD 3 clause
#
# This is a modified version by George Choumos <g.choumos@gmail.com>

from sklearn.base import BaseEstimator, TransformerMixin
import numpy as np

class ItemSelector(BaseEstimator, TransformerMixin):
    def __init__(self, key):
        self.key = key

    def fit(self, x, y=None):
        return self

    def transform(self, data_dict):
        return data_dict[self.key]

class MainExtractor(BaseEstimator, TransformerMixin):
    def fit(self, x, y=None):
        return self

    def transform(self, lines):
        features = np.recarray(
                    shape=(len(lines),),
                        dtype=[
                                ('comment', object),
							  ])
        for i, line in enumerate(lines):
            comment = line[0]

            features['comment'][i] = comment if comment==comment else ''

        # print("Features shape is {0}".format(features.shape))
        # print("{0}".format(features[0]))
        return features
