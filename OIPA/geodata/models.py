from django.contrib.gis.db import models


class Region(models.Model):
    code = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=80)
    region_vocabulary = models.ForeignKey('iati.RegionVocabulary', default=1)
    parental_region = models.ForeignKey('self', null=True, blank=True)
    center_longlat = models.PointField(null=False, blank=True)
    objects = models.GeoManager()

    def __unicode__(self):
        return self.name

class Country(models.Model):
    code = models.CharField(primary_key=True, max_length=2)
    numerical_code_un = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=100, db_index=True)
    alt_name = models.CharField(max_length=100, null=True, blank=True)
    language = models.CharField(max_length=2, null=True)
    capital_city = models.ForeignKey("City", related_name='capital_city', null=True, blank=True)
    region = models.ForeignKey(Region, null=True, blank=True)
    un_region = models.ForeignKey('Region', null=True, blank=True, related_name='un_region')
    unesco_region = models.ForeignKey('Region', null=True, blank=True, related_name='unesco_region')
    dac_country_code = models.IntegerField(null=True, blank=True)
    iso3 = models.CharField(max_length=3, null=True, blank=True)
    alpha3 = models.CharField(max_length=3, null=True, blank=True)
    fips10 = models.CharField(max_length=2, null=True, blank=True)
    center_longlat = models.PointField(null=False, blank=True)
    polygon = models.TextField(null=True, blank=True)
    data_source = models.CharField(max_length=20, null=True, blank=True)
    geom = models.MultiPolygonField(srid=4326)
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

class City(models.Model):
    geoname_id = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=200)
    country = models.ForeignKey(Country, null=True, blank=True)
    location = models.PointField(null=False, blank=True)
    ascii_name = models.CharField(max_length=200, null=True, blank=True)
    alt_name = models.CharField(max_length=200, null=True, blank=True)
    namepar = models.CharField(max_length=200, null=True, blank=True)
    objects = models.GeoManager()

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = "cities"


class Adm1Region(models.Model):
    adm1_code = models.CharField(primary_key=True, max_length=10)
    OBJECTID_1 = models.IntegerField(null=True, blank=True)
    diss_me = models.IntegerField(null=True, blank=True)
    adm1_cod_1 = models.CharField(null=True, blank=True, max_length=20)
    iso_3166_2 = models.CharField(null=True, blank=True, max_length=2)
    wikipedia = models.CharField(null=True, blank=True, max_length=150)
    country = models.ForeignKey(Country, null=True, blank=True)
    adm0_sr = models.IntegerField(null=True, blank=True)
    name = models.CharField(null=True, blank=True, max_length=100)
    name_alt = models.CharField(null=True, blank=True, max_length=200)
    name_local = models.CharField(null=True, blank=True, max_length=100)
    type = models.CharField(null=True, blank=True, max_length=100)
    type_en = models.CharField(null=True, blank=True, max_length=100)
    code_local = models.CharField(null=True, blank=True, max_length=100)
    code_hasc = models.CharField(null=True, blank=True, max_length=100)
    note = models.TextField(null=True, blank=True)
    hasc_maybe = models.CharField(null=True, blank=True, max_length=100)
    region = models.CharField(null=True, blank=True, max_length=100)
    region_cod = models.CharField(null=True, blank=True, max_length=100)
    provnum_ne = models.IntegerField(null=True, blank=True)
    gadm_level = models.IntegerField(null=True, blank=True)
    check_me = models.IntegerField(null=True, blank=True)
    scalerank = models.IntegerField(null=True, blank=True)
    datarank = models.IntegerField(null=True, blank=True)
    abbrev = models.CharField(null=True, blank=True, max_length=100)
    postal = models.CharField(null=True, blank=True, max_length=100)
    area_sqkm = models.CharField(null=True, blank=True, max_length=100)
    sameascity = models.IntegerField(null=True, blank=True)
    labelrank = models.IntegerField(null=True, blank=True)
    featurecla = models.CharField(null=True, blank=True, max_length=100)
    name_len = models.IntegerField(null=True, blank=True)
    mapcolor9 = models.IntegerField(null=True, blank=True)
    mapcolor13 = models.IntegerField(null=True, blank=True)
    fips = models.CharField(null=True, blank=True, max_length=100)
    fips_alt = models.CharField(null=True, blank=True, max_length=100)
    woe_id = models.IntegerField(null=True, blank=True)
    woe_label = models.CharField(null=True, blank=True, max_length=100)
    woe_name = models.CharField(null=True, blank=True, max_length=100)
    center_location = models.PointField(null=False, blank=True)
    sov_a3 = models.CharField(null=True, blank=True, max_length=3)
    adm0_a3 = models.CharField(null=True, blank=True, max_length=3)
    adm0_label = models.IntegerField(null=True, blank=True)
    admin = models.CharField(null=True, blank=True, max_length=100)
    geonunit = models.CharField(null=True, blank=True, max_length=100)
    gu_a3 = models.CharField(null=True, blank=True, max_length=3)
    gn_id = models.IntegerField(null=True, blank=True)
    gn_name = models.CharField(null=True, blank=True, max_length=100)
    gns_id = models.IntegerField(null=True, blank=True)
    gns_name = models.CharField(null=True, blank=True, max_length=100)
    gn_level = models.IntegerField(null=True, blank=True)
    gn_region = models.CharField(null=True, blank=True, max_length=100)
    gn_a1_code = models.CharField(null=True, blank=True, max_length=100)
    region_sub = models.CharField(null=True, blank=True, max_length=100)
    sub_code = models.CharField(null=True, blank=True, max_length=100)
    gns_level = models.IntegerField(null=True, blank=True)
    gns_lang = models.CharField(null=True, blank=True, max_length=100)
    gns_adm1 = models.CharField(null=True, blank=True, max_length=100)
    gns_region = models.CharField(null=True, blank=True, max_length=100)
    polygon = models.TextField(null=True, blank=True)
    geometry_type = models.CharField(null=True, blank=True, max_length=50)
    geom = models.MultiPolygonField(srid=4326)
    objects = models.GeoManager()

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = "admin1 regions"


class Adm2Region(models.Model):

    code = models.CharField(primary_key=True, max_length=10)
    name = models.CharField(null=True, blank=True, max_length=100)
    region = models.ForeignKey(Adm1Region, null=False, blank=False)
    geom = models.MultiPolygonField(srid=4326)
    objects = models.GeoManager()

    def __unicode__(self):
        return "Adm2Region %s in %s" % (self.name, self.region.name)
