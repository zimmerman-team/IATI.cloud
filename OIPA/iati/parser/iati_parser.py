from lxml import etree
from collections import OrderedDict
import datetime
import traceback
import dateutil.parser
import re
from decimal import Decimal, InvalidOperation

from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.db.models.fields.related import ForeignKey, OneToOneField
from django.db.models import Model


class IatiParser(object):
    # default version
    VERSION = '2.01'

    def __init__(self, root):
        self.logged_functions = []
        self.hints = []
        self.errors = []
        self.validation_errors = []
        self.required_field_errors = []
        self.iati_source = None
        self.parse_start_datetime = datetime.datetime.now()
        self.force_reparse = False
        self.default_lang = None

        # TODO: find a way to simply save in parser functions, and actually commit to db on exit
        self.model_store = OrderedDict()

        self.root = root

    class RequiredFieldError(Exception):
        def __init__(self, field, msg):
            """
            field: the field that is required
            msg: explanation why
            """
            self.field = field
            self.message = msg

        def __str__(self):
            return repr(self.field)

    class ValidationError(Exception):
        def __init__(self, field, msg):
            """
            field: the field that is validated
            msg: explanation what went wrong
            """
            self.field = field
            self.message = msg

        def __str__(self):
            return repr(self.field)

    def get_or_none(self, model, *args, **kwargs):
        try:
            return model.objects.get(*args, **kwargs)
        except model.DoesNotExist:
            return None

    def _get_currency_or_raise(self, currency):
        """
        get default currency if not available for currency-related fields
        """
        # TO DO; this does not invalidate the whole element (budget, transaction, planned disbursement) while it should
        if not currency:
            currency = getattr(self.get_model('Activity'), 'default_currency')
            if not currency:
                raise self.RequiredFieldError(
                    "currency",
                    "value__currency: currency is not set and default-currency is not set on activity as well")

        return currency

    def makeBool(self, text):
        if text == '1':
            return True
        return False

    def guess_number(self,number_string):
        #first strip non numeric values, except for -.,
        decimal_string = re.sub(r'[^\d.,-]+', '', number_string)

        try:
            return Decimal(decimal_string)
        except ValueError:
            raise ValueError("ValueError: Input must be decimal or integer string")
        except InvalidOperation:
            raise InvalidOperation("InvalidOperation: Input must be decimal or integer string")

    def isInt(self, obj):
        try:
            int(obj)
            return True
        except:
            return False

    def _normalize(self, attr): 
        attr = attr.strip(' \t\n\r').replace(" ", "")
        attr = re.sub("[/:',]", "-", attr)
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
            raise self.ValidationError("date", "Invalid date used: " + unvalidated_date)

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
        # TODO: refactor this and the module
        for e in root.getchildren():
            self.model_store = OrderedDict()
            parsed = self.parse(e)
            # only save if the activity is updated
            if parsed:
                self.save_all_models()
                self.post_save_models()
        self.post_save_file(self.iati_source)
    
    def post_save_models(self):
        print "override in children"

    def post_save_file(self, iati_source):
        print "override in children"

    def parse(self, element):
        if element == None:
            return
        if type(element).__name__ != '_Element':
            return
        if element.tag == etree.Comment:
            return

        x_path = self.root.getroottree().getpath(element)
        function_name = self.generate_function_name(x_path)

        if hasattr(self, function_name) and callable(getattr(self, function_name)):
            elementMethod = getattr(self, function_name)
            try:
                elementMethod(element)
            except self.RequiredFieldError as e:
                print e.message
                # traceback.print_exc()
                return
            except self.ValidationError as e:
                print e.message
                # traceback.print_exc()
                return
            except Exception as exception:
                # print exception.message
                traceback.print_exc()
                return

        # TODO: rewrite this
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
    def register_model(self, key, model):
        if isinstance(key, Model):
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
                    # if model.__class__.__name__ == "Narrative":
                    #     print(type(model.parent_object))
                except Exception as e:
                    # traceback.print_exc()
                    print(e)


    def remove_brackets(self,function_name):

        result = ""
        flag = True
        for c in function_name:
            if c == "[": flag = False
            if flag: result += c
            if c == "]": flag = True
        return result

    def handle_exception(self, xpath, function_name, exception,element):
        hint = """look at XML document"""
        errorStr = "error in method:"+function_name+" location in document:"+xpath+" at line "+str(element.sourceline)+" source is "+self.iati_source.source_url
        errExceptionStr = errorStr+"\n"+str(traceback.format_exc())+"\n"
        for attr in element.attrib :
            errExceptionStr = errExceptionStr+" "+attr+" = "+element.attrib.get(attr)+"\n"
        if element.text != '':
            errExceptionStr = errExceptionStr+element.text
        self.errors.append(errExceptionStr)
        log_entry = log_models.ParseLog()
        log_entry.error_hint = hint
        log_entry.error_text = errExceptionStr
        log_entry.error_msg = str(exception)
        log_entry.file_name = self.iati_source.source_url
        log_entry.location = xpath
        log_entry.error_time = datetime.datetime.now()
        log_entry.save()

    def sendErrorMail(self,toAddress, errorString):
        send_mail('error mail!', errorString, 'error@oipa.nl',[toAddress], fail_silently=False)

    def handle_log(self):
        hintsStr = ''
        errorStr = ''
        validating_error_str = ''
        required_field_error_str = ''

        send_mail = False
        print 'before sending mail'
        if len(self.hints) > 0:
            hintsStr = "function that are missing:"
            hintsStr += "\n".join( self.hints )
            send_mail = True
        if len(self.errors) > 0:
            errorStr = hintsStr+"\n\n errors found:\n"
            errorStr += "\n".join( self.errors)
            send_mail = True
        if len(self.validation_errors) > 0:
            validating_error_str = required_field_error_str+"\n\n validation errors found:\n"
            validating_error_str += "\n".join( self.validation_errors)
            send_mail = True
        if len(self.required_field_errors) > 0:
            required_field_error_str = required_field_error_str+"\n\n required field errors found:\n"
            required_field_error_str += "\n".join( self.required_field_errors)
            send_mail = True

        if(send_mail):
            print 'sending mail'
            for developer in User.objects.filter(groups__name='developers').all():
                self.sendErrorMail(developer.email, hintsStr +"\n"+errorStr +"\n"+validating_error_str+"\n"+required_field_error_str)

