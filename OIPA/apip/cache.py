# Tastypie specific
from tastypie.cache import SimpleCache


class NoTransformCache(SimpleCache):
    def cache_control(self):
        control = super(NoTransformCache, self).cache_control()
        control.update({"no_transform": True})
        return control