from django.conf.urls import url
import api.activity.views
import api.sector.views
from django.views.decorators.cache import cache_page
from OIPA.production_settings import API_CACHE_SECONDS


urlpatterns = [
    url(r'^$',
        api.activity.views.ActivityList.as_view(),
        name='activity-list'),
    url(r'^aggregations/',
        cache_page(API_CACHE_SECONDS)(api.activity.views.ActivityAggregations.as_view()),
        name='activity-aggregations'),
    url(r'^(?P<pk>[^@$&+,/:;=?]+)/$',
        api.activity.views.ActivityDetail.as_view(),
        name='activity-detail'),

    url(r'^(?P<pk>[^@$&+,/:;=?]+)/transactions/$',
        api.activity.views.ActivityTransactions.as_view(),
        name='activity-transactions'),

    url(r'^(?P<pk>[^@$&+,/:;=?]+)/transactions/(?P<id>[^@$&+,/:;=?]+)$',
        api.activity.views.ActivityTransactionDetail.as_view(),
        name='activity-transaction-detail'),

    url(r'^(?P<pk>[^@$&+,/:;=?]+)/reporting_organisations/$',
        api.activity.views.ActivityReportingOrganisationList.as_view(),
        name='activity-reporting_organisations'),
    url(r'^(?P<pk>[^@$&+,/:;=?]+)/reporting_organisations/(?P<id>[^@$&+,/:;=?]+)$',
        api.activity.views.ActivityReportingOrganisationDetail.as_view(),
        name='activity-reporting_organisations'),

    url(r'^(?P<pk>[^@$&+,/:;=?]+)/descriptions/$',
        api.activity.views.ActivityDescriptionList.as_view(),
        name='activity-descriptions'),
    url(r'^(?P<pk>[^@$&+,/:;=?]+)/descriptions/(?P<id>[^@$&+,/:;=?]+)',
        api.activity.views.ActivityDescriptionDetail.as_view(),
        name='activity-descriptions'),

    url(r'^(?P<pk>[^@$&+,/:;=?]+)/participating_organisations/$',
        api.activity.views.ActivityParticipatingOrganisationList.as_view(),
        name='activity-participating_organisations'),
    url(r'^(?P<pk>[^@$&+,/:;=?]+)/participating_organisations/(?P<id>[^@$&+,/:;=?]+)',
        api.activity.views.ActivityParticipatingOrganisationDetail.as_view(),
        name='activity-participating_organisations'),

    url(r'^(?P<pk>[^@$&+,/:;=?]+)/activity_dates/$',
        api.activity.views.ActivityActivityDateList.as_view(),
        name='activity-activity_dates'),
    url(r'^(?P<pk>[^@$&+,/:;=?]+)/activity_dates/(?P<id>[^@$&+,/:;=?]+)',
        api.activity.views.ActivityActivityDateDetail.as_view(),
        name='activity-activity_dates'),

    url(r'^(?P<pk>[^@$&+,/:;=?]+)/contact_info/$',
        api.activity.views.ActivityContactInfoList.as_view(),
        name='activity-contact_info'),
    url(r'^(?P<pk>[^@$&+,/:;=?]+)/contact_info/(?P<id>[^@$&+,/:;=?]+)',
        api.activity.views.ActivityContactInfoDetail.as_view(),
        name='activity-contact_info'),

    url(r'^(?P<pk>[^@$&+,/:;=?]+)/recipient_countries/$',
        api.activity.views.ActivityRecipientCountryList.as_view(),
        name='activity-recipient_countrys'),
    url(r'^(?P<pk>[^@$&+,/:;=?]+)/recipient_countries/(?P<id>[^@$&+,/:;=?]+)',
        api.activity.views.ActivityRecipientCountryDetail.as_view(),
        name='activity-recipient_countries'),

    url(r'^(?P<pk>[^@$&+,/:;=?]+)/recipient_regions/$',
        api.activity.views.ActivityRecipientRegionList.as_view(),
        name='activity-recipient_regions'),
    url(r'^(?P<pk>[^@$&+,/:;=?]+)/recipient_regions/(?P<id>[^@$&+,/:;=?]+)',
        api.activity.views.ActivityRecipientRegionDetail.as_view(),
        name='activity-recipient_regions'),


    url(r'^(?P<pk>[^@$&+,/:;=?]+)/recipient_sectors/$',
        api.activity.views.ActivitySectorList.as_view(),
        name='activity-recipient_sectors'),
    url(r'^(?P<pk>[^@$&+,/:;=?]+)/recipient_sectors/(?P<id>[^@$&+,/:;=?]+)',
        api.activity.views.ActivitySectorDetail.as_view(),
        name='activity-recipient_sectors'),


    url(r'^(?P<pk>[^@$&+,/:;=?]+)/locations/$',
        api.activity.views.ActivityLocationList.as_view(),
        name='activity-locations'),
    url(r'^(?P<pk>[^@$&+,/:;=?]+)/locations/(?P<id>[^@$&+,/:;=?]+)',
        api.activity.views.ActivityLocationDetail.as_view(),
        name='activity-locations'),


    url(r'^(?P<pk>[^@$&+,/:;=?]+)/sectors/$',
        api.activity.views.ActivitySectorList.as_view(),
        name='activity-sectors'),
    url(r'^(?P<pk>[^@$&+,/:;=?]+)/sectors/(?P<id>[^@$&+,/:;=?]+)',
        api.activity.views.ActivitySectorDetail.as_view(),
        name='activity-sectors'),

    url(r'^(?P<pk>[^@$&+,/:;=?]+)/humanitarian_scopes/$',
        api.activity.views.ActivityHumanitarianScopeList.as_view(),
        name='activity-humanitarian_scopes'),
    url(r'^(?P<pk>[^@$&+,/:;=?]+)/humanitarian_scopes/(?P<id>[^@$&+,/:;=?]+)',
        api.activity.views.ActivityHumanitarianScopeDetail.as_view(),
        name='activity-humanitarian_scopes'),

    url(r'^(?P<pk>[^@$&+,/:;=?]+)/policy_markers/$',
        api.activity.views.ActivityPolicyMarkerList.as_view(),
        name='activity-policy_markers'),
    url(r'^(?P<pk>[^@$&+,/:;=?]+)/policy_markers/(?P<id>[^@$&+,/:;=?]+)',
        api.activity.views.ActivityPolicyMarkerDetail.as_view(),
        name='activity-policy_markers'),

    url(r'^(?P<pk>[^@$&+,/:;=?]+)/budgets/$',
        api.activity.views.ActivityBudgetList.as_view(),
        name='activity-budgets'),
    url(r'^(?P<pk>[^@$&+,/:;=?]+)/budgets/(?P<id>[^@$&+,/:;=?]+)',
        api.activity.views.ActivityBudgetDetail.as_view(),
        name='activity-budgets'),

    url(r'^(?P<pk>[^@$&+,/:;=?]+)/planned_disbursements/$',
        api.activity.views.ActivityPlannedDisbursementList.as_view(),
        name='activity-planned_disbursements'),
    url(r'^(?P<pk>[^@$&+,/:;=?]+)/planned_disbursements/(?P<id>[^@$&+,/:;=?]+)',
        api.activity.views.ActivityPlannedDisbursementDetail.as_view(),
        name='activity-planned_disbursements'),

    url(r'^(?P<pk>[^@$&+,/:;=?]+)/document_links/$',
        api.activity.views.ActivityDocumentLinkList.as_view(),
        name='activity-document_links'),
    url(r'^(?P<pk>[^@$&+,/:;=?]+)/document_links/(?P<id>[^@$&+,/:;=?]+)',
        api.activity.views.ActivityDocumentLinkDetail.as_view(),
        name='activity-document_links'),

    url(r'^(?P<pk>[^@$&+,/:;=?]+)/related_activities/$',
        api.activity.views.ActivityRelatedActivityList.as_view(),
        name='activity-related_activities'),
    url(r'^(?P<pk>[^@$&+,/:;=?]+)/related_activities/(?P<id>[^@$&+,/:;=?]+)',
        api.activity.views.ActivityRelatedActivityDetail.as_view(),
        name='activity-related_activities'),

    url(r'^(?P<pk>[^@$&+,/:;=?]+)/results/$',
        api.activity.views.ActivityResultList.as_view(),
        name='activity-result-list'),
    url(r'^(?P<pk>[^@$&+,/:;=?]+)/results/(?P<id>[^@$&+,/:;=?]+)$',
        api.activity.views.ActivityResultDetail.as_view(),
        name='activity-result-detail'),

    url(r'^(?P<activity_id>[^@$&+,/:;=?]+)/results/(?P<result_id>[^@$&+,/:;=?]+)/result_indicators/$',
        api.activity.views.ResultIndicatorList.as_view(),
        name='activity-result_indicator-list'),
    url(r'^(?P<activity_id>[^@$&+,/:;=?]+)/results/(?P<result_id>[^@$&+,/:;=?]+)/result_indicators/(?P<resultindicator_id>[^@$&+,/:;=?]+)$',
        api.activity.views.ResultIndicatorDetail.as_view(),
        name='activity-result_indicator-detail'),

    url(r'^(?P<pk>[^@$&+,/:;=?]+)/provider-activity-tree/$',
        api.activity.views.ActivityProviderActivityTree.as_view(),
        name='provider-activity-tree'),]
