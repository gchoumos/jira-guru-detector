
import getpass
from jira import JIRA
from settings import SETTINGS

class DataLoader(object):

    def __init__(self):
        print("Initializing DataLoader...")
        self.jiraUrl = SETTINGS['jiraUrl']
        self.jiraPrj = SETTINGS['jiraPrj']
        self.ticketFrom = SETTINGS['ticketFrom']
        self.ticketTo = SETTINGS['ticketTo']

        print("Jira instance to be used: {0}".format(self.jiraUrl))
        print("Jira project: {0}".format(self.jiraPrj))

    def get_credentials(self):
        self.username = input("Type your username: ")
        self.password = getpass.getpass(prompt="Type your stash password: ")

    def jira_connect(self):
        # With this method a cookie will be created and upon expiration
        # the authentication process will be repeated transparently.
        self.jira = JIRA(self.jiraUrl,auth=(self.username, self.password))

    def get_titles(self):
        """ TODO: Use JQL to do the job with a single request """
        for i in range(self.ticketFrom,self.ticketTo+1):
            print("Processing {0}-{1}".format(self.jiraPrj,i))
            issue = self.jira.issue("{0}-{1}".format(self.jiraPrj,i),fields='summary')
            print(issue.fields.summary)


dataLoader = DataLoader()
dataLoader.get_credentials()
dataLoader.jira_connect()
dataLoader.get_titles()