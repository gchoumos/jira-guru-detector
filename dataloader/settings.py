""" Dataloader settings """
SETTINGS = {
    'jiraPrj': 'WIL',
    'options': {
        'server': 'https://jira.openbet.com',
    },
    'ticketFrom': 30000,
    'ticketTo': 30100,
    'maxResults': 200, # (defaults to 50)
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

"""
The Jira batches with boundaries that do exist. That's because if any
boundary does not exist, search with JQL against issuekey (or id) fails!
If there is another way to elegantly avoid this, then do so. To be clear
on this, it's not something that I haven't thought of, it's because of
a Jira Server **BUG**. I won't be doing funny hacks in the code just to
make this work by overcoming the Jira Server bugs. This should just be
fixed by Atlassian.

They are to be taken in pairs (from - to)

Created with the commands:
startl = [x for x in range(30000,57199,200)]
endl = [x for x in range(30199,57200,200)]
batch_intervals = startl + endl
batch_intervals.sort()
"""
BATCH_INTERVALS = [
    30000, 30199, 30200, 30399, 30400, 30599, 30600, 30799, 30800, 30999,
    31000, 31199, 31200, 31399, 31400, 31599, 31600, 31799, 31800, 31999,
    32000, 32199, 32200, 32399, 32400, 32599, 32600, 32799, 32800, 32999,
    33000, 33199, 33200, 33399, 33400, 33599, 33600, 33799, 33800, 33999,
    34000, 34199, 34200, 34399, 34400, 34599, 34600, 34799, 34800, 34999,
    35000, 35199, 35200, 35399, 35400, 35599, 35600, 35799, 35800, 35999,
    36000, 36199, 36200, 36399, 36400, 36599, 36600, 36799, 36800, 36999,
    37000, 37199, 37200, 37399, 37400, 37599, 37600, 37799, 37800, 37999,
    38000, 38199, 38200, 38399, 38400, 38599, 38600, 38799, 38800, 38999,
    39000, 39199, 39200, 39399, 39400, 39599, 39600, 39799, 39800, 39999,
    40000, 40199, 40200, 40399, 40400, 40599, 40600, 40799, 40800, 40999,
    41000, 41199, 41200, 41399, 41400, 41599, 41600, 41799, 41800, 41999,
    42000, 42199, 42200, 42399, 42400, 42599, 42600, 42799, 42800, 42999,
    43000, 43199, 43200, 43399, 43400, 43599, 43600, 43799, 43800, 43999,
    44000, 44199, 44200, 44399, 44400, 44599, 44600, 44799, 44800, 44999,
    45000, 45199, 45200, 45399, 45400, 45599, 45600, 45799, 45800, 45999,
    46000, 46199, 46200, 46399, 46400, 46599, 46600, 46799, 46800, 46999,
    47000, 47199, 47200, 47399, 47400, 47599, 47600, 47799, 47800, 47999,
    48000, 48199, 48200, 48399, 48400, 48599, 48600, 48799, 48800, 48999,
    49000, 49199, 49200, 49399, 49400, 49599, 49600, 49799, 49800, 49999,
    50000, 50199, 50200, 50399, 50400, 50599, 50600, 50799, 50800, 50999,
    51000, 51199, 51200, 51399, 51400, 51599, 51600, 51799, 51800, 51999,
    52000, 52199, 52200, 52399, 52400, 52599, 52600, 52799, 52800, 52999,
    53000, 53199, 53200, 53399, 53400, 53599, 53600, 53799, 53800, 53999,
    54000, 54199, 54200, 54399, 54400, 54599, 54600, 54799, 54800, 54999,
    55000, 55199, 55200, 55399, 55400, 55599, 55600, 55799, 55800, 55999,
    56000, 56199, 56200, 56399, 56400, 56599, 56600, 56799, 56800, 56999,
    57000, 57199,
]

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