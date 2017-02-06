import re
from iati import models
from iati.transaction import models as transaction_models
from iati_codelists import models as codelist_models
from iati_vocabulary import models as vocabulary_models
from iati_organisation import models as organisation_models
from geodata import models as geodata_models
import dateutil.parser
from datetime import datetime
from decimal import Decimal
from iati_synchroniser.models import Publisher

from iati.parser.exceptions import *

# def get_or_raise(model, validated_data, attr, default=None):
#     try:
#         pk = validated_data.pop(attr)
#     except KeyError:
#         raise RequiredFieldError(
#                 model.__name__,
#                 attr,
#                 apiField=attr,
#                 )

#     return model.objects.get(pk=pk)
#     # except model.DoesNotExist:
#     #     return default


def get_or_none(model, validated_data, attr, default=None):
    pk = validated_data.pop(attr, None)

    if pk is None:
        return default
    try:
        return model.objects.get(pk=pk)
    except model.DoesNotExist:
        return default

def get_or_none(model, *args, **kwargs):
    try:
        return model.objects.get(*args, **kwargs)
    except model.DoesNotExist:
        return None

def validate_date(unvalidated_date):
    # datetime

    if isinstance(unvalidated_date, datetime):
        return unvalidated_date

    if unvalidated_date:
        unvalidated_date = unvalidated_date.strip(' \t\n\rZ')
    else:
        return None

    #check if standard data parser works
    try:
        date = dateutil.parser.parse(unvalidated_date, ignoretz=True)
        if date.year >= 1900 and date.year <= 2100:
            return date
        else:
            return None
    except:
        raise RequiredFieldError(
                "TO DO",
                "iso-date",
                "Unspecified or invalid. Date should be of type xml:date.")

def validate_dates(*dates):
    return combine_validation([ validate_date(date) for date in dates ])

    # for date in dates:
    #     validate_date()

def narrative(i, activity_id, default_lang, lang, text, apiField=""):
    warnings = []
    errors = []

    if lang:
        lang = lang.lower()

    language = get_or_none(codelist_models.Language, code=lang)

    if not language:
        language = default_lang

    if not language:
        errors.append(
            RequiredFieldError(
                "narrative",
                "xml:lang",
                "must specify xml:lang on iati-activity or xml:lang on the element itself",
                apiField="{}narratives[{}].language".format(apiField + "." if apiField else "", i),
                ))

    if not text:
        errors.append(
            RequiredFieldError(
                'narrative',
                "text", 
                "empty narrative",
                apiField="{}narratives[{}].text".format(apiField + "." if apiField else "", i),
                ))

    return {
        "warnings": warnings,
        "errors": errors,
        "validated_data": {
            # "activity_id": activity_id,
            "language": language,
            "content": text,
        }
    }

def narratives(narratives, default_lang, activity_id, warnings=[], errors=[], apiField=""):
    # warnings = []
    # errors = []
    validated_data = []

    for i, n in enumerate(narratives):
        validated = narrative(i, activity_id, default_lang, n.get('language', {}).get('code'), n.get('content'), apiField)
        warnings = warnings + validated['warnings']
        errors = errors + validated['errors']
        validated_data.append(validated['validated_data'])

    return {
        "warnings": warnings,
        "errors": errors,
        "validated_data": validated_data,
    }


def activity_transaction(
        activity,
        ref,
        humanitarian,
        transaction_type_code,
        transaction_date_raw,
        value,
        value_date_raw,
        currency_code,
        description_narratives_data,
        provider_org_ref,
        provider_org_activity_id,
        provider_org_type_code,
        provider_org_narratives_data,
        receiver_org_ref,
        receiver_org_activity_id,
        receiver_org_type_code,
        receiver_org_narratives_data,
        disbursement_channel_code,
        # sector_code,
        # sector_vocabulary_code,
        # sector_vocabulary_uri,
        recipient_countries,
        recipient_region_code,
        recipient_region_vocabulary_code,
        recipient_region_vocabulary_uri,
        flow_type_code,
        finance_type_code,
        aid_type_code,
        tied_status_code,
        ):
        warnings = []
        errors = []

        if not description_narratives_data:
            description_narratives_data = []
        if not provider_org_narratives_data:
            provider_org_narratives_data = []
        if not receiver_org_narratives_data:
            receiver_org_narratives_data = []

        transaction_type = get_or_none(models.TransactionType, pk=transaction_type_code)
        currency = get_or_none(models.Currency, pk=currency_code)
        provider_org_type = get_or_none(models.OrganisationType, pk=provider_org_type_code)
        provider_org_organisation = get_or_none(models.Organisation, pk=provider_org_ref)
        provider_org_activity = get_or_none(models.Activity, pk=provider_org_activity_id)
        receiver_org_type = get_or_none(models.OrganisationType, pk=receiver_org_type_code)
        receiver_org_organisation = get_or_none(models.Organisation, pk=receiver_org_ref)
        receiver_org_activity = get_or_none(models.Activity, pk=receiver_org_activity_id)
        disbursement_channel = get_or_none(models.DisbursementChannel, pk=disbursement_channel_code)
        # sector = get_or_none(models.Sector, pk=sector_code)
        # sector_vocabulary = get_or_none(models.SectorVocabulary, pk=sector_vocabulary)
        # recipient_country = get_or_none(models.Country, pk=recipient_country_code)
        recipient_region = get_or_none(models.Region, pk=recipient_region_code)
        recipient_region_vocabulary = get_or_none(models.RegionVocabulary, pk=recipient_region_vocabulary_code)
        flow_type = get_or_none(models.FlowType, pk=flow_type_code)
        finance_type = get_or_none(models.FinanceType, pk=finance_type_code)
        aid_type = get_or_none(models.AidType, pk=aid_type_code)
        tied_status = get_or_none(models.TiedStatus, pk=tied_status_code)

        if not humanitarian in (0,1):
            errors.append(
                FieldValidationError(
                    "transaction",
                    "humanitarian",
                    apiField="humanitarian",
                    ))

        if not transaction_type_code:
            errors.append(
                RequiredFieldError(
                    "transaction",
                    "transaction-type",
                    apiField="transaction_type.code",
                    ))
        if not transaction_type:
            errors.append(
                FieldValidationError(
                    "transaction",
                    "transaction-type",
                    "codelist entry not found for {}".format(transaction_type_code),
                    apiField="transaction_type.code",
                    ))

        # if not disbursement_channel_code:
        #     errors.append(
        #         RequiredFieldError(
        #             "transaction",
        #             "disbursement-channel",
        #             apiField="disbursement_channel.code",
        #             ))
        if not disbursement_channel:
            errors.append(
                FieldValidationError(
                    "transaction",
                    "disbursement-channel",
                    "codelist entry not found for {}".format(disbursement_channel_code),
                    apiField="disbursement_channel.code",
                    ))

        if not transaction_date_raw:
            errors.append(
                RequiredFieldError(
                    "transaction",
                    "transaction-date",
                    apiField="transaction_date",
                    ))
            transaction_date = None
        else:
            try:
                transaction_date = validate_date(transaction_date_raw)
            except RequiredFieldError:
                errors.append(
                    FieldValidationError(
                        "transaction",
                        "transaction-date",
                        "iso-date not of type xsd:date",
                        apiField="transaction_date",
                        ))
                transaction_date = None

        if not value:
            errors.append(
                RequiredFieldError(
                    "transaction",
                    "value",
                    apiField="value",
                    ))

        if not value_date_raw:
            errors.append(
                RequiredFieldError(
                    "transaction",
                    "value-date",
                    apiField="value_date",
                    ))
            value_date = None
        else:
            try:
                value_date = validate_date(value_date_raw)
            except RequiredFieldError:
                errors.append(
                    FieldValidationError(
                        "transaction",
                        "value-date",
                        "iso-date not of type xsd:date",
                        apiField="value_date",
                        ))
                value_date = None

        if not currency and not activity.default_currency:
            errors.append(
                RequiredFieldError(
                    "transaction",
                    "currency",
                    "currency not specified and no default specified on activity",
                    apiField="currency.code",
                    ))


        # if sector_code:
        #     # check if activity is using sector-strategy or transaction-sector strategy
        #     has_existing_sectors = len(models.ActivitySector.objects.filter(activity=activity))

        #     if has_existing_sectors:
        #         errors.append(
        #             RequiredFieldError(
        #                 "transaction",
        #                 "sector",
        #                 "Already provided a sector on activity",
        #                 ))

        # if recipient_country_code:
        #     # check if activity is using recipient_country-strategy or transaction-recipient_country strategy
        #     has_existing_recipient_countries = len(models.ActivityRecipientCountry.objects.filter(activity=activity))


        #     if has_existing_recipient_countries:
        #         errors.append(
        #             FieldValidationError(
        #                 "transaction",
        #                 "recipient_country",
        #                 "Already provided a recipient_country on activity",
        #                 apiField="last_updated_datetime",
        #                 ))

        validated_recipient_countries = []
        countries_codes = []
        if len(recipient_countries) > 0:
        	for country in recipient_countries:
        		country_code = country.get('country')['code']
        		validated_country = get_or_none(geodata_models.Country, pk=country_code)
        		country_item = {}
        		country_item["country"] = validated_country
        		validated_recipient_countries.append(country_item)
        		countries_codes.append(country_code)

		if len(validated_recipient_countries) != len(validated_recipient_countries) or (len(validated_recipient_countries) > 1 and len(validated_recipient_countries) != len(set(validated_recipient_countries))):
			errors.append(
				FieldValidationError(
                    "transaction",
                    "recipient_countries",
                    "Country Code entry not found for {}".format(country_code),
                    apiField="recipient_countries",
                    ))



        if recipient_region_code:
            # check if activity is using recipient_region-strategy or transaction-recipient_region strategy
            has_existing_recipient_regions = len(models.ActivityRecipientRegion.objects.filter(activity=activity))

            if has_existing_recipient_regions:
                errors.append(
                    FieldValidationError(
                        "transaction",
                        "recipient_region",
                        "Already provided a recipient_region on activity",
                        apiField="recipient_countries",
                        ))



        # provider-org-ref is set so assume user wants to report it
        if provider_org_ref:
            if not provider_org_activity:
                provider_org_activity = activity

        description_narratives = narratives(description_narratives_data, activity.default_lang, activity.id,  warnings, errors, "description")
        errors = errors + description_narratives['errors']
        warnings = warnings + description_narratives['warnings']

        provider_org_narratives = narratives(provider_org_narratives_data, activity.default_lang, activity.id,  warnings, errors, "provider_organisation")
        errors = errors + provider_org_narratives['errors']
        warnings = warnings + provider_org_narratives['warnings']

        receiver_org_narratives = narratives(receiver_org_narratives_data, activity.default_lang, activity.id,  warnings, errors, "receiver_organisation")
        errors = errors + receiver_org_narratives['errors']
        warnings = warnings + receiver_org_narratives['warnings']

        return {
            "warnings": warnings,
            "errors": errors,
            "validated_data": {
                "activity": activity,
                "ref": ref,
                "humanitarian": humanitarian,
                "transaction_type": transaction_type,
                "transaction_date": transaction_date,
                "value": value,
                "value_date": value_date,
                "currency": currency,
                "description_narratives": description_narratives['validated_data'],
                "provider_org": {
                    "ref": provider_org_ref,
                    "normalized_ref": provider_org_ref,
                    "organisation": provider_org_organisation,
                    "provider_activity": provider_org_activity,
                    "type": provider_org_type,
                },
                "provider_org_narratives": provider_org_narratives['validated_data'],
                "receiver_org": {
                    "ref": receiver_org_ref,
                    "normalized_ref": receiver_org_ref,
                    "organisation": receiver_org_organisation,
                    "receiver_activity": receiver_org_activity,
                    "type": receiver_org_type,
                },
                "receiver_org_narratives": receiver_org_narratives['validated_data'],
                "disbursement_channel": disbursement_channel,
                # "sector": {
                #     "sector": sector,
                #     "vocabulary": sector_vocabulary,
                #     "vocabulary_uri": sector_vocabulary
                # },
                "recipient_countries": recipient_countries,
                "recipient_region": {
                    "recipient_region": recipient_region,
                    "vocabulary": recipient_region_vocabulary,
                    "vocabulary_uri": recipient_region_vocabulary
                },
                "flow_type": flow_type,
                "finance_type": finance_type,
                "aid_type": aid_type,
                "tied_status": tied_status,
            },
        }