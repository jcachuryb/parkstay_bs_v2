from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from django.utils import timezone
#from mooring.models import RegisteredVessels
from parkstay import models
from datetime import datetime
from django.conf import settings
from confy import env, database
import requests
import json

from datetime import timedelta

class Command(BaseCommand):
    help = 'Collect Park alerts from alerts.dbca.wa.gov.au .'

    def handle(self, *args, **options):

        try:
           alert_url = env("ALERT_URL","")
           alert_token = env("ALERT_TOKEN","")
           print (alert_url)
           print (alert_token)

           parks = models.Park.objects.filter(active=True)
           for p in parks:
               url = alert_url+'/api/AlertsApi/park/?token='+alert_token+'&count=true&id='+str(p.ratis_id)
               resp = requests.get(url, data = {}, cookies={})
               alert_resp = resp.json()
               p.alert_count = 0
               if 'status' in alert_resp:
                   if alert_resp['status'] == 'SUCCESS':
                        print (alert_resp['count'])
                        p.alert_count = int(alert_resp['count'])
               try:
                   print ("SAVING"+str(p.id))
                   print (p.name)
                   p.save()
               except Exception as e:
                   print (e)
                    
                    

               #print (p.ratis_id)


           #for p in places:
           #    try:
           #       mapbox_url='https://.dpaw.wa.gov.au/geocoding/v5/mapbox.places/'+p.name+'.json?country=au&proximity=115.659641265869,-33.3404350280762&bbox=112.920934,-35.191991,129.0019283,-11.9662455&types=place,region,postcode,locality,neighborhood,address'
           #       resp = requests.get(mapbox_url, data = {}, cookies={})
           #       print ("Building GPS for "+p.name)
           #       print (resp.json()['features'][0]['geometry']['coordinates'])
           #    
           #       p.wkb_geometry=Point(x=resp.json()['features'][0]['geometry']['coordinates'][0], y=resp.json()['features'][0]['geometry']['coordinates'][1], srid=4326)
           #       p.rebuild_gps=False
           #       p.save()
           #    except Exception as e:
           #       p.rebuild_gps=False
           #       p.save()
           #       print (e)

           #print ("Completed")
           #for b in places:
           #    print ("Rebuilding :"+str(b.id))

        except Exception as e:
            print (e)
            #Send fail email
            content = "Error message: {}".format(e)
