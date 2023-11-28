from direct_indexing.custom_fields.custom_fields import add_all, get_custom_metadata, process_activity

FCDO_IN = 'direct_indexing.custom_fields.custom_fields.settings.FCDO_INSTANCE'


def test_add_all(mocker):
    mock_pa = mocker.patch('direct_indexing.custom_fields.custom_fields.process_activity')
    mock_ca = mocker.patch('direct_indexing.custom_fields.custom_fields.currency_aggregation')
    mock_h2 = mocker.patch('direct_indexing.custom_fields.custom_fields.raise_h2_budget_data_to_h1')
    mock = mocker.MagicMock()
    # Test that the h2 function is not called when fcdo instance is false,
    # and that the process_activity and currency_aggregation functions are called once
    mocker.patch(FCDO_IN, False)
    data = {}
    add_all(data, mock, mock, {})
    mock_pa.assert_called_once()
    mock_ca.assert_called_once()
    mock_h2.assert_not_called()

    # Test that the process_activity function is called len(data) times
    data = [{}, {}]
    add_all(data, mock, mock, {})
    assert mock_pa.call_count == len(data) + 1  # +1 for the previous test

    # Test that the h2 function is called when fcdo instance is true
    mocker.patch(FCDO_IN, True)
    data = {}
    add_all(data, mock, mock, {})
    mock_h2.assert_called_once()


def test_process_activity(mocker):
    # patch all subfunctions
    mock_ac = mocker.patch('direct_indexing.custom_fields.custom_fields.add_codelist_fields')
    mock_tn = mocker.patch('direct_indexing.custom_fields.custom_fields.title_narrative_first')
    mock_ad = mocker.patch('direct_indexing.custom_fields.custom_fields.activity_dates')
    mock_pm = mocker.patch('direct_indexing.custom_fields.custom_fields.policy_marker_combined')
    mock_cc = mocker.patch('direct_indexing.custom_fields.custom_fields.currency_conversion')
    mock_am = mocker.patch('direct_indexing.custom_fields.custom_fields.add_meta_to_activity')
    mock_adh = mocker.patch('direct_indexing.custom_fields.custom_fields.add_default_hierarchy')
    mock_ajd = mocker.patch('direct_indexing.custom_fields.custom_fields.add_json_dumps')
    mock_adq = mocker.patch('direct_indexing.custom_fields.custom_fields.add_date_quarter_fields')
    mock_dlcc = mocker.patch('direct_indexing.custom_fields.custom_fields.document_link_category_combined')
    mock = mocker.MagicMock()

    # Test that all subfunctions are called once
    mocker.patch(FCDO_IN, False)
    activity = {}
    process_activity(activity, mock, mock, {})
    mock_ac.assert_called_once()
    mock_tn.assert_called_once()
    mock_ad.assert_called_once()
    mock_pm.assert_called_once()
    mock_cc.assert_called_once()
    mock_am.assert_called_once()
    mock_adh.assert_called_once()
    # test that the others are not called
    mock_ajd.assert_not_called()
    mock_adq.assert_not_called()
    mock_dlcc.assert_not_called()

    # Test that the remaining functions are called when FCDO_INSTANCE is True
    mocker.patch(FCDO_IN, True)
    process_activity(activity, mock, mock, {})
    mock_ajd.assert_called_once()
    mock_adq.assert_called_once()
    mock_dlcc.assert_called_once()


def test_get_custom_metadata(mocker):
    mock_dm = mocker.patch('direct_indexing.custom_fields.custom_fields.dataset_metadata')
    get_custom_metadata(None)
    mock_dm.assert_called_once()
