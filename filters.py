import constants


def formatted_duration(duration, input_units):
    base_duration = float(duration * constants.TIME_UNITS[input_units])
    if base_duration < 1:
        return '<1 %s' % constants.TIME_ABBREVIATIONS['second']
    parts = []
    for unit, value in constants.TIME_UNITS.items()[::-1]:
        if base_duration >= value:
            parts.append((base_duration / value, constants.TIME_ABBREVIATIONS[unit]))
            base_duration %= value
    return ' '.join('%d %s' % (value, abbr) for value, abbr in parts)


filters = {
    'duration': formatted_duration,
}
