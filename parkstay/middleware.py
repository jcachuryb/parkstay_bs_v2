import re
import datetime

#from django.core.urlresolvers import reverse
from django.urls import reverse
from django.http import Http404, HttpResponse, JsonResponse, HttpResponseRedirect
from django.utils import timezone
from parkstay.models import Booking


CHECKOUT_PATH = re.compile('^/ledger-api')
PROCESS_PAYMENT =  re.compile('^/ledger-api/process-payment')

class BookingTimerMiddleware(object):

    def __init__(self, get_response):
            self.get_response = get_response

    def __call__(self, request):
            return self.pr(request)

    def pr(self, request):
        response= self.get_response(request)
        if request.path.startswith('/static') or request.path.startswith('/favicon') or request.path.startswith('/media') or request.path.startswith('/api') or request.path.startswith('/search-availability/information/') or request.path.startswith('/search-availability/campground/') or request.path.startswith('/campground-image'):
             pass
        else:
            if 'ps_booking' in request.session:
                try:
                    booking = Booking.objects.get(pk=request.session['ps_booking'])
                except:
                    # no idea what object is in self.request.session['ps_booking'], ditch it
                    del request.session['ps_booking']
                    return response
                #if booking.booking_type != 3:
                #    # booking in the session is not a temporary type, ditch it
                #    del request.session['ps_booking']
                if booking.expiry_time is not None:
                    if timezone.now() > booking.expiry_time and booking.booking_type == 3:
                    # expiry time has been hit, destroy the Booking then ditch it
                    #booking.delete()
                        del request.session['ps_booking']

                if CHECKOUT_PATH.match(request.path) and request.method == 'POST' and booking.booking_type == 3:
                    # safeguard against e.g. part 1 of the multipart checkout confirmation process passing, then part 2 timing out.
                    # on POST boosts remaining time to at least 2 minutes
                    booking.expiry_time = max(booking.expiry_time, timezone.now()+datetime.timedelta(minutes=2))
                    booking.save()

            # force a redirect if in the checkout
            if ('ps_booking_internal' not in request.COOKIES) and CHECKOUT_PATH.match(request.path):
                if ('ps_booking' not in request.session) and CHECKOUT_PATH.match(request.path):
                    url_redirect = reverse('public_make_booking')
                    response = HttpResponse("<script> window.location='"+url_redirect+"';</script> <center><div class='container'><div class='alert alert-primary' role='alert'><a href='"+url_redirect+"'> Redirecting please wait: "+url_redirect+"</a><div></div></center>")
                    return response
                    #return HttpResponseRedirect(reverse('public_make_booking'))
                else:
                    return response
        return response


class CacheControl(object):

    def __init__(self, get_response):
            self.get_response = get_response

    def __call__(self, request):
       response= self.get_response(request)

       if request.path == '/':
            response['Cache-Control'] = 'public, max-age=60'
       elif request.path == '/map/':
            response['Cache-Control'] = 'public, max-age=300'
       elif request.path[:19] == '/api/search_suggest':
            response['Cache-Control'] = 'public, max-age=300'
       elif request.path[:12] == '/api/places/':
            response['Cache-Control'] = 'public, max-age=300'
       elif request.path[:20] == '/api/campground_map/':
            response['Cache-Control'] = 'public, max-age=300'
       elif request.path[:17] == '/campground-image':
            response['Cache-Control'] = 'public, max-age=86400'
       elif request.path[:31] == '/api/campsite_availablity_view/':
            response['Cache-Control'] = 'private, no-store'
       elif request.path[:5] == '/api/':
            response['Cache-Control'] = 'private, no-store'
            #response['Cache-Control'] = 'public, max-age=60'
       elif request.path[:8] == '/static/':
            response['Cache-Control'] = 'public, max-age=172800'
       elif request.path[:7] == '/media/':
            response['Cache-Control'] = 'public, max-age=86400'
       else:
            pass
            #response['Cache-Control'] = 'private, no-store'
       return response
    #def patch_response_headers(response, cache_timeout=None):
        #response['Cache-Control'] = 'private, no-store'
        #patch_cache_control(response, max_age=cache_timeout)        
    #def process_response(self, request, response):
        #print ("PATH")
        #print (request.path)
        #response['Cache-Control'] = 'private, no-store'
        #return add_cache_control(response)
