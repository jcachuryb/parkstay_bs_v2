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
            dont_send = timezone.now() + timedelta(days=8)

            booking_reminder = models.Booking.objects.filter(confirmation_sent=True, is_canceled=False,reminder_email_sent=False, do_not_send_confirmation=False, property_cache__paid=True,error_sending_confirmation=False, arrival__lt=next_check, next_check_for_payment__lt=timezone.now(), error_sending_reminder=False).exclude(booking_type=3).order_by('id')[:30]

            if booking_reminder:
                for b in booking_reminder:
                    print ("booking")
                    print (b.id)
                    if b.paid is True:
                        try:
                            booking_date_from_arrival = (b.created.date() - b.arrival).days
                            if booking_date_from_arrival > 7:
                               bc = utils.booking_cancellation_fees(b)
                               emails.send_booking_reminder(b.id, bc)
                               models.BookingLog.objects.create(booking=b,message="Reminder email sent")
                            else:
                               models.BookingLog.objects.create(booking=b,message="Reminder email not sent as booking created less than 8 days")
                               b.error_sending_reminder = True
                               b.save()
                        except Exception as e:
                            print ("Error Sending Reminder")
                            print (e)
                            b.error_sending_reminder = True
                            b.save()

        except Exception as e:
            print (e)
            #Send fail email
            content = "Error message: {}".format(e)


