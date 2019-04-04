"""
This module reletated to IATI Standard version 2.03
http://reference.iatistandard.org/203/activity-standard/iati-activities/iati-activity/
"""
from lxml import etree


class ElementReference(object):
    """
    http://reference.iatistandard.org/203/activity-standard/elements/
    """
    element = None
    parent_element = None
    data = None

    def __init__(self, parent_element, data, element=None):
        self.parent_element = parent_element
        self.data = data

        if element:
            self.element = element

    def create(self):
        pass


class NarrativeReference(ElementReference):
    """
    http://reference.iatistandard.org/203/activity-standard/iati-activities/iati-activity/title/narrative/
    """
    element = 'narrative'
    text_key = 'text'
    lang_key = 'en'
    language_key = 'language'
    language_code_key = 'code'
    default_language_code = 'en'

    def create(self):
        narrative_element = etree.SubElement(self.parent_element, self.element)
        narrative_element.text = self.data.get(self.text_key)

        language = self.data.get('language')
        if language:
            language_code = language.get(self.language_code_key)
            if language_code not in [self.default_language_code, None]:
                narrative_element.set(
                    '{http://www.w3.org/XML/1998/namespace}lang',
                    language_code
                )


class ElementWithNarrativeReference(ElementReference):
    narrative_element = 'narrative'
    narratives_key = 'narratives'

    def create_narrative(self, parent_element):
        if self.narratives_key in self.data:
            for narrative in self.data.get(self.narratives_key):
                narrative_reference = NarrativeReference(
                    parent_element=parent_element,
                    data=narrative
                )
                narrative_reference.create()

    def create(self):
        self.create_narrative(
            etree.SubElement(self.parent_element, self.element)
        )


class TitleReference(ElementWithNarrativeReference):
    """
    http://reference.iatistandard.org/203/activity-standard/iati-activities/iati-activity/title/
    """
    element = 'title'


class DescriptionReference(ElementWithNarrativeReference):
    """
    http://reference.iatistandard.org/203/activity-standard/iati-activities/iati-activity/description/
    """
    element = 'description'
    description_type_key = 'type'
    attribute_type_name = 'type'

    def create(self):
        description_element = etree.SubElement(
            self.parent_element, self.element
        )

        # Set attribute type
        description_type = self.data.get(self.description_type_key)
        if description_type:
            description_element.set(self.attribute_type_name, description_type)

        self.create_narrative(description_element)


class ActivityDateReference(ElementReference):
    element = 'activity-date'
    iso_date_key = 'iso_date'
    type_key = 'type'
    iso_date_attr = 'iso-date'
    type_attr = 'type'
    type_value_key = 'code'

    def create(self):
        # Only has iso date
        iso_date = self.data.get(self.iso_date_key)
        if iso_date:
            iso_date_element = etree.SubElement(
                self.parent_element, self.element
            )

            # Set attribute iso date
            iso_date_element.set(self.iso_date_attr, iso_date)

            # Set attribute type date
            type_date = self.data.get(self.type_key)
            if type_date:
                # type date is dictionary
                # Reference: ActivityDateSerializer
                type_value = type_date.get(self.type_value_key)
                if type_value:
                    iso_date_element.set(self.type_attr, type_value)


class ReportingOrgReference(ElementWithNarrativeReference):
    """
    http://reference.iatistandard.org/203/activity-standard/iati-activities/iati-activity/reporting-org/
    """
    element = 'reporting-org'
    ref_key = 'ref'
    ref_attr = 'ref'
    type_dict_key = 'type'
    type_value_key = 'code'
    type_attr = 'type'
    secondary_reporter_key = 'secondary_reporter'
    secondary_reporter_attr = 'secondary-reporter'

    def create(self):
        reporting_org_element = etree.SubElement(
            self.parent_element, self.element
        )
        ref_value = self.data.get(self.ref_key)
        if ref_value:
            reporting_org_element.set(self.ref_attr, ref_value)

        type_dict = self.data.get(self.type_dict_key)
        if type_dict:
            type_value = type_dict.get(self.type_value_key)
            if type_value:
                reporting_org_element.set(self.type_attr, type_value)

        secondary_reporter_value = self.data.get(self.secondary_reporter_key)
        if secondary_reporter_value is not None:
            reporting_org_element.set(
                self.secondary_reporter_attr, '1'
                if secondary_reporter_value else '0'
            )

        self.create_narrative(reporting_org_element)


class ParticipatingOrgReference(ElementWithNarrativeReference):
    """
    http://reference.iatistandard.org/203/activity-standard/iati-activities/iati-activity/participating-org/
    """
    element = 'participating-org'
    ref_key = 'ref'
    ref_attr = 'ref'
    type_dict_key = 'type'
    type_value_key = 'code'
    type_attr = 'type'
    role_dict_key = 'role'
    role_key = 'code'
    role_attr = 'role'

    def create(self):
        participating_org_element = etree.SubElement(
            self.parent_element, self.element
        )
        ref_value = self.data.get(self.ref_key)
        if ref_value:
            participating_org_element.set(self.ref_attr, ref_value)

        type_dict = self.data.get(self.type_dict_key)
        if type_dict:
            type_value = type_dict.get(self.type_value_key)
            if type_value:
                participating_org_element.set(self.type_attr, type_value)

        role_dict = self.data.get(self.role_dict_key)
        if role_dict:
            role_value = role_dict.get(self.role_key)
            if role_value:
                participating_org_element.set(self.role_attr, role_value)

        self.create_narrative(participating_org_element)


class ContactInfoReference(ElementReference):
    """
    http://reference.iatistandard.org/203/activity-standard/iati-activities/iati-activity/contact-info/
    """
    element = 'contact-info'
    # Type attribute
    type_dict_key = 'type'
    type_key = 'code'
    type_attr = 'type'
    # Organisation element
    organisation_dict_key = 'organisation'
    organisation_element = 'organisation'
    # Email element
    email_key = 'email'
    email_element = 'email'
    # Mailing address element
    mailing_address_dict_key = 'mailing_address'
    mailing_address_element = 'mailing-address'
    # Telephone element
    telephone_key = 'telephone'
    telephone_element = 'telephone'
    # Website element
    website_key = 'website'
    website_element = 'website'
    # Department element
    department_dict_key = 'department'
    department_element = 'department'
    # Person name element
    person_name_dict_key = 'person_name'
    person_name_element = 'person-name'
    # Job title element
    job_title_dict_key = 'job_title'
    job_title_element = 'job-title'

    def create(self):
        contact_info_element = etree.SubElement(
            self.parent_element, self.element
        )

        # Type attribute
        type_dict = self.data.get(self.type_dict_key)
        if type_dict:
            type_value = type_dict.get(self.type_key)
            contact_info_element.set(self.type_attr, type_value)

        # Organisation element
        organisation_dict = self.data.get(self.organisation_dict_key)
        if organisation_dict:
            organisation_narrative = ElementWithNarrativeReference(
                parent_element=contact_info_element,
                data=organisation_dict
            )
            organisation_narrative.element = self.organisation_element
            organisation_narrative.create()

        # Email element
        email_value = self.data.get(self.email_key)
        if email_value:
            email_element = etree.SubElement(
                contact_info_element, self.email_element
            )
            email_element.text = email_value

        # Mailing address element
        mailing_address_dict = self.data.get(self.mailing_address_dict_key)
        if mailing_address_dict:
            mailing_address_narrative = ElementWithNarrativeReference(
                parent_element=contact_info_element,
                data=mailing_address_dict
            )
            mailing_address_narrative.element = self.mailing_address_element
            mailing_address_narrative.create()

        # Telephone element
        telephone_value = self.data.get(self.telephone_key)
        if telephone_value:
            telephone_element = etree.SubElement(
                contact_info_element, self.telephone_element
            )
            telephone_element.text = telephone_value

        # Website element
        website_value = self.data.get(self.website_key)
        if website_value:
            website_element = etree.SubElement(
                contact_info_element, self.website_element
            )
            website_element.text = website_value

        # Department element
        department_dict = self.data.get(self.department_dict_key)
        if department_dict:
            department_narrative = ElementWithNarrativeReference(
                parent_element=contact_info_element,
                data=department_dict
            )
            department_narrative.element = self.mailing_address_element
            department_narrative.create()

        # Person name element
        person_name_dict = self.data.get(self.person_name_dict_key)
        if person_name_dict:
            person_name_narrative = ElementWithNarrativeReference(
                parent_element=contact_info_element,
                data=person_name_dict
            )
            person_name_narrative.element = self.person_name_element
            person_name_narrative.create()

        # Job title element
        job_title_dict = self.data.get(self.job_title_dict_key)
        if job_title_dict:
            job_title_narrative = ElementWithNarrativeReference(
                parent_element=contact_info_element,
                data=job_title_dict
            )
            job_title_narrative.element = self.job_title_element
            job_title_narrative.create()


class TransactionReference(ElementReference):
    """
    http://reference.iatistandard.org/202/activity-standard/iati-activities/iati-activity/transaction/
    """
    element = 'transaction'
    # Ref
    ref = {
        'key': 'ref',
        'attr': 'ref'
    }
    # Transaction type
    transaction_type = {
        'element': 'transaction-type',
        'key': 'transaction_type',
        # Attributes
        'code': {
            'key': 'code',
            'attr': 'code'
        }
    }
    # Transaction date
    transaction_date = {
        'element': 'transaction-date',
        'key': 'transaction_date',
        'attr': 'iso-date'
    }
    # Value
    value = {
        'element': 'value',
        'key': 'value',
        # Attributes
        'currency': {
            'key': 'currency',
            'code': {
                'key': 'code',
                'attr': 'currency'
            }
        },
        'date': {
            'key': 'value_date',
            'attr': 'value-date'
        }
    }
    # Flow type
    flow_type = {
        'element': 'flow-type',
        'key': 'flow_type',
        'code': {
            'key': 'code',
            'attr': 'code'
        }
    }
    # Finance type
    finance_type = {
        'element': 'finance-type',
        'key': 'finance_type',
        'code': {
            'key': 'code',
            'attr': 'code'
        }
    }
    # Aid type
    aid_type = {
        'element': 'aid-type',
        'key': 'aid_type',
        'code': {
            'key': 'code',
            'attr': 'code'
        }
    }
    # tied_status
    tied_status = {
        'element': 'tied-status',
        'key': 'tied_status',
        'code': {
            'key': 'code',
            'attr': 'code'
        }
    }
    # Provider Organisation
    provider_organisation = {
        'element': 'provider-org',
        'key': 'provider_organisation',
        # Attributes
        'ref': {
            'key': 'ref',
            'attr': 'ref'
        },
        'provider_activity_id': {
            'key': 'provider_activity_id',
            'attr': 'provider-activity-id'
        },
        'type': {
            'key': 'type',
            'attr': 'type'
        },
        'narratives': {
            'element': 'narrative',
            'key': 'narratives',
        }
    }
    # Recipient country
    recipient_countries = {
        'element': 'recipient-country',
        'key': 'recipient_countries',
        'country': {
            'key': 'country',
            'code': {
                'key': 'code',
                'attr': 'code'
            }
        },
        'percentage': {
            'key': 'percentage',
            'attr': 'percentage'
        }
    }
    # Recipient region
    recipient_regions = {
        'element': 'recipient-region',
        'key': 'recipient_regions',
        'region': {
            'key': 'region',
            'code': {
                'key': 'code',
                'attr': 'code'
            }
        },
        'vocabulary': {
            'key': 'vocabulary',
            'code': {
                'key': 'code',
                'attr': 'vocabulary',
            }
        }
    }
    # Sector
    sectors = {
        'element': 'sector',
        'key': 'sectors',
        'sector': {
            'key': 'sector',
            'code': {
                'key': 'code',
                'attr': 'code'
            },
        },
        'vocabulary': {
            'key': 'vocabulary',
            'code': {
                'key': 'code',
                'attr': 'vocabulary'
            },
        }
    }

    def create(self):
        transaction_element = etree.SubElement(
            self.parent_element, self.element
        )

        # Ref
        ref_value = self.data.get(self.ref.get('key'))
        if ref_value:
            transaction_element.set(self.ref.get('attr'), ref_value)

        # Transaction type
        transaction_dict = self.data.get(
            self.transaction_type.get('key')
        )
        if transaction_dict:
            transaction_type_element = etree.SubElement(
                transaction_element, self.transaction_type.get('element')
            )

            # Transaction type element: code attribute
            code_value = transaction_dict.get(
                self.transaction_type.get('code').get('key')
            )
            if code_value:
                transaction_type_element.set(
                    self.transaction_type.get('code').get('attr'),
                    code_value
                )

        # Transaction date
        transaction_date_value = self.data.get(
            self.transaction_date.get('key')
        )
        if transaction_date_value:
            transaction_date_element = etree.SubElement(
                transaction_element, self.transaction_date.get('element')
            )
            transaction_date_element.set(
                self.transaction_date.get('attr'),
                transaction_date_value
            )

        # Value
        value = self.data.get(self.value.get('key'))
        if value:
            value_element = etree.SubElement(
                transaction_element, self.value.get('element')
            )
            value_element.text = value

            # Attributes
            # Currency
            currency_dict = self.data.get(
                self.value.get('currency').get('key')
            )
            if currency_dict:
                code_value = currency_dict.get(
                    self.value.get('currency').get('code').get('key')
                )
                if code_value:
                    value_element.set(
                        self.value.get('currency').get('code').get('attr'),
                        code_value
                    )

            # Attributes
            # Value date
            value_date = self.data.get(self.value.get('date').get('key'))
            if value_date:
                value_element.set(
                    self.value.get('date').get('attr'),
                    value_date
                )

        # Flow type
        flow_type_dict = self.data.get(
            self.flow_type.get('key')
        )
        if flow_type_dict:
            flow_type_element = etree.SubElement(
                transaction_element, self.flow_type.get('element')
            )

            # Attributes
            # Code
            code = flow_type_dict.get(self.flow_type.get('code').get('key'))
            if code:
                flow_type_element.set(
                    self.flow_type.get('code').get('attr'),
                    code
                )

        # Finance type
        finance_type_dict = self.data.get(
            self.finance_type.get('key')
        )
        if finance_type_dict:
            finance_type_element = etree.SubElement(
                transaction_element, self.finance_type.get('element')
            )

            # Attributes
            # Code
            code = finance_type_dict.get(
                self.finance_type.get('code').get('key')
            )
            if code:
                finance_type_element.set(
                    self.flow_type.get('code').get('attr'),
                    code
                )

        # Aid type
        aid_type_dict = self.data.get(
            self.aid_type.get('key')
        )
        if aid_type_dict:
            aid_type_element = etree.SubElement(
                transaction_element, self.aid_type.get('element')
            )

            # Attributes
            # Code
            code = aid_type_dict.get(
                self.aid_type.get('code').get('key')
            )
            if code:
                aid_type_element.set(
                    self.aid_type.get('code').get('attr'),
                    code
                )

        # Tied status
        tied_status_dict = self.data.get(
            self.tied_status.get('key')
        )
        if tied_status_dict:
            tied_status_element = etree.SubElement(
                transaction_element, self.tied_status.get('element')
            )

            # Attributes
            # Code
            code = tied_status_dict.get(
                self.tied_status.get('code').get('key')
            )
            if code:
                tied_status_element.set(
                    self.tied_status.get('code').get('attr'),
                    code
                )

        # Provider Organisation
        provider_organisation_dict = self.data.get(
            self.provider_organisation.get('key')
        )
        if provider_organisation_dict:
            provider_organisation_element = etree.SubElement(
                transaction_element, self.provider_organisation.get('element')
            )

            # Attributes
            # Ref
            ref_value = provider_organisation_dict.get(
                self.provider_organisation.get('ref').get('key')
            )
            if ref_value:
                provider_organisation_element.set(
                    self.provider_organisation.get('ref').get('attr'),
                    ref_value
                )

            # Attributes
            # Provider activity id
            provider_activity_id_value = provider_organisation_dict.get(
                self.provider_organisation.get(
                    'provider_activity_id'
                ).get('key')
            )
            if provider_activity_id_value:
                provider_organisation_element.set(
                    self.provider_organisation.get(
                        'provider_activity_id'
                    ).get('attr'),
                    provider_activity_id_value
                )

            # Attributes
            # Type
            type_value = provider_organisation_dict.get(
                self.provider_organisation.get('type').get('key')
            )
            if type_value:
                provider_organisation_element.set(
                    self.provider_organisation.get('type').get('attr'),
                    type_value
                )

            # Narrative
            provider_organisation_narrative = ElementWithNarrativeReference(
                parent_element=None,
                data=provider_organisation_dict
            )
            provider_organisation_narrative.create_narrative(
                parent_element=provider_organisation_element
            )

        # Recipient country
        recipient_countries_list = self.data.get(
            self.recipient_countries.get('key')
        )
        if recipient_countries_list:
            for recipient_country in recipient_countries_list:
                recipient_country_element = etree.SubElement(
                    transaction_element,
                    self.recipient_countries.get('element')
                )

                # Attribute
                # Code
                country = recipient_country.get(
                    self.recipient_countries.get('country').get('key')
                )
                if country:
                    code = country.get(
                        self.recipient_countries.get(
                            'country'
                        ).get('code').get('key')
                    )

                    if code:
                        recipient_country_element.set(
                            self.recipient_countries.get(
                                'country'
                            ).get('code').get('attr'),
                            code
                        )

                # Attribute
                # Percentage
                percentage_value = recipient_country.get(
                    self.recipient_countries.get('percentage').get('key')
                )
                if percentage_value:
                    recipient_country_element.set(
                        self.recipient_countries.get('percentage').get('attr'),
                        percentage_value
                    )

        # Recipient region
        recipient_regions_list = self.data.get(
            self.recipient_regions.get('key')
        )
        if recipient_regions_list:
            for recipient_region in recipient_regions_list:
                recipient_region_element = etree.SubElement(
                    transaction_element,
                    self.recipient_regions.get('element')
                )

                # Attribute
                # Code
                region = recipient_region.get(
                    self.recipient_regions.get('region').get('key')
                )
                if region:
                    code = region.get(
                        self.recipient_regions.get(
                            'region'
                        ).get('code').get('key')
                    )

                    if code:
                        recipient_region_element.set(
                            self.recipient_regions.get(
                                'region'
                            ).get('code').get('attr'),
                            code
                        )

                # Attribute
                # Vocabulary
                vocabulary_dict = recipient_region.get(
                    self.recipient_regions.get('vocabulary').get('key')
                )
                if vocabulary_dict:
                    vocabulary_value = vocabulary_dict.get(
                        self.recipient_regions.get(
                            'vocabulary'
                        ).get('code').get('key')
                    )
                    recipient_region_element.set(
                        self.recipient_regions.get(
                            'vocabulary'
                        ).get('code').get('attr'),
                        vocabulary_value
                    )

        # Sector
        sectors_list = self.data.get(
            self.sectors.get('key')
        )
        if sectors_list:
            for sector_dict in sectors_list:
                sector_element = etree.SubElement(
                    transaction_element,
                    self.sectors.get('element')
                )

                # Attribute
                # Code
                sector = sector_dict.get(
                    self.sectors.get('sector').get('key')
                )
                if sector:
                    code = sector.get(
                        self.sectors.get(
                            'sector'
                        ).get('code').get('key')
                    )

                    if code:
                        sector_element.set(
                            self.sectors.get(
                                'sector'
                            ).get('code').get('attr'),
                            code
                        )

                # Attribute
                # Vocabulary
                vocabulary = sector_dict.get(
                    self.sectors.get('vocabulary').get('key')
                )
                if vocabulary:
                    code = vocabulary.get(
                        self.sectors.get(
                            'vocabulary'
                        ).get('code').get('key')
                    )

                    if code:
                        sector_element.set(
                            self.sectors.get(
                                'vocabulary'
                            ).get('code').get('attr'),
                            code
                        )


class SectorReference(ElementWithNarrativeReference):
    """
    http://reference.iatistandard.org/202/activity-standard/iati-activities/iati-activity/transaction/sector/
    """
    element = 'sector'
    # @code
    code = {
        'sector': {
            'key': 'sector',
            'code': {
                'key': 'code',
                'attr': 'code'
            },
        }
    }
    # @vocabulary
    vocabulary = {
        'vocabulary': {
            'key': 'vocabulary',
            'code': {
                'key': 'code',
                'attr': 'vocabulary'
            },
        }
    }
    # @vocabulary-uri
    vocabulary_uri = {
        'key': 'vocabulary_uri',
        'attr': 'vocabulary-uri'
    }
    # @percentage
    percentage = {
        'key': 'percentage',
        'attr': 'percentage'
    }

    def create(self):
        sector_element = etree.SubElement(
            self.parent_element, self.element
        )

        # @code
        sector_dict = self.data.get(self.code.get('sector').get('key'))
        if sector_dict:
            code_value = sector_dict.get(
                self.code.get('sector').get('code').get('key')
            )

            if code_value:
                sector_element.set(
                    self.code.get('sector').get('code').get('attr'),
                    code_value
                )

        # @vocabulary
        vocabulary_dict = self.data.get(
            self.vocabulary.get('vocabulary').get('key')
        )
        if vocabulary_dict:
            code_value = vocabulary_dict.get(
                self.vocabulary.get('vocabulary').get('code').get('key')
            )

            if code_value:
                sector_element.set(
                    self.vocabulary.get('vocabulary').get('code').get('attr'),
                    code_value
                )

        # @vocabulary-uri
        vocabulary_uri_value = self.data.get(
            self.vocabulary_uri.get('key')
        )
        if vocabulary_uri_value:
            sector_element.set(
                self.vocabulary_uri.get('attr'),
                vocabulary_uri_value
            )

        # @percentage
        percentage_value = self.data.get(
            self.percentage.get('key')
        )
        if percentage_value:
            sector_element.set(
                self.percentage.get('attr'),
                percentage_value
            )

        # Narrative
        self.create_narrative(sector_element)


class BudgetReference(ElementReference):
    """
    http://reference.iatistandard.org/203/activity-standard/iati-activities/iati-activity/budget/
    """
    # <budget
    element = 'budget'
    # @type
    _type = {
        'type': {
            'key': 'type',
            'code': {
                'key': 'code',
                'attr': 'type'
            }
        }
    }
    # @status
    status = {
        'status': {
            'key': 'status',
            'code': {
                'key': 'code',
                'attr': 'status'
            }
        }
    }
    # >
    # <period-start
    period_start = {
        'element': 'period-start',
        'key': 'period_start',
        # @iso-date
        'attr': 'iso-date'
    }
    # />
    # <period-end
    period_end = {
        'element': 'period-end',
        'key': 'period_end',
        # @iso-date
        'attr': 'iso-date'
    }
    # />
    # <value
    value = {
        'element': 'value',
        'key': 'value',
        # @currency
        'currency': {
            'key': 'currency',
            'code': {
                'key': 'code',
                'attr': 'currency'
            }
        },
        # @value-date
        'date': {
            'key': 'date',
            'attr': 'value-date'
        },
        # >
        # Content
        'value': {
            'key': 'value'
        }
    }
    # </value>
    # </budget>

    def create(self):
        budget_element = etree.SubElement(
            self.parent_element, self.element
        )

        # @type
        type_dict = self.data.get(self._type.get('type').get('key'))
        if type_dict:
            code_value = type_dict.get(
                self._type.get('type').get('code').get('key')
            )

            if code_value:
                budget_element.set(
                    self._type.get('type').get('code').get('attr'),
                    code_value
                )

        # @status
        status_dict = self.data.get(self.status.get('status').get('key'))
        if status_dict:
            code_value = status_dict.get(
                self.status.get('status').get('code').get('key')
            )

            if code_value:
                budget_element.set(
                    self.status.get('status').get('code').get('attr'),
                    code_value
                )

        # <period-start
        period_start_value = self.data.get(self.period_start.get('key'))
        if period_start_value:
            period_start_element = etree.SubElement(
                budget_element, self.period_start.get('element')
            )
            # @iso-date
            period_start_element.set(
                self.period_start.get('attr'),
                period_start_value
            )
        # />

        # <period-end
        period_end_value = self.data.get(self.period_end.get('key'))
        if period_end_value:
            period_end_element = etree.SubElement(
                budget_element, self.period_end.get('element')
            )
            # @iso-date
            period_end_element.set(
                self.period_end.get('attr'),
                period_end_value
            )
        # />

        # <value
        value_dict = self.data.get(self.value.get('key'))
        if value_dict:
            value_element = etree.SubElement(
                budget_element, self.value.get('element')
            )

            # @currency
            currency_dict = value_dict.get(
                self.value.get('currency').get('key')
            )
            if currency_dict:
                code_value = currency_dict.get(
                    self.value.get('currency').get('code').get('key')
                )

                if code_value:
                    value_element.set(
                        self.value.get('currency').get('code').get('attr'),
                        code_value
                    )

            # @value-date
            value_date = value_dict.get(
                self.value.get('date').get('key')
            )
            if value_date:
                value_element.set(
                    self.value.get('date').get('attr'),
                    value_date
                )
            # >

            # Content
            value = value_dict.get(self.value.get('value').get('key'))
            if value:
                # Value type is {Decimal}, then convert it to string
                value_element.text = str(value)


class OtherIdentifierReference(ElementReference):
    """
    http://reference.iatistandard.org/202/activity-standard/iati-activities/iati-activity/other-identifier/
    """
    # <other-identifier
    element = 'other-identifier'
    # @ref
    ref = {
        'key': 'ref',
        'attr': 'ref'
    }
    # @type
    _type = {
        'key': 'type',
        'code': {
            'key': 'code',
            'attr': 'type'
        }
    }
    # >
    # <owner-org
    owner_org = {
        'element': 'owner-org',
        'key': 'owner_org',
        # @type
        'ref': {
            'key': 'ref',
            'attr': 'ref'
        }
        # />
        # <narrative>
        # </narrative>
    }
    # </owner-org>
    # </other-identifier>

    def create(self):
        other_identifier_element = etree.SubElement(
            self.parent_element, self.element
        )

        # @ref
        ref_value = self.data.get(self.ref.get('key'))
        if ref_value:
            other_identifier_element.set(self.ref.get('attr'), ref_value)

        # @type
        type_dict = self.data.get(self._type.get('key'))
        if type_dict:
            code_value = type_dict.get(
                self._type.get('code').get('key')
            )

            if code_value:
                other_identifier_element.set(
                    self._type.get('code').get('attr'),
                    code_value
                )

        # <owner-org
        owner_org_dict = self.data.get(self.owner_org.get('key'))
        if owner_org_dict:
            owner_org_element = etree.SubElement(
                other_identifier_element,
                self.owner_org.get('element')
            )

            # @ref
            ref_value = owner_org_dict.get(
                self.owner_org.get('ref').get('key')
            )
            if ref_value:
                owner_org_element.set(
                    self.owner_org.get('ref').get('attr'),
                    ref_value
                )

            # <narrative>
            narrative_element = ElementWithNarrativeReference(
                None, owner_org_dict
            )
            narrative_element.create_narrative(owner_org_element)
            # </narrative>


class ActivityStatusReference(ElementReference):
    """
    http://reference.iatistandard.org/203/activity-standard/iati-activities/iati-activity/activity-status/
    """
    # <activity-status
    element = 'activity-status'
    # @code
    code = {
        'key': 'code',
        'attr': 'code'
    }
    # />

    def create(self):
        # <activity-status
        activity_status_element = etree.SubElement(
            self.parent_element, self.element
        )

        # @code
        code_value = self.data.get(self.code.get('key'))
        if code_value:
            activity_status_element.set(
                self.code.get('attr'),
                code_value
            )

        # />


class RecipientCountryReference(ElementReference):
    """
    http://reference.iatistandard.org/203/activity-standard/iati-activities/iati-activity/recipient-country/
    """
    # <recipient-country
    element = 'recipient-country'
    # @code
    country = {
        'key': 'country',
        'code': {
            'key': 'code',
            'attr': 'code'
        }
    }
    # @percentage
    percentage = {
        'key': 'percentage',
        'attr': 'percentage'
    }

    def create(self):
        # <recipient-country
        recipient_country_element = etree.SubElement(
            self.parent_element, self.element
        )

        # @code
        country_dict = self.data.get(self.country.get('key'))
        if country_dict:
            code_value = country_dict.get(self.country.get('code').get('key'))
            if code_value:
                recipient_country_element.set(
                    self.country.get('code').get('attr'),
                    code_value
                )

        # @percentage
        percentage_value = self.data.get(self.percentage.get('key'))
        if percentage_value:
            recipient_country_element.set(
                self.percentage.get('attr'),
                # Percentage value type is {Decimal}, then convert it to string
                str(percentage_value)
            )


class RecipientRegionReference(ElementReference):
    """
    http://reference.iatistandard.org/203/activity-standard/iati-activities/iati-activity/recipient-region/
    """
    # <recipient-region
    element = 'recipient-region'
    # @code
    region = {
        'key': 'region',
        'code': {
            'key': 'code',
            'attr': 'code'
        }
    }
    # @percentage
    percentage = {
        'key': 'percentage',
        'attr': 'percentage'
    }
    # @vocabulary
    vocabulary = {
        'key': 'vocabulary',
        'code': {
            'key': 'code',
            'attr': 'vocabulary'
        }
    }
    # @vocabulary-uri
    vocabulary_uri = {
        'key': 'vocabulary_uri',
        'attr': 'vocabulary-uri'
    }
    # />

    def create(self):
        # <recipient-country
        recipient_region_element = etree.SubElement(
            self.parent_element, self.element
        )

        # @code
        region_dict = self.data.get(self.region.get('key'))
        if region_dict:
            code_value = region_dict.get(self.region.get('code').get('key'))
            if code_value:
                recipient_region_element.set(
                    self.region.get('code').get('attr'),
                    code_value
                )

        # @percentage
        percentage_value = self.data.get(self.percentage.get('key'))
        if percentage_value:
            recipient_region_element.set(
                self.percentage.get('attr'),
                # Percentage value type is {Decimal}, then convert it to string
                str(percentage_value)
            )

        # @vocabulary
        vocabulary_dict = self.data.get(self.vocabulary.get('key'))
        if vocabulary_dict:
            code_value = vocabulary_dict.get(
                self.vocabulary.get('code').get('key')
            )
            if code_value:
                recipient_region_element.set(
                    self.vocabulary.get('code').get('attr'),
                    code_value
                )

        # @vocabulary-uri
        vocabulary_uri_value = self.data.get(self.vocabulary_uri.get('key'))
        if vocabulary_uri_value:
            recipient_region_element.set(
                self.vocabulary_uri.get('attr'),
                vocabulary_uri_value
            )
        # />


class LocationReference(ElementReference):
    """
    http://reference.iatistandard.org/203/activity-standard/iati-activities/iati-activity/location/
    """
    # <location
    element = 'location'
    # @ref
    ref = {
        'key': 'ref',
        'attr': 'ref'
    }
    # >
    # <location-reach
    location_reach = {
        'element': 'location-reach',
        'key': 'location_reach',
        # @code
        'code': {
            'key': 'code',
            'attr': 'code'
        }
    }
    # />
    # <location-id
    location_id = {
        'element': 'location-id',
        'key': 'location_id',
        # @vocabulary
        'vocabulary': {
            'key': 'vocabulary',
            'code': {
                'key': 'code',
                'attr': 'vocabulary'
            }
        },
        # @code
        'code': {
            'key': 'code',
            'attr': 'code'
        }
    }
    # />
    # <name>
    name = {
        'element': 'name',
        'key': 'name'
    }
    # <narrative>
    # Location name
    # </narrative>
    # </name>
    # <description>
    description = {
        'element': 'description',
        'key': 'description'
    }
    # <narrative>
    # Location description
    # </narrative>
    # </description>
    # </location>

    def create(self):
        # <location
        location_element = etree.SubElement(
            self.parent_element, self.element
        )

        # @ref
        ref_value = self.data.get(self.ref.get('key'))
        if ref_value:
            location_element.set(self.ref.get('attr'), ref_value)
        # >

        # <location-reach
        location_reach_dict = self.data.get(self.location_reach.get('key'))
        if location_reach_dict:
            location_reach_element = etree.SubElement(
                location_element, self.location_reach.get('element')
            )
            # @code
            code_value = location_reach_dict.get(
                self.location_reach.get('code').get('key')
            )
            if code_value:
                location_reach_element.set(
                    self.location_reach.get('code').get('attr'),
                    code_value
                )
        # />

        # <location-id
        location_id_dict = self.data.get(self.location_id.get('key'))
        if location_id_dict:
            location_id_element = etree.SubElement(
                location_element, self.location_id.get('element')
            )

            # @vocabulary
            vocabulary_dict = location_id_dict.get(
                self.location_id.get('vocabulary').get('key')
            )
            if vocabulary_dict:
                code_value = vocabulary_dict.get(
                    self.location_id.get('vocabulary').get('code').get('key')
                )
                if code_value:
                    location_id_element.set(
                        self.location_id.get(
                            'vocabulary'
                        ).get('code').get('attr'),
                        code_value
                    )

            # @code
            code_value = location_id_dict.get(
                self.location_id.get('code').get('key')
            )
            if code_value:
                location_id_element.set(
                    self.location_id.get('code').get('attr'),
                    code_value
                )
        # / >

        # <name>
        name_dict = self.data.get(self.name.get('key'))
        if name_dict:
            # <narrative>
            ElementWithNarrativeReference(
                location_element, name_dict, self.name.get('element')
            ).create()
            # </narrative>
        # </name>

        # <description>
        description_dict = self.data.get(self.description.get('key'))
        if description_dict:
            # <narrative>
            ElementWithNarrativeReference(
                location_element,
                description_dict,
                self.description.get('element')
            ).create()
            # </narrative>
        # </description>

        # </location>
