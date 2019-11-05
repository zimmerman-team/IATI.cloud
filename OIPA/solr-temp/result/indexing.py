from rest_framework.renderers import JSONRenderer

from api.activity.serializers import (
    DocumentLinkSerializer, ResultIndicatorReferenceSerializer,
    ResultIndicatorSerializer
)
from iati.models import ResultIndicatorPeriodTarget
from solr.indexing import BaseIndexing
from solr.utils import (
    add_reporting_org, bool_string, get_child_attr, value_string
)


class ResultIndexing(BaseIndexing):

    def field_narrative(self, field, key):
        if field:
            for narrative in field.narratives.all():
                self.add_value_list(key, narrative.content)

    def title(self):
        title = get_child_attr(self.record, 'resulttitle')
        if title:
            self.narrative(title, 'result_title', True)

            self.add_field('result_title_narrative', [])
            for narrative in title.narratives.all():
                self.add_value_list(
                    'result_title_narrative', 
                    narrative.content
                )

    def description(self):
        description = get_child_attr(self.record, 'resultdescription')
        if description:
            self.narrative(description, 'result_description', True)

            self.add_field('result_description_narrative', [])
            for narrative in description.narratives.all():
                self.add_value_list(
                    'result_description_narrative', 
                    narrative.content
                )

    def document_link(self, document_link_all, prefix='result_document_link'):
        if document_link_all:
            if prefix not in self.indexing:
                self.add_field(prefix, [])
                self.add_field(prefix + '_url', [])
                self.add_field(prefix + '_format', [])
                self.add_field(prefix + '_document_date_iso_date', [])
                self.add_field(prefix + '_description_narrative', [])
                self.add_field(prefix + '_category_code', [])
                self.add_field(prefix + '_language_code', [])

            for document_link in document_link_all:
                self.add_value_list(
                    prefix, JSONRenderer().render(
                        DocumentLinkSerializer(document_link).data
                    ).decode()
                )

                self.add_value_list(prefix + '_url', document_link.url)
                self.add_value_list(
                    prefix + '_format', document_link.file_format_id
                )
                self.add_value_list(
                    prefix + '_document_date_iso_date', value_string(
                        document_link.iso_date
                    )
                )

                category_all = document_link.documentlinkcategory_set.all()
                if category_all:
                    for category in category_all:
                        self.add_value_list(
                            prefix + '_category_code', category.category_id
                        )

                language_all = document_link.documentlinklanguage_set.all()
                if language_all:
                    for language in language_all:
                        self.add_value_list(
                            prefix + '_language_code', language.language_id
                        )

    def reference(
        self, reference_all, prefix='result_reference', is_indicator=False):
        if reference_all:
            if prefix not in self.indexing:
                self.add_field(prefix, [])
                self.add_field(prefix + '_code', [])
                self.add_field(prefix + '_vocabulary', [])
                if not is_indicator:
                    self.add_field(prefix + '_vocabulary_uri', [])
                else:
                    self.add_field(prefix + '_indicator_uri', [])

            for reference in reference_all:
                self.add_value_list(
                    prefix,
                    JSONRenderer().render(
                        ResultIndicatorReferenceSerializer(reference).data
                    ).decode()
                )

                self.add_value_list(prefix + '_code', reference.code)
                self.add_value_list(
                    prefix + '_vocabulary', reference.vocabulary_id
                )
                if not is_indicator:
                    self.add_value_list(
                        prefix + '_vocabulary_uri', reference.vocabulary_uri
                    )
                else:
                    self.add_value_list(
                        prefix + '_indicator_uri', reference.indicator_uri
                    )

    def indicator_baseline(self, indicator):
        baseline_all = indicator.resultindicatorbaseline_set.all()
        if baseline_all:
            if 'result_indicator_baseline_year' not in self.indexing:
                self.add_field('result_indicator_baseline_year', [])
                self.add_field('result_indicator_baseline_iso_date', [])
                self.add_field('result_indicator_baseline_value', [])
                self.add_field('result_indicator_baseline_location_ref', [])
                self.add_field('result_indicator_baseline_dimension_name', [])
                self.add_field('result_indicator_baseline_dimension_value', [])
                self.add_field(
                    'result_indicator_baseline_comment_narrative', 
                    []
                )

            for baseline in baseline_all:
                self.add_value_list(
                    'result_indicator_baseline_year', baseline.year
                )
                self.add_value_list(
                    'result_indicator_baseline_iso_date', 
                    value_string(baseline.iso_date)
                )
                self.add_value_list(
                    'result_indicator_baseline_value', baseline.value
                )

                for location in baseline.location_set.all():
                    self.add_value_list(
                        'result_indicator_baseline_location_ref', location.ref
                    )

                for dimension in baseline.resultindicatorbaselinedimension_set.all():
                    self.add_value_list(
                        'result_indicator_baseline_dimension_name', 
                        dimension.name
                    )
                    self.add_value_list(
                        'result_indicator_baseline_dimension_value', 
                        dimension.value
                    )

                comment = get_child_attr(
                    baseline, 'resultindicatorbaselinecomment'
                )
                if comment:
                    for narrative in comment.narratives.all():
                        self.add_value_list(
                            'result_indicator_baseline_comment_narrative', 
                            narrative.content
                        )

                self.document_link(
                    baseline.baseline_document_links.all(),
                    prefix='result_indicator_baseline_document_link'
                )

    def indicator_period_related(self, related_all):
        if related_all:
            is_target = True if isinstance(
                related_all.first(), ResultIndicatorPeriodTarget 
            ) else False
            prefix = 'result_indicator_period_target' \
                if isinstance(related_all.first(), 
                ResultIndicatorPeriodTarget) else 
                'result_indicator_period_actual'

            if prefix not in self.indexing:
                self.add_field(prefix + '_value', [])
                self.add_field(prefix + '_location_ref', [])

                self.add_field(prefix + '_dimmension_name', [])
                self.add_field(prefix + '_dimmension_value', [])
                self.add_field(prefix + '_comment_narrative', [])

            for related in related_all:
                self.add_value_list(prefix + '_value', related.value)

                location_all = 
                related.resultindicatorperiodtargetlocation_set.all() if 
                is_target
                    else related.resultindicatorperiodactuallocation_set.all()
                for location in location_all:
                    self.add_value_list(prefix + '_location_ref', location.ref)

                dimension_all = 
                related.resultindicatorperiodtargetdimension_set.all() if 
                is_target
                    else related.resultindicatorperiodactualdimension_set.all()
                for dimension in dimension_all:
                    self.add_value_list(
                        prefix + '_dimmension_name', dimension.name
                    )
                    self.add_value_list(
                        prefix + '_dimmension_value', dimension.value
                    )

                comment_all = 
                related.resultindicatorperiodtargetcomment_set.all() if 
                is_target
                    else related.resultindicatorperiodactualcomment_set.all()
                for comment in comment_all:
                    for narrative in comment.narratives.all():
                        self.add_value_list(
                            prefix + '_comment_narrative', narrative.content
                        )

                document_link_all = related.period_target_document_links.all() 
                if is_target else related.period_actual_document_links.all()
                self.document_link(
                    document_link_all, prefix=prefix + '_document_link'
                )

    def indicator_period(self, indicator):
        period_all = indicator.resultindicatorperiod_set.all()
        if period_all:
            if 'result_indicator_period_period_start_iso_date' not in self.indexing:  # NOQA: E501
                self.add_field(
                    'result_indicator_period_period_start_iso_date', 
                    []
                )
                self.add_field(
                    'result_indicator_period_period_end_iso_date', 
                    []
                )

            for period in period_all:
                self.add_value_list(
                    'result_indicator_period_period_start_iso_date', 
                    value_string(
                        period.period_start
                    )
                )
                self.add_value_list(
                    'result_indicator_period_period_end_iso_date', 
                    value_string(
                        period.period_end
                    )
                )

                self.indicator_period_related(
                    period.targets.all()
                )
                self.indicator_period_related(
                    period.actuals.all()
                )

    def indicator(self):
        indicator_all = self.record.resultindicator_set.all()
        if indicator_all:
            self.add_field('result_indicator', [])
            self.add_field('result_indicator_measure', [])
            self.add_field('result_indicator_ascending', [])
            self.add_field('result_indicator_aggregation_status', [])
            self.add_field('result_indicator_title_narrative', [])
            self.add_field('result_indicator_description_narrative', [])

            for indicator in indicator_all:
                self.add_value_list(
                    'result_indicator',
                    JSONRenderer().render(
                        ResultIndicatorSerializer(indicator).data
                    ).decode()
                )

                self.add_value_list(
                    'result_indicator_measure', indicator.measure_id
                )
                self.add_value_list(
                    'result_indicator_ascending', 
                    bool_string(
                        indicator.ascending
                    )
                )
                self.add_value_list(
                    'result_indicator_aggregation_status', 
                    bool_string(
                        indicator.aggregation_status
                    )
                )

                self.field_narrative(
                    get_child_attr(indicator, 'resultindicatortitle'),
                    'result_indicator_title_narrative'
                )
                self.field_narrative(
                    get_child_attr(indicator, 'resultindicatordescription'),
                    'result_indicator_description_narrative'
                )

                self.document_link(
                    indicator.result_indicator_document_links.all(),
                    prefix='result_indicator_document_link'
                )
                self.reference(
                    indicator.resultindicatorreference_set.all(),
                    prefix='result_indicator_reference',
                    is_indicator=True
                )

                self.indicator_baseline(indicator)
                self.indicator_period(indicator)

    def result(self):
        self.add_field('id', self.record.id)
        self.add_field('iati_identifier', self.record.activity.iati_identifier)
        self.add_field(
            'humanitarian', bool_string(
                get_child_attr(
                    self.record, 'activity.humanitarian'
                )
            )
        )

        add_reporting_org(self, self.record.activity)

        self.title()
        self.description()

        self.document_link(self.record.documentlink_set.all())
        self.reference(self.record.resultreference_set.all())

        self.indicator()

    def to_representation(self, result):
        self.record = result

        self.indexing = {}
        self.representation = {}

        self.result()
        self.build()

        return self.representation
