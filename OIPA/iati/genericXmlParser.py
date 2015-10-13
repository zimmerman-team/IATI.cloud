from lxml import etree
from parse_logger import models as logModels
from django.db.models import Q
from django.core.mail import send_mail
from deleter import Deleter
import gc
from iati.filegrabber import FileGrabber
import datetime
from collections import OrderedDict
from decimal import Decimal
import inspect
import traceback
import re
from iati_synchroniser.exception_handler import exception_handler
import re
from django.contrib.auth.models import User
import traceback
from django.db import IntegrityError
from django.db.models.fields.related import ForeignKey, OneToOneField

class XMLParser(object):
    VERSION = '2.01'  #overwrite for older versions
    xml_source_ref =''
    iati_source = None

    logged_functions = []
    hints = []
    errors = []

    # TODO: find a way to simply save in parser functions, and actually commit to db on exit
    model_store = OrderedDict()



    DB_CACHE_LIMIT = 30 #overwrite in subclass if you want more/less

    def __init__(self):
        self.hints = []
        self.logged_functions = []
        self.errors = []


    def testWithExampleFile(self):
        self.testWithFile("activity-standard-example-annotated_105.xml")

    def testWithRealFile(self):
        self.testWithFile("iat-activities-formated.xml")

    #do stuff if method is not found but the tag has to be used a saved
    def magicMethod(self,function_name,element):
        return False

    def load_and_parse(self, root):
        
        self.root = root
        self.parse_activities(root)

        hintsStr = ''
        errorStr = ''
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

        if(send_mail):
            print 'sending mail'
            for developer in User.objects.filter(groups__name='developers').all():
                self.sendErrorMail(developer.email, hintsStr +"\n"+errorStr)

    def testWithFile(self,fileName):
        with open(fileName, "r") as myfile:
            data = myfile.read().replace('\n', '')
        self.load_and_parse(data)

    def parse_activities(self, root):
        # TODO: refactor this and the module
        for e in root.getchildren():
            print(e)
            self.model_store = OrderedDict()
            self.parse(e)
            self.save_all_models()


    def parse(self,element):

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
                # print(e.message)
                traceback.print_exc()
                pass
            except self.ValidationError as e:
                print(e)
                pass
            except Exception as exception:
                # pass
                print(exception.message)
                # traceback.print_exc()
                # self.handle_exception(x_path, function_name, exeception,e)
        # else:
        #     if not self.magicMethod(function_name,e):
        #         self.handle_function_not_found(x_path, function_name,e)

            # try:
            #     self.parse(element)
            # except Exception as exeception:
            #     traceback.print_exc()
            #     self.handle_exception(x_path, function_name, exeception,element)

        for e in element.getchildren():
            self.parse(e)

        # todo: rewrite this
    
    def generate_function_name(self, xpath):
        function_name = xpath.replace('/', '__')
        function_name = function_name.replace('-', '_')
        function_name = self.remove_brackets(function_name)

        return function_name[2:]

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

        log_entry = logModels.ParseLog()
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
        log_entry = logModels.ParseLog()
        log_entry.error_hint = hint
        log_entry.error_text = errExceptionStr
        log_entry.error_msg = str(exception)
        log_entry.file_name = self.iati_source.source_url
        log_entry.location = xpath
        log_entry.error_time = datetime.datetime.now()
        log_entry.save()

    def sendErrorMail(self,toAddress, errorString):
        send_mail('error mail!', errorString, 'error@oipa.nl',[toAddress], fail_silently=False)

    # register last seen model of this type. Is overwritten on later encounters
    def register_model(self, key, model):
        if key in self.model_store:
            self.model_store[key].append(model)
        else:
            self.model_store[key] = [model]

    def get_model(self, key, index=-1):
        if key in self.model_store:
            return self.model_store[key][index]
        return None

    def pop_model(self, key):
        if key in self.model_store:
            return self.model_store[key].pop()
        return None

    def save_model(self, key, index=-1):
        return self.get_model(key, index).save()

    def guess_number(self,number_string):
        #first strip non numeric values from begin and end
        non_decimal = re.compile(r'[^\d.,]+')
        errormsg = "ValueError: Input must be decimal or integer string"
        stripped_string = non_decimal.sub('', number_string)
        #check if there is only 1 comma (central european way)
        try:
            if stripped_string.count(',') <= 1:
                return float(stripped_string.replace(',','.'))
            else:
                return float(stripped_string.replace(',',''))
        except ValueError,error:
            print "%s\n%s" %(errormsg, error)
            return None

    #helper function check if integer
    def isInt(self, obj):
        try:
            int(obj)
            return True
        except:
            return False

    #helper function return true boolean
    def makeBool(self,text):
        if text == '1':
            return True
        return False

    def update_related(self, model):
        """
        Don't ask why...
        """
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
                except Exception as e:
                    print(e)

        # saved_models = []
        # for path_name in self.model_store:
        #     db_model = self.model_store[path_name]
        #     if db_model.__class__.__name__ not in saved_models:
        #         db_model.save()
        #         saved_models.append(db_model.__class__.__name__)

