from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
import threading

#from mooring.models import RegisteredVessels
from parkstay import models
from parkstay import utils
from datetime import datetime
import json
import time
from parkstay import property_cache
from parkstay import emails
from datetime import timedelta

class Command(BaseCommand):
    help = 'Send reminder booking email.'

    def handle(self, *args, **options):
        try:
            next_check = timezone.now() + timedelta(days=7)
            booking_reminder = models.Booking.objects.filter(reminder_email_sent=False, do_not_send_confirmation=False, property_cache__paid=True,error_sending_confirmation=False, arrival__lt=timezone.now(), next_check_for_payment__lt=timezone.now(), error_sending_reminder=False).exclude(booking_type=3).order_by('id')[:3]

            if booking_reminder:
                for b in booking_reminder:
                    print ("booking")
                    print (b.id)
                    if b.paid is True:
                        try:
                            bc = utils.booking_cancellation_fees(b)
                            emails.send_booking_reminder(b.id, bc)
                        except Exception as e:
                            print ("Error Sending Reminder")
                            print (e)
                            b.error_sending_reminder = True
                            b.save()

        except Exception as e:
            print (e)
            #Send fail email
            content = "Error message: {}".format(e)


