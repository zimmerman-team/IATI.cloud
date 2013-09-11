from django.db import models
from geodata.models import country, region

class activity_date_type(models.Model):
    code = models.CharField(primary_key=True, max_length=20)
    name = models.CharField(max_length=200)


class activity_status(models.Model):
    code = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    language = models.CharField(max_length=2)

class aid_type_category(models.Model):
    code = models.CharField(primary_key=True, max_length=3)
    name = models.CharField(max_length=200)
    description = models.TextField()

class aid_type(models.Model):
    code = models.CharField(primary_key=True, max_length=3)
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(aid_type_category)

class budget_type(models.Model):
    code = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=20)
    language = models.CharField(max_length=2)

class collaboration_type(models.Model):
    code = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    language = models.CharField(max_length=2)

class condition_type(models.Model):
    code = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=40)
    language = models.CharField(max_length=2)

class currency(models.Model):
    code = models.CharField(primary_key=True, max_length=3)
    name = models.CharField(max_length=100)
    language = models.CharField(max_length=2)

class description_type(models.Model):
    code = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    description = models.TextField()

class disbursement_channel(models.Model):
    code = models.SmallIntegerField(primary_key=True)
    name = models.TextField()

class document_category(models.Model):
    code = models.CharField(primary_key=True, max_length=3)
    name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=1)
    category_name = models.CharField(max_length=30)

class file_format(models.Model):
    code = models.CharField(primary_key=True, max_length=30)
    name = models.CharField( max_length=30)

class finance_type_category(models.Model):
    code = models.IntegerField(primary_key=True)
    name = models.CharField( max_length=50)
    description = models.TextField()

class finance_type(models.Model):
    code = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=220)
    category = models.ForeignKey(finance_type_category)

class flow_type(models.Model):
    code = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=30)
    description = models.TextField()

class gazetteer_agency(models.Model):
    code = models.CharField(primary_key=True, max_length=3)
    name = models.CharField(max_length=80)

class geographical_precision(models.Model):
    code = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=80)
    description = models.TextField()

class indicator_measure(models.Model):
    code = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=40)

class language(models.Model):
    code = models.CharField(primary_key=True, max_length=2)
    name = models.CharField(max_length=80)

class location_type(models.Model):
    code = models.CharField(primary_key=True, max_length=10)
    name = models.CharField(max_length=100)

class organisation_identifier(models.Model):
    code = models.CharField(primary_key=True, max_length=20)
    abbreviation = models.CharField(max_length=30, default=None, null=True)
    name = models.CharField(max_length=250, default=None, null=True)

class organisation_role(models.Model):
    code = models.CharField(primary_key=True, max_length=20)
    name = models.CharField(max_length=20)
    description = models.TextField()

class organisation_type(models.Model):
    code = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=50)

class policy_marker(models.Model):
    code = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=200)

class policy_significance(models.Model):
    code = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()

class publisher_type(models.Model):
    code = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=50)

class related_activity_type(models.Model):
    code = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=20)
    description = models.TextField()

class result_type(models.Model):
    code = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=30)

# NEEDS SECTOR CATEGORY
class sector(models.Model):
    code = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    #category = models.ForeignKey(sector_category)

class sector_category(models.Model):
    code = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()

class tied_status(models.Model):
    code = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=40)
    description = models.TextField()


class transaction_type(models.Model):
    code = models.CharField(primary_key=True, max_length=2)
    name = models.CharField(max_length=40)
    description = models.TextField()

class value_type(models.Model):
    code = models.CharField(primary_key=True, max_length=2)
    name = models.CharField(max_length=40)
    description = models.TextField()

class verification_status(models.Model):
    code = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=20)


class vocabulary(models.Model):
    code = models.CharField(primary_key=True, max_length=10)
    name = models.CharField(max_length=140)


class organisation(models.Model):
    code = models.CharField(primary_key=True, max_length=30)
    abbreviation = models.CharField(max_length=30, null=True, default = None)
    type = models.ForeignKey(organisation_type, null=True, default = None)
    reported_by_organisation = models.CharField(max_length=100, null=True, default = None)
    name = models.CharField(max_length=250, null=True, default = None)

    def __unicode__(self):
        return self.name

    def total_activities(self):
        return self.activity_set.count()



class activity(models.Model):
    hierarchy_choices = (
        (1, u"Parent"),
        (2, u"Child"),
        )

    id = models.CharField(primary_key=True, max_length=100)
    default_currency = models.ForeignKey(currency, null=True, default = None)
    hierarchy = models.SmallIntegerField(choices=hierarchy_choices, default=1, null=True)
    last_updated_datetime = models.CharField(max_length=100, null=True, default = None)
    linked_data_uri = models.CharField(max_length=100, null=True)
    reporting_organisation = models.ForeignKey(organisation, null=True, default = None, related_name="activity_reporting_organisation")
    activity_status = models.ForeignKey(activity_status, null=True, default = None)

    start_planned = models.DateField(null=True, default = None)
    end_planned = models.DateField(null=True, default = None)
    start_actual = models.DateField(null=True, default = None)
    end_actual = models.DateField(null=True, default = None)

    participating_organisation = models.ManyToManyField(organisation, through="activity_participating_organisation")
    policy_marker = models.ManyToManyField(policy_marker, through="activity_policy_marker")
    sector = models.ManyToManyField(sector, through="activity_sector")
    recipient_country = models.ManyToManyField(country, through="activity_recipient_country")
    recipient_region = models.ManyToManyField(region, through="activity_recipient_region")

    collaboration_type = models.ForeignKey(collaboration_type, null=True, default = None)
    default_flow_type = models.ForeignKey(flow_type, null=True, default = None)
    default_aid_type = models.ForeignKey(aid_type, null=True, default = None)
    default_finance_type = models.ForeignKey(finance_type, null=True, default = None)
    default_tied_status = models.ForeignKey(tied_status, null=True, default = None)
    xml_source_ref = models.CharField(null=True, max_length=200)

    def __unicode__(self):
        return self.id

    class Meta:
        verbose_name_plural = "activities"



class activity_participating_organisation(models.Model):
    activity = models.ForeignKey(activity)
    organisation = models.ForeignKey(organisation, null=True, default = None)
    role = models.ForeignKey(organisation_role, null=True, default = None)
    name = models.TextField( null=True, default = None)

class activity_policy_marker(models.Model):
    policy_marker = models.ForeignKey(policy_marker, null=True, default = None)
    alt_policy_marker = models.CharField(max_length=200, null=True, default = None)
    activity = models.ForeignKey(activity)
    vocabulary = models.ForeignKey(vocabulary, null=True, default = None)
    policy_significance = models.ForeignKey(policy_significance, null=True, default = None)

class activity_sector(models.Model):
    activity = models.ForeignKey(activity)
    sector = models.ForeignKey(sector, null=True, default = None)
    alt_sector_name = models.CharField(max_length=200, null=True, default=None)
    vocabulary = models.ForeignKey(vocabulary, null=True, default = None)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, default = None)

class activity_recipient_country(models.Model):
    activity = models.ForeignKey(activity)
    country = models.ForeignKey(country)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, default = None)

class activity_recipient_region(models.Model):
    activity = models.ForeignKey(activity)
    region = models.ForeignKey(region)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, default = None)

class other_identifier(models.Model):
    activity = models.ForeignKey(activity)
    owner_ref = models.CharField(max_length=100, null=True, default = None)
    owner_name = models.CharField(max_length=100, null=True, default = None)
    identifier = models.CharField(max_length=100)

class activity_website(models.Model):
    activity = models.ForeignKey(activity)
    url = models.CharField(max_length=150)

#   Class not truly correct, attributes fully open
class contact_info(models.Model):
    activity = models.ForeignKey(activity)
    person_name = models.CharField(max_length=100, null=True, default = None)
    organisation = models.CharField(max_length=100, null=True, default = None)
    telephone = models.CharField(max_length=100, null=True, default = None)
    email = models.TextField(null=True, default = None)
    mailing_address = models.TextField(null=True, default = None)



class transaction(models.Model):
    activity = models.ForeignKey(activity)
    aid_type = models.ForeignKey(aid_type, null=True, default = None)
    description = models.TextField(null=True, default = None)
    description_type = models.ForeignKey(description_type, null=True, default = None)
    disbursement_channel = models.ForeignKey(disbursement_channel, null=True, default = None)
    finance_type = models.ForeignKey(finance_type, null=True, default = None)
    flow_type = models.ForeignKey(flow_type, null=True, default = None)
    provider_organisation = models.ForeignKey(organisation, related_name="transaction_providing_organisation", null=True, default = None)
    provider_activity = models.CharField(max_length=100, null=True)
    receiver_organisation = models.ForeignKey(organisation, related_name="transaction_receiving_organisation", null=True, default = None)
    tied_status = models.ForeignKey(tied_status, null=True, default = None)
    transaction_date = models.DateField(null=True, default = None)
    transaction_type = models.ForeignKey(transaction_type, null=True, default = None)
    value_date = models.DateField(null=True, default = None)
    value = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.ForeignKey(currency, null=True, default = None)
    ref = models.CharField(max_length=100, null=True, default = None)


# class transaction_description(models.Model):
#     transaction = models.ForeignKey(transaction)
#     type = models.ForeignKey(description_type, null=True, default = None)
#     language = models.ForeignKey(language, null=True, default = None)
#     description = models.TextField(null=True, default = None)


class planned_disbursement(models.Model):
    activity = models.ForeignKey(activity)
    period_start = models.CharField(max_length=100, null=True, default = None)
    period_end = models.CharField(max_length=100, null=True, default = None)
    value_date = models.DateField(null=True)
    value = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.ForeignKey(currency, null=True, default = None)
    updated = models.DateField(null=True, default = None)

class related_activity(models.Model):
    current_activity = models.ForeignKey(activity, related_name="current_activity")
    type = models.ForeignKey(related_activity_type, max_length=200, null=True, default = None)
    ref = models.CharField(max_length=200, null=True, default=None)
    text = models.TextField(null=True, default = None)

class document_link(models.Model):
    activity = models.ForeignKey(activity)
    url = models.CharField(max_length=200)
    file_format = models.ForeignKey(file_format, null=True, default = None)
    document_category = models.ForeignKey(document_category, null=True, default = None)

class result(models.Model):
    activity = models.ForeignKey(activity)
    result_type = models.ForeignKey(result_type, null=True, default = None)
    title = models.CharField(max_length=200, null=True, default = None)
    description = models.TextField(null=True, default = None)

class title(models.Model):
    activity = models.ForeignKey(activity)
    title = models.CharField(max_length=255)
    language = models.ForeignKey(language, null=True, default = None)

class description(models.Model):
    activity = models.ForeignKey(activity)
    text = models.TextField(null=True, default=None)
    language = models.ForeignKey(language, null=True, default = None)
    type = models.ForeignKey(description_type, related_name="description_type", null=True, default = None)

class budget(models.Model):
    activity = models.ForeignKey(activity)
    type = models.ForeignKey(budget_type, null=True, default = None)
    period_start = models.CharField(max_length=50, null=True, default = None)
    period_end = models.CharField(max_length=50, null=True, default = None)
    value = models.DecimalField(max_digits=12, decimal_places=2)
    value_date = models.DateField(null=True, default = None)
    currency = models.ForeignKey(currency, null=True, default = None)

class condition(models.Model):
    activity = models.ForeignKey(activity)
    text = models.TextField(null=True, default=None)
    type = models.ForeignKey(condition_type, null=True, default=None)

class location(models.Model):
    activity = models.ForeignKey(activity)
    name = models.CharField(max_length=200, null=True, default=None)
    type = models.ForeignKey(location_type, null=True, default=None)
    type_description = models.CharField(max_length=200, null=True, default=None)
    description = models.TextField(null=True, default=None)
    description_type = models.ForeignKey(description_type, null=True, default=None)
    adm_country_iso = models.ForeignKey(country, null=True, default=None)
    adm_country_adm1 = models.CharField(max_length=30, null=True, default=None)
    adm_country_adm2 = models.CharField(max_length=30, null=True, default=None)
    adm_country_name = models.CharField(max_length=200, null=True, default=None)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, default = None)
    latitude = models.CharField(max_length=70, null=True, default=None)
    longitude = models.CharField(max_length=70, null=True, default=None)
    precision = models.ForeignKey(geographical_precision, null=True, default=None)
    gazetteer_entry = models.CharField(max_length=70, null=True, default=None)
    gazetteer_ref = models.ForeignKey(gazetteer_agency, null=True, default=None)


