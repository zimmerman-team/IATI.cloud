from IATI_2_01 import Parse as IATI_201_Parser
from iati import models
from geodata.models import Country, Region
import dateutil.parser

class Parse(IATI_201_Parser):

    VERSION = '1.05'#version of iati standard

    sector_vocabulary_trans = {'ADT': 1,
                            'COFOG': 2,
                            'DAC' :3,
                            'DAC-3'  :4,
                            'ISO': 5,
                            'NACE':    6,
                            'NTEE':    7,
                            'WB':  8,
                            'RO':  99,
                            }

    transaction_type_trans = {'IF' :   1,
                                'C' :  2,
                                'D'  : 3,
                                'E'  : 4,
                                'IR' : 5,
                                'LR' : 6,
                                'R'  : 7,
                                'QP' : 8,
                                'Q3' : 9,
                                'CG' : 10}



    def add_narrative_105(self,text,parent):
        if text == '' or text == None:
            return
        parent.save()
        narrative = models.Narrative()
        lang = self.default_lang 
        narrative.language = self.cached_db_call(models.Language,lang)
        narrative.content = text
        narrative.iati_identifier = self.iati_identifier
        narrative.parent_object = parent
        narrative.save()


    def add_organisation(self, elem):
        try:
            ref = elem.attrib['ref']
            org_ref = ref
            type_ref = elem.attrib['type']
            name = elem.text
            for e in elem:
                name = e.text
                break

            org_type = None
            if self.isInt(type_ref) and self.cached_db_call(models.OrganisationType,type_ref) != None:
                org_type = self.cached_db_call(models.OrganisationType,type_ref)

            if models.Organisation.objects.filter(original_ref=ref).exists():
                org =  models.Organisation.objects.filter(original_ref=ref)[0]
                if org.name == name:
                    #organisation found 

                    return org
                else:
                    #organisation found but with different name
                    #look for org with different name but same ref
                    if models.Organisation.objects.filter(original_ref=ref, name=name).exists():
                        #found! return this org
                        found_org = models.Organisation.objects.filter(original_ref=ref, name=org.name)[0]
                        return found_org
                    else:
                        #org not found
                        ref = ref+'_'+name
        
            organisation = models.Organisation.objects.get_or_create(
                code=ref,
                defaults={
                    'name': name,
                    'type': org_type,
                    'original_ref': org_ref

                })[0]
            print "return organisation "+str(organisation)
            return organisation

        except Exception as e:
            print e

    '''atributes:
    ref:AA-AAA-123456789
    type:21

    tag:reporting-org'''
    def iati_activities__iati_activity__reporting_org(self,element):
        model = self.get_func_parent_model()
        organisation = self.add_organisation(element)
        model.secondary_publisher = False
        #print organisation.name
        model.reporting_organisation = organisation
        self.set_func_model(organisation)
        self.add_narrative_105(element.text,organisation)
        #store element 
        return element

 
    '''atributes:
    ref:ABC123-XYZ
    owner-name:A1
    tag:other-identifier'''
    def iati_activities__iati_activity__other_identifier(self,element):
        model = self.get_func_parent_model()
        identifier = element.text
        owner_ref = element.attrib.get('owner-ref')
        owner_name = element.attrib.get('owner-name')
        

        new_other_identifier = models.OtherIdentifier(activity=model, identifier=identifier,owner_name=owner_name,owner_ref=owner_ref)


        self.set_func_model(new_other_identifier)
        return element
    '''atributes:

    tag:title'''
    def iati_activities__iati_activity__title(self,element):
        model = self.get_func_parent_model()
        title = models.Title()
        title.activity = model
        self.add_narrative_105(element.text,title)
        self.set_func_model(title)
        return element

    '''atributes:
    type:1

    tag:description'''
    def iati_activities__iati_activity__description(self,element):
        model = self.get_func_parent_model()
        description = models.Description()
        description.activity = model
        desc_type = self.cached_db_call_no_version(models.DescriptionType, element.attrib.get('type'),keyDB='name')
        description.type = desc_type
        self.add_narrative_105(element.text,description)
        self.set_func_model(description)

        return element


    '''atributes:

    tag:organisation'''
    def iati_activities__iati_activity__contact_info__organisation(self,element):
        model = self.get_func_parent_model()
        contactInfoOrganisation =  models.ContactInfoOrganisation()
        contactInfoOrganisation.ContactInfo = model;
        self.add_narrative_105(element.text,contactInfoOrganisation)
        #store element 
        return element

    '''atributes:

    tag:person-name'''
    def iati_activities__iati_activity__contact_info__person_name(self,element):
        model = self.get_func_parent_model()
        contactInfoPersonName =  models.ContactInfoPersonName()
        contactInfoPersonName.ContactInfo = model
        self.add_narrative_105(element.text,contactInfoPersonName)
        #store element 
        return element

    '''atributes:

    tag:job-title'''
    def iati_activities__iati_activity__contact_info__job_title(self,element):
        model = self.get_func_parent_model()
        contactInfoJobTitle =  models.ContactInfoJobTitle()
        contactInfoJobTitle.ContactInfo = model
        self.add_narrative_105(element.text,contactInfoJobTitle)
        #store element 
        return element


    '''atributes:

    tag:mailing-address'''
    def iati_activities__iati_activity__contact_info__mailing_address(self,element):
        model = self.get_func_parent_model()
        contactInfoMailingAddress = models.ContactInfoMailingAddress()
        contactInfoMailingAddress.ContactInfo = model
        self.add_narrative_105(element.text,contactInfoMailingAddress)
        #store element 
        return element


    '''atributes:
    ref:BB-BBB-123456789
    role:Funding
    type:40

    tag:participating-org'''
    def iati_activities__iati_activity__participating_org(self,element):
        model = self.get_func_parent_model()
        org = self.add_organisation(element)
        activityParticipatingOrganisation = models.ActivityParticipatingOrganisation()
        activityParticipatingOrganisation.org = org
        activityParticipatingOrganisation.activity = model
        activityParticipatingOrganisation.type = self.cached_db_call(models.OrganisationType,element.attrib.get('type'))
        activityParticipatingOrganisation.role = self.cached_db_call(models.OrganisationRole, element.attrib.get('role'))

        self.add_narrative_105(element.text,activityParticipatingOrganisation)
        #store element 
        return element


    '''atributes:

    tag:name'''
    def iati_activities__iati_activity__location__name(self,element):
        model = self.get_func_parent_model()
        location_name = models.LocationName()
        location_name.location = model
        self.add_narrative_105(element.text,location_name)
        return element

    '''atributes:

    tag:description'''
    def iati_activities__iati_activity__location__description(self,element):
        model = self.get_func_parent_model()
        location_description = models.LocationDescription()
        location_description.location  = model
        self.add_narrative_105(element.text,location_description)
        #store element 
        return element

    '''atributes:

    tag:activity-description'''
    def iati_activities__iati_activity__location__activity_description(self,element):
        model = self.get_func_parent_model()
        location_activity_description = models.LocationActivityDescription()
        location_activity_description.location  = model
        self.add_narrative_105(element.text,location_activity_description)
        #store element 
        return element


    '''atributes:
    code:111
    vocabulary:DAC

    tag:sector'''
    def iati_activities__iati_activity__sector(self,element):
        model = self.get_func_parent_model()
        sector = models.Sector()
        sector.activity = model
        sector.code = element.attrib.get('code')
        sector.vocabulary = self.cached_db_call(models.Vocabulary,self.sector_vocabulary_trans.get(element.attrib.get('vocabulary')))
        sector.save()
         
        return element

    '''atributes:

    tag:description'''
    def iati_activities__iati_activity__country_budget_items__budget_item__description(self,element):
        model = self.get_func_parent_model()
        budget_item_description = models.BudgetItemDescription()
        budget_item_description.budget_item = model
        self.add_narrative_105(element.text,budget_item_description)
        return element



    '''atributes:

    tag:description'''
    def iati_activities__iati_activity__transaction__description(self,element):
        model = self.get_func_parent_model()
        description = models.TransactionDescription()
        description.transaction = model
        self.add_narrative_105(element.text,description)
        return element


    '''atributes:
    provider-activity-id:BB-BBB-123456789-1234AA
    ref:BB-BBB-123456789

    tag:provider-org'''
    def iati_activities__iati_activity__transaction__provider_org(self,element):
        model = self.get_func_parent_model()
        model.provider_activity = element.attrib.get('provider-activity-id')
        
        provider_organisation_name = element.text
            

        provider_org = self.add_organisation(element)
        transaction_provider = models.TransactionProvider()
        transaction_provider.transaction = model
        self.add_narrative_105(element.text,transaction_provider)
        #store element 
        return element

    '''atributes:
    receiver-activity-id:AA-AAA-123456789-1234
    ref:AA-AAA-123456789

    tag:receiver-org'''
    def iati_activities__iati_activity__transaction__receiver_org(self,element):
        model = self.get_func_parent_model()

        model.receiver_activity = element.attrib.get('receiver-activity-id')
      
        reciever_org = self.add_organisation(element)
        transaction_receiver = models.TransactionReciever()
        transaction_receiver.transaction = model
        self.add_narrative_105(element.text,transaction_receiver)
        #store element 
        return element



    '''atributes:

    tag:title'''
    def iati_activities__iati_activity__document_link__title(self,element):
        model = self.get_func_parent_model()
        document_link_title = models.DocumentLinkTitle()
        document_link_title.document_link = model
        self.add_narrative_105(element.text,document_link_title)
        return element


    '''atributes:

    tag:activity-website'''
    def iati_activities__iati_activity__activity_website(self,element):
        model = self.get_func_parent_model()
        website = models.ActivityWebsite()
        website.activity = model
        website.url = element.text
        website.save()
        #store element 
        return element




    '''atributes:
    type:1

    tag:condition'''
    def iati_activities__iati_activity__conditions__condition(self,element):
        model = self.get_func_parent_model()
        condition = models.Condition()
        condition.activity = model
        condition.type = self.cached_db_call(models.ConditionType,element.attrib.get('type'))
        self.add_narrative_105(element.text,condition) 
        return element



    '''atributes:

    tag:title'''
    def iati_activities__iati_activity__result__title(self,element):
        model = self.get_func_parent_model()
        result_title = models.ResultTitle()
        result_title.result = model
        self.add_narrative_105(element.text,result_title)
        return element

    '''atributes:

    tag:description'''
    def iati_activities__iati_activity__result__description(self,element):
        model = self.get_func_parent_model()
        result_description = models.ResultDescription()
        result_description.result = model
        self.add_narrative_105(element.text,result_description)
        return element


    '''atributes:

    tag:title'''
    def iati_activities__iati_activity__result__indicator__title(self,element):
        model = self.get_func_parent_model()
        result_indicator_title = models.ResultIndicatorTitle()
        result_indicator_title.result_indicator = model
        self.add_narrative_105(element.text,result_indicator_title)
        return element

    '''atributes:

    tag:description'''
    def iati_activities__iati_activity__result__indicator__description(self,element):
        model = self.get_func_parent_model()
        result_indicator_description = models.ResultIndicatorDescription()
        result_indicator_description.result_indicator = model
        self.add_narrative_105(element.text,result_indicator_description)
        #store element 
        return element


    '''atributes:

    tag:comment'''
    def iati_activities__iati_activity__result__indicator__baseline__comment(self,element):
        model = self.get_func_parent_model()
        indicator_baseline_comment = models.ResultIndicatorBaseLineComment()
        indicator_baseline_comment.result_indicator = model
        self.add_narrative_105(element.text,indicator_baseline_comment)
        return element


    '''atributes:

    tag:comment'''
    def iati_activities__iati_activity__result__indicator__period__target__comment(self,element):
        model = self.get_func_parent_model()
        period_target_comment = models.ResultIndicatorPeriodTargetComment()
        period_target_comment.result_indicator_period = model
        self.add_narrative_105(element.text,period_target_comment)
        return element


    '''atributes:

    tag:comment'''
    def iati_activities__iati_activity__result__indicator__period__actual__comment(self,element):
        model = self.get_func_parent_model()
        period_actual_comment = models.ResultIndicatorPeriodActualComment()
        period_actual_comment.result_indicator_period = model
        self.add_narrative_105(element.text,period_actual_comment)
        return element


    '''atributes:
    code:1
    significance:1

    tag:aidtype-flag'''
    def iati_activities__iati_activity__crs_add__aidtype_flag(self,element):
        model = self.get_func_parent_model()
        crs_other_flags = models.CrsAddOtherFlags()
        crs_other_flags.crs_add = model
        crs_other_flags.other_flags =  self.cached_db_call_no_version(models.OtherFlags,element.attrib.get('code'))
        crs_other_flags.significance = element.attrib.get('significance')
        crs_other_flags.save()
        #store element 
        return element


    '''atributes:
    year:2014
    value-date:2013-07-03
    currency:GBP

    tag:forecast'''
    def iati_activities__iati_activity__fss__forecast(self,element):
        model = self.get_func_parent_model()
        fss_forecast = models.FfsForecast()
        fss_forecast.ffs = model
        fss_forecast.year = element.attrib.get('year')
        fss_forecast.value_date = self.validate_date(element.attrib.get('value-date'))
        fss_forecast.currency = self.cached_db_call_no_version(models.Currency,element.attrib.get('currency'))
        return element




   

