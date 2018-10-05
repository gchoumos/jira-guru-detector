"""
TODO:

- Check if the regular expressions can be written more efficiently. The e-mail one for
  example is quite slow.
"""


import re
import pandas as pd
from settings import *

import pdb

class DataPreprocessor(object):

    def __init__(self):
        print("Initializing DataPreprocessor ...")

        self.input_path = DP_SETTINGS['input_path']
        self.output_path = DP_SETTINGS['output_path']

    def load_comments(self):
        print("Loading Comments dataset ...")
        self.comments = pd.read_csv('{0}/comments.csv'.format(self.input_path), header=0)

    def clean_comment_newlines(self):
        # Replace carriage returns and newlines with space
        print("Removing newlines and carriage returns ...")
        self.comments[['comment']] = self.comments[['comment']].replace([r'\n',r'\r'],' ', regex=True)

    def remove_multiple_spaces(self):
        print("Removing multiple spaces ...")
        self.comments[['comment']] = self.comments[['comment']].replace(r'\s+',' ', regex=True)

    def remove_urls(self):
        print("Removing URLs ...")
        self.comments[['comment']] = self.comments[['comment']].replace(r'((https?:\/\/)|(www\.))[^ \n\r]*', '', regex=True)

    def remove_emails(self):
        print("Removing e-mails ...")
        self.comments[['comment']] = self.comments[['comment']].replace(r'[\w\.-]+@[\w\.-]+\.\w+', '', regex=True)

    # def extract_quotes(self):
    #     print("Extracting text in {quote} tags ...")
    #     # Create first the new column with the quote contents from comments



    def comments_to_csv(self):
        self.comments.to_csv('{0}/comments.csv'.format(self.output_path))


preprocessor = DataPreprocessor()
preprocessor.load_comments()
preprocessor.clean_comment_newlines()
preprocessor.remove_urls()
preprocessor.remove_emails()
preprocessor.remove_multiple_spaces()

# Write out the cleaner comments file
preprocessor.comments_to_csv()


"""
comments.csv (WIL-20000 to WIL-57199)


Original    - Size: 782056 KB - Lines: 12864079
No newlines - Size: 709968 KB - Lines:   456201
No URLs     - Size: 698696 KB
No emails   - Size: 695204 KB

"""