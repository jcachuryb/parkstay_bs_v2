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
    help = 'Rebuild mooring booking property cache.'

    def handle(self, *args, **options):

        try:
           print ("Importing Legacy Booking Campsite Records")
           #json_resp = requests.get(url)

           f = open("/app/logs/campsite_booking_legacy.json", "r")
           json_data = f.read()
           data = json.loads(json_data)
           nowtime = datetime.now()
           recordschanges =0
           recordscreated =0
           for d in data:
               cb = models.CampsiteBookingLegacy.objects.filter(campsite_booking_id=d['id'])
               if cb.count() > 0:
                   cbl = cb[0]
                   cbl.campsite_booking_id=d['id']
                   cbl.campsite_id=d['campsite_id']
                   cbl.date=d['date']
                   cbl.booking_type=d['booking_type']
                   cbl.legacy_booking_id=d['booking_id']
                   cbl.updated = nowtime
                   cbl.is_cancelled = d['is_canceled']
                   cbl.save()
                   recordschanges = recordschanges + 1
               else:
                    models.CampsiteBookingLegacy.objects.create(campsite_booking_id=d['id'],
                                                        campsite_id=d['campsite_id'],
                                                        date=d['date'],
                                                        booking_type=d['booking_type'],
                                                        legacy_booking_id=d['booking_id'],
                                                        is_cancelled = d['is_canceled']
                                                       )
                    recordscreated = recordscreated + 1
           print ("Records Updated "+str(recordschanges))
           print ("Records Created "+str(recordscreated))

        except Exception as e:
            print (e)
            #Send fail email
            content = "Error message: {}".format(e)
