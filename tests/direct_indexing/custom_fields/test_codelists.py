import pytest

from direct_indexing.custom_fields.codelists import (
    CODELIST_POSTFIX, add_codelist_fields, check_and_get, extract_list_field, extract_nested_list_field,
    extract_single_field
)
from direct_indexing.custom_fields.models import codelists


def test_add_codelist_fields(mocker):
    # mock extract_single_field, extract_list_field, extract_nested_list_field
    mock_extract_single = mocker.patch('direct_indexing.custom_fields.codelists.extract_single_field')
    mock_extract_list = mocker.patch('direct_indexing.custom_fields.codelists.extract_list_field')
    mock_extract_nested_list = mocker.patch('direct_indexing.custom_fields.codelists.extract_nested_list_field')

    add_codelist_fields({}, {})
    mock_extract_single.assert_called_once()
    assert mock_extract_list.call_count == 10
    mock_extract_nested_list.assert_called_once()


def test_extract_single_field(fixture_cl):
    field_name = 'reporting-org'
    field_type = 'type'
    cl_name = 'OrganisationType'

    # Test data is not changed if field_name not in data
    data = {}
    data = extract_single_field(data, field_name, field_type, cl_name, fixture_cl)
    assert data == {}

    # Test data is not changed if field_type not in data[field_name]
    data = {field_name: {}}
    data = extract_single_field(data, field_name, field_type, cl_name, fixture_cl)
    assert data == {field_name: {}}

    # Test getting a single field
    data = {field_name: {field_type: "10"}}
    data = extract_single_field(data, field_name, field_type, cl_name, fixture_cl)
    assert data == {field_name: {field_type: "10"}, 'reporting-org.type.name': 'Government'}


def test_extract_list_field(fixture_cl):
    # Test extact list field with custom field name
    field_name = 'policy-marker'
    field_type = 'code'
    cl_name = 'PolicyMarkerVocabulary'
    custom_name = 'policy-marker.vocabulary'
    data_field = custom_name + CODELIST_POSTFIX
    data = {field_name: {field_type: "1"}}
    expected_res = {field_name: {field_type: "1"}, data_field: ['OECD DAC CRS']}
    extract_list_field(data, field_name, field_type, cl_name, fixture_cl, custom_name)
    assert data == expected_res

    # Test extract list field without custom field name
    field_name = 'recipient-country'
    field_type = 'code'
    cl_name = 'Country'
    data_field = field_name + CODELIST_POSTFIX
    expected_res = {field_name: {field_type: 'AF'}, data_field: ['Afghanistan']}
    data = {field_name: {field_type: 'AF'}}
    data = extract_list_field(data, field_name, field_type, cl_name, fixture_cl, None)
    assert data == expected_res

    # Test field name is not in data
    expected_res = {data_field: []}
    data = {}
    data = extract_list_field(data, field_name, field_type, cl_name, fixture_cl)
    assert data == expected_res

    # Test data[field_name] is list
    data = {field_name: [{field_type: 'AF'}, {field_type: 'AL'}]}
    data = extract_list_field(data, field_name, field_type, cl_name, fixture_cl)
    expected_res = {field_name: [{field_type: 'AF'}, {field_type: 'AL'}], data_field: ['Afghanistan', 'Albania']}
    assert data == expected_res


def test_extract_nested_list_field(mocker, fixture_cl):
    parent_field_name = 'transaction'
    field_name = 'receiver-org'
    field_type = 'type'
    cl_name = 'OrganisationType'
    data_field = f'{parent_field_name}.{field_name}.{field_type}{CODELIST_POSTFIX}'

    # Test that the data_field is initialised and returned if no data
    data = {}
    expected_res = {data_field: []}
    data = extract_nested_list_field(data, parent_field_name, field_name, field_type, cl_name, fixture_cl)
    assert data == expected_res

    mock_cag = mocker.patch('direct_indexing.custom_fields.codelists.check_and_get')
    # Test that check_and_get is called 0 times if the item does not have the field_name
    data = {parent_field_name: [{}, {}]}
    extract_nested_list_field(data, parent_field_name, field_name, field_type, cl_name, fixture_cl)
    mock_cag.assert_not_called()

    # Test that check_and_get is called twice for two items in the list
    data = {parent_field_name: [{field_name: {field_type: '10'}}, {field_name: {field_type: '20'}}]}
    extract_nested_list_field(data, parent_field_name, field_name, field_type, cl_name, fixture_cl)
    assert mock_cag.call_count == 2

    # Test that check_and_get is called one more time if the item is a dict
    data = {parent_field_name: {field_name: {field_type: '10'}}}
    extract_nested_list_field(data, parent_field_name, field_name, field_type, cl_name, fixture_cl)
    assert mock_cag.call_count == 3

    # Test that check_and_get is not called again if the item is an empty dict
    data = {parent_field_name: {}}
    extract_nested_list_field(data, parent_field_name, field_name, field_type, cl_name, fixture_cl)
    assert mock_cag.call_count == 3


def test_check_and_get(fixture_cl):
    # Test with field_type not in codelist_field
    field_name = 'recipient-country'
    field_type = 'code'
    cl_name = 'Country'
    data_field = field_name + CODELIST_POSTFIX
    data = {field_name: {}}
    check_and_get(field_type, data[field_name], None, None, None, None)
    assert data == {field_name: {}}
    # Test with field_type in codelist_field
    data = {field_name: {field_type: 'AF'}, data_field: []}
    expected_res = {field_name: {field_type: 'AF'}, data_field: ['Afghanistan']}
    check_and_get(field_type, data[field_name], data, data_field, fixture_cl, cl_name)
    assert data == expected_res


@pytest.fixture
def fixture_cl(monkeypatch):
    data = {
        "AidType": [
            {
                "code": "A01",
                "name": "General budget support",
                "description": "Unearmarked contributions to the government budget including funding to support the implementation of macroeconomic reforms (structural adjustment programmes, poverty reduction strategies). Budget support is a method of financing a recipient country\u2019s budget through a transfer of resources from an external financing agency to the recipient government\u2019s national treasury. The funds thus transferred are managed in accordance with the recipient\u2019s budgetary procedures. Funds transferred to the national treasury for financing programmes or projects managed according to different budgetary procedures from those of the recipient country, with the intention of earmarking the resources for specific uses, are therefore excluded.",  # NOQA: E501
                "category": "A",
                "status": "active"
            },
            {
                "code": "A02",
                "name": "Sector budget support",
                "description": "Sector budget support, like general budget support, is a financial contribution to a recipient government\u2019s budget. However, in sector budget support, the dialogue between donors and partner governments focuses on sector-specific concerns, rather than on overall policy and budget priorities.",  # NOQA: E501
                "category": "A",
                "status": "active"
            },
            {
                "code": "B01",
                "name": "Core support to NGOs, other private bodies, PPPs and research institutes",
                "description": "Funds are paid over to NGOs (local, national and international) for use at the latter\u2019s discretion, and contribute to programmes and activities which NGOs have developed themselves, and which they implement on their own authority and responsibility. Core contributions to PPPs, funds paid over to foundations (e.g. philanthropic foundations), and contributions to research institutes (public and private) are also recorded here. Annex 2 of the DAC Directives provides a list of INGOs, PPPs and networks core contributions to which may be reported under B01. This list is not exclusive.",  # NOQA: E501
                "category": "B",
                "status": "active"
            },
            {
                "code": "B02",
                "name": "Core contributions to multilateral institutions and global funds",
                "description": "These funds are classified as multilateral (all other categories are bilateral). The recipient multilateral institution pools contributions so that they lose their identity and become an integral part of its financial assets or liabilities. Also includes Financial Intermediary Funds (GEF, CIFs) for which the World Bank is the Trustee, as well as some UN inter-agency pooled funds, such as CERF and the UN Peacebuilding Fund. See Annex 2 of the Reporting Directives for a comprehensive list of agencies, core contributions to which may be reported under B02 and its subcategories. (Section I. Multilateral institutions). Nota bene: contributions to multilateral development organisations beyond Annex 2 are not reportable in the DAC statistics. The non-ODA components of core support to multilateral organisations included in Annex 2 are not reportable either.",  # NOQA: E501
                "category": "B",
                "status": "active"
            },
            {
                "code": "B021",
                "name": "Core contributions to multilateral institutions",
                "description": "Contributions in this category are pooled by the recipient multilateral institution and become an integral part of its financial assets or liabilities.",  # NOQA: E501
                "category": "B",
                "status": "active"
            },
            {
                "code": "B022",
                "name": "Core contributions to global funds",
                "description": "Contributions to global funds classified as multilateral including Financial Intermediary Funds for which the World Bank is the Trustee and which have gone through the Annex 2 process (GEF, CIFs) as well as some UN inter-agency pooled funds, e.g. CERF and the UN Peacebuilding Fund.",  # NOQA: E501
                "category": "B",
                "status": "active"
            },
            {
                "code": "B03",
                "name": "Contributions to specific-purpose programmes and funds managed by implementing partners",
                "description": "In addition to their core-funded operations, international organisations \u2013 multilateral agencies, NGOs, PPPs or networks \u2013 both in provider and in third countries, set up programmes and funds with a specific sectoral, thematic or geographical focus. Donors\u2019 bilateral contributions to such programmes and funds are recorded here. Use categories B031 and B032 for trust funds managed by the UN (all designed as multi-donor) unless contributions are earmarked for a specific geographical location or funding window.",  # NOQA: E501
                "category": "B",
                "status": "active"
            },
            {
                "code": "B031",
                "name": "Contributions to multi-donor/multi-entity funding mechanisms",
                "description": "Contributions to funding mechanisms (specific-purpose programmes and funds) that pool resources from several providers and from which several international organisations \u2013 multilateral agencies, NGOs, PPPs or networks \u2013 may be allocated funds for implementation e.g. contributions to UN country-based pooled funds and country-level development funds. Excludes contributions to global funds classified as multilateral (see B022). Includes Financial Intermediary Funds for which the World Bank is the Trustee and which have not gone through the Annex 2 process.",  # NOQA: E501
                "category": "B",
                "status": "active"
            },
            {
                "code": "B032",
                "name": "Contributions to multi-donor/single-entity funding mechanisms",
                "description": "Contributions to multi-donor funding mechanisms (specific-purpose programmes and funds) managed by a single international organisation \u2013 multilateral agency, NGO, PPP or network \u2013 e.g. UN single-agency thematic funds; World Bank or other MDB trust funds. Classify the contribution as B032 even if in the initial stages only one donor contributes to the fund.",  # NOQA: E501
                "category": "B",
                "status": "active"
            },
            {
                "code": "B033",
                "name": "Contributions to single-donor funding mechanisms and contributions earmarked for a specific funding window or geographical location",  # NOQA: E501
                "description": "Contributions to funding mechanisms (specific-purpose programmes and funds) where the donor has a significant influence on the allocation of funds. This includes contributions to single-donor trust funds and earmarked contributions to specific countries/geographical locations or funding windows within multi-donor trust funds. When the donor designs the activity but channels it through an international organisation, the activity should be classified as C01.",  # NOQA: E501
                "category": "B",
                "status": "active"
            },
            {
                "code": "B04",
                "name": "Basket funds/pooled funding",
                "description": "The donor contributes funds to an autonomous account, managed jointly with other donors and/or the recipient. The account will have specific purposes, modes of disbursement and accountability mechanisms, and a limited time frame. Basket funds are characterised by common project documents, common funding contracts and common reporting/audit procedures with all donors. Donors\u2019 contributions to funds managed autonomously by international organisations are recorded under B03.",  # NOQA: E501
                "category": "B",
                "status": "active"
            },
            {
                "code": "C01",
                "name": "Project-type interventions",
                "description": "A project is a set of inputs, activities and outputs, agreed with the partner country*, to reach specific objectives/outcomes within a defined time frame, with a defined budget and a defined geographical area. Projects can vary significantly in terms of objectives, complexity, amounts involved and duration. There are smaller projects that might involve modest financial resources and last only a few months, whereas large projects might involve more significant amounts, entail successive phases and last for many years. A large project with a number of different components is sometimes referred to as a programme, but should nevertheless be recorded here. Feasibility studies, appraisals and evaluations are included (whether designed as part of projects/programmes or dedicated funding arrangements). Academic studies, research and development, trainings, scholarships, and other technical assistance activities not directly linked to development projects/programmes should instead be recorded under D02. Aid channelled through NGOs or multilaterals is also recorded here. This includes payments for NGOs and multilaterals to implement donors\u2019 projects and programmes, and funding of specified NGOs projects. By contrast, core funding of NGOs and multilaterals as well as contributions to specific-purpose funds are recorded under B.* In the cases of equity investments, humanitarian aid or aid channelled through NGOs, projects are recorded here even if there was no direct agreement between the donor and the partner country. Contributions to single-donor trust funds and contributions to trust funds earmarked for a specific funding window and/or country are recorded under B033.",  # NOQA: E501
                "category": "C",
                "status": "active"
            },
            {
                "code": "D01",
                "name": "Donor country personnel",
                "description": "Experts, consultants, teachers, academics, researchers, volunteers and contributions to public and private bodies for sending experts to developing countries.",  # NOQA: E501
                "category": "D",
                "status": "active"
            },
            {
                "code": "D02",
                "name": "Other technical assistance",
                "description": "Provision, outside projects as described in category C01, of technical assistance in recipient countries (excluding technical assistance performed by donor experts reported under D01, and scholarships/training in donor country reported under E01). This includes training and research; language training; south-south studies; research studies; collaborative research between donor and recipient universities and organisations); local scholarships; development-oriented social and cultural programmes. This category also covers ad hoc contributions such as conferences, seminars and workshops, exchange visits, publications, etc.",  # NOQA: E501
                "category": "D",
                "status": "active"
            },
            {
                "code": "E01",
                "name": "Scholarships/training in donor country",
                "description": "Financial aid awards for individual students and contributions to trainees.",
                "category": "E",
                "status": "active"
            },
            {
                "code": "E02",
                "name": "Imputed student costs",
                "description": "Indirect (\u201cimputed\u201d) costs of tuition in donor countries.",
                "category": "E",
                "status": "active"
            },
            {
                "code": "F01",
                "name": "Debt relief",
                "description": "Groups all actions relating to debt (forgiveness, conversions, swaps, buy-backs, rescheduling, refinancing).",  # NOQA: E501
                "category": "F",
                "status": "active"
            },
            {
                "code": "G01",
                "name": "Administrative costs not included elsewhere",
                "description": "Administrative costs of development assistance programmes not already included under other ODA items as an integral part of the costs of delivering or implementing the aid provided. This category covers situation analyses and auditing activities.As regards the salaries component of administrative costs, it relates to in-house agency staff and contractors only; costs associated with donor experts/consultants are to be reported under category C or D01.",  # NOQA: E501
                "category": "G",
                "status": "active"
            },
            {
                "code": "H01",
                "name": "Development awareness",
                "description": "Funding of activities designed to increase public support, i.e. awareness in the donor country of development co-operation efforts, needs and issues.",  # NOQA: E501
                "category": "H",
                "status": "active"
            },
            {
                "code": "H02",
                "name": "Refugees/asylum seekers in donor countries",
                "description": "Costs incurred in donor countries for basic assistance to asylum seekers and refugees from developing countries, up to 12 months, when costs cannot be disaggregated. See section II.6 and Annex 17.",  # NOQA: E501
                "category": "H",
                "status": "active"
            },
            {
                "code": "H03",
                "name": "Asylum-seekers ultimately accepted",
                "description": "Costs incurred in donor countries for basic assistance to asylum seekers, when these are ultimately accepted. This category includes only costs incurred prior to recognition.",  # NOQA: E501
                "category": "H",
                "status": "active"
            },
            {
                "code": "H04",
                "name": "Asylum-seekers ultimately rejected",
                "description": "Costs incurred in donor countries for basic assistance to asylum seekers, when these are ultimately rejected. This category includes only costs incurred prior to rejection. Members may base their reporting on the first instance rejection, where a final decision on status is anticipated to occur after a 12-month period, and this facilitates the establishment of a conservative estimate. For further guidance on how to proceed with calculating costs related to rejected asylum seekers, see Clarification 5, third bullet in section II.6 of the Reporting Directives.",  # NOQA: E501
                "category": "H",
                "status": "active"
            },
            {
                "code": "H05",
                "name": "Recognised refugees",
                "description": "Costs incurred in donor countries for basic assistance to refugees with a recognised status. This category only includes costs after recognition (or after date of entry into a country through a resettlement programme).",  # NOQA: E501
                "category": "H",
                "status": "active"
            },
            {
                "code": "H06",
                "name": "Refugees and asylum seekers in other provider countries",
                "description": "Costs incurred in other non-ODA eligible provider countries for basic assistance to asylum seekers and refugees from developing countries, up to 12 months. The host and origin country of refugees/asylum seekers shall be specified in one of the descriptive fields of the CRS (fields 14 or 19).",  # NOQA: E501
                "category": "H",
                "status": "active"
            }
        ],
        "BudgetStatus": [
            {
                "code": "1",
                "name": "Indicative",
                "description": "A non-binding estimate for the described budget.",
                "status": "active"
            },
            {
                "code": "2",
                "name": "Committed",
                "description": "A binding agreement for the described budget.",
                "status": "active"
            }
        ],
        "BudgetType": [
            {
                "code": "1",
                "name": "Original",
                "description": "The original budget allocated to the activity",
                "status": "active"
            },
            {
                "code": "2",
                "name": "Revised",
                "description": "The updated budget for an activity",
                "status": "active"
            }
        ],
        "Country": [
            {
                "code": "AF",
                "name": "Afghanistan",
                "status": "active"
            },
            {
                "code": "AX",
                "name": "\u00c5land Islands",
                "status": "active"
            },
            {
                "code": "AL",
                "name": "Albania",
                "status": "active"
            },
            {
                "code": "DZ",
                "name": "Algeria",
                "status": "active"
            },
            {
                "code": "AS",
                "name": "American Samoa",
                "status": "active"
            },
            {
                "code": "AD",
                "name": "Andorra",
                "status": "active"
            },
            {
                "code": "AO",
                "name": "Angola",
                "status": "active"
            },
            {
                "code": "AI",
                "name": "Anguilla",
                "status": "active"
            },
            {
                "code": "AQ",
                "name": "Antarctica",
                "status": "active"
            },
            {
                "code": "AG",
                "name": "Antigua and Barbuda",
                "status": "active"
            },
            {
                "code": "AR",
                "name": "Argentina",
                "status": "active"
            },
            {
                "code": "AM",
                "name": "Armenia",
                "status": "active"
            },
            {
                "code": "AW",
                "name": "Aruba",
                "status": "active"
            },
            {
                "code": "AU",
                "name": "Australia",
                "status": "active"
            },
            {
                "code": "AT",
                "name": "Austria",
                "status": "active"
            },
            {
                "code": "AZ",
                "name": "Azerbaijan",
                "status": "active"
            },
            {
                "code": "BS",
                "name": "Bahamas (the)",
                "status": "active"
            },
            {
                "code": "BH",
                "name": "Bahrain",
                "status": "active"
            },
            {
                "code": "BD",
                "name": "Bangladesh",
                "status": "active"
            },
            {
                "code": "BB",
                "name": "Barbados",
                "status": "active"
            },
            {
                "code": "BY",
                "name": "Belarus",
                "status": "active"
            },
            {
                "code": "BE",
                "name": "Belgium",
                "status": "active"
            },
            {
                "code": "BZ",
                "name": "Belize",
                "status": "active"
            },
            {
                "code": "BJ",
                "name": "Benin",
                "status": "active"
            },
            {
                "code": "BM",
                "name": "Bermuda",
                "status": "active"
            },
            {
                "code": "BT",
                "name": "Bhutan",
                "status": "active"
            },
            {
                "code": "BO",
                "name": "Bolivia (Plurinational State of)",
                "status": "active"
            },
            {
                "code": "BQ",
                "name": "Bonaire, Sint Eustatius and Saba",
                "status": "active"
            },
            {
                "code": "BA",
                "name": "Bosnia and Herzegovina",
                "status": "active"
            },
            {
                "code": "BW",
                "name": "Botswana",
                "status": "active"
            },
            {
                "code": "BV",
                "name": "Bouvet Island",
                "status": "active"
            },
            {
                "code": "BR",
                "name": "Brazil",
                "status": "active"
            },
            {
                "code": "IO",
                "name": "British Indian Ocean Territory (the)",
                "status": "active"
            },
            {
                "code": "BN",
                "name": "Brunei Darussalam",
                "status": "active"
            },
            {
                "code": "BG",
                "name": "Bulgaria",
                "status": "active"
            },
            {
                "code": "BF",
                "name": "Burkina Faso",
                "status": "active"
            },
            {
                "code": "BU",
                "name": "Burma",
                "status": "withdrawn"
            },
            {
                "code": "BI",
                "name": "Burundi",
                "status": "active"
            },
            {
                "code": "KH",
                "name": "Cambodia",
                "status": "active"
            },
            {
                "code": "CM",
                "name": "Cameroon",
                "status": "active"
            },
            {
                "code": "CA",
                "name": "Canada",
                "status": "active"
            },
            {
                "code": "CV",
                "name": "Cabo Verde",
                "status": "active"
            },
            {
                "code": "KY",
                "name": "Cayman Islands (the)",
                "status": "active"
            },
            {
                "code": "CF",
                "name": "Central African Republic (the)",
                "status": "active"
            },
            {
                "code": "TD",
                "name": "Chad",
                "status": "active"
            },
            {
                "code": "CL",
                "name": "Chile",
                "status": "active"
            },
            {
                "code": "CN",
                "name": "China",
                "status": "active"
            },
            {
                "code": "CX",
                "name": "Christmas Island",
                "status": "active"
            },
            {
                "code": "CC",
                "name": "Cocos (Keeling) Islands (the)",
                "status": "active"
            },
            {
                "code": "CO",
                "name": "Colombia",
                "status": "active"
            },
            {
                "code": "KM",
                "name": "Comoros (the)",
                "status": "active"
            },
            {
                "code": "CG",
                "name": "Congo (the)",
                "status": "active"
            },
            {
                "code": "CD",
                "name": "Congo (the Democratic Republic of the)",
                "status": "active"
            },
            {
                "code": "CK",
                "name": "Cook Islands (the)",
                "status": "active"
            },
            {
                "code": "CR",
                "name": "Costa Rica",
                "status": "active"
            },
            {
                "code": "CI",
                "name": "C\u00f4te d'Ivoire",
                "status": "active"
            },
            {
                "code": "HR",
                "name": "Croatia",
                "status": "active"
            },
            {
                "code": "CU",
                "name": "Cuba",
                "status": "active"
            },
            {
                "code": "CW",
                "name": "Cura\u00e7ao",
                "status": "active"
            },
            {
                "code": "CY",
                "name": "Cyprus",
                "status": "active"
            },
            {
                "code": "CZ",
                "name": "Czechia",
                "status": "active"
            },
            {
                "code": "DK",
                "name": "Denmark",
                "status": "active"
            },
            {
                "code": "DJ",
                "name": "Djibouti",
                "status": "active"
            },
            {
                "code": "DM",
                "name": "Dominica",
                "status": "active"
            },
            {
                "code": "DO",
                "name": "Dominican Republic (the)",
                "status": "active"
            },
            {
                "code": "TP",
                "name": "East Timor",
                "status": "withdrawn"
            },
            {
                "code": "EC",
                "name": "Ecuador",
                "status": "active"
            },
            {
                "code": "EG",
                "name": "Egypt",
                "status": "active"
            },
            {
                "code": "SV",
                "name": "El Salvador",
                "status": "active"
            },
            {
                "code": "GQ",
                "name": "Equatorial Guinea",
                "status": "active"
            },
            {
                "code": "ER",
                "name": "Eritrea",
                "status": "active"
            },
            {
                "code": "EE",
                "name": "Estonia",
                "status": "active"
            },
            {
                "code": "ET",
                "name": "Ethiopia",
                "status": "active"
            },
            {
                "code": "FK",
                "name": "Falkland Islands (the) [Malvinas]",
                "status": "active"
            },
            {
                "code": "FO",
                "name": "Faroe Islands (the)",
                "status": "active"
            },
            {
                "code": "FJ",
                "name": "Fiji",
                "status": "active"
            },
            {
                "code": "FI",
                "name": "Finland",
                "status": "active"
            },
            {
                "code": "FR",
                "name": "France",
                "status": "active"
            },
            {
                "code": "GF",
                "name": "French Guiana",
                "status": "active"
            },
            {
                "code": "PF",
                "name": "French Polynesia",
                "status": "active"
            },
            {
                "code": "TF",
                "name": "French Southern Territories (the)",
                "status": "active"
            },
            {
                "code": "GA",
                "name": "Gabon",
                "status": "active"
            },
            {
                "code": "GM",
                "name": "Gambia (the)",
                "status": "active"
            },
            {
                "code": "GE",
                "name": "Georgia",
                "status": "active"
            },
            {
                "code": "DE",
                "name": "Germany",
                "status": "active"
            },
            {
                "code": "GH",
                "name": "Ghana",
                "status": "active"
            },
            {
                "code": "GI",
                "name": "Gibraltar",
                "status": "active"
            },
            {
                "code": "GR",
                "name": "Greece",
                "status": "active"
            },
            {
                "code": "GL",
                "name": "Greenland",
                "status": "active"
            },
            {
                "code": "GD",
                "name": "Grenada",
                "status": "active"
            },
            {
                "code": "GP",
                "name": "Guadeloupe",
                "status": "active"
            },
            {
                "code": "GU",
                "name": "Guam",
                "status": "active"
            },
            {
                "code": "GT",
                "name": "Guatemala",
                "status": "active"
            },
            {
                "code": "GG",
                "name": "Guernsey",
                "status": "active"
            },
            {
                "code": "GN",
                "name": "Guinea",
                "status": "active"
            },
            {
                "code": "GW",
                "name": "Guinea-Bissau",
                "status": "active"
            },
            {
                "code": "GY",
                "name": "Guyana",
                "status": "active"
            },
            {
                "code": "HT",
                "name": "Haiti",
                "status": "active"
            },
            {
                "code": "HM",
                "name": "Heard Island and McDonald Islands",
                "status": "active"
            },
            {
                "code": "VA",
                "name": "Holy See (the)",
                "status": "active"
            },
            {
                "code": "HN",
                "name": "Honduras",
                "status": "active"
            },
            {
                "code": "HK",
                "name": "Hong Kong",
                "status": "active"
            },
            {
                "code": "HU",
                "name": "Hungary",
                "status": "active"
            },
            {
                "code": "IS",
                "name": "Iceland",
                "status": "active"
            },
            {
                "code": "IN",
                "name": "India",
                "status": "active"
            },
            {
                "code": "ID",
                "name": "Indonesia",
                "status": "active"
            },
            {
                "code": "IR",
                "name": "Iran (Islamic Republic of)",
                "status": "active"
            },
            {
                "code": "IQ",
                "name": "Iraq",
                "status": "active"
            },
            {
                "code": "IE",
                "name": "Ireland",
                "status": "active"
            },
            {
                "code": "IM",
                "name": "Isle of Man",
                "status": "active"
            },
            {
                "code": "IL",
                "name": "Israel",
                "status": "active"
            },
            {
                "code": "IT",
                "name": "Italy",
                "status": "active"
            },
            {
                "code": "JM",
                "name": "Jamaica",
                "status": "active"
            },
            {
                "code": "JP",
                "name": "Japan",
                "status": "active"
            },
            {
                "code": "JE",
                "name": "Jersey",
                "status": "active"
            },
            {
                "code": "JO",
                "name": "Jordan",
                "status": "active"
            },
            {
                "code": "KZ",
                "name": "Kazakhstan",
                "status": "active"
            },
            {
                "code": "KE",
                "name": "Kenya",
                "status": "active"
            },
            {
                "code": "KI",
                "name": "Kiribati",
                "status": "active"
            },
            {
                "code": "KP",
                "name": "Korea (the Democratic People's Republic of)",
                "status": "active"
            },
            {
                "code": "KR",
                "name": "Korea (the Republic of)",
                "status": "active"
            },
            {
                "code": "XK",
                "name": "Kosovo",
                "status": "active"
            },
            {
                "code": "KW",
                "name": "Kuwait",
                "status": "active"
            },
            {
                "code": "KG",
                "name": "Kyrgyzstan",
                "status": "active"
            },
            {
                "code": "LA",
                "name": "Lao People's Democratic Republic (the)",
                "status": "active"
            },
            {
                "code": "LV",
                "name": "Latvia",
                "status": "active"
            },
            {
                "code": "LB",
                "name": "Lebanon",
                "status": "active"
            },
            {
                "code": "LS",
                "name": "Lesotho",
                "status": "active"
            },
            {
                "code": "LR",
                "name": "Liberia",
                "status": "active"
            },
            {
                "code": "LY",
                "name": "Libya",
                "status": "active"
            },
            {
                "code": "LI",
                "name": "Liechtenstein",
                "status": "active"
            },
            {
                "code": "LT",
                "name": "Lithuania",
                "status": "active"
            },
            {
                "code": "LU",
                "name": "Luxembourg",
                "status": "active"
            },
            {
                "code": "MO",
                "name": "Macao",
                "status": "active"
            },
            {
                "code": "MK",
                "name": "North Macedonia",
                "status": "active"
            },
            {
                "code": "MG",
                "name": "Madagascar",
                "status": "active"
            },
            {
                "code": "MW",
                "name": "Malawi",
                "status": "active"
            },
            {
                "code": "MY",
                "name": "Malaysia",
                "status": "active"
            },
            {
                "code": "MV",
                "name": "Maldives",
                "status": "active"
            },
            {
                "code": "ML",
                "name": "Mali",
                "status": "active"
            },
            {
                "code": "MT",
                "name": "Malta",
                "status": "active"
            },
            {
                "code": "MH",
                "name": "Marshall Islands (the)",
                "status": "active"
            },
            {
                "code": "MQ",
                "name": "Martinique",
                "status": "active"
            },
            {
                "code": "MR",
                "name": "Mauritania",
                "status": "active"
            },
            {
                "code": "MU",
                "name": "Mauritius",
                "status": "active"
            },
            {
                "code": "YT",
                "name": "Mayotte",
                "status": "active"
            },
            {
                "code": "MX",
                "name": "Mexico",
                "status": "active"
            },
            {
                "code": "FM",
                "name": "Micronesia (Federated States of)",
                "status": "active"
            },
            {
                "code": "MD",
                "name": "Moldova (the Republic of)",
                "status": "active"
            },
            {
                "code": "MC",
                "name": "Monaco",
                "status": "active"
            },
            {
                "code": "MN",
                "name": "Mongolia",
                "status": "active"
            },
            {
                "code": "ME",
                "name": "Montenegro",
                "status": "active"
            },
            {
                "code": "MS",
                "name": "Montserrat",
                "status": "active"
            },
            {
                "code": "MA",
                "name": "Morocco",
                "status": "active"
            },
            {
                "code": "MZ",
                "name": "Mozambique",
                "status": "active"
            },
            {
                "code": "MM",
                "name": "Myanmar",
                "status": "active"
            },
            {
                "code": "NA",
                "name": "Namibia",
                "status": "active"
            },
            {
                "code": "NR",
                "name": "Nauru",
                "status": "active"
            },
            {
                "code": "NP",
                "name": "Nepal",
                "status": "active"
            },
            {
                "code": "NL",
                "name": "Netherlands (Kingdom of the)",
                "status": "active"
            },
            {
                "code": "AN",
                "name": "Netherlands Antilles",
                "status": "withdrawn"
            },
            {
                "code": "NT",
                "name": "Neutral Zone",
                "status": "withdrawn"
            },
            {
                "code": "NC",
                "name": "New Caledonia",
                "status": "active"
            },
            {
                "code": "NZ",
                "name": "New Zealand",
                "status": "active"
            },
            {
                "code": "NI",
                "name": "Nicaragua",
                "status": "active"
            },
            {
                "code": "NE",
                "name": "Niger (the)",
                "status": "active"
            },
            {
                "code": "NG",
                "name": "Nigeria",
                "status": "active"
            },
            {
                "code": "NU",
                "name": "Niue",
                "status": "active"
            },
            {
                "code": "NF",
                "name": "Norfolk Island",
                "status": "active"
            },
            {
                "code": "MP",
                "name": "Northern Mariana Islands (the)",
                "status": "active"
            },
            {
                "code": "NO",
                "name": "Norway",
                "status": "active"
            },
            {
                "code": "OM",
                "name": "Oman",
                "status": "active"
            },
            {
                "code": "PK",
                "name": "Pakistan",
                "status": "active"
            },
            {
                "code": "PW",
                "name": "Palau",
                "status": "active"
            },
            {
                "code": "PS",
                "name": "Palestine, State of",
                "status": "active"
            },
            {
                "code": "PA",
                "name": "Panama",
                "status": "active"
            },
            {
                "code": "PG",
                "name": "Papua New Guinea",
                "status": "active"
            },
            {
                "code": "PY",
                "name": "Paraguay",
                "status": "active"
            },
            {
                "code": "PE",
                "name": "Peru",
                "status": "active"
            },
            {
                "code": "PH",
                "name": "Philippines (the)",
                "status": "active"
            },
            {
                "code": "PN",
                "name": "Pitcairn",
                "status": "active"
            },
            {
                "code": "PL",
                "name": "Poland",
                "status": "active"
            },
            {
                "code": "PT",
                "name": "Portugal",
                "status": "active"
            },
            {
                "code": "PR",
                "name": "Puerto Rico",
                "status": "active"
            },
            {
                "code": "QA",
                "name": "Qatar",
                "status": "active"
            },
            {
                "code": "RE",
                "name": "R\u00e9union",
                "status": "active"
            },
            {
                "code": "RO",
                "name": "Romania",
                "status": "active"
            },
            {
                "code": "RU",
                "name": "Russian Federation (the)",
                "status": "active"
            },
            {
                "code": "RW",
                "name": "Rwanda",
                "status": "active"
            },
            {
                "code": "BL",
                "name": "Saint Barth\u00e9lemy",
                "status": "active"
            },
            {
                "code": "SH",
                "name": "Saint Helena, Ascension and Tristan da Cunha",
                "status": "active"
            },
            {
                "code": "KN",
                "name": "Saint Kitts and Nevis",
                "status": "active"
            },
            {
                "code": "LC",
                "name": "Saint Lucia",
                "status": "active"
            },
            {
                "code": "MF",
                "name": "Saint Martin (French part)",
                "status": "active"
            },
            {
                "code": "PM",
                "name": "Saint Pierre and Miquelon",
                "status": "active"
            },
            {
                "code": "VC",
                "name": "Saint Vincent and the Grenadines",
                "status": "active"
            },
            {
                "code": "WS",
                "name": "Samoa",
                "status": "active"
            },
            {
                "code": "SM",
                "name": "San Marino",
                "status": "active"
            },
            {
                "code": "ST",
                "name": "Sao Tome and Principe",
                "status": "active"
            },
            {
                "code": "SA",
                "name": "Saudi Arabia",
                "status": "active"
            },
            {
                "code": "SN",
                "name": "Senegal",
                "status": "active"
            },
            {
                "code": "RS",
                "name": "Serbia",
                "status": "active"
            },
            {
                "code": "SC",
                "name": "Seychelles",
                "status": "active"
            },
            {
                "code": "SL",
                "name": "Sierra Leone",
                "status": "active"
            },
            {
                "code": "SG",
                "name": "Singapore",
                "status": "active"
            },
            {
                "code": "SX",
                "name": "Sint Maarten (Dutch part)",
                "status": "active"
            },
            {
                "code": "SK",
                "name": "Slovakia",
                "status": "active"
            },
            {
                "code": "SI",
                "name": "Slovenia",
                "status": "active"
            },
            {
                "code": "SB",
                "name": "Solomon Islands",
                "status": "active"
            },
            {
                "code": "SO",
                "name": "Somalia",
                "status": "active"
            },
            {
                "code": "ZA",
                "name": "South Africa",
                "status": "active"
            },
            {
                "code": "GS",
                "name": "South Georgia and the South Sandwich Islands",
                "status": "active"
            },
            {
                "code": "SS",
                "name": "South Sudan",
                "status": "active"
            },
            {
                "code": "ES",
                "name": "Spain",
                "status": "active"
            },
            {
                "code": "LK",
                "name": "Sri Lanka",
                "status": "active"
            },
            {
                "code": "SD",
                "name": "Sudan (the)",
                "status": "active"
            },
            {
                "code": "SR",
                "name": "Suriname",
                "status": "active"
            },
            {
                "code": "SJ",
                "name": "Svalbard and Jan Mayen",
                "status": "active"
            },
            {
                "code": "SZ",
                "name": "Eswatini",
                "status": "active"
            },
            {
                "code": "CS",
                "name": "Serbia and Montenegro",
                "status": "withdrawn"
            },
            {
                "code": "SE",
                "name": "Sweden",
                "status": "active"
            },
            {
                "code": "CH",
                "name": "Switzerland",
                "status": "active"
            },
            {
                "code": "SY",
                "name": "Syrian Arab Republic (the)",
                "status": "active"
            },
            {
                "code": "TW",
                "name": "Taiwan (Province of China)",
                "status": "active"
            },
            {
                "code": "TJ",
                "name": "Tajikistan",
                "status": "active"
            },
            {
                "code": "TZ",
                "name": "Tanzania, the United Republic of",
                "status": "active"
            },
            {
                "code": "TH",
                "name": "Thailand",
                "status": "active"
            },
            {
                "code": "TL",
                "name": "Timor-Leste",
                "status": "active"
            },
            {
                "code": "TG",
                "name": "Togo",
                "status": "active"
            },
            {
                "code": "TK",
                "name": "Tokelau",
                "status": "active"
            },
            {
                "code": "TO",
                "name": "Tonga",
                "status": "active"
            },
            {
                "code": "TT",
                "name": "Trinidad and Tobago",
                "status": "active"
            },
            {
                "code": "TN",
                "name": "Tunisia",
                "status": "active"
            },
            {
                "code": "TR",
                "name": "T\u00fcrkiye",
                "status": "active"
            },
            {
                "code": "TM",
                "name": "Turkmenistan",
                "status": "active"
            },
            {
                "code": "TC",
                "name": "Turks and Caicos Islands (the)",
                "status": "active"
            },
            {
                "code": "TV",
                "name": "Tuvalu",
                "status": "active"
            },
            {
                "code": "UG",
                "name": "Uganda",
                "status": "active"
            },
            {
                "code": "UA",
                "name": "Ukraine",
                "status": "active"
            },
            {
                "code": "AE",
                "name": "United Arab Emirates (the)",
                "status": "active"
            },
            {
                "code": "GB",
                "name": "United Kingdom of Great Britain and Northern Ireland (the)",
                "status": "active"
            },
            {
                "code": "US",
                "name": "United States of America (the)",
                "status": "active"
            },
            {
                "code": "UM",
                "name": "United States Minor Outlying Islands (the)",
                "status": "active"
            },
            {
                "code": "UY",
                "name": "Uruguay",
                "status": "active"
            },
            {
                "code": "UZ",
                "name": "Uzbekistan",
                "status": "active"
            },
            {
                "code": "VU",
                "name": "Vanuatu",
                "status": "active"
            },
            {
                "code": "VE",
                "name": "Venezuela (Bolivarian Republic of)",
                "status": "active"
            },
            {
                "code": "VN",
                "name": "Viet Nam",
                "status": "active"
            },
            {
                "code": "VG",
                "name": "Virgin Islands (British)",
                "status": "active"
            },
            {
                "code": "VI",
                "name": "Virgin Islands (U.S.)",
                "status": "active"
            },
            {
                "code": "WF",
                "name": "Wallis and Futuna",
                "status": "active"
            },
            {
                "code": "EH",
                "name": "Western Sahara",
                "status": "active"
            },
            {
                "code": "YE",
                "name": "Yemen",
                "status": "active"
            },
            {
                "code": "YU",
                "name": "Yugoslavia",
                "status": "withdrawn"
            },
            {
                "code": "ZR",
                "name": "Zaire",
                "status": "withdrawn"
            },
            {
                "code": "ZM",
                "name": "Zambia",
                "status": "active"
            },
            {
                "code": "ZW",
                "name": "Zimbabwe",
                "status": "active"
            }
        ],
        "OrganisationType": [
            {
                "code": "10",
                "name": "Government",
                "status": "active",
                "description": None
            },
            {
                "code": "11",
                "name": "Local Government",
                "description": "Any local (sub national) government organisation in either donor or recipient country.",
                "status": "active"
            },
            {
                "code": "15",
                "name": "Other Public Sector",
                "status": "active",
                "description": None
            },
            {
                "code": "21",
                "name": "International NGO",
                "status": "active",
                "description": None
            },
            {
                "code": "22",
                "name": "National NGO",
                "status": "active",
                "description": None
            },
            {
                "code": "23",
                "name": "Regional NGO",
                "status": "active",
                "description": None
            },
            {
                "code": "24",
                "name": "Partner Country based NGO",
                "description": "Local and National NGO / CSO based in aid/assistance recipient country",
                "status": "active"
            },
            {
                "code": "30",
                "name": "Public Private Partnership",
                "status": "active",
                "description": None
            },
            {
                "code": "40",
                "name": "Multilateral",
                "status": "active",
                "description": None
            },
            {
                "code": "60",
                "name": "Foundation",
                "status": "active",
                "description": None
            },
            {
                "code": "70",
                "name": "Private Sector",
                "status": "active",
                "description": None
            },
            {
                "code": "71",
                "name": "Private Sector in Provider Country",
                "description": "Is in provider / donor country.",
                "status": "active"
            },
            {
                "code": "72",
                "name": "Private Sector in Aid Recipient Country",
                "description": "Is in aid recipient country.",
                "status": "active"
            },
            {
                "code": "73",
                "name": "Private Sector in Third Country",
                "description": "Is not in either a donor or aid recipient country.",
                "status": "active"
            },
            {
                "code": "80",
                "name": "Academic, Training and Research",
                "status": "active",
                "description": None
            },
            {
                "code": "90",
                "name": "Other",
                "status": "active",
                "description": None
            }
        ],
        "Region": [
            {
                "code": "88",
                "name": "States Ex-Yugoslavia unspecified",
                "status": "active"
            },
            {
                "code": "89",
                "name": "Europe, regional",
                "status": "active"
            },
            {
                "code": "189",
                "name": "North of Sahara, regional",
                "status": "active"
            },
            {
                "code": "289",
                "name": "South of Sahara, regional",
                "status": "active"
            },
            {
                "code": "298",
                "name": "Africa, regional",
                "status": "active"
            },
            {
                "code": "380",
                "name": "West Indies, regional",
                "status": "withdrawn"
            },
            {
                "code": "389",
                "name": "Caribbean & Central America, regional",
                "status": "active"
            },
            {
                "code": "489",
                "name": "South America, regional",
                "status": "active"
            },
            {
                "code": "498",
                "name": "America, regional",
                "status": "active"
            },
            {
                "code": "589",
                "name": "Middle East, regional",
                "status": "active"
            },
            {
                "code": "619",
                "name": "Central Asia, regional",
                "status": "active"
            },
            {
                "code": "679",
                "name": "South Asia, regional",
                "status": "active"
            },
            {
                "code": "689",
                "name": "South & Central Asia, regional",
                "status": "active"
            },
            {
                "code": "789",
                "name": "Far East Asia, regional",
                "status": "active"
            },
            {
                "code": "798",
                "name": "Asia, regional",
                "status": "active"
            },
            {
                "code": "889",
                "name": "Oceania, regional",
                "status": "active"
            },
            {
                "code": "998",
                "name": "Developing countries, unspecified",
                "status": "active"
            },
            {
                "code": "1027",
                "name": "Eastern Africa, regional",
                "status": "active"
            },
            {
                "code": "1028",
                "name": "Middle Africa, regional",
                "status": "active"
            },
            {
                "code": "1029",
                "name": "Southern Africa, regional",
                "status": "active"
            },
            {
                "code": "1030",
                "name": "Western Africa, regional",
                "status": "active"
            },
            {
                "code": "1031",
                "name": "Caribbean, regional",
                "status": "active"
            },
            {
                "code": "1032",
                "name": "Central America, regional",
                "status": "active"
            },
            {
                "code": "1033",
                "name": "Melanesia, regional",
                "status": "active"
            },
            {
                "code": "1034",
                "name": "Micronesia, regional",
                "status": "active"
            },
            {
                "code": "1035",
                "name": "Polynesia, regional",
                "status": "active"
            }
        ],
        "TagVocabulary": [
            {
                "code": "1",
                "name": "Agrovoc",
                "description": "A controlled vocabulary covering all areas of interest of the Food and Agriculture Organization (FAO) of the United Nations, including food, nutrition, agriculture, fisheries, forestry, environment etc.",  # NOQA: E501
                "url": "https://agrovoc.fao.org/browse/agrovoc/en/",
                "status": "active"
            },
            {
                "code": "2",
                "name": "UN Sustainable Development Goals (SDG)",
                "description": "A value from the top-level list of UN sustainable development goals (SDGs) (e.g. \u20181\u2019)",  # NOQA: E501
                "url": "https://reference.iatistandard.org/codelists/UNSDG-Goals/",
                "status": "active"
            },
            {
                "code": "3",
                "name": "UN Sustainable Development Goals (SDG) Targets",
                "description": "A value from the second-level list of UN sustainable development goals (SDGs) (e.g. \u20181.1\u2019)",  # NOQA: E501
                "url": "https://reference.iatistandard.org/codelists/UNSDG-Targets/",
                "status": "active"
            },
            {
                "code": "4",
                "name": "Team Europe Initiatives",
                "description": "A value from the list of Team Europe Initiatives. Team Europe consists of the European Commission, the EU Member States \u2014 including their implementing agencies and public development banks \u2014 as well as the European Investment Bank (EIB) and the European Bank for Reconstruction and Development (EBRD).",  # NOQA: E501
                "url": "https://europa.eu/capacity4dev/joint-programming/documents/tei-codes-0",
                "status": "active"
            },
            {
                "code": "99",
                "name": "Reporting Organisation",
                "status": "active",
                "description": None,
                "url": None
            }
        ],
        "SectorCategory": [
            {
                "code": "111",
                "name": "Education, Level Unspecified",
                "description": "The codes in this category are to be used only when level of education is unspecified or unknown (e.g. training of primary school teachers should be coded under 11220).",  # NOQA: E501
                "status": "active"
            },
            {
                "code": "112",
                "name": "Basic Education",
                "status": "active",
                "description": None
            },
            {
                "code": "113",
                "name": "Secondary Education",
                "status": "active",
                "description": None
            },
            {
                "code": "114",
                "name": "Post-Secondary Education",
                "status": "active",
                "description": None
            },
            {
                "code": "121",
                "name": "Health, General",
                "status": "active",
                "description": None
            },
            {
                "code": "122",
                "name": "Basic Health",
                "status": "active",
                "description": None
            },
            {
                "code": "123",
                "name": "Non-communicable diseases (NCDs)",
                "status": "active",
                "description": None
            },
            {
                "code": "130",
                "name": "Population Policies/Programmes & Reproductive Health",
                "status": "active",
                "description": None
            },
            {
                "code": "140",
                "name": "Water Supply & Sanitation",
                "status": "active",
                "description": None
            },
            {
                "code": "151",
                "name": "Government & Civil Society-general",
                "description": "N.B. Use code 51010 for general budget support.",
                "status": "active"
            },
            {
                "code": "152",
                "name": "Conflict, Peace & Security",
                "description": "N.B. Further notes on ODA eligibility (and exclusions) of conflict, peace and security related activities are given in paragraphs 76-81 of the Directives.",  # NOQA: E501
                "status": "active"
            },
            {
                "code": "160",
                "name": "Other Social Infrastructure & Services",
                "status": "active",
                "description": None
            },
            {
                "code": "210",
                "name": "Transport & Storage",
                "description": "Note: Manufacturing of transport equipment should be included under code 32172.",
                "status": "active"
            },
            {
                "code": "220",
                "name": "Communications",
                "status": "active",
                "description": None
            },
            {
                "code": "230",
                "name": "ENERGY GENERATION AND SUPPLY",
                "description": "Energy sector policy, planning and programmes; aid to energy ministries; institution capacity building and advice; unspecified energy activities including energy conservation.",  # NOQA: E501
                "status": "withdrawn"
            },
            {
                "code": "231",
                "name": "Energy Policy",
                "status": "active",
                "description": None
            },
            {
                "code": "232",
                "name": "Energy generation, renewable sources",
                "status": "active",
                "description": None
            },
            {
                "code": "233",
                "name": "Energy generation, non-renewable sources",
                "status": "active",
                "description": None
            },
            {
                "code": "234",
                "name": "Hybrid energy plants",
                "status": "active",
                "description": None
            },
            {
                "code": "235",
                "name": "Nuclear energy plants",
                "status": "active",
                "description": None
            },
            {
                "code": "236",
                "name": "Energy distribution",
                "status": "active",
                "description": None
            },
            {
                "code": "240",
                "name": "Banking & Financial Services",
                "status": "active",
                "description": None
            },
            {
                "code": "250",
                "name": "Business & Other Services",
                "status": "active",
                "description": None
            },
            {
                "code": "311",
                "name": "Agriculture",
                "status": "active",
                "description": None
            },
            {
                "code": "312",
                "name": "Forestry",
                "status": "active",
                "description": None
            },
            {
                "code": "313",
                "name": "Fishing",
                "status": "active",
                "description": None
            },
            {
                "code": "321",
                "name": "Industry",
                "status": "active",
                "description": None
            },
            {
                "code": "322",
                "name": "Mineral Resources & Mining",
                "status": "active",
                "description": None
            },
            {
                "code": "323",
                "name": "Construction",
                "status": "active",
                "description": None
            },
            {
                "code": "331",
                "name": "Trade Policies & Regulations",
                "status": "active",
                "description": None
            },
            {
                "code": "332",
                "name": "Tourism",
                "status": "active",
                "description": None
            },
            {
                "code": "410",
                "name": "General Environment Protection",
                "description": "Covers activities concerned with conservation, protection or amelioration of the physical environment without sector allocation.",  # NOQA: E501
                "status": "active"
            },
            {
                "code": "430",
                "name": "Other Multisector",
                "status": "active",
                "description": None
            },
            {
                "code": "510",
                "name": "General Budget Support",
                "description": "Budget support in the form of sector-wide approaches (SWAps) should be included in the respective sectors.",  # NOQA: E501
                "status": "active"
            },
            {
                "code": "520",
                "name": "Development Food Assistance",
                "status": "active",
                "description": None
            },
            {
                "code": "530",
                "name": "Other Commodity Assistance",
                "description": "Non-food commodity assistance (when benefiting sector not specified).",
                "status": "active"
            },
            {
                "code": "600",
                "name": "Action Relating to Debt",
                "status": "active",
                "description": None
            },
            {
                "code": "720",
                "name": "Emergency Response",
                "description": "An emergency is a situation which results from man made crises and/or natural disasters.",  # NOQA: E501
                "status": "active"
            },
            {
                "code": "730",
                "name": "Reconstruction Relief & Rehabilitation",
                "description": "This relates to activities during and in the aftermath of an emergency situation. Longer-term activities to improve the level of infrastructure or social services should be reported under the relevant economic and social sector codes. See also guideline on distinguishing humanitarian from sector-allocable aid.",  # NOQA: E501
                "status": "active"
            },
            {
                "code": "740",
                "name": "Disaster Prevention & Preparedness",
                "description": "See code 43060 for disaster risk reduction.",
                "status": "active"
            },
            {
                "code": "910",
                "name": "Administrative Costs of Donors",
                "status": "active",
                "description": None
            },
            {
                "code": "920",
                "name": "SUPPORT TO NON- GOVERNMENTAL ORGANISATIONS (NGOs)",
                "description": "In the donor country.",
                "status": "withdrawn"
            },
            {
                "code": "930",
                "name": "Refugees in Donor Countries",
                "status": "active",
                "description": None
            },
            {
                "code": "998",
                "name": "Unallocated / Unspecified",
                "description": "Contributions to general development of the recipient should be included under programme assistance (51010).",  # NOQA: E501
                "status": "active"
            }
        ],
        "PolicyMarker": [
            {
                "code": "1",
                "name": "Gender Equality",
                "status": "active"
            },
            {
                "code": "2",
                "name": "Aid to Environment",
                "status": "active"
            },
            {
                "code": "3",
                "name": "Participatory Development/Good Governance",
                "status": "active"
            },
            {
                "code": "4",
                "name": "Trade Development",
                "status": "active"
            },
            {
                "code": "5",
                "name": "Aid Targeting the Objectives of the Convention on Biological Diversity",
                "status": "active"
            },
            {
                "code": "6",
                "name": "Aid Targeting the Objectives of the Framework Convention on Climate Change - Mitigation",
                "status": "active"
            },
            {
                "code": "7",
                "name": "Aid Targeting the Objectives of the Framework Convention on Climate Change - Adaptation",
                "status": "active"
            },
            {
                "code": "8",
                "name": "Aid Targeting the Objectives of the Convention to Combat Desertification",
                "status": "active"
            },
            {
                "code": "9",
                "name": "Reproductive, Maternal, Newborn and Child Health (RMNCH)",
                "status": "active"
            },
            {
                "code": "10",
                "name": "Disaster Risk Reduction(DRR)",
                "status": "active"
            },
            {
                "code": "11",
                "name": "Disability",
                "status": "active"
            },
            {
                "code": "12",
                "name": "Nutrition",
                "status": "active"
            }
        ],
        "PolicySignificance": [
            {
                "code": "0",
                "name": "not targeted",
                "description": "The score \"not targeted\" means that the activity was examined but found not to target the policy objective.",  # NOQA: E501
                "status": "active"
            },
            {
                "code": "1",
                "name": "significant objective",
                "description": "Significant (secondary) policy objectives are those which, although important, were not the prime motivation for undertaking the activity.",  # NOQA: E501
                "status": "active"
            },
            {
                "code": "2",
                "name": "principal objective",
                "description": "Principal (primary) policy objectives are those which can be identified as being fundamental in the design and impact of the activity and which are an explicit objective of the activity. They may be selected by answering the question \"Would the activity have been undertaken without this objective?\"",  # NOQA: E501
                "status": "active"
            },
            {
                "code": "3",
                "name": "principal objective AND in support of an action programme",
                "description": "For desertification-related aid only",
                "status": "active"
            },
            {
                "code": "4",
                "name": "Explicit primary objective",
                "status": "active",
                "description": None
            }
        ],
        "PolicyMarkerVocabulary": [
            {
                "code": "1",
                "name": "OECD DAC CRS",
                "description": "The policy marker is an OECD DAC CRS policy marker, Reported in columns 20-23, 28-31 and 54 of CRS++ reporting format.",  # NOQA: E501
                "url": "https://reference.iatistandard.org/codelists/PolicyMarker/",
                "status": "active"
            },
            {
                "code": "99",
                "name": "Reporting Organisation",
                "description": "The policy marker is one that is defined and tracked by the reporting organisation",
                "status": "active",
                "url": None
            }
        ]
    }
    # mock codelists class init to set self.codelists_dict to `data`
    monkeypatch.setattr(codelists.Codelists, "__init__", lambda x, y: setattr(x, "codelists_dict", data))
    return codelists.Codelists()
