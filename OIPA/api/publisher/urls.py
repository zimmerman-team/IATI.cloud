from django.conf.urls import url

import api
from api.export_organisation.views import OrganisationNextExportList
from api.publisher import views
from api.transaction.views import (
    TransactionSectorDetail, TransactionSectorList
)

app_name = 'api'
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
        r'^(?P<publisher_id>[^@$&+,/:;=?]+)/admin-group/(?P<id>[^@$&+,/:;=?]+)$',  # NOQA: E501
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

    # get all activities that are ready to be published + the ones that are
    # published
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/next_published_activities/$',
        api.export.views.IATIActivityNextExportList.as_view(),
        name='activity-nextexport-list'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/next_published_activities/(?P<job_id>[^@$+,/;=?]+)$',  # NOQA: E501
        api.export.views.IATIActivityNextExportListResult.as_view(),
        name='activity-nextexport-list'),

    # get all organisations that are ready to be published + the ones that are
    # published
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/next_published_organisations/$',
        OrganisationNextExportList,
        name='organisation-nextexport-list'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/mark_ready_to_publish$',  # NOQA: E501
        api.activity.views.ActivityMarkReadyToPublish.as_view(),
        name='activity-mark-ready-to-publish'
        ),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/organisations/(?P<pk>[^@$&+,/:;=?]+)/mark_ready_to_publish$',  # NOQA: E501
        api.organisation.views.OrganisationMarkReadyToPublish.as_view(),
        name='organisation-mark-ready-to-publish'
        ),

    #
    # Activity CRUD
    #

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/$',
        api.activity.views.ActivityListCRUD.as_view(),
        name='activity-detail'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/$',  # NOQA: E501
        api.activity.views.ActivityDetailCRUD.as_view(),
        name='activity-detail'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/transactions/$',  # NOQA: E501
        api.activity.views.ActivityTransactionListCRUD.as_view(),
        name='activity-transactions'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/transactions/(?P<id>[^@$&+,/:;=?]+)$',  # NOQA: E501
        api.activity.views.ActivityTransactionDetailCRUD.as_view(),
        name='activity-transaction-detail'),


    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<activity_id>[^@$&+,/:;=?]+)/transactions/(?P<pk>[^@$&+,/:;=?]+)/sectors/$',  # NOQA: E501
        TransactionSectorList.as_view(),
        name='transaction-sectors'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<activity_id>[^@$&+,/:;=?]+)/transactions/(?P<pk>[^@$&+,/:;=?]+)/sectors/(?P<id>[^@$&+,/:;=?]+)/$',  # NOQA: E501
        TransactionSectorDetail.as_view(),
        name='activity-sectors-detail'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/reporting_organisations/$',  # NOQA: E501
        api.activity.views.ActivityReportingOrganisationList.as_view(),
        name='activity-reporting_organisations'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/reporting_organisations/(?P<id>[^@$&+,/:;=?]+)$',  # NOQA: E501
        api.activity.views.ActivityReportingOrganisationDetail.as_view(),
        name='activity-reporting_organisations'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/descriptions/$',  # NOQA: E501
        api.activity.views.ActivityDescriptionList.as_view(),
        name='activity-descriptions'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/descriptions/(?P<id>[^@$&+,/:;=?]+)',  # NOQA: E501
        api.activity.views.ActivityDescriptionDetail.as_view(),
        name='activity-descriptions'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/participating_organisations/$',  # NOQA: E501
        api.activity.views.ActivityParticipatingOrganisationList.as_view(),
        name='activity-participating_organisations'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/participating_organisations/(?P<id>[^@$&+,/:;=?]+)',  # NOQA: E501
        api.activity.views.ActivityParticipatingOrganisationDetail.as_view(),
        name='activity-participating_organisations'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/other_identifiers/$',  # NOQA: E501
        api.activity.views.ActivityOtherIdentifierList.as_view(),
        name='activity-other_identifiers'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/other_identifiers/(?P<id>[^@$&+,/:;=?]+)',  # NOQA: E501
        api.activity.views.ActivityOtherIdentifierDetail.as_view(),
        name='activity-other_identifiers'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/activity_dates/$',  # NOQA: E501
        api.activity.views.ActivityActivityDateList.as_view(),
        name='activity-activity_dates'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/activity_dates/(?P<id>[^@$&+,/:;=?]+)',  # NOQA: E501
        api.activity.views.ActivityActivityDateDetail.as_view(),
        name='activity-activity_dates'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/contact_info/$',  # NOQA: E501
        api.activity.views.ActivityContactInfoList.as_view(),
        name='activity-contact_info'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/contact_info/(?P<id>[^@$&+,/:;=?]+)',  # NOQA: E501
        api.activity.views.ActivityContactInfoDetail.as_view(),
        name='activity-contact_info'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/recipient_countries/$',  # NOQA: E501
        api.activity.views.ActivityRecipientCountryList.as_view(),
        name='activity-recipient_countries'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/recipient_countries/(?P<id>[^@$&+,/:;=?]+)',  # NOQA: E501
        api.activity.views.ActivityRecipientCountryDetail.as_view(),
        name='activity-recipient_countries'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/recipient_regions/$',  # NOQA: E501
        api.activity.views.ActivityRecipientRegionList.as_view(),
        name='activity-recipient_regions'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/recipient_regions/(?P<id>[^@$&+,/:;=?]+)',  # NOQA: E501
        api.activity.views.ActivityRecipientRegionDetail.as_view(),
        name='activity-recipient_regions'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/sectors/$',  # NOQA: E501
        api.activity.views.ActivitySectorList.as_view(),
        name='activity-sectors'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/sectors/(?P<id>[^@$&+,/:;=?]+)',  # NOQA: E501
        api.activity.views.ActivitySectorDetail.as_view(),
        name='activity-sectors'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/locations/$',  # NOQA: E501
        api.activity.views.ActivityLocationList.as_view(),
        name='activity-locations'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/locations/(?P<id>[^@$&+,/:;=?]+)',  # NOQA: E501
        api.activity.views.ActivityLocationDetail.as_view(),
        name='activity-locations'),

    # url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/country_budget_items/(?P<id>[^@$&+,/:;=?]+)',
    #     api.activity.views.ActivityCountryBudgetItemDetail.as_view(),
    #     name='activity-country_budget_items'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/country_budget_items/$',  # NOQA: E501
        api.activity.views.ActivityCountryBudgetItemDetail.as_view(),
        name='activity-country_budget_items'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/country_budget_items/budget_items/$',  # NOQA: E501
        api.activity.views.ActivityBudgetItemList.as_view(),
        name='activity-budget_items-list'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/country_budget_items/budget_items/(?P<budget_item_id>[^@$&+,/:;=?]+)',  # NOQA: E501
        api.activity.views.ActivityBudgetItemDetail.as_view(),
        name='activity-budget_items-detail'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/humanitarian_scopes/$',  # NOQA: E501
        api.activity.views.ActivityHumanitarianScopeList.as_view(),
        name='activity-humanitarian_scopes'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/humanitarian_scopes/(?P<id>[^@$&+,/:;=?]+)',  # NOQA: E501
        api.activity.views.ActivityHumanitarianScopeDetail.as_view(),
        name='activity-humanitarian_scopes'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/policy_markers/$',  # NOQA: E501
        api.activity.views.ActivityPolicyMarkerList.as_view(),
        name='activity-policy_markers'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/policy_markers/(?P<id>[^@$&+,/:;=?]+)',  # NOQA: E501
        api.activity.views.ActivityPolicyMarkerDetail.as_view(),
        name='activity-policy_markers'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/budgets/$',  # NOQA: E501
        api.activity.views.ActivityBudgetList.as_view(),
        name='activity-budgets'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/budgets/(?P<id>[^@$&+,/:;=?]+)',  # NOQA: E501
        api.activity.views.ActivityBudgetDetail.as_view(),
        name='activity-budgets'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/planned_disbursements/$',  # NOQA: E501
        api.activity.views.ActivityPlannedDisbursementList.as_view(),
        name='activity-planned_disbursements'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/planned_disbursements/(?P<id>[^@$&+,/:;=?]+)',  # NOQA: E501
        api.activity.views.ActivityPlannedDisbursementDetail.as_view(),
        name='activity-planned_disbursements'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/document_links/$',  # NOQA: E501
        api.activity.views.ActivityDocumentLinkList.as_view(),
        name='activity-document_links'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/document_links/(?P<id>[^@$&+,/:;=?]+)$',  # NOQA: E501
        api.activity.views.ActivityDocumentLinkDetail.as_view(),
        name='activity-document_links'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<activity_id>[^@$&+,/:;=?]+)/document_links/(?P<document_link_id>[^@$&+,/:;=?]+)/categories/$',  # NOQA: E501
        api.activity.views.ActivityDocumentLinkCategoryList.as_view(),
        name='activity-document_link_category-list'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<activity_id>[^@$&+,/:;=?]+)/document_links/(?P<document_link_id>[^@$&+,/:;=?]+)/categories/(?P<category_id>[^@$&+,/:;=?]+)$',  # NOQA: E501
        api.activity.views.ActivityDocumentLinkCategoryDetail.as_view(),
        name='activity-document_link_category-detail'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<activity_id>[^@$&+,/:;=?]+)/document_links/(?P<document_link_id>[^@$&+,/:;=?]+)/languages/$',  # NOQA: E501
        api.activity.views.ActivityDocumentLinkLanguageList.as_view(),
        name='activity-document_link_language-list'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<activity_id>[^@$&+,/:;=?]+)/document_links/(?P<document_link_id>[^@$&+,/:;=?]+)/languages/(?P<language_id>[^@$&+,/:;=?]+)$',  # NOQA: E501
        api.activity.views.ActivityDocumentLinkLanguageDetail.as_view(),
        name='activity-document_link_language-detail'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/related_activities/$',  # NOQA: E501
        api.activity.views.ActivityRelatedActivityList.as_view(),
        name='activity-related_activities'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/related_activities/(?P<id>[^@$&+,/:;=?]+)',  # NOQA: E501
        api.activity.views.ActivityRelatedActivityDetail.as_view(),
        name='activity-related_activities'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/legacy_data/$',  # NOQA: E501
        api.activity.views.ActivityLegacyDataList.as_view(),
        name='activity-legacy_data-list'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/legacy_data/(?P<id>[^@$&+,/:;=?]+)$',  # NOQA: E501
        api.activity.views.ActivityLegacyDataDetail.as_view(),
        name='activity-legacy_data-detail'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/results/$',  # NOQA: E501
        api.activity.views.ActivityResultList.as_view(),
        name='activity-result-list'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/results/(?P<id>[^@$&+,/:;=?]+)$',  # NOQA: E501
        api.activity.views.ActivityResultDetail.as_view(),
        name='activity-result-detail'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<activity_id>[^@$&+,/:;=?]+)/results/(?P<result_id>[^@$&+,/:;=?]+)/indicators/$',  # NOQA: E501
        api.activity.views.ResultIndicatorList.as_view(),
        name='activity-result_indicator-list'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<activity_id>[^@$&+,/:;=?]+)/results/(?P<result_id>[^@$&+,/:;=?]+)/indicators/(?P<resultindicator_id>[^@$&+,/:;=?]+)$',  # NOQA: E501
        api.activity.views.ResultIndicatorDetail.as_view(),
        name='activity-result_indicator-detail'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<activity_id>[^@$&+,/:;=?]+)/results/(?P<result_id>[^@$&+,/:;=?]+)/indicators/(?P<resultindicator_id>[^@$&+,/:;=?]+)/references/$',  # NOQA: E501
        api.activity.views.ResultIndicatorReferenceList.as_view(),
        name='activity-result_indicator_reference-list'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<activity_id>[^@$&+,/:;=?]+)/results/(?P<result_id>[^@$&+,/:;=?]+)/indicators/(?P<resultindicator_id>[^@$&+,/:;=?]+)/references/(?P<reference_id>[^@$&+,/:;=?]+)$',  # NOQA: E501
        api.activity.views.ResultIndicatorReferenceDetail.as_view(),
        name='activity-result_indicator_reference-detail'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<activity_id>[^@$&+,/:;=?]+)/results/(?P<result_id>[^@$&+,/:;=?]+)/indicators/(?P<resultindicator_id>[^@$&+,/:;=?]+)/periods/$',  # NOQA: E501
        api.activity.views.ResultIndicatorPeriodList.as_view(),
        name='activity-result_indicator_period-list'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<activity_id>[^@$&+,/:;=?]+)/results/(?P<result_id>[^@$&+,/:;=?]+)/indicators/(?P<resultindicator_id>[^@$&+,/:;=?]+)/periods/(?P<period_id>[^@$&+,/:;=?]+)$',  # NOQA: E501
        api.activity.views.ResultIndicatorPeriodDetail.as_view(),
        name='activity-result_indicator_period-detail'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<activity_id>[^@$&+,/:;=?]+)/results/(?P<result_id>[^@$&+,/:;=?]+)/indicators/(?P<resultindicator_id>[^@$&+,/:;=?]+)/periods/(?P<period_id>[^@$&+,/:;=?]+)/actual/location/$',  # NOQA: E501
        api.activity.views.ResultIndicatorPeriodActualLocationList.as_view(),
        name='activity-result_indicator_period_actual_location-list'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<activity_id>[^@$&+,/:;=?]+)/results/(?P<result_id>[^@$&+,/:;=?]+)/indicators/(?P<resultindicator_id>[^@$&+,/:;=?]+)/periods/(?P<period_id>[^@$&+,/:;=?]+)/actual/location/(?P<actual_location_id>[^@$&+,/:;=?]+)$',  # NOQA: E501
        api.activity.views.ResultIndicatorPeriodActualLocationDetail.as_view(),
        name='activity-result_indicator_period_actual_location-detail'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<activity_id>[^@$&+,/:;=?]+)/results/(?P<result_id>[^@$&+,/:;=?]+)/indicators/(?P<resultindicator_id>[^@$&+,/:;=?]+)/periods/(?P<period_id>[^@$&+,/:;=?]+)/target/location/$',  # NOQA: E501
        api.activity.views.ResultIndicatorPeriodTargetLocationList.as_view(),
        name='activity-result_indicator_period_target_location-list'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<activity_id>[^@$&+,/:;=?]+)/results/(?P<result_id>[^@$&+,/:;=?]+)/indicators/(?P<resultindicator_id>[^@$&+,/:;=?]+)/periods/(?P<period_id>[^@$&+,/:;=?]+)/target/location/(?P<target_location_id>[^@$&+,/:;=?]+)$',  # NOQA: E501
        api.activity.views.ResultIndicatorPeriodTargetLocationDetail.as_view(),
        name='activity-result_indicator_period_target_location-detail'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<activity_id>[^@$&+,/:;=?]+)/results/(?P<result_id>[^@$&+,/:;=?]+)/indicators/(?P<resultindicator_id>[^@$&+,/:;=?]+)/periods/(?P<period_id>[^@$&+,/:;=?]+)/actual/dimension/$',  # NOQA: E501
        api.activity.views.ResultIndicatorPeriodActualDimensionList.as_view(),
        name='activity-result_indicator_period_actual_dimension-list'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<activity_id>[^@$&+,/:;=?]+)/results/(?P<result_id>[^@$&+,/:;=?]+)/indicators/(?P<resultindicator_id>[^@$&+,/:;=?]+)/periods/(?P<period_id>[^@$&+,/:;=?]+)/actual/dimension/(?P<actual_dimension_id>[^@$&+,/:;=?]+)$',  # NOQA: E501
        api.activity.views.ResultIndicatorPeriodActualDimensionDetail\
            .as_view(),
        name='activity-result_indicator_period_actual_dimension-detail'),


    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<activity_id>[^@$&+,/:;=?]+)/results/(?P<result_id>[^@$&+,/:;=?]+)/indicators/(?P<resultindicator_id>[^@$&+,/:;=?]+)/periods/(?P<period_id>[^@$&+,/:;=?]+)/target/dimension/$',  # NOQA: E501
        api.activity.views.ResultIndicatorPeriodTargetDimensionList.as_view(),
        name='activity-result_indicator_period_target_dimension-list'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<activity_id>[^@$&+,/:;=?]+)/results/(?P<result_id>[^@$&+,/:;=?]+)/indicators/(?P<resultindicator_id>[^@$&+,/:;=?]+)/periods/(?P<period_id>[^@$&+,/:;=?]+)/target/dimension/(?P<target_dimension_id>[^@$&+,/:;=?]+)$',  # NOQA: E501
        api.activity.views.ResultIndicatorPeriodTargetDimensionDetail\
            .as_view(),
        name='activity-result_indicator_period_target_dimension-detail'),


    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/crs_add/$',  # NOQA: E501
        api.activity.views.ActivityCrsAddList.as_view(),
        name='activity-crs_add-list'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/crs_add/(?P<id>[^@$&+,/:;=?]+)$',  # NOQA: E501
        api.activity.views.ActivityCrsAddDetail.as_view(),
        name='activity-crs_add-detail'),


    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/crs_add/(?P<id>[^@$&+,/:;=?]+)/other_flags/$',  # NOQA: E501
        api.activity.views.ActivityCrsAddOtherFlagsList.as_view(),
        name='activity-other_flags-list'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/crs_add/(?P<id>[^@$&+,/:;=?]+)/other_flags/(?P<other_flags_id>[^@$&+,/:;=?]+)$',  # NOQA: E501
        api.activity.views.ActivityCrsAddOtherFlagsDetail.as_view(),
        name='activity-other_flags-detail'),


    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/fss/$',  # NOQA: E501
        api.activity.views.ActivityFssList.as_view(),
        name='activity-fss-list'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/fss/(?P<id>[^@$&+,/:;=?]+)$',  # NOQA: E501
        api.activity.views.ActivityFssDetail.as_view(),
        name='activity-fss-detail'),


    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/fss/(?P<id>[^@$&+,/:;=?]+)/forecast/$',  # NOQA: E501
        api.activity.views.ActivityFssForecastList.as_view(),
        name='activity-fss-list'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/fss/(?P<id>[^@$&+,/:;=?]+)/forecast/(?P<forecast_id>[^@$&+,/:;=?]+)$',  # NOQA: E501
        api.activity.views.ActivityFssForecastDetail.as_view(),
        name='activity-fss-detail'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/conditions/$',  # NOQA: E501
        api.activity.views.ActivityConditionsDetail.as_view(),
        name='activity-conditions'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/conditions/condition/$',  # NOQA: E501
        api.activity.views.ActivityConditionList.as_view(),
        name='activity-conditions-list'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/activities/(?P<pk>[^@$&+,/:;=?]+)/conditions/condition/(?P<condition_id>[^@$&+,/:;=?]+)',  # NOQA: E501
        api.activity.views.ActivityConditionDetail.as_view(),
        name='activity-conditions-detail'),

    #
    # Organisation CRUD
    #

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/organisations/$',
        api.organisation.views.OrganisationListCRUD.as_view(),
        name='organisation-list'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/organisations/(?P<pk>[^@$&+,/:;=?]+)/$',  # NOQA: E501
        api.organisation.views.OrganisationDetailCRUD.as_view(),
        name='organisation-detail'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/organisations/(?P<pk>[^@$&+,/:;=?]+)/total_budgets/$',  # NOQA: E501
        api.organisation.views.OrganisationTotalBudgetListCRUD.as_view(),
        name='organisation-total_budget-list'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/organisations/(?P<pk>[^@$&+,/:;=?]+)/total_budgets/(?P<id>[^@$&+,/:;=?]+)$',  # NOQA: E501
        api.organisation.views.OrganisationTotalBudgetDetailCRUD.as_view(),
        name='organisation-total_budget-detail'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/organisations/(?P<pk>[^@$&+,/:;=?]+)/total_budgets/(?P<total_budget_id>[^@$&+,/:;=?]+)/budget_lines/$',  # NOQA: E501
        api.organisation.views.OrganisationTotalBudgetBudgetLineListCRUD\
            .as_view(),
        name='organisation-total_budget-list'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/organisations/(?P<pk>[^@$&+,/:;=?]+)/total_budgets/(?P<total_budget_id>[^@$&+,/:;=?]+)/budget_lines/(?P<id>[^@$&+,/:;=?]+)$',  # NOQA: E501
        api.organisation.views.OrganisationTotalBudgetBudgetLineDetailCRUD\
            .as_view(),
        name='organisation-total_budget-detail'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/organisations/(?P<pk>[^@$&+,/:;=?]+)/recipient_org_budgets/$',  # NOQA: E501
        api.organisation.views.OrganisationRecipientOrgBudgetListCRUD\
            .as_view(),
        name='organisation-recipient_org_budget-list'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/organisations/(?P<pk>[^@$&+,/:;=?]+)/recipient_org_budgets/(?P<id>[^@$&+,/:;=?]+)$',  # NOQA: E501
        api.organisation.views.OrganisationRecipientOrgBudgetDetailCRUD\
            .as_view(),
        name='organisation-recipient_org_budget-detail'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/organisations/(?P<pk>[^@$&+,/:;=?]+)/recipient_org_budgets/(?P<recipient_org_budget_id>[^@$&+,/:;=?]+)/budget_lines/$',  # NOQA: E501
        api.organisation\
            .views.OrganisationRecipientOrgBudgetBudgetLineListCRUD.as_view(),
        name='organisation-recipient_org_budget-list'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/organisations/(?P<pk>[^@$&+,/:;=?]+)/recipient_org_budgets/(?P<recipient_org_budget_id>[^@$&+,/:;=?]+)/budget_lines/(?P<id>[^@$&+,/:;=?]+)$',  # NOQA: E501
        api.organisation.views\
            .OrganisationRecipientOrgBudgetBudgetLineDetailCRUD.as_view(),
        name='organisation-recipient_org_budget-detail'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/organisations/(?P<pk>[^@$&+,/:;=?]+)/recipient_country_budgets/$',  # NOQA: E501
        api.organisation.views.OrganisationRecipientCountryBudgetListCRUD\
            .as_view(),
        name='organisation-recipient_country_budget-list'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/organisations/(?P<pk>[^@$&+,/:;=?]+)/recipient_country_budgets/(?P<id>[^@$&+,/:;=?]+)$',  # NOQA: E501
        api.organisation.views.OrganisationRecipientCountryBudgetDetailCRUD\
            .as_view(),
        name='organisation-recipient_country_budget-detail'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/organisations/(?P<pk>[^@$&+,/:;=?]+)/recipient_region_budgets/$',  # NOQA: E501
        api.organisation.views.OrganisationRecipientRegionBudgetListCRUD\
            .as_view(),
        name='organisation-recipient_region_budget-list'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/organisations/(?P<pk>[^@$&+,/:;=?]+)/recipient_region_budgets/(?P<id>[^@$&+,/:;=?]+)$',  # NOQA: E501
        api.organisation.views\
            .OrganisationRecipientRegionBudgetDetailCRUD.as_view(),
        name='organisation-recipient_region_budget-detail'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/organisations/(?P<pk>[^@$&+,/:;=?]+)/recipient_region_budgets/(?P<recipient_region_budget_id>[^@$&+,/:;=?]+)/budget_lines/$',  # NOQA: E501
        api.organisation.views\
            .OrganisationRecipientRegionBudgetBudgetLineListCRUD.as_view(),
        name='organisation-recipient_region_budget-list'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/organisations/(?P<pk>[^@$&+,/:;=?]+)/recipient_region_budgets/(?P<recipient_region_budget_id>[^@$&+,/:;=?]+)/budget_lines/(?P<id>[^@$&+,/:;=?]+)$',  # NOQA: E501
        api.organisation.views\
            .OrganisationRecipientRegionBudgetBudgetLineDetailCRUD.as_view(),
        name='organisation-recipient_region_budget-detail'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/organisations/(?P<pk>[^@$&+,/:;=?]+)/total_expenditures/$',  # NOQA: E501
        api.organisation.views.OrganisationTotalExpenditureListCRUD.as_view(),
        name='organisation-total_expenditure-list'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/organisations/(?P<pk>[^@$&+,/:;=?]+)/total_expenditures/(?P<id>[^@$&+,/:;=?]+)$',  # NOQA: E501
        api.organisation.views\
            .OrganisationTotalExpenditureDetailCRUD.as_view(),
        name='organisation-total_expenditure-detail'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/organisations/(?P<pk>[^@$&+,/:;=?]+)/total_expenditures/(?P<total_expenditure_id>[^@$&+,/:;=?]+)/expense_lines/$',  # NOQA: E501
        api.organisation.views\
            .OrganisationTotalExpenditureExpenseLineListCRUD.as_view(),
        name='organisation-total_expenditure-list'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/organisations/(?P<pk>[^@$&+,/:;=?]+)/total_expenditures/(?P<total_expenditure_id>[^@$&+,/:;=?]+)/expense_lines/(?P<id>[^@$&+,/:;=?]+)$',  # NOQA: E501
        api.organisation.views\
            .OrganisationTotalExpenditureExpenseLineDetailCRUD.as_view(),
        name='organisation-total_expenditure-detail'),


    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/organisations/(?P<pk>[^@$&+,/:;=?]+)/document_links/$',  # NOQA: E501
        api.organisation.views.OrganisationDocumentLinkList.as_view(),
        name='organisation-document_links'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/organisations/(?P<pk>[^@$&+,/:;=?]+)/document_links/(?P<id>[^@$&+,/:;=?]+)$',  # NOQA: E501
        api.organisation.views.OrganisationDocumentLinkDetail.as_view(),
        name='organisation-document_links'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/organisations/(?P<organisation_id>[^@$&+,/:;=?]+)/document_links/(?P<document_link_id>[^@$&+,/:;=?]+)/categories/$',  # NOQA: E501
        api.organisation.views.OrganisationDocumentLinkCategoryList.as_view(),
        name='organisation-document_link_category-list'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/organisations/(?P<organisation_id>[^@$&+,/:;=?]+)/document_links/(?P<document_link_id>[^@$&+,/:;=?]+)/categories/(?P<category_id>[^@$&+,/:;=?]+)$',  # NOQA: E501
        api.organisation.views.OrganisationDocumentLinkCategoryDetail\
            .as_view(),
        name='organisation-document_link_category-detail'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/organisations/(?P<organisation_id>[^@$&+,/:;=?]+)/document_links/(?P<document_link_id>[^@$&+,/:;=?]+)/languages/$',  # NOQA: E501
        api.organisation.views.OrganisationDocumentLinkLanguageList.as_view(),
        name='organisation-document_link_language-list'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/organisations/(?P<organisation_id>[^@$&+,/:;=?]+)/document_links/(?P<document_link_id>[^@$&+,/:;=?]+)/languages/(?P<language_id>[^@$&+,/:;=?]+)$',  # NOQA: E501
        api.organisation.views.OrganisationDocumentLinkLanguageDetail\
            .as_view(),
        name='organisation-document_link_language-detail'),

    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/organisations/(?P<organisation_id>[^@$&+,/:;=?]+)/document_links/(?P<document_link_id>[^@$&+,/:;=?]+)/recipient_countries/$',  # NOQA: E501
        api.organisation.views.OrganisationDocumentLinkRecipientCountryList\
            .as_view(),
        name='organisation-document_link_recipient_country-list'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/organisations/(?P<organisation_id>[^@$&+,/:;=?]+)/document_links/(?P<document_link_id>[^@$&+,/:;=?]+)/recipient_countries/(?P<recipient_country_id>[^@$&+,/:;=?]+)$',  # NOQA: E501
        api.organisation.views.OrganisationDocumentLinkRecipientCountryDetail\
            .as_view(),
        name='organisation-document_link_recipient_country-detail'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/organisations/(?P<pk>[^@$&+,/:;=?]+)/recipient_country_budgets/(?P<recipient_country_budget_id>[^@$&+,/:;=?]+)/budget_lines/$',  # NOQA: E501
        api.organisation.views\
            .OrganisationRecipientCountryBudgetBudgetLineListCRUD.as_view(),
        name='organisation-recipient_country_budget-list'),
    url(r'^(?P<publisher_id>[^@$+,/:;=?]+)/organisations/(?P<pk>[^@$&+,/:;=?]+)/recipient_country_budgets/(?P<recipient_country_budget_id>[^@$&+,/:;=?]+)/budget_lines/(?P<id>[^@$&+,/:;=?]+)$',  # NOQA: E501
        api.organisation.views\
            .OrganisationRecipientCountryBudgetBudgetLineDetailCRUD.as_view(),
        name='organisation-recipient_country_budget-detail'),
]
