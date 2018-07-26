import json
import os

from iati_codelists.models import Sector
from iati_vocabulary.models import SectorVocabulary


# TODO: test
class UnescoSectorImporter():
    """
    There are Unesco-specific sectors that need to be imported to the new
    OIPA YODA for Unesco (from a Google docs file)

    See: #667
    """

    def update(self):
        # XXX: specific OIPA tasks (see: where_to_start.md are already ran, so
        # this already exists in the database):

        # "The sector reported corresponds to a sector vocabulary maintained
        # by the reporting organisation for this activity (if they are
        # referencing more than one)"
        strategies_vocabulary = SectorVocabulary.objects.get(
            code=98
        )

        # "The sector reported corresponds to a sector vocabulary maintained
        # by the reporting organisation for this activity"
        sector_vocabulary = SectorVocabulary.objects.get(
            code=99
        )

        # 1. Sectors related to strategies and plans:
        with open(
            os.path.dirname(
                os.path.abspath(__file__)
            ) + '/data/unesco_specific_sectors/strategies_and_action_plans.json'  # NOQA: E501
        ) as f:

            data = json.load(f)

            for sector in data:
                new_unesco_sector, created = Sector.objects.get_or_create(
                    code=sector['code'],
                    name=sector['label'],
                    vocabulary=strategies_vocabulary,
                )

                if created:
                    new_unesco_sector.save()

        # 2. Simply Uensco-specific sectors:
        with open(
            os.path.dirname(
                os.path.abspath(__file__)
            ) + '/data/unesco_specific_sectors/sectors.json'
        ) as f:

            data = json.load(f)

            for sector in data:
                new_unesco_sector, created = Sector.objects.get_or_create(
                    code=sector['code'],
                    name=sector['label'],
                    vocabulary=sector_vocabulary,
                )

                if created:
                    new_unesco_sector.save()
