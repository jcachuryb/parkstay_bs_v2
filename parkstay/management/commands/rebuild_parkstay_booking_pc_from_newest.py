from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings

#from mooring.models import RegisteredVessels
from parkstay import models
from datetime import datetime
import json

from datetime import timedelta

class Command(BaseCommand):
    help = 'Rebuild mooring booking property cache.'

    def handle(self, *args, **options):

        try:
           bookings = models.Booking.objects.all().order_by('-id')
           for b in bookings:
               try: 
                   b.property_cache['cache_version'] 
               except:
                    b.update_property_cache()
               if b.property_cache['cache_version'] != settings.BOOKING_PROPERTY_CACHE_VERSION:
                    print ("Rebuilding :"+str(b.id))
                    b.update_property_cache()

        except Exception as e:
            print (e)
            #Send fail email
            content = "Error message: {}".format(e)
