import re
from iati import models
from iati.transaction import models as transaction_models
from iati_codelists import models as codelist_models
from iati_vocabulary import models as vocabulary_models
from iati_organisation import models as organisation_models
import dateutil.parser
from datetime import datetime
from decimal import Decimal
from iati_synchroniser.models import Publisher

from iati.parser.exceptions import *

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
    # except model.DoesNotExist:
    #     return default

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

iati_regex = re.compile(r'^[^\/\&\|\?]*$')
def validate_organisation_identifier(iati_identifier):
    if iati_regex.match(iati_identifier):
        return True
    else:
        return False


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

def narratives_validate(narratives, default_lang, activity_id, warnings=[], errors=[], apiField=""):
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


def organisation(
        organisation_identifier,
        default_lang,
        default_currency,
        name={},
        iati_standard_version="2.02",
        published=False,
        ):

        warnings = []
        errors = []

        default_currency = get_or_none(models.Currency, pk=default_currency)
        iati_standard_version = get_or_none(models.Version, pk=iati_standard_version)
        default_lang = get_or_none(models.Language, pk=default_lang)

        if not default_lang:
            warnings.append(
                RequiredFieldError(
                    "organisation",
                    "default-lang",
                    apiField="default_lang",
                    ))


        if not validate_organisation_identifier(organisation_identifier):
            errors.append(
                FieldValidationError(
                    "organisation",
                    "organisation-identifier",
                    apiField="organisation_identifier",
                    ))

        name_narratives = name.get('narratives', [])
        # if not len(name_narratives):
        #     errors.append(
        #         RequiredFieldError(
        #             "organisation",
        #             "name__narratives",
        #             ))

        name_narratives = narratives_validate(name_narratives, default_lang, None,  warnings, errors, "name")
        errors = errors + name_narratives['errors']
        warnings = warnings + name_narratives['warnings']

        return {
            "warnings": warnings,
            "errors": errors,
            "validated_data": {
                "organisation_identifier": organisation_identifier,
                "normalized_organisation_identifier": organisation_identifier,
                "default_lang": default_lang,
                "default_currency": default_currency,
                "iati_standard_version": iati_standard_version,
                "published": published,
                "name": {
                },
                "name_narratives": name_narratives['validated_data'],
            },
        }

def organisation_total_budget(
        organisation,
        status_code,
        period_start_raw,
        period_end_raw,
        value,
        currency_code,
        value_date_raw,
        ):
        warnings = []
        errors = []

        status = get_or_none(models.BudgetStatus, code=status_code)
        currency = get_or_none(models.Currency, code=currency_code)

        if not status_code:
            errors.append(
                RequiredFieldError(
                    "total-budget",
                    "status",
                    apiField="status.code",
                    ))
        if not status:
            errors.append(
                FieldValidationError(
                    "total-budget",
                    "status",
                    "codelist entry not found for {}".format(status_code),
                    apiField="status.code",
                    ))

        if not period_start_raw:
            errors.append(
                RequiredFieldError(
                    "total-budget",
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
                        "total-budget",
                        "period-start",
                        "iso-date not of type xsd:date",
                        apiField="period_start",
                        ))
                period_start = None

        if not period_end_raw:
            errors.append(
                RequiredFieldError(
                    "total-budget",
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
                        "total-budget",
                        "period-end",
                        "iso-date not of type xsd:date",
                        apiField="period_end",
                        ))
                period_end = None

        if not value:
            errors.append(
                RequiredFieldError(
                    "total-budget",
                    "value",
                    apiField="value",
                    ))


        if not value_date_raw:
            errors.append(
                RequiredFieldError(
                    "total-budget",
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
                        "total-budget",
                        "value-date",
                        "iso-date not of type xsd:date",
                        apiField="value_date",
                        ))
                value_date = None

        if not currency and not organisation.default_currency:
            errors.append(
                RequiredFieldError(
                    "total-budget",
                    "currency",
                    "currency not specified and no default specified on organisation",
                    apiField="currency.code",
                    ))

        return {
            "warnings": warnings,
            "errors": errors,
            "validated_data": {
                "organisation": organisation,
                "status": status,
                "period_start": period_start,
                "period_end": period_end,
                "value": value,
                "currency": currency,
                "value_date": value_date,
            },
        }

def organisation_total_budget_line(
        total_budget,
        ref,
        value,
        currency_code,
        value_date_raw,
        narratives_data,
        ):
        warnings = []
        errors = []

        if not narratives_data:
            narratives_data = []

        currency = get_or_none(models.Currency, code=currency_code)

        if not value:
            errors.append(
                RequiredFieldError(
                    "total-budget/budget-line",
                    "value",
                    apiField="value",
                    ))


        if not value_date_raw:
            errors.append(
                RequiredFieldError(
                    "total-budget/budget-line",
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
                        "total-budget/budget-line",
                        "value-date",
                        "iso-date not of type xsd:date",
                        apiField="value_date",
                        ))
                value_date = None

        if not currency and not total_budget.organisation.default_currency:
            errors.append(
                RequiredFieldError(
                    "total-budget/budget-line",
                    "currency",
                    "currency not specified and no default specified on organisation",
                    apiField="currency.code",
                    ))

        narratives = narratives_validate(narratives_data, total_budget.organisation.default_lang, total_budget.organisation.id,  warnings, errors, "total-budget/budget-line")
        errors = errors + narratives['errors']
        warnings = warnings + narratives['warnings']

        return {
            "warnings": warnings,
            "errors": errors,
            "validated_data": {
                "total_budget": total_budget,
                "ref": ref,
                "value": value,
                "currency": currency,
                "value_date": value_date,
                "narratives": narratives['validated_data'],
            },
        }


def organisation_recipient_org_budget(
        organisation,
        status_code,
        recipient_org_identifier,
        period_start_raw,
        period_end_raw,
        value,
        currency_code,
        value_date_raw,
        ):
        warnings = []
        errors = []

        status = get_or_none(models.BudgetStatus, code=status_code)
        currency = get_or_none(models.Currency, code=currency_code)
        recipient_org = get_or_none(organisation_models.Organisation, pk=recipient_org_identifier)

        if not status_code:
            errors.append(
                RequiredFieldError(
                    "recipient-org-budget",
                    "status",
                    apiField="status.code",
                    ))
        if not status:
            errors.append(
                FieldValidationError(
                    "recipient-org-budget",
                    "status",
                    "codelist entry not found for {}".format(status_code),
                    apiField="status.code",
                    ))

        if not recipient_org_identifier:
            errors.append(
                RequiredFieldError(
                    "recipient-org-identifier",
                    "recipient_org",
                    apiField="recipient_org.code",
                    ))
        # TODO: require that the org is in iati? - 2017-03-14
        # if not recipient_org:
        #     errors.append(
        #         FieldValidationError(
        #             "recipient-org-budget",
        #             "recipient_org",
        #             "codelist entry not found for {}".format(recipient_org_identifier),
        #             apiField="recipient_org.code",
        #             ))

        if not period_start_raw:
            errors.append(
                RequiredFieldError(
                    "recipient-org-budget",
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
                        "recipient-org-budget",
                        "period-start",
                        "iso-date not of type xsd:date",
                        apiField="period_start",
                        ))
                period_start = None

        if not period_end_raw:
            errors.append(
                RequiredFieldError(
                    "recipient-org-budget",
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
                        "recipient-org-budget",
                        "period-end",
                        "iso-date not of type xsd:date",
                        apiField="period_end",
                        ))
                period_end = None

        if not value:
            errors.append(
                RequiredFieldError(
                    "recipient-org-budget",
                    "value",
                    apiField="value",
                    ))


        if not value_date_raw:
            errors.append(
                RequiredFieldError(
                    "recipient-org-budget",
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
                        "recipient-org-budget",
                        "value-date",
                        "iso-date not of type xsd:date",
                        apiField="value_date",
                        ))
                value_date = None

        if not currency and not organisation.default_currency:
            errors.append(
                RequiredFieldError(
                    "recipient-org-budget",
                    "currency",
                    "currency not specified and no default specified on organisation",
                    apiField="currency.code",
                    ))

        return {
            "warnings": warnings,
            "errors": errors,
            "validated_data": {
                "organisation": organisation,
                "status": status,
                "recipient_org_identifier": recipient_org_identifier,
                "recipient_org": recipient_org,
                "period_start": period_start,
                "period_end": period_end,
                "value": value,
                "currency": currency,
                "value_date": value_date,
            },
        }

def organisation_recipient_org_budget_line(
        recipient_org_budget,
        ref,
        value,
        currency_code,
        value_date_raw,
        narratives_data,
        ):
        warnings = []
        errors = []

        if not narratives_data:
            narratives_data = []

        currency = get_or_none(models.Currency, code=currency_code)

        if not value:
            errors.append(
                RequiredFieldError(
                    "total-budget/budget-line",
                    "value",
                    apiField="value",
                    ))


        if not value_date_raw:
            errors.append(
                RequiredFieldError(
                    "total-budget/budget-line",
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
                        "total-budget/budget-line",
                        "value-date",
                        "iso-date not of type xsd:date",
                        apiField="value_date",
                        ))
                value_date = None

        if not currency and not recipient_org_budget.organisation.default_currency:
            errors.append(
                RequiredFieldError(
                    "total-budget/budget-line",
                    "currency",
                    "currency not specified and no default specified on organisation",
                    apiField="currency.code",
                    ))

        narratives = narratives_validate(narratives_data, recipient_org_budget.organisation.default_lang, recipient_org_budget.organisation.id,  warnings, errors, "total-budget/budget-line")
        errors = errors + narratives['errors']
        warnings = warnings + narratives['warnings']

        return {
            "warnings": warnings,
            "errors": errors,
            "validated_data": {
                "recipient_org_budget": recipient_org_budget,
                "ref": ref,
                "value": value,
                "currency": currency,
                "value_date": value_date,
                "narratives": narratives['validated_data'],
            },
        }

def organisation_recipient_country_budget(
        organisation,
        status_code,
        country_code,
        period_start_raw,
        period_end_raw,
        value,
        currency_code,
        value_date_raw,
        ):
        warnings = []
        errors = []

        status = get_or_none(models.BudgetStatus, code=status_code)
        currency = get_or_none(models.Currency, code=currency_code)
        country = get_or_none(models.Country, code=country_code)

        if not status_code:
            errors.append(
                RequiredFieldError(
                    "recipient-org-budget",
                    "status",
                    apiField="status.code",
                    ))
        if not status:
            errors.append(
                FieldValidationError(
                    "recipient-org-budget",
                    "status",
                    "codelist entry not found for {}".format(status_code),
                    apiField="status.code",
                    ))

        if not country_code:
            errors.append(
                RequiredFieldError(
                    "recipient-org-budget",
                    "country",
                    apiField="country.code",
                    ))
        if not country:
            errors.append(
                FieldValidationError(
                    "recipient-org-budget",
                    "country",
                    "codelist entry not found for {}".format(country_code),
                    apiField="country.code",
                    ))


        if not period_start_raw:
            errors.append(
                RequiredFieldError(
                    "recipient-org-budget",
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
                        "recipient-org-budget",
                        "period-start",
                        "iso-date not of type xsd:date",
                        apiField="period_start",
                        ))
                period_start = None

        if not period_end_raw:
            errors.append(
                RequiredFieldError(
                    "recipient-org-budget",
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
                        "recipient-org-budget",
                        "period-end",
                        "iso-date not of type xsd:date",
                        apiField="period_end",
                        ))
                period_end = None

        if not value:
            errors.append(
                RequiredFieldError(
                    "recipient-org-budget",
                    "value",
                    apiField="value",
                    ))


        if not value_date_raw:
            errors.append(
                RequiredFieldError(
                    "recipient-org-budget",
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
                        "recipient-org-budget",
                        "value-date",
                        "iso-date not of type xsd:date",
                        apiField="value_date",
                        ))
                value_date = None

        if not currency and not organisation.default_currency:
            errors.append(
                RequiredFieldError(
                    "recipient-org-budget",
                    "currency",
                    "currency not specified and no default specified on organisation",
                    apiField="currency.code",
                    ))

        return {
            "warnings": warnings,
            "errors": errors,
            "validated_data": {
                "organisation": organisation,
                "status": status,
                "country": country,
                "period_start": period_start,
                "period_end": period_end,
                "value": value,
                "currency": currency,
                "value_date": value_date,
            },
        }

def organisation_recipient_country_budget_line(
        recipient_country_budget,
        ref,
        value,
        currency_code,
        value_date_raw,
        narratives_data,
        ):
        warnings = []
        errors = []

        if not narratives_data:
            narratives_data = []

        currency = get_or_none(models.Currency, code=currency_code)

        if not value:
            errors.append(
                RequiredFieldError(
                    "total-budget/budget-line",
                    "value",
                    apiField="value",
                    ))


        if not value_date_raw:
            errors.append(
                RequiredFieldError(
                    "total-budget/budget-line",
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
                        "total-budget/budget-line",
                        "value-date",
                        "iso-date not of type xsd:date",
                        apiField="value_date",
                        ))
                value_date = None

        if not currency and not recipient_country_budget.organisation.default_currency:
            errors.append(
                RequiredFieldError(
                    "total-budget/budget-line",
                    "currency",
                    "currency not specified and no default specified on organisation",
                    apiField="currency.code",
                    ))

        narratives = narratives_validate(narratives_data, recipient_country_budget.organisation.default_lang, recipient_country_budget.organisation.id,  warnings, errors, "total-budget/budget-line")
        errors = errors + narratives['errors']
        warnings = warnings + narratives['warnings']

        return {
            "warnings": warnings,
            "errors": errors,
            "validated_data": {
                "recipient_country_budget": recipient_country_budget,
                "ref": ref,
                "value": value,
                "currency": currency,
                "value_date": value_date,
                "narratives": narratives['validated_data'],
            },
        }

def organisation_recipient_region_budget(
        organisation,
        status_code,
        region_code,
        period_start_raw,
        period_end_raw,
        value,
        currency_code,
        value_date_raw,
        ):
        warnings = []
        errors = []

        status = get_or_none(models.BudgetStatus, code=status_code)
        currency = get_or_none(models.Currency, code=currency_code)
        region = get_or_none(models.Region, code=region_code)

        if not status_code:
            errors.append(
                RequiredFieldError(
                    "recipient-org-budget",
                    "status",
                    apiField="status.code",
                    ))
        if not status:
            errors.append(
                FieldValidationError(
                    "recipient-org-budget",
                    "status",
                    "codelist entry not found for {}".format(status_code),
                    apiField="status.code",
                    ))

        if not region_code:
            errors.append(
                RequiredFieldError(
                    "recipient-org-budget",
                    "region",
                    apiField="region.code",
                    ))
        if not region:
            errors.append(
                FieldValidationError(
                    "recipient-org-budget",
                    "region",
                    "codelist entry not found for {}".format(region_code),
                    apiField="region.code",
                    ))


        if not period_start_raw:
            errors.append(
                RequiredFieldError(
                    "recipient-org-budget",
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
                        "recipient-org-budget",
                        "period-start",
                        "iso-date not of type xsd:date",
                        apiField="period_start",
                        ))
                period_start = None

        if not period_end_raw:
            errors.append(
                RequiredFieldError(
                    "recipient-org-budget",
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
                        "recipient-org-budget",
                        "period-end",
                        "iso-date not of type xsd:date",
                        apiField="period_end",
                        ))
                period_end = None

        if not value:
            errors.append(
                RequiredFieldError(
                    "recipient-org-budget",
                    "value",
                    apiField="value",
                    ))


        if not value_date_raw:
            errors.append(
                RequiredFieldError(
                    "recipient-org-budget",
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
                        "recipient-org-budget",
                        "value-date",
                        "iso-date not of type xsd:date",
                        apiField="value_date",
                        ))
                value_date = None

        if not currency and not organisation.default_currency:
            errors.append(
                RequiredFieldError(
                    "recipient-org-budget",
                    "currency",
                    "currency not specified and no default specified on organisation",
                    apiField="currency.code",
                    ))

        return {
            "warnings": warnings,
            "errors": errors,
            "validated_data": {
                "organisation": organisation,
                "status": status,
                "region": region,
                "period_start": period_start,
                "period_end": period_end,
                "value": value,
                "currency": currency,
                "value_date": value_date,
            },
        }

def organisation_recipient_region_budget_line(
        recipient_region_budget,
        ref,
        value,
        currency_code,
        value_date_raw,
        narratives_data,
        ):
        warnings = []
        errors = []

        if not narratives_data:
            narratives_data = []

        currency = get_or_none(models.Currency, code=currency_code)

        if not value:
            errors.append(
                RequiredFieldError(
                    "total-budget/budget-line",
                    "value",
                    apiField="value",
                    ))


        if not value_date_raw:
            errors.append(
                RequiredFieldError(
                    "total-budget/budget-line",
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
                        "total-budget/budget-line",
                        "value-date",
                        "iso-date not of type xsd:date",
                        apiField="value_date",
                        ))
                value_date = None

        if not currency and not recipient_region_budget.organisation.default_currency:
            errors.append(
                RequiredFieldError(
                    "total-budget/budget-line",
                    "currency",
                    "currency not specified and no default specified on organisation",
                    apiField="currency.code",
                    ))

        narratives = narratives_validate(narratives_data, recipient_region_budget.organisation.default_lang, recipient_region_budget.organisation.id,  warnings, errors, "total-budget/budget-line")
        errors = errors + narratives['errors']
        warnings = warnings + narratives['warnings']

        return {
            "warnings": warnings,
            "errors": errors,
            "validated_data": {
                "recipient_region_budget": recipient_region_budget,
                "ref": ref,
                "value": value,
                "currency": currency,
                "value_date": value_date,
                "narratives": narratives['validated_data'],
            },
        }


def organisation_total_expenditure(
        organisation,
        period_start_raw,
        period_end_raw,
        value,
        currency_code,
        value_date_raw,
        ):
        warnings = []
        errors = []

        currency = get_or_none(models.Currency, code=currency_code)

        if not period_start_raw:
            errors.append(
                RequiredFieldError(
                    "recipient-org-budget",
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
                        "recipient-org-budget",
                        "period-start",
                        "iso-date not of type xsd:date",
                        apiField="period_start",
                        ))
                period_start = None

        if not period_end_raw:
            errors.append(
                RequiredFieldError(
                    "recipient-org-budget",
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
                        "recipient-org-budget",
                        "period-end",
                        "iso-date not of type xsd:date",
                        apiField="period_end",
                        ))
                period_end = None

        if not value:
            errors.append(
                RequiredFieldError(
                    "recipient-org-budget",
                    "value",
                    apiField="value",
                    ))


        if not value_date_raw:
            errors.append(
                RequiredFieldError(
                    "recipient-org-budget",
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
                        "recipient-org-budget",
                        "value-date",
                        "iso-date not of type xsd:date",
                        apiField="value_date",
                        ))
                value_date = None

        if not currency and not organisation.default_currency:
            errors.append(
                RequiredFieldError(
                    "recipient-org-budget",
                    "currency",
                    "currency not specified and no default specified on organisation",
                    apiField="currency.code",
                    ))

        return {
            "warnings": warnings,
            "errors": errors,
            "validated_data": {
                "organisation": organisation,
                "period_start": period_start,
                "period_end": period_end,
                "value": value,
                "currency": currency,
                "value_date": value_date,
            },
        }


def organisation_total_expenditure_line(
        total_expenditure,
        ref,
        value,
        currency_code,
        value_date_raw,
        narratives_data,
        ):
        warnings = []
        errors = []

        if not narratives_data:
            narratives_data = []

        currency = get_or_none(models.Currency, code=currency_code)

        if not value:
            errors.append(
                RequiredFieldError(
                    "total-budget/budget-line",
                    "value",
                    apiField="value",
                    ))


        if not value_date_raw:
            errors.append(
                RequiredFieldError(
                    "total-budget/budget-line",
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
                        "total-budget/budget-line",
                        "value-date",
                        "iso-date not of type xsd:date",
                        apiField="value_date",
                        ))
                value_date = None

        if not currency and not total_expenditure.organisation.default_currency:
            errors.append(
                RequiredFieldError(
                    "total-budget/budget-line",
                    "currency",
                    "currency not specified and no default specified on organisation",
                    apiField="currency.code",
                    ))

        narratives = narratives_validate(narratives_data, total_expenditure.organisation.default_lang, total_expenditure.organisation.id,  warnings, errors, "total-budget/budget-line")
        errors = errors + narratives['errors']
        warnings = warnings + narratives['warnings']

        return {
            "warnings": warnings,
            "errors": errors,
            "validated_data": {
                "total_expenditure": total_expenditure,
                "ref": ref,
                "value": value,
                "currency": currency,
                "value_date": value_date,
                "narratives": narratives['validated_data'],
            },
        }


def organisation_document_link(
        organisation,
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
                    "organisation/document-link",
                    "file-format",
                    apiField="file_format.code",
                    ))
        elif not file_format:
            errors.append(
                FieldValidationError(
                    "organisation/document-link",
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
            # if not document_date:
            #     errors.append(
            #             RequiredFieldError(
            #                 "organisation/document-link",
            #                 "document-date",
            #                 ))

            document_date = None


        title_narratives = narratives_validate(title_narratives_data, organisation.default_lang, organisation.id,  warnings, errors, "title")
        errors = errors + title_narratives['errors']
        warnings = warnings + title_narratives['warnings']

        return {
            "warnings": warnings,
            "errors": errors,
            "validated_data": {
                "organisation": organisation,
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
                    "organisation/document-link/category",
                    "code",
                    apiField="category.code",
                    ))
        elif not category:
            errors.append(
                FieldValidationError(
                    "organisation/document-link/category",
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
                    "organisation/document-link/language",
                    "code",
                    apiField="language.code",
                    ))
        elif not language:
            errors.append(
                FieldValidationError(
                    "organisation/document-link/language",
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

def document_link_recipient_country(
        document_link,
        recipient_country_code,
        ):
        warnings = []
        errors = []

        recipient_country = get_or_none(models.Country, code=recipient_country_code)

        if not recipient_country_code:
            errors.append(
                RequiredFieldError(
                    "organisation/document-link/recipient_country",
                    "code",
                    apiField="recipient_country.code",
                    ))
        elif not recipient_country:
            errors.append(
                FieldValidationError(
                    "organisation/document-link/recipient_country",
                    "code",
                    "recipient_country not found for code {}".format(recipient_country_code),
                    apiField="recipient_country.code",
                    ))

        return {
            "warnings": warnings,
            "errors": errors,
            "validated_data": {
                "document_link": document_link,
                "recipient_country": recipient_country,
            },
        }

