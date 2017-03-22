from iati.models import Activity
from traceability.models import Chain, ChainNode, ChainNodeError, ChainLink, 
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime


def contains(list, filter):
    for x in list:
        if filter(x):
            return True
    return False


def find(list, filter):
    for x in list:
        if filter(x):
            return x
    return False


class ChainRetriever():
    """
    Wrapper class for all chain building functionality

    """
    def __init__(self):
        self.nodes = []

        self.links = []
        self.link_relations = []

        self.errors = []
        self.started_at 
        self.chain = None

    def retrieve_chains_by_publisher(self, publisher_iati_id):
        for activity in Activity.objects.filter(publisher__publisher_iati_id=publisher_iati_id):
            print activity
            self.retrieve_chain(activity)

    def retrieve_chain_by_activity_id(self, activity_id):
        activity = Activity.objects.get(iati_identifier=activity_id)
        self.retrieve_chain(activity)

    def retrieve_chain_for_all_activities(self):
        for activity in Activity.objects.iterator():

            chain = Chain.objects.filter(chainlink__activity=activity)
            if len(chain) > 0 and chain.last_updated < self.started_at:
                self.retrieve_chain(activity)

            if not ChainLink.objects.filter(activity=activity).exists():
                # not in a chain yet, create the chain
                retrieve_chain(activity)


    def retrieve_chain(self, activity):

        # delete old chain
        if Chain.objects.filter(chainlink__activity=activity).count() > 0:
            Chain.objects.filter(chainlink__activity=activity).delete()

        # create, is saved as self.chain
        self.create_chain(activity)
        
        # add all links based upon the current activity
        self.get_activity_links(activity)

        # add all links based upon the links within our current activity and do that recursively
        self.walk_the_tree(0)

        # save links
        for link in self.links:
            link.pop('iati_identifier', None)
            link.pop('checked', None)

        ChainLink.objects.bulk_create([ChainLink(**link) for link in self.links])
        ChainLinkRelation.objects.bulk_create(ChainLinkRelation(**link_relation) for link_relation in self.link_relations[])

        # save errors
        ChainErrorError.objects.bulk_create([ChainNodeError(**error) for error in self.errors])


        # TODO set eol, bol, level of nodes.
        # idea:
        # to find bols, get all activities that are in the chain and are not mentioned as end_node.
        # to find eols, get all activities that are in the chain and are not mentioned as start_node.
        # to calculate levels, start with bols.

        # reinit
        self.links = []
        self.errors = []
        self.chain = None

    def create_chain(self, root_activity):
        # create chain
        chain = Chain(name="Unnamed chain", last_updated=datetime.now())
        chain.save()
        self.chain = chain

    def walk_the_tree(self, loops):

        for link in self.links:
            if not link['checked']:
                link['checked'] = True
                self.get_activity_links(link['activity'])

        if contains(self.links, lambda x: x['checked'] == False):
            loops += 1
            self.walk_the_tree(loops)

    def get_activity_links(self, activity):
        """
        Apply rules defined in the technical design.

        Rule 1.
        If it has Incoming fund with provider-activity-id  
        Then add link to reference upstream activity
        Else if they have no correct provider-activity-id set, create a broken link warning/error
        

        Rule 2.
        If it has disbursements with receiver-activity-id
        Then add link that references downstream activity
        Else if they have no correct receiver-activity-id set, create a broken link warning/error


        Rule 3.   
        If it has children as related-activity
        Then add link that references downstream activity


        Rule 4.   
        If it has parents as related-activity
        Then add link that references upstream activity


        Rule 5.   
        If it has participating-orgs not mentioned in rule 1 and 2 
        Then, depending upon role, add as possibly missing upstream or downstream links
        Upstream on role is funder and org is not the reporter of his activity. Downstream on other roles?


        Rule 6.
        If it is mentioned as provider-activity-id in incoming funds of activities
        Then add link that reference as downstream activity (direction is upwards)


        Rule 7.
        If it is mentioned as receiver-activity-id in disbursements of activities
        Then add link that reference as upstream activity (direction is downwards)


        Rule 8. = rule 1 else
        If it has provider-orgs with incorrect/missing provider-activity-id.
        Then add as broken link


        Rule 9. = rule 2 else
        If it has receiver-orgs with incorrect/missing receiver-activity-id.
        Then add as broken link

        
        # link relation types:
        ('incoming_fund', u"Incoming Fund"),
        ('disbursement', u"Disbursement"),
        ('expenditure', u"Expenditure"),
        ('incoming_commitment', u"Incoming commitment"),
        ('outgoing_commitment', u"Outgoing commitment"),
        ('expenditure', u"Expenditure"),
        ('parent', u"Parent"),
        ('child', u"Child")

        
        # node error types:
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


        # error warning level choices
            ('info', u"Info"),
            ('warning', u"Warning"),
            ('error', u"Error")
        
        # error type choices
            ('1', u"provider-org not set on incoming fund"),
            ('2', u"provider-activity-id not set on incoming fund"),
            ('3', u"given provider-activity-id set on incoming fund does not exist"),

            ('4', u"receiver-org not set on disbursement"),
            ('5', u"receiver-activity-id not set on disbursement"),
            ('6', u"given receiver-activity-id set on disbursement does not exist"),

            ('7', u"given related-activity with type parent does not exist"),
            ('8', u"given related-activity with type child does not exist"),

            ('9', u"participating-org is given as funder but there are no incoming funds from this organisation ref"),
            ('10', u"participating-org is given as implementer but there are no disbursements nor expenditures to this organisation ref")

        """

        # init 
        provider_org_refs = []
        receiver_org_refs = []

        activity_node = ChainNode.objects.get_or_create(
            activity=activity,
            defaults={
                'activity_oipa_id': activity.id,
                'activity_iati_id': activity.iati_identifier,
                'level': None,
                'bol': False,
                'eol': False
            },
        )

        # 1.
        for t in activity.transaction_set.filter(transaction_type='1'):
            try:
                provider_org = t.provider_organisation
                provider_org_refs.append(provider_org.ref)
            except ObjectDoesNotExist:
                self.add_error(activity_node, '1', '', 'error', t.id)
                continue
            if not provider_org.provider_activity_ref or provider_org.provider_activity_ref == '':
                self.add_error(activity_node, '2', '', 'error', t.id)
            elif not provider_org.provider_activity:
                self.add_error(activity_node, '3', provider_org.provider_activity_ref, 'error', t.id)
            else:
                self.add_link(provider_org.provider_activity, t.activity, 'incoming_fund', 'end_node', t.id)


        # 2.
        for t in activity.transaction_set.filter(transaction_type='3'):
            try:
                receiver_org = t.receiver_organisation
                receiver_org_refs.append(receiver_org.ref)
            except ObjectDoesNotExist:
                self.add_error(activity_node, '4', '', 'warning', t.id)
                continue
            if not receiver_org.receiver_activity_ref or receiver_org.receiver_activity_ref == '':
                self.add_error(activity_node, '5', '', 'info', t.id)
            elif not receiver_org.receiver_activity:
                self.add_error(activity_node, '6', receiver_org.receiver_activity_ref, 'error', t.id)
            else:

                self.add_link(t.activity, receiver_org.receiver_activity, 'disbursement', 'start_node', t.id)


        # 3 and 4.
        for ra in activity.relatedactivity_set.all():

            # parent
            if ra.type.code == '1':
                if not ra.ref_activity:
                    self.add_error(activity_node, '7', ra.ref, 'error', ra.id)
                else:
                    self.add_link(ra.ref_activity, activity, 'parent', 'end_node', ra.id)
            # child
            elif ra.type.code == '2':
                if not ra.ref_activity:
                    self.add_error(activity_node, '8', ra.ref, 'error', ra.id)
                else:
                    self.add_link(activity, ra.ref_activity, 'child', 'start_node', ra.id)

        # 4.
        # DONE IN #3.

        # cache for #5
        for t in activity.transaction_set.filter(transaction_type='4'):
            try:
                receiver_org = t.receiver_organisation
                receiver_org_refs.append(receiver_org.ref)
            except ObjectDoesNotExist:
                continue

        # 5.
        for ra in activity.participating_organisations.all():
            # for role funding, check if in incoming funds
            if ra.role.code == '1' and not ra.ref in provider_org_refs:
                self.add_error(activity_node, '9', ra.ref, 'info', ra.id)
            # for role implementing, check if in disbursements or expenditures
            elif ra.role.code == '4' and not ra.ref in receiver_org_refs:
                self.add_error(activity_node, '10', ra.ref, 'info', ra.id)

        # 6. 
        for a in Activity.objects.filter(transaction__transaction_type="1", transaction__provider_organisation__provider_activity_ref=activity.iati_identifier).distinct():
            self.add_link(self, activity, a, 'incoming_fund', 'end_node', 'to do')

        # 7.
        for a in Activity.objects.filter(transaction__transaction_type="3", transaction__receiver_organisation__receiver_activity_ref=activity.iati_identifier).distinct():
            self.add_link(self, a, activity, 'disbursement', 'start_node', 'to do')

        # 8.
        # DONE IN #1

        # 9.
        # DONE IN #2

    def add_link(self, start_activity, end_activity, relation, from_node, related_id):
        """
        start_activity
        end_activity
        relation: ChainLinkRelation.relation
        from: ChainLinkRelation.from : is this link made based upon data from the start_node or end_node
        related_id: ChainLinkRelation.related_id : 
        """

        # add start activity
        start_node = ChainNode.objects.get_or_create(
            activity=start_activity,
            defaults={
                'activity_oipa_id': start_activity.id,
                'activity_iati_id': start_activity.iati_identifier,
                'level': None,
                'bol': False,
                'eol': False
            },
        )

        # add end activity
        end_node = ChainNode.objects.get_or_create(
            activity=end_activity,
            defaults={
                'activity_oipa_id': end_activity.id,
                'activity_iati_id': end_activity.iati_identifier,
                'level': None,
                'bol': False,
                'eol': False
            },
        )

        # add link + relation info
        link = find(self.links, lambda x: (x['start_node'].activity == activity and x['end_node'].activity == activity)):

        if not link:
            self.links.append({
                'chain': self.chain,
                'start_node': start_node,
                'end_node': end_node,
                'relations': [
                    {
                        'relation': relation,
                        'from': from_node,
                        'related_id': related_id,
                    }
                ]
            })
        else:
            link.relations.append(
                {
                'relation': relation,
                'from': from_node,
                'related_id': related_id,
            })

    def add_error(self, chain_node, error_code, mentioned_activity_or_org, warning_level, related_id):
        self.errors.append({
            'chain_node': chain_node,
            'error_type': error_code,
            'mentioned_activity_or_org': mentioned_activity_or_org,
            'warning_level': warning_level,
            'related_id': related_id
        })


