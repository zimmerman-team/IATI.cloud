from django.db import models
from iati.models import Activity
from django.utils.timezone import now

# Networks should be based upon orgs in the org standard

# class Network(models.Model):

# class NetworkLink(models.Model):

# class NetworkError(models.Model):

# class NetworkOrganisation(models.Model):


class Chain(models.Model):
    # chains have no name
    name = models.CharField(max_length=255, blank=False)
    last_updated = models.DateTimeField(default=now)

    def __unicode__(self):
        return self.name


class ChainNode(models.Model):
    chain = models.ForeignKey(Chain, null=False)
    activity = models.ForeignKey(Activity, null=True)
    activity_oipa_id = models.IntegerField(blank=False)
    activity_iati_id = models.CharField(max_length=255, blank=False)
    tier = models.IntegerField(null=True, default=None)
    bol = models.BooleanField(default=False)
    eol = models.BooleanField(default=False)
    checked = models.BooleanField(default=False)
    treated_as_end_node = models.BooleanField(default=False)

    def __unicode__(self):
        return self.activity_iati_id


class ChainNodeError(models.Model):
    level_choices = (
        ('info', u"Info"),
        ('warning', u"Warning"),
        ('error', u"Error")
    )

    error_type_choices = (
        ('1', u"provider-org not set on incoming fund"),
        ('2', u"provider-activity-id not set on incoming fund"),
        ('3', u"given provider-activity-id set on incoming fund does not exist"),

        ('4', u"receiver-org not set on disbursement"),
        ('5', u"receiver-activity-id not set on disbursement"),
        ('6', u"given receiver-activity-id set on disbursement does not exist"),

        ('7', u"given related-activity with type parent does not exist"),
        ('8', u"given related-activity with type child does not exist"),

        ('9', u"participating-org is given as funder but there are no incoming funds from this organisation ref"),
        ('10', u"participating-org is given as implementer but there are no disbursements nor expenditures to this organisation ref"),
    )

    chain_node = models.ForeignKey(ChainNode)
    error_type = models.CharField(choices=level_choices, max_length=10, null=False)
    mentioned_activity_or_org = models.CharField(
        max_length=255, null=True, blank=False, default=None)
    related_id = models.CharField(max_length=100)
    warning_level = models.CharField(choices=level_choices, max_length=255, null=False)


class ChainLink(models.Model):
    chain = models.ForeignKey(Chain, null=False)
    start_node = models.ForeignKey(ChainNode, null=False, related_name='start_link')
    end_node = models.ForeignKey(ChainNode, null=False, related_name='end_link')


class ChainLinkRelation(models.Model):
    relation_choices = (
        ('incoming_fund', u"Incoming Fund"),
        ('disbursement', u"Disbursement"),
        ('expenditure', u"Expenditure"),
        ('incoming_commitment', u"Incoming commitment"),
        ('outgoing_commitment', u"Outgoing commitment"),
        ('expenditure', u"Expenditure"),
        ('parent', u"Parent"),
        ('child', u"Child")
    )

    from_choices = (
        ('start_node', u"Start node"),
        ('end_node', u"End node")
    )

    chain_link = models.ForeignKey(ChainLink, related_name='relations')
    relation = models.CharField(choices=relation_choices, max_length=30)
    from_node = models.CharField(choices=from_choices, max_length=10)
    related_id = models.CharField(max_length=100)
