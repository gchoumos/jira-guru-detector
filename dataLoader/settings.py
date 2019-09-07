""" Dataloader settings """
SETTINGS = {
    'jiraPrj': 'WIL',
    'options': {
        'server': 'https://jira.openbet.com',
    },
    'ticketFrom': 50000, # doesn't matter anymore
    'ticketTo': 61674, # doesn't matter anymore
    'maxResults': 200, # (defaults to 50)
    'fields': [
        'key',
        'summary',
        'assignee',
        'created',
        'issuetype',
        'description',
        'comment',
        'labels',
        'creator',
    ],
    'summaries_fields': [
        'key',
        'summary',
        'creator',
        'created',
    ],
    'output_path': '/home/gchoumo/Documents/jira-guru-detector/datasets',
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
startl = [x for x in range(20000,57199,200)]
endl = [x for x in range(20199,57200,200)]
batch_intervals = startl + endl
batch_intervals.sort()

# Then changed the boundaries that were complaining to valid ones
"""
BATCH_INTERVALS = [
    20000, 20199, 20200, 20399, 20400, 20599, 20600, 20799, 20800, 20999,
    21000, 21199, 21200, 21399, 21400, 21599, 21600, 21799, 21800, 21999,
    22000, 22199, 22200, 22399, 22400, 22599, 22600, 22799, 22800, 22999,
    23000, 23199, 23200, 23399, 23400, 23599, 23600, 23799, 23800, 23999,
    24000, 24199, 24200, 24399, 24400, 24599, 24600, 24799, 24800, 24999,
    25000, 25199, 25200, 25399, 25400, 25599, 25600, 25799, 25800, 25996, # <-- modded
    26000, 26199, 26200, 26399, 26400, 26599, 26600, 26799, 26800, 26999,
    27000, 27199, 27200, 27399, 27400, 27599, 27600, 27799, 27800, 27999,
    28000, 28199, 28200, 28399, 28400, 28599, 28600, 28799, 28800, 28999,
    29000, 29199, 29200, 29399, 29400, 29599, 29600, 29799, 29800, 29999,
    30000, 30199, 30200, 30399, 30400, 30599, 30600, 30799, 30800, 30999,
    31000, 31199, 31200, 31399, 31400, 31599, 31600, 31799, 31800, 31999,
    32000, 32199, 32200, 32399, 32400, 32599, 32600, 32799, 32800, 32999,
    33000, 33199, 33200, 33399, 33400, 33599, 33600, 33799, 33800, 33999,
    34000, 34199, 34200, 34399, 34400, 34599, 34600, 34799, 34800, 34999,
    35000, 35199, 35200, 35399, 35400, 35599, 35600, 35799, 35800, 35999,
    36000, 36199, 36201, 36399, 36400, 36599, 36600, 36799, 36800, 36999, # <-- modded
    37000, 37199, 37200, 37399, 37400, 37599, 37601, 37799, 37800, 37999, # <-- modded
    38000, 38199, 38200, 38399, 38400, 38599, 38600, 38799, 38800, 38999,
    39000, 39199, 39203, 39399, 39400, 39599, 39600, 39799, 39800, 39999, # <-- modded
    40000, 40199, 40200, 40399, 40400, 40599, 40600, 40799, 40800, 40999,
    41000, 41199, 41200, 41398, 41400, 41599, 41600, 41799, 41800, 41999, # <-- modded
    42000, 42199, 42200, 42399, 42400, 42599, 42600, 42799, 42800, 42999,
    43000, 43199, 43200, 43399, 43400, 43599, 43600, 43799, 43800, 43999,
    44000, 44199, 44200, 44399, 44400, 44599, 44600, 44799, 44800, 44999,
    45000, 45199, 45200, 45399, 45400, 45599, 45600, 45799, 45800, 45999,
    46000, 46199, 46200, 46399, 46400, 46599, 46600, 46799, 46800, 46999,
    47000, 47199, 47200, 47399, 47400, 47599, 47600, 47799, 47800, 47999,
    48000, 48199, 48200, 48399, 48400, 48599, 48600, 48799, 48800, 48999,
    49000, 49199, 49200, 49399, 49400, 49599, 49600, 49799, 49800, 49980, # <-- modded
    50002, 50199, 50200, 50399, 50400, 50599, 50600, 50799, 50800, 50999, # <-- modded
    51000, 51199, 51200, 51399, 51400, 51599, 51600, 51799, 51800, 51999,
    52000, 52199, 52200, 52398, 52400, 52599, 52600, 52799, 52800, 52999, # <-- modded
    53000, 53199, 53200, 53399, 53401, 53599, 53600, 53799, 53800, 53999, # <-- modded
    54000, 54199, 54200, 54399, 54400, 54599, 54600, 54799, 54800, 54999,
    55000, 55199, 55200, 55399, 55400, 55599, 55600, 55799, 55800, 55999,
    56000, 56199, 56200, 56399, 56400, 56599, 56600, 56799, 56800, 56999,
    57000, 57199, 57200, 57399, 57400, 57599, 57600, 57799, 57800, 57999,
    58000, 58199, 58200, 58399, 58400, 58599, 58600, 58799, 58800, 58999,
    59000, 59199, 59200, 59399, 59400, 59599, 59600, 59799, 59800, 59951, # <-- modded
    60001, 60199, 60200, 60399, 60400, 60599, 60600, 60799, 60800, 60999, # <-- modded
    61000, 61199, 61200, 61399, 61400, 61599, 61600, 61674, 
]

################################################
# Boundaries removed as they don't exist (WIL) #
################################################
# 25997, 25998, 25999, 36200, 37600, 39200, 41399
# 49981-49999, 50000 (because it's a troll ticket)
# 50001, 52399, 53400, 59952-59999 (those are a
# lot and they really don't exist. probably a user
# - the one who created WIL-60000 did it on purpose)
# 60000 (because it's a troll ticket)