from iati.parser.IATI_2_02 import Parse as IATI_202_Parser


class Parse(IATI_202_Parser):

    def __init__(self, *args, **kwargs):
        super(Parse, self).__init__(*args, **kwargs)
        self.VERSION = '2.01'
