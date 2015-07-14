from lxml import etree
from parse_logger import models as logModels
from django.db.models import Q
from django.core.mail import send_mail
from deleter import Deleter
import gc
from iati.filegrabber import FileGrabber
import datetime
import inspect
import traceback
import re
from iati_synchroniser.exception_handler import exception_handler


class XMLParser(object):

    VERSION = '2.01'  #overwrite for older versions
    xml_source_ref =''
    logged_functions = []
    hints = []
    errors = []

    db_call_cache = {}
    model_store = {}

    DB_CACHE_LIMIT = 30 #overwrite in subclass if you want more/less 


   

    def testWithExampleFile(self):
        self.testWithFile("activity-standard-example-annotated_105.xml")

    def testWithRealFile(self):
        self.testWithFile("iat-activities-formated.xml")

    #do stuff if method is not found but the tag has to be used a saved
    def magicMethod(self,function_name,element):
        return False

    def load_and_parse(self, root):
        
        self.root = root
        print root.attrib.get('version')
        #exit
        self.parse(root)
        self.save_all_models()

        hintsStr = ''
        errorStr = ''
        send_mail = False
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
            self.sendErrorMail('daniel@zimmermanzimmerman.nl', hintsStr +"\n"+errorStr)

    def testWithFile(self,fileName):
        with open(fileName, "r") as myfile:
            data = myfile.read().replace('\n', '')
        self.load_and_parse(data)


    def parse(self,element):

        if element == None:
            return
        if type(element).__name__ != '_Element':
            #print type(element).__name__ 
            return


        for e in element.getchildren():

            if e == None or type(e).__name__ != '_Element':
                
                continue
            x_path = self.root.getroottree().getpath(e)
            function_name = self.generate_function_name(x_path)
            #print function_name
            if element.tag == etree.Comment:
                continue
            if hasattr(self, function_name) and callable(getattr(self, function_name)):
                elementMethod = getattr(self, function_name)
                try:
                    self.parse(elementMethod(e))
                except Exception as exeception:
                    print 'error'
                    #print function_name
                    traceback.print_exc()
                    return
                    self.handle_exception(x_path, function_name, exeception)
                    self.parse(e)
            else:
                if not self.magicMethod(function_name,e):
                    self.handle_function_not_found(x_path, function_name,e)
                #print function_name

                self.parse(e)

        

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
    tag:"""+element.tag+"""'''
    def """ + function_name + """(self,element):
        model = self.get_func_parent_model()
        #store element 
        return element"""
        #print hint
        self.hints.append(hint)

        log_entry = logModels.ParseLog()
        log_entry.error_hint = hint
        log_entry.error_text = 'Function ' + function_name + ' not found'
        log_entry.file_name = 'test'
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


    def handle_exception(self, xpath, function_name, exception):
        hint = """look at XML document"""
        errorStr = "error in method:"+function_name+" location in document:"+xpath
        errExceptionStr = errorStr+"\n"+str(exception)
        
        self.errors.append(errExceptionStr)
        log_entry = logModels.ParseLog()
        log_entry.error_hint = hint
        log_entry.error_text = errExceptionStr
        log_entry.file_name = 'test'
        log_entry.location = xpath
        log_entry.error_time = datetime.datetime.now()
        log_entry.save()



    def sendErrorMail(self,toAddress, errorString):
        send_mail('error mail!', errorString, 'error@oipa.nl',[toAddress], fail_silently=False)

    # call db to find a key 
    def cached_db_call(self,model, key,keyDB = 'code',createNew=False):
        if key == '' or key == None:
            return None
        opts =   model._meta
        try:
            opts.get_field('codelist_iati_version')
        except:
            return self.cached_db_call_no_version(model,key,keyDB=keyDB,createNew=createNew)

        model_name = model.__name__
        codelist_iati_version = self.VERSION
        #print model_name
        print str(key)+' is the key'
        if model_name in self.db_call_cache:
            model_cache = self.db_call_cache[model_name]
            if key in model_cache:
                return model_cache[key]
            else:
                try:
                    if model.objects.filter(code=key,codelist_iati_version=codelist_iati_version).exists():
                        model_cache[key] = model.objects.get(code=key,codelist_iati_version=codelist_iati_version)
                        return model_cache[key]
                except:
                    if model.objects.filter(name=key,codelist_iati_version=codelist_iati_version).exists():
                        model_cache[key] = model.objects.get(name=key,codelist_iati_version=codelist_iati_version)
                        return model_cache[key]
                else:
                    if createNew == True:
                        #print 'in create new'
                        modelInstance = model()
                        modelInstance.code = key
                        modelInstance.codelist_iati_version=codelist_iati_version
                        modelInstance.save()
                        return modelInstance
                    
                    return None
        else:
            self.db_call_cache[model_name] = {}
            objects = model.objects.all()[:self.DB_CACHE_LIMIT]
            for obj in objects:
                self.db_call_cache[model_name][obj.code] = obj
            #print 'call recursively'
            return self.cached_db_call(model,key,keyDB=keyDB,createNew=createNew)

    def cached_db_call_no_version(self,model, key,keyDB = 'code',createNew=False):
        model_name = model.__name__
        #print model_name
        #print createNew
        if model_name in self.db_call_cache:
            model_cache = self.db_call_cache[model_name]
            if key in model_cache:
                return model_cache[key]
            else:
                try:
                    if model.objects.filter(code=key).exists():
                        model_cache[key] = model.objects.get(code=key)
                        return model_cache[key]
                except:
                    if model.objects.filter(name=key).exists():
                        model_cache[key] = model.objects.get(name=key)
                        return model_cache[key]
                else:
                    if createNew == True:
                        print 'in create new'
                        modelInstance = model()
                        modelInstance.code = key
                        modelInstance.save()
                        return modelInstance
                    
                    return None
        else:
            self.db_call_cache[model_name] = {}
            objects = model.objects.all()[:self.DB_CACHE_LIMIT]
            for obj in objects:
                self.db_call_cache[model_name][obj.code] = obj
            #print 'call recursively'
            return self.cached_db_call_no_version(model,key,keyDB=keyDB,createNew=createNew)

        

    def get_func_parent_model(self,class_name = None):

        caller_name =  inspect.stack()[1][3] # get the name of the caller function
        caller_name_arr = caller_name.split("__")
        key_string = None
        model = None
        for caller_name_part in caller_name_arr[:-1]:
            #print caller_name_part
            if key_string == None:
                key_string = caller_name_part
                continue
            else:
                key_string += '__'+caller_name_part
                #print key_string
                if key_string in self.model_store:
                    model_temp = self.model_store[key_string]
                    #print model_temp.__class__.__name__
                    if(class_name == None or class_name == model_temp.__class__.__name__):
                        model = model_temp
                

        return model

    def set_func_model(self,model):
        caller_name =  inspect.stack()[1][3]# get the name of the caller function
        if caller_name in self.model_store:
            model_temp = self.model_store[caller_name]
            model_temp.save()

        model.save()
        self.model_store[caller_name] = model










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

    def save_all_models(self,subTree = ''):
        #make tree
        saved_models = []
        for path_name in self.model_store:
            db_model = self.model_store[path_name]
            if db_model.__class__.__name__ not in saved_models:
                db_model.save()
                saved_models.append(db_model.__class__.__name__)

