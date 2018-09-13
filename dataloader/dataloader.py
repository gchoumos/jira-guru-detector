
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
        self.fields = SETTINGS['fields']

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
        """ Using JQL to get multiple results with a single request """
        print("Will retrieve titles for tickets {0}-{1} to {0}-{2}"
            .format(self.jiraPrj, self.ticketFrom, self.ticketTo))

        # Build the JQL string and send a search request.
        issues = self.jira.search_issues(
            "id >= '{0}-{1}' and id <= '{0}-{2}'"
            .format(self.jiraPrj, self.ticketFrom, self.ticketTo), fields=self.fields)

        # Let's check the results
        for issue in issues:
            print("{0} -- {1}".format(issue.key,issue.fields.summary))


dataLoader = DataLoader()
dataLoader.get_credentials()
dataLoader.jira_connect()
dataLoader.get_titles()