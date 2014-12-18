#!/bin/sh

cd ../OIPA/ && ./manage.py rqenqueue synchronize_with_iati_api 1
cd ../OIPA/ && ./manage.py rqenqueue synchronize_with_iati_api 1
