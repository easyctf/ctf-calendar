from collections import OrderedDict

SECOND = 1
MINUTE = 60 * SECOND
HOUR = 60 * MINUTE
DAY = 24 * HOUR
WEEK = 7 * DAY

TIME_UNITS = OrderedDict([
    ('second', SECOND),
    ('minute', MINUTE),
    ('hour', HOUR),
    ('day', DAY),
    ('week', WEEK),
])

TIME_ABBREVIATIONS = OrderedDict([
    ('second', 's'),
    ('minute', 'm'),
    ('hour', 'h'),
    ('day', 'd'),
    ('week', 'w'),
])
