from django.core.management.base import BaseCommand
from django.utils import timezone
#from mooring.models import RegisteredVessels
from parkstay import models
from datetime import datetime
from django.conf import settings
import json
import requests

from datetime import timedelta, datetime

class Command(BaseCommand):
    help = 'Delete campsite booking days that have been removed in legacy.'

    def add_arguments(self, parser):
        parser.add_argument('-d' '--days', type=str, help='Enter days please')

    def handle(self, *args, **options):

        try:
           print ("Importing Legacy Booking Campsite Records")
           days_arg = options['d__days']
           if days_arg:
              days_arg = int(days_arg)
           else:
              days_arg=1

           CAMPSITE_BOOKING_API_KEY = settings.CAMPSITE_BOOKING_API_KEY
                           

           #url = settings.LEGACY_BOOKING_URL + '/api/campsitebookings?api_key='+CAMPSITE_BOOKING_API_KEY+'&today_updates_only=true'
           
           count = 0
           while (count < days_arg):
               print (count)
               nowtime = datetime.now() - timedelta(days=count)
               print (nowtime.strftime('%Y-%m-%d'))
               count = count + 1

               url = settings.LEGACY_BOOKING_URL + '/api/campsitebookings?api_key='+CAMPSITE_BOOKING_API_KEY+'&specified_date=true&lookup_date='+nowtime.strftime('%Y-%m-%d')
               print (url)
               json_resp = requests.get(url, verify=False)
               data = json_resp.json()
               nowtime = datetime.now()
               recordschanges =0 
               recordscreated =0
               bookings_array = {}
               # {'id': 21, 'booking_type': 1, 'date': '2022-06-21', 'campsite_id': 1, 'booking_id': 6, 'is_canceled': False}

               for cb in data:
                   if cb['booking_id'] not in bookings_array:
                        bookings_array[cb['booking_id']] = []
                   bookings_array[cb['booking_id']].append(cb['id'])
               
               for ba in bookings_array.keys():
                   cbl = models.CampsiteBookingLegacy.objects.filter(legacy_booking_id=ba)
                   for r in cbl:
                       if r.campsite_booking_id in bookings_array[ba]:
                           print ("Exists : "+str(r.campsite_booking_id))
                       else:
                           print ("Removing : "+str(r.campsite_booking_id))
                           models.CampsiteBookingLegacy.objects.filter(campsite_booking_id=r.campsite_booking_id).delete()
               #cb = models.CampsiteBookingLegacy.objects.filter(legacy_booking_id=cb['booking_id'])

        except Exception as e:
            print (e)
            #Send fail email
            content = "Error message: {}".format(e)
