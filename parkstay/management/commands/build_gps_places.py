from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from django.utils import timezone
#from mooring.models import RegisteredVessels
from parkstay import models
from datetime import datetime
from django.conf import settings
import requests
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
           #wkb_geometry
           places = models.Places.objects.filter(rebuild_gps=True)
           for p in places:
               try:
                  mapbox_url='https://mapbox.dpaw.wa.gov.au/geocoding/v5/mapbox.places/'+p.name+'.json?country=au&proximity=115.659641265869,-33.3404350280762&bbox=112.920934,-35.191991,129.0019283,-11.9662455&types=place,region,postcode,locality,neighborhood,address'
                  resp = requests.get(mapbox_url, data = {}, cookies={})
                  print ("Building GPS for "+p.name)
                  print (resp.json()['features'][0]['geometry']['coordinates'])
               
                  p.wkb_geometry=Point(x=resp.json()['features'][0]['geometry']['coordinates'][0], y=resp.json()['features'][0]['geometry']['coordinates'][1], srid=4326)
                  p.rebuild_gps=False
                  p.save()
               except Exception as e:
                  p.rebuild_gps=False
                  p.save()
                  print (e)

           print ("Completed")
           #for b in places:
           #    print ("Rebuilding :"+str(b.id))

        except Exception as e:
            print (e)
            #Send fail email
            content = "Error message: {}".format(e)
