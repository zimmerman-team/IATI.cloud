from django.conf.urls import url
from api.publisher import views

import api

from api.transaction.views import TransactionSectorList, TransactionSectorDetail

urlpatterns = [
    url(r'^$', 
        views.PublisherList.as_view(), 
        name='publisher-list'
    ),
    url(
        r'^(?P<pk>[^@$&+,/:;=?]+)/$',
        views.PublisherDetail.as_view(),
        name='publisher-detail'
    ),

    #
    # IATI Studio groups and admin groups, used for managing publishing rights
    #

    url(
        r'^(?P<publisher_id>[^@$&+,/:;=?]+)/admin-group/$',
        views.OrganisationAdminGroupView.as_view(),
        name='publisher-admingroup-list'
    ),
    url(
        r'^(?P<publisher_id>[^@$&+,/:;=?]+)/admin-group/(?P<id>[^@$&+,/:;=?]+)$',
        views.OrganisationAdminGroupDetailView.as_view(),
        name='publisher-admingroup-detail'
    ),
    url(
        r'^(?P<publisher_id>[^@$&+,/:;=?]+)/group/$',
        views.OrganisationGroupView.as_view(),
        name='publisher-group-list'
    ),
    url(
        r'^(?P<publisher_id>[^@$&+,/:;=?]+)/group/(?P<id>[^@$&+,/:;=?]+)$',
        views.OrganisationGroupDetailView.as_view(),
        name='publisher-group-detail'
    ),
    # verify API key and add user to the corresponding admin group
    url(
        r'^api_key/verify/$',
        views.OrganisationVerifyApiKey.as_view(),
        name='publisher-verify-api-key'
    ),
    # remove the API key and remove the user from the corresponding admin group
    url(
        r'^api_key/remove/$',
        views.OrganisationRemoveApiKey.as_view(),
        name='publisher-verify-api-key'
    ),

    #
    # For publishing
    #

    # get all activities that are ready to be published + the ones that are published
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/next_published_activities/$',
        api.export.views.IATIActivityNextExportList.as_view(),
        name='activity-nextexport-list'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/next_published_activities/(?P<job_id>[^@$+,/;=?]+)$',
        api.export.views.IATIActivityNextExportListResult.as_view(),
        name='activity-nextexport-list'),
    
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/mark_ready_to_publish$',
        api.activity.views.ActivityMarkReadyToPublish.as_view(),
        name='activity-mark-ready-to-publish'
        ),
    
    #
    # Activity CRUD
    #

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/$',
        api.activity.views.ActivityListCRUD.as_view(),
        name='activity-detail'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/$',
        api.activity.views.ActivityDetailCRUD.as_view(),
        name='activity-detail'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/transactions/$',
        api.activity.views.ActivityTransactionListCRUD.as_view(),
        name='activity-transactions'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/transactions/(?P<id>[^@$&+,/:;=?]+)$',
        api.activity.views.ActivityTransactionDetailCRUD.as_view(),
        name='activity-transaction-detail'),


    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<activity_id>[^@$&+,/:;=?]+)/transactions/(?P<pk>[^@$&+,/:;=?]+)/sectors/$',
        TransactionSectorList.as_view(),
        name='transaction-sectors'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<activity_id>[^@$&+,/:;=?]+)/transactions/(?P<pk>[^@$&+,/:;=?]+)/sectors/(?P<id>[^@$&+,/:;=?]+)/$',
        TransactionSectorDetail.as_view(),
        name='activity-sectors-detail'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/reporting_organisations/$',
        api.activity.views.ActivityReportingOrganisationList.as_view(),
        name='activity-reporting_organisations'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/reporting_organisations/(?P<id>[^@$&+,/:;=?]+)$',
        api.activity.views.ActivityReportingOrganisationDetail.as_view(),
        name='activity-reporting_organisations'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/descriptions/$',
        api.activity.views.ActivityDescriptionList.as_view(),
        name='activity-descriptions'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/descriptions/(?P<id>[^@$&+,/:;=?]+)',
        api.activity.views.ActivityDescriptionDetail.as_view(),
        name='activity-descriptions'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/participating_organisations/$',
        api.activity.views.ActivityParticipatingOrganisationList.as_view(),
        name='activity-participating_organisations'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/participating_organisations/(?P<id>[^@$&+,/:;=?]+)',
        api.activity.views.ActivityParticipatingOrganisationDetail.as_view(),
        name='activity-participating_organisations'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/other_identifiers/$',
        api.activity.views.ActivityOtherIdentifierList.as_view(),
        name='activity-other_identifiers'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/other_identifiers/(?P<id>[^@$&+,/:;=?]+)',
        api.activity.views.ActivityOtherIdentifierDetail.as_view(),
        name='activity-other_identifiers'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/activity_dates/$',
        api.activity.views.ActivityActivityDateList.as_view(),
        name='activity-activity_dates'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/activity_dates/(?P<id>[^@$&+,/:;=?]+)',
        api.activity.views.ActivityActivityDateDetail.as_view(),
        name='activity-activity_dates'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/contact_info/$',
        api.activity.views.ActivityContactInfoList.as_view(),
        name='activity-contact_info'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/contact_info/(?P<id>[^@$&+,/:;=?]+)',
        api.activity.views.ActivityContactInfoDetail.as_view(),
        name='activity-contact_info'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/recipient_countries/$',
        api.activity.views.ActivityRecipientCountryList.as_view(),
        name='activity-recipient_countrys'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/recipient_countries/(?P<id>[^@$&+,/:;=?]+)',
        api.activity.views.ActivityRecipientCountryDetail.as_view(),
        name='activity-recipient_countries'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/recipient_regions/$',
        api.activity.views.ActivityRecipientRegionList.as_view(),
        name='activity-recipient_regions'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/recipient_regions/(?P<id>[^@$&+,/:;=?]+)',
        api.activity.views.ActivityRecipientRegionDetail.as_view(),
        name='activity-recipient_regions'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/sectors/$',
        api.activity.views.ActivitySectorList.as_view(),
        name='activity-sectors'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/sectors/(?P<id>[^@$&+,/:;=?]+)',
        api.activity.views.ActivitySectorDetail.as_view(),
        name='activity-sectors'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/locations/$',
        api.activity.views.ActivityLocationList.as_view(),
        name='activity-locations'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/locations/(?P<id>[^@$&+,/:;=?]+)',
        api.activity.views.ActivityLocationDetail.as_view(),
        name='activity-locations'),

    # url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/country_budget_items/(?P<id>[^@$&+,/:;=?]+)',
    #     api.activity.views.ActivityCountryBudgetItemDetail.as_view(),
    #     name='activity-country_budget_items'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/country_budget_items/$',
        api.activity.views.ActivityCountryBudgetItemDetail.as_view(),
        name='activity-country_budget_items'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/country_budget_items/budget_items/$',
        api.activity.views.ActivityBudgetItemList.as_view(),
        name='activity-budget_items-list'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/country_budget_items/budget_items/(?P<budget_item_id>[^@$&+,/:;=?]+)',
        api.activity.views.ActivityBudgetItemDetail.as_view(),
        name='activity-budget_items-detail'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/humanitarian_scopes/$',
        api.activity.views.ActivityHumanitarianScopeList.as_view(),
        name='activity-humanitarian_scopes'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/humanitarian_scopes/(?P<id>[^@$&+,/:;=?]+)',
        api.activity.views.ActivityHumanitarianScopeDetail.as_view(),
        name='activity-humanitarian_scopes'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/policy_markers/$',
        api.activity.views.ActivityPolicyMarkerList.as_view(),
        name='activity-policy_markers'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/policy_markers/(?P<id>[^@$&+,/:;=?]+)',
        api.activity.views.ActivityPolicyMarkerDetail.as_view(),
        name='activity-policy_markers'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/budgets/$',
        api.activity.views.ActivityBudgetList.as_view(),
        name='activity-budgets'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/budgets/(?P<id>[^@$&+,/:;=?]+)',
        api.activity.views.ActivityBudgetDetail.as_view(),
        name='activity-budgets'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/planned_disbursements/$',
        api.activity.views.ActivityPlannedDisbursementList.as_view(),
        name='activity-planned_disbursements'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/planned_disbursements/(?P<id>[^@$&+,/:;=?]+)',
        api.activity.views.ActivityPlannedDisbursementDetail.as_view(),
        name='activity-planned_disbursements'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/document_links/$',
        api.activity.views.ActivityDocumentLinkList.as_view(),
        name='activity-document_links'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/document_links/(?P<id>[^@$&+,/:;=?]+)$',
        api.activity.views.ActivityDocumentLinkDetail.as_view(),
        name='activity-document_links'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<activity_id>[^@$&+,/:;=?]+)/document_links/(?P<document_link_id>[^@$&+,/:;=?]+)/categories/$',
        api.activity.views.ActivityDocumentLinkCategoryList.as_view(),
        name='activity-document_link_category-list'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<activity_id>[^@$&+,/:;=?]+)/document_links/(?P<document_link_id>[^@$&+,/:;=?]+)/categories/(?P<category_id>[^@$&+,/:;=?]+)$',
        api.activity.views.ActivityDocumentLinkCategoryDetail.as_view(),
        name='activity-document_link_category-detail'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<activity_id>[^@$&+,/:;=?]+)/document_links/(?P<document_link_id>[^@$&+,/:;=?]+)/languages/$',
        api.activity.views.ActivityDocumentLinkLanguageList.as_view(),
        name='activity-document_link_language-list'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<activity_id>[^@$&+,/:;=?]+)/document_links/(?P<document_link_id>[^@$&+,/:;=?]+)/languages/(?P<language_id>[^@$&+,/:;=?]+)$',
        api.activity.views.ActivityDocumentLinkLanguageDetail.as_view(),
        name='activity-document_link_language-detail'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/related_activities/$',
        api.activity.views.ActivityRelatedActivityList.as_view(),
        name='activity-related_activities'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/related_activities/(?P<id>[^@$&+,/:;=?]+)',
        api.activity.views.ActivityRelatedActivityDetail.as_view(),
        name='activity-related_activities'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/legacy_data/$',
        api.activity.views.ActivityLegacyDataList.as_view(),
        name='activity-legacy_data-list'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/legacy_data/(?P<id>[^@$&+,/:;=?]+)$',
        api.activity.views.ActivityLegacyDataDetail.as_view(),
        name='activity-legacy_data-detail'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/results/$',
        api.activity.views.ActivityResultList.as_view(),
        name='activity-result-list'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/results/(?P<id>[^@$&+,/:;=?]+)$',
        api.activity.views.ActivityResultDetail.as_view(),
        name='activity-result-detail'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<activity_id>[^@$&+,/:;=?]+)/results/(?P<result_id>[^@$&+,/:;=?]+)/indicators/$',
        api.activity.views.ResultIndicatorList.as_view(),
        name='activity-result_indicator-list'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<activity_id>[^@$&+,/:;=?]+)/results/(?P<result_id>[^@$&+,/:;=?]+)/indicators/(?P<resultindicator_id>[^@$&+,/:;=?]+)$',
        api.activity.views.ResultIndicatorDetail.as_view(),
        name='activity-result_indicator-detail'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<activity_id>[^@$&+,/:;=?]+)/results/(?P<result_id>[^@$&+,/:;=?]+)/indicators/(?P<resultindicator_id>[^@$&+,/:;=?]+)/references/$',
        api.activity.views.ResultIndicatorReferenceList.as_view(),
        name='activity-result_indicator_reference-list'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<activity_id>[^@$&+,/:;=?]+)/results/(?P<result_id>[^@$&+,/:;=?]+)/indicators/(?P<resultindicator_id>[^@$&+,/:;=?]+)/references/(?P<reference_id>[^@$&+,/:;=?]+)$',
        api.activity.views.ResultIndicatorReferenceDetail.as_view(),
        name='activity-result_indicator_reference-detail'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<activity_id>[^@$&+,/:;=?]+)/results/(?P<result_id>[^@$&+,/:;=?]+)/indicators/(?P<resultindicator_id>[^@$&+,/:;=?]+)/periods/$',
        api.activity.views.ResultIndicatorPeriodList.as_view(),
        name='activity-result_indicator_period-list'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<activity_id>[^@$&+,/:;=?]+)/results/(?P<result_id>[^@$&+,/:;=?]+)/indicators/(?P<resultindicator_id>[^@$&+,/:;=?]+)/periods/(?P<period_id>[^@$&+,/:;=?]+)$',
        api.activity.views.ResultIndicatorPeriodDetail.as_view(),
        name='activity-result_indicator_period-detail'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<activity_id>[^@$&+,/:;=?]+)/results/(?P<result_id>[^@$&+,/:;=?]+)/indicators/(?P<resultindicator_id>[^@$&+,/:;=?]+)/periods/(?P<period_id>[^@$&+,/:;=?]+)/actual/location/$',
        api.activity.views.ResultIndicatorPeriodActualLocationList.as_view(),
        name='activity-result_indicator_period_actual_location-list'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<activity_id>[^@$&+,/:;=?]+)/results/(?P<result_id>[^@$&+,/:;=?]+)/indicators/(?P<resultindicator_id>[^@$&+,/:;=?]+)/periods/(?P<period_id>[^@$&+,/:;=?]+)/actual/location/(?P<actual_location_id>[^@$&+,/:;=?]+)$',
        api.activity.views.ResultIndicatorPeriodActualLocationDetail.as_view(),
        name='activity-result_indicator_period_actual_location-detail'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<activity_id>[^@$&+,/:;=?]+)/results/(?P<result_id>[^@$&+,/:;=?]+)/indicators/(?P<resultindicator_id>[^@$&+,/:;=?]+)/periods/(?P<period_id>[^@$&+,/:;=?]+)/target/location/$',
        api.activity.views.ResultIndicatorPeriodTargetLocationList.as_view(),
        name='activity-result_indicator_period_target_location-list'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<activity_id>[^@$&+,/:;=?]+)/results/(?P<result_id>[^@$&+,/:;=?]+)/indicators/(?P<resultindicator_id>[^@$&+,/:;=?]+)/periods/(?P<period_id>[^@$&+,/:;=?]+)/target/location/(?P<target_location_id>[^@$&+,/:;=?]+)$',
        api.activity.views.ResultIndicatorPeriodTargetLocationDetail.as_view(),
        name='activity-result_indicator_period_target_location-detail'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<activity_id>[^@$&+,/:;=?]+)/results/(?P<result_id>[^@$&+,/:;=?]+)/indicators/(?P<resultindicator_id>[^@$&+,/:;=?]+)/periods/(?P<period_id>[^@$&+,/:;=?]+)/actual/dimension/$',
        api.activity.views.ResultIndicatorPeriodActualDimensionList.as_view(),
        name='activity-result_indicator_period_actual_dimension-list'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<activity_id>[^@$&+,/:;=?]+)/results/(?P<result_id>[^@$&+,/:;=?]+)/indicators/(?P<resultindicator_id>[^@$&+,/:;=?]+)/periods/(?P<period_id>[^@$&+,/:;=?]+)/actual/dimension/(?P<actual_dimension_id>[^@$&+,/:;=?]+)$',
        api.activity.views.ResultIndicatorPeriodActualDimensionDetail.as_view(),
        name='activity-result_indicator_period_actual_dimension-detail'),


    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<activity_id>[^@$&+,/:;=?]+)/results/(?P<result_id>[^@$&+,/:;=?]+)/indicators/(?P<resultindicator_id>[^@$&+,/:;=?]+)/periods/(?P<period_id>[^@$&+,/:;=?]+)/target/dimension/$',
        api.activity.views.ResultIndicatorPeriodTargetDimensionList.as_view(),
        name='activity-result_indicator_period_target_dimension-list'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<activity_id>[^@$&+,/:;=?]+)/results/(?P<result_id>[^@$&+,/:;=?]+)/indicators/(?P<resultindicator_id>[^@$&+,/:;=?]+)/periods/(?P<period_id>[^@$&+,/:;=?]+)/target/dimension/(?P<target_dimension_id>[^@$&+,/:;=?]+)$',
        api.activity.views.ResultIndicatorPeriodTargetDimensionDetail.as_view(),
        name='activity-result_indicator_period_target_dimension-detail'),
    

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/crs_add/$',
        api.activity.views.ActivityCrsAddList.as_view(),
        name='activity-crs_add-list'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/crs_add/(?P<id>[^@$&+,/:;=?]+)$',
        api.activity.views.ActivityCrsAddDetail.as_view(),
        name='activity-crs_add-detail'),


    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/crs_add/(?P<id>[^@$&+,/:;=?]+)/other_flags/$',
        api.activity.views.ActivityCrsAddOtherFlagsList.as_view(),
        name='activity-other_flags-list'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/crs_add/(?P<id>[^@$&+,/:;=?]+)/other_flags/(?P<other_flags_id>[^@$&+,/:;=?]+)$',
        api.activity.views.ActivityCrsAddOtherFlagsDetail.as_view(),
        name='activity-other_flags-detail'),


    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/fss/$',
        api.activity.views.ActivityFssList.as_view(),
        name='activity-fss-list'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/fss/(?P<id>[^@$&+,/:;=?]+)$',
        api.activity.views.ActivityFssDetail.as_view(),
        name='activity-fss-detail'),


    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/fss/(?P<id>[^@$&+,/:;=?]+)/forecast/$',
        api.activity.views.ActivityFssForecastList.as_view(),
        name='activity-fss-list'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/fss/(?P<id>[^@$&+,/:;=?]+)/forecast/(?P<forecast_id>[^@$&+,/:;=?]+)$',
        api.activity.views.ActivityFssForecastDetail.as_view(),
        name='activity-fss-detail'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/conditions/$',
        api.activity.views.ActivityConditionsDetail.as_view(),
        name='activity-conditions'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/conditions/condition/$',
        api.activity.views.ActivityConditionList.as_view(),
        name='activity-conditions-list'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/conditions/condition/(?P<condition_id>[^@$&+,/:;=?]+)',
        api.activity.views.ActivityConditionDetail.as_view(),
        name='activity-conditions-detail'),

    #
    # Organisation CRUD
    #

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/organisations/$',
            api.organisation.views.OrganisationListCRUD.as_view(),
            name='organisation-list'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/organisations/(?P<pk>[^@$&+,/:;=?]+)/$',
            api.organisation.views.OrganisationDetailCRUD.as_view(),
            name='organisation-detail'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/organisations/(?P<pk>[^@$&+,/:;=?]+)/total_budgets/$',
            api.organisation.views.OrganisationTotalBudgetListCRUD.as_view(),
            name='organisation-total_budget-list'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/organisations/(?P<pk>[^@$&+,/:;=?]+)/total_budgets/(?P<id>[^@$&+,/:;=?]+)$',
            api.organisation.views.OrganisationTotalBudgetDetailCRUD.as_view(),
            name='organisation-total_budget-detail'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/organisations/(?P<pk>[^@$&+,/:;=?]+)/recipient_org_budgets/$',
            api.organisation.views.OrganisationRecipientOrgBudgetListCRUD.as_view(),
            name='organisation-recipient_org_budget-list'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/organisations/(?P<pk>[^@$&+,/:;=?]+)/recipient_org_budgets/(?P<id>[^@$&+,/:;=?]+)$',
            api.organisation.views.OrganisationRecipientOrgBudgetDetailCRUD.as_view(),
            name='organisation-recipient_org_budget-detail'),
]

