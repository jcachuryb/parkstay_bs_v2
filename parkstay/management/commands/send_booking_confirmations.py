from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
import threading

#from mooring.models import RegisteredVessels
from parkstay import models
from datetime import datetime
import json
import time
from parkstay import property_cache
from parkstay import emails
from datetime import timedelta

class Command(BaseCommand):
    help = 'Send confirmation booking email.'

    def handle(self, *args, **options):
        try:
            unconfirmed = models.Booking.objects.filter(created__gt='2020-08-25', confirmation_sent=False, property_cache__paid=True).exclude(booking_type=3).order_by('id')[:10]
            if unconfirmed:
                for b in unconfirmed:
                    if b.paid:
                        try:
                            emails.send_booking_invoice(b)
                            emails.send_booking_confirmation(b.id)
                        except Exception as e:
                            print (e)

            bookings = models.Booking.objects.filter(created__gt='2020-08-25', send_invoice=False).exclude(booking_type=3).order_by('id')[:10]
            for b in bookings:
                try:
                    emails.send_booking_invoice(b)  
                except Exception as e:
                    print (e)

        except Exception as e:
            print (e)
            #Send fail email
            content = "Error message: {}".format(e)



