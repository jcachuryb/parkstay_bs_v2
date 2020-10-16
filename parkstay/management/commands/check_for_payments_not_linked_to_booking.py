from django.core.management.base import BaseCommand
from django.utils import timezone
from parkstay.emails import sendHtmlEmail
from parkstay import models 
from parkstay import utils
from parkstay import context_processors
#from ledger.payments.bpoint.models import BpointTransaction, BpointToken
#from ledger.payments.models import Invoice,OracleInterface,CashTransaction
#from oscar.apps.order.models import Order
from ledger.basket.models import Basket
from django.conf import settings
from datetime import timedelta, datetime
from ledger.payments.utils import bpoint_integrity_checks, bpoint_integrity_checks_completed
import socket

class Command(BaseCommand):
    help = 'Check for payment which have been completed but are missing a booking.'


    def log(self,line):
         dt = datetime.now()
         hostname = socket.gethostname()
         f= open(settings.BASE_DIR+"/logs/check_for_payments_not_linked_to_booking.log","a+")
         f.write(str(dt.strftime('%Y-%m-%d %H:%M:%S'))+': '+hostname+': '+line+"\r\n")
         f.close()

    def handle(self, *args, **options):
           rows = []
           system = settings.PS_PAYMENT_SYSTEM_ID
           system = system.replace('S','0')
           rows = bpoint_integrity_checks(system,2,10)

           for r in rows:
               print (r['booking_reference'])
               booking_reference_split = r['booking_reference'].split('-')
               if len(booking_reference_split) == 2:
                   booking_group_type= booking_reference_split[0]
                   booking_id = booking_reference_split[1]
                   if booking_group_type == 'PS':
                       baa = models.Booking.objects.filter(id=booking_id)
                       if baa.count() > 0:
                           basket = Basket.objects.filter(id=int(r['basket']))
                           if baa[0].booking_type == 3:
                              booking_obj = baa[0]
                              booking_obj.error_sending_confirmation=True
                              booking_obj.error_sending_invoice=True
                              booking_obj.save() 

                              utils.bind_booking(baa[0], r['reference']) 
                              bpoint_integrity_checks_completed(r['bpoint_id'],r['reference'])
                              self.log("Booking Recovery for ("+str(r['booking_reference'].replace("-",""))+") with invoice ("+r['reference']+")")
                              emails = models.EmailGroup.objects.filter(email_group=0)
                              context = {
                                  'booking' : baa[0],
                                  'booking_reference': r['booking_reference'].replace("-",""),
                                  'invoice': r['reference'],
                                  'customer_name' : baa[0].details['first_name']+' '+baa[0].details['last_name']
                              }

                              email_list = []
                              for e in emails:
                                  email_list.append(e.email)
                              sendHtmlEmail(tuple(email_list),"[PARKSTAY] Booking Recovery for ("+str(r['booking_reference'].replace("-",""))+") with invoice ("+r['reference']+")",context,'ps/email/booking_recovery.html',None,None,settings.EMAIL_FROM,'system-oim',attachments=None)
                           else:
                               bpoint_integrity_checks_completed(r['bpoint_id'],r['reference'])
                       else:
                           bpoint_integrity_checks_completed(r['bpoint_id'],r['reference'])
               else:                       
                   bpoint_integrity_checks_completed(r['bpoint_id'],r['reference'])
