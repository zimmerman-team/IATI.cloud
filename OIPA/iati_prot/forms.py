from django import forms


class activity_date_form(forms.Form):
    iso_date = forms.DateField(blank=True)
    type = forms.CharField(max_length=1000, blank=True)
    narrative = forms.MultipleChoiceField(narrative_model.objects.all())
     = forms.CharField(max_length=1000, blank=True)

class activity_scope_form(forms.Form):
    code = forms.CharField(max_length=1000, blank=True)
     = forms.CharField(max_length=1000, blank=True)

class activity_status_form(forms.Form):
    code = forms.CharField(max_length=1000, blank=True)
     = forms.CharField(max_length=1000, blank=True)

class actualType_form(forms.Form):
    value = forms.CharField(max_length=1000, blank=True)
    comment = forms.MultipleChoiceField(textRequiredType_model.objects.all())
     = forms.CharField(max_length=1000, blank=True)

class administrativeType_form(forms.Form):
    code = forms.CharField(max_length=1000, blank=True)
    vocabulary = forms.CharField(max_length=1000, blank=True)
    level = forms.IntegerField(blank=True)
     = forms.CharField(max_length=1000, blank=True)

class aid_typeType_form(forms.Form):
    code = forms.CharField(max_length=1000, blank=True)
     = forms.CharField(max_length=1000, blank=True)

class baselineType_form(forms.Form):
    value = forms.CharField(max_length=1000, blank=True)
    year = forms.IntegerField(blank=True)
    comment = forms.MultipleChoiceField(textRequiredType_model.objects.all())
     = forms.CharField(max_length=1000, blank=True)

class budget_form(forms.Form):
    type = forms.CharField(max_length=1000, blank=True)
    period_start = forms.MultipleChoiceField(period_startType1_model.objects.all())
    period_end = forms.MultipleChoiceField(period_endType2_model.objects.all())
    value = forms.MultipleChoiceField(currencyType_model.objects.all())
     = forms.CharField(max_length=1000, blank=True)

class budget_itemType_form(forms.Form):
    percentage = forms.FloatField(blank=True)
    code = forms.CharField(max_length=1000, blank=True)
    description = forms.MultipleChoiceField(description_model.objects.all())
     = forms.CharField(max_length=1000, blank=True)

class capital_spend_form(forms.Form):
    percentage = forms.FloatField(blank=True)
     = forms.CharField(max_length=1000, blank=True)

class categoryType_form(forms.Form):
    code = forms.CharField(max_length=1000, blank=True)
     = forms.CharField(max_length=1000, blank=True)

class collaboration_type_form(forms.Form):
    code = forms.CharField(max_length=1000, blank=True)
     = forms.CharField(max_length=1000, blank=True)

class commitment_dateType_form(forms.Form):
    iso_date = forms.DateField(blank=True)
     = forms.CharField(max_length=1000, blank=True)

class conditionType_form(forms.Form):
    type = forms.CharField(max_length=1000, blank=True)
    narrative = forms.MultipleChoiceField(narrative_model.objects.all())
     = forms.CharField(max_length=1000, blank=True)

class conditions_form(forms.Form):
    attached = forms.BooleanField(blank=True)
    condition = forms.MultipleChoiceField(conditionType_model.objects.all())
     = forms.CharField(max_length=1000, blank=True)

class contact_info_form(forms.Form):
    type = forms.CharField(max_length=1000, blank=True)
    organisation = forms.MultipleChoiceField(textRequiredType_model.objects.all())
    department = forms.MultipleChoiceField(textRequiredType_model.objects.all())
    person_name = forms.MultipleChoiceField(textRequiredType_model.objects.all())
    job_title = forms.MultipleChoiceField(textRequiredType_model.objects.all())
    telephone = forms.MultipleChoiceField(telephoneType_model.objects.all())
    email = forms.MultipleChoiceField(emailType_model.objects.all())
    website = forms.MultipleChoiceField(websiteType_model.objects.all())
    mailing_address = forms.MultipleChoiceField(textRequiredType_model.objects.all())
     = forms.CharField(max_length=1000, blank=True)

class country_budget_items_form(forms.Form):
    vocabulary = forms.CharField(max_length=1000, blank=True)
    budget_item = forms.MultipleChoiceField(budget_itemType_model.objects.all())
     = forms.CharField(max_length=1000, blank=True)

class crs_add_form(forms.Form):
    other_flags = forms.MultipleChoiceField(other_flagsType_model.objects.all())
    loan_terms = forms.MultipleChoiceField(loan_termsType_model.objects.all())
    loan_status = forms.MultipleChoiceField(loan_statusType_model.objects.all())
     = forms.CharField(max_length=1000, blank=True)

class currencyType_form(forms.Form):
    currency = forms.CharField(max_length=1000, blank=True)
    value_date = forms.DateField(blank=True)
    valueOf_x = forms.FloatField(blank=True)

class default_aid_type_form(forms.Form):
    code = forms.CharField(max_length=1000, blank=True)
     = forms.CharField(max_length=1000, blank=True)

class default_finance_type_form(forms.Form):
    code = forms.CharField(max_length=1000, blank=True)
     = forms.CharField(max_length=1000, blank=True)

class default_flow_type_form(forms.Form):
    code = forms.CharField(max_length=1000, blank=True)
     = forms.CharField(max_length=1000, blank=True)

class default_tied_status_form(forms.Form):
    code = forms.CharField(max_length=1000, blank=True)
     = forms.CharField(max_length=1000, blank=True)

class description_form(forms.Form):
    narrative = forms.MultipleChoiceField(narrative_model.objects.all())
     = forms.CharField(max_length=1000, blank=True)

class descriptionType_form(forms.Form):
    type = forms.CharField(max_length=1000, blank=True)
    narrative = forms.MultipleChoiceField(narrative_model.objects.all())
     = forms.CharField(max_length=1000, blank=True)

class disbursement_channelType_form(forms.Form):
    code = forms.CharField(max_length=1000, blank=True)
     = forms.CharField(max_length=1000, blank=True)

class document_link_form(forms.Form):
    url = forms.CharField(max_length=1000, blank=True)
    format = forms.CharField(max_length=1000, blank=True)
    title = forms.MultipleChoiceField(textRequiredType_model.objects.all())
    category = forms.MultipleChoiceField(categoryType_model.objects.all())
    language = forms.MultipleChoiceField(languageType_model.objects.all())
     = forms.CharField(max_length=1000, blank=True)

class emailType_form(forms.Form):
    valueOf_x = forms.CharField(max_length=1000, blank=True)

class exactnessType_form(forms.Form):
    code = forms.CharField(max_length=1000, blank=True)
     = forms.CharField(max_length=1000, blank=True)

class feature_designationType_form(forms.Form):
    code = forms.CharField(max_length=1000, blank=True)
     = forms.CharField(max_length=1000, blank=True)

class finance_typeType_form(forms.Form):
    code = forms.CharField(max_length=1000, blank=True)
     = forms.CharField(max_length=1000, blank=True)

class flow_typeType_form(forms.Form):
    code = forms.CharField(max_length=1000, blank=True)
     = forms.CharField(max_length=1000, blank=True)

class forecastType_form(forms.Form):
    currency = forms.CharField(max_length=1000, blank=True)
    value_date = forms.DateField(blank=True)
    year = forms.FloatField(blank=True)
    valueOf_x = forms.FloatField(blank=True)

class fss_form(forms.Form):
    priority = forms.BooleanField(blank=True)
    phaseout_year = forms.FloatField(blank=True)
    extraction_date = forms.DateField(blank=True)
    forecast = forms.MultipleChoiceField(forecastType_model.objects.all())
     = forms.CharField(max_length=1000, blank=True)

class iati_activities_form(forms.Form):
    generated_datetime = forms.DateTimeField(blank=True)
    version = forms.CharField(max_length=1000, blank=True)
    linked_data_default = forms.CharField(max_length=1000, blank=True)
    iati_activity = forms.MultipleChoiceField(iati_activity_model.objects.all())
     = forms.CharField(max_length=1000, blank=True)

class iati_activity_form(forms.Form):
    lang = forms.CharField(max_length=1000, blank=True)
    last_updated_datetime = forms.DateTimeField(blank=True)
    linked_data_uri = forms.CharField(max_length=1000, blank=True)
    hierarchy = forms.IntegerField(blank=True)
    default_currency = forms.CharField(max_length=1000, blank=True)
    iati_identifier = forms.MultipleChoiceField(iati_identifier_model.objects.all())
    reporting_org = forms.MultipleChoiceField(reporting_org_model.objects.all())
    title = forms.MultipleChoiceField(textRequiredType_model.objects.all())
    description = forms.MultipleChoiceField(description_model.objects.all())
    participating_org = forms.MultipleChoiceField(participating_org_model.objects.all())
    other_identifier = forms.MultipleChoiceField(other_identifier_model.objects.all())
    activity_status = forms.MultipleChoiceField(activity_status_model.objects.all())
    activity_date = forms.MultipleChoiceField(activity_date_model.objects.all())
    contact_info = forms.MultipleChoiceField(contact_info_model.objects.all())
    activity_scope = forms.MultipleChoiceField(activity_scope_model.objects.all())
    recipient_country = forms.MultipleChoiceField(recipient_country_model.objects.all())
    recipient_region = forms.MultipleChoiceField(recipient_region_model.objects.all())
    location = forms.MultipleChoiceField(location_model.objects.all())
    sector = forms.MultipleChoiceField(sector_model.objects.all())
    country_budget_items = forms.MultipleChoiceField(country_budget_items_model.objects.all())
    policy_marker = forms.MultipleChoiceField(policy_marker_model.objects.all())
    collaboration_type = forms.MultipleChoiceField(collaboration_type_model.objects.all())
    default_flow_type = forms.MultipleChoiceField(default_flow_type_model.objects.all())
    default_finance_type = forms.MultipleChoiceField(default_finance_type_model.objects.all())
    default_aid_type = forms.MultipleChoiceField(default_aid_type_model.objects.all())
    default_tied_status = forms.MultipleChoiceField(default_tied_status_model.objects.all())
    budget = forms.MultipleChoiceField(budget_model.objects.all())
    planned_disbursement = forms.MultipleChoiceField(planned_disbursement_model.objects.all())
    capital_spend = forms.MultipleChoiceField(capital_spend_model.objects.all())
    transaction = forms.MultipleChoiceField(transaction_model.objects.all())
    document_link = forms.MultipleChoiceField(document_link_model.objects.all())
    related_activity = forms.MultipleChoiceField(related_activity_model.objects.all())
    legacy_data = forms.MultipleChoiceField(legacy_data_model.objects.all())
    conditions = forms.MultipleChoiceField(conditions_model.objects.all())
    result = forms.MultipleChoiceField(result_model.objects.all())
    crs_add = forms.MultipleChoiceField(crs_add_model.objects.all())
    fss = forms.MultipleChoiceField(fss_model.objects.all())
     = forms.CharField(max_length=1000, blank=True)

class iati_identifier_form(forms.Form):
    valueOf_x = forms.CharField(max_length=1000, blank=True)

class indicatorType_form(forms.Form):
    ascending = forms.BooleanField(blank=True)
    measure = forms.CharField(max_length=1000, blank=True)
    title = forms.MultipleChoiceField(textRequiredType_model.objects.all())
    description = forms.MultipleChoiceField(description_model.objects.all())
    baseline = forms.MultipleChoiceField(baselineType_model.objects.all())
    period = forms.MultipleChoiceField(periodType_model.objects.all())
     = forms.CharField(max_length=1000, blank=True)

class languageType_form(forms.Form):
    code = forms.CharField(max_length=1000, blank=True)
     = forms.CharField(max_length=1000, blank=True)

class legacy_data_form(forms.Form):
    name = forms.CharField(max_length=1000, blank=True)
    value = forms.CharField(max_length=1000, blank=True)
    iati_equivalent = forms.CharField(max_length=1000, blank=True)
     = forms.CharField(max_length=1000, blank=True)

class loan_statusType_form(forms.Form):
    currency = forms.CharField(max_length=1000, blank=True)
    value_date = forms.DateField(blank=True)
    year = forms.FloatField(blank=True)
    interest_received = forms.FloatField(blank=True)
    principal_outstanding = forms.FloatField(blank=True)
    principal_arrears = forms.FloatField(blank=True)
    interest_arrears = forms.FloatField(blank=True)
     = forms.CharField(max_length=1000, blank=True)

class loan_termsType_form(forms.Form):
    rate_2 = forms.FloatField(blank=True)
    rate_1 = forms.FloatField(blank=True)
    repayment_type = forms.MultipleChoiceField(repayment_typeType_model.objects.all())
    repayment_plan = forms.MultipleChoiceField(repayment_planType_model.objects.all())
    commitment_date = forms.MultipleChoiceField(commitment_dateType_model.objects.all())
    repayment_first_date = forms.MultipleChoiceField(repayment_first_dateType_model.objects.all())
    repayment_final_date = forms.MultipleChoiceField(repayment_final_dateType_model.objects.all())
     = forms.CharField(max_length=1000, blank=True)

class location_form(forms.Form):
    ref = forms.CharField(max_length=1000, blank=True)
    location_reach = forms.MultipleChoiceField(location_reachType_model.objects.all())
    location_id = forms.MultipleChoiceField(location_idType_model.objects.all())
    name = forms.MultipleChoiceField(textRequiredType_model.objects.all())
    description = forms.MultipleChoiceField(description_model.objects.all())
    activity_description = forms.MultipleChoiceField(textRequiredType_model.objects.all())
    administrative = forms.MultipleChoiceField(administrativeType_model.objects.all())
    point = forms.MultipleChoiceField(pointType_model.objects.all())
    exactness = forms.MultipleChoiceField(exactnessType_model.objects.all())
    location_class = forms.MultipleChoiceField(location_classType_model.objects.all())
    feature_designation = forms.MultipleChoiceField(feature_designationType_model.objects.all())
     = forms.CharField(max_length=1000, blank=True)

class location_classType_form(forms.Form):
    code = forms.CharField(max_length=1000, blank=True)
     = forms.CharField(max_length=1000, blank=True)

class location_idType_form(forms.Form):
    code = forms.CharField(max_length=1000, blank=True)
    vocabulary = forms.CharField(max_length=1000, blank=True)
     = forms.CharField(max_length=1000, blank=True)

class location_reachType_form(forms.Form):
    code = forms.CharField(max_length=1000, blank=True)
     = forms.CharField(max_length=1000, blank=True)

class narrative_form(forms.Form):
    lang = forms.CharField(max_length=1000, blank=True)
    valueOf_x = forms.CharField(max_length=1000, blank=True)

class other_flagsType_form(forms.Form):
    code = forms.CharField(max_length=1000, blank=True)
    significance = forms.BooleanField(blank=True)
     = forms.CharField(max_length=1000, blank=True)

class other_identifier_form(forms.Form):
    type = forms.CharField(max_length=1000, blank=True)
    ref = forms.CharField(max_length=1000, blank=True)
    owner_org = forms.MultipleChoiceField(owner_orgType_model.objects.all())
     = forms.CharField(max_length=1000, blank=True)

class owner_orgType_form(forms.Form):
    ref = forms.CharField(max_length=1000, blank=True)
    narrative = forms.MultipleChoiceField(narrative_model.objects.all())
     = forms.CharField(max_length=1000, blank=True)

class participating_org_form(forms.Form):
    type = forms.CharField(max_length=1000, blank=True)
    role = forms.CharField(max_length=1000, blank=True)
    ref = forms.CharField(max_length=1000, blank=True)
    narrative = forms.MultipleChoiceField(narrative_model.objects.all())
     = forms.CharField(max_length=1000, blank=True)

class periodType_form(forms.Form):
    period_start = forms.MultipleChoiceField(period_startType_model.objects.all())
    period_end = forms.MultipleChoiceField(period_endType_model.objects.all())
    target = forms.MultipleChoiceField(targetType_model.objects.all())
    actual = forms.MultipleChoiceField(actualType_model.objects.all())
     = forms.CharField(max_length=1000, blank=True)

class period_endType_form(forms.Form):
    iso_date = forms.DateField(blank=True)
     = forms.CharField(max_length=1000, blank=True)

class period_endType2_form(forms.Form):
    iso_date = forms.DateField(blank=True)
     = forms.CharField(max_length=1000, blank=True)

class period_endType4_form(forms.Form):
    iso_date = forms.DateField(blank=True)
     = forms.CharField(max_length=1000, blank=True)

class period_startType_form(forms.Form):
    iso_date = forms.DateField(blank=True)
     = forms.CharField(max_length=1000, blank=True)

class period_startType1_form(forms.Form):
    iso_date = forms.DateField(blank=True)
     = forms.CharField(max_length=1000, blank=True)

class period_startType3_form(forms.Form):
    iso_date = forms.DateField(blank=True)
     = forms.CharField(max_length=1000, blank=True)

class planned_disbursement_form(forms.Form):
    type = forms.CharField(max_length=1000, blank=True)
    period_start = forms.MultipleChoiceField(period_startType3_model.objects.all())
    period_end = forms.MultipleChoiceField(period_endType4_model.objects.all())
    value = forms.MultipleChoiceField(currencyType_model.objects.all())
     = forms.CharField(max_length=1000, blank=True)

class pointType_form(forms.Form):
    srsName = forms.CharField(max_length=1000, blank=True)
    pos = forms.CharField(max_length=1000, blank=True)
     = forms.CharField(max_length=1000, blank=True)

class policy_marker_form(forms.Form):
    code = forms.CharField(max_length=1000, blank=True)
    vocabulary = forms.CharField(max_length=1000, blank=True)
    significance = forms.CharField(max_length=1000, blank=True)
    narrative = forms.MultipleChoiceField(narrative_model.objects.all())
     = forms.CharField(max_length=1000, blank=True)

class provider_orgType_form(forms.Form):
    provider_activity_id = forms.CharField(max_length=1000, blank=True)
    ref = forms.CharField(max_length=1000, blank=True)
    narrative = forms.MultipleChoiceField(narrative_model.objects.all())
     = forms.CharField(max_length=1000, blank=True)

class receiver_orgType_form(forms.Form):
    receiver_activity_id = forms.CharField(max_length=1000, blank=True)
    ref = forms.CharField(max_length=1000, blank=True)
    narrative = forms.MultipleChoiceField(narrative_model.objects.all())
     = forms.CharField(max_length=1000, blank=True)

class recipient_country_form(forms.Form):
    percentage = forms.FloatField(blank=True)
    code = forms.CharField(max_length=1000, blank=True)
    narrative = forms.MultipleChoiceField(narrative_model.objects.all())
     = forms.CharField(max_length=1000, blank=True)

class recipient_countryType_form(forms.Form):
    code = forms.CharField(max_length=1000, blank=True)
    narrative = forms.MultipleChoiceField(narrative_model.objects.all())
     = forms.CharField(max_length=1000, blank=True)

class recipient_region_form(forms.Form):
    percentage = forms.FloatField(blank=True)
    code = forms.CharField(max_length=1000, blank=True)
    vocabulary = forms.CharField(max_length=1000, blank=True)
    narrative = forms.MultipleChoiceField(narrative_model.objects.all())
     = forms.CharField(max_length=1000, blank=True)

class recipient_regionType_form(forms.Form):
    code = forms.CharField(max_length=1000, blank=True)
    vocabulary = forms.CharField(max_length=1000, blank=True)
    narrative = forms.MultipleChoiceField(narrative_model.objects.all())
     = forms.CharField(max_length=1000, blank=True)

class related_activity_form(forms.Form):
    type = forms.CharField(max_length=1000, blank=True)
    ref = forms.CharField(max_length=1000, blank=True)
     = forms.CharField(max_length=1000, blank=True)

class repayment_final_dateType_form(forms.Form):
    iso_date = forms.DateField(blank=True)
     = forms.CharField(max_length=1000, blank=True)

class repayment_first_dateType_form(forms.Form):
    iso_date = forms.DateField(blank=True)
     = forms.CharField(max_length=1000, blank=True)

class repayment_planType_form(forms.Form):
    code = forms.CharField(max_length=1000, blank=True)
     = forms.CharField(max_length=1000, blank=True)

class repayment_typeType_form(forms.Form):
    code = forms.CharField(max_length=1000, blank=True)
     = forms.CharField(max_length=1000, blank=True)

class reporting_org_form(forms.Form):
    type = forms.CharField(max_length=1000, blank=True)
    secondary_reporter = forms.BooleanField(blank=True)
    ref = forms.CharField(max_length=1000, blank=True)
    narrative = forms.MultipleChoiceField(narrative_model.objects.all())
     = forms.CharField(max_length=1000, blank=True)

class result_form(forms.Form):
    type = forms.CharField(max_length=1000, blank=True)
    aggregation_status = forms.BooleanField(blank=True)
    title = forms.MultipleChoiceField(textRequiredType_model.objects.all())
    description = forms.MultipleChoiceField(description_model.objects.all())
    indicator = forms.MultipleChoiceField(indicatorType_model.objects.all())
     = forms.CharField(max_length=1000, blank=True)

class sector_form(forms.Form):
    percentage = forms.FloatField(blank=True)
    code = forms.CharField(max_length=1000, blank=True)
    vocabulary = forms.CharField(max_length=1000, blank=True)
    narrative = forms.MultipleChoiceField(narrative_model.objects.all())
     = forms.CharField(max_length=1000, blank=True)

class sectorType_form(forms.Form):
    code = forms.CharField(max_length=1000, blank=True)
    vocabulary = forms.CharField(max_length=1000, blank=True)
    narrative = forms.MultipleChoiceField(narrative_model.objects.all())
     = forms.CharField(max_length=1000, blank=True)

class targetType_form(forms.Form):
    value = forms.CharField(max_length=1000, blank=True)
    comment = forms.MultipleChoiceField(textRequiredType_model.objects.all())
     = forms.CharField(max_length=1000, blank=True)

class telephoneType_form(forms.Form):
    valueOf_x = forms.CharField(max_length=1000, blank=True)

class textRequiredType_form(forms.Form):
    narrative = forms.MultipleChoiceField(narrative_model.objects.all())
     = forms.CharField(max_length=1000, blank=True)

class textType_form(forms.Form):
    narrative = forms.MultipleChoiceField(narrative_model.objects.all())
     = forms.CharField(max_length=1000, blank=True)

class tied_statusType_form(forms.Form):
    code = forms.CharField(max_length=1000, blank=True)
     = forms.CharField(max_length=1000, blank=True)

class transaction_form(forms.Form):
    ref = forms.CharField(max_length=1000, blank=True)
    transaction_type = forms.MultipleChoiceField(transaction_typeType_model.objects.all())
    transaction_date = forms.MultipleChoiceField(transaction_dateType_model.objects.all())
    value = forms.MultipleChoiceField(currencyType_model.objects.all())
    description = forms.MultipleChoiceField(description_model.objects.all())
    provider_org = forms.MultipleChoiceField(provider_orgType_model.objects.all())
    receiver_org = forms.MultipleChoiceField(receiver_orgType_model.objects.all())
    disbursement_channel = forms.MultipleChoiceField(disbursement_channelType_model.objects.all())
    sector = forms.MultipleChoiceField(sector_model.objects.all())
    recipient_country = forms.MultipleChoiceField(recipient_countryType_model.objects.all())
    recipient_region = forms.MultipleChoiceField(recipient_regionType_model.objects.all())
    flow_type = forms.MultipleChoiceField(flow_typeType_model.objects.all())
    finance_type = forms.MultipleChoiceField(finance_typeType_model.objects.all())
    aid_type = forms.MultipleChoiceField(aid_typeType_model.objects.all())
    tied_status = forms.MultipleChoiceField(tied_statusType_model.objects.all())
     = forms.CharField(max_length=1000, blank=True)

class transaction_dateType_form(forms.Form):
    iso_date = forms.DateField(blank=True)
     = forms.CharField(max_length=1000, blank=True)

class transaction_typeType_form(forms.Form):
    code = forms.CharField(max_length=1000, blank=True)
     = forms.CharField(max_length=1000, blank=True)

class websiteType_form(forms.Form):
    valueOf_x = forms.CharField(max_length=1000, blank=True)
