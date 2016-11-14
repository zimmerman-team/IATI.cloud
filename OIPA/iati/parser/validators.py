import re
from iati import models
from iati.transaction import models as transaction_models
from iati_codelists import models as codelist_models
from iati_vocabulary import models as vocabulary_models
from iati_organisation import models as organisation_models
import dateutil.parser
from datetime import datetime
from decimal import Decimal

from iati.parser.exceptions import *

def get_or_raise(model, validated_data, attr, default=None):
    try:
        pk = validated_data.pop(attr)
    except KeyError:
        raise RequiredFieldError(
                model.__name__,
                attr,
                )

    return model.objects.get(pk=pk)
    # except model.DoesNotExist:
    #     return default


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

def normalize(attr): 
    attr = attr.strip(' \t\n\r').replace(" ", "")
    attr = re.sub("[/:',.+]", "-", attr)
    return attr

def makeBool(text):
    if type(text) == bool:
        return text
    if text == '1' or text == 'true':
        return True
    return False

def makeBoolNone(text):
    if type(text) == bool:
        return text
    if text == '1':
        return True
    elif text == '0':
        return False

    return None

def combine_validation(validations=[]):
    warnings = []
    errors = []
    validated_data = {}

    for validation in validations:
        warnings.append(validation['warnings'])
        errors.append(validation['errors'])
        validated_data.update(validation['validated_data'])

    return {
        "warnings": warnings,
        "errors": errors,
        "validated_data": validated_data,
    }

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


def narrative(activity_id, default_lang, lang, text):
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
                ))

    if not text:
        errors.append(
            RequiredFieldError(
                'narrative',
                "text", 
                "empty narrative",
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

def narratives(narratives, default_lang, activity_id, warnings=[], errors=[]):
    # warnings = []
    # errors = []
    validated_data = []

    for n in narratives:
        validated = narrative(activity_id, default_lang, n.get('language', {}).get('code'), n.get('content'))
        warnings = warnings + validated['warnings']
        errors = errors + validated['errors']
        validated_data.append(validated['validated_data'])

    return {
        "warnings": warnings,
        "errors": errors,
        "validated_data": validated_data,
    }

def codelist(iati_name, model, code):
    warnings = []
    errors = []

    if not code:
        errors.append(
            RequiredFieldError(
                iati_name,
                "ref",
                ))
    
    instance = get_or_none(model, pk=code)

    if not instance:
        errors.append(
            RequiredFieldError(
                iati_name,
                "code",
                "not found on the accompanying code list"
                ))

    return {
        "warnings": warnings,
        "errors": errors,
        "validated_data": instance,
    }


def activity(
        iati_identifier,
        default_lang,
        hierarchy,
        humanitarian,
        last_updated_datetime,
        linked_data_uri,
        default_currency,
        dataset=None, # if parsed
        activity_status=None,
        activity_scope=None,
        collaboration_type=None,
        default_flow_type=None,
        default_finance_type=None,
        default_aid_type=None,
        default_tied_status=None,
        planned_start=None,
        actual_start=None,
        start_date=None,
        planned_end=None,
        actual_end=None,
        end_date=None,
        title={}, # important arg
        iati_standard_version="2.02",
        published=False,
        ):

        warnings = []
        errors = []

        if not hierarchy: hierarchy = 1

        default_currency = get_or_none(models.Currency, pk=default_currency)
        iati_standard_version = get_or_none(models.Version, pk=iati_standard_version)
        activity_status = get_or_none(models.ActivityStatus, pk=activity_status)
        activity_scope = get_or_none(models.ActivityScope, pk=activity_scope)
        collaboration_type = get_or_none(models.CollaborationType, pk=collaboration_type)
        default_flow_type = get_or_none(models.FlowType, pk=default_flow_type)
        default_finance_type = get_or_none(models.FinanceType, pk=default_finance_type)
        default_aid_type = get_or_none(models.AidType, pk=default_aid_type)
        default_tied_status = get_or_none(models.TiedStatus, pk=default_tied_status)
        default_lang = get_or_none(models.Language, pk=default_lang)

        try:
            last_updated_datetime = validate_date(last_updated_datetime)
        except RequiredFieldError:
            errors.append(
                RequiredFieldError(
                    "activity",
                    "last-updated-datetime",
                    "invalid date",
                    ))
            last_updated_datetime = None

        try:
            planned_start = validate_date(planned_start)
        except RequiredFieldError:
            errors.append(
                RequiredFieldError(
                    "activity",
                    "planned-start",
                    "invalid date",
                    ))
            planned_start = None


        try:
            actual_start = validate_date(actual_start)
        except RequiredFieldError:
            errors.append(
                RequiredFieldError(
                    "activity",
                    "planned-start",
                    "invalid date",
                    ))
            actual_start = None


        try:
            start_date = validate_date(start_date)
        except RequiredFieldError:
            errors.append(
                RequiredFieldError(
                    "activity",
                    "planned-start",
                    "invalid date",
                    ))
            start_date = None

        try:
            planned_end = validate_date(planned_end)
        except RequiredFieldError:
            errors.append(
                RequiredFieldError(
                    "activity",
                    "planned-start",
                    "invalid date",
                    ))
            planned_end = None

        try:
            actual_end = validate_date(actual_end)
        except RequiredFieldError:
            errors.append(
                RequiredFieldError(
                    "activity",
                    "planned-start",
                    "invalid date",
                    ))
            actual_end = None

        try:
            end_date = validate_date(end_date)
        except RequiredFieldError:
            errors.append(
                RequiredFieldError(
                    "activity",
                    "planned-start",
                    "invalid date",
                    ))
            end_date = None

            # validate_dates(
            #     last_updated_datetime,
            #     planned_start,
            #     actual_start,
            #     start_date,
            #     planned_end,
            #     actual_end,
            #     end_date
            # ),


        if not default_lang:
            warnings.append(
                RequiredFieldError(
                    "activity",
                    "default-lang",
                    ))


        activity_id = normalize(iati_identifier)

        if not activity_id:
            errors.append(
                RequiredFieldError(
                    "activity",
                    "iati-identifier",
                    ))

        if not len(title):
            errors.append(
                RequiredFieldError(
                    "activity",
                    "title",
                    ))

        title_narratives = title.get('narratives', [])
        if not len(title_narratives):
            errors.append(
                RequiredFieldError(
                    "activity",
                    "title__narratives",
                    ))

        validate_dates()

        title_narratives = narratives(title_narratives, default_lang, activity_id,  warnings, errors)
        errors = errors + title_narratives['errors']
        warnings = warnings + title_narratives['warnings']

        return {
            "warnings": warnings,
            "errors": errors,
            "validated_data": {
                "id": activity_id,
                "iati_identifier": iati_identifier,
                "default_lang": default_lang,
                "hierarchy": hierarchy,
                "humanitarian": humanitarian,
                "dataset": dataset,
                "last_updated_datetime": last_updated_datetime,
                "linked_data_uri": linked_data_uri,
                "default_currency": default_currency,
                "activity_status": activity_status,
                "activity_scope": activity_scope,
                "collaboration_type": collaboration_type,
                "default_flow_type": default_flow_type,
                "default_finance_type": default_finance_type,
                "default_aid_type": default_aid_type,
                "default_tied_status": default_tied_status,
                "default_lang": default_lang,
                "iati_standard_version_id": iati_standard_version,
                "published": published,
                "title": {
                    "activity_id": activity_id,
                },
                "title_narratives": title_narratives['validated_data'],
            },
        }

def activity_reporting_org(
        activity,
        ref,
        org_type,
        secondary_reporter,
        narratives_data=[],
        ):

        organisation = get_or_none(models.Organisation, pk=ref)
        org_type = get_or_none(codelist_models.OrganisationType, code=org_type)

        warnings = []
        errors = []

        if not ref:
            errors.append(
                RequiredFieldError(
                    "reporting-org",
                    "ref",
                    ))

        if not org_type:
            errors.append(
                RequiredFieldError(
                    "reporting-org",
                    "type",
                    ))

        if not secondary_reporter:
            secondary_reporter = False

        if not organisation:
            warnings.append(
                RequiredFieldError(
                    "reporting-org",
                    "organisation",
                    "organisation with ref {} does not exist in organisation standard".format(ref)
                    ))

        validated_narratives = narratives(narratives_data, activity.default_lang, activity.id,  warnings, errors)
        errors = errors + validated_narratives['errors']
        warnings = warnings + validated_narratives['warnings']

        return {
            "warnings": warnings,
            "errors": errors,
            "validated_data": { # maps to model fields
                "activity": activity,
                "ref": ref,
                "normalized_ref": normalize(ref),
                "type": org_type,
                "secondary_reporter": secondary_reporter,
                "organisation": organisation,
                "narratives": validated_narratives['validated_data'],
            }
        }
        

def activity_description(
        activity,
        type_code=0,
        narratives_data=[]
        ):
        warnings = []
        errors = []

        description_type = get_or_none(models.DescriptionType, code=type_code)

        if not len(narratives_data):
            errors.append(
                RequiredFieldError(
                    "activity",
                    "description__narratives",
                    ))

        validated_narratives = narratives(narratives_data, activity.default_lang, activity.id,  warnings, errors)

        return {
            "warnings": warnings,
            "errors": errors,
            "validated_data": {
                "activity": activity,
                "type": description_type,
                "narratives": validated_narratives['validated_data'],
            },
        }


def activity_participating_org(
        activity,
        ref,
        org_type,
        org_role,
        org_activity_id=None,
        narratives_data=[],
        ):

        organisation = get_or_none(models.Organisation, pk=ref)
        org_type = get_or_none(codelist_models.OrganisationType, code=org_type)
        org_role = get_or_none(codelist_models.OrganisationRole, code=org_role)

        warnings = []
        errors = []

        # NOTE: strictly taken, the ref should be specified. In practice many reporters don't use them
        # simply because they don't know the ref.
        if not ref:
            warnings.append(
                RequiredFieldError(
                    "reporting-org",
                    "ref",
                    ))

        if not org_type:
            warnings.append(
                RequiredFieldError(
                    "reporting-org",
                    "type",
                    ))

        if not org_role:
            errors.append(
                RequiredFieldError(
                    "reporting-org",
                    "role",
                    ))

        if not organisation:
            warnings.append(
                RequiredFieldError(
                    "reporting-org",
                    "organisation",
                    "organisation with ref {} does not exist in organisation standard".format(ref)
                    ))

        validated_narratives = narratives(narratives_data, activity.default_lang, activity.id,  warnings, errors)

        return {
            "warnings": warnings,
            "errors": errors,
            "validated_data": {
                "ref": ref,
                "normalized_ref": normalize(ref),
                "type": org_type,
                "role": org_role,
                "activity": activity,
                "organisation": organisation,
                "org_activity_id": org_activity_id,
                "narratives": validated_narratives['validated_data'],
            },
        }
 

def activity_activity_date(
        activity,
        type_code=0,
        iso_date=None,
        ):
        warnings = []
        errors = []

        activity_date_type = get_or_none(models.ActivityDateType, code=type_code)

        try:
            iso_date = validate_date(iso_date)
        except RequiredFieldError:
            errors.append(
                RequiredFieldError(
                    "activity",
                    "iso-date",
                    "invalid date",
                    ))

        return {
            "warnings": warnings,
            "errors": errors,
            "validated_data": {
                "activity": activity,
                "type": activity_date_type,
                "iso_date": iso_date,
            },
        }

def activity_contact_info(
        activity,
        type_code,
        organisation,
        department,
        person_name,
        job_title,
        telephone,
        email,
        website,
        mailing_address,
        ):

        warnings = []
        errors = []

        contact_type = get_or_none(models.ContactType, code=type_code)

        organisation_narratives_data = organisation.get('narratives', [])
        organisation_narratives = narratives(organisation_narratives_data, activity.default_lang, activity.id,  warnings, errors)
        errors = errors + organisation_narratives['errors']
        warnings = warnings + organisation_narratives['warnings']

        department_narratives_data = department.get('narratives', [])
        department_narratives = narratives(department_narratives_data, activity.default_lang, activity.id,  warnings, errors)
        errors = errors + department_narratives['errors']
        warnings = warnings + department_narratives['warnings']

        person_name_narratives_data = person_name.get('narratives', [])
        person_name_narratives = narratives(person_name_narratives_data, activity.default_lang, activity.id,  warnings, errors)
        errors = errors + person_name_narratives['errors']
        warnings = warnings + person_name_narratives['warnings']

        job_title_narratives_data = job_title.get('narratives', [])
        job_title_narratives = narratives(job_title_narratives_data, activity.default_lang, activity.id,  warnings, errors)
        errors = errors + job_title_narratives['errors']
        warnings = warnings + job_title_narratives['warnings']

        mailing_address_narratives_data = mailing_address.get('narratives', [])
        mailing_address_narratives = narratives(mailing_address_narratives_data, activity.default_lang, activity.id,  warnings, errors)
        errors = errors + mailing_address_narratives['errors']
        warnings = warnings + mailing_address_narratives['warnings']

        # TODO: test email, telephone, website for form - 2016-10-11
        return {
            "warnings": warnings,
            "errors": errors,
            "validated_data": {
                "activity": activity,
                "type": contact_type,
                "organisation": {
                    # "contact_info_id": contact_info.id,
                },
                "organisation_narratives": organisation_narratives['validated_data'],
                "department": {
                    # "contact_info_id": contact_info.id,
                },
                "department_narratives": department_narratives['validated_data'],
                "person_name": {
                    # "contact_info_id": contact_info.id,
                },
                "person_name_narratives": person_name_narratives['validated_data'],
                "job_title": {
                    # "contact_info_id": contact_info.id,
                },
                "job_title_narratives": job_title_narratives['validated_data'],
                "telephone": telephone,
                "email": email,
                "website": website,
                "mailing_address": {
                    # "contact_info_id": contact_info.id,
                },
                "mailing_address_narratives": mailing_address_narratives['validated_data'],
            },
        }


def activity_recipient_country(
        activity,
        country_code,
        percentage=0,
        instance=None, # only set on update
        ):
        warnings = []
        errors = []

        recipient_country = get_or_none(models.Country, code=country_code)

        if not recipient_country:
            errors.append(
                RequiredFieldError(
                    "recipient-country",
                    "code",
                    ))

        print(percentage, type(percentage))

        if type(percentage) is not int and type(percentage) is not Decimal:
            errors.append(
                RequiredFieldError(
                    "recipient-country",
                    "percentage",
                    ))

        if percentage < 0 or percentage > 100:
            errors.append(
                RequiredFieldError(
                    "recipient-country",
                    "percentage",
                    "percentage must be a value between 0 and 100"
                    ))

        # recipient_countries = activity.activityrecipientcountry_set.all()
        # # TODO: we need the update instance here ideally - 2016-10-17
        # if instance:
        #     sum_percentage = reduce(lambda acc, x: acc + x[0], recipient_countries.exclude(pk=instance.id).values_list('percentage'), 0) + percentage
        # else:
        #     sum_percentage = reduce(lambda acc, x: acc + x[0], recipient_countries.values_list('percentage'), 0) + percentage

        # if sum_percentage != Decimal(100):
        #     errors.append(
        #         ValidationError(
        #             "recipient-country",
        #             "percentage",
        #             "The recipient-country percentage doesn't add up to 100"
        #             ))

        return {
            "warnings": warnings,
            "errors": errors,
            "validated_data": {
                "activity": activity,
                "country": recipient_country,
                "percentage": percentage,
            },
        }

def activity_recipient_region(
        activity,
        region_code,
        vocabulary_code,
        vocabulary_uri,
        percentage=0,
        instance=None, # only set on update
        ):
        warnings = []
        errors = []

        recipient_region = get_or_none(models.Region, code=region_code)
        vocabulary = get_or_none(models.RegionVocabulary, code=vocabulary_code)

        if not region_code:
            errors.append(
                RequiredFieldError(
                    "recipient-region",
                    "code",
                    ))
        elif not recipient_region:
            errors.append(
                RequiredFieldError(
                    "recipient-region",
                    "code",
                    "recipient-region not found for code {}".format(region_code)
                    ))

        if not vocabulary_code:
            errors.append(
                RequiredFieldError(
                    "recipient-region",
                    "vocabulary",
                    ))
        elif not vocabulary: 
            errors.append(
                RequiredFieldError(
                    "recipient-region",
                    "vocabulary",
                    "vocabulary not found for code {}".format(vocabulary_code)
                    ))

        if vocabulary_code == "99" and not vocabulary_uri:
            errors.append(
                RequiredFieldError(
                    "recipient-region",
                    "vocabulary_uri",
                    "vocabulary_uri is required when vocabulary code is 99"
                    ))

        if type(percentage) is not int and type(percentage) is not Decimal:
            errors.append(
                RequiredFieldError(
                    "recipient-region",
                    "percentage",
                    ))

        if percentage < 0 or percentage > 100:
            errors.append(
                RequiredFieldError(
                    "recipient-region",
                    "percentage",
                    "percentage must be a value between 0 and 100"
                    ))


        return {
            "warnings": warnings,
            "errors": errors,
            "validated_data": {
                "activity": activity,
                "region": recipient_region,
                "vocabulary": vocabulary,
                "vocabulary_uri": vocabulary_uri,
                "percentage": percentage,
            },
        }


def activity_location(
        activity,
        ref,
        location_reach_code,
        location_id_code,
        location_id_vocabulary_code,
        name_narratives_data,
        description_narratives_data,
        activity_description_narratives_data,
        point_srs_name,
        point_pos,
        exactness_code,
        location_class_code,
        feature_designation_code,
        ):

        warnings = []
        errors = []

        location_reach = get_or_none(models.GeographicLocationReach, pk=location_reach_code)
        location_id_vocabulary = get_or_none(models.GeographicVocabulary, pk=location_id_vocabulary_code)
        exactness = get_or_none(models.GeographicExactness, pk=exactness_code)
        location_class = get_or_none(models.GeographicLocationClass, pk=location_class_code)
        feature_designation = get_or_none(models.LocationType, pk=feature_designation_code)

        if not ref:
            errors.append(
                RequiredFieldError(
                    "location",
                    "ref",
                    ))

        if not exactness_code:
            errors.append(
                RequiredFieldError(
                    "location",
                    "exactness",
                    ))
        elif not exactness: 
            errors.append(
                RequiredFieldError(
                    "location",
                    "exactness",
                    "codelist entry not found for {}".format(exactness_code)
                    ))

        name_narratives = narratives(name_narratives_data, activity.default_lang, activity.id,  warnings, errors)
        errors = errors + name_narratives['errors']
        warnings = warnings + name_narratives['warnings']

        description_narratives = narratives(description_narratives_data, activity.default_lang, activity.id,  warnings, errors)
        errors = errors + description_narratives['errors']
        warnings = warnings + description_narratives['warnings']

        activity_description_narratives = narratives(activity_description_narratives_data, activity.default_lang, activity.id,  warnings, errors)
        errors = errors + activity_description_narratives['errors']
        warnings = warnings + activity_description_narratives['warnings']

        return {
            "warnings": warnings,
            "errors": errors,
            "validated_data": {
                "activity": activity,
                "ref": ref,
                "location_reach": location_reach,
                "location_id_code": location_id_code,
                "location_id_vocabulary": location_id_vocabulary,
                "name_narratives": name_narratives_data,
                "description_narratives": description_narratives_data,
                "activity_description_narratives": activity_description_narratives_data,
                "point_srs_name": point_srs_name,
                "point_pos": point_pos,
                "exactness": exactness,
                "location_class": location_class,
                "feature_designation": feature_designation,
            },
        }
 

