def policy_marker_combined(data):
    """
    Requested for MFA by Zimmerman: a combined code and significance,
    connected with two underscores.

    Policy marker code is required, significance optional. If the latter is
    not available, use the letter N.

    :param data: reference to the activity in the data
    """
    s = 'significance'
    if 'policy-marker' not in data:
        return data

    if type(data['policy-marker']) is dict:
        data['policy-marker'] = [data['policy-marker']]
    data['policy-marker.combined'] = []
    for pm in data['policy-marker']:
        if 'code' not in pm:
            continue  # skip if there is no code reported
        code = pm['code']
        pmc = f'{code}__'
        if s in pm and pm[s] is not None:
            pmc += str(pm[s])
        else:
            pmc += 'n'
        data['policy-marker.combined'].append(pmc)
    return data
