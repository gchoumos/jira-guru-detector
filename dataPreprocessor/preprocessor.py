
import re
import pandas as pd
from settings import *

import pdb

class DataPreprocessor(object):

    def __init__(self):
        print("Initializing DataPreprocessor...")

        self.input_path = DP_SETTINGS['input_path']
        self.output_path = DP_SETTINGS['output_path']

    def load_comments(self):
        self.comments = pd.read_csv('{0}/comments.csv'.format(self.input_path), header=0)

    def clean_comment_newlines(self):
        # Replace carriage returns and newlines with space
        self.comments.replace([r'\n',r'\r'],' ', regex=True, inplace=True)

    def single_spaces_comments(self):
        self.comments.replace(r'\s+',' ', regex=True, inplace=True)

    def comments_to_csv(self):
        self.comments.to_csv('{0}/comments.csv'.format(self.output_path))


preprocessor = DataPreprocessor()
preprocessor.load_comments()
preprocessor.clean_comment_newlines()
preprocessor.single_spaces_comments()

# Write out the cleaner comments file
preprocessor.comments_to_csv()