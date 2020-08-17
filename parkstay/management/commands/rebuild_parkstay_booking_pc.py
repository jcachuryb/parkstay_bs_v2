from django.core.management.base import BaseCommand
from django.utils import timezone
#from mooring.models import RegisteredVessels
from parkstay import models
from datetime import datetime
import json

from datetime import timedelta

class Command(BaseCommand):
    help = 'Rebuild mooring booking property cache.'

    def handle(self, *args, **options):

        try:
           bookings = models.Booking.objects.all()
           for b in bookings:
               print ("Rebuilding :"+str(b.id))
               b.update_property_cache()

        except Exception as e:
            print (e)
            #Send fail email
            content = "Error message: {}".format(e)
