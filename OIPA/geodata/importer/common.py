import os
import os.path

import ujson


def get_json_data(location_from_here):
    base = os.path.dirname(os.path.abspath(__file__))
    location = base + location_from_here
    json_data = open(location)
    data = ujson.load(json_data)
    json_data.close()
    return data
