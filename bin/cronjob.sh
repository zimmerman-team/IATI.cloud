#!/bin/sh

cd ../OIPA/ && ./manage.py rqenqueue get_new_sources_from_iati_api
