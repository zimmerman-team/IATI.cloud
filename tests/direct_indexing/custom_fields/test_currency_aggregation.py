import pytest
from pymongo.errors import PyMongoError
from pytest_mock_resources import create_mongo_fixture

from direct_indexing.custom_fields.currency_aggregation import (
    TVU_CLEAN, TVU_CLEAN_GBP, TVU_CLEAN_TYPE, TVU_CLEAN_TYPE_GBP, TVU_DASHES, TVU_DASHES_GBP, TVU_DASHES_TYPE,
    TVU_DASHES_TYPE_GBP, aggregate_converted_types, clean_aggregation_result, connect_to_mongo, currency_aggregation,
    get_aggregation_fields, get_aggregations, get_child_aggregations, get_currency, index_activity_data, prepare_data,
    process_activity_aggregations, process_budget_agg, process_child_agg_currencies, process_child_aggregations,
    process_planned_disbursement_agg, process_transaction_agg, process_transaction_currency_agg, refresh_mongo_data,
    revert_activity_tvu
)

mongo = create_mongo_fixture()


def test_currency_aggregation(mocker):
    # mock all the functions in currency_aggregation
    mock_prepare_data = mocker.patch('direct_indexing.custom_fields.currency_aggregation.prepare_data')  # NOQA: 501
    mock_connect_to_mongo = mocker.patch('direct_indexing.custom_fields.currency_aggregation.connect_to_mongo')  # NOQA: 501
    mock_get_aggregations = mocker.patch('direct_indexing.custom_fields.currency_aggregation.get_aggregations')  # NOQA: 501
    mock_get_aggregation_fields = mocker.patch('direct_indexing.custom_fields.currency_aggregation.get_aggregation_fields')  # NOQA: 501
    mock_index_activity_data = mocker.patch('direct_indexing.custom_fields.currency_aggregation.index_activity_data')  # NOQA: 501
    mock_process_activity_aggregations = mocker.patch('direct_indexing.custom_fields.currency_aggregation.process_activity_aggregations')  # NOQA: 501
    mock_refresh_mongo_data = mocker.patch('direct_indexing.custom_fields.currency_aggregation.refresh_mongo_data')  # NOQA: 501
    mock_get_child_aggregations = mocker.patch('direct_indexing.custom_fields.currency_aggregation.get_child_aggregations')  # NOQA: 501
    mock_process_child_aggregations = mocker.patch('direct_indexing.custom_fields.currency_aggregation.process_child_aggregations')  # NOQA: 501
    mock_clean_aggregation_result = mocker.patch('direct_indexing.custom_fields.currency_aggregation.clean_aggregation_result')  # NOQA: 501

    client_mock = mocker.MagicMock()
    mock_prepare_data.return_value = {}
    mock_connect_to_mongo.return_value = None, client_mock
    mock_get_aggregation_fields.return_value = {}, {}, {}, {}
    mock_process_activity_aggregations.return_value = {}
    mock_process_child_aggregations.return_value = {}
    mock_clean_aggregation_result.return_value = {}
    res = currency_aggregation({})

    # assert the mocks were all called once
    mock_prepare_data.assert_called_once()
    mock_connect_to_mongo.assert_called_once()
    mock_get_aggregations.assert_called_once()
    mock_get_aggregation_fields.assert_called_once()
    mock_index_activity_data.assert_called_once()
    mock_process_activity_aggregations.assert_called_once()
    mock_refresh_mongo_data.assert_called_once()
    mock_get_child_aggregations.assert_called_once()
    mock_process_child_aggregations.assert_called_once()
    mock_clean_aggregation_result.assert_called_once()
    client_mock.close.assert_called_once()
    assert res == {}

    mock_prepare_data.reset_mock()
    mock_prepare_data.side_effect = PyMongoError
    assert currency_aggregation({}) == [{}]


def test_prepare_data():
    # Data is a list of objects
    data = [{
        TVU_CLEAN: 0,
        TVU_CLEAN_TYPE: 1,
        TVU_CLEAN_GBP: 2,
        TVU_CLEAN_TYPE_GBP: 3
    }]
    expected_res = [{
        TVU_DASHES: 0,
        TVU_DASHES_TYPE: 1,
        TVU_DASHES_GBP: 2,
        TVU_DASHES_TYPE_GBP: 3,
    }]
    assert prepare_data(data) == expected_res


def test_connect_to_mongo(mocker):
    mongo_mocker = mocker.MagicMock()
    mock = mocker.patch('direct_indexing.custom_fields.currency_aggregation.MongoClient', return_value=mongo_mocker)

    connect_to_mongo([{}])
    mongo_mocker.activities.activity.drop.assert_called_once()
    mongo_mocker.activities.activity.insert_many.assert_called_once()

    mock.side_effect = PyMongoError
    with pytest.raises(PyMongoError):
        connect_to_mongo([{}])


def test_get_aggregations(mocker, fixture_activity_aggregations_res, fixture_aggregation_data):
    # # mock dba.aggregate to return a list of objects
    b_res = fixture_activity_aggregations_res['budget']
    t_res = fixture_activity_aggregations_res['transaction']
    p_res = fixture_activity_aggregations_res['planned-disbursement']
    mock_dba = mocker.MagicMock()
    mock_dba.aggregate.side_effect = [b_res, t_res, p_res]

    # Mock aggregate_converted_types
    mock_agg = mocker.patch('direct_indexing.custom_fields.currency_aggregation.aggregate_converted_types')
    mock_agg.return_value = []

    data = fixture_aggregation_data.copy()
    ex_res = fixture_activity_aggregations_res.copy()
    assert get_aggregations(mock_dba, data) == ex_res
    assert mock_dba.aggregate.call_count == 3
    assert mock_agg.call_count == 2


def test_aggregate_converted_types():
    curr = "USD"
    data = []
    assert aggregate_converted_types(data, curr) == []

    data = [
        {
            'iati-identifier': "test",
            'transaction-value-USD': [1, 1, 42, None],
            'transaction-value-USD-type': [1, 1, 2, 2],
        }
    ]
    expected_res = [
        {'_id': ['test', 1], 'transaction-value-USD-sum': 2},
        {'_id': ['test', 2], 'transaction-value-USD-sum': 42}
    ]
    assert aggregate_converted_types(data, curr) == expected_res


def test_get_aggregation_fields(fixture_af, fixture_faf, fixture_caf, fixture_ppcaf):
    assert get_aggregation_fields() == (fixture_af, fixture_faf, fixture_caf, fixture_ppcaf)


def test_index_activity_data():
    assert index_activity_data([]) == {}
    data = [
        {'iati-identifier': 'test1'},
        {},
        {'iati-identifier': 'test2'}
    ]
    # index of test1 is 0, index of test2 is 2
    assert index_activity_data(data) == {'test1': 0, 'test2': 2}


def test_process_activity_aggregations(mocker):
    # mock all functions in process_activity_aggregations
    mock_process_budget_agg = mocker.patch('direct_indexing.custom_fields.currency_aggregation.process_budget_agg')  # NOQA: 501
    mock_process_planned_disbursement_agg = mocker.patch('direct_indexing.custom_fields.currency_aggregation.process_planned_disbursement_agg')  # NOQA: 501
    mock_process_transaction_agg = mocker.patch('direct_indexing.custom_fields.currency_aggregation.process_transaction_agg')  # NOQA: 501
    mock_process_transaction_currency_agg = mocker.patch('direct_indexing.custom_fields.currency_aggregation.process_transaction_currency_agg')  # NOQA: 501
    process_activity_aggregations(None, {}, None, None)

    mock_process_budget_agg.assert_called_once()
    mock_process_planned_disbursement_agg.assert_called_once()
    mock_process_transaction_agg.assert_called_once()
    assert mock_process_transaction_currency_agg.call_count == 2


def test_refresh_mongo_data(mocker):
    mock = mocker.MagicMock()
    refresh_mongo_data(mock, None)
    mock.drop.assert_called_once()
    mock.insert_many.assert_called_once()


def test_get_child_aggregations(mocker):
    # This function receives the database with data, and the first result of get_aggregation_fields
    aggregation_fields, _, _, _ = get_aggregation_fields()
    dba = mocker.MagicMock()
    dba.aggregate.return_value = []

    # count the number of keys in aggregation_fields that are not currency
    n_keys = sum("currency" not in key for key in aggregation_fields)
    assert get_child_aggregations(dba, aggregation_fields) == []

    # assert that dba.aggregate was called with a list, the 3rd item's key is '$group',
    # and the group_object is a dict with n_keys + 1 length
    dba.aggregate.assert_called_once()
    assert len(dba.aggregate.call_args[0][0][2]['$group']) == n_keys + 1

    # We do not test the aggregate function of pymongo. We assume it works as intended.


def test_process_child_aggregations(mocker, fixture_simple_data_list_activity_with_child):
    """
    A very simple iati activity with a child activity
    """
    # mock process_child_agg_currencies
    mock_process_child_agg_currencies = mocker.patch('direct_indexing.custom_fields.currency_aggregation.process_child_agg_currencies')  # NOQA: 501
    # Sample of aggregation fields
    aggregation_fields = {"budget": "activity-aggregation-budget-value", "planned-disbursement": "activity-aggregation-planned-disbursement-value"}  # NOQA: 501
    child_aggregation_fields = {"budget": "child-aggregation-budget-value", "planned-disbursement": "child-aggregation-planned-disbursement-value"}  # NOQA: 501
    parent_plus_child_aggregation_fields = {"budget": "activity-plus-child-aggregation-budget-value", "planned-disbursement": "activity-plus-child-aggregation-planned-disbursement-value"}  # NOQA: 501
    activity_indexes = {"test1": 0, "test2": 1, "test3": 2}  # based on the fixture
    dba = mocker.MagicMock()
    dba.aggregate.return_value = [
        {'_id': 'test1', 'budget': 42, 'planned-disbursement': 0},
        {'_id': 'testNA', 'budget': 21, 'planned-disbursement': 0}
    ]
    data = fixture_simple_data_list_activity_with_child.copy()
    children_agg = get_child_aggregations(dba, aggregation_fields)
    res = process_child_aggregations(
        data,
        children_agg,
        activity_indexes,
        aggregation_fields,
        child_aggregation_fields,
        parent_plus_child_aggregation_fields
    )
    # once for budget, not for pd in test1, none for testNA as it is not in activity_indexes
    mock_process_child_agg_currencies.assert_called_once()
    # assert the first activity in res (test1), has child aggregation value for budget, but not for pd as it is 0
    assert res[0]['child-aggregation-budget-value'] == 42
    assert 'child-aggregation-planned-disbursement-value' not in res[0]
    # assert the child + parent together is 42 + 21 + 21
    assert res[0]['activity-plus-child-aggregation-budget-value'] == 84


def test_process_child_agg_currencies(mocker, fixture_simple_data_list_activity_with_child):
    # Taking the fixture data and assuming the first agg result for test 1 (budget value of 42)
    data = fixture_simple_data_list_activity_with_child.copy()
    key = 'budget'
    index_of_activity = 0
    child_aggregation_fields = {"budget": "child-aggregation-budget-value", "budget_currency": "child-aggregation-budget-currency"}  # NOQA: 501
    parent_plus_child_aggregation_fields = {"budget": "activity-plus-child-aggregation-budget-value", "budget_currency": "activity-plus-child-aggregation-budget-currency"}  # NOQA: 501

    # mock get_currency to return "USD"
    mock_get_currency = mocker.patch('direct_indexing.custom_fields.currency_aggregation.get_currency', return_value="USD")  # NOQA: 501
    process_child_agg_currencies(data, key, index_of_activity, child_aggregation_fields, parent_plus_child_aggregation_fields)  # NOQA: 501
    assert data[index_of_activity][child_aggregation_fields[key + "_currency"]] == "USD"
    assert data[index_of_activity][parent_plus_child_aggregation_fields[key + "_currency"]] == "USD"
    mock_get_currency.assert_called_once()


def test_get_currency():
    key = "budget"
    data = [{'budget.value-usd.conversion-currency': "CAD"}]
    assert get_currency(key, data, 0) == "CAD"
    data = [{'budget.value-gbp.conversion-currency': "CAD"}]
    assert get_currency(key, data, 0) == "CAD"
    key = "planned-disbursement"
    data = [{'planned-disbursement.value-usd.conversion-currency': "CAD"}]
    assert get_currency(key, data, 0) == "CAD"
    data = [{'planned-disbursement.value-gbp.conversion-currency': "CAD"}]
    assert get_currency(key, data, 0) == "CAD"
    key = "transaction"
    data = [{'transaction.value-usd.conversion-currency': "CAD"}]
    assert get_currency(key, data, 0) == "CAD"
    data = [{'transaction.value-gbp.conversion-currency': "CAD"}]
    assert get_currency(key, data, 0) == "CAD"


def test_clean_aggregation_result():
    aggregation_fields, formatted_aggregation_fields, _, _ = get_aggregation_fields()
    data = [
        {
            '_id': None,
        },
        {
            'activity-aggregation-budget-value': 42
        }
    ]
    res = clean_aggregation_result(data, aggregation_fields, formatted_aggregation_fields)
    assert '_id' not in res[0]
    assert 'activity-aggregation-budget-value' not in res[1]
    assert res[1]['activity-aggregation.budget.value'] == 42


def test_revert_activity_tvu():
    activity = {
        TVU_DASHES: 1,
        TVU_DASHES_TYPE: 2,
        TVU_DASHES_GBP: 3,
        TVU_DASHES_TYPE_GBP: 4,
    }
    ex_res = {
        TVU_CLEAN: 1,
        TVU_CLEAN_TYPE: 2,
        TVU_CLEAN_GBP: 3,
        TVU_CLEAN_TYPE_GBP: 4,
    }
    assert revert_activity_tvu(activity) == ex_res


def test_process_budget_agg():
    data = [
        {
            'iati-identifier': 'test1',
            'budget.value-usd.sum': 42,
            'budget.value-gbp.sum': 42,
            'budget.value-usd.conversion-currency': 'USD'
        }
    ]
    # Test that the correct values are appended to the correct data entry
    ex_res = data.copy()
    ex_res[0]['activity-aggregation-budget-value'] = 42
    ex_res[0]['activity-aggregation-budget-value-usd'] = 42
    ex_res[0]['activity-aggregation-budget-value-gbp'] = 42
    budget_agg = [{'_id': 'test1', 'budget-value-sum': 42}, {'_id': 'testNA', 'budget-value-sum': 21}]
    activity_indexes = {'test1': 0}
    aggregation_fields, _, _, _ = get_aggregation_fields()
    process_budget_agg(budget_agg, activity_indexes, aggregation_fields, data)
    assert data == ex_res


def test_process_planned_disbursement_agg():
    data = [
        {
            'iati-identifier': 'test1',
            'planned-disbursement.value-usd.sum': 42,
            'planned-disbursement.value-gbp.sum': 42,
            'planned-disbursement.value-usd.conversion-currency': 'USD',
            'planned-disbursement.value-gbp.conversion-currency': 'USD'
        }
    ]
    # Test that the correct values are appended to the correct data entry
    ex_res = data.copy()
    ex_res[0]['activity-aggregation-planned-disbursement-value'] = 42
    ex_res[0]['activity-aggregation-planned-disbursement-value-usd'] = 42
    ex_res[0]['activity-aggregation-planned-disbursement-value-gbp'] = 42
    pd_agg = [{'_id': 'test1', 'planned-disbursement-value-sum': 42}, {'_id': 'testNA', 'planned-disbursement-value-sum': 21}]  # NOQA: 501
    activity_indexes = {'test1': 0}
    aggregation_fields, _, _, _ = get_aggregation_fields()
    process_planned_disbursement_agg(pd_agg, activity_indexes, aggregation_fields, data)
    assert data == ex_res


def test_process_transaction_agg():
    data = [
        {
            'iati-identifier': 'test1',
        },
        {
            'iati-identifier': 'test2',
        }
    ]
    transaction_agg = [
        {'_id': ('test1', 3), 'transaction-value-sum': 42},
        {'_id': ('test2', '2'), 'transaction-value-sum': 42},
        {'_id': ('testNA', 1)}
    ]
    activity_indexes = {'test1': 0, 'test2': 1}
    aggregation_fields, _, _, _ = get_aggregation_fields()
    process_transaction_agg(transaction_agg, activity_indexes, aggregation_fields, data)
    assert data[0]['activity-aggregation-disbursement-value'] == 42
    assert 'activity-aggregation-outgoing-commitment-value' not in data[1]


def test_process_transaction_currency_agg():
    # sample usage
    transaction_usd_agg = [
        {'_id': ('test1', 3), 'transaction-value-usd-sum': 42, 'transaction-value-gbp-sum': 42},
        {'_id': ('test2', '2'), 'transaction-value-usd-sum': 42},
        {'_id': ('test3', None), 'transaction-value-usd-sum': 42},
        {'_id': ('testNA', 1)}
    ]
    activity_indexes = {'test1': 0, 'test2': 1, 'test3': 2}
    aggregation_fields, _, _, _ = get_aggregation_fields()
    data = [
        {
            'iati-identifier': 'test1',
            'transaction.value-usd.conversion-currency': 'USD',
            'transaction-value-usd-conversion-currency': 'USD',
            'transaction.value-gbp.conversion-currency': 'GBP',
            'transaction-value-gbp-conversion-currency': 'GBP'
        },
        {
            'iati-identifier': 'test2',
        },
        {
            'iati-identifier': 'test3',
        }
    ]

    process_transaction_currency_agg(transaction_usd_agg, activity_indexes, aggregation_fields, data, 'usd')
    assert data[0]['activity-aggregation-disbursement-value-usd'] == 42
    assert 'activity-aggregation-outgoing-commitment-value-usd' not in data[1]
    assert len(data[2].keys()) == 1

    process_transaction_currency_agg(transaction_usd_agg, activity_indexes, aggregation_fields, data, 'gbp')
    assert data[0]['activity-aggregation-disbursement-value-gbp'] == 42
    assert data[0]['activity-aggregation-disbursement-value-usd'] == 42


@pytest.fixture
def fixture_af():
    return {'budget': 'activity-aggregation-budget-value', 'budget_usd': 'activity-aggregation-budget-value-usd', 'budget_gbp': 'activity-aggregation-budget-value-gbp', 'budget_currency': 'activity-aggregation-budget-currency', 'planned_disbursement': 'activity-aggregation-planned-disbursement-value', 'planned_disbursement_usd': 'activity-aggregation-planned-disbursement-value-usd', 'planned_disbursement_gbp': 'activity-aggregation-planned-disbursement-value-gbp', 'planned_disbursement_currency': 'activity-aggregation-planned-disbursement-currency', 'incoming_funds': 'activity-aggregation-incoming-funds-value', 'incoming_funds_usd': 'activity-aggregation-incoming-funds-value-usd', 'incoming_funds_gbp': 'activity-aggregation-incoming-funds-value-gbp', 'incoming_funds_currency': 'activity-aggregation-incoming-funds-currency', 'outgoing_commitment': 'activity-aggregation-outgoing-commitment-value', 'outgoing_commitment_usd': 'activity-aggregation-outgoing-commitment-value-usd', 'outgoing_commitment_gbp': 'activity-aggregation-outgoing-commitment-value-gbp', 'outgoing_commitment_currency': 'activity-aggregation-outgoing-commitment-currency', 'disbursement': 'activity-aggregation-disbursement-value', 'disbursement_usd': 'activity-aggregation-disbursement-value-usd', 'disbursement_gbp': 'activity-aggregation-disbursement-value-gbp', 'disbursement_currency': 'activity-aggregation-disbursement-currency', 'expenditure': 'activity-aggregation-expenditure-value', 'expenditure_usd': 'activity-aggregation-expenditure-value-usd', 'expenditure_gbp': 'activity-aggregation-expenditure-value-gbp', 'expenditure_currency': 'activity-aggregation-expenditure-currency', 'interest_payment': 'activity-aggregation-interest-payment-value', 'interest_payment_usd': 'activity-aggregation-interest-payment-value-usd', 'interest_payment_gbp': 'activity-aggregation-interest-payment-value-gbp', 'interest_payment_currency': 'activity-aggregation-interest-payment-currency', 'loan_repayment': 'activity-aggregation-loan-repayment-value', 'loan_repayment_usd': 'activity-aggregation-loan-repayment-value-usd', 'loan_repayment_gbp': 'activity-aggregation-loan-repayment-value-gbp', 'loan_repayment_currency': 'activity-aggregation-loan-repayment-currency', 'reimbursement': 'activity-aggregation-reimbursement-value', 'reimbursement_usd': 'activity-aggregation-reimbursement-value-usd', 'reimbursement_gbp': 'activity-aggregation-reimbursement-value-gbp', 'reimbursement_currency': 'activity-aggregation-reimbursement-currency', 'purchase_of_equity': 'activity-aggregation-purchase-of-equity-value', 'purchase_of_equity_usd': 'activity-aggregation-purchase-of-equity-value-usd', 'purchase_of_equity_gbp': 'activity-aggregation-purchase-of-equity-value-gbp', 'purchase_of_equity_currency': 'activity-aggregation-purchase-of-equity-currency', 'sale_of_equity': 'activity-aggregation-sale-of-equity-value', 'sale_of_equity_usd': 'activity-aggregation-sale-of-equity-value-usd', 'sale_of_equity_gbp': 'activity-aggregation-sale-of-equity-value-gbp', 'sale_of_equity_currency': 'activity-aggregation-sale-of-equity-currency', 'credit_guarantee': 'activity-aggregation-credit-guarantee-value', 'credit_guarantee_usd': 'activity-aggregation-credit-guarantee-value-usd', 'credit_guarantee_gbp': 'activity-aggregation-credit-guarantee-value-gbp', 'credit_guarantee_currency': 'activity-aggregation-credit-guarantee-currency', 'incoming_commitment': 'activity-aggregation-incoming-commitment-value', 'incoming_commitment_usd': 'activity-aggregation-incoming-commitment-value-usd', 'incoming_commitment_gbp': 'activity-aggregation-incoming-commitment-value-gbp', 'incoming_commitment_currency': 'activity-aggregation-incoming-commitment-currency', 'outgoing_pledge': 'activity-aggregation-outgoing-pledge-value', 'outgoing_pledge_usd': 'activity-aggregation-outgoing-pledge-value-usd', 'outgoing_pledge_gbp': 'activity-aggregation-outgoing-pledge-value-gbp', 'outgoing_pledge_currency': 'activity-aggregation-outgoing-pledge-currency', 'incoming_pledge': 'activity-aggregation-incoming-pledge-value', 'incoming_pledge_usd': 'activity-aggregation-incoming-pledge-value-usd', 'incoming_pledge_gbp': 'activity-aggregation-incoming-pledge-value-gbp', 'incoming_pledge_currency': 'activity-aggregation-incoming-pledge-currency'}  # NOQA: 501


@pytest.fixture
def fixture_faf():
    return {'budget': 'activity-aggregation.budget.value', 'budget_usd': 'activity-aggregation.budget.value-usd', 'budget_gbp': 'activity-aggregation.budget.value-gbp', 'budget_currency': 'activity-aggregation.budget.currency', 'planned_disbursement': 'activity-aggregation.planned-disbursement.value', 'planned_disbursement_usd': 'activity-aggregation.planned-disbursement.value-usd', 'planned_disbursement_gbp': 'activity-aggregation.planned-disbursement.value-gbp', 'planned_disbursement_currency': 'activity-aggregation.planned-disbursement.currency', 'incoming_funds': 'activity-aggregation.incoming-funds.value', 'incoming_funds_usd': 'activity-aggregation.incoming-funds.value-usd', 'incoming_funds_gbp': 'activity-aggregation.incoming-funds.value-gbp', 'incoming_funds_currency': 'activity-aggregation.incoming-funds.currency', 'outgoing_commitment': 'activity-aggregation.outgoing-commitment.value', 'outgoing_commitment_usd': 'activity-aggregation.outgoing-commitment.value-usd', 'outgoing_commitment_gbp': 'activity-aggregation.outgoing-commitment.value-gbp', 'outgoing_commitment_currency': 'activity-aggregation.outgoing-commitment.currency', 'disbursement': 'activity-aggregation.disbursement.value', 'disbursement_usd': 'activity-aggregation.disbursement.value-usd', 'disbursement_gbp': 'activity-aggregation.disbursement.value-gbp', 'disbursement_currency': 'activity-aggregation.disbursement.currency', 'expenditure': 'activity-aggregation.expenditure.value', 'expenditure_usd': 'activity-aggregation.expenditure.value-usd', 'expenditure_gbp': 'activity-aggregation.expenditure.value-gbp', 'expenditure_currency': 'activity-aggregation.expenditure.currency', 'interest_payment': 'activity-aggregation.interest-payment.value', 'interest_payment_usd': 'activity-aggregation.interest-payment.value-usd', 'interest_payment_gbp': 'activity-aggregation.interest-payment.value-gbp', 'interest_payment_currency': 'activity-aggregation.interest-payment.currency', 'loan_repayment': 'activity-aggregation.loan-repayment.value', 'loan_repayment_usd': 'activity-aggregation.loan-repayment.value-usd', 'loan_repayment_gbp': 'activity-aggregation.loan-repayment.value-gbp', 'loan_repayment_currency': 'activity-aggregation.loan-repayment.currency', 'reimbursement': 'activity-aggregation.reimbursement.value', 'reimbursement_usd': 'activity-aggregation.reimbursement.value-usd', 'reimbursement_gbp': 'activity-aggregation.reimbursement.value-gbp', 'reimbursement_currency': 'activity-aggregation.reimbursement.currency', 'purchase_of_equity': 'activity-aggregation.purchase-of-equity.value', 'purchase_of_equity_usd': 'activity-aggregation.purchase-of-equity.value-usd', 'purchase_of_equity_gbp': 'activity-aggregation.purchase-of-equity.value-gbp', 'purchase_of_equity_currency': 'activity-aggregation.purchase-of-equity.currency', 'sale_of_equity': 'activity-aggregation.sale-of-equity.value', 'sale_of_equity_usd': 'activity-aggregation.sale-of-equity.value-usd', 'sale_of_equity_gbp': 'activity-aggregation.sale-of-equity.value-gbp', 'sale_of_equity_currency': 'activity-aggregation.sale-of-equity.currency', 'credit_guarantee': 'activity-aggregation.credit-guarantee.value', 'credit_guarantee_usd': 'activity-aggregation.credit-guarantee.value-usd', 'credit_guarantee_gbp': 'activity-aggregation.credit-guarantee.value-gbp', 'credit_guarantee_currency': 'activity-aggregation.credit-guarantee.currency', 'incoming_commitment': 'activity-aggregation.incoming-commitment.value', 'incoming_commitment_usd': 'activity-aggregation.incoming-commitment.value-usd', 'incoming_commitment_gbp': 'activity-aggregation.incoming-commitment.value-gbp', 'incoming_commitment_currency': 'activity-aggregation.incoming-commitment.currency', 'outgoing_pledge': 'activity-aggregation.outgoing-pledge.value', 'outgoing_pledge_usd': 'activity-aggregation.outgoing-pledge.value-usd', 'outgoing_pledge_gbp': 'activity-aggregation.outgoing-pledge.value-gbp', 'outgoing_pledge_currency': 'activity-aggregation.outgoing-pledge.currency', 'incoming_pledge': 'activity-aggregation.incoming-pledge.value', 'incoming_pledge_usd': 'activity-aggregation.incoming-pledge.value-usd', 'incoming_pledge_gbp': 'activity-aggregation.incoming-pledge.value-gbp', 'incoming_pledge_currency': 'activity-aggregation.incoming-pledge.currency'}  # NOQA: 501


@pytest.fixture
def fixture_caf():
    return {'budget': 'child-aggregation.budget.value', 'budget_usd': 'child-aggregation.budget.value-usd', 'budget_gbp': 'child-aggregation.budget.value-gbp', 'budget_currency': 'child-aggregation.budget.currency', 'planned_disbursement': 'child-aggregation.planned-disbursement.value', 'planned_disbursement_usd': 'child-aggregation.planned-disbursement.value-usd', 'planned_disbursement_gbp': 'child-aggregation.planned-disbursement.value-gbp', 'planned_disbursement_currency': 'child-aggregation.planned-disbursement.currency', 'incoming_funds': 'child-aggregation.incoming-funds.value', 'incoming_funds_usd': 'child-aggregation.incoming-funds.value-usd', 'incoming_funds_gbp': 'child-aggregation.incoming-funds.value-gbp', 'incoming_funds_currency': 'child-aggregation.incoming-funds.currency', 'outgoing_commitment': 'child-aggregation.outgoing-commitment.value', 'outgoing_commitment_usd': 'child-aggregation.outgoing-commitment.value-usd', 'outgoing_commitment_gbp': 'child-aggregation.outgoing-commitment.value-gbp', 'outgoing_commitment_currency': 'child-aggregation.outgoing-commitment.currency', 'disbursement': 'child-aggregation.disbursement.value', 'disbursement_usd': 'child-aggregation.disbursement.value-usd', 'disbursement_gbp': 'child-aggregation.disbursement.value-gbp', 'disbursement_currency': 'child-aggregation.disbursement.currency', 'expenditure': 'child-aggregation.expenditure.value', 'expenditure_usd': 'child-aggregation.expenditure.value-usd', 'expenditure_gbp': 'child-aggregation.expenditure.value-gbp', 'expenditure_currency': 'child-aggregation.expenditure.currency', 'interest_payment': 'child-aggregation.interest-payment.value', 'interest_payment_usd': 'child-aggregation.interest-payment.value-usd', 'interest_payment_gbp': 'child-aggregation.interest-payment.value-gbp', 'interest_payment_currency': 'child-aggregation.interest-payment.currency', 'loan_repayment': 'child-aggregation.loan-repayment.value', 'loan_repayment_usd': 'child-aggregation.loan-repayment.value-usd', 'loan_repayment_gbp': 'child-aggregation.loan-repayment.value-gbp', 'loan_repayment_currency': 'child-aggregation.loan-repayment.currency', 'reimbursement': 'child-aggregation.reimbursement.value', 'reimbursement_usd': 'child-aggregation.reimbursement.value-usd', 'reimbursement_gbp': 'child-aggregation.reimbursement.value-gbp', 'reimbursement_currency': 'child-aggregation.reimbursement.currency', 'purchase_of_equity': 'child-aggregation.purchase-of-equity.value', 'purchase_of_equity_usd': 'child-aggregation.purchase-of-equity.value-usd', 'purchase_of_equity_gbp': 'child-aggregation.purchase-of-equity.value-gbp', 'purchase_of_equity_currency': 'child-aggregation.purchase-of-equity.currency', 'sale_of_equity': 'child-aggregation.sale-of-equity.value', 'sale_of_equity_usd': 'child-aggregation.sale-of-equity.value-usd', 'sale_of_equity_gbp': 'child-aggregation.sale-of-equity.value-gbp', 'sale_of_equity_currency': 'child-aggregation.sale-of-equity.currency', 'credit_guarantee': 'child-aggregation.credit-guarantee.value', 'credit_guarantee_usd': 'child-aggregation.credit-guarantee.value-usd', 'credit_guarantee_gbp': 'child-aggregation.credit-guarantee.value-gbp', 'credit_guarantee_currency': 'child-aggregation.credit-guarantee.currency', 'incoming_commitment': 'child-aggregation.incoming-commitment.value', 'incoming_commitment_usd': 'child-aggregation.incoming-commitment.value-usd', 'incoming_commitment_gbp': 'child-aggregation.incoming-commitment.value-gbp', 'incoming_commitment_currency': 'child-aggregation.incoming-commitment.currency', 'outgoing_pledge': 'child-aggregation.outgoing-pledge.value', 'outgoing_pledge_usd': 'child-aggregation.outgoing-pledge.value-usd', 'outgoing_pledge_gbp': 'child-aggregation.outgoing-pledge.value-gbp', 'outgoing_pledge_currency': 'child-aggregation.outgoing-pledge.currency', 'incoming_pledge': 'child-aggregation.incoming-pledge.value', 'incoming_pledge_usd': 'child-aggregation.incoming-pledge.value-usd', 'incoming_pledge_gbp': 'child-aggregation.incoming-pledge.value-gbp', 'incoming_pledge_currency': 'child-aggregation.incoming-pledge.currency'}  # NOQA: 501


@pytest.fixture
def fixture_ppcaf():
    return {'budget': 'activity-plus-child-aggregation.budget.value', 'budget_usd': 'activity-plus-child-aggregation.budget.value-usd', 'budget_gbp': 'activity-plus-child-aggregation.budget.value-gbp', 'budget_currency': 'activity-plus-child-aggregation.budget.currency', 'planned_disbursement': 'activity-plus-child-aggregation.planned-disbursement.value', 'planned_disbursement_usd': 'activity-plus-child-aggregation.planned-disbursement.value-usd', 'planned_disbursement_gbp': 'activity-plus-child-aggregation.planned-disbursement.value-gbp', 'planned_disbursement_currency': 'activity-plus-child-aggregation.planned-disbursement.currency', 'incoming_funds': 'activity-plus-child-aggregation.incoming-funds.value', 'incoming_funds_usd': 'activity-plus-child-aggregation.incoming-funds.value-usd', 'incoming_funds_gbp': 'activity-plus-child-aggregation.incoming-funds.value-gbp', 'incoming_funds_currency': 'activity-plus-child-aggregation.incoming-funds.currency', 'outgoing_commitment': 'activity-plus-child-aggregation.outgoing-commitment.value', 'outgoing_commitment_usd': 'activity-plus-child-aggregation.outgoing-commitment.value-usd', 'outgoing_commitment_gbp': 'activity-plus-child-aggregation.outgoing-commitment.value-gbp', 'outgoing_commitment_currency': 'activity-plus-child-aggregation.outgoing-commitment.currency', 'disbursement': 'activity-plus-child-aggregation.disbursement.value', 'disbursement_usd': 'activity-plus-child-aggregation.disbursement.value-usd', 'disbursement_gbp': 'activity-plus-child-aggregation.disbursement.value-gbp', 'disbursement_currency': 'activity-plus-child-aggregation.disbursement.currency', 'expenditure': 'activity-plus-child-aggregation.expenditure.value', 'expenditure_usd': 'activity-plus-child-aggregation.expenditure.value-usd', 'expenditure_gbp': 'activity-plus-child-aggregation.expenditure.value-gbp', 'expenditure_currency': 'activity-plus-child-aggregation.expenditure.currency', 'interest_payment': 'activity-plus-child-aggregation.interest-payment.value', 'interest_payment_usd': 'activity-plus-child-aggregation.interest-payment.value-usd', 'interest_payment_gbp': 'activity-plus-child-aggregation.interest-payment.value-gbp', 'interest_payment_currency': 'activity-plus-child-aggregation.interest-payment.currency', 'loan_repayment': 'activity-plus-child-aggregation.loan-repayment.value', 'loan_repayment_usd': 'activity-plus-child-aggregation.loan-repayment.value-usd', 'loan_repayment_gbp': 'activity-plus-child-aggregation.loan-repayment.value-gbp', 'loan_repayment_currency': 'activity-plus-child-aggregation.loan-repayment.currency', 'reimbursement': 'activity-plus-child-aggregation.reimbursement.value', 'reimbursement_usd': 'activity-plus-child-aggregation.reimbursement.value-usd', 'reimbursement_gbp': 'activity-plus-child-aggregation.reimbursement.value-gbp', 'reimbursement_currency': 'activity-plus-child-aggregation.reimbursement.currency', 'purchase_of_equity': 'activity-plus-child-aggregation.purchase-of-equity.value', 'purchase_of_equity_usd': 'activity-plus-child-aggregation.purchase-of-equity.value-usd', 'purchase_of_equity_gbp': 'activity-plus-child-aggregation.purchase-of-equity.value-gbp', 'purchase_of_equity_currency': 'activity-plus-child-aggregation.purchase-of-equity.currency', 'sale_of_equity': 'activity-plus-child-aggregation.sale-of-equity.value', 'sale_of_equity_usd': 'activity-plus-child-aggregation.sale-of-equity.value-usd', 'sale_of_equity_gbp': 'activity-plus-child-aggregation.sale-of-equity.value-gbp', 'sale_of_equity_currency': 'activity-plus-child-aggregation.sale-of-equity.currency', 'credit_guarantee': 'activity-plus-child-aggregation.credit-guarantee.value', 'credit_guarantee_usd': 'activity-plus-child-aggregation.credit-guarantee.value-usd', 'credit_guarantee_gbp': 'activity-plus-child-aggregation.credit-guarantee.value-gbp', 'credit_guarantee_currency': 'activity-plus-child-aggregation.credit-guarantee.currency', 'incoming_commitment': 'activity-plus-child-aggregation.incoming-commitment.value', 'incoming_commitment_usd': 'activity-plus-child-aggregation.incoming-commitment.value-usd', 'incoming_commitment_gbp': 'activity-plus-child-aggregation.incoming-commitment.value-gbp', 'incoming_commitment_currency': 'activity-plus-child-aggregation.incoming-commitment.currency', 'outgoing_pledge': 'activity-plus-child-aggregation.outgoing-pledge.value', 'outgoing_pledge_usd': 'activity-plus-child-aggregation.outgoing-pledge.value-usd', 'outgoing_pledge_gbp': 'activity-plus-child-aggregation.outgoing-pledge.value-gbp', 'outgoing_pledge_currency': 'activity-plus-child-aggregation.outgoing-pledge.currency', 'incoming_pledge': 'activity-plus-child-aggregation.incoming-pledge.value', 'incoming_pledge_usd': 'activity-plus-child-aggregation.incoming-pledge.value-usd', 'incoming_pledge_gbp': 'activity-plus-child-aggregation.incoming-pledge.value-gbp', 'incoming_pledge_currency': 'activity-plus-child-aggregation.incoming-pledge.currency'}  # NOQA: 501


@pytest.fixture
def fixture_activity_aggregations_res():
    b_res = [{'_id': None, 'budget-value-sum': 126}]
    t_res = [{'_id': [None, 1], 'transaction-value-sum': 84},
             {'_id': [None, 2], 'transaction-value-sum': 42}]
    p_res = [{'_id': None, 'planned-disbursement-value-sum': 126}]

    return {
        'budget': b_res,
        'transaction': t_res,
        'transaction-usd': [],
        'transaction-gbp': [],
        'planned-disbursement': p_res
    }


@pytest.fixture
def fixture_aggregation_data():
    budget_data = [{'iati-identifier': 'test1', 'budget': [{'value': 42}, {'value': 42}]}, {'iati-identifier': 'test1', 'budget': [{'value': 21}, {'value': 21}]}]  # NOQA: 501
    transaction_data = [{'iati-identifier': 'test1', 'transaction': [{'value': 42, 'transaction-type': {'code': 1}}, {'value': 42, 'transaction-type': {'code': 1}}]}, {'iati-identifier': 'test1', 'transaction': [{'value': 21, 'transaction-type': {'code': 2}}, {'value': 21, 'transaction-type': {'code': 2}}]}]  # NOQA: 501
    pd_data = [{'iati-identifier': 'test1', 'planned-disbursement': [{'value': 42}, {'value': 42}]}, {'iati-identifier': 'test1', 'planned-disbursement': [{'value': 21}, {'value': 21}]}]  # NOQA: 501
    data = budget_data + transaction_data + pd_data
    return data


@pytest.fixture
def fixture_simple_data_list_activity_with_child():
    # At this time in the processing, the activity objects are updated with the aggregated values
    # A budget value is also provided as activity-aggregation-budget-value
    return [
        {
            "iati-identifier": "test1",
            "budget": [
                {
                    "value": 42,
                    "value-date": "2019-01-01",
                }
            ],
            "related-activity": [
                {'ref': 'test2', 'type': 2},
                {'ref': 'test3', 'type': 2},
            ],
            "activity-aggregation-budget-value": 42
        },
        {
            "iati-identifier": "test2",
            "budget": [
                {
                    "value": 21,
                    "value-date": "2019-01-01",
                }
            ],
            "related-activity": [
                {'ref': 'test1', 'type': 1},
            ],
            "activity-aggregation-budget-value": 21
        },
        {
            "iati-identifier": "test3",
            "budget": [
                {
                    "value": 21,
                    "value-date": "2019-01-01",
                }
            ],
            "related-activity": [
                {'ref': 'test1', 'type': 1},
            ],
            "activity-aggregation-budget-value": 21
        },
        {
            "iati-identifier": "test4",
            "budget": [
                {
                    "value": 21,
                    "value-date": "2019-01-01",
                }
            ],
            "related-activity": [
                {'ref': 'testNA', 'type': 1},
            ],
            "activity-aggregation-budget-value": 21
        }
    ]


@pytest.fixture
def fixture_simple_data_list_activity_with_child_aggregated():
    return [
        {
            "_id": "test2",  # Grouped by "related-activity.ref"
            "budget_value": 21,  # Sum of "activity-aggregation-budget-value" for related-activity.type: 1
        },
        {
            "_id": "test3",  # Grouped by "related-activity.ref"
            "budget_value": 21,  # Sum of "activity-aggregation-budget-value" for related-activity.type: 1
        },
        {
            "_id": "test1",
            "budget_value": 42,
        }
    ]
