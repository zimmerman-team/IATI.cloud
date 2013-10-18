
from django.contrib.gis.db import models
from django.contrib.gis import geos

class region(models.Model):
    code = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=80)
    source = models.CharField(max_length=80)
    parental_region = models.ForeignKey('self', null=True, blank=True)

    def __unicode__(self):
        return self.name

class country(models.Model):
    code = models.CharField(primary_key=True, max_length=2)
    numerical_code_un = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=100, db_index=True)
    language = models.CharField(max_length=2, null=True)
    capital_city = models.ForeignKey("city", related_name='capital_city', null=True, blank=True)
    region = models.ForeignKey(region, null=True, blank=True)
    un_region = models.ForeignKey('region', null=True, blank=True, related_name='un_region')
    dac_country_code = models.IntegerField(null=True, blank=True)
    iso3 = models.CharField(max_length=3, null=True, blank=True)
    alpha3 = models.CharField(max_length=3, null=True, blank=True)
    fips10 = models.CharField(max_length=2, null=True, blank=True)
    center_longlat = models.PointField(null=True, blank=True)
    polygon = models.TextField(null=True, blank=True)
    objects = models.GeoManager()

    class Meta:
        verbose_name_plural = "countries"

    def __unicode__(self):
        return self.name

    # def save(self, *args, **kwargs):
    #     # if polygon ends up as a Polygon, make it into a MultiPolygon
    #     if self.polygon and isinstance(self.polygon, geos.Polygon):
    #         self.polygon = geos.MultiPolygon(self.polygon)
    #     super(country, self).save(*args, **kwargs)

class city(models.Model):
    geoname_id = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=200)
    country = models.ForeignKey(country, null=True, blank=True)
    location = models.PointField(null=True, blank=True)
    ascii_name = models.CharField(max_length=200, null=True, blank=True)
    alt_name = models.CharField(max_length=200, null=True, blank=True)
    namepar = models.CharField(max_length=200, null=True, blank=True)
    objects = models.GeoManager()

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = "cities"


