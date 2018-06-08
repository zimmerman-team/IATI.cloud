from iati_organisation.parser.organisation_2_02 import Parse as IATI_202_Parser


class Parse(IATI_202_Parser):

    organisation_identifier = ''

    def __init__(self, *args, **kwargs):
        super(Parse, self).__init__(*args, **kwargs)
        self.VERSION = '2.01'
