from django.db.models import query


class OrganisationQuerySet(query.QuerySet):
    def reporting_organisations(self):
        return self.exclude(activity_reporting_organisation__exact=None)
