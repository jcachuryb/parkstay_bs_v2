from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from django.utils import timezone
#from mooring.models import RegisteredVessels
from parkstay import models
from parkstay import utils_cache
from datetime import datetime
from django.conf import settings
from django.db.models import Q
from datetime import datetime, timedelta, date, timezone as timezone_dt
import requests
import json
import os
from datetime import timedelta
from parkstay import datasets

class Command(BaseCommand):
    help = 'Rebuild Campsite Attributes'

    def handle(self, *args, **options):
        params = {}
        print ("Completed")
        object_hash  = {"campgrounds": {}}
        data_file = settings.BASE_DIR+"/datasets/campground-attributes.json"
        try:
             campsites = models.Campsite.objects.all()
             for cs in campsites:
                 if cs.campground.id not in object_hash['campgrounds']:
                       object_hash['campgrounds'][cs.campground.id] = {}

                 if 'campsites' not in object_hash['campgrounds'][cs.campground.id]:
                       object_hash['campgrounds'][cs.campground.id]['campsites'] = {}
                       
                 if cs.id not in object_hash['campgrounds'][cs.campground.id]['campsites']:
                       object_hash['campgrounds'][cs.campground.id]['campsites'][cs.id] = {}

                 if 'features' not in object_hash['campgrounds'][cs.campground.id]['campsites'][cs.id]:
                       object_hash['campgrounds'][cs.campground.id]['campsites'][cs.id]['features'] = []

                 if 'properties' not in object_hash['campgrounds'][cs.campground.id]['campsites'][cs.id]:
                       object_hash['campgrounds'][cs.campground.id]['campsites'][cs.id]['properties'] = {}

                 object_hash['campgrounds'][cs.campground.id]['campsites'][cs.id]['properties']['tent'] = cs.tent
                 object_hash['campgrounds'][cs.campground.id]['campsites'][cs.id]['properties']['vehicle'] = cs.vehicle
                 object_hash['campgrounds'][cs.campground.id]['campsites'][cs.id]['properties']['campervan'] = cs.campervan
                 object_hash['campgrounds'][cs.campground.id]['campsites'][cs.id]['properties']['caravan'] = cs.caravan
                 object_hash['campgrounds'][cs.campground.id]['campsites'][cs.id]['properties']['motorcycle'] = cs.motorcycle
                 object_hash['campgrounds'][cs.campground.id]['campsites'][cs.id]['properties']['trailer'] = cs.trailer
               
                 for f in cs.features.all():
                     object_hash['campgrounds'][cs.campground.id]['campsites'][cs.id]['features'].append(f.id)


             f = open(data_file, "w")
             f.write(json.dumps(object_hash, indent=4))
             f.close()


             print (object_hash)
        except Exception as e:
            print (e)
            #Send fail email
            content = "Error message: {}".format(e)
