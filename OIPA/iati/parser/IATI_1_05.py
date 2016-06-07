from IATI_2_01 import Parse as IATI_201_Parser
from lxml.builder import E

from iati import models
from iati_codelists import models as codelist_models
from iati_vocabulary import models as vocabulary_models 
from iati.parser.exceptions import *

# TODO: separate validation logic and model saving login in recursive tree walk


class Parse(IATI_201_Parser):

    #version of iati standard
    VERSION = '1.05'
    
    activity_date_type_mapping = {
        "start-planned": "1",
        "start-actual": "2",
        "end-planned": "3",
        "end-actual": "4",
    }

    # mapping from Vocabulary 1.05 to SectorVocabulary 2.01
    # TODO: this mapping is very unclear
    sector_vocabulary_mapping = {
        'DAC': "1",
        'DAC-3': "1",
        'RO': "2",
        'RO2': "2",
    }

    # mapping from Vocabulary 1.05 to PolicyMarkerVocabulary 2.01
    policy_marker_vocabulary_mapping = {
        'ADT': "6",
        'COFOG': "3",
        'DAC': "1",
        'DAC-3': "2",
        'ISO': None, # has no mapping
        'NACE': "4",
        'NTEE': "5",
        'RO': "99",
        'RO2': "98",
        'WB': None, # has no mapping
    }

    transaction_type_mapping = {
        'IF': '1',
        'C': '2',
        'D': '3',
        'E': '4',
        'IR': '5',
        'LR': '6',
        'R': '7',
        'QP': '8',
        'Q3': '9',
        'CG': '10'
    }

    def __init__(self, *args, **kwargs):
        super(Parse, self).__init__(*args, **kwargs)
        # self.VERSION = codelist_models.Version.objects.get(code='1.05')
        
    def iati_activities__iati_activity__reporting_org(self, element):
        """atributes:
        ref:AA-AAA-123456789
        type:21
    
        tag:reporting-org"""
        super(Parse, self).iati_activities__iati_activity__reporting_org(element)

        activity_reporting_organisation = self.get_model('ActivityReportingOrganisation')

        if element.text:
            self.add_narrative(element, activity_reporting_organisation)
            if activity_reporting_organisation.organisation:
                activity_reporting_organisation.organisation.primary_name = self.get_primary_name(element, activity_reporting_organisation.organisation.primary_name)
        return element

    def iati_activities__iati_activity__participating_org(self, element):
        """atributes:
        ref:BB-BBB-123456789
        role:Funding
        type:40
    
        tag:participating-org"""

        role_name = element.attrib.get('role')
        role = self.get_or_none(codelist_models.OrganisationRole, name=role_name)

        if not role_name: 
            raise RequiredFieldError(
                "participating-org",
                "role",
                "required attribute missing")

        if not role: 
            raise ValidationError(
                "participating-org",
                "role",
                "not found on the accompanying code list")

        element.attrib['role'] = role.code

        super(Parse, self).iati_activities__iati_activity__participating_org(element)

        participating_organisation = self.get_model('ActivityParticipatingOrganisation')

        if element.text:
            self.add_narrative(element, participating_organisation)
            # workaround for IATI ref uniqueness limitation
            participating_organisation.primary_name = self.get_primary_name(element, participating_organisation.primary_name)

        return element

    def iati_activities__iati_activity__other_identifier(self, element):
        """atributes:
    ref:ABC123-XYZ
    owner-name:A1
    tag:other-identifier"""
        identifier = element.text
        owner_ref = element.attrib.get('owner-ref')
        owner_name = element.attrib.get('owner-name')

        if not identifier:
            raise RequiredFieldError(
                "other-identifier",
                "text",
                "required element empty")

        if identifier and len(identifier) > 200:
            raise ValidationError(
                "other-identifier",
                "text",
                "identifier is longer than 200 characters (unlikely and is most often a data bug)")

        if not (owner_ref or owner_name):
            raise RequiredFieldError(
                "other-identifier",
                "owner-ref/owner-name", 
                "either owner_ref or owner_name must be set")

        activity = self.get_model('Activity')

        other_identifier = models.OtherIdentifier()
        other_identifier.activity = activity
        other_identifier.identifier = identifier
        other_identifier.owner_ref = owner_ref

        # TODO: refactor this to not create an lxml element
        self.register_model('OtherIdentifier', other_identifier)

        if element.text:
            self.add_narrative(E('elem', owner_name), other_identifier)

        return element

    def iati_activities__iati_activity__title(self, element):
        """atributes:

        tag:title"""
        title_list = self.get_model_list('Title')

        if not title_list or len(title_list) == 0:
            super(Parse, self).iati_activities__iati_activity__title(element)
        # else title exists, this is a new narrative

        title = self.get_model('Title')

        if element.text:
            self.add_narrative(element, title)

        return element

    def iati_activities__iati_activity__description(self, element):
        """atributes:
        type:1

        tag:description"""
        text = element.text
        description_type_code = element.attrib.get('type', 1)

        if not text:
            raise RequiredFieldError(
                "description", 
                "text", 
                "required element empty")

        description_type = self.get_or_none(codelist_models.DescriptionType, code=description_type_code)

        activity = self.get_model('Activity')
        description = models.Description()
        description.activity = activity
        description.type = description_type

        self.register_model('Description', description)

        if element.text:
            self.add_narrative(element, description)

        return element

    def iati_activities__iati_activity__activity_date(self, element):
        """atributes:
        iso-date:2012-04-15
        type:1

        tag:activity-date"""
        # TODO: should iati Rules be checked?
        # http://iatistandard.org/201/activity-standard/iati-activities/iati-activity/activity-date/
        type_name = element.attrib.get('type')
        type_code = self.activity_date_type_mapping.get(type_name)

        if not type_name:
            raise RequiredFieldError(
                "activity-date",
                "type",
                "required attribute missing")

        if not type_code:
            raise RequiredFieldError(
                "activity-date",
                "type",
                "not found on the accompanying code list")

        if type_code:
            element.attrib['type'] = type_code

        super(Parse, self).iati_activities__iati_activity__activity_date(element)

        activity_date = self.get_model('ActivityDate')

        if element.text:
            self.add_narrative(element, activity_date)

        return element


    def iati_activities__iati_activity__contact_info__organisation(self, element):
        """atributes:
    tag:organisation"""
        super(Parse, self).iati_activities__iati_activity__contact_info__organisation(element)
        contact_info_organisation = self.get_model('ContactInfoOrganisation')

        if element.text:
            self.add_narrative(element, contact_info_organisation)

        return element

    def iati_activities__iati_activity__contact_info__person_name(self, element):
        """atributes:

    tag:person-name"""
        super(Parse, self).iati_activities__iati_activity__contact_info__person_name(element)
        contact_info_person_name = self.get_model('ContactInfoPersonName')

        if element.text:
            self.add_narrative(element, contact_info_person_name)

        return element

    def iati_activities__iati_activity__contact_info__job_title(self, element):
        """atributes:

    tag:job-title"""
        super(Parse, self).iati_activities__iati_activity__contact_info__job_title(element)
        contact_info_job_title = self.get_model('ContactInfoJobTitle')

        if element.text:
            self.add_narrative(element, contact_info_job_title)

        return element

    def iati_activities__iati_activity__contact_info__mailing_address(self, element):
        """atributes:

    tag:mailing-address"""
        super(Parse, self).iati_activities__iati_activity__contact_info__mailing_address(element)
        contact_info_mailing_address = self.get_model('ContactInfoMailingAddress')

        if element.text:
            self.add_narrative(element, contact_info_mailing_address)

        return element

    def iati_activities__iati_activity__location__name(self, element):
        """atributes:

    tag:name"""
        super(Parse, self).iati_activities__iati_activity__location__name(element)
        location_name = self.get_model('LocationName')

        if element.text:
            self.add_narrative(element, location_name)

        return element

    def iati_activities__iati_activity__location__description(self, element):
        """atributes:

    tag:description"""
        super(Parse, self).iati_activities__iati_activity__location__description(element)
        location_description = self.get_model('LocationDescription')

        if element.text:
            self.add_narrative(element, location_description)

        return element

    def iati_activities__iati_activity__location__activity_description(self, element):
        """atributes:

    tag:activity-description"""
        super(Parse, self).iati_activities__iati_activity__location__activity_description(element)
        location_activity_description = self.get_model('LocationActivityDescription')

        if element.text:
            self.add_narrative(element, location_activity_description)

        return element

    def iati_activities__iati_activity__sector(self, element):
        """atributes:
    code:111
    vocabulary:DAC

    tag:sector"""
        vocabulary = self.sector_vocabulary_mapping.get(element.attrib.get('vocabulary'))

        if vocabulary:
            element.attrib['vocabulary'] = vocabulary
        super(Parse, self).iati_activities__iati_activity__sector(element)

        return element

    def iati_activities__iati_activity__country_budget_items__budget_item__description(self, element):
        """atributes:

        tag:description"""
        super(Parse, self).iati_activities__iati_activity__country_budget_items__budget_item__description(element)
        budget_item_description = self.get_model('BudgetItemDescription')

        if element.text:
            self.add_narrative(element, budget_item_description)

        return element

    def iati_activities__iati_activity__humanitarian_scope(self, element):
        """attributes:

        tag:narrative"""
        super(Parse, self).iati_activities__iati_activity__humanitarian_scope(element)
        humanitarian_scope = self.get_model('HumanitarianScope')

        if element.text:
            self.add_narrative(element, humanitarian_scope)

        return element

    def iati_activities__iati_activity__policy_marker(self, element):
        """atributes:
    vocabulary:1
    code:2
    significance:3

    tag:policy-marker"""
        vocabulary = self.policy_marker_vocabulary_mapping.get(element.attrib.get('vocabulary'))

        if not vocabulary:
            vocabulary = vocabulary_models.PolicyMarkerVocabulary.objects.get(code='1')

        if vocabulary:
            element.attrib['vocabulary'] = vocabulary
        super(Parse, self).iati_activities__iati_activity__policy_marker(element)

        policy_marker = self.get_model('ActivityPolicyMarker')

        if element.text:
            self.add_narrative(element, policy_marker)

        return element

    def iati_activities__iati_activity__transaction__transaction_type(self, element):
        """atributes:

    tag:description"""
        code = self.transaction_type_mapping.get(element.attrib.get('code'))

        if code:
            element.attrib['code'] = code

        super(Parse, self).iati_activities__iati_activity__transaction__transaction_type(element)
        return element

    def iati_activities__iati_activity__transaction__description(self, element):
        """atributes:

    tag:description"""
        super(Parse, self).iati_activities__iati_activity__transaction__description(element)
    
        transaction_description = self.get_model('TransactionDescription')

        if element.text:
            self.add_narrative(element, transaction_description)

        return element

    def iati_activities__iati_activity__transaction__provider_org(self, element):
        """atributes:
    provider-activity-id:BB-BBB-123456789-1234AA
    ref:BB-BBB-123456789

    tag:provider-org"""
        super(Parse, self).iati_activities__iati_activity__transaction__provider_org(element)
    
        # transaction_provider = self.get_model('Transaction', index=-2)
        transaction_provider = self.get_model('TransactionProvider')

        if element.text:
            self.add_narrative(element, transaction_provider)
            transaction_provider.primary_name = self.get_primary_name(element, transaction_provider.primary_name)

        return element

    def iati_activities__iati_activity__transaction__receiver_org(self, element):
        """atributes:
        receiver-activity-id:AA-AAA-123456789-1234
        ref:AA-AAA-123456789
    
        tag:receiver-org"""
        super(Parse, self).iati_activities__iati_activity__transaction__receiver_org(element)
    
        # transaction_receiver = self.get_model('Transaction', index=-2)
        transaction_receiver = self.get_model('TransactionReceiver')

        if element.text:
            self.add_narrative(element, transaction_receiver)
            transaction_receiver.primary_name = self.get_primary_name(element, transaction_receiver.primary_name)

        return element

    def iati_activities__iati_activity__document_link__title(self, element):
        """atributes:

        tag:title"""
        super(Parse, self).iati_activities__iati_activity__document_link__title(element)

        document_link_title = self.get_model('DocumentLinkTitle')

        if element.text:
            self.add_narrative(element, document_link_title)

        return element

#     """atributes:

#     tag:activity-website"""
#     def iati_activities__iati_activity__activity_website(self, element):
#         model = self.get_func_parent_model()
#         website = models.ActivityWebsite()
#         website.activity = model
#         website.url = element.text
#         website.save()
#         #store element 
#         return element

#     """atributes:
#     type:1

#     tag:condition"""
#     def iati_activities__iati_activity__conditions__condition(self, element):
#         model = self.get_func_parent_model()
#         condition = models.Condition()
#         condition.activity = model
#         condition.type = self.cached_db_call(models.ConditionType,element.attrib.get('type'))
#         self.add_narrative(element, condition)
#         return element


    def check_narrative_duplicate(self, parent, child, fk_field):
        """
        Given a 1.05 narrative mimicking element, like all results free text elements,
        make sure only one parent object is created, and add a narrative to that object
        """
        return child and getattr(child, fk_field) == parent

#     """atributes:

#     tag:title"""
    def iati_activities__iati_activity__result__title(self, element):
        result_title_narrative = self.get_model('ResultTitleNarrative')

        result = self.get_model('Result')
        result_title = self.get_model('ResultTitle')

        if self.check_narrative_duplicate(result, result_title, 'result'):
            self.add_narrative(element, result_title)
            return element

        result_title = models.ResultTitle()
        result_title.result = result
        self.register_model('ResultTitle', result_title)

        if element.text:
            self.add_narrative(element, result_title)

        return element

#     """atributes:

#     tag:description"""
    def iati_activities__iati_activity__result__description(self, element):
        result = self.get_model('Result')
        result_description = self.get_model('ResultDescription')

        # create this element, can occur multiple times
        # if a narrative for this result's result_description has already been added
        if self.check_narrative_duplicate(result, result_description, 'result'):
            self.add_narrative(element, result_description)
            return element

        result_description = models.ResultDescription()
        result_description.result = result
        self.register_model('ResultDescription', result_description)

        if element.text:
            self.add_narrative(element, result_description)

        return element

#     """atributes:

#     tag:title"""
    def iati_activities__iati_activity__result__indicator__title(self, element):

        result_indicator = self.get_model('ResultIndicator')
        result_indicator_title = self.get_model('ResultIndicatorTitle')

        if self.check_narrative_duplicate(result_indicator, result_indicator_title, 'result_indicator'):
            self.add_narrative(element, result_indicator_title)
            return element

        result_indicator_title = models.ResultIndicatorTitle()
        result_indicator_title.result_indicator = result_indicator
        self.register_model('ResultIndicatorTitle', result_indicator_title)

        if element.text:
            self.add_narrative(element, result_indicator_title)
            result_indicator_title.primary_name = self.get_primary_name(element, result_indicator_title.primary_name)

        return element

#     """atributes:

#     tag:description"""
    def iati_activities__iati_activity__result__indicator__description(self, element):

        result_indicator = self.get_model('ResultIndicator')
        result_indicator_description = self.get_model('ResultIndicatorDescription')

        if self.check_narrative_duplicate(result_indicator, result_indicator_description, 'result_indicator'):
            self.add_narrative(element, result_indicator_description)
            return element

        result_indicator_description = models.ResultIndicatorDescription()
        result_indicator_description.result_indicator = result_indicator
        self.register_model('ResultIndicatorDescription', result_indicator_description)

        if element.text:
            self.add_narrative(element, result_indicator_description)

        return element


#     """atributes:

#     tag:comment"""
    def iati_activities__iati_activity__result__indicator__baseline__comment(self, element):

        result_indicator = self.get_model('ResultIndicator')
        result_indicator_baseline_comment = self.get_model('ResultIndicatorBaselineComment')

        if self.check_narrative_duplicate(result_indicator, result_indicator_baseline_comment, 'result_indicator'):
            self.add_narrative(element, result_indicator_baseline_comment)
            return element

        result_indicator_baseline_comment = models.ResultIndicatorBaselineComment()
        result_indicator_baseline_comment.result_indicator = result_indicator
        self.register_model('ResultIndicatorBaselineComment', result_indicator_baseline_comment)

        if element.text:
            self.add_narrative(element, result_indicator_baseline_comment)

        return element

#     """atributes:

#     tag:comment"""
    def iati_activities__iati_activity__result__indicator__period__target__comment(self, element):

        result_indicator_period = self.get_model('ResultIndicatorPeriod')
        result_indicator_period_target_comment = self.get_model('ResultIndicatorPeriodTargetComment')

        if self.check_narrative_duplicate(result_indicator_period, result_indicator_period_target_comment, 'result_indicator_period'):
            self.add_narrative(element, result_indicator_period_target_comment)
            return element

        result_indicator_period_target_comment = models.ResultIndicatorPeriodTargetComment()
        result_indicator_period_target_comment.result_indicator_period = result_indicator_period
        self.register_model('ResultIndicatorPeriodTargetComment', result_indicator_period_target_comment)

        if element.text:
            self.add_narrative(element, result_indicator_period_target_comment)

        return element

#     """atributes:

#     tag:comment"""
    def iati_activities__iati_activity__result__indicator__period__actual__comment(self, element):
        result_indicator_period = self.get_model('ResultIndicatorPeriod')
        result_indicator_period_actual_comment = self.get_model('ResultIndicatorPeriodActualComment')

        if self.check_narrative_duplicate(result_indicator_period, result_indicator_period_actual_comment, 'result_indicator_period'):
            self.add_narrative(element, result_indicator_period_actual_comment)
            return element

        result_indicator_period_actual_comment = models.ResultIndicatorPeriodActualComment()
        result_indicator_period_actual_comment.result_indicator_period = result_indicator_period
        self.register_model('ResultIndicatorPeriodActualComment', result_indicator_period_actual_comment)

        if element.text:
            self.add_narrative(element, result_indicator_period_actual_comment)

        return element

#     """atributes:
#     code:1
#     significance:1

#     tag:aidtype-flag"""
#     def iati_activities__iati_activity__crs_add__aidtype_flag(self, element):
#         model = self.get_func_parent_model()
#         crs_other_flags = models.CrsAddOtherFlags()
#         crs_other_flags.crs_add = model
#         crs_other_flags.other_flags = self.cached_db_call_no_version(models.OtherFlags,element.attrib.get('code'))
#         crs_other_flags.significance = element.attrib.get('significance')
#         crs_other_flags.save()
#         #store element 
#         return element


#     """atributes:
#     year:2014
#     value-date:2013-07-03
#     currency:GBP

#     tag:forecast"""
#     def iati_activities__iati_activity__fss__forecast(self, element):
#         model = self.get_func_parent_model()
#         fss_forecast = models.FssForecast()
#         fss_forecast.fss = model
#         fss_forecast.year = element.attrib.get('year')
#         fss_forecast.value_date = self.validate_date(element.attrib.get('value-date'))
#         fss_forecast.currency = self.cached_db_call_no_version(models.Currency,element.attrib.get('currency'))
#         return element
