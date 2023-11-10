from direct_indexing.custom_fields.policy_marker_combined import policy_marker_combined


def test_policy_marker_combined():
    pm = 'policy-marker'
    pmc = 'policy-marker.combined'
    # Test if no policy-marker, assert nothing changes
    data = {}
    data = policy_marker_combined(data)
    assert data == {}

    # Test if a policy-marker is an empty dict, it is converted to a list
    data = {pm: {}}
    data = policy_marker_combined(data)
    assert data[pm] == [{}]  # Also tests if there is no code in pm
    assert data[pmc] == []

    # Test if pm has code, it is added to pmc with its significance.
    data = {pm: [{'code': 1}, {'code': 2, 'significance': 1}]}
    data = policy_marker_combined(data)
    # 1__n because the significance is not present for code 1
    # 2__1 because the significance is 1 for code 2
    assert data[pmc] == ['1__n', '2__1']
