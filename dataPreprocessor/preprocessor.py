"""
TODO:

- Check if the regular expressions can be written more efficiently. The e-mail one for
  example is quite slow.
- I am currently dropping rows based on the comment column being NA. Maybe I should
  be dropping a row if ANY of the columns is NA and not only the "comment"
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

    def drop_na_comments(self):
        # If any row doesn't have an actual comment in the "comment" column (N/A) drop it.
        print("Checking if NA comments exist ...")
        print("Dataset length: {0}".format(len(self.comments)))
        na_comms = self.comments['comment'].isna().sum()
        if na_comms > 0:
            print("Found! Dropping {0} NA comment rows ...".format(na_comms))
            self.comments = self.comments.dropna(subset=['comment'])
            # Reset the index as well so that we have no skipped values
            self.comments = self.comments.reset_index(drop=True)
            print("New length: {0}".format(len(self.comments)))

    def remove_multiple_spaces(self):
        print("Removing multiple spaces ...")
        self.comments[['comment']] = self.comments[['comment']].replace(r'\s+',' ', regex=True)

    def remove_urls(self):
        print("Removing URLs ...")
        self.comments[['comment']] = self.comments[['comment']].replace(r'((https?:\/\/)|(www\.))[^ \n\r]*', '', regex=True)

    def remove_emails(self):
        print("Removing e-mails ...")
        self.comments[['comment']] = self.comments[['comment']].replace(r'[\w\.-]+@[\w\.-]+\.\w+', '', regex=True)

    def extract_quotes(self):
        print("Extracting text in {quote} tags. This will take some time ...")
        # Create the new column with the quotes as returned by findall (list of tuples)
        self.comments['quotes'] = self.comments[['comment'][0]].str.findall(r'(\{quote\}(.*?)\{quote\})')
        # Iterate through the new column to keep only what we need from the tuples
        for i in range(len(self.comments)):
            if i % 2000 == 0:
                print("... processed {0} rows".format(i))
            if self.comments['quotes'][i] != []:
                cur_quotes = []
                for j in range(len(self.comments['quotes'][i])):
                    # Create a list with all the matches (without the {quote} tags
                    # That is actually the second element of each tuple
                    cur_quotes.append(self.comments['quotes'][i][j][1])
                # Join them in a single string
                self.comments['quotes'].loc[i] = ' '.join(cur_quotes)
            else:
                self.comments['quotes'].loc[i] = ''

        # Then remove quote parts from the comments column
        self.comments[['comment']] = self.comments[['comment']].replace(r'(\{quote\}(.*?)\{quote\})', '', regex=True)

    def comments_to_csv(self):
        self.comments.to_csv('{0}/comments.csv'.format(self.output_path))


preprocessor = DataPreprocessor()
preprocessor.load_comments()
preprocessor.clean_comment_newlines()
preprocessor.drop_na_comments()
preprocessor.remove_urls()
preprocessor.remove_emails()
preprocessor.remove_multiple_spaces()
preprocessor.extract_quotes()

# Write out the cleaner comments file
preprocessor.comments_to_csv()


"""
comments.csv (WIL-20000 to WIL-57199)


Original    - Size: 782056 KB - Lines: 12864079
No newlines - Size: 709968 KB - Lines:   456201
No URLs     - Size: 698696 KB
No emails   - Size: 695204 KB
"""