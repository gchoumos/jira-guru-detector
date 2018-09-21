
import getpass
import pprint
import json
import csv
import re
from jira import JIRA
from settings import SETTINGS

import pdb

class DataLoader(object):

    def __init__(self):
        print("Initializing DataLoader...")
        self.jiraPrj = SETTINGS['jiraPrj']
        self.ticketFrom = SETTINGS['ticketFrom']
        self.ticketTo = SETTINGS['ticketTo']
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
        self.username = input("Type your username: ")
        self.password = getpass.getpass(prompt="Type your stash password: ")

    def jira_connect(self):
        # With this method a cookie will be created and upon expiration
        # the authentication process will be repeated transparently.
        self.jira = JIRA(self.options,auth=(self.username, self.password))

    def get_issues(self):
        """ Using JQL to get multiple results with a single request """
        print("Will retrieve issues {0}-{1} to {0}-{2}"
            .format(self.jiraPrj, self.ticketFrom, self.ticketTo))

        # Build the JQL string and send a search request.
        issues = self.jira.search_issues(
            "id >= '{0}-{1}' and id <= '{0}-{2}'"
            .format(self.jiraPrj, self.ticketFrom, self.ticketTo),
                    fields=self.fields, maxResults=self.maxResults)

        # Get the info for the Summaries csv from the issues in the results
        cur_batch = self.get_issue_summary_data(issues)
        pprint.pprint(cur_batch)

        # print that batch to a csv
        summ_cols = ['key','summary','reporter','created','issuetype','labels']
        summ_name = 'summaries.csv'
        with open(summ_name,'w') as f:
            writer = csv.DictWriter(f, fieldnames=summ_cols)
            writer.writeheader()
            for issue in cur_batch:
                writer.writerow(issue)

    def get_issue_summary_data(self, issues):
        """ Swaggy list comprehension """
        return [{'key': issue.key,
                 'summary': issue.fields.summary,
                 'reporter': issue.fields.reporter.name,
                 'created': issue.fields.created[:10],
                 # 'description': issue.fields.description,
                 'issuetype': issue.fields.issuetype.name,
                 'labels': issue.fields.labels}
                for issue in issues]


dataLoader = DataLoader()
dataLoader.get_credentials()
dataLoader.jira_connect()
dataLoader.get_issues()
