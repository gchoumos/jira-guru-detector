"""
TODO:

- Check if the regular expressions can be written more efficiently. The e-mail one for
  example is quite slow.
- Extract tables? It could be fairly easy to extract them as most of them are actually
  lines that (after trimmed of whitespace) start and end with "|". However bear in mind
  that this kind of line starting/ending criterion only applies before removing the
  newlines. Actually I am more inclined to NOT extract them to be honest.
- I am currently dropping rows based on the comment column being NA. Maybe I should
  be dropping a row if ANY of the columns is NA and not only the "comment"
- extract_quotes and extract_noformats (and possibly more) can be merged into 1 function
  instead of separate ones. The specific case could be an argument and the regular
  expressions in an if/else clause (or even in settings)
- Regarding {quote}:
    * Broken quotes exist! For example {Quote} or {quote]. Maybe I can just fix those 2 particular cases.
      Actually only the first one is very common and it can be fixed if I convert all text to lower case
      first. The other one is way too uncommon.
    * We also have quotes with titles!! They look like {quote:title="blah blah blah"}
    * I wonder if it would make sense to remove any {quote} tags from the comments *after* extracting them
      to a separate column. If there are any left they are probably remnants of mistakes (for example
      3 {quote} tags in a single comment).
"""

import re
import string
import argparse
import os.path
import pandas as pd
from settings import *

import pdb

class DataPreprocessor(object):

    def __init__(self):
        print("Initializing DataPreprocessor ...")

        self.input_path = DP_SETTINGS['input_path']
        self.output_path = DP_SETTINGS['output_path']

        parser = argparse.ArgumentParser()
        parser.add_argument("--rebuild", help="rebuild datasets even if they already exist", action="store_true")
        self.args = parser.parse_args()

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

    def remove_multiple_spaces(self,colname='comment'):
        print("Removing multiple spaces from column '{0}' ...".format(colname))
        self.comments[[colname]] = self.comments[[colname]].replace(r'\s+',' ', regex=True)

    def remove_urls(self):
        print("Removing URLs ...")
        self.comments[['comment']] = self.comments[['comment']].replace(r'((https?:\/\/)|(www\.))[^ \n\r]*', '', regex=True)

    def remove_emails(self):
        print("Removing e-mails ...")
        self.comments[['comment']] = self.comments[['comment']].replace(r'[\w\.-]+@[\w\.-]+\.\w+', '', regex=True)

    def extract_quotes(self):
        print("Extracting text in {quote} tags. This will take some time ...")
        # Create the new column with the quotes as returned by findall (list of tuples)
        self.comments['quotes'] = self.comments[['comment'][0]].str.findall(r'(\{[Qq]uote.*?\}(.*?)\{[Qq]uote\})')
        # Iterate through the new column to keep only what we need from the tuples
        new_items = []
        for i, row in self.comments.iterrows():
            if i != 0 and i % 200000 == 0:
                print("Extracting quotes ... processed {0} rows".format(i))
            if row.quotes != []:
                cur_quotes = []
                for j, quote in enumerate(row.quotes):
                    # Create a list with all the matches (without the {quote} tags
                    # That is actually the second element of each tuple
                    cur_quotes.append(quote[1])
                # Join them in a single string
                new_items.append(' '.join(cur_quotes))
            else:
                new_items.append('')

        print("Extraction of quotes complete. Processed {0} rows".format(i))

        # Then set the new quotes to the quotes column and remove quote parts from the comments column
        self.comments['quotes'] = pd.Series(new_items).values
        self.comments[['comment']] = self.comments[['comment']].replace(r'(\{[Qq]uote.*?\}(.*?)\{[Qq]uote\})', '', regex=True)

    def extract_noformats(self):
        print("Extracting text in {noformat} tags. This will take some time ...")
        self.comments['noformats'] = self.comments[['comment'][0]].str.findall(r'(\{noformat.*?\}(.*?)\{noformat\})')
        new_items = []
        for i, row in self.comments.iterrows():
            if i != 0 and i % 200000 == 0:
                print("Extracting noformats ... processed {0} rows".format(i))
            if row.noformats != []:
                cur_noformats = []
                for j, noformat in enumerate(row.noformats):
                    cur_noformats.append(noformat[1])
                new_items.append(' '.join(cur_noformats))
            else:
                new_items.append('')

        print("Extraction of noformats complete. Processed {0} rows".format(i))
        # Remove noformat parts from the comments column
        self.comments['noformats'] = pd.Series(new_items).values
        self.comments[['comment']] = self.comments[['comment']].replace(r'(\{noformat.*?\}(.*?)\{noformat\})', '', regex=True)

    def extract_code(self):
        print("Extracting {code} tags. This will take some time ...")
        self.comments['code'] = self.comments[['comment'][0]].str.findall(r'(\{[Cc]ode.*?\}(.*?)\{[Cc]ode\})')
        new_items = []
        for i, row in self.comments.iterrows():
            if i != 0 and i % 200000 == 0:
                print("Extracting code ... processed {0} rows".format(i))
            if row.code != []:
                cur_code = []
                for j, code_block in enumerate(row.code):
                    cur_code.append(code_block[1])
                new_items.append(' '.join(cur_code))
            else:
                new_items.append('')

        print("Extraction of code complete. Processed {0} rows".format(i))

        # Remove code parts from the comments column
        self.comments['code'] = pd.Series(new_items).values
        self.comments[['comment']] = self.comments[['comment']].replace(r'(\{[Cc]ode.*?\}(.*?)\{[Cc]ode\})', '', regex=True)

    def extract_panels(self):
        # I am not sure if panels can include nested panels. I will assume no.
        print("Extracting {panel} tags. This will take some time ...")
        self.comments['panels'] = self.comments[['comment'][0]].str.findall(r'(\{[Pp]anel.*?\}(.*?)\{[Pp]anel\})')
        new_items = []
        for i, row in self.comments.iterrows():
            if i != 0 and i % 200000 == 0:
                print("Extracting panels ... processed {0} rows".format(i))
            if row.panels != []:
                cur_panel = []
                for j, panel in enumerate(row.panels):
                    cur_panel.append(panel[1])
                new_items.append(' '.join(cur_panel))
            else:
                new_items.append('')

        print("Extraction of panels complete. Processed {0} rows".format(i))

        # Remove panel parts from the comments column
        self.comments['panels'] = pd.Series(new_items).values
        self.comments[['comment']] = self.comments[['comment']].replace(r'(\{[Pp]anel.*?\}(.*?)\{[Pp]anel\})', '', regex=True)

    def fix_bad_tag_cases(self):
        # More will probably be added
        print("Fixing bad tag cases ...")
        self.comments[['comment']] = self.comments[['comment']].replace('{Noformat', '{noformat', regex=True)

    def remove_special_tags(self):
        print("Removing special tags ...")
        self.comments[['comment']] = self.comments[['comment']].replace(r'(\{[Cc]olor.*?\}(.*?)\{[Cc]olor\})', '', regex=True)

    def remove_punctuation(self, colname):
        print("Removing punctuation apart from dashes and underscores ...")
        print("   ~ column {0}".format(colname))
        # Remove punctuation except for dashes (-) and underscores(_)
        punct = '|'.join([re.escape(x) for x in string.punctuation.replace('-','').replace('_','')])

        new_items = []
        for i, row in self.comments.iterrows():
            if i != 0 and i % 200000 == 0:
                print("Removing punctuation ... processed {0} rows.".format(i))
            if len(row[colname]) > 0:
                new_items.append(re.sub(punct,' ',row[colname]))
            else:
                new_items.append('')

        self.comments[colname] = pd.Series(new_items).values

    def comments_to_csv(self):
        self.comments.to_csv('{0}/comments.csv'.format(self.output_path), index=False)

    def preprocess(self):
        if os.path.isfile("{0}/comments.csv".format(self.output_path)) and not self.args.rebuild:
            print("Preprocessed comments already exist. Run with --rebuild to rebuild anyway.")
            return

        self.load_comments()
        self.clean_comment_newlines()
        self.drop_na_comments()
        self.remove_urls()
        self.remove_emails()
        self.remove_multiple_spaces()
        self.fix_bad_tag_cases()
        self.remove_special_tags()
        self.extract_code()
        self.extract_quotes()
        self.extract_noformats()
        self.extract_panels()
        for column in ['comment', 'quotes', 'noformats', 'panels']:
            self.remove_punctuation(colname=column)
            # Now remove spaces again from each column
            self.remove_multiple_spaces(colname=column)

        # Write out the preprocessed comments file
        self.comments_to_csv()


preprocessor = DataPreprocessor()
preprocessor.preprocess()

"""
comments.csv (WIL-20000 to WIL-57199)


Original            - Size: 782056 KB - Lines: 12864079
No newlines         - Size: 709968 KB - Lines:   456201
No URLs             - Size: 698696 KB
No emails           - Size: 695204 KB
Quote separation    - Size: 
"""