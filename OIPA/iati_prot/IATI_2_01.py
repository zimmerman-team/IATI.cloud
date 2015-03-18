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
        #print parent
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
    def iati_activities__iati_activity(self,element):
        
        self.default_lang = 'en'
        activity = models.Activity()
        self.set_func_model(activity)
        activity.default_currency = self.cached_db_call(models.Currency, element.attrib.get('default-currency'))
        activity.save()
        return element

    '''atributes:

    tag:iati-identifier'''
    def iati_activities__iati_activity__iati_identifier(self,element):
        model = self.get_func_model()#model is activity
        model.iati_identifier = element.text
        
        return # endpoint return None 

    '''atributes:
    ref:AA-AAA-123456789
    type:40
    secondary-reporter:0

    tag:reporting-org'''
    def iati_activities__iati_activity__reporting_org(self,element):
        model = self.get_func_model()
        organisation = self.add_organisation(element)
        organisation.save()
        #print organisation.name
        model.reporting_organisation = organisation
        self.set_func_model(organisation)
    
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__reporting_org__narrative(self,element):
        model = self.get_func_model()
        self.add_narrative(element,model)

        return element


    '''atributes:

    tag:title'''
    def iati_activities__iati_activity__title(self,element):
        model = self.get_func_model()
        title = models.Title()
        title.activity = model
        title.save()
        self.set_func_model(title)
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__title__narrative(self,element):
        model = self.get_func_model()
        self.add_narrative(element,model)
        
        return element

    '''atributes:
    type:1

    tag:description'''
    def iati_activities__iati_activity__description(self,element):
        model = self.get_func_model(class_name='Activity')
        description = models.Description()

        description.activity = model
        desc_type = self.cached_db_call(models.DescriptionType, element.attrib.get('type'))
        description.type = desc_type
        description.save()
        self.set_func_model(description)
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__description__narrative(self,element):
        model = self.get_func_model()
        self.add_narrative(element,model)
        return element


    '''atributes:
    ref:BB-BBB-123456789
    role:1
    type:40

    tag:participating-org'''
    def iati_activities__iati_activity__participating_org(self,element):
        model = self.get_func_model(class_name='Activity')
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
    def iati_activities__iati_activity__participating_org__narrative(self,element):
        model = self.get_func_model()
        self.add_narrative(element,model)
        return element

    '''atributes:
    ref:ABC123-XYZ
    type:A1

    tag:other-identifier'''
    def iati_activities__iati_activity__other_identifier(self,element):
        model = self.get_func_model(class_name='Activity')
        identifier = element.attrib.get('ref')
        type = self.cached_db_call(models.OtherIdentifierType, element.attrib.get('type'))

        new_other_identifier = models.OtherIdentifier(activity=model, identifier=identifier,type=type)
        self.set_func_model(new_other_identifier)
        new_other_identifier.save()
        return element

    '''atributes:
    ref:AA-AAA-123456789

    tag:owner-org'''
    def iati_activities__iati_activity__other_identifier__owner_org(self,element):
        model = self.get_func_model()
        model.owner_ref = element.attrib.get('ref')
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__other_identifier__owner_org__narrative(self,element):
        model = self.get_func_model()
        self.add_narrative(element,model)
        return element

    '''atributes:
    code:2

    tag:activity-status'''
    def iati_activities__iati_activity__activity_status(self,element):
        model = self.get_func_model(class_name='Activity')
        model.activity_status = self.cached_db_call(models.ActivityStatus,element.attrib.get('code'))

        return element

    '''atributes:
    iso-date:2012-04-15
    type:1

    tag:activity-date'''
    def iati_activities__iati_activity__activity_date(self,element):
        model = self.get_func_model()
        activity_date  = models.ActivityDate()
        activity_date.iso_date = element.attrib.get('iso_date')
        activity_date.type = self.cached_db_call(models.ActivityDateType,element.attrib.get('type'))
        activity_date.save()
        self.set_func_model(activity_date)
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__activity_date__narrative(self,element):
        model = self.get_func_model()
        self.add_narrative(element,model)
        return element

    '''atributes:
    type:1

    tag:contact-info'''
    def iati_activities__iati_activity__contact_info(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:

    tag:organisation'''
    def iati_activities__iati_activity__contact_info__organisation(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__contact_info__organisation__narrative(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:

    tag:department'''
    def iati_activities__iati_activity__contact_info__department(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__contact_info__department__narrative(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:

    tag:person-name'''
    def iati_activities__iati_activity__contact_info__person_name(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__contact_info__person_name__narrative(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:

    tag:job-title'''
    def iati_activities__iati_activity__contact_info__job_title(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__contact_info__job_title__narrative(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:

    tag:telephone'''
    def iati_activities__iati_activity__contact_info__telephone(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:

    tag:email'''
    def iati_activities__iati_activity__contact_info__email(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:

    tag:website'''
    def iati_activities__iati_activity__contact_info__website(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:

    tag:mailing-address'''
    def iati_activities__iati_activity__contact_info__mailing_address(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__contact_info__mailing_address__narrative(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    code:3

    tag:activity-scope'''
    def iati_activities__iati_activity__activity_scope(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    code:AF
    percentage:25

    tag:recipient-country'''
    def iati_activities__iati_activity__recipient_country(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    code:489
    vocabulary:1
    percentage:25

    tag:recipient-region'''
    def iati_activities__iati_activity__recipient_region(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    ref:AF-KAN

    tag:location'''
    def iati_activities__iati_activity__location(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    code:1

    tag:location-reach'''
    def iati_activities__iati_activity__location__location_reach(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    vocabulary:G1
    code:1453782

    tag:location-id'''
    def iati_activities__iati_activity__location__location_id(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:

    tag:name'''
    def iati_activities__iati_activity__location__name(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__location__name__narrative(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:

    tag:description'''
    def iati_activities__iati_activity__location__description(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__location__description__narrative(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:

    tag:activity-description'''
    def iati_activities__iati_activity__location__activity_description(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__location__activity_description__narrative(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    vocabulary:G1
    level:1
    code:1453782

    tag:administrative'''
    def iati_activities__iati_activity__location__administrative(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    srsName:http://www.opengis.net/def/crs/EPSG/0/4326

    tag:point'''
    def iati_activities__iati_activity__location__point(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:

    tag:pos'''
    def iati_activities__iati_activity__location__point__pos(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    code:1

    tag:exactness'''
    def iati_activities__iati_activity__location__exactness(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    code:2

    tag:location-class'''
    def iati_activities__iati_activity__location__location_class(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    code:ADMF

    tag:feature-designation'''
    def iati_activities__iati_activity__location__feature_designation(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    vocabulary:2
    code:111
    percentage:50

    tag:sector'''
    def iati_activities__iati_activity__sector(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    vocabulary:2

    tag:country-budget-items'''
    def iati_activities__iati_activity__country_budget_items(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    code:1.1.1
    percentage:50

    tag:budget-item'''
    def iati_activities__iati_activity__country_budget_items__budget_item(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:

    tag:description'''
    def iati_activities__iati_activity__country_budget_items__budget_item__description(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__country_budget_items__budget_item__description__narrative(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    vocabulary:1
    code:2
    significance:3

    tag:policy-marker'''
    def iati_activities__iati_activity__policy_marker(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    code:1

    tag:collaboration-type'''
    def iati_activities__iati_activity__collaboration_type(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    code:10

    tag:default-flow-type'''
    def iati_activities__iati_activity__default_flow_type(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    code:110

    tag:default-finance-type'''
    def iati_activities__iati_activity__default_finance_type(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    code:A01

    tag:default-aid-type'''
    def iati_activities__iati_activity__default_aid_type(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    code:3

    tag:default-tied-status'''
    def iati_activities__iati_activity__default_tied_status(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    type:1

    tag:budget'''
    def iati_activities__iati_activity__budget(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    iso-date:2014-01-01

    tag:period-start'''
    def iati_activities__iati_activity__budget__period_start(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    iso-date:2014-12-31

    tag:period-end'''
    def iati_activities__iati_activity__budget__period_end(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    currency:EUR
    value-date:2014-01-01

    tag:value'''
    def iati_activities__iati_activity__budget__value(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    type:1

    tag:planned-disbursement'''
    def iati_activities__iati_activity__planned_disbursement(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    iso-date:2014-01-01

    tag:period-start'''
    def iati_activities__iati_activity__planned_disbursement__period_start(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    iso-date:2014-12-31

    tag:period-end'''
    def iati_activities__iati_activity__planned_disbursement__period_end(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    currency:EUR
    value-date:2014-01-01

    tag:value'''
    def iati_activities__iati_activity__planned_disbursement__value(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    percentage:88.8

    tag:capital-spend'''
    def iati_activities__iati_activity__capital_spend(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    ref:1234

    tag:transaction'''
    def iati_activities__iati_activity__transaction(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    code:1

    tag:transaction-type'''
    def iati_activities__iati_activity__transaction__transaction_type(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    iso-date:2012-01-01

    tag:transaction-date'''
    def iati_activities__iati_activity__transaction__transaction_date(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    currency:EUR
    value-date:2012-01-01

    tag:value'''
    def iati_activities__iati_activity__transaction__value(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:

    tag:description'''
    def iati_activities__iati_activity__transaction__description(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__transaction__description__narrative(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    provider-activity-id:BB-BBB-123456789-1234AA
    ref:BB-BBB-123456789

    tag:provider-org'''
    def iati_activities__iati_activity__transaction__provider_org(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__transaction__provider_org__narrative(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    receiver-activity-id:AA-AAA-123456789-1234
    ref:AA-AAA-123456789

    tag:receiver-org'''
    def iati_activities__iati_activity__transaction__receiver_org(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__transaction__receiver_org__narrative(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    code:1

    tag:disbursement-channel'''
    def iati_activities__iati_activity__transaction__disbursement_channel(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    vocabulary:2
    code:111

    tag:sector'''
    def iati_activities__iati_activity__transaction__sector(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    code:AF

    tag:recipient-country'''
    def iati_activities__iati_activity__transaction__recipient_country(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    code:456
    vocabulary:1

    tag:recipient-region'''
    def iati_activities__iati_activity__transaction__recipient_region(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    code:10

    tag:flow-type'''
    def iati_activities__iati_activity__transaction__flow_type(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    code:110

    tag:finance-type'''
    def iati_activities__iati_activity__transaction__finance_type(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    code:A01

    tag:aid-type'''
    def iati_activities__iati_activity__transaction__aid_type(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    code:3

    tag:tied-status'''
    def iati_activities__iati_activity__transaction__tied_status(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    format:application/vnd.oasis.opendocument.text
    url:http:www.example.org/docs/report_en.odt

    tag:document-link'''
    def iati_activities__iati_activity__document_link(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:

    tag:title'''
    def iati_activities__iati_activity__document_link__title(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__document_link__title__narrative(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    code:A01

    tag:category'''
    def iati_activities__iati_activity__document_link__category(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    code:en

    tag:language'''
    def iati_activities__iati_activity__document_link__language(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    ref:AA-AAA-123456789-6789
    type:1

    tag:related-activity'''
    def iati_activities__iati_activity__related_activity(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    name:Project Status
    value:7
    iati-equivalent:activity-status

    tag:legacy-data'''
    def iati_activities__iati_activity__legacy_data(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    attached:1

    tag:conditions'''
    def iati_activities__iati_activity__conditions(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    type:1

    tag:condition'''
    def iati_activities__iati_activity__conditions__condition(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__conditions__condition__narrative(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    type:1
    aggregation-status:1

    tag:result'''
    def iati_activities__iati_activity__result(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:

    tag:title'''
    def iati_activities__iati_activity__result__title(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__result__title__narrative(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:

    tag:description'''
    def iati_activities__iati_activity__result__description(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__result__description__narrative(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    measure:1
    ascending:1

    tag:indicator'''
    def iati_activities__iati_activity__result__indicator(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:

    tag:title'''
    def iati_activities__iati_activity__result__indicator__title(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__result__indicator__title__narrative(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:

    tag:description'''
    def iati_activities__iati_activity__result__indicator__description(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:

    tag:narrative'''
    def iati_activities__iati_activity__result__indicator__description__narrative(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    year:2012
    value:10

    tag:baseline'''
    def iati_activities__iati_activity__result__indicator__baseline(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:

    tag:period'''
    def iati_activities__iati_activity__result__indicator__period(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    iso-date:2013-01-01

    tag:period-start'''
    def iati_activities__iati_activity__result__indicator__period__period_start(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    iso-date:2013-03-31

    tag:period-end'''
    def iati_activities__iati_activity__result__indicator__period__period_end(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    value:10

    tag:target'''
    def iati_activities__iati_activity__result__indicator__period__target(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    value:11

    tag:actual'''
    def iati_activities__iati_activity__result__indicator__period__actual(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:

    tag:crs-add'''
    def iati_activities__iati_activity__crs_add(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    code:1
    significance:1

    tag:other-flags'''
    def iati_activities__iati_activity__crs_add__other_flags(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    rate-1:4
    rate-2:3

    tag:loan-terms'''
    def iati_activities__iati_activity__crs_add__loan_terms(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    code:1

    tag:repayment-type'''
    def iati_activities__iati_activity__crs_add__loan_terms__repayment_type(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    code:4

    tag:repayment-plan'''
    def iati_activities__iati_activity__crs_add__loan_terms__repayment_plan(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    iso-date:2013-09-01

    tag:commitment-date'''
    def iati_activities__iati_activity__crs_add__loan_terms__commitment_date(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    iso-date:2014-01-01

    tag:repayment-first-date'''
    def iati_activities__iati_activity__crs_add__loan_terms__repayment_first_date(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    iso-date:2020-12-31

    tag:repayment-final-date'''
    def iati_activities__iati_activity__crs_add__loan_terms__repayment_final_date(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    year:2014
    currency:GBP
    value-date:2013-05-24

    tag:loan-status'''
    def iati_activities__iati_activity__crs_add__loan_status(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:

    tag:interest-received'''
    def iati_activities__iati_activity__crs_add__loan_status__interest_received(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:

    tag:principal-outstanding'''
    def iati_activities__iati_activity__crs_add__loan_status__principal_outstanding(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:

    tag:principal-arrears'''
    def iati_activities__iati_activity__crs_add__loan_status__principal_arrears(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:

    tag:interest-arrears'''
    def iati_activities__iati_activity__crs_add__loan_status__interest_arrears(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    extraction-date:2014-05-06
    priority:1
    phaseout-year:2016

    tag:fss'''
    def iati_activities__iati_activity__fss(self,element):
        model = self.get_func_model()
        #store element 
        return element

    '''atributes:
    year:2014
    value-date:2013-07-03
    currency:GBP

    tag:forecast'''
    def iati_activities__iati_activity__fss__forecast(self,element):
        model = self.get_func_model()
        #store element 
        return element

