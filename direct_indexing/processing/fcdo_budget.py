import datetime
import json
import logging
import os
from copy import deepcopy

from django.conf import settings

from direct_indexing.util import index_to_core

BASE_FCDO_BUDGET = {
    "iati-identifier": '',  # non_case_sensitive
    "h1-activity": '',  # text_general_single
    "h2-activity": '',  # text_general_single
    "recipient-country.code": '',  # text_general_single
    "recipient-country.name": '',  # text_general_single
    "recipient-region.code": '',  # text_general_single
    "recipient-region.name": '',  # text_general_single
    "reporting-org.ref": '',  # text_general_single
    "dac5-sector.code": '',  # pint
    "dac5-sector.name": '',  # text_general_single
    "dac3-sector.code": '',  # pint
    "dac3-sector.name": '',  # text_general_single
    "sector.code": '',  # pint, alternative to DAC5/DAC3 option to remain true to simple `sector` fields
    "sector.narrative": '',  # text_general_single, same as sector.code
    "budget.value-gbp": '',  # pdouble
    "budget.type": '',  # pint
    "budget.period-start.iso-date": '',  # pdate
    "budget.period-end.iso-date": '',  # pdate
    "dataset.id": '',  # text_general_single
    "dataset.name": '',  # text_general_single
    "dataset.resources.hash": '',  # text_general_single
}
DAC5 = {
    11110: "Education policy and administrative management",
    11120: "Education facilities and training",
    11130: "Teacher training",
    11182: "Educational research",
    11220: "Primary education",
    11230: "Basic life skills for adults",
    11231: "Basic life skills for youth",
    11232: "Primary education equivalent for adults",
    11240: "Early childhood education",
    11250: "School feeding",
    11260: "Lower secondary education",
    11320: "Upper Secondary Education (modified and includes data from 11322)",
    11321: "Lower secondary education",
    11322: "Upper secondary education",
    11330: "Vocational training",
    11420: "Higher education",
    11430: "Advanced technical and managerial training",
    12110: "Health policy and administrative management",
    12181: "Medical education/training",
    12182: "Medical research",
    12191: "Medical services",
    12196: "Health statistics and data",
    12220: "Basic health care",
    12230: "Basic health infrastructure",
    12240: "Basic nutrition",
    12250: "Infectious disease control",
    12261: "Health education",
    12262: "Malaria control",
    12263: "Tuberculosis control",
    12264: "COVID-19 control",
    12281: "Health personnel development",
    12310: "NCDs control, general",
    12320: "Tobacco use control",
    12330: "Control of harmful use of alcohol and drugs",
    12340: "Promotion of mental health and well-being",
    12350: "Other prevention and treatment of NCDs",
    12382: "Research for prevention and control of NCDs",
    13010: "Population policy and administrative management",
    13020: "Reproductive health care",
    13030: "Family planning",
    13040: "STD control including HIV/AIDS",
    13081: "Personnel development for population and reproductive health",
    13096: "Population statistics and data",
    14010: "Water sector policy and administrative management",
    14015: "Water resources conservation (including data collection)",
    14020: "Water supply and sanitation - large systems",
    14021: "Water supply - large systems",
    14022: "Sanitation - large systems",
    14030: "Basic drinking water supply and basic sanitation",
    14031: "Basic drinking water supply",
    14032: "Basic sanitation",
    14040: "River basins development",
    14050: "Waste management/disposal",
    14081: "Education and training in water supply and sanitation",
    15110: "Public sector policy and administrative management",
    15111: "Public finance management (PFM)",
    15112: "Decentralisation and support to subnational government",
    15113: "Anti-corruption organisations and institutions",
    15114: "Domestic revenue mobilisation",
    15116: "Tax collection",
    15117: "Budget planning",
    15118: "National audit",
    15119: "Debt and aid management",
    15120: "Public sector financial management",
    15121: "Foreign affairs",
    15122: "Diplomatic missions",
    15123: "Administration of developing countries' foreign aid",
    15124: "General personnel services",
    15125: "Public Procurement",
    15126: "Other general public services",
    15127: "National monitoring and evaluation",
    15128: "Local government finance",
    15129: "Other central transfers to institutions",
    15130: "Legal and judicial development",
    15131: "Justice, law and order policy, planning and administration",
    15132: "Police",
    15133: "Fire and rescue services",
    15134: "Judicial affairs",
    15135: "Ombudsman",
    15136: "Immigration",
    15137: "Prisons",
    15142: "Macroeconomic policy",
    15143: "Meteorological services",
    15144: "National standards development",
    15150: "Democratic participation and civil society",
    15151: "Elections",
    15152: "Legislatures and political parties",
    15153: "Media and free flow of information",
    15154: "Executive office",
    15155: "Tax policy and administration support",
    15160: "Human rights",
    15161: "Elections",
    15162: "Human rights",
    15163: "Free flow of information",
    15164: "Women's equality organisations and institutions",
    15170: "Women's rights organisations and movements, and government institutions",
    15180: "Ending violence against women and girls",
    15185: "Local government administration",
    15190: "Facilitation of orderly, safe, regular and responsible migration and mobility",
    15196: "Government and civil society statistics and data",
    15210: "Security system management and reform",
    15220: "Civilian peace-building, conflict prevention and resolution",
    15230: "Participation in international peacekeeping operations",
    15240: "Reintegration and SALW control",
    15250: "Removal of land mines and explosive remnants of war",
    15261: "Child soldiers (prevention and demobilisation)",
    16010: "Social Protection",
    16011: "Social protection and welfare services policy, planning and administration",
    16012: "Social security (excl pensions)",
    16013: "General pensions",
    16014: "Civil service pensions",
    16015: "Social services (incl youth development and women+ children)",
    16020: "Employment creation",
    16030: "Housing policy and administrative management",
    16040: "Low-cost housing",
    16050: "Multisector aid for basic social services",
    16061: "Culture and recreation",
    16062: "Statistical capacity building",
    16063: "Narcotics control",
    16064: "Social mitigation of HIV/AIDS",
    16065: "Recreation and sport",
    16080: "Social dialogue",
    21010: "Transport policy and administrative management",
    21011: "Transport policy, planning and administration",
    21012: "Public transport services",
    21013: "Transport regulation",
    21020: "Road transport",
    21021: "Feeder road construction",
    21022: "Feeder road maintenance",
    21023: "National road construction",
    21024: "National road maintenance",
    21030: "Rail transport",
    21040: "Water transport",
    21050: "Air transport",
    21061: "Storage",
    21081: "Education and training in transport and storage",
    22011: "Communications policy, planning and administration",
    22013: "Information services",
    22020: "Telecommunications",
    22030: "Radio/television/print media",
    22040: "Information and communication technology (ICT)",
    23010: "Energy policy and administrative management",
    23020: "Power generation/non-renewable sources",
    23030: "Power generation/renewable sources",
    23040: "Electrical transmission/ distribution",
    23050: "Gas distribution",
    23061: "Oil-fired power plants",
    23062: "Gas-fired power plants",
    23065: "Hydro-electric power plants",
    23066: "Geothermal energy",
    23068: "Wind power",
    23069: "Ocean power",
    23070: "Biomass",
    23081: "Energy education/training",
    23082: "Energy research",
    23110: "Energy policy and administrative management",
    23111: "Energy sector policy, planning and administration",
    23181: "Energy education/training",
    23182: "Energy research",
    23183: "Energy conservation and demand-side efficiency",
    23210: "Energy generation, renewable sources - multiple technologies",
    23220: "Hydro-electric power plants",
    23230: "Solar energy for centralised grids",
    23231: "Solar energy for isolated grids and standalone systems",
    23232: "Solar energy - thermal applications",
    23240: "Wind energy",
    23250: "Marine energy",
    23260: "Geothermal energy",
    23270: "Biofuel-fired power plants",
    23310: "Energy generation, non-renewable sources, unspecified",
    23320: "Coal-fired electric power plants",
    23330: "Oil-fired electric power plants",
    23340: "Natural gas-fired electric power plants",
    23350: "Fossil fuel electric power plants with carbon capture and storage (CCS)",
    23360: "Non-renewable waste-fired electric power plants",
    23410: "Hybrid energy electric power plants",
    23510: "Nuclear energy electric power plants and nuclear safety",
    23610: "Heat plants",
    23620: "District heating and cooling",
    23630: "Electric power transmission and distribution (centralised grids)",
    23631: "Electric power transmission and distribution (isolated mini-grids)",
    23640: "Retail gas distribution",
    23641: "Retail distribution of liquid or solid fossil fuels",
    24010: "Financial policy and administrative management",
    24020: "Monetary institutions",
    24030: "Formal sector financial intermediaries",
    24040: "Informal/semi-formal financial intermediaries",
    24050: "Remittance facilitation, promotion and optimisation",
    24081: "Education/training in banking and financial services",
    25020: "Privatisation",
    25030: "Business development services",
    25040: "Responsible business conduct",
    31110: "Agricultural policy and administrative management",
    31120: "Agricultural development",
    31130: "Agricultural land resources",
    31140: "Agricultural water resources",
    31150: "Agricultural inputs",
    31161: "Food crop production",
    31162: "Industrial crops/export crops",
    31163: "Livestock",
    31164: "Agrarian reform",
    31165: "Agricultural alternative development",
    31166: "Agricultural extension",
    31181: "Agricultural education/training",
    31191: "Agricultural services",
    31192: "Plant and post-harvest protection and pest control",
    31193: "Agricultural financial services",
    31194: "Agricultural co-operatives",
    31195: "Livestock/veterinary services",
    31210: "Forestry policy and administrative management",
    31220: "Forestry development",
    31261: "Fuelwood/charcoal",
    31281: "Forestry education/training",
    31291: "Forestry services",
    31320: "Fishery development",
    31381: "Fishery education/training",
    31391: "Fishery services",
    32110: "Industrial policy and administrative management",
    32120: "Industrial development",
    32140: "Cottage industries and handicraft",
    32162: "Forest industries",
    32163: "Textiles, leather and substitutes",
    32164: "Chemicals",
    32165: "Fertilizer plants",
    32168: "Pharmaceutical production",
    32169: "Basic metal industries",
    32170: "Non-ferrous metal industries",
    32172: "Transport equipment industry",
    32173: "Modern biofuels manufacturing",
    32174: "Clean cooking appliances manufacturing",
    32182: "Technological research and development",
    32210: "Mineral/mining policy and administrative management",
    32220: "Mineral prospection and exploration",
    32261: "Coal",
    32262: "Oil and gas (upstream)",
    32263: "Ferrous metals",
    32264: "Nonferrous metals",
    32265: "Precious metals/materials",
    32266: "Industrial minerals",
    32267: "Fertilizer minerals",
    32268: "Offshore minerals",
    32310: "Construction policy and administrative management",
    33110: "Trade policy and administrative management",
    33120: "Trade facilitation",
    33130: "Regional trade agreements (RTAs)",
    33140: "Multilateral trade negotiations",
    33150: "Trade-related adjustment",
    33181: "Trade education/training",
    33210: "Tourism policy and administrative management",
    41020: "Biosphere protection",
    41030: "Biodiversity",
    41040: "Site preservation",
    41050: "Flood prevention/control",
    41081: "Environmental education/training",
    43010: "Multisector aid",
    43031: "Urban land policy and management",
    43032: "Urban development",
    43040: "Rural development",
    43041: "Rural land policy and management",
    43042: "Rural development",
    43050: "Non-agricultural alternative development",
    43060: "Disaster Risk Reduction",
    43071: "Food security policy and administrative management",
    43072: "Household food security programmes",
    43073: "Food safety and quality",
    43081: "Multisector education/training",
    43082: "Research/scientific institutions",
    51010: "General budget support-related aid",
    52010: "Food assistance",
    53030: "Import support (capital goods)",
    53040: "Import support (commodities)",
    60010: "Action relating to debt",
    60020: "Debt forgiveness",
    60040: "Rescheduling and refinancing",
    60062: "Other debt swap",
    60063: "Debt buy-back",
    72010: "Material relief assistance and services",
    72011: "Basic Health Care Services in Emergencies",
    72012: "Education in emergencies",
    72040: "Emergency food assistance",
    72050: "Relief co-ordination and support services",
    73010: "Immediate post-emergency reconstruction and rehabilitation",
    74010: "Disaster prevention and preparedness",
    74020: "Multi-hazard response preparedness",
    91010: "Administrative costs (non-sector allocable)",
    92020: "Support to international NGOs",
    93010: "Refugees/asylum seekers in donor countries (non-sector allocable)",
    93011: "Refugees/asylum seekers in donor countries - food and shelter",
    93012: "Refugees/asylum seekers in donor countries - training",
    93013: "Refugees/asylum seekers in donor countries - health",
    93014: "Refugees/asylum seekers in donor countries - other temporary sustenance",
    93015: "Refugees/asylum seekers in donor countries - voluntary repatriation",
    93016: "Refugees/asylum seekers in donor countries - transport",
    93017: "Refugees/asylum seekers in donor countries - rescue at sea",
    93018: "Refugees/asylum seekers in donor countries - administrative costs",
    99810: "Sectors not specified",
    99820: "Promotion of development awareness (non-sector allocable)",
}
DAC3 = {
    111: "Education, Level Unspecified",
    112: "Basic Education",
    113: "Secondary Education",
    114: "Post-Secondary Education",
    121: "Health, General",
    122: "Basic Health",
    123: "Non-communicable diseases (NCDs)",
    130: "Population Policies/Programmes & Reproductive Health",
    140: "Water Supply & Sanitation",
    151: "Government & Civil Society-general",
    152: "Conflict, Peace & Security",
    160: "Other Social Infrastructure & Services",
    210: "Transport & Storage",
    220: "Communications",
    230: "ENERGY GENERATION AND SUPPLY",
    231: "Energy Policy",
    232: "Energy generation, renewable sources",
    233: "Energy generation, non-renewable sources",
    234: "Hybrid energy plants",
    235: "Nuclear energy plants",
    236: "Energy distribution",
    240: "Banking & Financial Services",
    250: "Business & Other Services",
    311: "Agriculture",
    312: "Forestry",
    313: "Fishing",
    321: "Industry",
    322: "Mineral Resources & Mining",
    323: "Construction",
    331: "Trade Policies & Regulations",
    332: "Tourism",
    410: "General Environment Protection",
    430: "Other Multisector",
    510: "General Budget Support",
    520: "Development Food Assistance",
    530: "Other Commodity Assistance",
    600: "Action Relating to Debt",
    720: "Emergency Response",
    730: "Reconstruction Relief & Rehabilitation",
    740: "Disaster Prevention & Preparedness",
    910: "Administrative Costs of Donors",
    920: "SUPPORT TO NON- GOVERNMENTAL ORGANISATIONS (NGOs)",
    930: "Refugees in Donor Countries",
    998: "Unallocated / Unspecified",
}
REGIONS = {
    88: "States Ex-Yugoslavia unspecified",
    89: "Europe, regional",
    189: "North of Sahara, regional",
    289: "South of Sahara, regional",
    298: "Africa, regional",
    380: "West Indies, regional",
    389: "Caribbean & Central America, regional",
    489: "South America, regional",
    498: "America, regional",
    589: "Middle East, regional",
    619: "Central Asia, regional",
    679: "South Asia, regional",
    689: "South & Central Asia, regional",
    789: "Far East Asia, regional",
    798: "Asia, regional",
    889: "Oceania, regional",
    998: "Developing countries, unspecified",
    1027: "Eastern Africa, regional",
    1028: "Middle Africa, regional",
    1029: "Southern Africa, regional",
    1030: "Western Africa, regional",
    1031: "Caribbean, regional",
    1032: "Central America, regional",
    1033: "Melanesia, regional",
    1034: "Micronesia, regional",
    1035: "Polynesia, regional"
}
COUNTRIES = {
    "AF": "Afghanistan",
    "AX": "\u00c5land Islands",
    "AL": "Albania",
    "DZ": "Algeria",
    "AS": "American Samoa",
    "AD": "Andorra",
    "AO": "Angola",
    "AI": "Anguilla",
    "AQ": "Antarctica",
    "AG": "Antigua and Barbuda",
    "AR": "Argentina",
    "AM": "Armenia",
    "AW": "Aruba",
    "AU": "Australia",
    "AT": "Austria",
    "AZ": "Azerbaijan",
    "BS": "Bahamas (the)",
    "BH": "Bahrain",
    "BD": "Bangladesh",
    "BB": "Barbados",
    "BY": "Belarus",
    "BE": "Belgium",
    "BZ": "Belize",
    "BJ": "Benin",
    "BM": "Bermuda",
    "BT": "Bhutan",
    "BO": "Bolivia (Plurinational State of)",
    "BQ": "Bonaire, Sint Eustatius and Saba",
    "BA": "Bosnia and Herzegovina",
    "BW": "Botswana",
    "BV": "Bouvet Island",
    "BR": "Brazil",
    "IO": "British Indian Ocean Territory (the)",
    "BN": "Brunei Darussalam",
    "BG": "Bulgaria",
    "BF": "Burkina Faso",
    "BI": "Burundi",
    "KH": "Cambodia",
    "CM": "Cameroon",
    "CA": "Canada",
    "CV": "Cabo Verde",
    "KY": "Cayman Islands (the)",
    "CF": "Central African Republic (the)",
    "TD": "Chad",
    "CL": "Chile",
    "CN": "China",
    "CX": "Christmas Island",
    "CC": "Cocos (Keeling) Islands (the)",
    "CO": "Colombia",
    "KM": "Comoros (the)",
    "CG": "Congo (the)",
    "CD": "Congo (the Democratic Republic of the)",
    "CK": "Cook Islands (the)",
    "CR": "Costa Rica",
    "CI": "C\u00f4te d'Ivoire",
    "HR": "Croatia",
    "CU": "Cuba",
    "CW": "Cura\u00e7ao",
    "CY": "Cyprus",
    "CZ": "Czechia",
    "DK": "Denmark",
    "DJ": "Djibouti",
    "DM": "Dominica",
    "DO": "Dominican Republic (the)",
    "EC": "Ecuador",
    "EG": "Egypt",
    "SV": "El Salvador",
    "GQ": "Equatorial Guinea",
    "ER": "Eritrea",
    "EE": "Estonia",
    "ET": "Ethiopia",
    "FK": "Falkland Islands (the) [Malvinas]",
    "FO": "Faroe Islands (the)",
    "FJ": "Fiji",
    "FI": "Finland",
    "FR": "France",
    "GF": "French Guiana",
    "PF": "French Polynesia",
    "TF": "French Southern Territories (the)",
    "GA": "Gabon",
    "GM": "Gambia (the)",
    "GE": "Georgia",
    "DE": "Germany",
    "GH": "Ghana",
    "GI": "Gibraltar",
    "GR": "Greece",
    "GL": "Greenland",
    "GD": "Grenada",
    "GP": "Guadeloupe",
    "GU": "Guam",
    "GT": "Guatemala",
    "GG": "Guernsey",
    "GN": "Guinea",
    "GW": "Guinea-Bissau",
    "GY": "Guyana",
    "HT": "Haiti",
    "HM": "Heard Island and McDonald Islands",
    "VA": "Holy See (the)",
    "HN": "Honduras",
    "HK": "Hong Kong",
    "HU": "Hungary",
    "IS": "Iceland",
    "IN": "India",
    "ID": "Indonesia",
    "IR": "Iran (Islamic Republic of)",
    "IQ": "Iraq",
    "IE": "Ireland",
    "IM": "Isle of Man",
    "IL": "Israel",
    "IT": "Italy",
    "JM": "Jamaica",
    "JP": "Japan",
    "JE": "Jersey",
    "JO": "Jordan",
    "KZ": "Kazakhstan",
    "KE": "Kenya",
    "KI": "Kiribati",
    "KP": "Korea (the Democratic People's Republic of)",
    "KR": "Korea (the Republic of)",
    "XK": "Kosovo",
    "KW": "Kuwait",
    "KG": "Kyrgyzstan",
    "LA": "Lao People's Democratic Republic (the)",
    "LV": "Latvia",
    "LB": "Lebanon",
    "LS": "Lesotho",
    "LR": "Liberia",
    "LY": "Libya",
    "LI": "Liechtenstein",
    "LT": "Lithuania",
    "LU": "Luxembourg",
    "MO": "Macao",
    "MK": "North Macedonia",
    "MG": "Madagascar",
    "MW": "Malawi",
    "MY": "Malaysia",
    "MV": "Maldives",
    "ML": "Mali",
    "MT": "Malta",
    "MH": "Marshall Islands (the)",
    "MQ": "Martinique",
    "MR": "Mauritania",
    "MU": "Mauritius",
    "YT": "Mayotte",
    "MX": "Mexico",
    "FM": "Micronesia (Federated States of)",
    "MD": "Moldova (the Republic of)",
    "MC": "Monaco",
    "MN": "Mongolia",
    "ME": "Montenegro",
    "MS": "Montserrat",
    "MA": "Morocco",
    "MZ": "Mozambique",
    "MM": "Myanmar",
    "NA": "Namibia",
    "NR": "Nauru",
    "NP": "Nepal",
    "NL": "Netherlands (the)",
    "AN": "NETHERLAND ANTILLES",
    "NC": "New Caledonia",
    "NZ": "New Zealand",
    "NI": "Nicaragua",
    "NE": "Niger (the)",
    "NG": "Nigeria",
    "NU": "Niue",
    "NF": "Norfolk Island",
    "MP": "Northern Mariana Islands (the)",
    "NO": "Norway",
    "OM": "Oman",
    "PK": "Pakistan",
    "PW": "Palau",
    "PS": "Palestine, State of",
    "PA": "Panama",
    "PG": "Papua New Guinea",
    "PY": "Paraguay",
    "PE": "Peru",
    "PH": "Philippines (the)",
    "PN": "Pitcairn",
    "PL": "Poland",
    "PT": "Portugal",
    "PR": "Puerto Rico",
    "QA": "Qatar",
    "RE": "R\u00e9union",
    "RO": "Romania",
    "RU": "Russian Federation (the)",
    "RW": "Rwanda",
    "BL": "Saint Barth\u00e9lemy",
    "SH": "Saint Helena, Ascension and Tristan da Cunha",
    "KN": "Saint Kitts and Nevis",
    "LC": "Saint Lucia",
    "MF": "Saint Martin (French part)",
    "PM": "Saint Pierre and Miquelon",
    "VC": "Saint Vincent and the Grenadines",
    "WS": "Samoa",
    "SM": "San Marino",
    "ST": "Sao Tome and Principe",
    "SA": "Saudi Arabia",
    "SN": "Senegal",
    "RS": "Serbia",
    "SC": "Seychelles",
    "SL": "Sierra Leone",
    "SG": "Singapore",
    "SX": "Sint Maarten (Dutch part)",
    "SK": "Slovakia",
    "SI": "Slovenia",
    "SB": "Solomon Islands",
    "SO": "Somalia",
    "ZA": "South Africa",
    "GS": "South Georgia and the South Sandwich Islands",
    "SS": "South Sudan",
    "ES": "Spain",
    "LK": "Sri Lanka",
    "SD": "Sudan (the)",
    "SR": "Suriname",
    "SJ": "Svalbard and Jan Mayen",
    "SZ": "Eswatini",
    "SE": "Sweden",
    "CH": "Switzerland",
    "SY": "Syrian Arab Republic (the)",
    "TW": "Taiwan (Province of China)",
    "TJ": "Tajikistan",
    "TZ": "Tanzania, the United Republic of",
    "TH": "Thailand",
    "TL": "Timor-Leste",
    "TG": "Togo",
    "TK": "Tokelau",
    "TO": "Tonga",
    "TT": "Trinidad and Tobago",
    "TN": "Tunisia",
    "TR": "T\u00fcrkiye",
    "TM": "Turkmenistan",
    "TC": "Turks and Caicos Islands (the)",
    "TV": "Tuvalu",
    "UG": "Uganda",
    "UA": "Ukraine",
    "AE": "United Arab Emirates (the)",
    "GB": "United Kingdom of Great Britain and Northern Ireland (the)",
    "US": "United States of America (the)",
    "UM": "United States Minor Outlying Islands (the)",
    "UY": "Uruguay",
    "UZ": "Uzbekistan",
    "VU": "Vanuatu",
    "VE": "Venezuela (Bolivarian Republic of)",
    "VN": "Viet Nam",
    "VG": "Virgin Islands (British)",
    "VI": "Virgin Islands (U.S.)",
    "WF": "Wallis and Futuna",
    "EH": "Western Sahara",
    "YE": "Yemen",
    "ZM": "Zambia",
    "ZW": "Zimbabwe",
}


def fcdo_budget(filetype, data, json_path, currencies):
    """Entrypoint of this function is the end of dataset_processing.fun -> index_dataset ->
    convert_and_save_xml_to_processed_json, where we have added dataset metadata and
    all custom fields to the dataset.

    Args:
        filetype (string): "activity" or "organisation" identifying whether or not there are budgets
        data (dict): containing all processed IATI activities
        json_path (string): location where the dataset is saved, to be used to save the fcdo_budget.json
        currencies (dict): containing all known currencies and their exchange rates
    """
    # Skip organisation datasets, as there are no budgets.
    if filetype == "organisation":
        logging.info("Skipping organisation dataset.")
    # Create a json filepath for eventual storage of the fcdo_budget.json
    fcdo_budget_filepath = f'{os.path.splitext(json_path)[0]}_fcdo_budget.json'
    all_fcdo_budgets = []
    data = data if isinstance(data, list) else [data]
    for activity in data:
        budgets = activity.get('budget', [])
        budgets = budgets if isinstance(budgets, list) else [budgets]
        if not budgets:
            continue  # Skip if there is no budget in this activity
        try:
            _fcdo_budget_process_activity(activity, budgets, all_fcdo_budgets, currencies)
        except Exception as e:
            logging.error(f"Error processing fcdo_budget for dataset {activity.get('dataset.name', '')} activity {activity.get('iati-identifier', '')}: {e}")  # NOQA: E501
    # Save the fcdo_budget.json file
    with open(fcdo_budget_filepath, 'w', encoding='utf-8') as f:
        json.dump(all_fcdo_budgets, f)
    # Index the fcdo_budget.json file
    try:
        index_to_core(settings.SOLR_FCDO_BUDGET_URL, fcdo_budget_filepath, remove=True)
    except Exception as e:
        logging.error(f"Error indexing fcdo_budget.json for dataset {activity.get('dataset.name', '')} activity {activity.get('iati-identifier', '')}: {e}")  # NOQA: E501


def _fcdo_budget_process_activity(activity, budgets, all_fcdo_budgets, currencies):
    """Extracted from the main function to process each activity and its budgets.
    For the activity, get the main data, and for each budget, get the budget value.

    Args:
        activity (dict): activity data
        budgets (list): all budgets in the given activity
        all_fcdo_budgets (list): central list reference for all fcdo budgets to be stored
        currencies (dict): containing all known currencies and their exchange rates
    """
    iati_id = activity.get('iati-identifier', '')  # Can never be empty
    hierarchy = activity.get('hierarchy', 1)  # Can be empty, defaults to 1
    recipient_country = activity.get('recipient-country', [])  # Can be empty
    recipient_country = recipient_country if isinstance(recipient_country, list) else [recipient_country]
    recipient_region = activity.get('recipient-region', [])  # Can be empty
    recipient_region = recipient_region if isinstance(recipient_region, list) else [recipient_region]
    recipient = _set_default_percentage(recipient_country + recipient_region)
    reporting_org_ref = activity.get('reporting-org.ref', '')  # Should never be empty
    # Can be empty, if empty, sector is reported at transaction level,
    # but in that case, is not relevant to the budget
    sector = activity.get('sector', [])
    sector = sector if isinstance(sector, list) else [sector]
    sector = _set_default_percentage(sector)
    related_parent = _get_parent_activity(activity.get('related-activity', []))
    dataset_id = activity.get('dataset.id', "ID_NOT_FOUND")
    dataset_name = activity.get('dataset.name', "NAME_NOT_FOUND")
    dataset_resources_hash = activity.get('dataset.resources.hash', "HASH_NOT_FOUND")
    for budget in budgets:
        budget_gbp = _get_budget_value(budget, activity.get('default-currency', 'GBP'), currencies)
        if not budget_gbp:
            # Budget is not valid, skipping
            continue
        budget_start = budget.get('period-start', activity.get('start-iso-date', None))
        budget_end = budget.get('period-end', activity.get('end-iso-date', None))
        budget_type = budget.get('type', 1)
        if not budget_start or not budget_end:
            # Budget does not have a start or end date, even through it is a required field. Skip it.
            continue
        distributed_budget = _distribute_budget(budget_gbp, recipient, sector)
        for db in distributed_budget:
            _create_fcdo_budget_item(iati_id, hierarchy, db, budget_type, budget_start, budget_end, dataset_id,
                                     dataset_name, dataset_resources_hash, all_fcdo_budgets, related_parent,
                                     reporting_org_ref)


def _get_budget_value(budget, default_currency, currencies):
    """Get the currency of the budget value,
    if not present, get the activity default currency,
    if not present default to GBP.

    Args:
        budget (dict): IATI budget data
        default_currency (string): the default currency found in the IATI activity
        currencies (dict): containing all known currencies and their exchange rates

    Returns:
        float | none: distributed budget value in GBP or None if not valid
    """
    budget_value = budget.get('value', 0)
    budget_value_currency = budget.get('value.currency', default_currency)
    if budget_value_currency == 'GBP':
        budget_gbp = budget_value
    else:
        budget_value_value_date = budget.get('value.value-date', None)
        if not budget_value_value_date:
            # Budget does not have a value date, even through it is a required field. Skip it.
            return None
        budget_gbp = _convert_to_gbp(budget_value, budget_value_currency, budget_value_value_date, currencies)
    return budget_gbp


def _convert_to_gbp(budget_value, budget_value_currency, budget_value_value_date, currencies):
    """Convert the provided budget value to GBP for the provided currency and date.

    Args:
        budget_value (float): The budget value
        budget_value_currency (string): The budget currency
        budget_value_value_date (ISO date): The IATI budget's value date
        currencies (dict): containing all known currencies and their exchange rates

    Returns:
        float: the budget value converted to GBP at the provided date.
    """
    if budget_value_value_date is None or budget_value_value_date == '':
        return None, None
    # Exclude malformed budget_value_value_dates
    if '-' in budget_value_value_date[:4] or '-' in budget_value_value_date[5:7]:
        return None, None
    year = int(budget_value_value_date[:4])
    month = int(budget_value_value_date[5:7])
    now = datetime.datetime.now()
    if year > now.year:
        year = now.year
        month = now.month
    if year == now.year and month > now.month:
        month = now.month

    converted_value, _ = currencies.convert_currency(
        budget_value_currency, 'GBP', budget_value, month, year)

    return converted_value


def _set_default_percentage(targets):
    """Set default percentage to 100 / len(targets) for each target in targets.

    Args:
        targets (list): List of targets.

    Returns:
        list: List of targets with default percentage set.
    """
    if not targets:
        return
    default_percentage = 100 / len(targets)
    for target in targets:
        target.setdefault('percentage', default_percentage)
    return targets


def _get_parent_activity(related_activities):
    """Return the first parent activity found in the list of related activities.

    Args:
        related_activities (list | dict): the list of dicts (or dict) of related activities

    Returns:
        string | None: the ref of the first parent activity found, or None if not found
    """
    if not related_activities:
        return None
    if isinstance(related_activities, dict):
        related_activities = [related_activities]
    for related_activity in related_activities:
        # Requested was single valued ref for the parent activity if exists, so return the first encountered instance.
        if related_activity.get('type', '0') == '1' or related_activity.get('type', 0) == 1:
            return related_activity.get('ref', None)
    return None


def _distribute_budget(total_budget, recipients, sectors):
    """Distribute budget to recipients and sectors based on their percentage.

    Args:
        total_budget (float): Total budget.
        recipients (list): List of recipients with their percentage.
        sectors (list): List of sectors with their percentage.
c
    Returns:
        dict: Dictionary with distributed budget for each recipient and sector.
    """
    if not recipients and not sectors:
        return [{
            'recipient_code': '',
            'sector_code': '',
            'amount': round(total_budget, 2)
        }]

    budgets = []
    # Ensure there is at least one recipient and sector, if not, add a default empty one
    recipient_list = recipients or [{'code': '', 'percentage': 100}]
    sector_list = sectors or [{'code': '', 'percentage': 100}]

    # For every recipient and sector, calculate the budget
    for rec in recipient_list:
        rec_code = rec.get('code')
        rec_pct = rec.get('percentage', 100 / len(recipient_list)) / 100
        for sec in sector_list:
            sec_code = sec.get('code')
            sec_pct = sec.get('percentage', 100 / len(sector_list)) / 100
            _distribute_budget_append(budgets, total_budget, rec_code, rec_pct, sec_code, sec_pct)

    return budgets


def _distribute_budget_append(budgets, total_budget, rec_code, rec_pct, sec_code, sec_pct):
    """Function that takes the budget value, recipient and sector data,
    and creates a distributed budget object.

    Args:
        budgets (list): reference to the list of budgets created
        total_budget (float): budget value
        rec_code (string): recipient code, can be country or region
        rec_pct (float): the percentage of the budget that goes to this recipient
        sec_code (string): sector code, can be DAC5 or DAC3
        sec_pct (float): the percentage of the budget that goes to this sector
    """
    amount = total_budget * rec_pct * sec_pct
    budgets.append({
        'recipient_code': rec_code or '',
        'sector_code': sec_code or '',
        'amount': round(amount, 2)
    })


def _create_fcdo_budget_item(iati_id, hierarchy, db, budget_type, budget_start, budget_end, dataset_id, dataset_name,
                             dataset_resources_hash, all_fcdo_budgets, related_parent, reporting_org_ref):
    """Extracted from the main function to create a fcdo budget item.
    Takes the input data and inserts it into a copy of the base fcdo budget item.

    Args:
        iati_id (string): IATI identifier
        hierarchy (int): IATI activity hierarchy
        db (dict): distributed budget data
        budget_type (int): IATI budget type related to db
        budget_start (ISO date): IATI budget start date related to db
        budget_end (ISO date): IATI budget end date related to db
        dataset_id (string): IATI Dataset id
        dataset_name (string): IATI Dataset name
        dataset_resources_hash (string): IATI Dataset hash
        all_fcdo_budgets (list): reference to the list of fcdo budget items created.
        related_parent (string): the ref of the parent activity if exists
        reporting_org_ref (string): the ref of the reporting organisation
    """
    item = deepcopy(BASE_FCDO_BUDGET)
    item['iati-identifier'] = iati_id
    if hierarchy == 1:
        item['h1-activity'] = iati_id
        item['h2-activity'] = ''
    elif hierarchy == 2:
        item['h1-activity'] = related_parent if related_parent else ''
        item['h2-activity'] = iati_id
    recip_code = db.get('recipient_code', '')
    if recip_code in COUNTRIES:
        item['recipient-country.code'] = recip_code
        item['recipient-country.name'] = COUNTRIES.get(recip_code, '')
    if recip_code in REGIONS:
        item['recipient-region.code'] = recip_code
        item['recipient-region.name'] = REGIONS.get(recip_code, '')
    item["reporting-org.ref"] = reporting_org_ref
    sector_code = db.get('sector_code', '')
    dac3_name = DAC3.get(sector_code, '')
    dac5_name = DAC5.get(sector_code, '')
    if sector_code in DAC5:
        item['dac5-sector.code'] = sector_code
        item['dac5-sector.name'] = dac5_name
    if sector_code in DAC3:
        item['dac3-sector.code'] = sector_code
        item['dac3-sector.name'] = dac3_name
    item['sector.code'] = sector_code
    item['sector.narrative'] = dac3_name if dac3_name else dac5_name  # if both are empty, defaulkts to empty
    item["budget.value-gbp"] = round(db.get('amount', 0), 2)
    item["budget.type"] = budget_type
    item["budget.period-start.iso-date"] = budget_start
    item["budget.period-end.iso-date"] = budget_end
    item["dataset.id"] = dataset_id
    item["dataset.name"] = dataset_name
    item["dataset.resources.hash"] = dataset_resources_hash
    all_fcdo_budgets.append(item)
