from django.core.cache import cache
from parkstay import models as parkstay_models
import json

def all_campgrounds():
    cg_array = []

    dumped_data = cache.get('utils_cache.all_campgrounds')
    #dumped_data = None
    if dumped_data is None:
        grounds = parkstay_models.Campground.objects.all()
        for cg in grounds:
            cg_array.append({'id': cg.id, 'campground_name': cg.name,'campground_type': cg.campground_type})
        cache.set('utils_cache.all_campgrounds', json.dumps(cg_array),  86400)
    else:
        cg_array = json.loads(dumped_data)

    return cg_array


def all_campground_campsites(cg_id):
    cs_array = []
    dumped_data = cache.get('utils_cache.all_campground_campsites('+str(cg_id)+')')
    if dumped_data is None:
        campsites = parkstay_models.Campsite.objects.filter(campground_id=cg_id)
        for cs in campsites:
              cs_array.append({'id': cs.id, 'campground_name': cs.name})
        cache.set('utils_cache.all_campground_campsites('+str(cg_id)+')', json.dumps(cs_array),  86400)
    else:
        cs_array = json.loads(dumped_data)
    return cs_array


