""" Settings for the Data Preprocessor """

# The team that we will be running this for
TEAM = 'WIL'

# Consider only users that are still active in Jira. Default = True
ACTIVE_ONLY = True

DP_SETTINGS = {
    'input_path': '/home/gchoumo/Documents/jira-guru-detector/datasets',
    'output_path': '/home/gchoumo/Documents/jira-guru-detector/datasets/preprocessed_{0}'.format(TEAM),
    'jiraPrj': TEAM,
}

# Issue types not in this list will be discarded. If it's empty though, everything will be included.
VALID_ISSUE_TYPES = [
  'Alert',
  'Analysis',
  'Casino Defect',
  'Change',
  'Defect',
  'Development',
  'Documentation Request',
  'Epic',
  'Incident',
  'Problem',
  'Release Request',
  'Requirement Capture',
  'Story',
  'Subtask',
  'Task',
  'Test Execution',
  'Test Preparation',
]

# These are in addition to the stopwords.
# h1-h6: Jira comment notation for headers
# p1-p5: The Jira priorities
WORDS_TO_IGNORE = {
  '2char': [
    'll',
    'hi',
    'cc',
    'wh',
    'im',
    'p1', 'p2', 'p3', 'p4', 'p5',
    '1g', '2g', '3g', '4g', '5g', '6g', '7g', '8g',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'kb',
  ]
}

# Will be overriden by the redacted settings. 
IGNORE_AUTHOR_GROUPS = [r'.*exampleregexp\.com', r'.*exampleregexp2\.com']
ACTIVE_USERS = {
  'TEAM-1': {
    'test1': 'Test User 1',
    'test2': 'Test User 2',
    'test3': 'Test User 3',
  },
  'TEAM-2': {
    'test4': 'Test User 4'
  }
}

try:
    from redacted import *
except ImportError:
    print("No valid redacted settings found.")
