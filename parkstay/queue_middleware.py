import re
import datetime
import requests
from django.conf import settings
#from django.core.urlresolvers import reverse
from django.urls import reverse
from django.http import Http404, HttpResponse, JsonResponse, HttpResponseRedirect
from django.utils import timezone

CHECKOUT_PATH = re.compile('^/ledger-api')
PROCESS_PAYMENT =  re.compile('^/ledger-api/process-payment')

class QueueControl(object):

    def __init__(self, get_response):
            self.get_response = get_response

    def __call__(self, request):
       if settings.WAITING_QUEUE_ENABLED is True:
            # Required for ledger to send completion signal after payment is received.
            if request.path.startswith('/api/complete_booking/') or request.path.startswith('/api/booking_pricing/') or request.path.startswith('/api/booking_updates/'):
                 response= self.get_response(request)
                 return response

            sitequeuesession = request.COOKIES.get('sitequeuesession', None)
            if request.path == '/' or request.path.startswith('/search-availability/information/') or request.path.startswith('/search-availability/campground') or  request.path.startswith('/mybookings') or request.path.startswith('/api/'):

                 try:
                      if 'HTTP_HOST' in request.META:
                           if settings.QUEUE_ACTIVE_HOSTS == request.META.get('HTTP_HOST',''):
                                if settings.QUEUE_WAITING_URL:

                                    if sitequeuesession is None:
                                         print ("QUEUE REDIRECT")
                                         response =HttpResponse("<script>window.location.replace('"+settings.QUEUE_WAITING_URL+"');</script>Redirecting")
                                         return response
                                    else:
                                         print ("QUEUE SESSION")
                                         url = settings.QUEUE_URL+"/api/check-create-session/?session_key="+sitequeuesession+"&queue_group="+settings.QUEUE_GROUP_NAME
                                         resp = requests.get(url, data = {}, cookies={},  verify=False)
                                         queue_json = resp.json()
                                         if queue_json['status'] == 'Waiting': 
                                               response =HttpResponse("<script>window.location.replace('"+settings.QUEUE_WAITING_URL+"');</script>Redirecting")
                                               print ('You are waiting')
                                               return response
                                         else:
                                               print ('Active Session')
                                               
                 except Exception as e:
                     print (e)
                     print ("ERROR LOADING QUEUE")
            else:
                 pass
       else:
           pass
       response= self.get_response(request)
       return response
