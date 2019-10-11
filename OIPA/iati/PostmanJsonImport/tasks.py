# Create your tasks here
from __future__ import absolute_import, unicode_literals

from celery import task

from iati.PostmanJsonImport.importPostmanJson import PostmanAPIImport


@task
def get_postman_api():
    PostmanAPIImport().get_json()


@task
def printHello():
    print('hello')
