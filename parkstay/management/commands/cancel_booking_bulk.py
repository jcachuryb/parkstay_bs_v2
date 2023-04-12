from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from parkstay.models import Booking, BookingInvoice, BookingLog

from parkstay import emails
#from ledger.payments.models import Invoice
#from ledger.accounts.models import EmailUser, Address, EmailIdentity
#from ledger.payments.utils import systemid_check, update_payments
from ledger_api_client.ledger_models import EmailUserRO as EmailUser

from datetime import timedelta, date, datetime
from decimal import Decimal as D
#from ledger.payments.utils import systemid_check
from decimal import Decimal
import itertools

class Command(BaseCommand):
    help = 'Bulk booking cancellation'

    def add_arguments(self, parser):
        # Positional arguments
        #parser.add_argument('days_back', nargs='+', type=int)
        parser.add_argument('file',)

    def handle(self, *args, **options):
        print ("RUNNING")
        user = EmailUser.objects.get(email='jason.moore@dbca.wa.gov.au') 
        #days_back = options['days_back'][0]
        file_path = options['file']
        print (file_path)

        booking_cancelled = []
        booking_errors = []
        refund_success = False

        #Booking.objects.filter(arrival__gte='2020-01-01', arrival__lte='2020-01-21')[:2]
        f = open(file_path)
        for line in f:
           line = line.strip('\n')
           print(line+":")
           refund_success = False 
           try:
               b = Booking.objects.get(id=line)
               if b.is_canceled is False:
                    b.is_canceled = True
                    b.canceled_by = user 
                    b.cancelation_time = timezone.now()
                    b.cancellation_reason = "Booking cancelled due to campsite closure (Bulk Cancellation)"
                    b.save()
                    #b.cancelBooking('Campground Closure');
                    print (b) 
                    booking_cancelled.append({'booking_id': b.id,'booking_customer': b.customer })
                    BookingLog.objects.create(booking=b,message="Booking Cancelled (Bulk Cancellation)")
               else:
                    booking_errors.append({"bookingid": b.id,"booking_error": "Booking is already cancelled"})
           except Exception as e:
               print (e)
               booking_errors.append({"bookingid": line,"booking_error": str(e)})
           print ("-----")

        # Send email with success and failed refunds 
        #print (days_back)
        context = {
         "booking_cancellation":booking_cancelled,
         "booking_errors": booking_errors 
        }
        email_list = []
        for email_to in settings.NOTIFICATION_EMAIL.split(","):
               email_list.append(email_to)
        print ("SENDING EMAIL")
        print (settings.EMAIL_FROM)
        print (booking_cancelled)
        emails.sendHtmlEmail(tuple(email_list),"[PARKSTAY] Bulk cancellation script",context,'ps/email/bulk_cancel.html',None,None,settings.EMAIL_FROM,'system-oim',attachments=None)
        return "Completed"

