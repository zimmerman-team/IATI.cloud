"""
This module reletated to IATI Standard version 2.03
http://reference.iatistandard.org/203/activity-standard/iati-activities/iati-activity/
"""
from lxml import etree

from api.iati.attributes import DataAttribute
from api.iati.elements import (
    AttributeRecord, ElementBase, ElementRecord, ElementReference,
    ElementWithNarrativeReference
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
    # @type
    _type = {
        'key': 'type',
        'code': {
            'key': 'code',
            'attr': 'type'
        }
    }

    def create(self):
        description_element = etree.SubElement(
            self.parent_element, self.element
        )

        # Set attribute type
        type_dict = self.data.get(self._type.get('key'))
        if type_dict:
            type_value = type_dict.get(self._type.get('code').get('key'))
            description_element.set(
                self._type.get('code').get('attr'),
                type_value
            )

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

        # Department element
        department_dict = self.data.get(self.department_dict_key)
        if department_dict:
            department_narrative = ElementWithNarrativeReference(
                parent_element=contact_info_element,
                data=department_dict
            )
            department_narrative.element = self.department_element
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

        # Telephone element
        telephone_value = self.data.get(self.telephone_key)
        if telephone_value:
            telephone_element = etree.SubElement(
                contact_info_element, self.telephone_element
            )
            telephone_element.text = telephone_value

        # Email element
        email_value = self.data.get(self.email_key)
        if email_value:
            email_element = etree.SubElement(
                contact_info_element, self.email_element
            )
            email_element.text = email_value

        # Website element
        website_value = self.data.get(self.website_key)
        if website_value:
            website_element = etree.SubElement(
                contact_info_element, self.website_element
            )
            website_element.text = website_value

        # Mailing address element
        mailing_address_dict = self.data.get(self.mailing_address_dict_key)
        if mailing_address_dict:
            mailing_address_narrative = ElementWithNarrativeReference(
                parent_element=contact_info_element,
                data=mailing_address_dict
            )
            mailing_address_narrative.element = self.mailing_address_element
            mailing_address_narrative.create()


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
    humanitarian = {
        'key': 'humanitarian',
        'attr': 'humanitarian'
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
    # Descripion
    description = {
        'element': 'description',
        'key': 'description'
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
    aid_types = {
        'key': 'transaction_aid_types',
        'element': 'aid-type',
        'aid_type': {
            'key': 'aid_type',
            'code': {
                'key': 'code',
                'attr': 'code'
            },
            'vocabulary': {
                'key': 'vocabulary',
                'code': {
                    'key': 'code',
                    'attr': 'vocabulary'
                },
            }
        },
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
            'code': {
                'key': 'code',
                'attr': 'type'
            }
        },
        'narratives': {
            'element': 'narrative',
            'key': 'narratives',
        }
    }
    # Receiver Organisation
    receiver_organisation = {
        'element': 'receiver-org',
        'key': 'receiver_organisation',
        # Attributes
        'ref': {
            'key': 'ref',
            'attr': 'ref'
        },
        'receiver_activity_id': {
            'key': 'receiver_activity_id',
            'attr': 'receiver-activity-id'
        },
        'type': {
            'key': 'type',
            'code': {
                'key': 'code',
                'attr': 'type'
            }
        },
        'narratives': {
            'element': 'narrative',
            'key': 'narratives',
        }

    }
    disbursement_channel = {
        'element': 'disbursement-channel',
        'key': 'disbursement_channel',
        # Attributes,
        'code': {
            'key': 'code',
            'attr': 'code'
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

        # Humanitarian
        humanitarian_value = self.data.get(
            self.humanitarian.get('key')
        )
        if humanitarian_value in [True, False, 1, 0]:
            transaction_element.set(
                self.humanitarian.get('attr'),
                '1' if humanitarian_value else '0'
            )

        # Transaction type
        transaction_type_dict = self.data.get(
            self.transaction_type.get('key')
        )
        if transaction_type_dict:
            transaction_type_element = etree.SubElement(
                transaction_element, self.transaction_type.get('element')
            )

            # Transaction type element: code attribute
            code_value = transaction_type_dict.get(
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

        # Description element
        description_dict = self.data.get(self.description.get('key'))
        if description_dict:
            description_narrative = ElementWithNarrativeReference(
                parent_element=transaction_element,
                data=description_dict
            )
            description_narrative.element = self.description.get(
                'element'
            )
            description_narrative.create()

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
            type_dict = provider_organisation_dict.get(
                self.provider_organisation.get('type').get('key')
            )
            if type_dict:
                type_value = type_dict.get(
                    self.provider_organisation.get(
                        'type'
                    ).get('code').get('key')
                )
                provider_organisation_element.set(
                    self.provider_organisation.get(
                        'type'
                    ).get('code').get('attr'),
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

        # Receiver Organisation
        receiver_organisation_dict = self.data.get(
            self.receiver_organisation.get('key')
        )
        if receiver_organisation_dict:
            receiver_organisation_element = etree.SubElement(
                transaction_element,
                self.receiver_organisation.get('element')
            )

            # Attributes
            # Ref
            ref_value = receiver_organisation_dict.get(
                self.receiver_organisation.get('ref').get('key')
            )
            if ref_value:
                receiver_organisation_element.set(
                    self.receiver_organisation.get('ref').get('attr'),
                    ref_value
                )

            # Attributes
            # Receiver activity id
            receiver_activity_id_value = receiver_organisation_dict.get(
                self.receiver_organisation.get(
                    'receiver_activity_id'
                ).get('key')
            )
            if receiver_activity_id_value:
                receiver_organisation_element.set(
                    self.receiver_organisation.get(
                        'receiver_activity_id'
                    ).get('attr'),
                    receiver_activity_id_value
                )

            # Attributes
            # Type
            type_dict = receiver_organisation_dict.get(
                self.provider_organisation.get('type').get('key')
            )
            if type_dict:
                type_value = type_dict.get(
                    self.receiver_organisation.get(
                        'type'
                    ).get('code').get('key')
                )
                receiver_organisation_element.set(
                    self.receiver_organisation.get(
                        'type'
                    ).get('code').get('attr'),
                    type_value
                )

            # Narrative
            receiver_organisation_narrative = ElementWithNarrativeReference(
                parent_element=None,
                data=receiver_organisation_dict
            )
            receiver_organisation_narrative.create_narrative(
                parent_element=receiver_organisation_element
            )

        # Disbursement channel
        disbursement_channel_dict = self.data.get(
            self.disbursement_channel.get('key')
        )
        if disbursement_channel_dict:
            disbursement_channel_element = etree.SubElement(
                transaction_element, self.disbursement_channel.get('element')
            )

            # Attributes
            # Code
            code_value = disbursement_channel_dict.get(
                self.disbursement_channel.get('code').get('key')
            )
            if ref_value:
                disbursement_channel_element.set(
                    self.disbursement_channel.get('code').get('attr'),
                    code_value
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
        aid_type_list = self.data.get(
            self.aid_types.get('key')
        )
        if aid_type_list:
            for aid_type_dict in aid_type_list:
                aid_type_element = etree.SubElement(
                    transaction_element, self.aid_types.get('element')
                )

                aid_type = aid_type_dict.get(
                    self.aid_types.get('aid_type').get('key')
                )
                if aid_type:
                    # Attributes
                    # Code
                    code = aid_type.get(
                        self.aid_types.get('aid_type').get('code').get('key')
                    )
                    if code:
                        aid_type_element.set(
                            self.aid_types.get('aid_type').get(
                                'code'
                            ).get('attr'),
                            code
                        )

                    # Attributes
                    # Vocabulary
                    vocabulary = aid_type.get(
                        self.aid_types.get('aid_type').get(
                            'vocabulary'
                        ).get('key')
                    )
                    if vocabulary:
                        code = vocabulary.get(
                            self.aid_types.get('aid_type').get(
                                'vocabulary'
                            ).get('code').get('key')
                        )

                        if code:
                            aid_type_element.set(
                                self.aid_types.get('aid_type').get(
                                    'vocabulary'
                                ).get('code').get('attr'),
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
                str(percentage_value)
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
    # <activity-description>
    activity_description = {
        'element': 'activity-description',
        'key': 'activity_description'
    }
    # <narrative>
    # A description that qualifies the activity taking place at the location.
    # </narrative>
    # </activity-description>
    # <administrative
    administrative = {
        'element': 'administrative',
        'key': 'administrative',
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
        },
        # @level
        'level': {
            'key': 'level',
            'attr': 'level'
        },
    }
    # />
    # <point
    point = {
        'element': 'point',
        'key': 'point',
        # @srsName
        'srsName': {
            'key': 'srsName',
            'attr': 'srsName'
        },
        # <pos>
        'pos': {
            'element': 'pos',
            'key': 'pos',
            'latitude': {
                'key': 'latitude'
            },
            'longitude': {
                'key': 'longitude'
            }
        }
        # </pos
    }
    # >
    # </pos>
    # <exactness
    exactness = {
        'element': 'exactness',
        'key': 'exactness',
        # @code
        'code': {
            'key': 'code',
            'attr': 'code'
        }
    }
    # />
    # <location-class
    location_class = {
        'element': 'location-class',
        'key': 'location_class',
        # @code
        'code': {
            'key': 'code',
            'attr': 'code'
        }
    }
    # />
    # <feature-designation
    feature_designation = {
        'element': 'feature-designation',
        'key': 'feature_designation',
        # @code
        'code': {
            'key': 'code',
            'attr': 'code'
        }
    }

    # />
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

        # <activity-description>
        activity_description_dict = self.data.get(
            self.activity_description.get('key')
        )
        if activity_description_dict:
            # <narrative>
            ElementWithNarrativeReference(
                location_element,
                activity_description_dict,
                self.activity_description.get('element')
            ).create()
            # </narrative>
        # </activity-description>

        administrative_list = self.data.get(self.administrative.get('key'))
        if administrative_list:
            for administrative_dict in administrative_list:
                # <administrative
                administrative_element = etree.SubElement(
                    location_element, self.administrative.get('element')
                )

                # @vocabulary
                vocabulary_dict = administrative_dict.get(
                    self.administrative.get('vocabulary').get('key')
                )
                if vocabulary_dict:
                    code_value = vocabulary_dict.get(
                        self.administrative.get(
                            'vocabulary'
                        ).get('code').get('key')
                    )
                    if code_value:
                        administrative_element.set(
                            self.administrative.get(
                                'vocabulary'
                            ).get('code').get('attr'),
                            code_value
                        )

                # @level
                level_value = administrative_dict.get(
                    self.administrative.get('level').get('key')
                )
                if level_value:
                    administrative_element.set(
                        self.administrative.get('level').get('attr'),
                        str(level_value)
                    )

                # @code
                code_value = administrative_dict.get(
                    self.administrative.get('code').get('key')
                )
                if code_value:
                    administrative_element.set(
                        self.location_id.get('code').get('attr'),
                        code_value
                    )
                # />

        # <point
        point_dict = self.data.get(self.point.get('key'))
        if point_dict:
            point_element = etree.SubElement(
                location_element, self.point.get('element')
            )

            # @srsName
            srs_name_value = point_dict.get(
                self.point.get('srsName').get('key')
            )
            if srs_name_value:
                point_element.set(
                    self.point.get('srsName').get('attr'),
                    srs_name_value
                )
            # >

            # <pos>
            pos_dict = point_dict.get(self.point.get('pos').get('key'))
            if pos_dict:
                pos_element = etree.SubElement(
                    point_element, self.point.get('pos').get('element')
                )

                latitude_value = pos_dict.get(
                    self.point.get('pos').get('latitude').get('key')
                )

                longitude_value = pos_dict.get(
                    self.point.get('pos').get('longitude').get('key')
                )

                if latitude_value and longitude_value:
                    pos_element.text = '{latitude} {longitude}'.format(
                        latitude=latitude_value,
                        longitude=longitude_value
                    )
            # </pos>
        # </point>

        # <exactness
        exactness_dict = self.data.get(self.exactness.get('key'))
        if exactness_dict:
            exactness_element = etree.SubElement(
                location_element, self.exactness.get('element')
            )

            # @code
            code_value = location_reach_dict.get(
                self.exactness.get('code').get('key')
            )
            if code_value:
                exactness_element.set(
                    self.exactness.get('code').get('attr'),
                    code_value
                )
        # />

        # <location-class
        location_class_dict = self.data.get(self.location_class.get('key'))
        if location_class_dict:
            location_class_element = etree.SubElement(
                location_element, self.location_class.get('element')
            )

            # @code
            code_value = location_class_dict.get(
                self.location_class.get('code').get('key')
            )
            if code_value:
                location_class_element.set(
                    self.location_class.get('code').get('attr'),
                    code_value
                )
        # />

        # <feature-designation
        feature_designation_dict = self.data.get(
            self.feature_designation.get('key')
        )
        if feature_designation_dict:
            feature_designation_element = etree.SubElement(
                location_element, self.feature_designation.get('element')
            )

            # @code
            code_value = feature_designation_dict.get(
                self.feature_designation.get('code').get('key')
            )
            if code_value:
                feature_designation_element.set(
                    self.feature_designation.get('code').get('attr'),
                    code_value
                )
        # />

        # </location>


class PolicyMarkerReference(ElementReference):
    """
    http://reference.iatistandard.org/203/activity-standard/iati-activities/iati-activity/policy-marker/
    """
    # <policy-marker
    element = 'policy-marker'
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
    # @code
    code = {
        'key': 'policy_marker',
        'code': {
            'key': 'code',
            'attr': 'code'
        }
    }
    # @significance
    significance = {
        'key': 'significance',
        'code': {
            'key': 'code',
            'attr': 'significance'
        }
    }
    # >
    # <narrative>
    # A policy marker description
    # </narrative>
    # </policy-marker>

    def create(self):
        # <policy-marker
        policy_marker_element = etree.SubElement(
            self.parent_element, self.element
        )

        # @vocabulary
        vocabulary_dict = self.data.get(self.vocabulary.get('key'))
        if vocabulary_dict:
            code_value = vocabulary_dict.get(
                self.vocabulary.get('code').get('key')
            )

            if code_value:
                policy_marker_element.set(
                    self.vocabulary.get('code').get('attr'),
                    code_value
                )

        # @vocabulary-uri
        vocabulary_uri_value = self.data.get(self.vocabulary_uri.get('key'))
        if vocabulary_uri_value:
            policy_marker_element.set(
                self.vocabulary_uri.get('attr'),
                vocabulary_uri_value
            )

        # @code
        code_dict = self.data.get(self.code.get('key'))
        if code_dict:
            code_value = code_dict.get(
                self.code.get('code').get('key')
            )

            if code_value:
                policy_marker_element.set(
                    self.code.get('code').get('attr'),
                    code_value
                )

        # @significance
        significance_dict = self.data.get(self.significance.get('key'))
        if significance_dict:
            code_value = significance_dict.get(
                self.significance.get('code').get('key')
            )

            if code_value:
                policy_marker_element.set(
                    self.significance.get('code').get('attr'),
                    code_value
                )
        # >

        # <narrative>
        ElementWithNarrativeReference(
            None,
            self.data
        ).create_narrative(policy_marker_element)
        # </narrative>
        # </policy-marker>


class AttributeReference(ElementReference):
    # <element
    element = 'element'
    # @attr
    attr = {
        'key': 'attr',
        'attr': 'attr'
    }
    # />

    def create(self):
        if self.data:
            # <element
            attr_element = etree.SubElement(
                self.parent_element, self.element
            )

            # @code
            DataAttribute(
                attr_element,
                self.attr.get('attr'),
                self.data,
                self.attr.get('key')
            ).set()
            # />


class CodeReference(AttributeReference):
    # <element
    element = 'element'
    # @code
    attr = {
        'key': 'code',
        'attr': 'code'
    }
    # />


class CollaborationTypeReference(CodeReference):
    """
    http://reference.iatistandard.org/203/activity-standard/iati-activities/iati-activity/collaboration-type/
    """
    # <collaboration-type
    element = 'collaboration-type'
    # />


class DefaultFlowTypeReference(CodeReference):
    """
    http://reference.iatistandard.org/203/activity-standard/iati-activities/iati-activity/default-flow-type/
    """
    # <collaboration-type
    element = 'default-flow-type'
    # />


class DefaultFinanceTypeReference(CodeReference):
    """
    http://reference.iatistandard.org/203/activity-standard/iati-activities/iati-activity/default-finance-type/
    """
    # <collaboration-type
    element = 'default-finance-type'
    # />


class DefaultTiedStatusReference(CodeReference):
    """
    http://reference.iatistandard.org/203/activity-standard/iati-activities/iati-activity/default-tied-status/
    """
    # <collaboration-type
    element = 'default-tied-status'
    # />


class PlannedDisbursementReference(ElementReference):
    """
    http://reference.iatistandard.org/203/activity-standard/iati-activities/iati-activity/planned-disbursement/
    """
    # <planned-disbursement
    element = 'planned-disbursement'
    # @type
    _type = {
        'key': 'type',
        'code': {
            'key': 'code',
            'attr': 'type'
        }
    }
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
        # <planned-disbursement
        planned_disbursement_element = etree.SubElement(
            self.parent_element, self.element
        )

        # @type
        DataAttribute(
            planned_disbursement_element,
            self._type.get('code').get('attr'),
            self.data,
            self._type.get('code').get('key'),
            self._type.get('key')
        ).set()

        # <period-start
        period_start_value = self.data.get(self.period_start.get('key'))
        if period_start_value:
            period_start_element = etree.SubElement(
                planned_disbursement_element, self.period_start.get('element')
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
                planned_disbursement_element, self.period_end.get('element')
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
                planned_disbursement_element, self.value.get('element')
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
        # </planned-disbursement>


class CapitalSpendReference(ElementReference):
    """
    http://reference.iatistandard.org/203/activity-standard/iati-activities/iati-activity/capital-spend/
    """
    # <capital-spend
    element = 'capital-spend'
    # @percentage
    percentage = {
        'attr': 'percentage'
    }
    # />

    def create(self):
        if self.data:
            # <capital-spend
            capital_spend_element = etree.SubElement(
                self.parent_element, self.element
            )

            # @percentage
            capital_spend_element.set(
                self.percentage.get('attr'),
                str(self.data)
            )
            # />


class DocumentLinkReference(ElementReference):
    """
    http://reference.iatistandard.org/203/activity-standard/iati-activities/iati-activity/document-link/
    """
    # <document-link
    element = 'document-link'
    # @url
    url = {
        'key': 'url',
        'attr': 'url'
    }
    # @format
    format = {
        'key': 'format',
        'code': {
            'key': 'code',
            'attr': 'format'
        }
    }
    # <title>
    title = {
        'element': 'title',
        'key': 'title'
    }
    # <narrative>
    # Title narrative
    # </narrative>
    # </title>
    # <title>
    description = {
        'element': 'description',
        'key': 'description'
    }
    # <narrative>
    # Title narrative
    # </narrative>
    # </title>
    # <category>
    category = {
        # category data in list
        'list': 'categories',
        'element': 'category',
        'key': 'category',
        'code': {
            'key': 'code',
            'attr': 'code'
        }
    }
    # />
    # <language
    language = {
        # category data in list
        'list': 'languages',
        'element': 'language',
        'key': 'language',
        'code': {
            'key': 'code',
            'attr': 'code'
        }
    }
    # />
    # <document-date
    document_date = {
        'element': 'document-date',
        'key': 'document_date',
        # @iso-date
        'iso_date': {
            'key': 'iso_date',
            'attr': 'iso-date'
        }
    }
    # />

    def create(self):
        # <document-link
        document_link_element = etree.SubElement(
            self.parent_element, self.element
        )

        # @url
        DataAttribute(
            document_link_element,
            self.url.get('attr'),
            self.data,
            self.url.get('key')
        ).set()

        # @format
        format_dict = self.data.get(self.format.get('key'))
        if format_dict:
            DataAttribute(
                document_link_element,
                self.format.get('code').get('attr'),
                format_dict,
                self.format.get('code').get('key')
            ).set()

        # <title>
        # <narrative>
        ElementWithNarrativeReference(
            parent_element=document_link_element,
            data=self.data.get(self.title.get('key')),
            element=self.title.get('element')
        ).create()
        # </narrative>
        # </title>

        # <description>
        # <narrative>
        ElementWithNarrativeReference(
            parent_element=document_link_element,
            data=self.data.get(self.description.get('key')),
            element=self.description.get('element')
        ).create()
        # </narrative>
        # </description>

        categories = self.data.get(self.category.get('list'))
        for category in categories:
            category_dict = category.get(
                self.category.get('key')
            )
            if category_dict:
                # <category
                category_element = etree.SubElement(
                    document_link_element,
                    self.category.get('element')
                )
                # @code
                DataAttribute(
                    category_element,
                    self.category.get('code').get('attr'),
                    category_dict,
                    self.category.get('code').get('key')
                ).set()
                # />

        # <document-date
        document_date_dict = self.data.get(self.document_date.get('key'))
        if document_date_dict:
            document_date_element = etree.SubElement(
                document_link_element, self.document_date.get('element')
            )

            # @iso-date
            DataAttribute(
                document_date_element,
                self.document_date.get('iso_date').get('attr'),
                document_date_dict,
                self.document_date.get('iso_date').get('key')
            ).set()
        # />


class LegacyDataReference(ElementReference):
    """
    http://reference.iatistandard.org/203/activity-standard/iati-activities/iati-activity/legacy-data/
    """
    # <document-link
    element = 'legacy-data'
    legacy_data = {
        'list': 'legacy_data',
        'key': 'legacy_data',
        # @name
        'name': {
            'key': 'name',
            'attr': 'name'
        },
        # @value
        'value': {
            'key': 'value',
            'attr': 'value'
        },
        # @iati-equivalent
        'iati_equivalent': {
            'key': 'iati_equivalent',
            'attr': 'iati-equivalent'
        }
    }
    # />

    def create(self):
        # <document-link
        legacy_data_element = etree.SubElement(
            self.parent_element, self.element
        )

        # @name
        DataAttribute(
            legacy_data_element,
            self.legacy_data.get('name').get('attr'),
            self.data,
            self.legacy_data.get('name').get('key')
        ).set()

        # @value
        DataAttribute(
            legacy_data_element,
            self.legacy_data.get('value').get('attr'),
            self.data,
            self.legacy_data.get('value').get('key')
        ).set()

        # @iati-equivalent
        DataAttribute(
            legacy_data_element,
            self.legacy_data.get('iati_equivalent').get('attr'),
            self.data,
            self.legacy_data.get('iati_equivalent').get('key')
        ).set()

        # />


class CrsAddReference(ElementReference):
    """
    http://reference.iatistandard.org/203/activity-standard/iati-activities/iati-activity/crs-add/
    """
    # <crs-add>
    element = 'crs-add'
    # <other-flags
    other_flags = {
        'element': 'other-flags',
        'list': 'other_flags',
        # @code
        'code': {
            'dict': 'other_flags',
            'key': 'code',
            'attr': 'code'
        },
        # @significance
        'significance': {
            'key': 'significance',
            'attr': 'significance'
        }
    }
    # />
    # <loan-terms
    loan_terms = {
        'element': 'loan-terms',
        'key': 'loan_terms',
        # @rate-1
        'rate_1': {
            'key': 'rate_1',
            'attr': 'rate-1'
        },
        # @rate-2
        'rate_2': {
            'key': 'rate_2',
            'attr': 'rate-2'
        },
        # />
        # <repayment-type
        'repayment_type': {
            'element': 'repayment-type',
            'key': 'repayment_type',
            # @code
            'code': {
                'key': 'code',
                'attr': 'code'
            }
        },
        # />
        # <repayment-plan
        'repayment_plan': {
            'element': 'repayment-plan',
            'key': 'repayment_plan',
            # @code
            'code': {
                'key': 'code',
                'attr': 'code'
            }
        },
        # />
        # <commitment-date
        'commitment_date': {
            'element': 'commitment-date',
            'key': 'commitment_date',
            # @iso-date
            'attr': 'iso-date'
        },
        # />
        # <repayment-first-date
        'repayment_first_date': {
            'element': 'repayment-first-date',
            'key': 'repayment_first_date',
            # @iso-date
            'attr': 'iso-date'
        },
        # />
        # <repayment-final-date
        'repayment_final_date': {
            'element': 'repayment-final-date',
            'key': 'repayment_final_date',
            # @iso-date
            'attr': 'iso-date'
        }
        # />
    }
    # </loan-terms>
    # <loan-status
    loan_status = {
        'element': 'loan-status',
        'key': 'loan_status',
        # @year
        'year': {
            'key': 'year',
            'attr': 'year'
        },
        # @currency
        'currency': {
            'dict': 'currency',
            'key': 'code',
            'attr': 'currency'
        },
        # @value-date
        'value_date': {
            'key': 'value_date',
            'attr': 'value-date'
        },
        # <interest-received>
        'interest_received': {
            'element': 'interest-received',
            'key': 'interest_received'
        },
        # </interest-received>
        # <principal-outstanding>
        'principal_outstanding': {
            'element': 'principal-outstanding',
            'key': 'principal_outstanding'
        },
        # </principal-outstanding>
        # <principal-arrears>
        'principal_arrears': {
            'element': 'principal-arrears',
            'key': 'principal_arrears'
        },
        # </principal-arrears>
        # <interest-arrears>
        'interest_arrears': {
            'element': 'interest-arrears',
            'key': 'interest_arrears'
        }
        # </interest-arrears>
    }
    # </loan-status>
    # TODO: No Channel code
    # <channel-code>
    # </channel-code>
    # <crs-add/>

    def create(self):
        # <crs-add>
        crs_add_element = etree.SubElement(
            self.parent_element, self.element
        )

        other_flags_list = self.data.get(self.other_flags.get('list'))
        for other_flags_dict in other_flags_list:
            # <other-flags
            other_flags_element = etree.SubElement(
                crs_add_element, self.other_flags.get('element')
            )

            code_dict = other_flags_dict.get(
                self.other_flags.get('code').get('dict')
            )
            if code_dict:
                # @code
                DataAttribute(
                    other_flags_element,
                    self.other_flags.get('code').get('attr'),
                    code_dict,
                    self.other_flags.get('code').get('key')
                ).set()

            # @significance
            value = other_flags_dict.get(
                self.other_flags.get('significance').get('key')
            )
            other_flags_element.set(
                self.other_flags.get('significance').get('attr'),
                '1' if value == 'True' else '0'
            )
            # />

        loan_terms_dict = self.data.get(self.loan_terms.get('key'))
        if loan_terms_dict:
            # <loan-terms
            loan_terms_element = etree.SubElement(
                crs_add_element, self.loan_terms.get('element')
            )

            # @rate-1
            DataAttribute(
                loan_terms_element,
                self.loan_terms.get('rate_1').get('attr'),
                loan_terms_dict,
                self.loan_terms.get('rate_1').get('key')
            ).set()

            # @rate-2
            DataAttribute(
                loan_terms_element,
                self.loan_terms.get('rate_2').get('attr'),
                loan_terms_dict,
                self.loan_terms.get('rate_2').get('key')
            ).set()
            # >

            # <repayment-type
            CodeReference(
                loan_terms_element,
                loan_terms_dict.get(
                    self.loan_terms.get('repayment_type').get('key')
                ),
                self.loan_terms.get('repayment_type').get('element')
            ).create()
            # />

            # <repayment-plan
            CodeReference(
                loan_terms_element,
                loan_terms_dict.get(
                    self.loan_terms.get('repayment_plan').get('key')
                ),
                self.loan_terms.get('repayment_plan').get('element')
            ).create()
            # />

            # <commitment-date
            commitment_date_element = etree.SubElement(
                loan_terms_element,
                self.loan_terms.get('commitment_date').get('element')
            )
            commitment_date_element.set(
                self.loan_terms.get('commitment_date').get('attr'),
                loan_terms_dict.get(
                    self.loan_terms.get('commitment_date').get('key')
                )
            )
            # />

            # <repayment-first-date
            repayment_first_date_value = loan_terms_dict.get(
                self.loan_terms.get('repayment_first_date').get('key')
            )
            if repayment_first_date_value:
                repayment_first_date_element = etree.SubElement(
                    loan_terms_element,
                    self.loan_terms.get('repayment_first_date').get('element')
                )
                repayment_first_date_element.set(
                    self.loan_terms.get('repayment_first_date').get('attr'),
                    repayment_first_date_value
                )
            # />

            # <repayment-final-date
            repayment_final_date_value = loan_terms_dict.get(
                self.loan_terms.get('repayment_final_date').get('key')
            )
            if repayment_final_date_value:
                repayment_final_date_element = etree.SubElement(
                    loan_terms_element,
                    self.loan_terms.get('repayment_final_date').get('element')
                )
                repayment_final_date_element.set(
                    self.loan_terms.get('repayment_final_date').get('attr'),
                    repayment_final_date_value
                )
            # />
            # </loan-terms>

        loan_status_dict = self.data.get(self.loan_status.get('key'))
        if loan_status_dict:
            # <loan-status
            loan_status_element = etree.SubElement(
                crs_add_element, self.loan_status.get('element')
            )

            # @year
            year_value = loan_status_dict.get(
                self.loan_status.get('year').get('key')
            )
            if year_value:
                loan_status_element.set(
                    self.loan_status.get('year').get('attr'),
                    str(year_value)
                )

            # @currency
            currency_dict = loan_status_dict.get(
                self.loan_status.get('currency').get('dict')
            )
            if currency_dict:
                currency_value = currency_dict.get(
                    self.loan_status.get('currency').get('key')
                )
                if currency_value:
                    loan_status_element.set(
                        self.loan_status.get('currency').get('attr'),
                        str(currency_value)
                    )

            value_date_value = loan_status_dict.get(
                self.loan_status.get('value_date').get('key')
            )
            if value_date_value:
                loan_status_element.set(
                    self.loan_status.get('value_date').get('attr'),
                    str(value_date_value)
                )
            # >

            # <interest-received>
            interest_received_value = loan_status_dict.get(
                self.loan_status.get('interest_received').get('key')
            )
            if interest_received_value:
                interest_received_element = etree.SubElement(
                    loan_status_element,
                    self.loan_status.get('interest_received').get('element')
                )
                interest_received_element.text = interest_received_value
            # </interest-received>

            # <principal-outstanding>
            principal_outstanding_value = loan_status_dict.get(
                self.loan_status.get('principal_outstanding').get('key')
            )
            if principal_outstanding_value:
                principal_outstanding_element = etree.SubElement(
                    loan_status_element,
                    self.loan_status.get(
                        'principal_outstanding'
                    ).get('element')
                )
                principal_outstanding_element.text = \
                    principal_outstanding_value
            # </principal-outstanding>

            # <principal-arrears>
            principal_arrears_value = loan_status_dict.get(
                self.loan_status.get('principal_arrears').get('key')
            )
            if principal_arrears_value:
                principal_arrears_value_element = etree.SubElement(
                    loan_status_element,
                    self.loan_status.get(
                        'principal_arrears'
                    ).get('element')
                )
                principal_arrears_value_element.text = principal_arrears_value
            # </principal-arrears>

            # <interest-arrears>
            interest_arrears_value = loan_status_dict.get(
                self.loan_status.get('interest_arrears').get('key')
            )
            if interest_arrears_value:
                principal_arrears_value_element = etree.SubElement(
                    loan_status_element,
                    self.loan_status.get(
                        'interest_arrears'
                    ).get('element')
                )
                principal_arrears_value_element.text = interest_arrears_value
            # </interest-arrears>

        # </crs-add>


class BaseReference(ElementReference):
    """
    Base of reference
    """
    # <element>
    # </element>

    def create(self):
        # <element>
        element_base = ElementBase(
            element_record=self.element_record,
            parent_element=self.parent_element,
            data=self.data
        )
        element_base.create()
        # </element>


class DocumentLinkBaseReference(BaseReference):
    """
    The base of the document link element
    """
    # <document-link>
    attributes = [
        # @url
        AttributeRecord(
            name='url',
            key='url'
        ),
        # @format
        # Dict type
        AttributeRecord(
            name='format',
            key='code',
            dict_key='format'
        )
    ]
    children = [
        # <title>
        # <narrative>
        ElementRecord(
            name='title',
            key='title',
            element_type=ElementWithNarrativeReference
        ),
        # </narrative>
        # </title>
        # <description>
        # <narrative>
        ElementRecord(
            name='description',
            key='description',
            element_type=ElementWithNarrativeReference
        ),
        # </narrative>
        # </description>
        # <category
        ElementRecord(
            name='category',
            key='categories',
            attributes=[
                # @code
                # Dict type
                AttributeRecord(
                    name='code',
                    key='code',
                    dict_key='category'
                )
            ]
        ),
        # />
        # <language
        ElementRecord(
            name='language',
            key='languages',
            attributes=[
                # @code
                # Dict type
                AttributeRecord(
                    name='code',
                    key='code',
                    dict_key='language'
                )
            ]
        ),
        # />
        # <document-date
        ElementRecord(
            name='document-date',
            key='document_date',
            attributes=[
                # @iso-date
                AttributeRecord(
                    name='iso-date',
                    key='iso_date',
                )
            ]
        ),
        # />
    ]
    element_record = ElementRecord(
        name='document-link',
        key='document_links',
        attributes=attributes,
        children=children
    )
    # <document-link>


class ResultReference(BaseReference):
    """
    http://reference.iatistandard.org/203/activity-standard/iati-activities/iati-activity/result/
    """

    # <result>
    attributes = [
        # @type
        # Dict type
        AttributeRecord(
            name='type',
            key='code',
            dict_key='type'
        ),
        # @aggregation-status
        AttributeRecord(
            name='aggregation-status',
            key='aggregation_status'
        )
    ]
    children = [
        # <title>
        # <narrative>
        ElementRecord(
            name='title',
            key='title',
            element_type=ElementWithNarrativeReference
        ),
        # </narrative>
        # </title>
        # <description>
        # <narrative>
        ElementRecord(
            name='description',
            key='description',
            element_type=ElementWithNarrativeReference
        ),
        # </narrative>
        # </description>
        # <indicator>
        # <document-link>
        DocumentLinkBaseReference(
            parent_element=None,
            data=None,
            element=DocumentLinkBaseReference.element_record
        ),
        # <document-link>
        ElementRecord(
            name='indicator',
            key='indicators',
            attributes=[
                # @measure
                # Dict type
                AttributeRecord(
                    name='measure',
                    key='code',
                    dict_key='measure'
                ),
                # @ascending
                AttributeRecord(
                    name='ascending',
                    key='ascending'
                ),
                # @aggregation-status
                AttributeRecord(
                    name='aggregation-status',
                    key='aggregation_status'
                )
            ],
            children=[
                # <title>
                # <narrative>
                ElementRecord(
                    name='title',
                    key='title',
                    element_type=ElementWithNarrativeReference
                ),
                # </narrative>
                # </title>
                # <description>
                # <narrative>
                ElementRecord(
                    name='description',
                    key='description',
                    element_type=ElementWithNarrativeReference
                ),
                # </narrative>
                # </description>
                # <document-link>
                DocumentLinkBaseReference(
                    parent_element=None,
                    data=None,
                    element=DocumentLinkBaseReference.element_record
                ),
                # <document-link>
                # <reference>
                ElementRecord(
                    name='reference',
                    key='references',
                    attributes=[
                        # @vocabulary
                        # Dict type
                        AttributeRecord(
                            name='vocabulary',
                            key='code',
                            dict_key='vocabulary'
                        ),
                        # @code
                        AttributeRecord(
                            name='code',
                            key='code'
                        )
                    ],
                ),
                # </reference>
                # <baseline>
                ElementRecord(
                    name='baseline',
                    key='baseline',
                    attributes=[
                        # @year
                        AttributeRecord(
                            name='year',
                            key='year'
                        ),
                        # @value
                        AttributeRecord(
                            name='value',
                            key='value'
                        ),
                        # @iso-date
                        AttributeRecord(
                            name='iso-date',
                            key='iso_date'
                        )
                    ],
                    children=[
                        # <location>
                        ElementRecord(
                            name='location',
                            key='locations',
                            attributes=[
                                # @ref
                                AttributeRecord(
                                    name='ref',
                                    key='ref'
                                )
                            ]
                        ),
                        # />
                        # <dimension>
                        ElementRecord(
                            name='dimension',
                            key='dimensions',
                            attributes=[
                                # @name
                                AttributeRecord(
                                    name='name',
                                    key='name'
                                ),
                                # @value
                                AttributeRecord(
                                    name='value',
                                    key='value'
                                )
                            ],
                        ),
                        # </dimension>
                        # <document-link>
                        DocumentLinkBaseReference(
                            parent_element=None,
                            data=None,
                            element=DocumentLinkBaseReference.element_record
                        ),
                        # <document-link>
                        # <comment>
                        # <narrative>
                        ElementRecord(
                            name='comment',
                            key='comment',
                            element_type=ElementWithNarrativeReference
                        ),
                        # </narrative>
                        # </comment>
                    ]
                ),
                # </baseline>
                # <period>
                ElementRecord(
                    name='period',
                    key='periods',
                    children=[
                        # <period-start>
                        ElementRecord(
                            name='period-start',
                            attributes=[
                                # @iso-date
                                AttributeRecord(
                                    name='iso-date',
                                    key='period_start'
                                )
                            ],
                        ),
                        # </period-start>
                        # <period-end>
                        ElementRecord(
                            name='period-end',
                            attributes=[
                                # @iso-date
                                AttributeRecord(
                                    name='iso-date',
                                    key='period_end'
                                )
                            ],
                        ),
                        # </period-end>
                        # <target>
                        ElementRecord(
                            name='target',
                            key='targets',
                            attributes=[
                                # @value
                                AttributeRecord(
                                    name='value',
                                    key='value'
                                )
                            ],
                            children=[
                                # <location>
                                ElementRecord(
                                    name='location',
                                    key='locations',
                                    attributes=[
                                        # @ref
                                        AttributeRecord(
                                            name='ref',
                                            key='ref'
                                        )
                                    ],
                                ),
                                # </location>
                                # <dimension>
                                ElementRecord(
                                    name='dimension',
                                    key='dimensions',
                                    attributes=[
                                        # @name
                                        AttributeRecord(
                                            name='name',
                                            key='name'
                                        ),
                                        # @value
                                        AttributeRecord(
                                            name='value',
                                            key='value'
                                        )
                                    ],
                                ),
                                # </dimension>
                                # <comment>
                                # <narrative>
                                ElementRecord(
                                    name='comment',
                                    key='comment',
                                    element_type=ElementWithNarrativeReference
                                ),
                                # </narrative>
                                # </comment>
                                # <document-link>
                                DocumentLinkBaseReference(
                                    parent_element=None,
                                    data=None,
                                    element=DocumentLinkBaseReference.element_record  # NOQA: E501
                                ),
                                # <document-link>
                            ]
                        ),
                        # </target>
                        # <actual>
                        ElementRecord(
                            name='actual',
                            key='actuals',
                            attributes=[
                                # @value
                                AttributeRecord(
                                    name='value',
                                    key='value'
                                )
                            ],
                            children=[
                                # TODO: add <comment></comment>
                                ElementRecord(
                                    name='location',
                                    key='locations',
                                    attributes=[
                                        # @ref
                                        AttributeRecord(
                                            name='ref',
                                            key='ref'
                                        )
                                    ],
                                ),
                                # </location>
                                # <location>
                                ElementRecord(
                                    name='dimension',
                                    key='dimensions',
                                    attributes=[
                                        # @name
                                        AttributeRecord(
                                            name='name',
                                            key='name'
                                        ),
                                        # @value
                                        AttributeRecord(
                                            name='value',
                                            key='value'
                                        )
                                    ],
                                ),
                                # </location>
                                # <document-link>
                                DocumentLinkBaseReference(
                                    parent_element=None,
                                    data=None,
                                    element=DocumentLinkBaseReference.element_record  # NOQA: E501
                                ),
                                # <document-link>
                            ]
                        )
                        # </actual>
                    ]
                ),
                # </period>
            ]
        )
        # </indicator>
    ]
    element_record = ElementRecord(
        name='result',
        attributes=attributes,
        children=children
    )
    # </result>


class FssReference(BaseReference):
    """
    http://reference.iatistandard.org/203/activity-standard/iati-activities/iati-activity/fss/
    """

    # <fss>
    attributes = [
        # @extraction-date
        AttributeRecord(
            name='extraction-date',
            key='extraction_date'
        ),
        # @priority
        AttributeRecord(
            name='priority',
            key='priority'
        ),
        # @phaseout-year
        AttributeRecord(
            name='phaseout-year',
            key='phaseout_year'
        )
    ]
    children = [
        # <condition>
        ElementRecord(
            name='forecast',
            key='forecasts',
            attributes=[
                # @year
                AttributeRecord(
                    name='year',
                    key='year'
                ),
                # @value-date
                AttributeRecord(
                    name='value-date',
                    key='value_date'
                ),
                # @currency
                AttributeRecord(
                    name='currency',
                    key='code',
                    dict_key='currency'
                ),
            ],
            children=[
                ElementRecord(
                    name=None,
                    key='value'
                )
            ]
        ),
        # </condition>

    ]
    element_record = ElementRecord(
        name='fss',
        attributes=attributes,
        children=children
    )
    # </fss>


class HumanitarianScopeReference(BaseReference):
    """
    http://reference.iatistandard.org/203/activity-standard/iati-activities/iati-activity/humanitarian-scope/
    """

    # <humanitarian-scope>
    attributes = [
        # @type
        AttributeRecord(
            name='type',
            key='code',
            dict_key='type'
        ),
        # @vocabulary
        AttributeRecord(
            name='vocabulary',
            key='code',
            dict_key='vocabulary'
        ),
        # @vocabulary-uri
        AttributeRecord(
            name='vocabulary-uri',
            key='vocabulary_uri'
        ),
        # @code
        AttributeRecord(
            name='code',
            key='code'
        )
    ]
    children = [
        # <narrative>
        ElementRecord(
            name=None,
            element_type=ElementWithNarrativeReference
        ),
        # </narrative>
    ]
    element_record = ElementRecord(
        name='humanitarian-scope',
        attributes=attributes,
        children=children

    )
    # </humanitarian-scope>


class RelatedActivityReference(BaseReference):
    """
    http://reference.iatistandard.org/203/activity-standard/iati-activities/iati-activity/related-activity/
    """

    # <related-activity>
    attributes = [
        # @ref
        AttributeRecord(
            name='ref',
            key='ref'
        ),
        # @type
        AttributeRecord(
            name='type',
            key='code',
            dict_key='type'
        )
    ]
    element_record = ElementRecord(
        name='related-activity',
        attributes=attributes
    )
    # </related-activity>


class ConditionsReference(BaseReference):
    """
    http://reference.iatistandard.org/203/activity-standard/iati-activities/iati-activity/conditions/
    """

    # <conditions>
    attributes = [
        # @attached
        AttributeRecord(
            name='attached',
            key='attached'
        ),
    ]
    children = [
        # <condition>
        ElementRecord(
            name='condition',
            key='condition',
            attributes=[
                # @type
                AttributeRecord(
                    name='type',
                    key='code',
                    dict_key='type'
                ),
            ],
            children=[
                # <narrative>
                ElementRecord(
                    name=None,
                    element_type=ElementWithNarrativeReference
                ),
                # </narrative>
            ]
        ),
        # </condition>
    ]
    element_record = ElementRecord(
        name='conditions',
        attributes=attributes,
        children=children
    )
    # </conditions>


class CountryBudgetItemsReference(BaseReference):
    """
    http://reference.iatistandard.org/203/activity-standard/iati-activities/iati-activity/country-budget-items/
    """

    # <country-budget-items>
    attributes = [
        # @vocabulary
        AttributeRecord(
            name='vocabulary',
            key='code',
            dict_key='vocabulary'
        ),
    ]
    children = [
        # <budget-item>
        ElementRecord(
            name='budget-item',
            key='budget_items',
            attributes=[
                # @code
                AttributeRecord(
                    name='code',
                    key='code',
                    dict_key='budget_identifier'
                ),
                # @percentage
                AttributeRecord(
                    name='percentage',
                    key='percentage'
                ),
            ],
            children=[
                # <description>
                # <narrative>
                ElementRecord(
                    name='description',
                    key='description',
                    element_type=ElementWithNarrativeReference
                ),
                # </narrative>
                # </description>
            ]
        ),
        # </budget-item>
    ]
    element_record = ElementRecord(
        name='country-budget-items',
        attributes=attributes,
        children=children
    )
    # </country-budget-items>


class TagReference(BaseReference):
    """
    http://reference.iatistandard.org/203/activity-standard/iati-activities/iati-activity/tag/
    """

    # <tag>
    attributes = [
        # @vocabulary
        AttributeRecord(
            name='vocabulary',
            key='code',
            dict_key='vocabulary'
        ),
        # @vocabulary-uri
        AttributeRecord(
            name='vocabulary-uri',
            key='vocabulary_uri'
        ),
        # @code
        AttributeRecord(
            name='code',
            key='code'
        ),
    ]
    children = [
        # <narrative>
        ElementRecord(
            name=None,
            element_type=ElementWithNarrativeReference
        ),
        # </narrative>
    ]
    element_record = ElementRecord(
        name='tag',
        attributes=attributes,
        children=children
    )
    # </tag>


class ActivityScopeReference(BaseReference):
    """
    http://reference.iatistandard.org/203/activity-standard/iati-activities/iati-activity/activity-scope/
    """

    # <activity-scope>
    attributes = [
        # @code
        AttributeRecord(
            name='code',
            key='code'
        ),
    ]
    element_record = ElementRecord(
        name='activity-scope',
        attributes=attributes
    )
    # </activity-scope>


class DefaultCurrencyOrgReference(BaseReference):
    """
    http://reference.iatistandard.org/203/organisation-standard/iati-organisations/iati-organisation/
    """

    # <iati-organisation
    attributes = [
        # @code
        AttributeRecord(
            name='default-currency',
            key='code'
        ),
    ]
    element_record = ElementRecord(
        attributes=attributes,
    )
    # />


class LastUpdatedDatetimeOrgReference(BaseReference):
    """
    http://reference.iatistandard.org/203/organisation-standard/iati-organisations/iati-organisation/
    """

    # <iati-organisation
    attributes = [
        # @code
        AttributeRecord(
            name='last-updated-datetime'
        ),
    ]
    element_record = ElementRecord(
        attributes=attributes,
    )
    # />


class XmlLangReference(BaseReference):
    """
    http://reference.iatistandard.org/203/organisation-standard/iati-organisations/iati-organisation/
    """

    # <iati-organisation />

    def create(self):
        self.parent_element.set(
            '{http://www.w3.org/XML/1998/namespace}lang', self.data.lower()
        )


class NameOrgReference(BaseReference):
    """
    http://reference.iatistandard.org/203/activity-standard/iati-activities/iati-activity/activity-scope/
    """

    # <name>
    element_record = ElementRecord(
        name='name',
        element_type=ElementWithNarrativeReference
    )
    # </name>


class ReportingOrgOrgReference(BaseReference):
    """
    http://reference.iatistandard.org/203/organisation-standard/iati-organisations/iati-organisation/reporting-org/
    """

    # <reporting-org
    attributes = [
        # @ref
        AttributeRecord(
            name='ref',
            key='ref'
        ),
        # @type
        AttributeRecord(
            name='type',
            key='code',
            dict_key='type'
        ),
        # @secondary-reporter
        AttributeRecord(
            name='secondary-reporter',
            key='secondary_reporter'
        ),
    ]
    # >
    children = [
        # <narrative>
        ElementRecord(
            name=None,
            element_type=ElementWithNarrativeReference
        ),
        # </narrative>
    ]
    element_record = ElementRecord(
        name='reporting-org',
        attributes=attributes,
        children=children
    )
    # </reporting-org>


class TotalBudgetOrgReference(BaseReference):
    """
    http://reference.iatistandard.org/203/organisation-standard/iati-organisations/iati-organisation/total-budget/
    """

    # <total-budget
    attributes = [
        # @status
        AttributeRecord(
            name='status',
            key='code',
            dict_key='status'
        )
    ]
    # >
    children = [
        # <period-start
        ElementRecord(
            name='period-start',
            attributes=[
                # @iso-date
                AttributeRecord(
                    name='iso-date',
                    key='period_start',
                )
            ],
        ),
        # />
        # <period-start
        ElementRecord(
            name='period-end',
            attributes=[
                # @iso-date
                AttributeRecord(
                    name='iso-date',
                    key='period_end',
                )
            ],
        ),
        # />
        # <value
        ElementRecord(
            name='value',
            key='value',
            attributes=[
                # @currency
                AttributeRecord(
                    name='currency',
                    key='code',
                    dict_key='currency'
                ),
                # @value-date
                AttributeRecord(
                    name='value-date',
                    key='date'
                ),
            ],
            # />
        ),
        # </value>
        # <budget-line
        ElementRecord(
            name='budget-line',
            key='budget_lines',
            attributes=[
                # @ref
                AttributeRecord(
                    name='ref',
                    key='ref'
                ),
            ],
            # />
            children=[
                # <value
                ElementRecord(
                    name='value',
                    key='value',
                    attributes=[
                        # @currency
                        AttributeRecord(
                            name='currency',
                            key='code',
                            dict_key='currency'
                        ),
                        # @value-date
                        AttributeRecord(
                            name='value-date',
                            key='date'
                        ),
                    ],
                    # />
                ),
                # </value>
                # <narrative>
                ElementRecord(
                    name=None,
                    element_type=ElementWithNarrativeReference
                ),
                # </narrative>
            ]
        ),
        # </budget-line>
    ]
    element_record = ElementRecord(
        name='reporting-org',
        attributes=attributes,
        children=children
    )
    # <total-budget/>


class RecipientOrgBudgetOrgReference(BaseReference):
    """
    http://reference.iatistandard.org/203/organisation-standard/iati-organisations/iati-organisation/recipient-org-budget/
    """

    # <recipient-org-budget
    attributes = [
        # @status
        AttributeRecord(
            name='status',
            key='code',
            dict_key='status'
        )
    ]
    # >
    children = [
        # <recipient-org
        ElementRecord(
            name='recipient-org',
            key='recipient_org',
            attributes=[
                # @ref
                AttributeRecord(
                    name='ref',
                    key='ref',
                )
            ],
            # />
            children=[
                # <narrative>
                ElementRecord(
                    name=None,
                    element_type=ElementWithNarrativeReference
                ),
                # </narrative>
            ]
        ),
        # </recipient-org>
        # <period-start
        ElementRecord(
            name='period-start',
            attributes=[
                # @iso-date
                AttributeRecord(
                    name='iso-date',
                    key='period_start',
                )
            ],
        ),
        # />
        # <period-start
        ElementRecord(
            name='period-end',
            attributes=[
                # @iso-date
                AttributeRecord(
                    name='iso-date',
                    key='period_end',
                )
            ],
        ),
        # />
        # <value
        ElementRecord(
            name='value',
            key='value',
            attributes=[
                # @currency
                AttributeRecord(
                    name='currency',
                    key='code',
                    dict_key='currency'
                ),
                # @value-date
                AttributeRecord(
                    name='value-date',
                    key='date'
                ),
            ],
            # />
        ),
        # </value>
        # <budget-line
        ElementRecord(
            name='budget-line',
            key='budget_lines',
            attributes=[
                # @ref
                AttributeRecord(
                    name='ref',
                    key='ref'
                ),
            ],
            # />
            children=[
                # <value
                ElementRecord(
                    name='value',
                    key='value',
                    attributes=[
                        # @currency
                        AttributeRecord(
                            name='currency',
                            key='code',
                            dict_key='currency'
                        ),
                        # @value-date
                        AttributeRecord(
                            name='value-date',
                            key='date'
                        ),
                    ],
                    # />
                ),
                # </value>
                # <narrative>
                ElementRecord(
                    name=None,
                    element_type=ElementWithNarrativeReference
                ),
                # </narrative>
            ]
        ),
        # </budget-line>
    ]
    element_record = ElementRecord(
        name='recipient-org-budget',
        attributes=attributes,
        children=children
    )
    # <recipient-org-budget/>


class RecipientRegionBudgetOrgReference(BaseReference):
    """
    http://reference.iatistandard.org/203/organisation-standard/iati-organisations/iati-organisation/recipient-region-budget/
    """

    # <recipient-region-budget
    attributes = [
        # @status
        AttributeRecord(
            name='status',
            key='code',
            dict_key='status'
        )
    ]
    # >
    children = [
        # <recipient-org
        ElementRecord(
            name='recipient-region',
            key='recipient_region',
            attributes=[
                # @vocabulary
                AttributeRecord(
                    name='vocabulary',
                    key='code',
                    dict_key='region_vocabulary'
                ),
                # @vocabulary-uri
                AttributeRecord(
                    name='vocabulary-uri',
                    key='url'
                ),
                # @code
                AttributeRecord(
                    name='code',
                    key='code'
                ),
            ],
        ),
        # />
        # <period-start
        ElementRecord(
            name='period-start',
            attributes=[
                # @iso-date
                AttributeRecord(
                    name='iso-date',
                    key='period_start',
                )
            ],
        ),
        # />
        # <period-start
        ElementRecord(
            name='period-end',
            attributes=[
                # @iso-date
                AttributeRecord(
                    name='iso-date',
                    key='period_end',
                )
            ],
        ),
        # />
        # <value
        ElementRecord(
            name='value',
            key='value',
            attributes=[
                # @currency
                AttributeRecord(
                    name='currency',
                    key='code',
                    dict_key='currency'
                ),
                # @value-date
                AttributeRecord(
                    name='value-date',
                    key='date'
                ),
            ],
            # />
        ),
        # </value>
        # <budget-line
        ElementRecord(
            name='budget-line',
            key='budget_lines',
            attributes=[
                # @ref
                AttributeRecord(
                    name='ref',
                    key='ref'
                ),
            ],
            # />
            children=[
                # <value
                ElementRecord(
                    name='value',
                    key='value',
                    attributes=[
                        # @currency
                        AttributeRecord(
                            name='currency',
                            key='code',
                            dict_key='currency'
                        ),
                        # @value-date
                        AttributeRecord(
                            name='value-date',
                            key='date'
                        ),
                    ],
                    # />
                ),
                # </value>
                # <narrative>
                ElementRecord(
                    name=None,
                    element_type=ElementWithNarrativeReference
                ),
                # </narrative>
            ]
        ),
        # </budget-line>
    ]
    element_record = ElementRecord(
        name='recipient-region-budget',
        attributes=attributes,
        children=children
    )
    # </recipient-region-budget>


class RecipientCountryBudgetOrgReference(BaseReference):
    """
    http://reference.iatistandard.org/203/organisation-standard/iati-organisations/iati-organisation/recipient-country-budget/
    """

    # <recipient-country-budge
    attributes = [
        # @status
        AttributeRecord(
            name='status',
            key='code',
            dict_key='status'
        )
    ]
    # >
    children = [
        # <recipient-org
        ElementRecord(
            name='recipient-country',
            key='recipient_country',
            attributes=[
                # @code
                AttributeRecord(
                    name='code',
                    key='code'
                )
            ],
        ),
        # />
        # <period-start
        ElementRecord(
            name='period-start',
            attributes=[
                # @iso-date
                AttributeRecord(
                    name='iso-date',
                    key='period_start',
                )
            ],
        ),
        # />
        # <period-start
        ElementRecord(
            name='period-end',
            attributes=[
                # @iso-date
                AttributeRecord(
                    name='iso-date',
                    key='period_end',
                )
            ],
        ),
        # />
        # <value
        ElementRecord(
            name='value',
            key='value',
            attributes=[
                # @currency
                AttributeRecord(
                    name='currency',
                    key='code',
                    dict_key='currency'
                ),
                # @value-date
                AttributeRecord(
                    name='value-date',
                    key='date'
                ),
            ],
            # />
        ),
        # </value>
        # <budget-line
        ElementRecord(
            name='budget-line',
            key='budget_lines',
            attributes=[
                # @ref
                AttributeRecord(
                    name='ref',
                    key='ref'
                ),
            ],
            # />
            children=[
                # <value
                ElementRecord(
                    name='value',
                    key='value',
                    attributes=[
                        # @currency
                        AttributeRecord(
                            name='currency',
                            key='code',
                            dict_key='currency'
                        ),
                        # @value-date
                        AttributeRecord(
                            name='value-date',
                            key='date'
                        ),
                    ],
                    # />
                ),
                # </value>
                # <narrative>
                ElementRecord(
                    name=None,
                    element_type=ElementWithNarrativeReference
                ),
                # </narrative>
            ]
        ),
        # </budget-line>
    ]
    element_record = ElementRecord(
        name='recipient-country-budget',
        attributes=attributes,
        children=children
    )
    # </recipient-country-budge>


class TotalExpenditureOrgReference(BaseReference):
    """
    http://reference.iatistandard.org/203/organisation-standard/iati-organisations/iati-organisation/total-expenditure/
    """

    # <recipient-region-budget>
    children = [
        # <period-start
        ElementRecord(
            name='period-start',
            attributes=[
                # @iso-date
                AttributeRecord(
                    name='iso-date',
                    key='period_start',
                )
            ],
        ),
        # />
        # <period-start
        ElementRecord(
            name='period-end',
            attributes=[
                # @iso-date
                AttributeRecord(
                    name='iso-date',
                    key='period_end',
                )
            ],
        ),
        # />
        # <value
        ElementRecord(
            name='value',
            key='value',
            attributes=[
                # @currency
                AttributeRecord(
                    name='currency',
                    key='code',
                    dict_key='currency'
                ),
                # @value-date
                AttributeRecord(
                    name='value-date',
                    key='date'
                ),
            ],
            # />
        ),
        # </value>
        # <expense-line
        ElementRecord(
            name='expense-line',
            key='expense_line',
            attributes=[
                # @ref
                AttributeRecord(
                    name='ref',
                    key='ref'
                ),
            ],
            # />
            children=[
                # <value
                ElementRecord(
                    name='value',
                    key='value',
                    attributes=[
                        # @currency
                        AttributeRecord(
                            name='currency',
                            key='code',
                            dict_key='currency'
                        ),
                        # @value-date
                        AttributeRecord(
                            name='value-date',
                            key='date'
                        ),
                    ],
                    # />
                ),
                # </value>
                # <narrative>
                ElementRecord(
                    name=None,
                    element_type=ElementWithNarrativeReference
                ),
                # </narrative>
            ]
        ),
        # </budget-line>
    ]
    element_record = ElementRecord(
        name='total-expenditure',
        children=children
    )
    # </total-expenditure>
