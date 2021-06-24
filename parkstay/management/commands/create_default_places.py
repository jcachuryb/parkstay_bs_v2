from django.core.management.base import BaseCommand
from django.utils import timezone
#from mooring.models import RegisteredVessels
from parkstay import models
from datetime import datetime
from django.conf import settings
import json

from datetime import timedelta

class Command(BaseCommand):
    help = 'Rebuild mooring booking property cache.'

    def handle(self, *args, **options):

        try:
#  url: 'https://mapbox.dpaw.wa.gov.au/geocoding/v5/mapbox.places/all.json?'+ $.param({
#                    country: 'au',
#                    proximity:'115.659641265869,-33.3404350280762',
#                    bbox: '112.920934,-35.191991,129.0019283,-11.9662455',
#                    types: 'place'
#                }),

           data = None
           with open(settings.BASE_DIR+'/parkstay/fixtures/default_towns.json') as f:
                   data = json.load(f)

           for town in data:
               place = models.Places.objects.filter(name=town['name'])
               if place.count() > 0:
                   # nothing to do
                   pass
               else:
                   print ("Creating"+str(town['name']))
                   models.Places.objects.create(name=town['name'])
           print ("Completed")
           #for b in places:
           #    print ("Rebuilding :"+str(b.id))

        except Exception as e:
            print (e)
            #Send fail email
            content = "Error message: {}".format(e)
