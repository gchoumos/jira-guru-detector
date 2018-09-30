""" Settings for the Data Preprocessor """


# The following list should hold all the valid users. Any data coming from inactive
# users should be discarded.
VALID_USERS = [
 'user1', 'user2', 'user3',
]

# Issue types not in this list will be discarded.
VALID_ISSUE_TYPES = [
  'Analysis',
  'Change Request',
  'Defect',
  'Development',
  'Epic',
  'Incident',
  'Problem',
  'Story',
  'Task',
]
