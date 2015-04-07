#!/usr/bin/env python

import os
from distutils.core import setup
from setuptools import find_packages
from pip.req import parse_requirements

os.chdir('OIPA')
install_requirements = parse_requirements('requirements.txt')
requirements = [str(ir.req) for ir in install_requirements]

setup(name='OIPA',
      version='2.1',
      description='',
      author='Zimmerman & Zimmerman',
      url="OIPA is an open-source framework that renders IATI compliant XML and \
            related indicator #opendata into the OIPA datamodel for storage. \
            This ETL approach provides I/O using the OIPA Tastypie RESTless API (soon DRF!) \
            providing you with direct XML or JSON output. Does Django and MySQL. \
            Codebase maintained by Zimmerman & Zimmerman in Amsterdam. http://www.oipa.nl/",
      packages=find_packages(),
      install_requires=requirements,
     )
