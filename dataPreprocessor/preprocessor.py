"""
TODO:

- Check if the regular expressions can be written more efficiently. The e-mail one for
  example is quite slow.
- Extract tables? It could be fairly easy to extract them as most of them are actually
  lines that (after trimmed of whitespace) start and end with "|". However bear in mind
  that this kind of line starting/ending criterion only applies before removing the
  newlines. Actually I am more inclined to NOT extract them to be honest.
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
- I don't see any point having the check for the preprocessed files already existing and the --rebuild argument
  both in the preprocess and the selective_preprocess functions. We are repeating ourselves. This check should
  be made only once, before preprocess or selective_preprocess is called.
---- Maybe I should consider removing the selective preprocess at some point completely.
- I am not sure if I should continue NOT replacing dashes. If we apply the same preprocess to the user input,
  then there is no point probably. Also, it looks like it's going to make the data clearer. Underscores should
  stay though (or should be MERGED - so app_name should become appname and not "app name").
- Would make more sense to convert to lowercase as soon as possible. And then this will mean that I will be
  able to also update some of the regular expressions accordingly.
- I strongly believe that I should only preprocess the comments coming from Active authors, otherwise we'll
  end up preprocessing a massive amount of data that will never be used. This problem is going to get worse
  and worse as time passes.
- If I stay with ignoring inactive, then more changes are needed because parts of the functionality have
  become redundant. Search for "active" and it will become obvious.
"""

import re
import string
import argparse
import os
import spacy
import pandas as pd
from gensim.parsing.preprocessing import STOPWORDS
from collections import defaultdict
from csv import DictWriter
from settings import *

import pdb

class DataPreprocessor(object):

    def __init__(self):
        print("Initializing DataPreprocessor ...")

        self.input_path = DP_SETTINGS['input_path']
        self.output_path = DP_SETTINGS['output_path']
        self.comms_input_file = DP_SETTINGS['comms_input_file']
        self.comms_output_file = DP_SETTINGS['comms_output_file']
        self.summs_input_file = DP_SETTINGS['summs_input_file']
        self.summs_output_file = DP_SETTINGS['summs_output_file']
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
            .format(self.input_path,self.comms_input_file), header=0)
        print("Loading finished - Comments Dataset length is {0} rows".format(len(self.comments)))



    def load_summaries(self):
        print("Loading Summaries dataset ...")
        self.summaries = pd.read_csv('{0}/{1}'
            .format(self.input_path,self.summs_input_file), header=0)
        print("Loading finished - Summaries Dataset length is {0} rows".format(len(self.summaries)))



    def ignore_inactive_user_comments(self):
        rows_before = self.comments.shape[0]
        self.comments = self.comments[self.comments.active == 'True']
        print("CONFIG: Keeping only comments from active accounts. {0} rows have been removed."
                .format(rows_before-self.comments.shape[0]))




    def clean_newlines(self, dataset='comments', colname='comment'):
        # Replace carriage returns and newlines with space
        print("Removing newlines and carriage returns. Dataset: {0}, Column: {1} ...".format(dataset,colname))
        if dataset == 'comments':
            self.comments[[colname]] = self.comments[[colname]].replace([r'\n',r'\r'],' ', regex=True)
        elif dataset == 'summaries':
            self.summaries[[colname]] = self.summaries[[colname]].replace([r'\n',r'\r'],' ', regex=True)



    def drop_na(self, dataset='comments', colname='comment'):
        # If any row doesn't have value for the column (so it's N/A), then drop it.
        print("Checking if NAs exist. Dataset: {0}, Column: {1} ...".format(dataset,colname))
        if dataset == 'comments':
            na_num = self.comments[colname].isna().sum()
        elif dataset == 'summaries':
            na_num = self.summaries[colname].isna().sum()
        if na_num > 0:
            print("Found! Dropping {0} rows with NA values for column: {1}...".format(na_num,colname))
            if dataset == 'comments':
                self.comments = self.comments.dropna(subset=[colname])
                # Reset the index as well so that we have no skipped values
                self.comments = self.comments.reset_index(drop=True)
                print("New length: {0}".format(len(self.comments)))
            elif dataset == 'summaries':
                self.summaries = self.summaries.dropna(subset=[colname])
                self.summaries = self.summaries.reset_index(drop=True)
        else:
            print("No NAs found")



    def remove_multiple_spaces(self, dataset='comments', colname='comment'):
        print("Removing multiple spaces. Dataset: {0}, Column: {1} ...".format(dataset,colname))
        if dataset == 'comments':
            self.comments[[colname]] = self.comments[[colname]].replace(r'\s+',' ', regex=True)
        elif dataset == 'summaries':
            self.summaries[[colname]] = self.summaries[[colname]].replace(r'\s+',' ', regex=True)



    def remove_urls(self, dataset='comments', colname='comment'):
        # If clean newlines has already been called, there is no need to check for '\n\r' at the end of the regex
        print("Removing URLs. Dataset: {0}, Column: {1} ...".format(dataset,colname))
        if dataset == 'comments':
            self.comments[[colname]] = self.comments[[colname]].replace(r'((https?:\/\/)|(www\.))[^\s]*', '', regex=True)
        elif dataset == 'summaries':
            self.summaries[[colname]] = self.summaries[[colname]].replace(r'((https?:\/\/)|(www\.))[^\s]*', '', regex=True)



    def remove_emails(self, dataset='comments', colname='comment'):
        print("Removing e-mails. Dataset: {0}, Column: {1} ...".format(dataset,colname))
        if dataset == 'comments':
            self.comments[[colname]] = self.comments[[colname]].replace(r'[\w\.-]+@[\w\.-]+\.\w+', '', regex=True)
        elif dataset == 'summaries':
            self.summaries[[colname]] = self.summaries[[colname]].replace(r'[\w\.-]+@[\w\.-]+\.\w+', '', regex=True)



    def extract_quotes(self, dataset='comments', colname='comment'):
        print("Extracting text in {{quote}} tags. Dataset {0}, Column: {1}. This may take some time ...".format(dataset,colname))
        new_items = []
        # Create the new column with the quotes as returned by findall (list of tuples)
        if dataset == 'comments':
            self.comments['quotes'] = self.comments[[colname][0]].str.findall(r'(\{[Qq]uote.*?\}(.*?)\{[Qq]uote\})')
            loop = self.comments.iterrows()
        elif dataset == 'summaries':
            self.summaries['quotes'] = self.summaries[[colname][0]].str.findall(r'(\{[Qq]uote.*?\}(.*?)\{[Qq]uote\})')
            loop = self.summaries.iterrows()
        # Iterate through the new column to keep only what we need from the tuples
        for i, row in loop:
            if i != 0 and i % 200000 == 0:
                print("Extracting quotes ... processed {0} rows".format(i))
            if isinstance(row.quotes,list) and row.quotes != []:
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
        # Then set the new quotes to the quotes column and remove quote parts from the given column
        if dataset == 'comments':
            self.comments['quotes'] = pd.Series(new_items).values
            self.comments[[colname]] = self.comments[[colname]].replace(r'(\{[Qq]uote.*?\}(.*?)\{[Qq]uote\})', '', regex=True)
        elif dataset == 'summaries':
            self.summaries['quotes'] = pd.Series(new_items).values
            self.summaries[[colname]] = self.summaries[[colname]].replace(r'(\{[Qq]uote.*?\}(.*?)\{[Qq]uote\})', '', regex=True)



    def extract_noformats(self, dataset='comments', colname='comment'):
        print("Extracting text in {{noformat}} tags. Dataset: {0}, Column: {1}. This may take some time ...".format(dataset,colname))
        new_items = []
        if dataset == 'comments':
            self.comments['noformats'] = self.comments[[colname][0]].str.findall(r'(\{noformat.*?\}(.*?)\{noformat\})')
            loop = self.comments.iterrows()
        elif dataset == 'summaries':
            self.summaries['noformats'] = self.summaries[[colname][0]].str.findall(r'(\{noformat.*?\}(.*?)\{noformat\})')
            loop = self.summaries.iterrows()
        for i, row in loop:
            if i != 0 and i % 200000 == 0:
                print("Extracting noformats ... processed {0} rows".format(i))
            if isinstance(row.noformats,list) and row.noformats != []:
                cur_noformats = []
                for noformat in row.noformats:
                    cur_noformats.append(noformat[1])
                new_items.append(' '.join(cur_noformats))
            else:
                new_items.append('')

        print("noformat extraction complete. Processed {0} rows".format(i))
        # Remove noformat parts from the given column
        if dataset == 'comments':
            self.comments['noformats'] = pd.Series(new_items).values
            self.comments[[colname]] = self.comments[[colname]].replace(r'(\{noformat.*?\}(.*?)\{noformat\})', '', regex=True)
        elif dataset == 'summaries':
            self.summaries['noformats'] = pd.Series(new_items).values
            self.summaries[[colname]] = self.summaries[[colname]].replace(r'(\{noformat.*?\}(.*?)\{noformat\})', '', regex=True)



    def extract_code(self, dataset='comments', colname='comment'):
        print("Extracting {{code}} tags. Dataset: {0}, Column: {1}. This may take some time ...".format(dataset,colname))
        new_items = []
        if dataset == 'comments':
            self.comments['code'] = self.comments[[colname][0]].str.findall(r'(\{[Cc]ode.*?\}(.*?)\{[Cc]ode\})')
            loop = self.comments.iterrows()
        elif dataset == 'summaries':
            self.summaries['code'] = self.summaries[[colname][0]].str.findall(r'(\{[Cc]ode.*?\}(.*?)\{[Cc]ode\})')
            loop = self.summaries.iterrows()
        for i, row in loop:
            if i != 0 and i % 200000 == 0:
                print("Extracting code ... processed {0} rows".format(i))
            if  isinstance(row.code,list) and row.code != []:
                cur_code = []
                for code_block in row.code:
                    cur_code.append(code_block[1])
                new_items.append(' '.join(cur_code))
            else:
                new_items.append('')

        print("Code extraction complete. Processed {0} rows".format(i))
        # Remove code parts from the column and move them to a new one
        if dataset == 'comments':
            self.comments['code'] = pd.Series(new_items).values
            self.comments[[colname]] = self.comments[[colname]].replace(r'(\{[Cc]ode.*?\}(.*?)\{[Cc]ode\})', '', regex=True)
        elif dataset == 'summaries':
            self.summaries['code'] = pd.Series(new_items).values
            self.summaries[[colname]] = self.summaries[[colname]].replace(r'(\{[Cc]ode.*?\}(.*?)\{[Cc]ode\})', '', regex=True)



    def extract_panels(self, dataset='comments', colname='comment'):
        # I am not sure if panels can include nested panels. I will assume no.
        print("Extracting text in {{panel}} tags. Dataset: {0}, Column: {1}. This will take some time ...".format(dataset,colname))
        new_items = []
        if dataset == 'comments':
            self.comments['panels'] = self.comments[[colname][0]].str.findall(r'(\{[Pp]anel.*?\}(.*?)\{[Pp]anel\})')
            loop = self.comments.iterrows()
        elif dataset == 'summaries':
            self.summaries['panels'] = self.summaries[[colname][0]].str.findall(r'(\{[Pp]anel.*?\}(.*?)\{[Pp]anel\})')
            loop = self.summaries.iterrows()
        for i, row in loop:
            if i != 0 and i % 200000 == 0:
                print("Extracting panels ... processed {0} rows".format(i))
            if isinstance(row.panels,list) and row.panels != []:
                cur_panel = []
                for panel in row.panels:
                    cur_panel.append(panel[1])
                new_items.append(' '.join(cur_panel))
            else:
                new_items.append('')

        print("Panel extraction complete. Processed {0} rows".format(i))
        # Remove panel parts from the given column and move them to a new one
        if dataset == 'comments':
            self.comments['panels'] = pd.Series(new_items).values
            self.comments[[colname]] = self.comments[[colname]].replace(r'(\{[Pp]anel.*?\}(.*?)\{[Pp]anel\})', '', regex=True)
        elif dataset == 'summaries':
            self.summaries['panels'] = pd.Series(new_items).values
            self.summaries[[colname]] = self.summaries[[colname]].replace(r'(\{[Pp]anel.*?\}(.*?)\{[Pp]anel\})', '', regex=True)



    def fix_bad_tag_cases(self, dataset='comments', colname='comment'):
        # More will probably be added
        print("Fixing bad tag cases. Dataset: {0}, Column: {1} ...".format(dataset,colname))
        if dataset == 'comments':
            self.comments[[colname]] = self.comments[[colname]].replace('{Noformat', '{noformat', regex=True)
        elif dataset == 'summaries':
            self.summaries[[colname]] = self.summaries[[colname]].replace('{Noformat', '{noformat', regex=True)



    def remove_special_tags(self, dataset='comments', colname='comment'):
        print("Removing special tags. Dataset: {0}, Column: {1} ...".format(dataset,colname))
        if dataset == 'comments':
            self.comments[[colname]] = self.comments[[colname]].replace(r'(\{[Cc]olor.*?\}(.*?)\{[Cc]olor\})', '', regex=True)
        elif dataset == 'summaries':
            self.summaries[[colname]] = self.summaries[[colname]].replace(r'(\{[Cc]olor.*?\}(.*?)\{[Cc]olor\})', '', regex=True)



    def remove_punctuation(self, dataset='comments',colname='comment'):
        print("Removing punctuation (apart from dashes and underscores). Dataset: {0}, Column: {1} ...".format(dataset,colname))
        # Remove punctuation except for dashes (-) and underscores(_)
        punct = '|'.join([re.escape(x) for x in string.punctuation.replace('-','').replace('_','')])
        new_items = []
        if dataset == 'comments':
            loop = self.comments.iterrows()
        elif dataset == 'summaries':
            loop = self.summaries.iterrows()
        for i, row in loop:
            if i != 0 and i % 200000 == 0:
                print("Removing punctuation from {0} ... processed {1} rows".format(colname, i))
            # After a recent change, the else here may not be needed - Check it
            if isinstance(row[colname],str):
                new_items.append(re.sub(punct,' ',row[colname]))
            else:
                new_items.append('')

        print("Punctuation removal complete. Processed {0} rows".format(i))
        if dataset == 'comments':
            self.comments[colname] = pd.Series(new_items).values
        elif dataset == 'summaries':
            self.summaries[colname] = pd.Series(new_items).values



    def remove_digit_only_words(self, dataset='comments', colname='comment'):
        print("Removing digit-only words. Dataset: {0}, Column: {1} ...".format(dataset,colname))
        new_items = []
        if dataset == 'comments':
            loop = self.comments.iterrows()
        elif dataset == 'summaries':
            loop = self.summaries.iterrows()
        for i, row in loop:
            if i != 0 and i%200000 == 0:
                print("Removing digit-only words from {0} ... processed {1} rows".format(colname, i))
            words = row[colname].split()
            new_items.append(' '.join([word for word in words if not word.isdigit()]))
        print("Digit-only word removal complete. Processed {0} rows".format(i))
        if dataset == 'comments':
            self.comments[colname] = pd.Series(new_items).values
        elif dataset == 'summaries':
            self.summaries[colname] = pd.Series(new_items).values



    def remove_small_words(self, dataset, colname, minlen):
        print("Removing small words (len < {0}). Dataset: {1}, Column: {2} ...".format(minlen,dataset,colname))
        new_items = []
        if dataset == 'comments':
            loop = self.comments.iterrows()
        elif dataset == 'summaries':
            loop = self.summaries.iterrows()
        for i, row in loop:
            if i != 0 and i%200000 == 0:
                print("Removing small words (len < {0}) from {1} ... processed {2} rows".format(minlen, colname, i))
            words = row[colname].split()
            new_items.append(' '.join([word for word in words if len(word) >= minlen]))
        print("Small word removal complete. Processed {0} rows".format(i))
        if dataset == 'comments':
            self.comments[colname] = pd.Series(new_items).values
        elif dataset == 'summaries':
            self.summaries[colname] = pd.Series(new_items).values



    def convert_to_lowercase(self, dataset, colname):
        print("Converting to lowercase. Dataset: {0}, Column: {1} ...".format(dataset,colname))
        if dataset == 'comments':
            self.comments[colname] = self.comments[colname].str.lower()
        elif dataset == 'summaries':
            self.summaries[colname] = self.summaries[colname].str.lower()



    def remove_stopwords(self, dataset, colname):
        print("Removing stopwords. Dataset: {0}, Column {1} ...".format(dataset,colname))
        new_items = []
        if dataset == 'comments':
            loop = self.comments.iterrows()
        elif dataset == 'summaries':
            loop = self.summaries.iterrows()
        for i, row in loop:
            if i != 0 and i%200000 == 0:
                print("Removing stopwords from {0} ... processed {1} rows".format(colname, i))
            words = row[colname].split()
            new_items.append(' '.join([word for word in words if word not in self.stopwords]))
        print("Stopwords removal complete. Processed {0} rows".format(i))
        if dataset == 'comments':
            self.comments[colname] = pd.Series(new_items).values
        elif dataset == 'summaries':
            self.summaries[colname] = pd.Series(new_items).values



    def combine_ticket_presence_and_creation(self):
        print("Combining ticket presence and creation through comments...")
        # We'll need to know the active authors to include the active status in the added rows
        print("Generating list of active authors...")
        # Compare it as a string, not as a boolen (check if can be changed - it should be easy)
        active_authors = self.comments.author[self.comments.active=='True'].unique().tolist()

        print("Generating involvement map...")
        involvement = defaultdict(set)
        for _, comment in self.comments[['key','author']].iterrows():
            involvement[comment.key].add(comment.author)
        print("Involvement from comments generated. Moving to summaries...")
        for _, summary in self.summaries[['key','creator']].iterrows():
            involvement[summary.key].add(summary.creator)
        print("Involvement from summaries generated.")
        j = 0
        new_rows = []
        for _, ticket in self.summaries[['key','summary','created','issuetype']].iterrows():
            for person in involvement[ticket.key]:
                new_rows.append({
                    'key': ticket.key,
                    'author': person,
                    'active': person in active_authors,
                    'created': ticket.created,
                    'issuetype': ticket.issuetype,
                    'comment': ticket.summary,
                    'code': '',
                    'quotes': '',
                    'noformats': '',
                    'panels': ''
                })
            j += 1
            if j%1000 == 0:
                print("Processed {0} tickets.".format(j))
        print("Presence combination finished. Combined presence introduced {0} new rows".format(len(new_rows)))
        # Now write the result to a new csv
        dict_keys = new_rows[0].keys()
        with open('{0}/presence.csv'.format(self.output_path), 'w') as f:
            dict_writer = DictWriter(f, dict_keys)
            dict_writer.writeheader()
            dict_writer.writerows(new_rows)



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
        # Create output folders if they don't already exist
        if not os.path.isdir(self.output_path):
            os.makedirs(self.output_path)

        if len(columns) == 0:
            self.comments.to_csv('{0}/{1}'
                .format(self.output_path,self.comms_output_file), index=False)
        else:
            self.comments.to_csv('{0}/{1}_only.csv'
                .format(self.output_path,'-'.join(columns)),columns=columns, index=False)



    """ Save summaries to a CSV file with the selected columns. Save all columns if none is specified. """
    def summaries_to_csv(self, columns=[]):
        if not os.path.isdir(self.output_path):
            os.makedirs(self.output_path)

        if len(columns) == 0:
            self.summaries.to_csv('{0}/{1}'
                .format(self.output_path,self.summs_output_file), index=False)
        else:
            self.summaries.to_csv('{0}/{1}_only.csv'
                .format(self.output_path,'-'.join(columns)),columns=columns, index=False)



    def selective_preprocess(self):
        if os.path.isfile("{0}/{1}".format(self.output_path,self.comms_output_file)) and not self.args.rebuild:
            print("Preprocessed comments already exist. Run with --rebuild to rebuild anyway.")
            return

        self.load_comments()
        self.clean_newlines('comments','comment')
        self.drop_na('comments','comment')

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

        self.remove_urls('comments','comment') if p_url else {}
        self.remove_emails('comments','comment') if p_email else {}
        self.remove_multiple_spaces('comments','comment') if p_spaces else {}
        self.fix_bad_tag_cases('comments','comment') if p_fixtags else {}
        self.remove_special_tags('comments','comment') if p_specialtags else {}
        self.extract_code('comments','comment') if p_code else {}
        self.extract_quotes('comments','comment') if p_quotes else {}
        self.extract_noformats('comments','comment') if p_noformats else {}
        self.extract_panels('comments','comment') if p_panels else {}
        for column in ['comment', 'quotes', 'noformats', 'panels']:
            self.remove_punctuation('comments',column) if p_punct else {}
            # Now remove spaces again from each column
            self.remove_multiple_spaces('comments',column) if p_spaces else {}

        for column in ['comment', 'quotes', 'noformats', 'panels', 'code']:
            self.remove_digit_only_words('comments',column) if p_digits else {}
            self.remove_small_words('comments',column, minlen=2) if p_small else {}
            self.convert_to_lowercase('comments',column) if p_lower else {}
            self.remove_stopwords('comments',column) if p_stop else {}

        if p_lemma == True:
            self.lemmatizer = spacy.load('en')
            self.lemmatize(colname='comment')
            # Write out comment column only for inspection
            self.comments_to_csv(['comment'])

        # Write out the preprocessed comments file
        self.comments_to_csv()



    def preprocess(self):
        if os.path.isfile("{0}/{1}"
            .format(self.output_path,self.comms_output_file)) and not self.args.rebuild:
            print("Preprocessed comments already exist. Run with --rebuild to rebuild anyway.")
            return

        if os.path.isfile("{0}/{1}"
            .format(self.output_path,self.summs_output_file)) and not self.args.rebuild:
            print("Preprocessed summaries already exist. Run with --rebuild to rebuild anyway.")
            return

        # Load datasets
        self.load_comments()
        self.load_summaries()

        # Ignore comments from inactive users
        if ACTIVE_ONLY == True:
            self.ignore_inactive_user_comments()

        # Clean the newlines where it makes sense to
        self.clean_newlines('comments','comment')
        self.clean_newlines('summaries','description')

        # Drop rows with NA values in that column where it makes sense (so not in description of summaries)
        self.drop_na('comments','comment')
        self.drop_na('summaries','summary')

        # Remove URLs
        self.remove_urls('comments','comment')
        self.remove_urls('summaries','summary')
        self.remove_urls('summaries','description')

        # Remove emails
        self.remove_emails('comments','comment')
        self.remove_emails('summaries','summary')
        self.remove_emails('summaries','description')

        # Remove multiple spaces
        self.remove_multiple_spaces('comments','comment')
        self.remove_multiple_spaces('summaries','summary')
        self.remove_multiple_spaces('summaries','description')

        # Fix some of the bad tag cases (eg. {Noformat)). Will not do this for summary column of summaries
        self.fix_bad_tag_cases('comments','comment')
        self.fix_bad_tag_cases('summaries','description')

        # Remove special tags
        self.remove_special_tags('comments','comment')
        self.remove_special_tags('summaries','description')

        # Extracting special blocks like code, quotes, noformats and panels
        self.extract_code('comments','comment')
        self.extract_code('summaries','description')
        self.extract_quotes('comments','comment')
        self.extract_quotes('summaries','description')
        self.extract_noformats('comments','comment')
        self.extract_noformats('summaries','description')
        self.extract_panels('comments','comment')
        self.extract_panels('summaries','description')

        for column in ['comment', 'quotes', 'noformats', 'panels']:
            self.remove_punctuation('comments',column)
        # This is deliberately out of the for loop - Could we avoid having to do this again?
        # note: this may really be unecessary and can probably be removed - Check it 
        self.remove_multiple_spaces('comments','comment')

        for column in ['summary', 'description']:
            self.remove_punctuation('summaries',column)
        # This is deliberately out of the for loop
        self.remove_multiple_spaces('summaries','description')

        for column in ['comment', 'quotes', 'noformats', 'panels', 'code']:
            self.remove_digit_only_words('comments',column)
            self.remove_small_words('comments',column,minlen=2)
            self.convert_to_lowercase('comments',column)
            self.remove_stopwords('comments',column)

        # Same for summaries
        for column in ['summary','description']:
            self.remove_digit_only_words('summaries',column)
            self.remove_small_words('summaries',column,minlen=2)
            self.convert_to_lowercase('summaries',column)
            self.remove_stopwords('summaries',column)

        # Initialize lemmatizer and apply lemmatization to the comments.
        # (would be good to do this for panels and quotes maybe)
        # self.lemmatizer = spacy.load('en')
        # self.lemmatize(colname='comment')

        # Write out the preprocessed comments file
        self.comments_to_csv()
        # Write out comment column only for inspection
        self.comments_to_csv(['comment'])

        # Write out the preprocessed summaries to a file
        self.summaries_to_csv()
        self.summaries_to_csv(['summary'])

        ######################################################
        # Include summaries and comment presence as comments #
        ######################################################
        # The following cases will result to a pseudo-comment added with the ticket summary
        # * Ticket creation  (whoever created the ticket)
        # * Comment presence (whoever commented on the ticket)
        # * Moved after
        self.combine_ticket_presence_and_creation()
        # And now append the combined to the comments for full thrust!
        combined = pd.concat([
            self.comments,
            pd.read_csv('{0}/presence.csv'.format(self.output_path), header=0)
        ])
        # And write the all to the final output file
        combined.to_csv(
            '{0}/combined.csv'.format(self.output_path),
            columns=['key','created','issuetype','author','active','comment','code','quotes'],
            index=False
        )


preprocessor = DataPreprocessor()
if preprocessor.args.selective:
    preprocessor.selective_preprocess()
else:
    preprocessor.preprocess()
