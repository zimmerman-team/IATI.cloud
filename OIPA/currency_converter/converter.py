from iati.models import Transaction

class CurrencyConverter():

    def convert_all(self):
        for entry in Transaction.objects.all():

            try:
                values = self.get_converted_values(entry.value, entry.currency_id, entry.value_date)
                self.store_converted_transaction(values)

            except Exception as e:
                print e.message


    def get_converted_values(self, current_value, current_currency, current_value_date):
        print "not implemented"
        # get conversion table
        #
        # return values

    def get_conversion_table(self, year):
        print "not implemented"
        #


    def store_converted_transaction(self, values):
        print "not implemented"
        # look if exists in transaction_converted table
        # create / update row
        # save