""" Dataloader settings """
SETTINGS = {
    'jiraPrj': 'WIL',
    'options': {
        'server': 'https://jira.openbet.com',
    },
    'ticketFrom': 4,
    'ticketTo': 4,
    'fields':
            [
                #'key',     # Doesn't need to be explicitly set. We always want it
                'summary',
                'assignee', # We want the assignee.displayName
                'created',
                'issuetype', # We want the issuetype.name
                'description',
                'comment', # We want stuff under the comment.comments
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
# }
#   key     ('WIL-4')
#   id      ('163244')
#   fields  (is a dict)
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