from lxml import etree
from collections import OrderedDict
import datetime
import traceback
import dateutil.parser
import re
from decimal import Decimal, InvalidOperation

from django.db.models.fields.related import ForeignKey, OneToOneField
from django.db.models import Model
from iati_synchroniser.models import IatiXmlSourceNote
from django.conf import settings
from iati.parser.exceptions import *


class IatiParser(object):
    # default version
    VERSION = '2.02'

    def __init__(self, root):
        self.logged_functions = []
        self.hints = []
        self.errors = []
        self.parse_start_datetime = datetime.datetime.now()
        self.iati_source = None
        self.force_reparse = False
        self.default_lang = None

        # TODO: find a way to simply save in parser functions, and actually commit to db on exit
        self.model_store = OrderedDict()
        self.root = root

    def get_or_none(self, model, *args, **kwargs):
        try:
            return model.objects.get(*args, **kwargs)
        except model.DoesNotExist:
            return None

    def _get_currency_or_raise(self, model_name, currency):
        """
        get default currency if not available for currency-related fields
        """
        # TO DO; this does not invalidate the whole element (budget, transaction, planned disbursement) while it should
        if not currency:
            currency = getattr(self.get_model('Activity'), 'default_currency')
            if not currency:
                raise RequiredFieldError(
                    model_name,
                    "currency",
                    "must specify default-currency on iati-activity or as currency on the element itself")

        return currency

    def makeBool(self, text):
        if text == '1' or text == 'true':
            return True
        return False

    def makeBoolNone(self, text):
        if text == '1':
            return True
        elif text == '0':
            return False

        return None

    def guess_number(self, model_name, number_string):
        #first strip non numeric values, except for -.,
        decimal_string = re.sub(r'[^\d.,-]+', '', number_string)

        try:
            return Decimal(decimal_string)
        except ValueError:
            raise ValidationError(
                model_name,
                "value",
                "Must be decimal or integer string")
        except InvalidOperation:
            raise ValidationError(
                model_name,
                "value",
                "Must be decimal or integer string")

    def isInt(self, obj):
        try:
            int(obj)
            return True
        except:
            return False

    def _normalize(self, attr): 
        attr = attr.strip(' \t\n\r').replace(" ", "")
        attr = re.sub("[/:',.+]", "-", attr)
        return attr

    def validate_date(self, unvalidated_date):

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

    def get_primary_name(self, element, primary_name):
        if primary_name:
            lang = element.attrib.get('{http://www.w3.org/XML/1998/namespace}lang', self.default_lang)
            if lang == 'en':
                primary_name = element.text
        else:
            primary_name = element.text
        return primary_name

    def load_and_parse(self, root):
        self.parse_activities(root)

    def parse_activities(self, root):
        """

        """
        for e in root.getchildren():
            self.model_store = OrderedDict()
            parsed = self.parse(e)
            # only save if the activity is updated
            if parsed:
                self.save_all_models()
                self.post_save_models()

        self.post_save_file(self.iati_source)
        
        if settings.ERROR_LOGS_ENABLED:
            self.iati_source.note_count = len(self.errors)
            self.iati_source.save()
            IatiXmlSourceNote.objects.filter(source=self.iati_source).delete()
            IatiXmlSourceNote.objects.bulk_create(self.errors)
    
    def post_save_models(self):
        print "override in children"

    def post_save_file(self, iati_source):
        print "override in children"

    def append_error(self, error_type, model, field, message, sourceline, iati_id=None):
        if not settings.ERROR_LOGS_ENABLED:
            return

        # get iati identifier
        iati_identifier = None
        if iati_id:
            iati_identifier = iati_id
        elif self.iati_source.type == 1:
            activity = self.get_model('Activity')
            if activity and activity.iati_identifier:
                iati_identifier = activity.iati_identifier
            elif activity:
                iati_identifier = activity.id
        else:
            organisation = self.get_model('Organisation')
            if organisation and organisation.organisation_identifier:
                iati_identifier = organisation.organisation_identifier
            elif organisation:
                iati_identifier = organisation.id
        
        if not iati_identifier and hasattr(self, 'identifier'):
            iati_identifier = self.identifier
        elif not iati_identifier:
            iati_identifier = 'no-identifier'

        note = IatiXmlSourceNote(
            source=self.iati_source,
            iati_identifier=iati_identifier,
            model=model,
            field=field,
            message=message,
            exception_type=error_type,
            line_number=sourceline
        )

        self.errors.append(note)

    def parse(self, element):
        if element is None:
            return
        if type(element).__name__ != '_Element':
            return
        if element.tag == etree.Comment:
            return

        x_path = self.root.getroottree().getpath(element)
        function_name = self.generate_function_name(x_path)

        if hasattr(self, function_name) and callable(getattr(self, function_name)):
            element_method = getattr(self, function_name)
            try:
                element_method(element)
            except RequiredFieldError as e:
                self.append_error('RequiredFieldError', e.model, e.field, e.message, element.sourceline)
                return
            except EmptyFieldError as e:
                self.append_error('EmptyFieldError', e.model, e.field, e.message, element.sourceline)
                return
            except ValidationError as e:
                self.append_error('ValidationError', e.model, e.field, e.message, element.sourceline, e.iati_id)
                return
            except ValueError as e:
                traceback.print_exc()
                # self.append_error('ValueError', 'TO DO', 'TO DO', e.message, element.sourceline)
                return
            except InvalidOperation as e:
                traceback.print_exc()
                # self.append_error('InvalidOperation', 'TO DO', 'TO DO', e.message, element.sourceline)
                return
            except IgnoredVocabularyError as e:
                # not implemented, ignore for now
                return
            except ParserError as e:
                self.append_error('ParserError', 'TO DO', 'TO DO', e.message, None)
                return
            except NoUpdateRequired as e:
                # do nothing, go to next activity
                return
            except Exception as exception:
                # print exception.message
                traceback.print_exc()

        for e in element.getchildren():
            self.parse(e)

        return True

    def generate_function_name(self, xpath):
        function_name = xpath.replace('/', '__')
        function_name = function_name.replace('-', '_')
        function_name = self.remove_brackets(function_name)

        return function_name[2:]

    # TODO: separate these functions in their own data structure - 2015-12-02
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
            model.related_object = model.related_object
        for field in model._meta.fields:
            if isinstance(field, (ForeignKey, OneToOneField)):
                setattr(model, field.name, getattr(model, field.name))

    def save_all_models(self):
        # TODO: problem: assigning unsaved model to foreign key results in error because field_id has not been set (see issue )
        for model_list in self.model_store.items():
            for model in model_list[1]:
                try:
                    self.update_related(model)
                    model.save()

                except ValueError as e:
                    # TO DO; check if we need to do internal logging on these value errors
                    print e.message

                except Exception as e:
                    # these stay in the logs until we know what to do with them
                    print e.message
                    # self.append_error(str(type(e)), e.message, 'TO DO')

    def remove_brackets(self,function_name):
        result = ""
        flag = True
        for c in function_name:
            if c == "[": flag = False
            if flag: result += c
            if c == "]": flag = True
        return result

