from datetime import datetime

from django.contrib.gis.geos import GEOSGeometry, Point

from iati_parser import IatiParser
from IATI_2_02 import Parse as IATI_202_Parser
from iati import models
from iati.transaction import models as transaction_models
from iati_codelists import models as codelist_models
from iati_vocabulary import models as vocabulary_models
from iati_organisation import models as organisation_models
from geodata.models import Country, Region
from iati.parser import post_save
from currency_convert import convert


class Parse(IATI_202_Parser):

    VERSION = '2.01' 

    def __init__(self, *args, **kwargs):
        super(Parse, self).__init__(*args, **kwargs)

