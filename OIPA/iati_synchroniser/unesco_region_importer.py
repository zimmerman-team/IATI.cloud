import json
import os

from geodata.models import Region
from iati_vocabulary.models import RegionVocabulary


class UnescoRegionImporter():
    """
    Currently, Region objects in OIPA are Codelists (see:
    http://reference.iatistandard.org/203/codelists/Region/). The problem is,
    that Unesco is using their external codelist from a Google docs file for
    Regions, and it is not IATI-related. So in order for new Unesco portal to
    work properly with OIPA, we will temporary store these Unesco-specific
    regions in our database.

    See: #667
    """

    def update(self):
        # XXX: specific OIPA tasks (see: where_to_start.md are already ran, so
        # this already exists in the database):

        # "The region reported corresponds to a region vocabulary maintained by
        # the reporting organisation for this activity":
        reporting_org_region_vocabulary = RegionVocabulary.objects.get(
            code=99
        )

        with open(
            os.path.dirname(os.path.abspath(__file__)) +
                '/data/unesco_specific_regions.json') as f:
            data = json.load(f)

            for region in data:
                new_unesco_region, created = Region.objects.get_or_create(
                    added_manually=True,
                    code=region['code'],
                    name=region['label'],
                    region_vocabulary=reporting_org_region_vocabulary,
                )

                if created:
                    new_unesco_region.save()
