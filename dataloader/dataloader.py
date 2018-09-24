"""
TO DO

-   Put the search for issues in a loop so that we can get more than one batch.
"""


import getpass
import pprint
import json
import csv
import re
from jira import JIRA
from settings import SETTINGS, BATCH_INTERVALS

import pdb

class DataLoader(object):

    def __init__(self):
        print("Initializing DataLoader...")
        self.jiraPrj = SETTINGS['jiraPrj']
        self.ticketFrom = BATCH_INTERVALS[0]
        self.ticketTo = BATCH_INTERVALS[-1]
        self.fields = SETTINGS['fields']

        # Setting of whether special blocks will be kept
        self.keep_noformat = SETTINGS['keep_noformat']
        self.keep_code = SETTINGS['keep_code']

        # The options dict is the one that we pass in the JIRA constructor
        self.options = SETTINGS['options']

        # Max results for the jql searches
        self.maxResults = SETTINGS['maxResults']

        # The dict for the Summaries csv file. Will only hold what we need for the csv.
        self.summaries = {}

        print("Jira instance to be used: {0}".format(self.options['server']))
        print("Jira project: {0}".format(self.jiraPrj))

    def get_credentials(self):
        self.username = input("Type your Jira username: ")
        self.password = getpass.getpass(prompt="Type your Jira password: ")

    def jira_connect(self):
        # With this method a cookie will be created and upon expiration
        # the authentication process will be repeated transparently.
        self.jira = JIRA(self.options,auth=(self.username, self.password))

    def get_issues_batch(self, batchFrom, batchTo):

        # If the issue search is of the form "issueKey in (WIL-1, WIL-2, WIL-3), then the
        # latest Jira Server will successfully ignore the non-existent (eg. deleted) issues.
        # Otherwise the range query could fail if a boundary is a non-existent issue.
        # I am forced to use an ugly implementation as the project I am interested in is
        # not hosted in a Jira Server of the latest (> 2 - I think) version.
        issues = self.jira.search_issues(
            "project = {0} and issuekey >= {0}-{1} and issuekey <={0}-{2}"
            .format(self.jiraPrj, batchFrom, batchTo),
            maxResults=self.maxResults)

        # pprint.pprint(cur_batch)

        # Get the info for the Summaries csv from the issues in the results
        return self.get_issue_summary_data(issues)

    def get_issues(self):
        """ Using JQL to get multiple results with a single request """
        print("Will retrieve issues {0}-{1} to {0}-{2} in batches."
            .format(self.jiraPrj, self.ticketFrom, self.ticketTo))

        # For the csv printing
        summ_cols = ['key','summary','reporter','created','issuetype','labels','description']
        summ_name = 'summaries.csv'

        # It's ugly I know
        for i in range(0,len(BATCH_INTERVALS),2):
            batchFrom = BATCH_INTERVALS[i]
            batchTo = BATCH_INTERVALS[i+1]
            print("Getting issues {0}-{1} to {0}-{2}".format(self.jiraPrj, batchFrom, batchTo))
            cur_batch = self.get_issues_batch(batchFrom,batchTo)

            #  'a' to append instead of overwriting
            with open(summ_name,'a') as f:
                writer = csv.DictWriter(f, fieldnames=summ_cols)
                writer.writeheader()
                writer.writerows(cur_batch)

    def get_issue_summary_data(self, issues):
        """ Swaggy list comprehension """
        # pdb.set_trace()
        return [{'key': issue.key,
                 'summary': issue.fields.summary,
                 'reporter': issue.fields.reporter.name,
                 'created': issue.fields.created[:10],
                 'description': issue.fields.description,
                 'issuetype': issue.fields.issuetype.name,
                 'labels': issue.fields.labels}
                for issue in issues]


dataLoader = DataLoader()
dataLoader.get_credentials()
dataLoader.jira_connect()
dataLoader.get_issues()
