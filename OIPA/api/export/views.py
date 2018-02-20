from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from iati.models import Activity
from api.export import serializers as export_serializers
from api.activity import filters
from api.generics.filters import SearchFilter
from api.generics.utils import get_serializer_fields
from common.util import difference
from django_filters.rest_framework import DjangoFilterBackend
from api.renderers import XMLRenderer
from rest_framework.renderers import BrowsableAPIRenderer
from api.pagination import IatiXMLPagination, IatiXMLUnlimitedPagination
from django.db.models import Q

from rest_framework import authentication, permissions
from api.publisher.permissions import OrganisationAdminGroupPermissions, ActivityCreatePermissions, PublisherPermissions


class IATIActivityList(ListAPIView):

    """IATI representation for activities"""

    queryset = Activity.objects.all()
    filter_backends = (SearchFilter, DjangoFilterBackend, filters.RelatedOrderingFilter,)
    filter_class = filters.ActivityFilter
    serializer_class = export_serializers.ActivityXMLSerializer
    pagination_class = IatiXMLPagination

    renderer_classes = (BrowsableAPIRenderer, XMLRenderer)

    fields = difference(
        get_serializer_fields(serializer_class),
        ['url', 'activity_aggregation', 'child_aggregation', 'activity_plus_child_aggregation']
    )

    ordering = ('iati_identifier',)
    ordering_fields = (
        'title',
        'planned_start_date',
        'actual_start_date',
        'planned_end_date',
        'actual_end_date',
        'start_date',
        'end_date',
        'activity_budget_value',
        'activity_incoming_funds_value',
        'activity_disbursement_value',
        'activity_expenditure_value',
        'activity_plus_child_budget_value',
    )

    def get_queryset(self):
        return super(IATIActivityList, self).get_queryset().prefetch_all()


import django_rq
from task_queue.tasks import export_publisher_activities
from rest_framework.response import Response
from iati_synchroniser.models import Dataset

import uuid


class IATIActivityNextExportList(APIView):
    """IATI representation for activities"""

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def post(self, request, publisher_id):

        try:
            dataset, created = Dataset.objects.get_or_create(
                publisher_id=publisher_id,
                added_manually=True,
                filetype=1,
            )

        except Dataset.DoesNotExist:
            return Response({
                'status': 'failed',
                'message': 'Dataset does not exist'
            })

        if dataset.export_in_progress:
            return Response({
                'status': 'failed',
                'message': 'Export already in progress'
            })

        dataset.export_in_progress = True
        dataset.save()

        queue = django_rq.get_queue('export')
        job = queue.enqueue(export_publisher_activities, publisher_id)

        return Response({
            'status': 'processing',
            'job': job.key,
        })


class IATIActivityNextExportListResult(APIView):
    """IATI representation for activities"""

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get(self, request, publisher_id, job_id):
        job_id = job_id.split(':')[2]

        queue = django_rq.get_queue('export')
        job = queue.fetch_job(job_id)

        if job.is_finished:
            ret = {'status': 'completed', 'result': job.return_value}

            try:
                dataset = Dataset.objects.get(
                    publisher_id=publisher_id, filetype=1, added_manually=True)
            except Dataset.DoesNotExist:
                return Response({
                    'status': 'failed',
                    'message': 'Dataset does not exist'
                })

            dataset.export_in_progress = False
            dataset.save()

        elif job.is_queued:
            ret = {'status': 'in-queue'}
        elif job.is_started:
            ret = {'status': 'waiting'}
        elif job.is_failed:
            ret = {'status': 'failed', 'message': "job failed for unknown reasons"}
            print(job.to_dict())

        return Response(ret)
