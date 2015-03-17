from genericXmlParser import XMLParser
from iati import models


class Parse(XMLParser):

    VERSION = '2.01'#version of iati standard
    default_lang = 'en'


    def __init__(self, *args, **kwargs):
        self.test = 'blabla'



    def add_organisation(self, elem):
        try:
            ref = elem.attrib['ref']
            type_ref = elem.attrib['type']
            name = None
            for e in elem:
                name = e.text
                break

            org_type = None
            if self.isInt(type_ref) and self.cached_db_call(models.OrganisationType,type_ref) != None:
                org_type = self.cached_db_call(models.OrganisationType,type_ref)

            organisation = models.Organisation.objects.get_or_create(
                code=ref,
                defaults={
                    'name': name,
                    'type': org_type,
                    'original_ref': ref

                })[0]
            return organisation

        except Exception as e:
            print e

    def add_narrative(self,element,parent):
        narrative = models.Narrative()
        lang = self.default_lang 
        if '{http://www.w3.org/XML/1998/namespace}lang' in element.attrib:
            lang = element.attrib['{http://www.w3.org/XML/1998/namespace}lang']
        print parent
        narrative.language = lang
        narrative.content = element.text
        narrative.parent_object = parent
        narrative.save()

    '''atributes:
    {http://www.w3.org/XML/1998/namespace}lang:en
    default-currency:USD
    last-updated-datetime:2014-09-10T07:15:37Z
    linked-data-uri:http://data.example.org/123456789
    hierarchy:1

    tag:iati-activity'''
    def iati_activities_iati_activity(self,element):
        
        self.default_lang = 'en'
        activity = models.Activity()
        self.set_func_model(activity)
        activity.default_currency = self.cached_db_call(models.Currency, element.attrib.get('default-currency'))
        activity.save()
        return element

    '''atributes:

    tag:iati-identifier'''
    def iati_activities_iati_activity_iati_identifier(self,element):
        model = self.get_func_model()#model is activity
        model.iati_identifier = element.text
        
        return # endpoint return None 

    '''atributes:
    ref:AA-AAA-123456789
    type:40
    secondary-reporter:0

    tag:reporting-org'''
    def iati_activities_iati_activity_reporting_org(self,element):
        model = self.get_func_model()
        organisation = self.add_organisation(element)
        organisation.save()
        print organisation.name
        model.reporting_organisation = organisation
        self.set_func_model(organisation)
    
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities_iati_activity_reporting_org_narrative(self,element):
        model = self.get_func_model()
        self.add_narrative(element,model)

        return element


    '''atributes:

    tag:title'''
    def iati_activities_iati_activity_title(self,element):
        model = self.get_func_model()
        title = models.Title()
        title.activity = model
        title.save()
        self.set_func_model(title)
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities_iati_activity_title_narrative(self,element):
        model = self.get_func_model()
        self.add_narrative(element,model)
        
        return element

    '''atributes:
    type:1

    tag:description'''
    def iati_activities_iati_activity_description(self,element):
        model = self.get_func_model()
        description = models.Description()
        description.activity = model
        desc_type = self.cached_db_call(models.DescriptionType, element.attrib.get('type'))
        description.type = desc_type
        description.save()
        self.set_func_model(description)
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities_iati_activity_description_narrative(self,element):
        model = self.get_func_model()
        self.add_narrative(element,model)
        return element


    '''atributes:
    ref:BB-BBB-123456789
    role:1
    type:40

    tag:participating-org'''
    def iati_activities_iati_activity_participating_org(self,element):
        model = self.get_func_model()
        org = self.add_organisation(element)
        activityParticipatingOrganisation = models.ActivityParticipatingOrganisation()
        activityParticipatingOrganisation.org = org
        activityParticipatingOrganisation.activity = model
        activityParticipatingOrganisation.role = self.cached_db_call(models.OrganisationRole, element.attrib.get('role'))
        activityParticipatingOrganisation.save()
        self.set_func_model(activityParticipatingOrganisation)
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities_iati_activity_participating_org_narrative(self,element):
        model = self.get_func_model()
        self.add_narrative(element,model)
        return element

    '''atributes:
    ref:ABC123-XYZ
    type:A1

    tag:other-identifier'''
    def iati_activities_iati_activity_other_identifier(self,element):
        model = self.get_func_model()
        owner_ref = element.attrib['ref']
        type = self.cached_db_call(models.OtherIdentifierType, element.attrib.get('type))
        new_other_identifier = models.OtherIdentifier(activity=model, owner_ref=owner_ref, owner_name=owner_name, identifier=other_identifier)

        return element

    '''atributes:
    ref:AA-AAA-123456789

    tag:owner-org'''
    def iati_activities_iati_activity_other_identifier_owner_org(self,element):
        model = self.get_func_model()
        
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities_iati_activity_other_identifier_owner_org_narrative(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    code:2

    tag:activity-status'''
    def iati_activities_iati_activity_activity_status(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    iso-date:2012-04-15
    type:1

    tag:activity-date'''
    def iati_activities_iati_activity_activity_date(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities_iati_activity_activity_date_narrative(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    type:1

    tag:contact-info'''
    def iati_activities_iati_activity_contact_info(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:

    tag:organisation'''
    def iati_activities_iati_activity_contact_info_organisation(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities_iati_activity_contact_info_organisation_narrative(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:

    tag:department'''
    def iati_activities_iati_activity_contact_info_department(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities_iati_activity_contact_info_department_narrative(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:

    tag:person-name'''
    def iati_activities_iati_activity_contact_info_person_name(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities_iati_activity_contact_info_person_name_narrative(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:

    tag:job-title'''
    def iati_activities_iati_activity_contact_info_job_title(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities_iati_activity_contact_info_job_title_narrative(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:

    tag:telephone'''
    def iati_activities_iati_activity_contact_info_telephone(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:

    tag:email'''
    def iati_activities_iati_activity_contact_info_email(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:

    tag:website'''
    def iati_activities_iati_activity_contact_info_website(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:

    tag:mailing-address'''
    def iati_activities_iati_activity_contact_info_mailing_address(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities_iati_activity_contact_info_mailing_address_narrative(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    code:3

    tag:activity-scope'''
    def iati_activities_iati_activity_activity_scope(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    code:AF
    percentage:25

    tag:recipient-country'''
    def iati_activities_iati_activity_recipient_country(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    code:489
    vocabulary:1
    percentage:25

    tag:recipient-region'''
    def iati_activities_iati_activity_recipient_region(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    ref:AF-KAN

    tag:location'''
    def iati_activities_iati_activity_location(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    code:1

    tag:location-reach'''
    def iati_activities_iati_activity_location_location_reach(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    vocabulary:G1
    code:1453782

    tag:location-id'''
    def iati_activities_iati_activity_location_location_id(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:

    tag:name'''
    def iati_activities_iati_activity_location_name(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities_iati_activity_location_name_narrative(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:

    tag:description'''
    def iati_activities_iati_activity_location_description(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities_iati_activity_location_description_narrative(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:

    tag:activity-description'''
    def iati_activities_iati_activity_location_activity_description(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities_iati_activity_location_activity_description_narrative(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    vocabulary:G1
    level:1
    code:1453782

    tag:administrative'''
    def iati_activities_iati_activity_location_administrative(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    srsName:http://www.opengis.net/def/crs/EPSG/0/4326

    tag:point'''
    def iati_activities_iati_activity_location_point(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:

    tag:pos'''
    def iati_activities_iati_activity_location_point_pos(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    code:1

    tag:exactness'''
    def iati_activities_iati_activity_location_exactness(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    code:2

    tag:location-class'''
    def iati_activities_iati_activity_location_location_class(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    code:ADMF

    tag:feature-designation'''
    def iati_activities_iati_activity_location_feature_designation(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    vocabulary:2
    code:111
    percentage:50

    tag:sector'''
    def iati_activities_iati_activity_sector(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    vocabulary:2

    tag:country-budget-items'''
    def iati_activities_iati_activity_country_budget_items(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    code:1.1.1
    percentage:50

    tag:budget-item'''
    def iati_activities_iati_activity_country_budget_items_budget_item(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:

    tag:description'''
    def iati_activities_iati_activity_country_budget_items_budget_item_description(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities_iati_activity_country_budget_items_budget_item_description_narrative(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    vocabulary:1
    code:2
    significance:3

    tag:policy-marker'''
    def iati_activities_iati_activity_policy_marker(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    code:1

    tag:collaboration-type'''
    def iati_activities_iati_activity_collaboration_type(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    code:10

    tag:default-flow-type'''
    def iati_activities_iati_activity_default_flow_type(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    code:110

    tag:default-finance-type'''
    def iati_activities_iati_activity_default_finance_type(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    code:A01

    tag:default-aid-type'''
    def iati_activities_iati_activity_default_aid_type(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    code:3

    tag:default-tied-status'''
    def iati_activities_iati_activity_default_tied_status(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    type:1

    tag:budget'''
    def iati_activities_iati_activity_budget(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    iso-date:2014-01-01

    tag:period-start'''
    def iati_activities_iati_activity_budget_period_start(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    iso-date:2014-12-31

    tag:period-end'''
    def iati_activities_iati_activity_budget_period_end(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    currency:EUR
    value-date:2014-01-01

    tag:value'''
    def iati_activities_iati_activity_budget_value(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    type:1

    tag:planned-disbursement'''
    def iati_activities_iati_activity_planned_disbursement(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    iso-date:2014-01-01

    tag:period-start'''
    def iati_activities_iati_activity_planned_disbursement_period_start(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    iso-date:2014-12-31

    tag:period-end'''
    def iati_activities_iati_activity_planned_disbursement_period_end(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    currency:EUR
    value-date:2014-01-01

    tag:value'''
    def iati_activities_iati_activity_planned_disbursement_value(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    percentage:88.8

    tag:capital-spend'''
    def iati_activities_iati_activity_capital_spend(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    ref:1234

    tag:transaction'''
    def iati_activities_iati_activity_transaction(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    code:1

    tag:transaction-type'''
    def iati_activities_iati_activity_transaction_transaction_type(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    iso-date:2012-01-01

    tag:transaction-date'''
    def iati_activities_iati_activity_transaction_transaction_date(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    currency:EUR
    value-date:2012-01-01

    tag:value'''
    def iati_activities_iati_activity_transaction_value(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:

    tag:description'''
    def iati_activities_iati_activity_transaction_description(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities_iati_activity_transaction_description_narrative(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    provider-activity-id:BB-BBB-123456789-1234AA
    ref:BB-BBB-123456789

    tag:provider-org'''
    def iati_activities_iati_activity_transaction_provider_org(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities_iati_activity_transaction_provider_org_narrative(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    receiver-activity-id:AA-AAA-123456789-1234
    ref:AA-AAA-123456789

    tag:receiver-org'''
    def iati_activities_iati_activity_transaction_receiver_org(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities_iati_activity_transaction_receiver_org_narrative(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    code:1

    tag:disbursement-channel'''
    def iati_activities_iati_activity_transaction_disbursement_channel(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    vocabulary:2
    code:111

    tag:sector'''
    def iati_activities_iati_activity_transaction_sector(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    code:AF

    tag:recipient-country'''
    def iati_activities_iati_activity_transaction_recipient_country(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    code:456
    vocabulary:1

    tag:recipient-region'''
    def iati_activities_iati_activity_transaction_recipient_region(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    code:10

    tag:flow-type'''
    def iati_activities_iati_activity_transaction_flow_type(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    code:110

    tag:finance-type'''
    def iati_activities_iati_activity_transaction_finance_type(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    code:A01

    tag:aid-type'''
    def iati_activities_iati_activity_transaction_aid_type(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    code:3

    tag:tied-status'''
    def iati_activities_iati_activity_transaction_tied_status(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    format:application/vnd.oasis.opendocument.text
    url:http:www.example.org/docs/report_en.odt

    tag:document-link'''
    def iati_activities_iati_activity_document_link(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:

    tag:title'''
    def iati_activities_iati_activity_document_link_title(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities_iati_activity_document_link_title_narrative(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    code:A01

    tag:category'''
    def iati_activities_iati_activity_document_link_category(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    code:en

    tag:language'''
    def iati_activities_iati_activity_document_link_language(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    ref:AA-AAA-123456789-6789
    type:1

    tag:related-activity'''
    def iati_activities_iati_activity_related_activity(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    name:Project Status
    value:7
    iati-equivalent:activity-status

    tag:legacy-data'''
    def iati_activities_iati_activity_legacy_data(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    attached:1

    tag:conditions'''
    def iati_activities_iati_activity_conditions(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    type:1

    tag:condition'''
    def iati_activities_iati_activity_conditions_condition(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities_iati_activity_conditions_condition_narrative(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    type:1
    aggregation-status:1

    tag:result'''
    def iati_activities_iati_activity_result(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:

    tag:title'''
    def iati_activities_iati_activity_result_title(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities_iati_activity_result_title_narrative(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:

    tag:description'''
    def iati_activities_iati_activity_result_description(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities_iati_activity_result_description_narrative(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    measure:1
    ascending:1

    tag:indicator'''
    def iati_activities_iati_activity_result_indicator(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:

    tag:title'''
    def iati_activities_iati_activity_result_indicator_title(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities_iati_activity_result_indicator_title_narrative(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:

    tag:description'''
    def iati_activities_iati_activity_result_indicator_description(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities_iati_activity_result_indicator_description_narrative(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    year:2012
    value:10

    tag:baseline'''
    def iati_activities_iati_activity_result_indicator_baseline(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:

    tag:period'''
    def iati_activities_iati_activity_result_indicator_period(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    iso-date:2013-01-01

    tag:period-start'''
    def iati_activities_iati_activity_result_indicator_period_period_start(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    iso-date:2013-03-31

    tag:period-end'''
    def iati_activities_iati_activity_result_indicator_period_period_end(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    value:10

    tag:target'''
    def iati_activities_iati_activity_result_indicator_period_target(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    value:11

    tag:actual'''
    def iati_activities_iati_activity_result_indicator_period_actual(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:

    tag:crs-add'''
    def iati_activities_iati_activity_crs_add(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    code:1
    significance:1

    tag:other-flags'''
    def iati_activities_iati_activity_crs_add_other_flags(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    rate-1:4
    rate-2:3

    tag:loan-terms'''
    def iati_activities_iati_activity_crs_add_loan_terms(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    code:1

    tag:repayment-type'''
    def iati_activities_iati_activity_crs_add_loan_terms_repayment_type(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    code:4

    tag:repayment-plan'''
    def iati_activities_iati_activity_crs_add_loan_terms_repayment_plan(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    iso-date:2013-09-01

    tag:commitment-date'''
    def iati_activities_iati_activity_crs_add_loan_terms_commitment_date(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    iso-date:2014-01-01

    tag:repayment-first-date'''
    def iati_activities_iati_activity_crs_add_loan_terms_repayment_first_date(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    iso-date:2020-12-31

    tag:repayment-final-date'''
    def iati_activities_iati_activity_crs_add_loan_terms_repayment_final_date(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    year:2014
    currency:GBP
    value-date:2013-05-24

    tag:loan-status'''
    def iati_activities_iati_activity_crs_add_loan_status(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:

    tag:interest-received'''
    def iati_activities_iati_activity_crs_add_loan_status_interest_received(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:

    tag:principal-outstanding'''
    def iati_activities_iati_activity_crs_add_loan_status_principal_outstanding(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:

    tag:principal-arrears'''
    def iati_activities_iati_activity_crs_add_loan_status_principal_arrears(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:

    tag:interest-arrears'''
    def iati_activities_iati_activity_crs_add_loan_status_interest_arrears(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    extraction-date:2014-05-06
    priority:1
    phaseout-year:2016

    tag:fss'''
    def iati_activities_iati_activity_fss(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

    '''atributes:
    year:2014
    value-date:2013-07-03
    currency:GBP

    tag:forecast'''
    def iati_activities_iati_activity_fss_forecast(self,element):
        model = self.get_func_model()
        print element.tag 
        #store element 

        for key in element.attrib:
            print key+' '+element.attrib.get(key)
        return element

