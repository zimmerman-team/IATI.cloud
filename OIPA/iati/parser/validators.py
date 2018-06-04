import re
from datetime import date as datetime_date
from decimal import Decimal

import dateutil.parser

from iati import models
from iati.parser.exceptions import FieldValidationError, RequiredFieldError
from iati_codelists import models as codelist_models


def get_or_raise(model, validated_data, attr, default=None):
    try:
        pk = validated_data.pop(attr)
    except KeyError:
        raise RequiredFieldError(
            model.__name__,
            attr,
            apiField=attr,
        )

    return model.objects.get(pk=pk)


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
    if isinstance(text, bool):
        return text
    if text == '1' or text == 'true':
        return True
    return False


def makeBoolNone(text):
    if isinstance(text, bool):
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


iati_regex = re.compile(r'^[^\/\&\|\?]*$')


def validate_iati_identifier(iati_identifier):
    if iati_regex.match(iati_identifier):
        return True
    else:
        return False


def validate_date(unvalidated_date):
    # datetime

    if isinstance(unvalidated_date, datetime_date):
        return unvalidated_date

    if unvalidated_date:
        unvalidated_date = unvalidated_date.strip(' \t\n\rZ')
    else:
        return None

    # check if standard data parser works
    try:
        date = dateutil.parser.parse(unvalidated_date, ignoretz=True)
        if date.year >= 1900 and date.year <= 2100:
            return date
        else:
            return None
    except BaseException:
        raise RequiredFieldError(
            "TO DO",
            "iso-date",
            "Unspecified or invalid. Date should be of type xml:date.")


def validate_dates(*dates):
    return combine_validation([validate_date(date) for date in dates])


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
                "must specify xml:lang on iati-activity or xml:lang on the \
                        element itself",
                apiField="{}narratives[{}].language".format(
                    apiField + "." if apiField else "", i),
            ))

    if not text:
        errors.append(
            RequiredFieldError(
                'narrative',
                "text",
                "empty narrative",
                apiField="{}narratives[{}].text".format(
                    apiField + "." if apiField else "", i),
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


def narratives(narratives, default_lang, activity_id, warnings=[], errors=[],
               apiField=""):

    validated_data = []

    for i, n in enumerate(narratives):
        validated = narrative(
            i,
            activity_id,
            default_lang,
            n.get(
                'language',
                {}).get('code'),
            n.get('content'),
            apiField)
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
            FieldValidationError(
                iati_name,
                "code",
                "not found on the accompanying code list",
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
        dataset=None,  # if parsed
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
        capital_spend=None,
        secondary_reporter=None,
        title={},  # important arg
        iati_standard_version="2.02",
        published=False,
):

    warnings = []
    errors = []

    if not hierarchy:
        hierarchy = 1
    if not secondary_reporter:
        secondary_reporter = False

    default_currency = get_or_none(models.Currency, pk=default_currency)
    iati_standard_version = get_or_none(
        models.Version, pk=iati_standard_version)
    activity_status = get_or_none(models.ActivityStatus, pk=activity_status)
    activity_scope = get_or_none(models.ActivityScope, pk=activity_scope)
    collaboration_type = get_or_none(
        models.CollaborationType, pk=collaboration_type)
    default_flow_type = get_or_none(models.FlowType, pk=default_flow_type)
    default_finance_type = get_or_none(
        models.FinanceType, pk=default_finance_type)
    default_aid_type = get_or_none(models.AidType, pk=default_aid_type)
    default_tied_status = get_or_none(
        models.TiedStatus, pk=default_tied_status)
    default_lang = get_or_none(models.Language, pk=default_lang)

    try:
        last_updated_datetime = validate_date(last_updated_datetime)
    except RequiredFieldError:
        errors.append(
            FieldValidationError(
                "activity",
                "last-updated-datetime",
                "invalid date",
                apiField="last_updated_datetime",
            ))
        last_updated_datetime = None

    try:
        planned_start = validate_date(planned_start)
    except RequiredFieldError:
        errors.append(
            FieldValidationError(
                "activity",
                "planned-start",
                "invalid date",
                apiField="planned_start",
            ))
        planned_start = None

    try:
        actual_start = validate_date(actual_start)
    except RequiredFieldError:
        errors.append(
            FieldValidationError(
                "activity",
                "actual-start",
                "invalid date",
                apiField="planned_start",
            ))
        actual_start = None

    try:
        start_date = validate_date(start_date)
    except RequiredFieldError:
        errors.append(
            FieldValidationError(
                "activity",
                "start-date",
                "invalid date",
                apiField="start_date",
            ))
        start_date = None

    try:
        planned_end = validate_date(planned_end)
    except RequiredFieldError:
        errors.append(
            FieldValidationError(
                "activity",
                "planned-end",
                "invalid date",
                apiField="planned_end",
            ))
        planned_end = None

    try:
        actual_end = validate_date(actual_end)
    except RequiredFieldError:
        errors.append(
            FieldValidationError(
                "activity",
                "actual-end",
                "invalid date",
                apiField="actual_end",
            ))
        actual_end = None

    try:
        end_date = validate_date(end_date)
    except RequiredFieldError:
        errors.append(
            FieldValidationError(
                "activity",
                "end-date",
                "invalid date",
                apiField="end_date",
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
                apiField="default_lang",
            ))

    if not validate_iati_identifier(iati_identifier):
        errors.append(
            FieldValidationError(
                "activity",
                "iati-identifier",
                apiField="iati_identifier",
            ))

    # TODO: must be separated as validation to ensure - 2016-12-19
    # if not len(title):
    #     errors.append(
    #         RequiredFieldError(
    #             "activity",
    #             "title",
    #             ))

    title_narratives = title.get('narratives', [])
    # if not len(title_narratives):
    #     errors.append(
    #         RequiredFieldError(
    #             "activity",
    #             "title__narratives",
    #             ))

    title_narratives = narratives(
        title_narratives, default_lang, None, warnings, errors, "title")
    errors = errors + title_narratives['errors']
    warnings = warnings + title_narratives['warnings']

    return {
        "warnings": warnings,
        "errors": errors,
        "validated_data": {
            "iati_identifier": iati_identifier,
            "normalized_iati_identifier": iati_identifier,
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
            "capital_spend": capital_spend,
            "iati_standard_version": iati_standard_version,
            "published": published,
            "title": {
            },
            "title_narratives": title_narratives['validated_data'],
            "secondary_reporter": secondary_reporter,
        },
    }


def activity_reporting_org(
        activity,
        ref,
        org_type,
        secondary_reporter,
        narratives_data=[],
):

    organisation = get_or_none(
        models.Organisation, organisation_identifier=ref)
    org_type = get_or_none(codelist_models.OrganisationType, code=org_type)

    warnings = []
    errors = []

    if not ref:
        errors.append(
            RequiredFieldError(
                "reporting-org",
                "ref",
                apiField="ref",
            ))

    if not org_type:
        errors.append(
            FieldValidationError(
                "reporting-org",
                "type",
                apiField="type.code",
            ))

    if not secondary_reporter:
        secondary_reporter = False

    if not organisation:
        warnings.append(
            FieldValidationError(
                "reporting-org",
                "organisation",
                "organisation with ref {} does not exist in organisation \
                        standard".format(ref),
                apiField="organisation",
            ))

    validated_narratives = narratives(
        narratives_data,
        activity.default_lang,
        activity.id,
        warnings,
        errors)
    errors = errors + validated_narratives['errors']
    warnings = warnings + validated_narratives['warnings']

    return {
        "warnings": warnings,
        "errors": errors,
        "validated_data": {  # maps to model fields
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
                apiField="narratives",
            ))

    validated_narratives = narratives(
        narratives_data,
        activity.default_lang,
        activity.id,
        warnings,
        errors)
    errors = errors + validated_narratives['errors']
    warnings = warnings + validated_narratives['warnings']

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

    organisation = get_or_none(
        models.Organisation, organisation_identifier=ref)
    org_type = get_or_none(codelist_models.OrganisationType, code=org_type)
    org_role = get_or_none(codelist_models.OrganisationRole, code=org_role)

    warnings = []
    errors = []

    # NOTE: strictly taken, the ref should be specified. In practice many
    # reporters don't use them simply because they don't know the ref.
    if not ref:
        warnings.append(
            RequiredFieldError(
                "reporting-org",
                "ref",
                apiField="ref",
            ))

    if not org_type:
        warnings.append(
            FieldValidationError(
                "reporting-org",
                "type",
                apiField="type.code",
            ))

    if not org_role:
        errors.append(
            FieldValidationError(
                "reporting-org",
                "role",
                apiField="role.code",
            ))

    if not organisation:
        warnings.append(
            FieldValidationError(
                "reporting-org",
                "organisation",
                "organisation with ref {} does not exist in organisation \
                        standard".format(ref),
                apiField="organisation",
            ))

    validated_narratives = narratives(
        narratives_data,
        activity.default_lang,
        activity.id,
        warnings,
        errors)
    errors = errors + validated_narratives['errors']
    warnings = warnings + validated_narratives['warnings']

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
            FieldValidationError(
                "activity",
                "iso-date",
                "invalid date",
                apiField="iso_date",
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
    organisation_narratives = narratives(
        organisation_narratives_data,
        activity.default_lang,
        activity.id,
        warnings,
        errors,
        "organisation")
    errors = errors + organisation_narratives['errors']
    warnings = warnings + organisation_narratives['warnings']

    department_narratives_data = department.get('narratives', [])
    department_narratives = narratives(
        department_narratives_data,
        activity.default_lang,
        activity.id,
        warnings,
        errors,
        "department")
    errors = errors + department_narratives['errors']
    warnings = warnings + department_narratives['warnings']

    person_name_narratives_data = person_name.get('narratives', [])
    person_name_narratives = narratives(
        person_name_narratives_data,
        activity.default_lang,
        activity.id,
        warnings,
        errors,
        "person_name")
    errors = errors + person_name_narratives['errors']
    warnings = warnings + person_name_narratives['warnings']

    job_title_narratives_data = job_title.get('narratives', [])
    job_title_narratives = narratives(
        job_title_narratives_data,
        activity.default_lang,
        activity.id,
        warnings,
        errors,
        "job_title")
    errors = errors + job_title_narratives['errors']
    warnings = warnings + job_title_narratives['warnings']

    mailing_address_narratives_data = mailing_address.get('narratives', [])
    mailing_address_narratives = narratives(
        mailing_address_narratives_data,
        activity.default_lang,
        activity.id,
        warnings,
        errors,
        "mailing_address")
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
            "organisation_narratives": organisation_narratives[
                'validated_data'
            ],
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
            "mailing_address_narratives": mailing_address_narratives[
                'validated_data'
            ],
        },
    }


def activity_recipient_country(
        activity,
        country_code,
        percentage=0,
        instance=None,  # only set on update
):
    warnings = []
    errors = []

    recipient_country = get_or_none(models.Country, code=country_code)

    if not recipient_country:
        errors.append(
            FieldValidationError(
                "recipient-country",
                "code",
                apiField="country.code",
            ))

    if not isinstance(percentage, int) and not isinstance(percentage, Decimal):
        errors.append(
            RequiredFieldError(
                "recipient-country",
                "percentage",
                apiField="percentage",
            ))

    if percentage < 0 or percentage > 100:
        errors.append(
            FieldValidationError(
                "recipient-country",
                "percentage",
                "percentage must be a value between 0 and 100",
                apiField="percentage",
            ))

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
        instance=None,  # only set on update
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
                apiField="region.code",
            ))
    elif not recipient_region:
        errors.append(
            FieldValidationError(
                "recipient-region",
                "code",
                "recipient-region not found for code {}".format(region_code),
                apiField="region.code",
            ))

    if not vocabulary_code:
        errors.append(
            RequiredFieldError(
                "recipient-region",
                "vocabulary",
                apiField="vocabulary.code",
            ))
    elif not vocabulary:
        errors.append(
            FieldValidationError(
                "recipient-region",
                "vocabulary",
                "vocabulary not found for code {}".format(vocabulary_code),
                apiField="vocabulary.code",
            ))

    if vocabulary_code == "99" and not vocabulary_uri:
        errors.append(
            FieldValidationError(
                "recipient-region",
                "vocabulary_uri",
                "vocabulary_uri is required when vocabulary code is 99",
                apiField="vocabulary_uri",
            ))

    if not isinstance(percentage, int) and not isinstance(percentage, Decimal):
        errors.append(
            FieldValidationError(
                "recipient-region",
                "percentage",
                apiField="percentage",
            ))

    if percentage < 0 or percentage > 100:
        errors.append(
            FieldValidationError(
                "recipient-region",
                "percentage",
                "percentage must be a value between 0 and 100",
                apiField="percentage",
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


def activity__sector(
        activity,
        sector_code,
        vocabulary_code,
        vocabulary_uri,
        percentage=0,
        instance=None,  # only set on update
):
    warnings = []
    errors = []

    sector = get_or_none(models.Sector, code=sector_code)
    vocabulary = get_or_none(models.SectorVocabulary, code=vocabulary_code)

    if not sector_code:
        errors.append(
            RequiredFieldError(
                "sector",
                "code",
                apiField="sector.code",
            ))
    elif not sector:
        errors.append(
            FieldValidationError(
                "sector",
                "code",
                "sector not found for code {}".format(sector_code),
                apiField="sector.code",
            ))

    if not vocabulary_code:
        errors.append(
            RequiredFieldError(
                "sector",
                "vocabulary",
                apiField="vocabulary.code",
            ))
    elif not vocabulary:
        errors.append(
            FieldValidationError(
                "sector",
                "vocabulary",
                "vocabulary not found for code {}".format(vocabulary_code),
                apiField="vocabulary.code",
            ))

    if vocabulary_code == "99" and not vocabulary_uri:
        errors.append(
            FieldValidationError(
                "sector",
                "vocabulary_uri",
                "vocabulary_uri is required when vocabulary code is 99",
                apiField="vocabulary_uri",
            ))

    if not isinstance(percentage, int) and not isinstance(percentage, Decimal):
        errors.append(
            FieldValidationError(
                "sector",
                "percentage",
                apiField="percentage",
            ))

    if percentage < 0 or percentage > 100:
        errors.append(
            FieldValidationError(
                "sector",
                "percentage",
                "percentage must be a value between 0 and 100",
                apiField="percentage",
            ))

    return {
        "warnings": warnings,
        "errors": errors,
        "validated_data": {
            "activity": activity,
            "sector": sector,
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

    location_reach = get_or_none(
        models.GeographicLocationReach, pk=location_reach_code)
    location_id_vocabulary = get_or_none(
        models.GeographicVocabulary,
        pk=location_id_vocabulary_code)
    exactness = get_or_none(models.GeographicExactness, pk=exactness_code)
    location_class = get_or_none(
        models.GeographicLocationClass, pk=location_class_code)
    feature_designation = get_or_none(
        models.LocationType, pk=feature_designation_code)

    if not ref:
        errors.append(
            RequiredFieldError(
                "location",
                "ref",
                apiField="ref",
            ))

    if not exactness_code:
        errors.append(
            RequiredFieldError(
                "location",
                "exactness",
                apiField="exactness.code",
            ))
    elif not exactness:
        errors.append(
            FieldValidationError(
                "location",
                "exactness",
                "codelist entry not found for {}".format(exactness_code),
                apiField="exactness.code",
            ))

    name_narratives = narratives(
        name_narratives_data,
        activity.default_lang,
        activity.id,
        warnings,
        errors,
        "name")
    errors = errors + name_narratives['errors']
    warnings = warnings + name_narratives['warnings']

    description_narratives = narratives(
        description_narratives_data,
        activity.default_lang,
        activity.id,
        warnings,
        errors,
        "description")
    errors = errors + description_narratives['errors']
    warnings = warnings + description_narratives['warnings']

    activity_description_narratives = narratives(
        activity_description_narratives_data,
        activity.default_lang,
        activity.id,
        warnings,
        errors,
        "activity_description")
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
            "name_narratives": name_narratives['validated_data'],
            "description_narratives": description_narratives['validated_data'],
            "activity_description_narratives": activity_description_narratives[
                'validated_data'
            ],
            "point_srs_name": point_srs_name,
            "point_pos": point_pos,
            "exactness": exactness,
            "location_class": location_class,
            "feature_designation": feature_designation,
        },
    }


def activity_humanitarian_scope(
        activity,
        type_code,
        vocabulary_code,
        vocabulary_uri,
        code,
):
    warnings = []
    errors = []

    type = get_or_none(models.HumanitarianScopeType, code=type_code)
    vocabulary = get_or_none(
        models.HumanitarianScopeVocabulary, code=vocabulary_code)

    if not type_code:
        errors.append(
            RequiredFieldError(
                "location",
                "type",
                apiField="type.code",
            ))
    if not type:
        errors.append(
            FieldValidationError(
                "location",
                "type",
                "codelist entry not found for {}".format(type_code),
                apiField="type.code",
            ))
    if not vocabulary_code:
        errors.append(
            RequiredFieldError(
                "location",
                "vocabulary",
                apiField="vocabulary.code",
            ))
    if not vocabulary:
        errors.append(
            FieldValidationError(
                "location",
                "vocabulary",
                "codelist entry not found for {}".format(vocabulary_code),
                apiField="vocabulary.code",
            ))
    if not code:
        errors.append(
            RequiredFieldError(
                "location",
                "code",
                apiField="code",
            ))

    return {
        "warnings": warnings,
        "errors": errors,
        "validated_data": {
            "activity": activity,
            "type": type,
            "vocabulary": vocabulary,
            "vocabulary_uri": vocabulary_uri,
            "code": code,
        },
    }


def activity_policy_marker(
        activity,
        vocabulary_code,
        vocabulary_uri,
        policy_marker_code,
        significance_code,
        narratives_data=[]
):
    warnings = []
    errors = []

    vocabulary = get_or_none(
        models.PolicyMarkerVocabulary, code=vocabulary_code)
    policy_marker = get_or_none(models.PolicyMarker, code=policy_marker_code)
    significance = get_or_none(
        models.PolicySignificance, code=significance_code)

    if not policy_marker_code:
        errors.append(
            RequiredFieldError(
                "policy-marker",
                "code",
                apiField="policy_marker.code",
            ))
    if not policy_marker:
        errors.append(
            FieldValidationError(
                "policy-marker",
                "code",
                "codelist entry not found for {}".format(policy_marker_code),
                apiField="policy_marker.code",
            ))

    if not significance_code:
        errors.append(
            RequiredFieldError(
                "policy-marker",
                "significance",
                apiField="significance.code",
            ))
    if not significance:
        errors.append(
            FieldValidationError(
                "policy-marker",
                "significance",
                "codelist entry not found for {}".format(significance_code),
                apiField="significance.code",
            ))

    if not len(narratives_data):
        errors.append(
            RequiredFieldError(
                "policy-marker",
                "narratives",
                apiField="narratives",
            ))

    validated_narratives = narratives(
        narratives_data,
        activity.default_lang,
        activity.id,
        warnings,
        errors)
    errors = errors + validated_narratives['errors']
    warnings = warnings + validated_narratives['warnings']

    return {
        "warnings": warnings,
        "errors": errors,
        "validated_data": {
            "activity": activity,
            "vocabulary": vocabulary,
            "vocabulary_uri": vocabulary_uri,
            "code": policy_marker,
            "significance": significance,
            "narratives": validated_narratives['validated_data'],
        },
    }


def activity_budget(
        activity,
        type_code,
        status_code,
        period_start_raw,
        period_end_raw,
        value,
        currency_code,
        value_date_raw,
):
    warnings = []
    errors = []

    type = get_or_none(models.BudgetType, code=type_code)
    status = get_or_none(models.BudgetStatus, code=status_code)
    currency = get_or_none(models.Currency, code=currency_code)

    if not type_code:
        errors.append(
            RequiredFieldError(
                "budget",
                "type",
                apiField="type.code",
            ))
    elif not type:
        errors.append(
            FieldValidationError(
                "budget",
                "type",
                "codelist entry not found for {}".format(type_code),
                apiField="type.code",
            ))
    if not status_code:
        errors.append(
            RequiredFieldError(
                "budget",
                "status",
                apiField="status.code",
            ))
    if not status:
        errors.append(
            FieldValidationError(
                "budget",
                "status",
                "codelist entry not found for {}".format(status_code),
                apiField="status.code",
            ))

    if not period_start_raw:
        errors.append(
            RequiredFieldError(
                "budget",
                "period-start",
                apiField="period_start",
            ))
        period_start = None
    else:
        try:
            period_start = validate_date(period_start_raw)
        except RequiredFieldError:
            errors.append(
                FieldValidationError(
                    "budget",
                    "period-start",
                    "iso-date not of type xsd:date",
                    apiField="period_start",
                ))
            period_start = None

    if not period_end_raw:
        errors.append(
            RequiredFieldError(
                "budget",
                "period-end",
                apiField="period_end",
            ))
        period_end = None
    else:
        try:
            period_end = validate_date(period_end_raw)
        except RequiredFieldError:
            errors.append(
                FieldValidationError(
                    "budget",
                    "period-end",
                    "iso-date not of type xsd:date",
                    apiField="period_end",
                ))
            period_end = None

    if not value:
        errors.append(
            RequiredFieldError(
                "budget",
                "value",
                apiField="value",
            ))

    if not value_date_raw:
        errors.append(
            RequiredFieldError(
                "budget",
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
                    "budget",
                    "value-date",
                    "iso-date not of type xsd:date",
                    apiField="value_date",
                ))
            value_date = None

    if not currency and not activity.default_currency:
        errors.append(
            RequiredFieldError(
                "budget",
                "currency",
                "currency not specified and no default specified on activity",
                apiField="currency.code",
            ))

    return {
        "warnings": warnings,
        "errors": errors,
        "validated_data": {
            "activity": activity,
            "type": type,
            "status": status,
            "period_start": period_start,
            "period_end": period_end,
            "value": value,
            "currency": currency,
            "value_date": value_date,
        },
    }


def activity_planned_disbursement(
        activity,
        type_code,
        period_start_raw,
        period_end_raw,
        currency_code,
        value_date_raw,
        value,
        provider_org_ref,
        provider_org_activity_id,
        provider_org_type_code,
        provider_org_narratives_data,
        receiver_org_ref,
        receiver_org_activity_id,
        receiver_org_type_code,
        receiver_org_narratives_data,
):
    warnings = []
    errors = []

    if not provider_org_narratives_data:
        provider_org_narratives_data = []
    if not receiver_org_narratives_data:
        receiver_org_narratives_data = []

    type = get_or_none(models.BudgetType, pk=type_code)
    currency = get_or_none(models.Currency, pk=currency_code)
    provider_org_type = get_or_none(
        models.OrganisationType, pk=provider_org_type_code)
    provider_org_organisation = get_or_none(
        models.Organisation,
        organisation_identifier=provider_org_ref)
    provider_org_activity = get_or_none(
        models.Activity, iati_identifier=provider_org_activity_id)
    receiver_org_type = get_or_none(
        models.OrganisationType, pk=receiver_org_type_code)
    receiver_org_organisation = get_or_none(
        models.Organisation,
        organisation_identifier=receiver_org_ref)
    receiver_org_activity = get_or_none(
        models.Activity,
        pk=receiver_org_activity_id,
    )

    if not type_code:
        errors.append(
            RequiredFieldError(
                "planned-disbursement",
                "type",
                apiField="type.code",
            ))
    if not type:
        errors.append(
            FieldValidationError(
                "planned-disbursement",
                "type",
                "codelist entry not found for {}".format(type_code),
                apiField="type.code",
            ))

    if not period_start_raw:
        errors.append(
            RequiredFieldError(
                "planned-disbursement",
                "period-start",
                apiField="period_start",
            ))
        period_start = None
    else:
        try:
            period_start = validate_date(period_start_raw)
        except RequiredFieldError:
            errors.append(
                FieldValidationError(
                    "planned-disbursement",
                    "period-start",
                    "iso-date not of type xsd:date",
                    apiField="period_start",
                ))
            period_start = None

    if not period_end_raw:
        errors.append(
            RequiredFieldError(
                "planned-disbursement",
                "period-end",
                apiField="period_end",
            ))
        period_end = None
    else:
        try:
            period_end = validate_date(period_end_raw)
        except RequiredFieldError:
            errors.append(
                FieldValidationError(
                    "planned-disbursement",
                    "period-end",
                    "iso-date not of type xsd:date",
                    apiField="period_end",
                ))
            period_end = None

    if not value:
        errors.append(
            RequiredFieldError(
                "planned-disbursement",
                "value",
                apiField="value",
            ))

    if not value_date_raw:
        errors.append(
            RequiredFieldError(
                "planned-disbursement",
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
                    "planned-disbursement",
                    "value-date",
                    "iso-date not of type xsd:date",
                    apiField="last_updated_datetime",
                ))
            value_date = None

    if not currency and not activity.default_currency:
        errors.append(
            RequiredFieldError(
                "planned-disbursement",
                "currency",
                "currency not specified and no default specified on activity",
                apiField="currency.code",
            ))

    # provider-org-ref is set so assume user wants to report it
    if provider_org_ref:
        if not provider_org_activity:
            provider_org_activity = activity

    provider_org_narratives = narratives(
        provider_org_narratives_data,
        activity.default_lang,
        activity.id,
        warnings,
        errors,
        'provider_organisation')
    errors = errors + provider_org_narratives['errors']
    warnings = warnings + provider_org_narratives['warnings']

    receiver_org_narratives = narratives(
        receiver_org_narratives_data,
        activity.default_lang,
        activity.id,
        warnings,
        errors,
        'receiver_organisation')
    errors = errors + receiver_org_narratives['errors']
    warnings = warnings + receiver_org_narratives['warnings']

    return {
        "warnings": warnings,
        "errors": errors,
        "validated_data": {
            "activity": activity,
            "type": type,
            "period_start": period_start,
            "period_end": period_end,
            "currency": currency,
            "value_date": value_date,
            "value": value,
            "provider_org": {
                "ref": provider_org_ref,
                "normalized_ref": provider_org_ref,
                "organisation": provider_org_organisation,
                "provider_activity": provider_org_activity,
                "type": provider_org_type,
            },
            "provider_org_narratives": provider_org_narratives[
                'validated_data'
            ],
            "receiver_org": {
                "ref": receiver_org_ref,
                "normalized_ref": receiver_org_ref,
                "organisation": receiver_org_organisation,
                "receiver_activity": receiver_org_activity,
                "type": receiver_org_type,
            },
            "receiver_org_narratives": receiver_org_narratives[
                'validated_data'
            ],
        },
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
        sector_code,
        sector_vocabulary_code,
        sector_vocabulary_uri,
        recipient_country_code,
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

    transaction_type = get_or_none(
        codelist_models.TransactionType, pk=transaction_type_code)
    currency = get_or_none(models.Currency, pk=currency_code)
    provider_org_type = get_or_none(
        codelist_models.OrganisationType, pk=provider_org_type_code)
    provider_org_organisation = get_or_none(
        models.Organisation,
        organisation_identifier=provider_org_ref)
    provider_org_activity = get_or_none(
        models.Activity, iati_identifier=provider_org_activity_id)
    receiver_org_type = get_or_none(
        models.OrganisationType, pk=receiver_org_type_code)
    receiver_org_organisation = get_or_none(
        models.Organisation,
        organisation_identifier=receiver_org_ref)
    receiver_org_activity = get_or_none(
        models.Activity, iati_identifier=receiver_org_activity_id)
    disbursement_channel = get_or_none(
        models.DisbursementChannel, pk=disbursement_channel_code)
    sector = get_or_none(models.Sector, pk=sector_code)
    sector_vocabulary = get_or_none(
        models.SectorVocabulary, pk=sector_vocabulary_code)
    recipient_country = get_or_none(models.Country, pk=recipient_country_code)
    recipient_region = get_or_none(models.Region, pk=recipient_region_code)
    recipient_region_vocabulary = get_or_none(
        models.RegionVocabulary,
        pk=recipient_region_vocabulary_code)
    flow_type = get_or_none(models.FlowType, pk=flow_type_code)
    finance_type = get_or_none(models.FinanceType, pk=finance_type_code)
    aid_type = get_or_none(models.AidType, pk=aid_type_code)
    tied_status = get_or_none(models.TiedStatus, pk=tied_status_code)

    if humanitarian not in (0, 1):
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
                "codelist entry not found for {}".format(
                    transaction_type_code),
                apiField="transaction_type.code",
            ))

    if not disbursement_channel:
        errors.append(
            FieldValidationError(
                "transaction",
                "disbursement-channel",
                "codelist entry not found for {}".format(
                    disbursement_channel_code),
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

    if sector_code:
        # check if activity is using sector-strategy or transaction-sector
        # strategy
        has_existing_sectors = len(
            models.ActivitySector.objects.filter(activity=activity))

        if has_existing_sectors:
            errors.append(
                RequiredFieldError(
                    "transaction",
                    "sector",
                    "Already provided a sector on activity",
                ))

    if recipient_country_code:
        # check if activity is using recipient_country-strategy or
        # transaction-recipient_country strategy
        has_existing_recipient_countries = len(
            models.ActivityRecipientCountry.objects.filter(
                activity=activity))

        if has_existing_recipient_countries:
            errors.append(
                FieldValidationError(
                    "transaction",
                    "recipient_country",
                    "Already provided a recipient_country on activity",
                    apiField="last_updated_datetime",
                ))

    if recipient_region_code:
        # check if activity is using recipient_region-strategy or
        # transaction-recipient_region strategy
        has_existing_recipient_regions = len(
            models.ActivityRecipientRegion.objects.filter(
                activity=activity))

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

    description_narratives = narratives(
        description_narratives_data,
        activity.default_lang,
        activity.id,
        warnings,
        errors,
        "description")
    errors = errors + description_narratives['errors']
    warnings = warnings + description_narratives['warnings']

    provider_org_narratives = narratives(
        provider_org_narratives_data,
        activity.default_lang,
        activity.id,
        warnings,
        errors,
        "provider_organisation")
    errors = errors + provider_org_narratives['errors']
    warnings = warnings + provider_org_narratives['warnings']

    receiver_org_narratives = narratives(
        receiver_org_narratives_data,
        activity.default_lang,
        activity.id,
        warnings,
        errors,
        "receiver_organisation")
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
            "provider_org_narratives": provider_org_narratives[
                'validated_data'
            ],
            "receiver_org": {
                "ref": receiver_org_ref,
                "normalized_ref": receiver_org_ref,
                "organisation": receiver_org_organisation,
                "receiver_activity": receiver_org_activity,
                "type": receiver_org_type,
            },
            "receiver_org_narratives": receiver_org_narratives[
                'validated_data'
            ],
            "disbursement_channel": disbursement_channel,
            "sector": {
                "sector": sector,
                "vocabulary": sector_vocabulary,
                "vocabulary_uri": sector_vocabulary
            },
            "recipient_country": {
                "country": recipient_country,
            },
            "recipient_region": {
                "region": recipient_region,
                "vocabulary": recipient_region_vocabulary,
                "vocabulary_uri": recipient_region_vocabulary
            },
            "flow_type": flow_type,
            "finance_type": finance_type,
            "aid_type": aid_type,
            "tied_status": tied_status,
        },
    }


def transaction_sector(
        transaction,
        sector_code,
        vocabulary_code,
        vocabulary_uri,
        instance=None,  # only set on update
):
    warnings = []
    errors = []

    sector = get_or_none(models.Sector, code=sector_code)
    vocabulary = get_or_none(models.SectorVocabulary, code=vocabulary_code)

    if not sector_code:
        errors.append(
            RequiredFieldError(
                "recipient-sector",
                "code",
                apiField="sector.code",
            ))
    elif not sector:
        errors.append(
            FieldValidationError(
                "recipient-sector",
                "code",
                "recipient-sector not found for code {}".format(sector_code),
                apiField="sector.code",
            ))

    if not vocabulary_code:
        errors.append(
            RequiredFieldError(
                "recipient-sector",
                "vocabulary",
                apiField="vocabulary.code",
            ))
    elif not vocabulary:
        errors.append(
            FieldValidationError(
                "recipient-sector",
                "vocabulary",
                "vocabulary not found for code {}".format(vocabulary_code),
                apiField="vocabulary.code",
            ))

    if vocabulary_code == "99" and not vocabulary_uri:
        errors.append(
            RequiredFieldError(
                "recipient-sector",
                "vocabulary_uri",
                "vocabulary_uri is required when vocabulary code is 99",
                apiField="vocabulary.code",
            ))

    if sector_code:
        # check if activity is using sector-strategy or transaction-sector
        # strategy
        has_existing_sectors = len(
            models.ActivitySector.objects.filter(activity=activity))

        if has_existing_sectors:
            errors.append(
                FieldValidationError(
                    "transaction",
                    "sector",
                    "Already provided a sector on activity",
                    apiField="sector",
                ))

    return {
        "warnings": warnings,
        "errors": errors,
        "validated_data": {
            "transaction": transaction,
            "sector": sector,
            "vocabulary": vocabulary,
            "vocabulary_uri": vocabulary_uri,
            "percentage": 100,
        },
    }


def activity_result(
        activity,
        type_code,
        aggregation_status,
        title_narratives_data,
        description_narratives_data,
        instance=None,  # only set on update
):
    warnings = []
    errors = []

    if not title_narratives_data:
        title_narratives_data = []
    if not description_narratives_data:
        description_narratives_data = []

    type = get_or_none(models.ResultType, code=type_code)

    if not type_code:
        errors.append(
            RequiredFieldError(
                "result",
                "type",
                apiField="type.code",
            ))
    elif not type:
        errors.append(
            FieldValidationError(
                "result",
                "type",
                "type not found for code {}".format(type_code),
                apiField="type.code",
            ))

    aggregation_status = makeBool(aggregation_status)

    title_narratives = narratives(
        title_narratives_data,
        activity.default_lang,
        activity.id,
        warnings,
        errors,
        'title')
    errors = errors + title_narratives['errors']
    warnings = warnings + title_narratives['warnings']

    description_narratives = narratives(
        description_narratives_data,
        activity.default_lang,
        activity.id,
        warnings,
        errors,
        "title")
    errors = errors + description_narratives['errors']
    warnings = warnings + description_narratives['warnings']

    return {
        "warnings": warnings,
        "errors": errors,
        "validated_data": {
            "activity": activity,
            "type": type,
            "aggregation_status": aggregation_status,
            "title_narratives": title_narratives['validated_data'],
            "description_narratives": description_narratives['validated_data'],
        },
    }


def activity_result_indicator(
        result,
        measure_code,
        ascending,
        title_narratives_data,
        description_narratives_data,
        baseline_year,
        baseline_value,
        baseline_comment_narratives_data,
        instance=None,  # only set on update
):
    warnings = []
    errors = []

    if not title_narratives_data:
        title_narratives_data = []
    if not description_narratives_data:
        description_narratives_data = []
    if not baseline_comment_narratives_data:
        baseline_comment_narratives_data = []

    measure = get_or_none(models.IndicatorMeasure, code=measure_code)

    if not measure_code:
        errors.append(
            RequiredFieldError(
                "indicator",
                "measure",
                apiField="measure.code",
            ))
    elif not measure:
        errors.append(
            FieldValidationError(
                "indicator",
                "measure",
                "measure not found for code {}".format(measure_code),
                apiField="measure.code",
            ))

    if not len(title_narratives_data):
        errors.append(
            RequiredFieldError(
                "indicator",
                "title",
                apiField="title",
            ))

    if baseline_year or baseline_value:
        if not baseline_year:
            errors.append(
                RequiredFieldError(
                    "baseline",
                    "year",
                    apiField="baseline.year",
                ))
        if not baseline_value:
            errors.append(
                RequiredFieldError(
                    "baseline",
                    "value",
                    apiField="baseline.value",
                ))

    ascending = makeBool(ascending)

    title_narratives = narratives(
        title_narratives_data,
        result.activity.default_lang,
        result.activity.id,
        warnings,
        errors,
        "title")
    errors = errors + title_narratives['errors']
    warnings = warnings + title_narratives['warnings']

    description_narratives = narratives(
        description_narratives_data,
        result.activity.default_lang,
        result.activity.id,
        warnings,
        errors,
        "description")
    errors = errors + description_narratives['errors']
    warnings = warnings + description_narratives['warnings']

    baseline_comment_narratives = narratives(
        baseline_comment_narratives_data,
        result.activity.default_lang,
        result.activity.id,
        warnings,
        errors,
        "baseline.comment")
    errors = errors + baseline_comment_narratives['errors']
    warnings = warnings + baseline_comment_narratives['warnings']

    return {
        "warnings": warnings,
        "errors": errors,
        "validated_data": {
            "result": result,
            "measure": measure,
            "ascending": ascending,
            "title_narratives": title_narratives['validated_data'],
            "description_narratives": description_narratives['validated_data'],
            "baseline_year": baseline_year,
            "baseline_value": baseline_value,
            "baseline_comment_narratives": baseline_comment_narratives[
                'validated_data'
            ]
        },
    }


def activity_result_indicator_reference(
        result_indicator,
        vocabulary_code,
        indicator_code,
        indicator_uri,
        instance=None,  # only set on update
):
    warnings = []
    errors = []

    vocabulary = get_or_none(models.IndicatorVocabulary, code=vocabulary_code)

    if not indicator_code:
        errors.append(
            RequiredFieldError(
                "result-indicator-reference",
                "code",
                apiField="code",
            ))

    if not vocabulary_code:
        errors.append(
            RequiredFieldError(
                "result-indicator-reference",
                "vocabulary",
                apiField="vocabulary.code",
            ))
    elif not vocabulary:
        errors.append(
            FieldValidationError(
                "result-indicator-reference",
                "vocabulary",
                "vocabulary not found for code {}".format(vocabulary_code),
                apiField="vocabulary.code",
            ))

    if vocabulary_code == "99" and not indicator_uri:
        errors.append(
            RequiredFieldError(
                "result-indicator-reference",
                "indicator_uri",
                "indicator_uri is required when vocabulary code is 99",
                apiField="vocabulary.code",
            ))

    return {
        "warnings": warnings,
        "errors": errors,
        "validated_data": {
            "result_indicator": result_indicator,
            "code": indicator_code,
            "vocabulary": vocabulary,
            "indicator_uri": indicator_uri,
        },
    }


def activity_result_indicator_period(
        result_indicator,
        target,
        actual,
        period_start_raw,
        period_end_raw,
        target_comment_narratives_data,
        actual_comment_narratives_data,
):
    warnings = []
    errors = []

    if not target_comment_narratives_data:
        target_comment_narratives_data = []
    if not actual_comment_narratives_data:
        actual_comment_narratives_data = []

    if not period_start_raw:
        errors.append(
            RequiredFieldError(
                "result-indicator-period",
                "period-start",
                apiField="period_start",
            ))
        period_start = None
    else:
        try:
            period_start = validate_date(period_start_raw)
        except RequiredFieldError:
            errors.append(
                FieldValidationError(
                    "result-indicator-period",
                    "period-start",
                    "iso-date not of type xsd:date",
                    apiField="period_start",
                ))
            period_start = None

    if not period_end_raw:
        errors.append(
            RequiredFieldError(
                "result-indicator-period",
                "period-end",
                apiField="period_end",
            ))
        period_end = None
    else:
        try:
            period_end = validate_date(period_end_raw)
        except RequiredFieldError:
            errors.append(
                FieldValidationError(
                    "result-indicator-period",
                    "period-end",
                    "iso-date not of type xsd:date",
                    apiField="period_end",
                ))
            period_end = None

    if period_start and period_end:
        if period_start >= period_end:
            errors.append(
                FieldValidationError(
                    "result-indicator-period",
                    "period-start",
                    "period-start must be before period-end",
                    apiField="period_end",
                ))

    if not target:
        errors.append(
            RequiredFieldError(
                "result-indicator-period-target",
                "value",
                apiField="target.value",
            ))
    if not actual:
        errors.append(
            RequiredFieldError(
                "result-indicator-period-actual",
                "value",
                apiField="actual.value",
            ))

    activity = result_indicator.result.activity

    target_comment_narratives = narratives(
        target_comment_narratives_data,
        activity.default_lang,
        activity.id,
        warnings,
        errors,
        "target.comment")
    errors = errors + target_comment_narratives['errors']
    warnings = warnings + target_comment_narratives['warnings']

    actual_comment_narratives = narratives(
        actual_comment_narratives_data,
        activity.default_lang,
        activity.id,
        warnings,
        errors,
        "actual.comment")
    errors = errors + actual_comment_narratives['errors']
    warnings = warnings + actual_comment_narratives['warnings']

    return {
        "warnings": warnings,
        "errors": errors,
        "validated_data": {
            "result_indicator": result_indicator,
            "target": target,
            "actual": actual,
            "period_start": period_start,
            "period_end": period_end,
            "target_comment_narratives": target_comment_narratives[
                'validated_data'
            ],
            "actual_comment_narratives": actual_comment_narratives[
                'validated_data'
            ],
        },
    }


def activity_result_indicator_period_location(
    result_indicator_period,
    ref,
):
    warnings = []
    errors = []

    activity = result_indicator_period.result_indicator.result.activity

    location = get_or_none(models.Location, activity=activity, ref=ref)

    if not ref:
        errors.append(
            RequiredFieldError(
                "result/indicator/period/actual/location",
                "ref",
                apiField="ref",
            ))

    if not location:
        errors.append(
            FieldValidationError(
                "result/indicator/period/actual/location",
                "location with ref {} not found".format(ref),
                apiField="location.code",
            ))

    return {
        "warnings": warnings,
        "errors": errors,
        "validated_data": {
            "result_indicator_period": result_indicator_period,
            "ref": ref,
            "location": location,
        },
    }


def activity_result_indicator_period_dimension(
        result_indicator_period,
        name,
        value,
):
    warnings = []
    errors = []

    if not name:
        errors.append(
            RequiredFieldError(
                "result/indicator/period/actual/dimension",
                "name",
                apiField="name",
            ))

    if not value:
        errors.append(
            RequiredFieldError(
                "result/indicator/period/actual/dimension",
                "value",
                apiField="value",
            ))

    return {
        "warnings": warnings,
        "errors": errors,
        "validated_data": {
            "result_indicator_period": result_indicator_period,
            "name": name,
            "value": value,
        },
    }


def other_identifier(
        activity,
        ref,
        type_code,
        owner_ref,
        narratives_data=[],
):
    warnings = []
    errors = []

    type = get_or_none(codelist_models.OtherIdentifierType, code=type_code)

    if not ref:
        errors.append(
            RequiredFieldError(
                "activity/other-identifier",
                "ref",
                apiField="ref",
            ))

    if not type_code:
        errors.append(
            RequiredFieldError(
                "activity/other-identifier",
                "type",
                apiField="type.code",
            ))
    elif not type:
        errors.append(
            FieldValidationError(
                "activity/other-identifier",
                "type with code {} not found".format(type.code),
                apiField="type.code",
            ))

    if owner_ref:
        pass
        # TODO:  check for valid org id
        # http://iatistandard.org/202/activity-standard/iati-activities/iati-activity/other-identifier/owner-org/
        # - 2016-12-07

    validated_narratives = narratives(
        narratives_data,
        activity.default_lang,
        activity.id,
        warnings,
        errors,
        "owner_org")
    errors = errors + validated_narratives['errors']
    warnings = warnings + validated_narratives['warnings']

    return {
        "warnings": warnings,
        "errors": errors,
        "validated_data": {
            "activity": activity,
            "identifier": ref,
            "type": type,
            "owner_ref": owner_ref,
            "narratives": validated_narratives['validated_data'],
        },
    }


def country_budget_items(
        activity,
        vocabulary_code,
):
    warnings = []
    errors = []

    vocabulary = get_or_none(
        codelist_models.BudgetIdentifierVocabulary, code=vocabulary_code)

    if not vocabulary_code:
        errors.append(
            RequiredFieldError(
                "activity/country-budget-items",
                "vocabulary",
                apiField="vocabulary.code",
            ))
    elif not vocabulary:
        errors.append(
            FieldValidationError(
                "activity/country-budget-items",
                "vocabulary",
                "vocabulary with code {} not found".format(vocabulary_code),
                apiField="vocabulary.code",
            ))

    return {
        "warnings": warnings,
        "errors": errors,
        "validated_data": {
            "activity": activity,
            "vocabulary": vocabulary,
        },
    }


def budget_item(
        country_budget_item,
        budget_identifier_code,
        narratives_data=[],
):
    warnings = []
    errors = []

    budget_identifier = get_or_none(
        codelist_models.BudgetIdentifier, code=budget_identifier_code)

    if not budget_identifier_code:
        errors.append(
            RequiredFieldError(
                "activity/country-budget-items/budget-item",
                "code",
                apiField="budget_identifier.code",
            ))
    elif not budget_identifier:
        errors.append(
            FieldValidationError(
                "activity/country-budget-items/budget-item",
                "code {} not found on BudgetIdentifier codelist".format(
                    budget_identifier_code),
                apiField="budget_identifier.code",
            ))

    # TODO: validate something with percentage here? - 2016-12-08

    validated_narratives = narratives(
        narratives_data,
        country_budget_item.activity.default_lang,
        country_budget_item.activity.id,
        warnings,
        errors,
        "description")
    errors = errors + validated_narratives['errors']
    warnings = warnings + validated_narratives['warnings']

    return {
        "warnings": warnings,
        "errors": errors,
        "validated_data": {
            "country_budget_item": country_budget_item,
            "code": budget_identifier,
            "narratives": validated_narratives['validated_data'],
        },
    }


def legacy_data(
        activity,
        name,
        value,
        iati_equivalent
):
    warnings = []
    errors = []

    if not name:
        errors.append(
            RequiredFieldError(
                "activity/legacy-data",
                "name",
                apiField="name",
            ))
    if not value:
        errors.append(
            RequiredFieldError(
                "activity/legacy-data",
                "value",
                apiField="value",
            ))

    return {
        "warnings": warnings,
        "errors": errors,
        "validated_data": {
            "activity": activity,
            "name": name,
            "value": value,
            "iati_equivalent": iati_equivalent,
        },
    }


def conditions(
        activity,
        attached,
):
    warnings = []
    errors = []

    if not attached:
        errors.append(
            RequiredFieldError(
                "activity/conditions",
                "attached",
                apiField="attached",
            ))
    return {
        "warnings": warnings,
        "errors": errors,
        "validated_data": {
            "activity": activity,
            "attached": attached,
        },
    }


def condition(
        conditions,
        type_code,
        narratives_data=[],
):
    warnings = []
    errors = []

    type = get_or_none(codelist_models.ConditionType, code=type_code)

    if not type_code:
        errors.append(
            RequiredFieldError(
                "activity/conditions/condition",
                "type",
                apiField="type.code",
            ))
    elif not type:
        errors.append(
            FieldValidationError(
                "activity/conditions/condition",
                "code {} not found on ConditionType codelist".format(
                    type_code),
                apiField="type.code",
            ))

    validated_narratives = narratives(
        narratives_data,
        conditions.activity.default_lang,
        conditions.activity.id,
        warnings,
        errors)
    errors = errors + validated_narratives['errors']
    warnings = warnings + validated_narratives['warnings']

    return {
        "warnings": warnings,
        "errors": errors,
        "validated_data": {
            "conditions": conditions,
            "type": type,
            "narratives": validated_narratives['validated_data'],
        },
    }


def crs_add(
        activity,
        channel_code,
):
    warnings = []
    errors = []

    return {
        "warnings": warnings,
        "errors": errors,
        "validated_data": {
            "activity": activity,
            "channel_code": channel_code,
        },
    }


def crs_add_loan_terms(
        activity,
        rate_1,
        rate_2,
        repayment_type_code,
        repayment_period_code,
        commitment_date_raw,
        repayment_first_date_raw,
        repayment_final_date_raw,
):
    warnings = []
    errors = []

    repayment_type = get_or_none(
        codelist_models.LoanRepaymentType, code=repayment_type_code)
    repayment_period = get_or_none(
        codelist_models.LoanRepaymentPeriod, code=repayment_period_code)

    if not rate_1:
        errors.append(
            RequiredFieldError(
                "activity/crs_add/loan_terms",
                "rate_1",
                apiField="loan_terms.rate_1",
            ))
    if not rate_2:
        errors.append(
            RequiredFieldError(
                "activity/crs_add/loan_terms",
                "rate_2",
                apiField="loan_terms.rate_2",
            ))

    try:
        commitment_date = validate_date(commitment_date_raw)
    except RequiredFieldError:
        errors.append(
            FieldValidationError(
                "activity/crs_add/loan_terms",
                "commitment_date",
                "invalid date",
                apiField="loan_terms.commitment_date",
            ))
        commitment_date = None

    try:
        repayment_first_date = validate_date(repayment_first_date_raw)
    except RequiredFieldError:
        errors.append(
            FieldValidationError(
                "activity/crs_add/loan_terms",
                "repayment_first_date",
                "invalid date",
                apiField="loan_terms.repayment_first_date",
            ))
        repayment_first_date = None

    try:
        repayment_final_date = validate_date(repayment_final_date_raw)
    except RequiredFieldError:
        errors.append(
            FieldValidationError(
                "activity/crs_add/loan_terms",
                "repayment_final_date",
                "invalid date",
                apiField="loan_terms.repayment_final_date",
            ))
        repayment_final_date = None

    return {
        "warnings": warnings,
        "errors": errors,
        "validated_data": {
            "loan_terms": {
                "rate_1": rate_1,
                "rate_2": rate_2,
                "repayment_type": repayment_type,
                "repayment_plan": repayment_period,
                "commitment_date": commitment_date,
                "repayment_first_date": repayment_first_date,
                "repayment_final_date": repayment_final_date,
            }
        },
    }


def crs_add_loan_status(
        activity,
        year,
        currency_code,
        value_date_raw,
        interest_received,
        principal_outstanding,
        principal_arrears,
        interest_arrears,
):
    warnings = []
    errors = []

    currency = get_or_none(models.Currency, code=currency_code)

    if not year:
        errors.append(
            RequiredFieldError(
                "activity/crs_add/loan_status",
                "year",
                apiField="loan_status.year",
            ))

    try:
        value_date = validate_date(value_date_raw)
    except RequiredFieldError:
        errors.append(
            FieldValidationError(
                "activity/crs_add/loan_status",
                "value_date",
                "invalid date",
                apiField="loan_status.value_date",
            ))
        value_date = None

    return {
        "warnings": warnings,
        "errors": errors,
        "validated_data": {
            "loan_status": {
                "year": year,
                "currency": currency,
                "value_date": value_date,
                "interest_received": interest_received,
                "principal_outstanding": principal_outstanding,
                "principal_arrears": principal_arrears,
                "interest_arrears": interest_arrears,
            }
        },
    }


def crs_add_other_flags(
        crs_add,
        other_flags_code,
        significance,
):
    warnings = []
    errors = []

    other_flags = get_or_none(models.OtherFlags, code=other_flags_code)

    if not other_flags_code:
        errors.append(
            RequiredFieldError(
                "activity/crs_add/other_flags",
                "other_flags",
                apiField="other_flags.code",
            ))
    elif not other_flags:
        errors.append(
            FieldValidationError(
                "activity/crs_add/other_flags",
                "code {} not found on OtherFlags codelist".format(other_flags),
                apiField="other_flags.code",
            ))

    if not significance:
        errors.append(
            RequiredFieldError(
                "activity/crs_add/other_flags",
                "significance",
                apiField="significance",
            ))

    return {
        "warnings": warnings,
        "errors": errors,
        "validated_data": {
            "crs_add": crs_add,
            "other_flags": other_flags,
            "significance": significance,
        },
    }


def fss(
        activity,
        extraction_date_raw,
        priority,
        phaseout_year
):
    warnings = []
    errors = []

    try:
        extraction_date = validate_date(extraction_date_raw)
    except RequiredFieldError:
        errors.append(
            FieldValidationError(
                "activity/fss",
                "extraction_date",
                "invalid date",
                apiField="extraction_date",
            ))
        extraction_date = None

    return {
        "warnings": warnings,
        "errors": errors,
        "validated_data": {
            "activity": activity,
            "extraction_date": extraction_date,
            "priority": priority,
            "phaseout_year": phaseout_year,
        },
    }


def fss_forecast(
        fss,
        year,
        value_date_raw,
        currency_code,
        value,
):
    warnings = []
    errors = []

    currency = get_or_none(models.Currency, code=currency_code)

    try:
        value_date = validate_date(value_date_raw)
    except RequiredFieldError:
        if not value:
            errors.append(
                FieldValidationError(
                    "activity/fss/forecast",
                    "value",
                    apiField="value",
                ))

        value_date = None

    if not currency and not fss.activity.default_currency:
        errors.append(
            FieldValidationError(
                "activity/fss/forecast",
                "currency",
                "currency not specified and no default specified on activity",
                apiField="currency.code",
            ))

    if not year:
        errors.append(
            RequiredFieldError(
                "activity/fss/forecast",
                "year",
                apiField="currency.code",
            ))

    if not value:
        errors.append(
            RequiredFieldError(
                "activity/fss/forecast",
                "value",
                apiField="value",
            ))

    return {
        "warnings": warnings,
        "errors": errors,
        "validated_data": {
            "fss": fss,
            "year": year,
            "value_date": value_date,
            "currency": currency,
            "value": value,
        },
    }


# def related_activity(
        # fss,
        # year,
        # value_date_raw,
        # currency_code,
        # value,
# ):
    # warnings = []
    # errors = []

    # currency = get_or_none(models.Currency, code=currency_code)

    # try:
        # value_date = validate_date(value_date_raw)
    # except RequiredFieldError:
        # if not value:
            # errors.append(
                # FieldValidationError(
                    # "activity/fss/forecast",
                    # "value",
                    # apiField="value",
                # ))

        # value_date = None

    # if not currency and not fss.activity.default_currency:
        # errors.append(
            # FieldValidationError(
                # "activity/fss/forecast",
                # "currency",
                # "currency not specified and no default specified on activity",
                # apiField="currency.code",
            # ))

    # if not year:
        # errors.append(
            # RequiredFieldError(
                # "activity/fss/forecast",
                # "year",
                # apiField="year",
            # ))

    # if not value:
        # errors.append(
            # RequiredFieldError(
                # "activity/fss/forecast",
                # "value",
                # apiField="value",
            # ))

    # return {
        # "warnings": warnings,
        # "errors": errors,
        # "validated_data": {
            # "fss": fss,
            # "year": year,
            # "value_date": value_date,
            # "currency": currency,
            # "value": value,
        # },
    # }


def related_activity(
        activity,
        ref,
        type_code,
):
    warnings = []
    errors = []

    type = get_or_none(models.RelatedActivityType, code=type_code)
    ref_activity = get_or_none(models.Activity, pk=ref)

    if not ref:
        errors.append(
            RequiredFieldError(
                "related-activity",
                "ref",
                apiField="ref",
            ))
    elif not ref_activity:
        errors.append(
            FieldValidationError(
                "related-activity",
                "ref",
                "activity not found for {}".format(type_code),
                apiField="ref",
            ))

    if not type_code:
        errors.append(
            RequiredFieldError(
                "related-activity",
                "type",
                apiField="type.code",
            ))
    elif not type:
        errors.append(
            FieldValidationError(
                "related-activity",
                "type",
                "codelist entry not found for {}".format(type_code),
                apiField="type.code",
            ))

    return {
        "warnings": warnings,
        "errors": errors,
        "validated_data": {
            "current_activity": activity,
            "ref_activity": ref_activity,
            "ref": ref,
            "type": type,
        },
    }


def activity_document_link(
        activity,
        url,
        file_format_code,
        document_date_raw,
        title_narratives_data,
):
    warnings = []
    errors = []

    if not title_narratives_data:
        title_narratives_data = []

    file_format = get_or_none(models.FileFormat, code=file_format_code)

    if not file_format_code:
        errors.append(
            RequiredFieldError(
                "activity/document-link",
                "file-format",
                apiField="file_format.code",
            ))
    elif not file_format:
        errors.append(
            FieldValidationError(
                "activity/document-link",
                "file-format",
                "format not found for code {}".format(file_format_code),
                apiField="file_format.code",
            ))

    # TODO: check the url actually resolves? - 2016-12-14
    if not url:
        errors.append(
            RequiredFieldError(
                "document_link",
                "url",
                apiField="url",
            ))

    try:
        document_date = validate_date(document_date_raw)
    except RequiredFieldError:

        document_date = None

    title_narratives = narratives(
        title_narratives_data,
        activity.default_lang,
        activity.id,
        warnings,
        errors,
        "title")
    errors = errors + title_narratives['errors']
    warnings = warnings + title_narratives['warnings']

    return {
        "warnings": warnings,
        "errors": errors,
        "validated_data": {
            "activity": activity,
            "url": url,
            "file_format": file_format,
            "title_narratives": title_narratives['validated_data'],
            "iso_date": document_date,
        },
    }


def document_link_category(
        document_link,
        category_code,
):
    warnings = []
    errors = []

    category = get_or_none(models.DocumentCategory, code=category_code)

    if not category_code:
        errors.append(
            RequiredFieldError(
                "activity/document-link/category",
                "code",
                apiField="category.code",
            ))
    elif not category:
        errors.append(
            FieldValidationError(
                "activity/document-link/category",
                "code",
                "category not found for code {}".format(category_code),
                apiField="category.code",
            ))

    return {
        "warnings": warnings,
        "errors": errors,
        "validated_data": {
            "document_link": document_link,
            "category": category,
        },
    }


def document_link_language(
        document_link,
        language_code,
):
    warnings = []
    errors = []

    language = get_or_none(models.Language, code=language_code)

    if not language_code:
        errors.append(
            RequiredFieldError(
                "activity/document-link/language",
                "code",
                apiField="language.code",
            ))
    elif not language:
        errors.append(
            FieldValidationError(
                "activity/document-link/language",
                "code",
                "language not found for code {}".format(language_code),
                apiField="language.code",
            ))

    return {
        "warnings": warnings,
        "errors": errors,
        "validated_data": {
            "document_link": document_link,
            "language": language,
        },
    }
