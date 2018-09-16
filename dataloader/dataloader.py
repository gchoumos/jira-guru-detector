
import getpass
import pprint
import json
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
            .format(self.jiraPrj, self.ticketFrom, self.ticketTo), fields=self.fields)

        # Let's check the results
        for issue in issues:
            print(issue.key)
            # pprint.pprint(issue.raw)
            # for field in self.fields:
            #     pprint.pprint(issue.raw['fields'][field])

    # def format_field(self,cur_field):
    #     if not self.keep_noformat:
    #         cur_field =


dataLoader = DataLoader()
dataLoader.get_credentials()
dataLoader.jira_connect()
dataLoader.get_issues()