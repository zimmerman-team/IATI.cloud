import datetime
import hashlib
import logging
import re
from collections import OrderedDict
from decimal import Decimal, InvalidOperation

import dateutil.parser
from django.conf import settings
from django.db.models import Model
from django.db.models.fields.related import ForeignKey, OneToOneField
from lxml import etree

from common.util import findnth_occurence_in_string, normalise_unicode_string
from iati.models import Activity
from iati.parser.exceptions import (
    FieldValidationError, IgnoredVocabularyError, NoUpdateRequired,
    ParserError, RequiredFieldError, ValidationError
)
from iati_codelists import models as codelist_models
from iati_synchroniser.models import DatasetNote
from solr.activity.tasks import ActivityTaskIndexing
from solr.datasetnote.tasks import DatasetNoteTaskIndexing

log = logging.getLogger(__name__)


class IatiParser(object):
    # default version
    VERSION = '2.03'

    def __init__(self, root):
        self.logged_functions = []
        self.hints = []
        self.errors = []
        self.parse_start_datetime = datetime.datetime.now()
        self.dataset = None
        self.publisher = None
        self.force_reparse = False
        self.default_lang = settings.DEFAULT_LANG
        # A cache to store codelist items in memory (for each element when
        # parsing).
        # During tests, if a new model with a same name is added to the
        # database, this has to be cleared:
        self.codelist_cache = {}

        # TODO: find a way to simply save in parser functions, and actually
        # commit to db on exit
        self.model_store = OrderedDict()
        self.root = root

    def check_registration_agency_validity(self, element_name, element, ref):
        reg_agency_found = False
        if ref and findnth_occurence_in_string(ref, '-', 1) > -1:
            index = findnth_occurence_in_string(ref, '-', 1)
            reg_agency = self.get_or_none(
                codelist_models.OrganisationRegistrationAgency,
                code=ref[:index]
            )
            if reg_agency:
                reg_agency_found = True

        if not reg_agency_found:
            self.append_error(
                'FieldValidationError',
                element_name,
                "ref",
                "Must be in the format {Registration Agency} - (Registration "
                "Number}",
                element.sourceline,
                ref)

    def get_or_none(self, model, *args, **kwargs):
        code = kwargs.get('code', None)
        if code:
            code = normalise_unicode_string(code)
            try:
                model_cache = self.codelist_cache[model.__name__]
            except KeyError:
                model_cache = model.objects.in_bulk()
                self.codelist_cache[model.__name__] = model_cache
            return model_cache.get(code)

        else:

            try:
                return model.objects.get(*args, **kwargs)
            except model.DoesNotExist:
                return None

    def _get_currency_or_raise(self, model_name, currency):
        """
        get default currency if not available for currency-related fields
        """
        # TODO: this does not invalidate the whole element (budget,
        # transaction, planned disbursement) while it should
        if not currency:
            currency = getattr(self.get_model('Activity'), 'default_currency')
            if not currency:
                raise RequiredFieldError(
                    model_name,
                    "currency",
                    "must specify default-currency on iati-activity or as "
                    "currency on the element itself")

        return currency

    # TODO: test this function! it's used everywhere
    def makeBool(self, text):
        if text == '1' or text == 'true':
            return True
        return False

    def makeBoolNone(self, text):
        if text == '1':
            return True
        elif text == '0':
            return False
        elif text == 'true':
            return True
        elif text == 'false':
            return False

        return None

    def guess_number(self, model_name, number_string):
        # first strip non numeric values, except for -.,
        decimal_string = re.sub(r'[^\d.,-]+', '', number_string)

        try:
            return Decimal(decimal_string)
        except ValueError:
            raise FieldValidationError(
                model_name,
                "value",
                "Must be decimal or integer string")
        except InvalidOperation:
            raise FieldValidationError(
                model_name,
                "value",
                "Must be decimal or integer string")

    def isInt(self, obj):
        try:
            int(obj)
            return True
        except BaseException:
            return False

    def _normalize(self, attr):
        # attr = attr.strip(' \t\n\r').replace(" ", "")
        # attr = re.sub("[/:&',.+]", "-", attr)

        # normalize for use in the API with comma-separated values
        attr = re.sub(",", "COMMA", attr)
        return attr

    def validate_date(self, unvalidated_date):

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

    def get_primary_name(self, element, primary_name):
        if primary_name:
            lang = element.attrib.get(
                '{http://www.w3.org/XML/1998/namespace}lang',
                self.default_lang)
            if lang == 'en':
                primary_name = element.text
        else:
            primary_name = element.text

        # FIXME: this is hardcoded!
        return primary_name[:255]

    def load_and_parse(self, root):
        self.parse_activities(root)

    def parse_activities(self, root):
        """

        """
        activities_to_keep = []
        for e in root.getchildren():
            self.model_store = OrderedDict()
            parsed = False
            should_be_parsed = True

            hasher = hashlib.sha1()
            hasher.update(etree.tostring(e))
            sha1 = hasher.hexdigest()
            if not self.force_reparse:
                try:
                    iati_id = e.find('iati-identifier').text
                    saved_activity = Activity.objects.\
                        filter(iati_identifier=iati_id).values("sha1")
                    if saved_activity.count() == 1:
                        if saved_activity[0]['sha1'] == sha1:
                            activities_to_keep.append(iati_id)
                            should_be_parsed = False
                except Exception:
                    should_be_parsed = True

            if should_be_parsed:
                parsed = self.parse(e)
            # only save if the activity is updated

            if parsed:
                try:
                    model = self.get_model('Activity')
                    if model is not None:
                        if sha1:
                            model.sha1 = sha1
                    self.save_all_models()
                    self.post_save_models()
                except Exception:
                    model = self.get_model('Activity')
                    if model is not None:
                        if sha1:
                            model.sha1 = sha1
                        ActivityTaskIndexing(model,
                                             related=True).run()
                else:
                    model = self.get_model('Activity')
                    if model is not None:
                        if sha1:
                            model.sha1 = sha1
                        ActivityTaskIndexing(model, related=True).run()

        self.post_save_file(self.dataset, activities_to_keep)

        if settings.ERROR_LOGS_ENABLED:
            self.post_save_validators(self.dataset)

            # TODO - only delete errors on activities that were updated
            self.dataset.note_count = len(self.errors)
            self.dataset.save()

            DatasetNote.objects.filter(dataset=self.dataset).delete()
            DatasetNote.objects.bulk_create(self.errors)

            DatasetNoteTaskIndexing().run_from_dataset(dataset=self.dataset)

    def post_save_models(self):
        print("override in children")

    def post_save_file(self, dataset):
        print("override in children")

    def append_error(self, error_type, model, field, message,
                     sourceline, variable='', iati_id=None):
        if not settings.ERROR_LOGS_ENABLED:
            return

        # get iati identifier
        iati_identifier = None
        if iati_id:
            iati_identifier = iati_id
        elif self.dataset.filetype == 1:
            activity = self.get_model('Activity')
            if activity and activity.iati_identifier:
                iati_identifier = activity.iati_identifier
            # elif activity:
            #     iati_identifier = activity.id
        else:
            organisation = self.get_model('Organisation')
            if organisation and organisation.organisation_identifier:
                iati_identifier = organisation.organisation_identifier
            # elif organisation:
            #     iati_identifier = organisation.id

        if not iati_identifier and hasattr(self, 'identifier'):
            iati_identifier = self.identifier
        elif not iati_identifier:
            iati_identifier = 'no-identifier'

        if variable:
            variable = str(variable)[0:255]

        note = DatasetNote(
            dataset=self.dataset,
            iati_identifier=iati_identifier,
            model=model,
            field=field,
            message=str(message)[0:255],
            exception_type=error_type,
            line_number=sourceline,
            variable=variable
        )

        self.errors.append(note)

    def parse(self, element):
        """All of the methods from specific parser file (i. e. IATI_2_03.py)
        get called in this method
        """
        if element is None:
            return
        if type(element).__name__ != '_Element':
            return
        if element.tag == etree.Comment:
            return

        x_path = self.root.getroottree().getpath(element)
        function_name = self.generate_function_name(x_path)

        if hasattr(self, function_name)\
                and callable(getattr(self, function_name)):
            element_method = getattr(self, function_name)

            try:
                element_method(element)
            except RequiredFieldError as e:
                log.exception(e)
                self.append_error(
                    'RequiredFieldError',
                    e.model,
                    e.field,
                    e.message,
                    element.sourceline,
                    None)
                return
            except FieldValidationError as e:
                log.exception(e)
                self.append_error(
                    'FieldValidationError',
                    e.model,
                    e.field,
                    e.message,
                    element.sourceline,
                    e.variable,
                    e.iati_id)
                return
            except ValidationError as e:
                log.exception(e)
                self.append_error(
                    'FieldValidationError',
                    e.model,
                    e.field,
                    e.message,
                    element.sourceline,
                    None,
                    e.iati_id)
                return
            except IgnoredVocabularyError as e:
                # not implemented, ignore for now
                return
            except ParserError as e:
                log.exception(e)
                self.append_error(
                    'ParserError',
                    'TO DO',
                    'TO DO',
                    e.message,
                    None,
                    element.sourceline)
                return
            except NoUpdateRequired as e:
                # do nothing, go to next activity
                return
            except Exception as e:
                log.exception(e)
                return

        for e in element.getchildren():
            self.parse(e)

        return True

    def generate_function_name(self, xpath):
        function_name = xpath.replace('/', '__')
        function_name = function_name.replace('-', '_')
        function_name = self.remove_brackets(function_name)

        return function_name[2:]

    # TODO: separate these functions in their own data structure
    # - 2015-12-02
    def get_model_list(self, key):
        if key in self.model_store:
            return self.model_store[key]
        return None

    # register last seen model of this type. Is overwritten on later encounters
    def register_model(self, key, model=None):
        if isinstance(key, Model):
            model = key
            key = key.__class__.__name__

        if key in self.model_store:
            self.model_store[key].append(model)
        else:
            self.model_store[key] = [model]

        # The position of the current model on the model store
        return len(self.model_store[key]) - 1

    def get_model(self, key, index=-1):
        if isinstance(key, Model):
            key = key.__class__.__name__

        if key in self.model_store:
            if len(self.model_store[key]) > 0:
                return self.model_store[key][index]
        return None

    def pop_model(self, key):
        if isinstance(key, Model):
            key = key.__class__.__name__

        if key in self.model_store:
            if len(self.model_store[key]) > 0:
                return self.model_store[key].pop()
        return None

    def save_model(self, key, index=-1):
        return self.get_model(key, index).save()

    def update_related(self, model):
        """
        Currently a workaround for foreign key assignment before save
        """
        if model.__class__.__name__ in ("OrganisationNarrative", "Narrative"):
            # This is set in parser (IATI_2_02.py, IATI_2_03.py,
            # organisation_2_02 etc.) files:
            model.related_object = getattr(model, '_related_object')

        for field in model._meta.fields:
            if isinstance(field, (ForeignKey, OneToOneField)):
                setattr(model, field.name, getattr(model, field.name))

    def save_all_models(self):
        # TODO: problem: assigning unsaved model to foreign key results in
        # error because field_id has not been set (see: https://git.io/fbphN)
        for model_list in self.model_store.items():
            for model in model_list[1]:
                try:
                    self.update_related(model)

                    model.save()

                except Exception as e:
                    log.exception(e)
                    pass

    def remove_brackets(self, function_name):
        result = ""
        flag = True
        for c in function_name:
            if c == "[":
                flag = False
            if flag:
                result += c
            if c == "]":
                flag = True
        return result
