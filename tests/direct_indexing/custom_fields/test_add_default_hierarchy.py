from direct_indexing.custom_fields.add_default_hierarchy import add_default_hierarchy


def test_add_default_hierarchy():
    default_res = {'hierarchy': 1}
    data = {}
    add_default_hierarchy(data)
    assert data == default_res

    data = {'hierarchy': 2}
    add_default_hierarchy(data)
    assert data != default_res
