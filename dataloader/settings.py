""" Dataloader settings """
SETTINGS = {
    'jiraPrj': 'WIL',
    'options': {
        'server': 'https://jira.openbet.com',
    },
    'ticketFrom': 50000,
    'ticketTo': 50100,
    'maxResults': 100, # (defaults to 50)
    'fields': [
        'key',
        'summary',
        'assignee',
        'created',
        'issuetype',
        'description',
        'comment', # We want stuff under the comment.comments
        'labels',
        'reporter',
    ],
    'summaries_fields': [
        'key',
        'summary',
        'reporter',
        'created',
    ],
    'keep_noformat': False,
    'keep_code': False,
}

#####################
## Issue Structure ##
#####################
#
# issue
#   key (eg. 'WIL-4')
#   id  (eg. '162344' - we don't care)
#
#
# issue.raw
# {
#     'key': 'WIL-4',
#     'id': '162344',
#     'fields': {
#         'assignee': {
#             'timeZone': '',
#             'self': '',
#             'displayName': 'George Choumos',
#             'name': 'gchoumo',
#             'avatarUrls': {},
#             'active': True,
#             'key': 'george.choumos@sgdigital.com',
#             'emailAddress': 'george.choumos@sgdigital.com',
#         },
#         'comment': {
#             'total': 2,
#             'startAt': 0,
#             'comments':
#         }
#     }
#
#
# comment
#   comments (list of dicts [{},{},{}])
#     self
#     id
#     author
#       self
#       name
#       key
#       emailAddress
#       avatarUrls
#       displayName
#       active
#    body