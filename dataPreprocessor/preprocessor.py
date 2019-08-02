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
- Add logging
- It would probably make sense to remove multiple comments before separating columns. I guess it would
  decrease overall preprocess time a lot.
- Stemming is probably worth considering. There are tons of eligible cases.
- Looks like the comments_to_csv function is not necessary as it just make a single call. So maybe better to
  just make the call instead of triggering a new function to do this. Having a separate function would make
  more sense if there was more logic involved.
- I don't see any point having the check for the preprocessed files already existing and the --rebuild argument
  both in the preprocess and the selective_preprocess functions. We are repeating ourselves. This check should
  be made only once, before preprocess or selective_preprocess is called.
- Maybe I should consider removing the selective preprocess at some point completely.
- I am not sure if I should continue NOT replacing dashes. If we apply the same preprocess to the user input,
  then there is no point probably. Also, it looks like it's going to make the data clearer. Underscores should
  stay though.
"""

import re
import string
import argparse
import os.path
import spacy
import pandas as pd
from gensim.parsing.preprocessing import STOPWORDS
from settings import *

import pdb

class DataPreprocessor(object):

    def __init__(self):
        print("Initializing DataPreprocessor ...")

        self.input_path = DP_SETTINGS['input_path']
        self.output_path = DP_SETTINGS['output_path']
        self.input_file = DP_SETTINGS['input_file']
        self.output_file = DP_SETTINGS['output_file']
        self.stopwords = set(STOPWORDS)
        for x in WORDS_TO_IGNORE['2char']:
            self.stopwords.add(x)

        parser = argparse.ArgumentParser()
        parser.add_argument("--rebuild", help="rebuild datasets even if they already exist", action="store_true")
        parser.add_argument("--selective", help="prompt before each preprocess step", action="store_true")
        self.args = parser.parse_args()

    def load_comments(self):
        print("Loading Comments dataset ...")
        self.comments = pd.read_csv('{0}/{1}'
            .format(self.input_path,self.input_file), header=0)
        print("Loading finished - Dataset length is {0} rows".format(len(self.comments)))

    def clean_comment_newlines(self):
        # Replace carriage returns and newlines with space
        print("Removing newlines and carriage returns ...")
        self.comments[['comment']] = self.comments[['comment']].replace([r'\n',r'\r'],' ', regex=True)

    def drop_na_comments(self):
        # If any row doesn't have an actual comment in the "comment" column (N/A) drop it.
        print("Checking if NA comments exist ...")
        na_comms = self.comments['comment'].isna().sum()
        if na_comms > 0:
            print("Found! Dropping {0} NA comment rows ...".format(na_comms))
            self.comments = self.comments.dropna(subset=['comment'])
            # Reset the index as well so that we have no skipped values
            self.comments = self.comments.reset_index(drop=True)
            print("New length: {0}".format(len(self.comments)))
        else:
            print("No NA comments found")

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
                for quote in row.quotes:
                    # Create a list with all the matches (without the {quote} tags
                    # That is actually the second element of each tuple
                    cur_quotes.append(quote[1])
                # Join them in a single string
                new_items.append(' '.join(cur_quotes))
            else:
                new_items.append('')

        print("Quote extraction complete. Processed {0} rows".format(i))

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
                for noformat in row.noformats:
                    cur_noformats.append(noformat[1])
                new_items.append(' '.join(cur_noformats))
            else:
                new_items.append('')

        print("noformat extraction complete. Processed {0} rows".format(i))
        # Remove noformat parts from the comments column
        self.comments['noformats'] = pd.Series(new_items).values
        self.comments[['comment']] = self.comments[['comment']].replace(r'(\{noformat.*?\}(.*?)\{noformat\})', '', regex=True)

    def extract_code(self):
        print("Extracting code in {code} tags. This will take some time ...")
        self.comments['code'] = self.comments[['comment'][0]].str.findall(r'(\{[Cc]ode.*?\}(.*?)\{[Cc]ode\})')
        new_items = []
        for i, row in self.comments.iterrows():
            if i != 0 and i % 200000 == 0:
                print("Extracting code ... processed {0} rows".format(i))
            if row.code != []:
                cur_code = []
                for code_block in row.code:
                    cur_code.append(code_block[1])
                new_items.append(' '.join(cur_code))
            else:
                new_items.append('')

        print("Code extraction complete. Processed {0} rows".format(i))

        # Remove code parts from the comments column
        self.comments['code'] = pd.Series(new_items).values
        self.comments[['comment']] = self.comments[['comment']].replace(r'(\{[Cc]ode.*?\}(.*?)\{[Cc]ode\})', '', regex=True)

    def extract_panels(self):
        # I am not sure if panels can include nested panels. I will assume no.
        print("Extracting text in {panel} tags. This will take some time ...")
        self.comments['panels'] = self.comments[['comment'][0]].str.findall(r'(\{[Pp]anel.*?\}(.*?)\{[Pp]anel\})')
        new_items = []
        for i, row in self.comments.iterrows():
            if i != 0 and i % 200000 == 0:
                print("Extracting panels ... processed {0} rows".format(i))
            if row.panels != []:
                cur_panel = []
                for panel in row.panels:
                    cur_panel.append(panel[1])
                new_items.append(' '.join(cur_panel))
            else:
                new_items.append('')

        print("Panel extraction complete. Processed {0} rows".format(i))

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
        print("Removing punctuation from column {0} (apart from dashes and underscores) ...".format(colname))
        # Remove punctuation except for dashes (-) and underscores(_)
        punct = '|'.join([re.escape(x) for x in string.punctuation.replace('-','').replace('_','')])

        new_items = []
        for i, row in self.comments.iterrows():
            if i != 0 and i % 200000 == 0:
                print("Removing punctuation from {0} ... processed {1} rows".format(colname, i))
            if len(row[colname]) > 0:
                new_items.append(re.sub(punct,' ',row[colname]))
            else:
                new_items.append('')

        print("Punctuation removal complete. Processed {0} rows".format(i))
        self.comments[colname] = pd.Series(new_items).values

    def remove_digit_only_words(self, colname):
        print("Removing digit-only words from column {0} ...".format(colname))
        new_items = []
        for i, row in self.comments.iterrows():
            if i != 0 and i%200000 == 0:
                print("Removing digit-only words from {0} ... processed {1} rows".format(colname, i))
            words = row[colname].split()
            new_items.append(' '.join([word for word in words if not word.isdigit()]))
        print("Digit-only word removal complete. Processed {0} rows".format(i))
        self.comments[colname] = pd.Series(new_items).values

    def remove_small_words(self, colname, minlen):
        print("Removing small words (len < {0}) from column {1} ...".format(minlen, colname))
        new_items = []
        for i, row in self.comments.iterrows():
            if i != 0 and i%200000 == 0:
                print("Removing small words (len < {0}) from {1} ... processed {2} rows".format(minlen, colname, i))
            words = row[colname].split()
            new_items.append(' '.join([word for word in words if len(word) >= minlen]))
        print("Small word removal complete. Processed {0} rows".format(i))
        self.comments[colname] = pd.Series(new_items).values

    def convert_to_lowercase(self, colname):
        print("Converting column '{0}' to lowercase ...".format(colname))
        self.comments[colname] = self.comments[colname].str.lower()

    def remove_stopwords(self, colname):
        print("Removing stopwords from column {0} ...".format(colname))
        new_items = []
        for i, row in self.comments.iterrows():
            if i != 0 and i%200000 == 0:
                print("Removing stopwords from {0} ... processed {1} rows".format(colname, i))
            words = row[colname].split()
            new_items.append(' '.join([word for word in words if word not in self.stopwords]))
        print("Stopwords removal complete. Processed {0} rows".format(i))
        self.comments[colname] = pd.Series(new_items).values

    def lemmatize(self, colname):
        print("Lemmatizing column {0} ...".format(colname))
        new_items = []
        for i, row in self.comments.iterrows():
            if i != 0 and i%200000 == 0:
                print("Lemmatizing {0} ... processed {1} rows".format(colname, i))
            if len(row[colname]) > 0:
                lemmata = self.lemmatizer(row[colname]) # This and next could be one row but it's easier to read
                new_items.append(' '.join([x.lemma_ for x in lemmata]))
            else:
                new_items.append('')
        print("Lemmatization of {0} complete. Processed {1} rows".format(colname,i))
        self.comments[colname] = pd.Series(new_items).values

    def get_proper_answer(self,text="Please respond (y,n): "):
            answer = input(text).lower().strip()
            while answer not in ['y', 'n']:
                print("Please enter a valid answer (y or n)")
                answer = input(text).lower().strip()
            if answer == 'y':
                return True
            else:
                return False

    """ Save comments to a CSV file with the selected columns. Save all columns if none is specified. """
    def comments_to_csv(self, columns=[]):
        if len(columns) == 0:
            self.comments.to_csv('{0}/{1}'
                .format(self.output_path,self.output_file), index=False)
        else:
            self.comments.to_csv('{0}/{1}_only.csv'
                .format(self.output_path,'-'.join(columns)),columns=columns, index=False)

    def selective_preprocess(self):
        if os.path.isfile("{0}/{1}".format(self.output_path,self.output_file)) and not self.args.rebuild:
            print("Preprocessed comments already exist. Run with --rebuild to rebuild anyway.")
            return

        self.load_comments()
        self.clean_comment_newlines()
        self.drop_na_comments()

        p_url = self.get_proper_answer("Remove urls? (y,n): ")
        p_email = self.get_proper_answer("Remove emails? (y,n): ")
        p_spaces = self.get_proper_answer("Remove multiple spaces? (y,n): ")
        p_fixtags = self.get_proper_answer("Fix bad tag cases? (y,n): ")
        p_specialtags = self.get_proper_answer("Remove special tags? (y,n): ")
        p_code = self.get_proper_answer("Extract code? (y,n): ")
        p_quotes = self.get_proper_answer("Extract quotes? (y,n): ")
        p_noformats = self.get_proper_answer("Extract noformats? (y,n): ")
        p_panels = self.get_proper_answer("Extract panels? (y,n): ")
        p_punct = self.get_proper_answer("Remove punctuation? (y.n): ")
        p_digits = self.get_proper_answer("Remove digit-only words? (y,n): ")
        p_small = self.get_proper_answer("Remove small words? (y,n): ")
        p_lower = self.get_proper_answer("Convert to lowercase? (y,n): ")
        p_stop = self.get_proper_answer("Remove stopwords? (y,n): ")
        p_lemma = self.get_proper_answer("Apply lemmatization in comments? (y,n): ")

        self.remove_urls() if p_url else {}
        self.remove_emails() if p_email else {}
        self.remove_multiple_spaces() if p_spaces else {}
        self.fix_bad_tag_cases() if p_fixtags else {}
        self.remove_special_tags() if p_specialtags else {}
        self.extract_code() if p_code else {}
        self.extract_quotes() if p_quotes else {}
        self.extract_noformats() if p_noformats else {}
        self.extract_panels() if p_panels else {}
        for column in ['comment', 'quotes', 'noformats', 'panels']:
            self.remove_punctuation(colname=column) if p_punct else {}
            # Now remove spaces again from each column
            self.remove_multiple_spaces(colname=column) if p_spaces else {}

        for column in ['comment', 'quotes', 'noformats', 'panels', 'code']:
            self.remove_digit_only_words(colname=column) if p_digits else {}
            self.remove_small_words(colname=column, minlen=2) if p_small else {}
            self.convert_to_lowercase(colname=column) if p_lower else {}
            self.remove_stopwords(colname=column) if p_stop else {}

        if p_lemma == True:
            self.lemmatizer = spacy.load('en')
            self.lemmatize(colname='comment')
            # Write out comment column only for inspection
            self.comments_to_csv(['comment'])

        # Write out the preprocessed comments file
        self.comments_to_csv()


    def preprocess(self):
        if os.path.isfile("{0}/{1}"
            .format(self.output_path,self.output_file)) and not self.args.rebuild:
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
            # Now remove spaces again from each column - Could we avoid having to do this again?
            self.remove_multiple_spaces(colname=column)

        for column in ['comment', 'quotes', 'noformats', 'panels', 'code']:
            self.remove_digit_only_words(colname=column)
            self.remove_small_words(colname=column, minlen=2)
            self.convert_to_lowercase(colname=column)
            self.remove_stopwords(colname=column)

        # Initialize lemmatizer and apply lemmatization to the comments.
        # (would be good to do this for panels and quotes maybe)
        # self.lemmatizer = spacy.load('en')
        # self.lemmatize(colname='comment')

        # Write out the preprocessed comments file
        self.comments_to_csv()

        # Write out comment column only for inspection
        self.comments_to_csv(['comment'])


preprocessor = DataPreprocessor()
if preprocessor.args.selective:
    preprocessor.selective_preprocess()
else:
    preprocessor.preprocess()
