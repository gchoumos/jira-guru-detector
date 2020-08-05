"""
TO DO

- Mention the captcha challenge case that leads to a login error.
- Find a better way to overcome the jira jql bug when a boundary ticket does not exist.
"""

import getpass
import pprint
import json
import csv
import re
import os
from jira import JIRA
from settings import SETTINGS, BATCH_INTERVALS, ACTIVE_USERS

import pdb

class DataLoader(object):

    def __init__(self):
        print("Initializing DataLoader...")
        self.jiraPrj = SETTINGS['jiraPrj']
        self.fields = SETTINGS['fields']

        # Get the active users of the team(s)/jira project(s) this is about
        self.active_users = {}
        for project in self.jiraPrj:
            if project in ACTIVE_USERS.keys():
                print('Adding active users for project {0}.'.format(project))
                self.active_users.update(ACTIVE_USERS[project])
            else:
                print('{0} does not have an active users list. This may be normal for multi-project cases.'.format(project))

        self.output_path = SETTINGS['output_path']

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


    def get_issues_batch(self, proj, batchFrom, batchTo):
        # If the issue search is of the form "issueKey in (WIL-1, WIL-2, WIL-3), then the
        # latest Jira Server will successfully ignore the non-existent (eg. deleted) issues.
        # Otherwise the range query could fail if a boundary is a non-existent issue.
        # I am forced to use an ugly implementation as the projects I am interested in are
        # not hosted in a Jira Server of the latest (> 2 - I think) version.
        return self.jira.search_issues(
            "project = {0} and issuekey >= {0}-{1} and issuekey <={0}-{2} order by issuekey asc"
            .format(proj, batchFrom, batchTo),
            maxResults=self.maxResults,
            fields=SETTINGS['fields'])


    def get_project_issues(self, proj, projFrom, projTo):
        """ Using JQL to get multiple results with a single request """
        print("Will retrieve issues {0}-{1} to {0}-{2} in batches."
            .format(proj, projFrom, projTo))

        # For the csv printing
        summ_cols = ['key','summary','creator','created','issuetype','labels','description']
        comm_cols = ['key','created','issuetype','author','active','comment']
        summ_file = '{0}/summaries_{1}.csv'.format(self.output_path,'-'.join(self.jiraPrj))
        comm_file = '{0}/comments_{1}.csv'.format(self.output_path,'-'.join(self.jiraPrj))

        # Create output folders if they don't already exist
        if not os.path.isdir(self.output_path):
            os.makedirs(self.output_path)

        # If datasets already exist - Do nothing
        if os.path.isfile(summ_file) or os.path.isfile(comm_file):
            print("Datasets already exist. Exiting...")
            return

        # It's ugly I know
        for i in range(0,len(BATCH_INTERVALS[proj]),2):
            batchFrom = BATCH_INTERVALS[proj][i]
            batchTo = BATCH_INTERVALS[proj][i+1]
            print("Getting issues {0}-{1} to {0}-{2}".format(proj, batchFrom, batchTo))
            cur_batch = self.get_issues_batch(proj,batchFrom,batchTo)

            # Get the info we want for the "summaries" and "comments" csv files from this batch
            summaries = self.get_summary_data(cur_batch)
            # 'a' to append instead of overwriting
            with open(summ_file,'a') as f:
                writer = csv.DictWriter(f, fieldnames=summ_cols)
                writer.writeheader()
                writer.writerows(summaries)

            comments = self.get_comment_data(cur_batch)
            with open(comm_file,'a') as f:
                writer = csv.DictWriter(f, fieldnames=comm_cols)
                writer.writeheader()
                writer.writerows(comments)


    def get_issues(self):
        # Trigger the issue fetching for each project that is configured in the Settings
        print("Jira Projects configured: {0}".format(self.jiraPrj))
        for project in self.jiraPrj:
            issues_from = BATCH_INTERVALS[project][0]
            issues_to = BATCH_INTERVALS[project][-1]
            self.get_project_issues(project, issues_from, issues_to)


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


    # Below change suggestions could probably be implemented in the jql that fetches the data instead of
    # fetching them first and then filtering.
    # Change suggestion: Save only if coming from active account. This is later checked as one of the
    # preprocessor's first steps, but checking it here means that the size of the dataset will be greatly
    # reduced.
    # Change suggestion 2: Save only if it is coming from an author that belongs to the team of interest.
    # This will greatly reduce both the size of this dataset as well as the preprocess time of the preprocessor.
    # This filtering could also happen though in the preprocessor. Currently it happens in the guruDetector.
    def get_comment_data(self, issues):
        """ List coprehension for comments is a bit more swaggy than for the summaries """
        com_data = []
        for issue in issues:
            for i in range(issue.fields.comment.total):
                # This if check reduces dataset size and preprocessing time significantly.
                if issue.fields.comment.comments[i].author.name in self.active_users:
                    com_data.append({
                        'key': issue.key,
                        'created': issue.fields.comment.comments[i].created[:10],
                        'issuetype': issue.fields.issuetype.name,
                        'author': issue.fields.comment.comments[i].author.name,
                        'active': issue.fields.comment.comments[i].author.active,
                        'comment': issue.fields.comment.comments[i].body,
                    })
        return com_data


dataLoader = DataLoader()
dataLoader.get_credentials()
dataLoader.jira_connect()
dataLoader.get_issues()
