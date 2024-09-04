from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from django.utils import timezone
#from mooring.models import RegisteredVessels
from parkstay import models
from datetime import datetime
from django.conf import settings
import requests
from parkstay import api
import json

from datetime import timedelta

class Command(BaseCommand):
    help = 'Rebuild Map JSON Data'

    def handle(self, *args, **options):

        try:
            dump_data = api.campground_map_data()
            f = open(settings.DATA_STORE+"/campground_map.json", "w")
            f.write(dump_data)
            f.close()

            places_data = api.places_data()
            f = open(settings.DATA_STORE+"/places.json", "w")
            f.write(places_data)
            f.close()
          
            search_suggest_data = api.search_suggest_data()
            f = open(settings.DATA_STORE+"/search_suggest.json","w")
            f.write(search_suggest_data)
            f.close()


        except Exception as e:
            print (e)
            #Send fail email
            content = "Error message: {}".format(e)
