def policy_marker_combined(data):
    """
    Requested for MFA by Zimmerman: a combined code and significance,
    connected with two underscores.

    Policy marker code is required, significance optional. If the latter is
    not available, use the letter N.

    :param data: reference to the activity in the data
    """
    try:
        data['policy-marker.combined'] = []
        s = 'significance'
        for pm in data['policy-marker']:
            # data.
            code = pm['code']
            if s in pm.keys() and pm[s] is not None:
                pmc = f'{code}__{pm[s]}'
            else:
                pmc = f'{code}__n'
            data['policy-marker.combined'].append(pmc)
    except:  # NOQA
        pass  # No policy marker found
    return data
