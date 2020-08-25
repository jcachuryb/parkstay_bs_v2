from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
import threading

#from mooring.models import RegisteredVessels
from parkstay import models
from datetime import datetime
import json
import time
from datetime import timedelta
globalcount = 0
class Command(BaseCommand):
    help = 'Rebuild mooring booking property cache.'

    def handle(self, *args, **options):
        print ("current version: " + settings.BOOKING_PROPERTY_CACHE_VERSION)
        try:
           bookings = models.Booking.objects.all().order_by('-id')
           print (bookings)
           globalcount = 0
           for b in bookings:
               t = None
               try:
               
                   b.property_cache['cache_version']
                   print (b.property_cache['cache_version'])
                   if b.property_cache['cache_version'] != settings.BOOKING_PROPERTY_CACHE_VERSION:
                       print ("Rebuilding :"+str(b.id))
                       t = threading.Thread(target=update_cache,args=[b.id,],daemon=False)
                       globalcount = globalcount + 1
               except:
                    #b.update_property_cache()
                    t = threading.Thread(target=update_cache,args=[b.id,],daemon=False)
                    globalcount = globalcount + 1
               #if b.property_cache['cache_version'] != settings.BOOKING_PROPERTY_CACHE_VERSION:
               #     print ("Rebuilding :"+str(b.id))
               #     t = threading.Thread(target=update_cache,args=[b.id,],daemon=True)
               #print ('thread')
               #print (t)
               if t is not None:
                    if globalcount > 9:
                         print ("Sleeping")      
                         time.sleep(10)
                         globalcount = 0
                    t.start()

                    #b.update_property_cache()

        except Exception as e:
            print (e)
            #Send fail email
            content = "Error message: {}".format(e)

def update_cache(booking_id):
     print ('New Rebuild for: '+str(booking_id))
     b= models.Booking.objects.get(id=int(booking_id))
     b.update_property_cache(False)
     print ('Finished :'+str(booking_id))


