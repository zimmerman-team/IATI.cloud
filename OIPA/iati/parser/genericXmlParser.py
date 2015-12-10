from lxml import etree
from parse_logger import models as log_models
from django.core.mail import send_mail
from collections import OrderedDict
import datetime
import re
import traceback
from django.contrib.auth.models import User
from django.db.models.fields.related import ForeignKey, OneToOneField
from decimal import Decimal, InvalidOperation

class XMLParser(object):

    VERSION = '2.01' # default version

    def __init__(self, root):
        self.logged_functions = []
        self.hints = []
        self.errors = []
        self.validation_errors = []
        self.required_field_errors = []
        self.iati_source = None

        # TODO: find a way to simply save in parser functions, and actually commit to db on exit
        self.model_store = OrderedDict()

        self.root = root

    def load_and_parse(self, root):
        self.parse_activities(root)

    def parse_activities(self, root):
        # TODO: refactor this and the module
        for e in root.getchildren():
            self.model_store = OrderedDict()
            self.parse(e)
            self.save_all_models()
            self.post_save()
            
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
                # print(e.field)
                print(e.message)
                print(e)
                return
            except self.ValidationError as e:
                # print(e.field)
                # print(e.message)
                traceback.print_exc()
                return
            except Exception as exception:
                # pass
                # print(exception.message)
                traceback.print_exc()
                return

        for e in element.getchildren():
            self.parse(e)

        # todo: rewrite this

    def generate_function_name(self, xpath):
        function_name = xpath.replace('/', '__')
        function_name = function_name.replace('-', '_')
        function_name = self.remove_brackets(function_name)

        return function_name[2:]

    # register last seen model of this type. Is overwritten on later encounters
    def register_model(self, key, model):
        if key in self.model_store:
            self.model_store[key].append(model)
        else:
            self.model_store[key] = [model]

    def get_model(self, key, index=-1):
        if key in self.model_store:
            if len(self.model_store[key]) > 0: 
                return self.model_store[key][index]
        return None

    def pop_model(self, key):
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
        if model.__class__.__name__ == "Narrative":
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


    def handle_function_not_found(self, xpath, function_name,element):
        print 'function not found '+function_name
        if function_name in self.logged_functions:
            return  # function already logged
        # add function name to logged functions
        self.logged_functions.append(function_name)
        keys = ''
        for key in element.attrib:
            keys += "\t"+key+':'+element.attrib.get(key)+"\n"

        hint = """

    '''atributes:
"""+keys+"""
    tag:"""+element.tag+"""
    found in """+ self.iati_source.source_url+""" at line """+str(element.sourceline)+""" iati_version ="""+self.VERSION+"""'''
    def """ + function_name + """(self,element):
        model = self.get_func_parent_model()
        #store element
        return element"""
        #print hint
        self.hints.append(hint)

        log_entry = log_models.ParseLog()
        log_entry.error_hint = hint
        log_entry.error_text = 'Function ' + function_name + ' not found'
        log_entry.error_msg = function_name
        log_entry.file_name = self.iati_source.source_url
        log_entry.location = xpath
        log_entry.error_time = datetime.datetime.now()
        log_entry.save()

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

