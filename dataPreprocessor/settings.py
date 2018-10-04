""" Settings for the Data Preprocessor """

# Issue types not in this list will be discarded. If it's empty, include them all.
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

# Will be overriden by the redacted settings. 
IGNORE_AUTHOR_GROUPS = [r'.*exampleregexp\.com', r'.*exampleregexp2\.com']
WIL_USERS_ACTIVE = ['exampleuser1', 'exampleuser2', 'exampleuser3']
VALID_USERS = ['exampleuser1','exampleuser2']

try:
    from redacted import *
except ImportError:
    print("No valid redacted settings found.")
