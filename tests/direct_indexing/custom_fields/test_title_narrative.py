from direct_indexing.custom_fields.title_narrative import title_narrative_first


def test_title_narrative_first():
    data = []
    assert title_narrative_first(data) == []

    data = {}
    assert title_narrative_first(data) == {}

    data = {'title': {}}
    expected_res = data.copy()
    assert title_narrative_first(data) == expected_res

    data = {'title': {'narrative': 'test'}}
    expected_res = data.copy()
    expected_res['title.narrative.first'] = 'test'
    assert title_narrative_first(data) == expected_res

    data = {'title': {'narrative': ['first test', 'second test']}}
    expected_res = data.copy()
    expected_res['title.narrative.first'] = 'first test'
    assert title_narrative_first(data) == expected_res
