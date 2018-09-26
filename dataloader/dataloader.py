"""
TO DO

- If assignee is different than the creator (or reporter) then maybe we could insert a line for both
  (if they are openbet of course). This will also benefit us in cases that the ticket has been raised
  by WH, which means that the summary line will be ignored.
- What about using creator instead of reporter??
- We may be only getting a maximum of 50 comments per issue. Have a look at this.
- Mention the captcha challenge case that leads to a login error.
- I should make sure that the csv files are generated in the proper directory. Currently I only give
  the name. This will be useful to later check if they are already there so we can ask if the user wants
  to indeed recreate them or not.
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
        return self.jira.search_issues(
            "project = {0} and issuekey >= {0}-{1} and issuekey <={0}-{2} order by issuekey asc"
            .format(self.jiraPrj, batchFrom, batchTo),
            maxResults=self.maxResults,
            fields=SETTINGS['fields'])

    def get_issues(self):
        """ Using JQL to get multiple results with a single request """
        print("Will retrieve issues {0}-{1} to {0}-{2} in batches."
            .format(self.jiraPrj, self.ticketFrom, self.ticketTo))

        # For the csv printing
        summ_cols = ['key','summary','creator','created','issuetype','labels','description']
        comm_cols = ['key','created','author','active','comment']
        summ_name = 'summaries.csv'
        comm_name = 'comments.csv'

        # It's ugly I know
        for i in range(0,len(BATCH_INTERVALS),2):
            batchFrom = BATCH_INTERVALS[i]
            batchTo = BATCH_INTERVALS[i+1]
            print("Getting issues {0}-{1} to {0}-{2}".format(self.jiraPrj, batchFrom, batchTo))
            cur_batch = self.get_issues_batch(batchFrom,batchTo)

            # Get the info we want for the "summaries" and "comments" csv files from this batch
            summaries = self.get_summary_data(cur_batch)
            #  'a' to append instead of overwriting
            with open(summ_name,'a') as f:
                writer = csv.DictWriter(f, fieldnames=summ_cols)
                writer.writeheader()
                writer.writerows(summaries)

            comments = self.get_comment_data(cur_batch)
            with open(comm_name,'a') as f:
                writer = csv.DictWriter(f, fieldnames=comm_cols)
                writer.writeheader()
                writer.writerows(comments)

    def get_summary_data(self, issues):
        """ Swaggy list comprehension """
        return [{'key': issue.key,
                 'summary': issue.fields.summary,
                 'creator': issue.fields.creator.name,
                 'created': issue.fields.created[:10],
                 'description': issue.fields.description,
                 'issuetype': issue.fields.issuetype.name,
                 'labels': issue.fields.labels}
                for issue in issues]

    def get_comment_data(self, issues):
        """ List coprehension for comments is a bit more swaggy than for the summaries """
        com_data = []
        for issue in issues:
            for i in range(issue.fields.comment.total):
                com_data.append({
                    'key': issue.key,
                    'created': issue.fields.comment.comments[i].created[:10],
                    'author': issue.fields.comment.comments[i].author.name,
                    'active': issue.fields.comment.comments[i].author.active,
                    'comment': issue.fields.comment.comments[i].body,
                 })
        return com_data

dataLoader = DataLoader()
dataLoader.get_credentials()
dataLoader.jira_connect()
dataLoader.get_issues()
